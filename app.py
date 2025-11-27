from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import joblib
import logging
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class EmotionPredictor:
    def __init__(self):
        self.lr_model = None
        self.rf_model = None
        self.vectorizer = None
        self.label_encoder = None
        self.models_loaded = False
        self.load_models()
    
    def load_models(self):
        """Charger les modèles ML"""
        try:
            self.lr_model = joblib.load('models/model_lr.pkl')
            self.rf_model = joblib.load('models/model_rf.pkl')
            self.vectorizer = joblib.load('models/vectorizer.pkl')
            self.label_encoder = joblib.load('models/label_encoder.pkl')
            self.models_loaded = True
            logger.info("✅ Tous les modèles chargés avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèles: {str(e)}")
            self.models_loaded = False
    
    def predict_emotion(self, text: str, use_rf: bool = True) -> Dict[str, Any]:
        """Prédire l'émotion depuis le texte"""
        if not self.models_loaded:
            raise Exception("Modèles non chargés correctement")
        
        # Transformer le texte
        text_tfidf = self.vectorizer.transform([text])
        
        if use_rf:
            # Utiliser Random Forest
            probabilities = self.rf_model.predict_proba(text_tfidf)[0]
            predicted_idx = self.rf_model.predict(text_tfidf)[0]
            confidence = float(probabilities[predicted_idx])
            model_used = "Random Forest"
        else:
            # Utiliser Logistic Regression
            probabilities = self.lr_model.predict_proba(text_tfidf)[0]
            predicted_idx = self.lr_model.predict(text_tfidf)[0]
            confidence = float(probabilities[predicted_idx])
            model_used = "Logistic Regression"
        
        # Obtenir le label d'émotion
        emotion = self.label_encoder.inverse_transform([predicted_idx])[0]
        
        return {
            'emotion': emotion,
            'confidence': confidence,
            'model_used': model_used,
            'probabilities': {
                self.label_encoder.inverse_transform([i])[0]: float(prob)
                for i, prob in enumerate(probabilities)
            }
        }

# Initialize predictor
predictor = EmotionPredictor()

# Game state
game_state = {
    'ai_score': 0,
    'user_score': 0,
    'total_rounds': 0
}

@app.route('/')
def home():
    """Render the main game page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for emotion prediction"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        user_emotion = data.get('user_emotion', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if not user_emotion:
            return jsonify({'error': 'No emotion selected'}), 400
        
        # Get AI prediction (use Random Forest by default)
        result = predictor.predict_emotion(text, use_rf=True)
        
        # Update game scores
        game_state['total_rounds'] += 1
        
        # Determine if AI guessed correctly
        ai_correct = (result['emotion'].lower() == user_emotion.lower())
        
        if ai_correct:
            game_state['ai_score'] += 1
            user_won = False
        else:
            game_state['user_score'] += 1
            user_won = True
        
        response = {
            'predicted_emotion': result['emotion'],
            'model_used': result['model_used'],
            'confidence': result['confidence'],
            'probabilities': result['probabilities'],
            'ai_score': game_state['ai_score'],
            'user_score': game_state['user_score'],
            'ai_correct': ai_correct,
            'user_won': user_won,
            'total_rounds': game_state['total_rounds']
        }
        
        logger.info(f"Prediction: {result['emotion']} (Confidence: {result['confidence']:.3f})")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed'}), 500

@app.route('/reset', methods=['POST'])
def reset_game():
    """Reset game scores"""
    game_state['ai_score'] = 0
    game_state['user_score'] = 0
    game_state['total_rounds'] = 0
    return jsonify({'message': 'Game reset successfully'})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': predictor.models_loaded,
        'game_state': game_state
    })

if __name__ == '__main__':
    # Check if models exist, if not train them
    if not os.path.exists('models/model_lr.pkl'):
        logger.info("Models not found. Training models...")
        from train_models import train_models
        train_models()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
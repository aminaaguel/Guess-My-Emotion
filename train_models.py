import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib
import os

# Créer le dossier models s'il n'existe pas
os.makedirs('models', exist_ok=True)

def create_synthetic_data():
    """Créer des données synthétiques supplémentaires"""
    emotions = {
        'Happy': [
            "I'm feeling great!", "This is fantastic!", "So much joy!", 
            "Wonderful experience", "I love this!", "Amazing day!",
            "Feeling blessed", "So grateful", "Excellent news!",
            "I'm over the moon", "Pure happiness", "Life is good",
            "So excited about this", "Having a wonderful time", "This is awesome"
        ],
        'Sad': [
            "Feeling down", "This is terrible", "So disappointed",
            "Heartbroken", "Miserable day", "Feeling blue",
            "So upset", "Can't stop crying", "Everything is wrong",
            "So depressing", "Feeling low", "Empty inside",
            "Nothing going right", "Feeling hopeless", "So lonely"
        ],
        'Angry': [
            "This is ridiculous", "I'm furious", "So annoyed",
            "Completely unacceptable", "I hate this", "So frustrating",
            "Making me mad", "Infuriating situation", "I'm livid",
            "This pisses me off", "Unbelievable!", "How dare they",
            "So angry right now", "This makes me rage", "Completely pissed off"
        ],
        'Stress': [
            "Overwhelmed", "Too much pressure", "Can't handle this",
            "Stressed out", "Anxious feeling", "Pressure building",
            "Too many deadlines", "Burning out", "Panic setting in",
            "Too much to do", "Feeling pressured", "Stressful situation",
            "So much anxiety", "Overloaded with work", "Can't cope anymore"
        ],
        'Neutral': [
            "Regular day", "Nothing special", "Usual routine",
            "Average day", "Standard procedure", "Normal activities",
            "Typical day", "As expected", "Routine work",
            "Ordinary tasks", "Standard day", "Nothing unusual",
            "Just normal stuff", "Everything is fine", "Nothing to report"
        ]
    }
    
    synthetic_data = []
    for emotion, texts in emotions.items():
        for text in texts:
            synthetic_data.append({'text': text, 'emotion': emotion})
    
    return pd.DataFrame(synthetic_data)

def train_models():
    # Charger et préparer les données
    print("📊 Chargement du dataset...")
    df = pd.read_csv('dataset.csv')
    synthetic_df = create_synthetic_data()
    df = pd.concat([df, synthetic_df], ignore_index=True)
    
    print(f"📈 Taille du dataset: {len(df)} exemples")
    print("📋 Distribution des émotions:")
    print(df['emotion'].value_counts())
    
    # Préparer les features et labels
    X = df['text'].values
    y = df['emotion'].values
    
    # Encoder les labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Split des données
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Vectorization TF-IDF
    print("🔧 Entraînement du TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english')
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    # Modèle 1: Logistic Regression
    print("🤖 Entraînement du modèle Logistic Regression...")
    lr_model = LogisticRegression(
        random_state=42,
        max_iter=1000,
        C=1.0,
        solver='liblinear'
    )
    lr_model.fit(X_train_tfidf, y_train)
    
    # Calculer l'accuracy
    y_pred_lr = lr_model.predict(X_test_tfidf)
    lr_accuracy = accuracy_score(y_test, y_pred_lr)
    print(f"✅ Logistic Regression Accuracy: {lr_accuracy:.4f}")
    
    # Modèle 2: Random Forest
    print("🌳 Entraînement du modèle Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        max_depth=10,
        min_samples_split=5
    )
    rf_model.fit(X_train_tfidf, y_train)
    
    # Calculer l'accuracy
    y_pred_rf = rf_model.predict(X_test_tfidf)
    rf_accuracy = accuracy_score(y_test, y_pred_rf)
    print(f"✅ Random Forest Accuracy: {rf_accuracy:.4f}")
    
    # Sauvegarder les modèles
    print("💾 Sauvegarde des modèles...")
    joblib.dump(lr_model, 'models/model_lr.pkl')
    joblib.dump(rf_model, 'models/model_rf.pkl') 
    joblib.dump(vectorizer, 'models/vectorizer.pkl')
    joblib.dump(le, 'models/label_encoder.pkl')
    
    print("🎉 Entraînement des modèles terminé!")
    print("📊 Accuracies finales:")
    print(f"   - Logistic Regression: {lr_accuracy:.4f}")
    print(f"   - Random Forest: {rf_accuracy:.4f}")
    
    # Déterminer le meilleur modèle
    best_model = "Random Forest" if rf_accuracy > lr_accuracy else "Logistic Regression"
    print(f"🏆 Meilleur modèle: {best_model}")
    
    return lr_accuracy, rf_accuracy

if __name__ == "__main__":
    train_models()
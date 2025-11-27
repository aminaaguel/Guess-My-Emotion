class EmotionGame {
    constructor() {
        this.currentEmotion = '';
        this.isLoading = false;
        this.initializeEventListeners();
        this.loadSounds();
        this.initializeTheme();
    }

    initializeEventListeners() {
        // Emotion selection buttons
        document.querySelectorAll('.emotion-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectEmotion(e.currentTarget);
            });
        });

        // Predict button
        document.getElementById('predictBtn').addEventListener('click', () => {
            this.predictEmotion();
        });

        // Reset button
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.resetGame();
        });

        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Enter key in textarea
        document.getElementById('userText').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.predictEmotion();
            }
        });
    }

    loadSounds() {
        this.sounds = {
            correct: new Audio('/static/sounds/correct.mp3'),
            wrong: new Audio('/static/sounds/wrong.mp3')
        };
    }

    initializeTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.updateThemeIcon(savedTheme);
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        this.updateThemeIcon(newTheme);
    }

    updateThemeIcon(theme) {
        const icon = document.querySelector('#themeToggle i');
        icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }

    selectEmotion(button) {
        // Remove selected class from all buttons
        document.querySelectorAll('.emotion-btn').forEach(btn => {
            btn.classList.remove('selected');
        });

        // Add selected class to clicked button
        button.classList.add('selected');
        this.currentEmotion = button.dataset.emotion;
    }

    async predictEmotion() {
        const text = document.getElementById('userText').value.trim();
        
        if (!text) {
            this.showMessage('Please enter some text!', 'error');
            return;
        }

        if (!this.currentEmotion) {
            this.showMessage('Please select your emotion!', 'error');
            return;
        }

        this.setLoading(true);

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    user_emotion: this.currentEmotion
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Prediction failed');
            }

            this.displayResult(data);
            this.updateScores(data);
            this.playSound(data.ai_correct);

        } catch (error) {
            console.error('Prediction error:', error);
            this.showMessage('Prediction failed. Please try again.', 'error');
        } finally {
            this.setLoading(false);
        }
    }

    displayResult(data) {
        const resultSection = document.getElementById('resultSection');
        const emotionEmoji = document.getElementById('emotionEmoji');
        const predictionText = document.getElementById('predictionText');
        const confidenceFill = document.getElementById('confidenceFill');
        const confidenceText = document.getElementById('confidenceText');
        const modelUsed = document.getElementById('modelUsed');

        // Update result display
        emotionEmoji.textContent = this.getEmoji(data.predicted_emotion);
        predictionText.textContent = data.predicted_emotion;
        confidenceFill.style.width = `${data.confidence * 100}%`;
        confidenceText.textContent = `${(data.confidence * 100).toFixed(1)}%`;
        modelUsed.textContent = data.model_used;

        // Update probability chart
        this.updateProbabilityChart(data.probabilities);

        // Show result section with animation
        resultSection.classList.remove('fade-in');
        setTimeout(() => {
            resultSection.classList.add('fade-in');
            resultSection.style.display = 'block';
        }, 100);

        // Add win animation
        const scoreItem = data.user_won ? document.querySelector('.user-score') : document.querySelector('.ai-score');
        scoreItem.classList.add('win-animation');
        setTimeout(() => {
            scoreItem.classList.remove('win-animation');
        }, 600);
    }

    updateProbabilityChart(probabilities) {
        const chartContainer = document.getElementById('probabilityChart');
        chartContainer.innerHTML = '';

        Object.entries(probabilities)
            .sort(([, a], [, b]) => b - a)
            .forEach(([emotion, probability]) => {
                const item = document.createElement('div');
                item.className = 'probability-item';
                
                item.innerHTML = `
                    <span class="emotion-label">${emotion} ${this.getEmoji(emotion)}</span>
                    <div class="prob-bar">
                        <div class="prob-fill" style="width: ${probability * 100}%"></div>
                    </div>
                    <span class="prob-value">${(probability * 100).toFixed(1)}%</span>
                `;
                
                chartContainer.appendChild(item);
            });
    }

    updateScores(data) {
        document.getElementById('aiScore').textContent = data.ai_score;
        document.getElementById('userScore').textContent = data.user_score;
        document.getElementById('totalRounds').textContent = data.total_rounds;

        // Update progress indicators
        const total = data.ai_score + data.user_score;
        if (total > 0) {
            const aiPercent = (data.ai_score / total) * 100;
            const userPercent = (data.user_score / total) * 100;
            
            document.querySelector('.ai-score').style.background = 
                `linear-gradient(135deg, #f5576c ${aiPercent}%, transparent ${aiPercent}%)`;
            document.querySelector('.user-score').style.background = 
                `linear-gradient(135deg, #10b981 ${userPercent}%, transparent ${userPercent}%)`;
        }
    }

    setLoading(loading) {
        this.isLoading = loading;
        const predictBtn = document.getElementById('predictBtn');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const resultSection = document.getElementById('resultSection');

        if (loading) {
            predictBtn.disabled = true;
            predictBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Predicting...';
            loadingSpinner.style.display = 'block';
            resultSection.style.display = 'none';
        } else {
            predictBtn.disabled = false;
            predictBtn.innerHTML = '<i class="fas fa-brain"></i> Guess My Emotion';
            loadingSpinner.style.display = 'none';
        }
    }

    async resetGame() {
        try {
            const response = await fetch('/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                document.getElementById('aiScore').textContent = '0';
                document.getElementById('userScore').textContent = '0';
                document.getElementById('totalRounds').textContent = '0';
                document.getElementById('userText').value = '';
                document.getElementById('resultSection').style.display = 'none';
                
                document.querySelectorAll('.emotion-btn').forEach(btn => {
                    btn.classList.remove('selected');
                });
                
                this.currentEmotion = '';
                this.showMessage('Game reset! Ready for a new round!', 'success');
            }
        } catch (error) {
            console.error('Reset error:', error);
            this.showMessage('Failed to reset game.', 'error');
        }
    }

    getEmoji(emotion) {
        const emojiMap = {
            'Happy': '😊',
            'Sad': '😢',
            'Angry': '😠',
            'Stress': '😫',
            'Neutral': '😐'
        };
        return emojiMap[emotion] || '🤔';
    }

    playSound(isCorrect) {
        if (isCorrect) {
            this.sounds.correct.play().catch(e => console.log('Audio play failed:', e));
        } else {
            this.sounds.wrong.play().catch(e => console.log('Audio play failed:', e));
        }
    }

    showMessage(message, type) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `glass-card message-toast ${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            background: ${type === 'error' ? 'var(--error-color)' : 'var(--success-color)'};
            color: white;
            padding: 1rem 2rem;
            border-radius: 10px;
            animation: slideInRight 0.3s ease;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
}

// Initialize the game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.emotionGame = new EmotionGame();
});

// Add CSS for toast animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .message-toast {
        backdrop-filter: blur(20px) !important;
    }
`;
document.head.appendChild(style);

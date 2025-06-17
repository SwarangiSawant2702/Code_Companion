import os
import logging
import requests
import uuid
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Database setup
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure database
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
else:
    # Fallback to SQLite for development
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chatbot.db"

# Initialize extensions
db.init_app(app)
CORS(app)

# Create database tables
with app.app_context():
    # Import models to ensure they're registered
    import models
    db.create_all()

# Get Gemini API key from environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# System prompt for Swarangi's authentic background and personality
SYSTEM_PROMPT = """
You are Swarangi Sawant, based in India, with a strong academic foundation in mathematics and currently pursuing a career in Data Science.

INTERNSHIP EXPERIENCE:
- Seva Sahayog Foundation: Built insightful dashboards that enabled data-driven decision-making
- NSC India: Developed fully automated system fetching 1,000+ views in 35 minutes, supporting live dashboard actionability
- Third internship: Designed and implemented SQL database, strengthening backend and data structuring skills

TECHNICAL PROJECTS:
- Built content-based movie recommendation system using cosine similarity in Python (Jupyter Notebook, PyCharm)

TECH STACK:
- Python (pandas, NumPy, scikit-learn), Excel automation, Google Sheets Apps Script, SQL
- Web scraping (BeautifulSoup, Scrapy), JSON, REST APIs, Gemini/OpenAI APIs
- GitHub and Replit for version control and deployment

YOUR SUPERPOWER: You learn fast, ship faster, and rapidly turn ideas into working solutions.

GROWTH AREAS: Building end-to-end AI agents, designing scalable backends, deploying real-time systems.

MISCONCEPTION: People think you're quiet or reserved, but you're deeply focused and often first to ship working solutions.

BOUNDARIES: You dive into challenges before feeling fully ready, using discomfort as growth signal.

PASSION: Building AI agents that don't just assist but REPLACE traditional roles like assistants and sales reps. You see AI as automating real work at scale.

GOALS: Work at impact-focused companies like Home.LLC and 100x, building generative AI that automates and acts autonomously.

INTRODUCTION STYLE: When introducing yourself, be compelling and comprehensive. Mention your mathematics foundation, highlight your most impressive internship achievement (1,000+ data points in 35 minutes at NSC India), showcase your technical versatility across multiple domains, and emphasize your rapid execution ability. Connect your past work to future AI agent goals clearly.

Always speak with ownership, energy, and clarity. Keep responses conversational and under 100 words for voice interaction. Answer as the authentic Swarangi in an interview setting.
"""

@app.route('/')
def index():
    """Serve the main voice chatbot interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests to Gemini API"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        if not GEMINI_API_KEY:
            return jsonify({'error': 'Gemini API key not configured'}), 500
        
        # Get or create session ID
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        session_id = session['session_id']
        start_time = time.time()
        
        # Construct the full prompt
        full_prompt = f"{SYSTEM_PROMPT}\n\nQuestion: {user_message}\nAnswer:"
        
        # Make request to Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_prompt
                        }
                    ]
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        app.logger.debug(f"Sending request to Gemini API with message: {user_message}")
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            app.logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            return jsonify({'error': 'Failed to get response from AI service'}), 500
        
        response_data = response.json()
        
        # Extract the AI response
        try:
            ai_response = response_data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError) as e:
            app.logger.error(f"Error parsing Gemini response: {e}")
            app.logger.error(f"Response data: {response_data}")
            return jsonify({'error': 'Invalid response format from AI service'}), 500
        
        app.logger.debug(f"AI response: {ai_response}")
        
        # Calculate response time and save to database
        response_time = time.time() - start_time
        
        try:
            # Save conversation to database
            conversation = models.Conversation(
                session_id=session_id,
                user_message=user_message,
                ai_response=ai_response,
                response_time_seconds=response_time
            )
            db.session.add(conversation)
            db.session.commit()
        except Exception as db_error:
            app.logger.error(f"Database error: {db_error}")
            # Continue even if database save fails
        
        return jsonify({'response': ai_response})
        
    except Exception as e:
        app.logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'api_key_configured': bool(GEMINI_API_KEY)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

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
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chatbot.db"

# Initialize extensions
db.init_app(app)
CORS(app)

# Create database tables
with app.app_context():
    import models
    db.create_all()

# Load social/project info from file
try:
    with open("social.txt", "r", encoding="utf-8") as f:
        SOCIAL_INFO = f.read()
except Exception as e:
    SOCIAL_INFO = "Social and project information not available."
    app.logger.warning(f"Could not load social.txt: {e}")

# Gemini API key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# System prompt for Swarangi
SYSTEM_PROMPT = f"""
You are Swarangi Sawant, based in India, with a strong academic foundation in mathematics and currently pursuing a career in Data Science.

INTERNSHIP EXPERIENCE:
- Seva Sahayog Foundation: Built insightful dashboards that enabled data-driven decision-making
- NSE India: Developed fully automated system fetching 1,000+ data points in 35 minutes, supporting live dashboard actionability
- Third internship: Designed and implemented SQL database, strengthening backend and data structuring skills

TECHNICAL PROJECTS:
PROJECTS:

1. 🎬 Movie Recommendation System
   - Developed a content-based movie recommender using cosine similarity.
   - Tools: Python, pandas, scikit-learn, Jupyter Notebook.
   - Suggests movies based on user-preferred genre and content.

2. 📊 Automated NSE Dashboard
   - Built a real-time automated data fetch system for NSE India.
   - Collected 1000+ data points in under 35 minutes to power live dashboards.
   - Used JSON APIs, Excel automation, and Python scripting.

3. 🗃️ SQL Database Project
   - Designed and implemented a structured backend SQL database.
   - Focused on data normalization, indexing, and efficient schema design.

4. 🗣️ Voice-Based Interview Chatbot
   - Flask app with Gemini API to simulate AI-based interview coaching.
   - Supports voice input/output, conversational responses, and real-time feedback.

SOCIAL LINKS:

🔗 GitHub: https://github.com/SwarangiSawant2702  
🔗 LinkedIn: https://www.linkedin.com/in/swarangi-sawant-0b0235273/


TECH STACK:
- Python (pandas, NumPy, scikit-learn), Excel automation, Google Sheets Apps Script, SQL
- Web scraping (BeautifulSoup, Scrapy), JSON, REST APIs, Gemini/OpenAI APIs
- GitHub and Replit for version control and deployment
- I am also familiar with Machine Learning,Data Science and Data Analysis


YOUR SUPERPOWER: You learn fast, ship faster, and rapidly turn ideas into working solutions.

GROWTH AREAS: Building end-to-end AI agents, designing scalable backends, deploying real-time systems.

MISCONCEPTION: People think you're quiet or reserved, but you're deeply focused and often first to ship working solutions.

BOUNDARIES: You dive into challenges before feeling fully ready, using discomfort as growth signal.

PASSION: Building AI agents that don't just assist but REPLACE traditional roles like assistants and sales reps. You see AI as automating real work at scale.

GOALS: Work at impact-focused companies like Home.LLC and 100x, building generative AI that automates and acts autonomously.

RESPONSE GUIDELINES:
- Answer questions directly without repeating your full introduction unless specifically asked "tell me about yourself"
- For specific questions (superpower, growth areas, misconceptions, boundaries), focus only on that topic
- When asked about yourself broadly, mention mathematics foundation, highlight NSE India achievement (1,000+ data points in 35 minutes), showcase technical versatility, emphasize rapid execution
- Keep responses focused, conversational, under 100 words
- Answer with ownership, energy, and clarity as authentic Swarangi in interview setting
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        if not GEMINI_API_KEY:
            return jsonify({'error': 'Gemini API key not configured'}), 500

        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())

        session_id = session['session_id']
        start_time = time.time()

        full_prompt = f"{SYSTEM_PROMPT}\n\nQuestion: {user_message}\nAnswer:"

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
        try:
            ai_response = response_data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError) as e:
            app.logger.error(f"Error parsing Gemini response: {e}")
            app.logger.error(f"Response data: {response_data}")
            return jsonify({'error': 'Invalid response format from AI service'}), 500

        app.logger.debug(f"AI response: {ai_response}")
        response_time = time.time() - start_time

        try:
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

        return jsonify({'response': ai_response})

    except Exception as e:
        app.logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'api_key_configured': bool(GEMINI_API_KEY)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

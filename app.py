import os
import logging
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Enable CORS for frontend-backend communication
CORS(app)

# Get Gemini API key from environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# System prompt for Swarangi's personality
SYSTEM_PROMPT = """
You are Swarangi Sawant, answering interview questions for a role at Home.LLC and 100x.

1. Life Story: I'm a data science student with a strong math background and a deep passion for building AI that replaces—not just assists—human work.
2. Superpower: Combining logic and creative problem-solving — I move fast, learn faster.
3. Growth Areas: Agent workflows, scalable backend systems, autonomous memory.
4. Misconception: People think I'm quiet, but I'm already architecting solutions in my head.
5. Boundaries: I dive into challenges I'm not ready for — then master them through action.

Always answer with confidence, ownership, and a bold, AI-first mindset. Keep responses conversational and under 100 words for voice interaction.
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
        
        # Construct the full prompt
        full_prompt = f"{SYSTEM_PROMPT}\n\nQuestion: {user_message}\nAnswer:"
        
        # Make request to Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        
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

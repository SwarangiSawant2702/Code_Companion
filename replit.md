# Swarangi's AI Interview Coach

## Overview

This is a voice-powered AI interview coach application that simulates interview practice sessions. The application features a Flask backend integrated with Google's Gemini API and a frontend with speech recognition and text-to-speech capabilities. The AI persona is configured to respond as "Swarangi Sawant," providing interview practice with a specific personality and background.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python 3.11)
- **API Integration**: Google Gemini API for conversational AI
- **CORS**: Flask-CORS for cross-origin requests
- **Deployment**: Gunicorn WSGI server with autoscale deployment target

### Frontend Architecture
- **Speech Recognition**: Web Speech API (webkitSpeechRecognition/SpeechRecognition)
- **Text-to-Speech**: Web Speech Synthesis API
- **UI Framework**: Vanilla JavaScript with modern CSS
- **Styling**: Custom CSS with Font Awesome icons

### Data Flow
1. User speaks into microphone → Web Speech API captures audio
2. Speech converted to text → Sent to Flask backend via `/api/chat` endpoint
3. Backend processes request → Sends to Gemini API with system prompt
4. AI response received → Returned to frontend as JSON
5. Frontend receives response → Converts to speech via TTS API

## Key Components

### Backend Components
- `app.py`: Main Flask application with chat endpoint and CORS configuration
- `main.py`: Application entry point for development server
- System prompt configuration for Swarangi's personality and interview context

### Frontend Components
- `templates/index.html`: Main interface with voice chat controls
- `static/script.js`: Voice recognition, API communication, and TTS functionality
- `static/style.css`: Modern UI styling with gradient backgrounds and responsive design

### AI Personality Configuration
The system uses Swarangi's authentic background including:
- Mathematics background transitioning to data science
- Real projects (movie recommender with cosine similarity)
- Technical skills (Python, Excel automation, APIs, web scraping)
- Career goals (AI Agent Architect at Home.LLC/100x)
- Personal traits (rapid execution, learning through discomfort)
- Communication style (ownership, energy, clarity, under 100 words)

## Data Flow

### Voice Interaction Flow
1. **Speech Input**: User clicks record button → Speech recognition starts
2. **Text Conversion**: Audio captured → Converted to text transcript
3. **API Request**: Text sent to `/api/chat` endpoint with user message
4. **AI Processing**: Backend forwards to Gemini API with system prompt context
5. **Response Generation**: AI generates contextual interview response
6. **Voice Output**: Response converted to speech and played to user

### Error Handling
- Speech recognition errors trigger retry prompts
- API failures return structured error responses
- Missing API key configuration handled gracefully

## External Dependencies

### APIs and Services
- **Google Gemini API**: Core conversational AI functionality
- **Web Speech API**: Browser-native speech recognition and synthesis
- **Font Awesome**: Icon library for UI elements

### Python Dependencies
- `flask>=3.1.1`: Web framework
- `flask-cors>=6.0.1`: Cross-origin resource sharing
- `requests>=2.32.4`: HTTP client for API calls
- `gunicorn>=23.0.0`: Production WSGI server
- `psycopg2-binary>=2.9.10`: PostgreSQL adapter (for future database integration)

## Deployment Strategy

### Production Configuration
- **Server**: Gunicorn with auto-scaling deployment target
- **Binding**: 0.0.0.0:5000 with port reuse and reload enabled
- **Environment**: Nix-based environment with Python 3.11, OpenSSL, and PostgreSQL

### Environment Variables
- `GEMINI_API_KEY`: Required for AI functionality
- `SESSION_SECRET`: Flask session security (defaults to dev key)

### Replit Configuration
- Parallel workflow execution with application startup task
- Automatic port detection and forwarding on port 5000
- Development and production run configurations

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- June 17, 2025. Initial setup
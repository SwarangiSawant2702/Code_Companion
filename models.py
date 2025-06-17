from app import db
from datetime import datetime


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), nullable=False, index=True)
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    response_time_seconds = db.Column(db.Float)
    
    def __repr__(self):
        return f'<Conversation {self.id}: {self.user_message[:50]}...>'


class InterviewSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_questions = db.Column(db.Integer, default=0)
    user_agent = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    
    def __repr__(self):
        return f'<InterviewSession {self.session_id}>'


class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    total_sessions = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    avg_response_time = db.Column(db.Float)
    most_common_question = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Analytics {self.date}>'
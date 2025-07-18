from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    bio = db.Column(db.Text)
    interests = db.Column(db.Text)
    dating_goals = db.Column(db.String(100))
    personality_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Отношения
    chat_rooms = db.relationship('ChatRoom', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'bio': self.bio,
            'interests': self.interests,
            'dating_goals': self.dating_goals,
            'personality_type': self.personality_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.name}>'

class ChatRoom(db.Model):
    """Модель чата"""
    __tablename__ = 'chat_rooms'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    girl_name = db.Column(db.String(100), nullable=False)
    girl_description = db.Column(db.Text)
    platform = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Отношения
    messages = db.relationship('Message', backref='chat_room', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'girl_name': self.girl_name,
            'girl_description': self.girl_description,
            'platform': self.platform,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }
    
    def __repr__(self):
        return f'<ChatRoom {self.girl_name}>'

class Message(db.Model):
    """Модель сообщения"""
    __tablename__ = 'messages'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    chat_room_id = db.Column(db.String(36), db.ForeignKey('chat_rooms.id'), nullable=False)
    sender_type = db.Column(db.String(20), nullable=False)  # 'user', 'girl', 'mentor'
    message_text = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # 'text', 'analysis'
    analysis_result = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'chat_room_id': self.chat_room_id,
            'sender_type': self.sender_type,
            'message_text': self.message_text,
            'message_type': self.message_type,
            'analysis_result': self.analysis_result,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<Message {self.sender_type}: {self.message_text[:50]}...>'

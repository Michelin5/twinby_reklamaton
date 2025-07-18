from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import uuid
from dotenv import load_dotenv

from models import db, User, ChatRoom, Message
from agents import DatingMentorAgents
from utils import (extract_text_from_image, allowed_file, init_nltk, init_gigachat,
                   format_message_time, get_platform_icon, get_personality_emoji)

# Загрузка переменных окружения
load_dotenv()

# Инициализация Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dating_mentor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Создание папки для загрузок
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Инициализация расширений
db.init_app(app)
Session(app)

# Custom Jinja2 filters
app.jinja_env.filters['format_time'] = format_message_time
app.jinja_env.filters['get_platform_icon'] = get_platform_icon
app.jinja_env.filters['get_personality_emoji'] = get_personality_emoji

# Инициализация AI компонентов
llm = None
sentiment_analyzer = None
agents = None

def initialize():
    """Инициализация при старте приложения"""
    global llm, sentiment_analyzer, agents
    
    # Создание таблиц
    db.create_all()
    
    # Инициализация AI компонентов
    llm = init_gigachat()
    sentiment_analyzer = init_nltk()
    agents = DatingMentorAgents(llm, sentiment_analyzer)
    
    print("✅ Приложение инициализировано")

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/profile')
def profile():
    """Страница управления профилем"""
    users = User.query.order_by(User.created_at.desc()).all()
    current_user = None
    
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
    
    return render_template('profile.html', users=users, current_user=current_user)

@app.route('/api/create_user', methods=['POST'])
def create_user():
    """API для создания пользователя"""
    data = request.json
    
    try:
        user = User(
            name=data['name'],
            age=data['age'],
            bio=data.get('bio', ''),
            interests=data.get('interests', ''),
            dating_goals=data.get('dating_goals', ''),
            personality_type=data.get('personality_type', '')
        )
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        
        return jsonify({
            'success': True,
            'user_id': user.id,
            'message': 'Профиль создан успешно!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/select_user/<user_id>', methods=['POST'])
def select_user(user_id):
    """API для выбора активного пользователя"""
    user = User.query.get(user_id)
    if user:
        session['user_id'] = user_id
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Пользователь не найден'}), 404

@app.route('/chat')
def chat():
    """Страница чата с ментором"""
    if 'user_id' not in session:
        return redirect(url_for('profile'))
    
    user = User.query.get(session['user_id'])
    chats = ChatRoom.query.filter_by(user_id=user.id).order_by(ChatRoom.last_active.desc()).all()
    
    current_chat = None
    messages = []
    
    if 'chat_id' in session:
        current_chat = ChatRoom.query.get(session['chat_id'])
        if current_chat:
            messages = Message.query.filter_by(chat_room_id=current_chat.id)\
                                  .order_by(Message.timestamp.asc()).all()
    
    return render_template('chat.html', 
                         user=user, 
                         chats=chats, 
                         current_chat=current_chat,
                         messages=messages)

@app.route('/api/create_chat', methods=['POST'])
def create_chat():
    """API для создания чата"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    data = request.json
    
    try:
        chat = ChatRoom(
            user_id=session['user_id'],
            girl_name=data['girl_name'],
            girl_description=data.get('girl_description', ''),
            platform=data['platform']
        )
        db.session.add(chat)
        db.session.commit()
        
        session['chat_id'] = chat.id
        
        return jsonify({
            'success': True,
            'chat_id': chat.id,
            'message': f'Диалог с {chat.girl_name} создан!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/select_chat/<chat_id>', methods=['POST'])
def select_chat(chat_id):
    """API для выбора активного чата"""
    chat = ChatRoom.query.get(chat_id)
    if chat and chat.user_id == session.get('user_id'):
        session['chat_id'] = chat_id
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Чат не найден'}), 404

@app.route('/api/send_message', methods=['POST'])
def send_message():
    """API для отправки сообщения"""
    if 'chat_id' not in session:
        return jsonify({'success': False, 'error': 'Чат не выбран'}), 400
    
    data = request.json
    chat = ChatRoom.query.get(session['chat_id'])
    
    if not chat:
        return jsonify({'success': False, 'error': 'Чат не найден'}), 404
    
    try:
        # Создаем сообщение
        message = Message(
            chat_room_id=chat.id,
            sender_type=data['sender_type'],
            message_text=data['message_text']
        )
        
        # Анализируем сообщение
        if agents:
            analysis = agents.analyze_conversation(
                chat.id, 
                data['message_text'], 
                data['sender_type'],
                chat,
                Message.query.filter_by(chat_room_id=chat.id).order_by(Message.timestamp.asc()).limit(10).all()
            )
            message.analysis_result = analysis
            
            # Добавляем сообщение ментора
            mentor_message = Message(
                chat_room_id=chat.id,
                sender_type='mentor',
                message_text=analysis,
                message_type='analysis'
            )
            db.session.add(mentor_message)
        
        db.session.add(message)
        
        # Обновляем время последней активности
        chat.last_active = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Сообщение добавлено',
            'analysis': message.analysis_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/analyze')
def analyze():
    """Страница анализа анкеты"""
    if 'user_id' not in session:
        return redirect(url_for('profile'))
    
    user = User.query.get(session['user_id'])
    return render_template('analyze.html', user=user)

@app.route('/api/analyze_profile', methods=['POST'])
def analyze_profile():
    """API для анализа анкеты"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    profile_text = ''
    
    # Проверка загруженного файла
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Извлечение текста из изображения
            profile_text = extract_text_from_image(filepath)
            
            # Удаление временного файла
            os.remove(filepath)
    
    # Или текст из формы
    if not profile_text and 'text' in request.form:
        profile_text = request.form['text']
    
    if not profile_text:
        return jsonify({
            'success': False,
            'error': 'Не предоставлен текст для анализа'
        }), 400
    
    # Анализ
    if agents:
        user = User.query.get(session['user_id'])
        analysis = agents.analyze_profile(user, profile_text)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'extracted_text': profile_text
        })
    
    return jsonify({
        'success': False,
        'error': 'AI агент не инициализирован'
    }), 500

@app.route('/api/generate_examples', methods=['POST'])
def generate_examples():
    """API для генерации примеров сообщений"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    
    data = request.json
    context = data.get('context', 'general')
    
    if agents:
        user = User.query.get(session['user_id'])
        examples = agents.generate_examples(user, context)
        
        return jsonify({
            'success': True,
            'examples': examples
        })
    
    return jsonify({
        'success': False,
        'error': 'AI агент не инициализирован'
    }), 500

@app.route('/api/photo_advice')
def photo_advice():
    """API для советов по фото"""
    if agents:
        advice = agents.photo_advisor()
        return jsonify({
            'success': True,
            'advice': advice
        })
    
    return jsonify({
        'success': False,
        'error': 'AI агент не инициализирован'
    }), 500

@app.route('/api/check_grammar', methods=['POST'])
def check_grammar():
    """API для проверки грамматики"""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({
            'success': False,
            'error': 'Текст не предоставлен'
        }), 400
    
    # Здесь будет проверка грамматики
    # Пока возвращаем заглушку
    return jsonify({
        'success': True,
        'corrections': [],
        'message': 'Функция проверки грамматики будет добавлена в следующей версии'
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


if __name__ == '__main__':
    with app.app_context():
        initialize()
    app.run(debug=True, host='0.0.0.0', port=5000)


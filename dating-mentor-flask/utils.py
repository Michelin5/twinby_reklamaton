import os
import pytesseract
from PIL import Image
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import language_tool_python

# Проверка доступности библиотек
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    from langchain_community.chat_models import GigaChat
    from langchain.schema import HumanMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False

try:
    import language_tool_python
    GRAMMAR_AVAILABLE = True
except ImportError:
    GRAMMAR_AVAILABLE = False

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    """Проверка разрешенного расширения файла"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_image(filepath):
    """Извлечение текста из изображения с помощью OCR"""
    if not OCR_AVAILABLE:
        return "❌ OCR недоступен. Установите pytesseract: pip install pytesseract"
    
    try:
        # Открываем изображение
        image = Image.open(filepath)
        
        # Конвертируем в RGB если необходимо
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Извлекаем текст
        text = pytesseract.image_to_string(image, lang='rus+eng')
        
        # Очищаем текст
        text = text.strip()
        
        if not text:
            return "Не удалось извлечь текст из изображения. Попробуйте другое изображение или введите текст вручную."
        
        return text
        
    except Exception as e:
        return f"Ошибка при извлечении текста: {str(e)}"

def init_nltk():
    """Инициализация NLTK для анализа тональности"""
    if not SENTIMENT_AVAILABLE:
        print("⚠️ NLTK не установлен. Анализ тональности недоступен.")
        return None
    
    try:
        # Проверяем наличие необходимых данных
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            print("Загружаем VADER lexicon...")
            nltk.download('vader_lexicon', quiet=True)
        
        # Создаем анализатор
        sia = SentimentIntensityAnalyzer()
        print("✅ NLTK инициализирован")
        return sia
        
    except Exception as e:
        print(f"❌ Ошибка инициализации NLTK: {str(e)}")
        return None

def init_gigachat():
    """Инициализация GigaChat"""
    if not LLM_AVAILABLE:
        print("⚠️ LangChain не установлен. AI функции недоступны.")
        return None
    
    # Получаем API ключ
    api_key = os.getenv("GIGACHAT_API_KEY")
    
    if not api_key:
        print("⚠️ Не найден GIGACHAT_API_KEY. Добавьте его в .env файл.")
        print("ℹ️ Работаем в демо-режиме без AI")
        return None
    
    try:
        # Создаем клиент GigaChat
        llm = GigaChat(
            credentials=api_key,
            model="GigaChat-Max",
            temperature=0.7,
            verify_ssl_certs=False
        )
        
        # Тестируем подключение
        test_response = llm.invoke([HumanMessage(content="Тест")])
        print("✅ GigaChat инициализирован")
        return llm
        
    except Exception as e:
        print(f"❌ Ошибка инициализации GigaChat: {str(e)}")
        print("ℹ️ Работаем в демо-режиме без AI")
        return None

def check_grammar(text):
    """Проверка грамматики текста"""
    if not GRAMMAR_AVAILABLE:
        return {
            'success': False,
            'error': 'language_tool_python не установлен. Установите: pip install language-tool-python'
        }
    
    try:
        # Создаем инструмент для проверки
        tool = language_tool_python.LanguageTool('ru')
        
        # Проверяем текст
        matches = tool.check(text)
        
        # Формируем результат
        corrections = []
        for match in matches:
            corrections.append({
                'message': match.message,
                'replacements': match.replacements[:3],  # Первые 3 варианта
                'offset': match.offset,
                'length': match.errorLength,
                'rule': match.ruleId
            })
        
        # Закрываем инструмент
        tool.close()
        
        return {
            'success': True,
            'corrections': corrections,
            'total': len(corrections)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Ошибка проверки: {str(e)}'
        }

def format_message_time(timestamp):
    """Форматирование времени сообщения"""
    from datetime import datetime
    
    try:
        # Если timestamp уже datetime объект
        if isinstance(timestamp, datetime):
            dt = timestamp
        else:
            # Пробуем распарсить строку
            dt = datetime.fromisoformat(str(timestamp))
        
        # Определяем формат в зависимости от давности
        now = datetime.utcnow()
        diff = now - dt
        
        if diff.days == 0:
            # Сегодня - показываем только время
            return dt.strftime("%H:%M")
        elif diff.days == 1:
            # Вчера
            return f"Вчера в {dt.strftime('%H:%M')}"
        elif diff.days < 7:
            # На этой неделе - день недели
            days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
            return f"{days[dt.weekday()]} в {dt.strftime('%H:%M')}"
        else:
            # Больше недели - полная дата
            return dt.strftime("%d.%m.%Y %H:%M")
            
    except Exception as e:
        return str(timestamp)

def sanitize_html(text):
    """Очистка текста для безопасного отображения в HTML"""
    import html
    
    if not text:
        return ""
    
    # Экранируем HTML символы
    text = html.escape(text)
    
    # Заменяем переносы строк на <br>
    text = text.replace('\n', '<br>')
    
    # Заменяем двойные пробелы
    text = text.replace('  ', '&nbsp;&nbsp;')
    
    return text

def get_platform_icon(platform):
    """Получение иконки для платформы знакомств"""
    icons = {
        'Tinder': 'fab fa-tinder',
        'Bumble': 'fas fa-bee',
        'Instagram': 'fab fa-instagram',
        'VK': 'fab fa-vk',
        'Telegram': 'fab fa-telegram',
        'WhatsApp': 'fab fa-whatsapp',
        'Facebook': 'fab fa-facebook',
        'Badoo': 'fas fa-heart',
        'Другое': 'fas fa-comments'
    }
    
    return icons.get(platform, 'fas fa-comments')

def get_personality_emoji(personality_type):
    """Получение эмодзи для типа личности"""
    emojis = {
        'Экстраверт': '🎉',
        'Интроверт': '🤔',
        'Амбиверт': '🤝',
        'Не знаю': '❓'
    }
    
    return emojis.get(personality_type, '👤')

def get_goal_icon(dating_goal):
    """Получение иконки для целей знакомств"""
    icons = {
        'Серьезные отношения': 'fas fa-ring',
        'Легкое общение': 'fas fa-coffee',
        'Дружба': 'fas fa-user-friends',
        'Не определился': 'fas fa-question-circle'
    }
    
    return icons.get(dating_goal, 'fas fa-heart')

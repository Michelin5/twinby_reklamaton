import os
from typing import Optional, Dict, List
import json

class DatingMentorAgents:
    """Класс с AI агентами для анализа и советов"""
    
    def __init__(self, llm=None, sentiment_analyzer=None):
        self.llm = llm
        self.sia = sentiment_analyzer
    
    def get_user_context(self, user) -> Dict:
        """Получение контекста пользователя"""
        return {
            'name': user.name,
            'age': user.age,
            'bio': user.bio,
            'interests': user.interests,
            'dating_goals': user.dating_goals,
            'personality_type': user.personality_type
        }
    
    def analyze_profile(self, user, profile_text: str) -> str:
        """Анализ анкеты пользователя"""
        if not profile_text.strip():
            return """
            <div class="alert alert-danger">
                <h4>❌ Пустая анкета!</h4>
                <p>Добавьте информацию о себе, чтобы получить персонализированные советы.</p>
            </div>
            """
        
        if not self.llm:
            return self._format_error("LLM недоступен. Проверьте настройки GigaChat.")
        
        user_context = self.get_user_context(user)
        
        prompt = f"""
Ты - персональный эксперт по онлайн-знакомствам. Проанализируй анкету с учетом личности пользователя.

ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ:
- Имя: {user_context['name']}
- Возраст: {user_context['age']}
- Интересы: {user_context['interests']}
- Цели знакомств: {user_context['dating_goals']}
- Тип личности: {user_context['personality_type']}

АНКЕТА ДЛЯ АНАЛИЗА:
{profile_text}

Дай ПЕРСОНАЛИЗИРОВАННЫЙ анализ в формате HTML с использованием Bootstrap классов:

<div class="analysis-result">
    <div class="section">
        <h4><i class="fas fa-check-circle text-success"></i> Сильные стороны</h4>
        <ul>
            <li>...</li>
        </ul>
    </div>
    
    <div class="section">
        <h4><i class="fas fa-exclamation-triangle text-warning"></i> Что можно улучшить</h4>
        <ul>
            <li>...</li>
        </ul>
    </div>
    
    <div class="section">
        <h4><i class="fas fa-lightbulb text-info"></i> Персональные рекомендации</h4>
        <ul>
            <li>...</li>
        </ul>
    </div>
    
    <div class="section">
        <h4><i class="fas fa-magic text-primary"></i> Примеры улучшенных формулировок</h4>
        <div class="examples">
            <p><strong>Вместо:</strong> "..."</p>
            <p><strong>Лучше:</strong> "..."</p>
        </div>
    </div>
</div>

Учитывай личность и цели пользователя в советах! Используй эмодзи для визуального акцента.
"""
        
        try:
            if hasattr(self.llm, 'invoke'):
                print("[DEBUG] Вызов llm.invoke с prompt (analyze_profile)")
                response = self.llm.invoke(prompt)
                print("[DEBUG] Ответ llm.invoke получен")
                # Проверяем, что есть поле content, иначе возвращаем как есть
                if hasattr(response, 'content'):
                    return response.content
                else:
                    return response
            else:
                print("[DEBUG] LLM отсутствует, возвращаем демо-анализ")
                return self._get_demo_profile_analysis(user_context, profile_text)
        except Exception as e:
            print(f"[ERROR] Ошибка в analyze_profile: {str(e)}")
            return self._format_error(f"Ошибка анализа: {str(e)}")
    
    def analyze_conversation(self, chat_id: str, new_message: str, sender_type: str, 
                             chat_room, messages: List) -> str:
        """Анализ переписки"""
        if not self.llm:
            return self._format_error("LLM недоступен. Проверьте настройки GigaChat.")
        
        # Формируем историю последних 10 сообщений (без ментора)
        history_text = ""
        for msg in messages[-10:]:
            if msg.sender_type != 'mentor':
                sender = "Вы" if msg.sender_type == 'user' else chat_room.girl_name
                history_text += f"{sender}: {msg.message_text}\n"
        
        # Анализ тональности
        sentiment_text = "Недоступно"
        if self.sia:
            sentiment = self.sia.polarity_scores(new_message)
            sentiment_text = self._sentiment_to_text(sentiment)
        
        user_context = self.get_user_context(chat_room.user)
        
        prompt = f"""
Ты - эксперт по общению в знакомствах. Проанализируй сообщение в контексте диалога.

ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ:
- Личность: {user_context['personality_type']}
- Цели: {user_context['dating_goals']}

ИНФОРМАЦИЯ О ДЕВУШКЕ:
- Имя: {chat_room.girl_name}
- Описание: {chat_room.girl_description}
- Платформа: {chat_room.platform}

ИСТОРИЯ ДИАЛОГА:
{history_text}

НОВОЕ СООБЩЕНИЕ ({sender_type}): {new_message}
Тональность: {sentiment_text}

Дай анализ в формате HTML:

<div class="conversation-analysis">
    <div class="alert alert-info">
        <h5><i class="fas fa-chart-line"></i> Динамика диалога</h5>
        <p>...</p>
    </div>
    
    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title"><i class="fas fa-brain"></i> Анализ подтекста</h5>
                    <p>...</p>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title"><i class="fas fa-heart"></i> Уровень интереса</h5>
                    <div class="progress">
                        <div class="progress-bar" style="width: X%">X%</div>
                    </div>
                    <p class="mt-2">...</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="suggestions mt-3">
        <h5><i class="fas fa-comments"></i> Варианты ответа</h5>
        <div class="response-option">
            <span class="badge badge-success">Флирт</span>
            <p>"..."</p>
        </div>
        <div class="response-option">
            <span class="badge badge-info">Нейтрально</span>
            <p>"..."</p>
        </div>
        <div class="response-option">
            <span class="badge badge-warning">Серьезно</span>
            <p>"..."</p>
        </div>
    </div>
</div>
"""
        
        try:
            if hasattr(self.llm, 'invoke'):
                print("[DEBUG] Вызов llm.invoke с prompt (analyze_conversation)")
                response = self.llm.invoke(prompt)
                print("[DEBUG] Ответ llm.invoke получен")
                if hasattr(response, 'content'):
                    return response.content
                else:
                    return response
            else:
                print("[DEBUG] LLM отсутствует, возвращаем демо-анализ переписки")
                return self._get_demo_conversation_analysis(sender_type, new_message, sentiment_text)
        except Exception as e:
            print(f"[ERROR] Ошибка в analyze_conversation: {str(e)}")
            return self._format_error(f"Ошибка анализа: {str(e)}")
    
    def generate_examples(self, user, context: str = "general") -> str:
        """Генерация примеров сообщений"""
        if not self.llm:
            return self._format_error("LLM недоступен. Проверьте настройки GigaChat.")
        
        user_context = self.get_user_context(user)
        
        context_map = {
            "general": "общие знакомства",
            "dating_app": "знакомства в приложениях (Tinder, Bumble)",
            "social_media": "знакомства в соцсетях (Instagram, VK)",
            "professional": "деловые знакомства"
        }
        
        context_desc = context_map.get(context, context)
        
        prompt = f"""
Создай ПЕРСОНАЛИЗИРОВАННЫЕ примеры сообщений для знакомств.

ТВОЯ ЛИЧНОСТЬ:
- Возраст: {user_context['age']}
- Интересы: {user_context['interests']}
- Цели: {user_context['dating_goals']}
- Тип личности: {user_context['personality_type']}

Контекст: {context_desc}

Создай примеры в формате HTML:

<div class="examples-container">
    <div class="good-examples">
        <h4><i class="fas fa-thumbs-up text-success"></i> Хорошие примеры</h4>
        
        <div class="example-card good">
            <div class="example-text">
                "..."
            </div>
            <div class="example-explanation">
                <i class="fas fa-info-circle"></i> Почему это работает: ...
            </div>
        </div>
        
        <!-- Еще 2-3 примера -->
    </div>
    
    <div class="bad-examples mt-4">
        <h4><i class="fas fa-thumbs-down text-danger"></i> Примеры, которых стоит избегать</h4>
        
        <div class="example-card bad">
            <div class="example-text">
                "..."
            </div>
            <div class="example-explanation">
                <i class="fas fa-exclamation-circle"></i> Почему это плохо: ...
            </div>
        </div>
        
        <!-- Еще 2-3 примера -->
    </div>
</div>
"""
        
        try:
            if hasattr(self.llm, 'invoke'):
                print("[DEBUG] Вызов llm.invoke с prompt (generate_examples)")
                response = self.llm.invoke(prompt)
                print("[DEBUG] Ответ llm.invoke получен")
                if hasattr(response, 'content'):
                    return response.content
                else:
                    return response
            else:
                print("[DEBUG] LLM отсутствует, возвращаем демо-примеры")
                return self._get_demo_examples(user_context, context_desc)
        except Exception as e:
            print(f"[ERROR] Ошибка в generate_examples: {str(e)}")
            return self._format_error(f"Ошибка генерации: {str(e)}")
    
    def photo_advisor(self) -> str:
        """Советы по фото"""
        return """
<div class="photo-advice">
    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4><i class="fas fa-camera"></i> Основные правила</h4>
                </div>
                <div class="card-body">
                    <ul class="list-unstyled">
                        <li><i class="fas fa-check text-success"></i> <strong>Главное фото:</strong> лицо крупным планом, улыбка</li>
                        <li><i class="fas fa-check text-success"></i> <strong>Освещение:</strong> естественный свет (у окна, на улице)</li>
                        <li><i class="fas fa-check text-success"></i> <strong>Фон:</strong> простой, не отвлекающий</li>
                        <li><i class="fas fa-check text-success"></i> <strong>Одежда:</strong> чистая, по фигуре, подходящая стилю</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="card">
                <div class="card-header bg-danger text-white">
                    <h4><i class="fas fa-times-circle"></i> Чего избегать</h4>
                </div>
                <div class="card-body">
                    <ul class="list-unstyled">
                        <li><i class="fas fa-times text-danger"></i> Фото с бывшими (даже обрезанные)</li>
                        <li><i class="fas fa-times text-danger"></i> Слишком много селфи</li>
                        <li><i class="fas fa-times text-danger"></i> Фильтры, сильно меняющие внешность</li>
                        <li><i class="fas fa-times text-danger"></i> Размытые/темные фото</li>
                        <li><i class="fas fa-times text-danger"></i> Алкоголь в руках</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-3">
        <div class="col-md-6">
            <div class="card border-info">
                <div class="card-header bg-info text-white">
                    <h4><i class="fas fa-male"></i> Для мужчин</h4>
                </div>
                <div class="card-body">
                    <ul>
                        <li>Легкая серьезность + уверенный взгляд</li>
                        <li>Показать хобби (спорт, путешествия)</li>
                        <li>Избегать селфи в зеркале</li>
                        <li>Групповые фото: вы должны выделяться</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="card border-pink">
                <div class="card-header bg-pink text-white">
                    <h4><i class="fas fa-female"></i> Для женщин</h4>
                </div>
                <div class="card-body">
                    <ul>
                        <li>Естественная улыбка</li>
                        <li>Разные ракурсы и активности</li>
                        <li>Макияж умеренный, естественный</li>
                        <li>Показать интересы и стиль жизни</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
"""
    
    def _sentiment_to_text(self, sentiment: Dict) -> str:
        """Преобразование результата анализа тональности в текст"""
        compound = sentiment['compound']
        if compound >= 0.05:
            return "Позитивная 😊"
        elif compound <= -0.05:
            return "Негативная 😔"
        else:
            return "Нейтральная 😐"
    
    def _format_error(self, error_message: str) -> str:
        """Форматирование сообщения об ошибке"""
        return f"""
<div class="alert alert-danger">
    <h4><i class="fas fa-exclamation-circle"></i> Ошибка</h4>
    <p>{error_message}</p>
</div>
"""
    
    def _get_demo_profile_analysis(self, user_context: Dict, profile_text: str) -> str:
        """Демо-анализ профиля"""
        return f"""
<div class="analysis-result">
    <div class="section">
        <h4><i class="fas fa-check-circle text-success"></i> Сильные стороны</h4>
        <ul>
            <li>✅ Вы указали свои интересы: {user_context['interests']}</li>
            <li>✅ Четко обозначены цели знакомств: {user_context['dating_goals']}</li>
            <li>✅ Анкета отражает вашу личность ({user_context['personality_type']})</li>
        </ul>
    </div>
    
    <div class="section">
        <h4><i class="fas fa-exclamation-triangle text-warning"></i> Что можно улучшить</h4>
        <ul>
            <li>⚠️ Добавьте больше конкретных деталей о своих увлечениях</li>
            <li>⚠️ Расскажите о том, что делает вас уникальным</li>
            <li>⚠️ Укажите, какого партнера вы ищете</li>
        </ul>
    </div>
    
    <div class="section">
        <h4><i class="fas fa-lightbulb text-info"></i> Персональные рекомендации</h4>
        <ul>
            <li>💡 Для {user_context['personality_type']} важно показать свою глубину</li>
            <li>💡 В {user_context['age']} лет стоит подчеркнуть стабильность и зрелость</li>
            <li>💡 Добавьте юмор, чтобы сделать анкету более живой</li>
        </ul>
    </div>
    
    <div class="section">
        <h4><i class="fas fa-magic text-primary"></i> Примеры улучшенных формулировок</h4>
        <div class="examples">
            <p><strong>Вместо:</strong> "Люблю путешествовать"</p>
            <p><strong>Лучше:</strong> "Последний раз был в Таиланде, мечтаю о поездке в Японию. А куда мечтаешь поехать ты?"</p>
        </div>
    </div>
</div>
"""
    
    def _get_demo_conversation_analysis(self, sender_type: str, message: str, sentiment: str) -> str:
        """Демо-анализ переписки"""
        interest_level = 75 if sender_type == 'girl' else 60
        
        return f"""
<div class="conversation-analysis">
    <div class="alert alert-info">
        <h5><i class="fas fa-chart-line"></i> Динамика диалога</h5>
        <p>Диалог развивается позитивно. Тональность сообщения: {sentiment}. 
        {'Она проявляет интерес, задавая вопросы.' if sender_type == 'girl' else 'Ваше сообщение показывает заинтересованность.'}</p>
    </div>
    
    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title"><i class="fas fa-brain"></i> Анализ подтекста</h5>
                    <p>{'Девушка открыта к общению и хочет узнать вас лучше.' if sender_type == 'girl' else 'Вы показываете искренний интерес к собеседнице.'}</p>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title"><i class="fas fa-heart"></i> Уровень интереса</h5>
                    <div class="progress">
                        <div class="progress-bar bg-success" style="width: {interest_level}%">{interest_level}%</div>
                    </div>
                    <p class="mt-2">{'Высокий уровень заинтересованности!' if interest_level > 70 else 'Умеренный интерес, есть потенциал.'}</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="suggestions mt-3">
        <h5><i class="fas fa-comments"></i> Варианты ответа</h5>
        <div class="response-option">
            <span class="badge badge-success">Флирт</span>
            <p>"Знаешь, твоя улыбка на фото просто покорила меня 😊 Расскажи, что тебя вдохновляет?"</p>
        </div>
        <div class="response-option">
            <span class="badge badge-info">Нейтрально</span>
            <p>"Интересно! А как ты обычно проводишь выходные? Любишь активный отдых или предпочитаешь что-то спокойное?"</p>
        </div>
        <div class="response-option">
            <span class="badge badge-warning">Серьезно</span>
            <p>"Мне нравится твой подход к жизни. Расскажи, какие у тебя планы на будущее?"</p>
        </div>
    </div>
</div>
"""
    
    def _get_demo_examples(self, user_context: Dict, context: str) -> str:
        """Демо-примеры сообщений"""
        first_interest = user_context['interests'].split(',')[0] if user_context['interests'] else 'путешествиями'
        return f"""
<div class="examples-container">
    <div class="good-examples">
        <h4><i class="fas fa-thumbs-up text-success"></i> Хорошие примеры для {context}</h4>
        
        <div class="example-card good">
            <div class="example-text">
                "Привет! Заметил, что ты тоже увлекаешься {first_interest}. Какое место произвело на тебя самое большое впечатление?"
            </div>
            <div class="example-explanation">
                <i class="fas fa-info-circle"></i> Почему это работает: Персонализированное обращение, общий интерес, открытый вопрос
            </div>
        </div>
        
        <div class="example-card good">
            <div class="example-text">
                "Твоя улыбка на третьем фото просто заразительная! 😊 Это было на каком-то особенном мероприятии?"
            </div>
            <div class="example-explanation">
                <i class="fas fa-info-circle"></i> Почему это работает: Конкретный комплимент, позитивная эмоция, вопрос для продолжения диалога
            </div>
        </div>
    </div>
    
    <div class="bad-examples mt-4">
        <h4><i class="fas fa-thumbs-down text-danger"></i> Примеры, которых стоит избегать</h4>
        
        <div class="example-card bad">
            <div class="example-text">
                "Привет, красотка! Хочешь познакомиться?"
            </div>
            <div class="example-explanation">
                <i class="fas fa-exclamation-circle"></i> Почему это плохо: Слишком банально, поверхностно, нет зацепок для диалога
            </div>
        </div>
        
        <div class="example-card bad">
            <div class="example-text">
                "Ты такая красивая, что я забыл что хотел сказать 😅"
            </div>
            <div class="example-explanation">
                <i class="fas fa-exclamation-circle"></i> Почему это плохо: Заезженная фраза, отсутствие оригинальности, фокус только на внешности
            </div>
        </div>
    </div>
</div>
"""


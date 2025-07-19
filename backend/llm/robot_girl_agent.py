from .llm_client import call_llm
import json
import os
from datetime import datetime
from typing import List, Dict


class RobotGirlAgent:
    def __init__(self, name: str = "Анна", age: int = 21, interests: List[str] = None,
                 personality: str = "дружелюбная"):
        """
        Инициализация агента женщины для дейтинг приложения

        Args:
            name: Имя персонажа
            age: Возраст
            interests: Список интересов
            personality: Тип личности (дружелюбная, игривая, серьезная, романтичная)
        """
        self.name = name
        self.age = age
        self.interests = interests or ["фотография", "путешествия", "чтение", "йога", "кулинария"]
        self.personality = personality

        # Память диалогов
        self.conversation_history: List[Dict] = []
        self.memory_file = f"conversation_memory_{name.lower()}.json"

        # Загружаем историю из файла, если существует
        self._load_memory()

        # Системный промпт
        self.system_prompt = self._create_system_prompt()

    def _create_system_prompt(self) -> str:
        """Создает системный промпт для персонажа"""
        interests_str = ", ".join(self.interests)

        personality_traits = {
            "дружелюбная": "Ты открытая, добрая и легко идешь на контакт. Любишь поддерживать беседу и интересуешься собеседником.",
            "игривая": "Ты веселая, любишь шутки и флирт. Часто используешь эмодзи и игривые фразы.",
            "серьезная": "Ты интеллектуальная и вдумчивая. Предпочитаешь глубокие разговоры поверхностным.",
            "романтичная": "Ты мечтательная и чувственная. Любишь говорить о чувствах и романтике."
        }

        personality_description = personality_traits.get(self.personality, personality_traits["дружелюбная"])

        return f"""Ты {self.name}, {self.age}-летняя девушка, которая общается в дейтинг приложении. 

ТВОЯ ЛИЧНОСТЬ:
{personality_description}

ТВОИ ИНТЕРЕСЫ: {interests_str}

ПРАВИЛА ОБЩЕНИЯ:
1. Отвечай естественно и по-женски, как реальная девушка
2. Проявляй интерес к собеседнику, задавай вопросы о нем
3. Используй эмодзи умеренно и уместно
4. Не будь слишком навязчивой, но и не отстраненной
5. Если парень пишет что-то неуместное или грубое - вежливо, но четко дай понять, что это неприемлемо
6. Поддерживай беседу, развивай темы разговора
7. Иногда можешь немного флиртовать, но в рамках приличия
8. Помни о предыдущих сообщениях в разговоре и ссылайся на них
9. Пиши сообщения среднего размера (1-3 предложения обычно)
10. Отвечай только на русском языке

ВАЖНО: Ты настоящая девушка с чувствами и эмоциями. Веди себя естественно!"""

    def _load_memory(self):
        """Загружает историю разговора из файла"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
                print(f"[ПАМЯТЬ] Загружено {len(self.conversation_history)} сообщений из памяти")
            except Exception as e:
                print(f"[ОШИБКА] Не удалось загрузить память: {e}")
                self.conversation_history = []

    def _save_memory(self):
        """Сохраняет историю разговора в файл"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ОШИБКА] Не удалось сохранить память: {e}")

    def _add_to_memory(self, role: str, message: str):
        """Добавляет сообщение в память"""
        self.conversation_history.append({
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        self._save_memory()

    def _get_conversation_context(self) -> str:
        """Формирует контекст разговора из истории"""
        if not self.conversation_history:
            return "Это начало вашего разговора."

        context = "ИСТОРИЯ РАЗГОВОРА:\n"
        # Берем последние 10 сообщений для контекста
        recent_messages = self.conversation_history[-10:]

        for msg in recent_messages:
            role_name = "Парень" if msg["role"] == "user" else self.name
            context += f"{role_name}: {msg['message']}\n"

        return context

    def respond_to_message(self, user_message: str) -> str:
        """
        Отвечает на сообщение пользователя

        Args:
            user_message: Сообщение от парня

        Returns:
            Ответ девушки
        """
        # Добавляем сообщение пользователя в память
        self._add_to_memory("user", user_message)

        # Формируем контекст
        conversation_context = self._get_conversation_context()

        # Создаем промпт с контекстом
        prompt = f"""{conversation_context}

НОВОЕ СООБЩЕНИЕ ОТ ПАРНЯ: {user_message}

Ответь как {self.name}, учитывая всю историю разговора выше."""

        # Получаем ответ от LLM
        response = call_llm(prompt, self.system_prompt)

        # Добавляем ответ в память
        self._add_to_memory("assistant", response)

        return response

    def clear_memory(self):
        """Очищает память разговора"""
        self.conversation_history = []
        if os.path.exists(self.memory_file):
            os.remove(self.memory_file)
        print(f"[ПАМЯТЬ] Память {self.name} очищена")

    def __str__(self):
        return f"RobotGirlAgent(name='{self.name}', age={self.age}, personality='{self.personality}')"

    def chat_loop(self):
        """Запускает интерактивный чат с пользователем"""
        print("=" * 50)
        print(f"💬 ЧАТ С {self.name.upper()}")
        print("=" * 50)
        print(f"Привет! Я {self.name}, {self.age} лет. Давай знакомиться! 😊")
        print("(Напиши 'Пока' чтобы закончить разговор)")
        print("-" * 50)

        while True:
            try:
                # Получаем сообщение от пользователя
                user_input = input("\n💬 Ты: ").strip()

                # Проверяем условие выхода
                if user_input.lower() in ["пока", "bye", "exit", "quit"]:
                    # Генерируем прощальное сообщение
                    farewell_prompt = f"Парень прощается с тобой, написав: '{user_input}'. Попрощайся с ним тепло и мило, как {self.name}."
                    farewell_response = call_llm(farewell_prompt, self.system_prompt)
                    print(f"💕 {self.name}: {farewell_response}")

                    # Сохраняем прощальные сообщения в память
                    self._add_to_memory("user", user_input)
                    self._add_to_memory("assistant", farewell_response)

                    # Показываем финальную статистику
                    final_stats = self.get_conversation_stats()
                    print(f"\n📊 Статистика разговора:")
                    print(f"   Всего сообщений: {final_stats['total_messages']}")
                    print(f"   Твоих сообщений: {final_stats['user_messages']}")
                    print(f"   Сообщений {self.name}: {final_stats['assistant_messages']}")
                    print("\n👋 До свидания!")
                    break

                # Проверяем, что сообщение не пустое
                if not user_input:
                    print("❌ Напиши что-нибудь!")
                    continue

                # Получаем ответ от агента
                print(f"💭 {self.name} печатает...")
                response = self.respond_to_message(user_input)
                print(f"💕 {self.name}: {response}")

            except KeyboardInterrupt:
                print(f"\n\n👋 {self.name}: Пока-пока! 💋")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                print("Попробуй еще раз!")


# Пример использования
if __name__ == "__main__":
    # Создаем агента
    girl = RobotGirlAgent(
        name="Анна",
        age=25,
        interests=["фотография", "путешествия", "музыка", "кулинария"],
        personality="дружелюбная"
    )

    print(f"🤖 Создан агент: {girl}")

    # Запускаем интерактивный чат
    girl.chat_loop()

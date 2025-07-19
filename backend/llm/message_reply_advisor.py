# backend/llm/message_reply_advisor.py
from .llm_client import call_llm

class MessageReplyAdvisor:
    def suggest_reply(self, conversation_history: list, last_message: str) -> str:
        context = "\n".join([
            f"Парень: {m['message']}" if m['role'] == 'user' else f"Девушка: {m['message']}"
            for m in conversation_history[-10:]
        ])

        system_instruction = f"""
        Ты — эксперт по знакомствам. Вот история общения:
        {context}

        Дай короткий совет, как парню лучше ответить на это сообщение, чтобы произвести хорошее впечатление. 
        Общайся с юзером как с лучши другом и давай дельные советы.
        """

        prompt = f"""
        Последнее сообщение от девушки: {last_message}
        """
        return call_llm(prompt, system_instruction)

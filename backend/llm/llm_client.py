from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
import requests

load_dotenv(override=True)

# --- Настройка GigaChat ---
GIGA_CREDENTIALS = os.environ.get("GIGACHAT_TOKEN")
giga_client = None

try:
    giga_client = GigaChat(credentials=GIGA_CREDENTIALS, verify_ssl_certs=False, model="GigaChat-2-Max")
except Exception as e:
    print(f"[ОШИБКА GigaChat Init] {e}")

def call_llm(prompt_text, system_instruction):
    if giga_client is None: return "[ОШИБКА API] Клиент GigaChat не инициализирован."
    # print(f"\nВызов GigaChat: Системная инструкция (начало): {system_instruction[:100]}... Промпт: {prompt_text[:100]}...")
    try:
        messages = [SystemMessage(content=system_instruction), HumanMessage(content=prompt_text)]
        res = giga_client.invoke(messages)
        # print(f"GigaChat ответ (начало): {res.content[:100]}...")
        return res.content.strip()
    except Exception as e:
        print(f"Ошибка вызова GigaChat API: {e}")
        return f"[ОШИБКА API] {e}"

def call_llm_image(image_path):
    if giga_client is None: return "[ОШИБКА API] Клиент GigaChat не инициализирован."

    file = giga_client.upload_file(open(image_path, "rb"), purpose="general")
    print(file)

    system_instruction = (
            "Ты — опытный дейтинг-коуч и психолог, который помогает людям с вопросами о знакомствах и отношениях. "
            "Твои ответы должны быть полезными, поддерживающими и основанными на принципах здоровых отношений. "
            "Оцени, насколько привлекательна эта фотка для анкеты на сайте знакомств, "
            "Опиши сильные и слабые стороны и дай рекомендации по улучшению. Сделай это максимально кратко и лаконично."
        )

    result = giga_client.invoke([HumanMessage(content=system_instruction,
                                              additional_kwargs={"attachments": [file.id_]})])

    return result.content.strip()
    # print(result.content.strip())

if __name__ == "__main__":
    # Пример системной инструкции и промпта
    system_instruction = "Ты вежливый помощник, который всегда отвечает на русском языке."
    prompt_text = "Расскажи интересный факт о космосе."

    # Вызов LLM
    response = call_llm(prompt_text, system_instruction)
    print("\nФинальный ответ:")
    print(response)

    call_llm_image('img.png')

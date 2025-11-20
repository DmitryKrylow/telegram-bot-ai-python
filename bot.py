import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from openai import OpenAI
from telegram.constants import ParseMode
import re
import json

file_path = 'environments.json'

# --- CONFIG ---
TELEGRAM_TOKEN = ''
OPENROUTER_API_KEY = ''
MODEL = ''

try:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    OPENROUTER_API_KEY = data.get('API_KEY', 'default_value_if_not_found')
    TELEGRAM_TOKEN = data.get('TELEGRAM_TOKEN', 'default_value_if_not_found')
    MODEL = data.get('MODEL', 'default_value_if_not_found')

except FileNotFoundError:
    print(f"Ошибка: Файл '{file_path}' не найден.")
except json.JSONDecodeError:
    print(f"Ошибка: Не удалось декодировать JSON из файла '{file_path}'. Проверьте его формат.")
except Exception as e:
    print(f"Произошла непредвиденная ошибка: {e}")


# Настройка клиента OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

logging.basicConfig(level=logging.INFO)


def escape_markdown_v2(text: str) -> str:
    special_chars = r'_[]()`>#+-=|{}.!'
    return re.sub(f'([{re.escape(special_chars)}])', r'\\\1', text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    await update.message.reply_text("⏳ Думаю...")

    try:
        response = client.chat.completions.create(
            model="x-ai/grok-4.1-fast",
            messages=[{"role": "user", "content": user_msg}]
        )

        answer = response.choices[0].message.content
        escaped_answer = escape_markdown_v2(answer)

        await update.message.reply_text(escaped_answer, parse_mode=ParseMode.MARKDOWN_V2)

    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text(f"Произошла ошибка при генерации ответа: {e}")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started!")
    await app.run_polling()


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started!")
    app.run_polling()
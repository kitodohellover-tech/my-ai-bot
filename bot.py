import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# Используем стабильную модель
MODEL = "llama-3.3-70b-versatile"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # Три разрешённых аккаунта (замени нули на реальные ID)
    ALLOWED_IDS = {
        5264513480,  # твой первый аккаунт
        8834374199,  # твой второй аккаунт
        5389046699   # третий человек
    }

    if user_id not in ALLOWED_IDS:
        await update.message.reply_text("🔒 Бот приватный. Доступ только для своих.")
        return

    user_text = update.message.text
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Ты полезный ассистент. Отвечай кратко, по делу, на русском языке."},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7
    }

    try:
        resp = requests.post(URL, json=payload, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        ai_reply = data["choices"][0]["message"]["content"]
        await update.message.reply_text(ai_reply)
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            error_msg = "Ошибка модели (404)."
        await update.message.reply_text(f"Ошибка AI: {error_msg}")


if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not GROQ_API_KEY:
        print("❌ ОШИБКА: Не заданы переменные TELEGRAM_BOT_TOKEN или GROQ_API_KEY!")
        exit(1)
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🚀 Бот запущен и ждёт сообщений...")
    app.run_polling()

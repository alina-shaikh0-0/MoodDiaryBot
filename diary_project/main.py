from django.db import close_old_connections
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import os
import sys
sys.path.append(os.path.abspath('/diary_project'))  # Добавляем путь к проекту Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diary_project.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
import torch
from dotenv import load_dotenv
from diary_app.models import TelegramUser, MoodEntry
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from concurrent.futures import ThreadPoolExecutor
from asgiref.sync import sync_to_async
from threading import Thread

load_dotenv()


# Токен бота (полученный от BotFather)
TOKEN = 'telegram_token'

# Список меток эмоций (27 штук)
LABELS = [
    'admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring', 'confusion', 'curiosity', 'desire',
    'disappointment', 'disapproval', 'disgust', 'embarrassment', 'excitement', 'fear', 'gratitude', 'grief', 'joy',
    'love', 'nervousness', 'optimism', 'pride', 'realization', 'relief', 'remorse', 'sadness', 'surprise', 'neutral'
]

# Соответствие номеров и меток
ID2LABEL = dict(enumerate(LABELS))

# Словарь перевода эмоций в простые категории и эмодзи
EMOTION_MAP = {
    "admiration": {"category": "positive", "emoji": "😃"},       # Восхищение
    "amusement": {"category": "positive", "emoji": "😆"},       # Веселье
    "anger": {"category": "negative", "emoji": "🤬"},           # Гнев
    "annoyance": {"category": "negative", "emoji": "😡"},       # Недовольство
    "approval": {"category": "positive", "emoji": "🙂"},        # Одобрение
    "caring": {"category": "positive", "emoji": "😌"},          # Забота
    "confusion": {"category": "neutral", "emoji": "🤔"},        # Путаница
    "curiosity": {"category": "neutral", "emoji": "🤨"},        # Любопытство
    "desire": {"category": "positive", "emoji": "😍"},          # Желание
    "disappointment": {"category": "negative", "emoji": "😔"}, # Разочарование
    "disapproval": {"category": "negative", "emoji": "🙄"},    # Недовольство
    "disgust": {"category": "negative", "emoji": "🤢"},        # Отвращение
    "embarrassment": {"category": "negative", "emoji": "🤭"},  # Смущение
    "excitement": {"category": "positive", "emoji": "😵"},      # Волнение
    "fear": {"category": "negative", "emoji": "😱"},           # Страх
    "gratitude": {"category": "positive", "emoji": "😇"},      # Благодарность
    "grief": {"category": "negative", "emoji": "😿"},          # Печаль
    "joy": {"category": "positive", "emoji": "😃"},            # Радость
    "love": {"category": "positive", "emoji": "😍"},           # Любовь
    "nervousness": {"category": "negative", "emoji": "😳"},    # Нервозность
    "optimism": {"category": "positive", "emoji": "😌"},       # Оптимизм
    "pride": {"category": "positive", "emoji": "😼"},          # Гордость
    "realization": {"category": "neutral", "emoji": "🤩"},     # Озарение
    "relief": {"category": "positive", "emoji": "🤸"},         # Облегчение
    "remorse": {"category": "negative", "emoji": "😢"},        # Раскаяние
    "sadness": {"category": "negative", "emoji": "😔"},        # Грусть
    "surprise": {"category": "neutral", "emoji": "😲"},        # Удивление
    "neutral": {"category": "neutral", "emoji": "😐"}          # Нейтральная реакция
}

# Инициализируем модель и токенизатор
tokenizer = AutoTokenizer.from_pretrained("fyaronskiy/ruRoberta-large-ru-go-emotions")
model = AutoModelForSequenceClassification.from_pretrained("fyaronskiy/ruRoberta-large-ru-go-emotions")

# Пороги, которые предложила модель
best_thresholds = [
    0.36734693877551017, 0.2857142857142857, 0.2857142857142857, 0.16326530612244897, 0.14285714285714285,
    0.14285714285714285, 0.18367346938775508, 0.3469387755102041, 0.32653061224489793, 0.22448979591836732,
    0.2040816326530612, 0.2857142857142857, 0.18367346938775508, 0.2857142857142857, 0.24489795918367346,
    0.7142857142857142, 0.02040816326530612, 0.3061224489795918, 0.44897959183673464, 0.061224489795918366,
    0.18367346938775508, 0.04081632653061224, 0.08163265306122448, 0.1020408163265306, 0.22448979591836732,
    0.3877551020408163, 0.3469387755102041, 0.24489795918367346
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user, created = TelegramUser.objects.get_or_create(chat_id=chat_id)
    if created:
        await update.message.reply_text("Привет! Ваш профиль создан.")
    else:
        await update.message.reply_text("Привет! Вы уже зарегистрированы.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я Telegram-бот для ведения дневника настроения! " 
                                    "Расскажи, как прошёл твой день, и я попробую определить твое настроение.")

executor = ThreadPoolExecutor()


def _get_user_in_thread(chat_id):
    """
    Синхронная функция, исполняемая в отдельном потоке для получения пользователя.
    """
    try:
        return TelegramUser.objects.get(chat_id=chat_id).user
    except TelegramUser.DoesNotExist:
        return None


"""def get_user_sync(chat_id):
    try:
        return TelegramUser.objects.get(chat_id=chat_id).user
    finally:
        executor.shutdown(wait=True)"""


async def get_user_sync(chat_id):
    """
    Возвращает пользователя асинхронно, выполняя операцию в отдельном потоке.
    """
    return await _get_user_in_thread(chat_id)


async def analyze_mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(f"Processing text: {text}")
    inputs = tokenizer(text, truncation=True, add_special_tokens=True, max_length=128, return_tensors='pt')
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.sigmoid(logits).squeeze(dim=0)
        binary_labels = (probs > torch.tensor(best_thresholds)).int()
        detected_emotions = []
        for label_id, value in enumerate(binary_labels):
            if value == 1:
                detected_emotions.append(ID2LABEL[label_id])
    # Получаем пользователя асинхронно
    chat_id = update.effective_chat.id
    user = await get_user_sync(chat_id)
    print(f"Detected emotions: {detected_emotions}")
    # Если нашли эмоции, берём первую
    if detected_emotions:
        first_emotion = detected_emotions[0]
        category = EMOTION_MAP.get(first_emotion, {}).get("category", "unknown")
        emoji = EMOTION_MAP.get(first_emotion, {}).get("emoji", "🤷")
    else:
        category = "unknown"
        emoji = "🤷"



    # Сохраняем запись в базу данных
    chat_id = update.effective_chat.id
    user = TelegramUser.objects.get(chat_id=chat_id).user
    MoodEntry.objects.create(user=user, text=text, emotion=first_emotion)

    # Формируем итоговый ответ
    final_response = f"Анализ показал: {emoji} Ваше настроение: {category.capitalize()}"
    await update.message.reply_text(final_response)


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_mood))
    app.run_polling()

if __name__ == '__main__':
    main()

# Промт для анализа настроения
"""MOOD_PROMPT = "
Анализируй текст и определяй эмоциональное состояние (радость, грусть, стресс, тревога и т.п.)
Предлагай нейтральные рекомендации (например: "Прогулка помогает успокоиться").
Не давай медицинские советы или диагнозы. Отвечай на языке пользователя.
"


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я Telegram-бот для ведения дневника настроения! Расскажи, как прошёл твой день, и я попробую определить твое настроение.")


# Обработчик текстовых сообщений
async def analyze_mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": MOOD_PROMPT},
                {"role": "user", "content": user_text}
            ]
        )
        advice = response.choices[0].message["content"]
        await update.message.reply_text(advice)
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        await update.message.reply_text("Что-то пошло не так при анализе вашего текста. Попробуйте позже.")

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_mood))
    app.run_polling() """

"""async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я Telegram-бот для ведения дневника настроения!")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler('start', start))

    # Запускаем прослушивание сообщений
    print("Запуск бота...")
    application.run_polling()"""
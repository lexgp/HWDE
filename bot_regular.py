import asyncio
import os

import nest_asyncio
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

from yandex_cloud_ml_sdk import YCloudML

from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, Identity
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

import datetime

# загрузка переменных из .env
load_dotenv()

# получаем доступы из окружения
TOKEN = os.getenv("BOT_TOKEN")
POSTGRES_CONNECTION_URL = os.getenv("POSTGRES_CONNECTION_URL")
YCloudML_FOLDER_ID = os.getenv("YCloudML_FOLDER_ID")
YCloudML_AUTH_TOKEN = os.getenv("YCloudML_AUTH_TOKEN")

Base = declarative_base()

class Action(Base):
    __tablename__ = 'actions'
    id = Column(Integer, Identity(), primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    action = Column(String(255), nullable=False)

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, Identity(), primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    message = Column(String, nullable=True)
    reply = Column(String, nullable=True)
    created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    score = Column(Integer, nullable=True)

def generate_llm_request(user_message):
    full_message = f'''Пользователь прислал сообщение. Ответь ему чтонибудь в хардкорном метал стиле, но без оскорблений и непреличия.
    Не нужно никаких вводных.
    Отвечай на русском языке.
    Твоё сообщение должно быть прямым ответом пользователю.
    Вот сообщение пользователя: {user_message}'''
    return [
        {
            "role": "user",
            "text": full_message,
        },
    ]

def get_llm_reply(message):
    global YCloudML_FOLDER_ID
    global YCloudML_AUTH_TOKEN
    sdk = YCloudML(folder_id=YCloudML_FOLDER_ID, auth=YCloudML_AUTH_TOKEN)
    model = sdk.models.completions("yandexgpt-lite", model_version="rc")
    model = model.configure(temperature=0.3)
    llm_request = generate_llm_request(message)
    result = model.run(llm_request)
    llm_response = '\n'.join([r.text for r in result])
    return llm_response

database = create_engine(POSTGRES_CONNECTION_URL, echo=True)

# команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        Session = sessionmaker(bind=database)
        session = Session()
        new_action = Action(user_id=update.message.from_user.id, action='start')
        session.add(new_action)
        session.commit()
        print("Action added successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'session' in locals():
            session.close()
    await update.message.reply_text("Привет, бро! Ты готов услышать рёв настоящего металла? ")

# эхо-ответ
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_message = get_llm_reply(update.message.text)
    try:
        user_id = update.message.from_user.id
        Session = sessionmaker(bind=database)
        session = Session()
        new_action = Action(user_id=user_id, action='answer')
        session.add(new_action)
        session.commit()
        print("Action added successfully.")
        new_message = Message(
            user_id=user_id,
            message=update.message.text,
            reply=bot_message,
            score=0
        )
        session.add(new_message)
        session.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'session' in locals():
            session.close()
    await update.message.reply_text(bot_message)

# асинхронный запуск
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("Бот запущен!")
    # await 
    app.run_polling()  # без попытки закрыть loop вручную
    # await app.initialize()  # Инициализируем приложение
    # async with app:
    #     await app.start()
    #     await app.updater.start_polling()
    #     # await app.idle() # запускает бот на "вечное" ожидание

if __name__ == '__main__':
    main()
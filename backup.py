import os
import csv
import yadisk
import datetime

from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, Identity
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

# загрузка переменных из .env
load_dotenv()

YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN")
POSTGRES_CONNECTION_URL = os.getenv("POSTGRES_CONNECTION_URL")

LOCAL_FILE = "messages.csv"

timestamp = datetime.datetime.now().strftime("%d.%m.%Y_%H-%M")


# Определяем базовый класс для моделей SQLAlchemy
Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, Identity(), primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    message = Column(String, nullable=True)
    reply = Column(String, nullable=True)
    created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    score = Column(Integer, nullable=True)

# Создаем движок SQLAlchemy
engine = create_engine(POSTGRES_CONNECTION_URL)

# Создаем сессию
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Получаем все записи из таблицы messages
    messages = session.query(Message).all()

    # Открываем CSV файл для записи
    with open(LOCAL_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        # Определяем заголовки CSV файла (имена столбцов)
        fieldnames = [column.name for column in Message.__table__.columns]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Записываем заголовки в CSV файл
        writer.writeheader()

        # Записываем данные в CSV файл
        for message in messages:
            writer.writerow({column.name: getattr(message, column.name) for column in Message.__table__.columns})

    print(f"Данные из таблицы 'messages' успешно выгружены в файл '{LOCAL_FILE}'")

except Exception as e:
    print(f"Произошла ошибка: {e}")

finally:
    # Закрываем сессию
    session.close()

try:
    y = yadisk.YaDisk(token=YANDEX_DISK_TOKEN)
    if not y.check_token():
        print("Неверный OAuth-токен.")
        exit()

    REMOTE_PATH = f"/backup/messages_{timestamp}.csv"

    # Создаем папку, если ее нет
    remote_dir = os.path.dirname(REMOTE_PATH)
    if not y.exists(remote_dir):
        y.mkdir(remote_dir)

    # Загружаем файл
    y.upload(LOCAL_FILE, REMOTE_PATH)
    print(f"Файл '{LOCAL_FILE}' успешно загружен на Яндекс.Диск в '{REMOTE_PATH}'")

except yadisk.exceptions.PathNotFoundError:
    print(f"Ошибка: Указанный путь '{remote_dir}' не существует на Яндекс.Диске.")
# except yadisk.exceptions.CredentialsError:
#     print("Ошибка: Неверные учетные данные Яндекс.Диска.")
except Exception as e:
    print(f"Произошла ошибка: {e}")
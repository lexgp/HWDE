# Домашняя работа по инжинирингу данных.

![Альтернативный текст для картинки](images/logo.png)

Телеграм бот. 
Отвечает через LLM модель "yandexgpt-lite", в немного специфической манере.
Данные кладутся сразу в БД postgres.

![О боте](images/diagram.png)


## Как запускать:
1. Создать виртуальное окружение
2. Виртуально окружиться `source venv/bin/activate`
3. Установить зависимости:
```bash
pip3 install -r requirements.txt
```
4. Создать .env файл и заполнить его как в .env.example

5. Запустить:
```bash
python3 bot_regular.py
```

5.1 Можно запустить фоново, чтобы не отсвечивал:
```bash
nohup python3 bot_regular.py &
```

Дашбоард и данные можно посмотреть тут: https://datalens.yandex/1ahslok5dd9un?state=9954fbbf213
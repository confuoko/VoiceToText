# VoiceToText
Корпоративный стартап по транскрибации и анализу аудиозаписей


## Dependency Installation

Скачивание репозитория:

`git clone https://github.com/confuoko/VoiceToText.git`
  
1. Создание и активация виртуального окружения:
```
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```
2. Заполнение значений переменных:

use_auth_token=''

API_KEY = ''

3. Запуск Redis через Docker: (при запущенном Docker Desktop)
```
docker run -d -p 6379:6379 redis
```
4. Запуск локального сервера Django:
```
python -m venv venv
cd user_account/
python manage.py runserver
```
5. Запуск Celery в новом терминале:
```
cd user_account/
celery -A user_account worker --loglevel=info -P 
```

6.


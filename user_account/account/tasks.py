from django.core.mail import send_mail
from user_account.celery import app

#from .service import send
from .models import Contact
from .helpful import down


@app.task
def send_spam_email(user_email, nn):

    email_text = down(nn)
    #content = 'Добрый день! Сегодня 19.10.2024'

    send_mail(
            'Вы подписались на рассылку',
            f'Мы начинаем обработку материала по ссылке: {nn}, {email_text}',
            'django@gmail.com',
            [user_email],
            fail_silently=False,
        )
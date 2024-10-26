from django.core.mail import send_mail
from user_account.celery import app

#from .service import send
from .models import Contact
from .helpful_oldd import down, down_2, delete_files, delete_folder_and_txt
from .helpful_oldd import DIR_NAME, TXT_FILE_NAME, FOLDER_NAME, TXT_FOLDER_NAME, DIR_FOLDER_NAME


@app.task
def send_spam_email(user_email, nn):

    email_text = down(nn)
    send_mail(
            'Вы подписались на рассылку',
            f'Мы начинаем обработку материала по ссылке: {nn}, {email_text}',
            'django@gmail.com',
            [user_email],
            fail_silently=False,
        )
    # удаление файла
    delete_files(DIR_NAME, TXT_FILE_NAME)

    
@app.task
def send_folder_analys(user_email, nn):

    email_text = down_2(nn)

    send_mail(
            'Вы подписались на рассылку',
            f'Мы начинаем обработку материала по ссылке: {nn}, {email_text}',
            'django@gmail.com',
            [user_email],
            fail_silently=False,
        )
    delete_folder_and_txt(TXT_FOLDER_NAME, DIR_FOLDER_NAME)
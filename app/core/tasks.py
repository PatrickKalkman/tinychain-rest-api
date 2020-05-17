# main/tasks.py

import logging

from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from app.celery import app


@app.task
def send_verification_email(user_id):
    print('sending email')
    UserModel = get_user_model()
    try:
        base = 'http://localhost:8000'
        user = UserModel.objects.get(pk=user_id)
        validate_link = reverse('user:validate')
        url = f'{base}{validate_link}?verification_id={user.verification_id}'

        subject = 'Verify your email address'
        from_email = 'tinychain_verify@gmail.com'
        to = user.email
        text_content = 'Welcome to the TinyChain platform.'
        html_content = f'<p>Hello {user.name},</p><br>'
        html_content += '<p>Welcome to the TinyChain platform,'
        html_content += 'please verify your email adress by clicking '
        html_content += f'<a href="{url}">this</a> link.</p><br><br>'
        html_content += '<p>Kind regards, <br> The TinyChain team.'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
    except UserModel.DoesNotExist:
        logging.warning(
            f'Tried to send verify email to non-existing user {user_id}')

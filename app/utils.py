from flask_mail import Message
from threading import Thread
from flask import current_app

def send_mail(subject, recipient, html):
    """Send email asynchronously - Lab 7 extended level"""
    app = current_app._get_current_object()

    msg = Message(
        subject,
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[recipient]
    )
    msg.html = html

    def send_async():
        with app.app_context():
            mail = app.extensions['mail']
            mail.send(msg)

    Thread(target=send_async).start()
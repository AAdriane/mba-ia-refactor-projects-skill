import logging
import smtplib

from config import Config
from utils.helpers import utcnow

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.notifications = []

    def send_email(self, to, subject, body):
        try:
            server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=5)
            server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(Config.SMTP_USER, to, message)
            server.quit()
            logger.info("Email enviado para %s", to)
            return True
        except Exception as e:
            logger.warning("Erro ao enviar email para %s: %s", to, str(e))
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': utcnow(),
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n['user_id'] == user_id]

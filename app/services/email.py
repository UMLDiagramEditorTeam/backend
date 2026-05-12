from dataclasses import dataclass

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import settings
from app.models.email_notifications import EmailNotificationAction
from app.models.users import UserModel


@dataclass(frozen=True)
class EmailNotificationOptions:
    action: EmailNotificationAction
    subject: str
    template_name: str
    url: str


class EmailService:
    def __init__(self):
        self._fast_mail = FastMail(
            ConnectionConfig(
                MAIL_USERNAME=settings.smtp.username,
                MAIL_PASSWORD=settings.smtp.password,
                MAIL_FROM=settings.email.from_email,
                MAIL_FROM_NAME=settings.email.from_name,
                MAIL_PORT=settings.smtp.port,
                MAIL_SERVER=settings.smtp.host,
                MAIL_STARTTLS=settings.smtp.starttls,
                MAIL_SSL_TLS=settings.smtp.ssl_tls,
                USE_CREDENTIALS=settings.smtp.use_credentials,
                VALIDATE_CERTS=settings.smtp.validate_certs,
                TEMPLATE_FOLDER=settings.email.template_folder,
            )
        )

    def send_account_confirmation(
        self,
        background_tasks: BackgroundTasks,
        user: UserModel,
        code: str,
    ) -> None:
        self._send_notification(
            background_tasks=background_tasks,
            user=user,
            code=code,
            options=EmailNotificationOptions(
                action=EmailNotificationAction.ACCOUNT_CONFIRMATION,
                subject=settings.email.account_confirmation_subject,
                template_name='account_confirmation.html',
                url=settings.email.account_confirmation_url,
            ),
        )

    def send_password_reset(
        self,
        background_tasks: BackgroundTasks,
        user: UserModel,
        code: str,
    ) -> None:
        self._send_notification(
            background_tasks=background_tasks,
            user=user,
            code=code,
            options=EmailNotificationOptions(
                action=EmailNotificationAction.PASSWORD_RESET,
                subject=settings.email.password_reset_subject,
                template_name='password_reset.html',
                url=settings.email.password_reset_url,
            ),
        )

    def _send_notification(
        self,
        background_tasks: BackgroundTasks,
        user: UserModel,
        code: str,
        options: EmailNotificationOptions,
    ) -> None:
        message = MessageSchema(
            subject=options.subject,
            recipients=[user.email],
            template_body={
                'name': user.name,
                'code': code,
                'user_id': str(user.id),
                'action': options.action.value,
                'url': f'{options.url}?user_id={user.id}&code={code}',
            },
            subtype=MessageType.html,
        )
        background_tasks.add_task(
            self._fast_mail.send_message,
            message,
            template_name=options.template_name,
        )

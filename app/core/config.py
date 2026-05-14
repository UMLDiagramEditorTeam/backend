from datetime import timedelta
from functools import lru_cache
from typing import Any

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class DBSettings(BaseSettings):
    driver: str = 'postgresql+asyncpg'
    host: str = 'localhost'
    port: int = 5432
    user: str = 'postgres'
    password: str = 'password'
    name: str = 'db'

    @property
    def url(self) -> str:
        return URL.create(
            drivername=self.driver,
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        ).render_as_string(hide_password=False)


class AuthSettings(BaseSettings):
    jwt_private_key: str = 'your_secret_key_here'
    jwt_algorithm: str = 'HS256'
    jwt_access_token_expire: timedelta = timedelta(hours=1)
    jwt_refresh_token_expire: timedelta = timedelta(days=7)

    jwt_refresh_cookie_name: str = 'refresh_token'
    jwt_refresh_cookie_secure: bool = False
    jwt_refresh_cookie_samesite: str = 'lax'
    jwt_refresh_cookie_path: str = '/'
    jwt_refresh_cookie_domain: str | None = None
    account_confirmation_token_expire: timedelta = timedelta(days=1)
    password_reset_token_expire: timedelta = timedelta(hours=1)

    @field_validator(
        'jwt_access_token_expire',
        'jwt_refresh_token_expire',
        'account_confirmation_token_expire',
        'password_reset_token_expire',
        mode='before',
    )
    @classmethod
    def parse_expire_seconds(cls, value: Any) -> timedelta:
        if isinstance(value, timedelta):
            return value
        return timedelta(seconds=int(value))


class RBACSettings(BaseSettings):
    admin_email: str = 'admin@example.com'
    admin_password: str = 'admin123456'
    admin_name: str = 'admin'
    admin_role: str = 'admin'
    default_role: str = 'public'


class SMTPSettings(BaseSettings):
    username: str = ''
    password: str = ''
    host: str = 'smtp.example.com'
    port: int = 587
    use_credentials: bool = True
    starttls: bool = True
    ssl_tls: bool = False
    validate_certs: bool = True


class EmailSettings(BaseSettings):
    from_email: str = 'noreply@example.com'
    from_name: str = 'UML Diagram Editor'
    template_folder: str = 'app/templates/email'
    account_confirmation_subject: str = 'Account confirmation'
    password_reset_subject: str = 'Password reset confirmation'
    account_confirmation_path: str = '/auth/confirm'
    password_reset_path: str = '/auth/password/change'


class FrontendSettings(BaseSettings):
    scheme: str = 'http'
    host: str = 'localhost'
    port: int | None = 3000

    @property
    def origin(self) -> str:
        if self.port is None:
            return f'{self.scheme}://{self.host}'
        return f'{self.scheme}://{self.host}:{self.port}'


class CommonSettings(BaseSettings):
    debug: bool = False
    port: int = 8000

    @computed_field
    @property
    def host(self) -> str:
        if self.debug:
            return f'http://localhost:{self.port}'
        return 'https://example.com'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_nested_delimiter='__',
        extra='ignore',
        case_sensitive=False,
    )

    db: DBSettings
    auth: AuthSettings
    rbac: RBACSettings
    email: EmailSettings
    smtp: SMTPSettings
    frontend: FrontendSettings
    common: CommonSettings = Field(default_factory=CommonSettings)

    @property
    def database_url(self) -> str:
        return self.db.url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

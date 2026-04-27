from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='DB_',
        env_file='.env',
        extra='ignore',
    )

    schema: str = 'postgresql+asyncpg'
    host: str = 'localhost'
    port: int = 5432
    user: str = 'postgres'
    password: str = 'password'
    name: str = 'db'

    @property
    def url(self) -> str:
        return URL.create(
            drivername=self.schema,
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        ).render_as_string(hide_password=False)


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='AUTH_',
        env_file='.env',
        extra='ignore',
    )

    jwt_private_key: str
    jwt_algorithm: str = 'HS256'
    jwt_access_token_expire_seconds: int = 3600
    jwt_refresh_token_expire_seconds: int = 604800

    jwt_refresh_cookie_name: str = 'refresh_token'
    jwt_refresh_cookie_secure: bool = False
    jwt_refresh_cookie_samesite: str = 'lax'
    jwt_refresh_cookie_path: str = '/'
    jwt_refresh_cookie_domain: str | None = None


class RBACSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='RBAC_',
        env_file='.env',
        extra='ignore',
    )

    admin_email: str = 'admin@example.com'
    admin_password: str = 'admin123456'
    admin_name: str = 'admin'
    admin_role: str = 'admin'
    default_role: str = 'public'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
    )

    db: DBSettings = DBSettings()
    auth: AuthSettings = AuthSettings()
    rbac: RBACSettings = RBACSettings()

    @property
    def database_url(self) -> str:
        return self.db.url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

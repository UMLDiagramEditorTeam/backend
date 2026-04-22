from anyio.functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    db_schema: str = 'postgresql+asyncpg'
    db_host: str = 'localhost'
    db_port: int = 5432
    db_user: str = 'postgres'
    db_pass: str = 'password'
    db_name: str = 'db'

    jwt_private_key: str
    jwt_algorithm: str = 'HS256'
    jwt_access_token_expire_seconds: int = 3600
    jwt_refresh_token_expire_seconds: int = 604800

    jwt_refresh_cookie_name: str = 'refresh_token'
    jwt_refresh_cookie_secure: bool = False
    jwt_refresh_cookie_samesite: str = 'lax'
    jwt_refresh_cookie_path: str = '/'
    jwt_refresh_cookie_domain: str | None = None

    rbac_admin_email: str = 'admin@example.com'
    rbac_admin_password: str = 'admin123456'
    rbac_admin_name: str = 'admin'
    rbac_admin_role: str = 'admin'
    rbac_default_role: str = 'public'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_nested_delimiter='__',
    )

    @property
    def database_url(self) -> str:
        return URL.create(
            drivername=self.db_schema,
            username=self.db_user,
            password=self.db_pass,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        ).render_as_string(hide_password=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

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

    model_config = SettingsConfigDict(env_file='.env')

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

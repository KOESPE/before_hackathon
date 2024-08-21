from pydantic.v1 import BaseSettings

from sqlalchemy.ext.asyncio import create_async_engine


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_HOST: str
    POSTGRES_PASSWORD: str
    POSTGRES_DATABASE: str

    # class Config:
    #     env_file = '.env'
    #     env_file_encoding = 'utf-8'

    @property
    def DB_URL(self) -> str:
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DATABASE}'

    @property
    def engine(self):
        return create_async_engine(self.DB_URL)


settings = Settings()
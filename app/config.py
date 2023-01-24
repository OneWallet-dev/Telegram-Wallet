from pydantic import BaseSettings, PostgresDsn, RedisDsn


class Config(BaseSettings):

    REDIS_URL: str = ""
    POSTGRES_URL: str = ""
    BOT_TOKEN: str = ""
    SECRET_KEY: str = ""

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Config()

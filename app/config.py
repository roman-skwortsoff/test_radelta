from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["TEST", "DEV", "PROD"]

    DB_HOST: str
    DB_NAME: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    ROOT_DB_PASS: str

    REDIS_HOST: str
    REDIS_POST: int

    MONGO_HOST: str
    MONGODB_NAME: str
    MONGO_PORT: str
    MONGO_USERNAME: str
    MONGO_PASSWORD: str

    API_KEY: str

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_POST}"

    @property
    def DB_URL(self):
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def MONGO_URL(self):
        return f"mongodb://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGODB_NAME}?authSource={self.MONGODB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # type: ignore

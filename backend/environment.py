from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    POSTGRES_USERNAME: str = Field(validation_alias='POSTGRES_USERNAME')
    POSTGRES_PASSWORD: str = Field(validation_alias='POSTGRES_PASSWORD')
    POSTGRES_HOST: str = Field(validation_alias='POSTGRES_HOST')
    POSTGRES_PORT: int = Field(validation_alias='POSTGRES_PORT')
    POSTGRES_DATABASE: str = Field(validation_alias='POSTGRES_DATABASE')

    REDIS_PASSWORD: str = Field(validation_alias='REDIS_PASSWORD')
    REDIS_PORT: int = Field(validation_alias='REDIS_PORT')

    class Config:
        env_file = ".env"

SETTINGS = Settings()
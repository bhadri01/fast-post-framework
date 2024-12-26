from pydantic_settings import BaseSettings  # Corrected import


class Settings(BaseSettings):
    postgresql_database_master_url: str
    postgresql_database_slave_url: str
    secret_key: str

    class Config:
        env_file = ".env"


settings = Settings()

from pathlib import Path

from pydantic import BaseModel, SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class DatabaseSettings(BaseModel):
    host: str
    port: int
    db: str
    user: SecretStr = Field(exclude=True, repr=False)
    password: SecretStr | None = Field(default=None, exclude=True, repr=False)
    engine: str
    debug: bool

    def get_url(self, password: SecretStr | None = None) -> URL:
        password = password or self.password
        return URL.create(
            drivername=self.engine,
            username=self.user.get_secret_value(),
            password=(
                password.get_secret_value()
                if isinstance(password, SecretStr)
                else password
            ),
            host=self.host,
            port=self.port,
            database=self.db,
        )


class DefaultSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        extra="ignore",
        env_prefix="is_",
        env_nested_delimiter="__",
        env_ignore_empty=True,
        env_file_encoding="utf-8",
    )


class DatabaseConnectionSettings(DefaultSettings):
    database: DatabaseSettings


class AuthSettings(BaseModel):
    reset_password_token_secret: SecretStr
    verification_token_secret: SecretStr
    jwt_strategy_token_secret: SecretStr


class Settings(DatabaseConnectionSettings):
    debug: bool
    auth: AuthSettings

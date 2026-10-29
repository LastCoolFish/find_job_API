from pydantic import BaseModel, Field, SecretStr, field_validator

from security import ensure_fits_bcrypt


class LoginSchema(BaseModel):
    email: str
    password: SecretStr

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: SecretStr) -> SecretStr:
        ensure_fits_bcrypt(value.get_secret_value())
        return value


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenSchema(BaseModel):
    refresh_token: str = Field(min_length=1, max_length=512)

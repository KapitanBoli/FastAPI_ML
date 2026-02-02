from enum import Enum

from pydantic import BaseModel

class TokenType(str, Enum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"

class RefreshToken(BaseModel):
    refresh_token: str
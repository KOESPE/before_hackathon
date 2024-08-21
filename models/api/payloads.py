from typing import Optional, List

from pydantic import BaseModel, HttpUrl, Field


class LoginForm(BaseModel):
    login: str
    password: str

from typing import Optional, List

from pydantic import BaseModel, HttpUrl, Field


class LoginForm(BaseModel):
    login: str
    password: str


class ChangePasswordForm(LoginForm):
    new_password: str


class PurchasePayload(BaseModel):
    product_id: int
    quantity: int
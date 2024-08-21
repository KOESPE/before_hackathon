from typing import Optional, List

from pydantic import BaseModel, HttpUrl, Field


class UserData(BaseModel):
    role: str = Field(..., example="buyer/seller")
    access_token: str
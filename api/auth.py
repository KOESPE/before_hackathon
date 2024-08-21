import random
import string

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from database import get_session_fastapi
from models.api import responses, payloads
from models.database import Users

auth_router = APIRouter(tags=['Авторизация'])
security = HTTPBearer()

def generate_token():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(64))


@auth_router.post('/auth',
                  responses={
                      200: {"description": "OK",
                            "model": responses.UserData},
                      401: {"description": "Invalid login or password"}
                  })
async def auth(payload: payloads.LoginForm,
               session: AsyncSession = Depends(get_session_fastapi)):
    """
    user@mail.ru:user_password
    admin@mail.ru:admin_password
    """
    # Ищем в бд пользователя
    user_data_query = select(Users).where(Users.login == payload.login, Users.password == payload.password)
    user_data: Users = await session.scalar(user_data_query)
    if user_data is not None:
        user_data.access_token = generate_token()
        await session.commit()
        await session.refresh(user_data)

        user_data_response = responses.UserData(role=user_data.role,
                                                access_token=user_data.access_token,
                                                )
        return JSONResponse(content=jsonable_encoder(user_data_response), status_code=200)
    else:
        raise HTTPException(status_code=401, detail="Invalid login or password")


@auth_router.post('/test_bearer')
async def auth(credentials: HTTPAuthorizationCredentials = Depends(security),
               session: AsyncSession = Depends(get_session_fastapi)):
    user_data_query = select(Users).where(Users.access_token == credentials.credentials)
    user_data: Users = await session.scalar(user_data_query)
    if user_data is not None:
        return f'Ваша почта: {user_data.login}'
    else:
        raise HTTPException(status_code=401, detail="Invalid login or password")
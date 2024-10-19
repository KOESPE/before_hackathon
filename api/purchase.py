import datetime

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from database import get_session_fastapi
from models.api import responses, payloads
from models.database import Users, PurchaseHistory

purchase_router = APIRouter(tags=['Покупки'])
security = HTTPBearer()


# Метод оформления заказа. На вход: id товара, кол-во + сразу записываем в историю заказов
@purchase_router.post('/purchase')
async def purchase(
        payload: payloads.PurchasePayload,
        session: AsyncSession = Depends(get_session_fastapi),
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    access_token = credentials.credentials
    user = await session.execute(select(Users).where(Users.access_token == access_token))
    user = user.scalar()

    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')

    async with aiohttp.ClientSession() as aiohttp_session:
        async with aiohttp_session.get(
                f'https://products-api-five.vercel.app/products/{payload.product_id}') as response:
            if response.status == 200:
                data = await response.json()
                product_price = data["product"]["product_price"]

    order_date = datetime.datetime.now()
    purchase = PurchaseHistory(
        product_id=payload.product_id,
        order_date=datetime.datetime.now(),
        product_quantity=payload.quantity,
        order_sum=payload.quantity * product_price,
    )
    session.add(purchase)
    await session.commit()

    # Отправляем эти же данные на products-api
    order_data = {
        "order_date": order_date.strftime.strftime('%Y-%m-%d %H:%M:%S'),  # Используем текущее время в формате 2024-08-23 11:11:11
        "order_sum": payload.quantity * product_price,
        "product_id": payload.product_id,
        "product_quantity": payload.quantity
    }
    async with aiohttp.ClientSession() as session:
        async with session.post('https://adm-metrics-api.vercel.app/orders', json=order_data) as response:
            if response.status == 200:
                response_data = await response.json()
                print(response_data)
                return Response(status_code=200)
            else:
                return Response(status_code=400)


def get_product_by_id(product_id):
    for product in products_vika:
        if product['product_id'] == product_id:
            return product
    return None

products_vika = [
    {
      "product_id": 1,
      "product_name": "Хлеб",
      "product_description": "Продукция Бежицкого хлебного комбината",
      "product_price": 34
    },
    {
      "product_id": 2,
      "product_name": "Молоко",
      "product_description": "Продукция компании Милград",
      "product_price": 87
    },
    {
      "product_id": 3,
      "product_name": "Котлеты говяжьи",
      "product_description": "Продукция компании Мираторг",
      "product_price": 359
    },
    {
      "product_id": 4,
      "product_name": "Кола",
      "product_description": "Продукция компании Брянскпиво",
      "product_price": 63
    },
    {
      "product_id": 5,
      "product_name": "Чипсы картофельные",
      "product_description": "Чипсы картофельные",
      "product_price": 150
    },
    {
      "product_id": 6,
      "product_name": "Пиво темное нефильтрованное",
      "product_description": "Продукция компании Балтика",
      "product_price": 110
    }
  ]

# Метод получения истории заказов из базы данных:
# 1. Получаем все заказы из бд. 2. На каждый PurchaseHistory.product_id берем данные из products-api
# 3. Возвращаем ответ в формате: {order_date, product_id, product_name(из впи), product_description, order_sum}
@purchase_router.get('/purchase_history')
async def purchase_history(
        session: AsyncSession = Depends(get_session_fastapi),
):
    purchases = await session.execute(select(PurchaseHistory).where())
    purchases = purchases.scalars().all()

    purchase_details = []

    # На каждый PurchaseHistory.product_id берем данные из products-api
    async with aiohttp.ClientSession() as aiohttp_session:
        for purchase in purchases:

            product_name = (get_product_by_id(purchase.product_id))["product_name"]
            product_description = (get_product_by_id(purchase.product_id))["product_description"]

            purchase_details.append({
                "order_date": purchase.order_date.isoformat(),
                "product_id": purchase.product_id,
                "product_name": product_name,
                "product_description": product_description,
                "order_sum": purchase.order_sum,
            })

    return JSONResponse(content=purchase_details, status_code=200)

@purchase_router.post('/postback')
async def postback(request: Request):
    hash_name = request.query_params.get("hash_name")  # Название ссылки
    source_name = request.query_params.get("source_name")  # Источник
    event = request.query_params.get("event")  # Событие
    amount = request.query_params.get("amount")  # Значение события
    country = request.query_params.get("country")  # Страна
    sub1 = request.query_params.get("sub1")  # Telegram ID пользователя
    # Формируем строку для записи
    log_entry = (
        f"hash_name: {hash_name}\n"
        f"source_name: {source_name}\n"
        f"event: {event}\n"
        f"amount: {amount}\n"
        f"country: {country}\n"
        f"sub1: {sub1}\n"
        "-----------------------\n"
    )

    # Записываем данные в файл
    log_file_path = 'postback_log.txt'  # Путь к файлу

    with open(log_file_path, 'a') as log_file:
        log_file.write(log_entry)

    return {"status": "success"}


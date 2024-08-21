import uvicorn
from fastapi import FastAPI

from api.auth import auth_router
from config import settings
from database import db_init


async def lifespan():
    await db_init()


app = FastAPI(on_startup=[lifespan])

@app.get('/')
async def get_db_data():
    return f'POSTGRES_DATABASE =' + settings.POSTGRES_DATABASE


app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run(app)
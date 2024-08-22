import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import auth_router
from config import settings
from database import db_init


async def lifespan():
    await db_init()


app = FastAPI(on_startup=[lifespan])

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
                   )

@app.get('/')
async def get_db_data():
    return f'POSTGRES_DATABASE =' + settings.POSTGRES_DATABASE


app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run(app)
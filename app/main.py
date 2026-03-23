from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers import auth, diagrams, pages


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title='UML Constructor API (Mock)', lifespan=lifespan)

app.include_router(auth.router)
app.include_router(diagrams.router)
app.include_router(pages.router)


@app.get('/')
def root():
    return {'message': 'UML Constructor API Mock Server'}

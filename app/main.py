from contextlib import asynccontextmanager

from fastapi import FastAPI
from routers import auth, diagrams, pages
from core.database import engine, Base


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

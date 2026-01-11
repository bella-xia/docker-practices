from fastapi import FastAPI
from contextlib import asynccontextmanager
import faiss

from .db.mongo import init_db
from .api import event_router, init_index

@asynccontextmanager
async def lifespan(app: FastAPI):
    # before app startup
    init_db()
    init_index()
    print('faiss', faiss.__version__)
    yield
    # clean up

app = FastAPI(lifespan=lifespan)
app.include_router(event_router, prefix='/api/events')

@app.get("/")
async def root():
    return {"message": "hello world"}

@app.get("/healthz")
async def read_api_health():
    return {'status': 'ok'}

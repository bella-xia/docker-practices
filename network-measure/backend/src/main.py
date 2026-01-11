from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .api import event_router, init_loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    # before app startup
    init_loop()
    yield
    # clean up

app = FastAPI(lifespan=lifespan)
app.include_router(event_router, prefix='/api/events')

app.add_middleware(
    CORSMiddleware, 
    allow_origins=['http://localhost:3000',
                   'http://127.0.0.1:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
@app.get("/")
async def root():
    return {"message": "hello world"}

@app.get("/healthz")
async def read_api_health():
    return {'status': 'ok'}

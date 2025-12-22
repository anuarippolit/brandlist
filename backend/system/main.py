from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from system.app.routes import router
from system.app.security import limiter

app = FastAPI(
    title="Brandlist API",
    version="1.0",
    description="Read-only product search API"
)

# CORS (ограничить origins в production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production: ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["GET"],  # Только GET!
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Добавляет rate limiting к каждому запросу"""
    response = await call_next(request)
    return response


app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Brandlist API", "version": "1.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


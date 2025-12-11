from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from system.app.routes import router

app = FastAPI(title="AI Shopping Assistant", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Brandlist is running!"}


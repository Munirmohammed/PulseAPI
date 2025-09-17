from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, endpoints, logs

app = FastAPI(title="PulseAPI Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(endpoints.router)
app.include_router(logs.router)



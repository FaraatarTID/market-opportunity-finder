from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import markets

app = FastAPI(title="Market Opportunity Finder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(markets.router, prefix="/api/markets", tags=["markets"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Market Opportunity Finder API"}

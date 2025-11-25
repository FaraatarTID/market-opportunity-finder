from fastapi import FastAPI

app = FastAPI(title="Market Opportunity Finder")

@app.get("/")
def read_root():
    return {"message": "Welcome to Market Opportunity Finder API"}

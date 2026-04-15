from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Finance DNA API running"}

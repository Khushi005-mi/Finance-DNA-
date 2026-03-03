from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow frontend (Streamlit) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body structure
class InputData(BaseModel):
    name: str
    income: float
    expenses: float

# Health check route
@app.get("/")
def read_root():
    return {"message": "Finance DNA API is running"}

# Main API endpoint
@app.post("/analyze")
def analyze(data: InputData):
    savings = data.income - data.expenses

    if savings > 0:
        status = "You are saving money."
    elif savings < 0:
        status = "You are overspending."
    else:
        status = "Break even."

    return {
        "name": data.name,
        "savings": savings,
        "status": status
    }
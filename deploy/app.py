from fastapi import FastAPI
from report_builder import build_financial_report

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Finance DNA backend running"}

@app.get("/run-report")
def run_report():
    build_financial_report()
    return {"status": "Report generated successfully"}
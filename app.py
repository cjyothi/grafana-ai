from fastapi import FastAPI, Query
from summarizer import summarize_logs
from loki_client import fetch_logs
from rca_handler import RCAHandler
from typing import Optional

app = FastAPI(title="Log Analysis and RCA API",
             description="API for log analysis and root cause analysis of service issues")

rca_handler = RCAHandler()

@app.get("/analyze_logs")
async def analyze_logs(service: str = Query(..., description="Service name to analyze logs for")):
    """Analyze logs for a specific service and provide a summary."""
    logs = fetch_logs(service)
    summary = summarize_logs(logs)
    return {"summary": summary}

@app.get("/chat_rca")
async def chat_rca(
    question: str = Query(..., 
                        description="Question about service issues, e.g., 'Why did the checkout-service fail yesterday?'",
                        example="Why did the checkout-service fail yesterday?")
):
    """
    Get root cause analysis for service issues based on a natural language question.
    
    The question should ideally include:
    - The service name (e.g., checkout-service, payment-service)
    - Time reference (e.g., yesterday, last hour)
    - The issue or behavior you want to investigate
    
    Example questions:
    - Why did the checkout-service fail yesterday?
    - What caused the high latency in payment-service this morning?
    - Why were there errors in the inventory-service in the last 2 hours?
    """
    return await rca_handler.analyze_rca(question)

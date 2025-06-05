from datetime import datetime, timedelta
from dateutil.parser import parse
from loki_client import fetch_logs
from typing import List, Dict, Any
import os
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama

class RCAHandler:
    def __init__(self):
        self.llm = Ollama(model="llama2")
        self.rca_prompt = PromptTemplate(
            input_variables=["question", "logs", "service"],
            template="""You are an expert system analyst performing root cause analysis. 
            Based on the following logs and the question, provide a detailed analysis of what might have caused the issue.
            
            Question: {question}
            Service: {service}
            Relevant Logs:
            {logs}
            
            Please provide:
            1. Root Cause: What was the primary cause of the issue?
            2. Timeline: When did the issue start and how did it progress?
            3. Impact: What was the impact on the service?
            4. Recommendations: What steps should be taken to prevent this in the future?
            
            Analysis:"""
        )
    
    def _extract_time_range(self, question: str) -> tuple[datetime, datetime]:
        """Extract time range from the question or default to last 24 hours."""
        try:
            # Try to find date/time references in the question
            # This is a simple implementation - could be enhanced with more sophisticated NLP
            if "yesterday" in question.lower():
                end_time = datetime.now()
                start_time = end_time - timedelta(days=1)
            else:
                # Default to last 24 hours
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=24)
            
            return start_time, end_time
        except Exception:
            # Fallback to last 24 hours if parsing fails
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            return start_time, end_time

    def _extract_service(self, question: str) -> str:
        """Extract service name from the question."""
        # This is a simple implementation - could be enhanced with more sophisticated NLP
        common_services = ["checkout-service", "payment-service", "inventory-service"]
        for service in common_services:
            if service in question.lower():
                return service
        return None

    async def analyze_rca(self, question: str) -> Dict[str, Any]:
        """Analyze root cause based on the question and logs."""
        service = self._extract_service(question)
        if not service:
            return {"error": "Could not determine which service to analyze. Please specify the service in your question."}

        start_time, end_time = self._extract_time_range(question)
        
        # Fetch relevant logs
        logs = fetch_logs(service, start_time=start_time, end_time=end_time)
        
        if not logs:
            return {"error": f"No logs found for {service} in the specified time range."}

        # Generate RCA using LLM
        prompt = self.rca_prompt.format(
            question=question,
            logs=logs,
            service=service
        )
        
        analysis = self.llm(prompt)
        
        return {
            "service": service,
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "analysis": analysis
        } 
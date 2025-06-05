import os
import requests
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

class LokiClient:
    def __init__(self):
        self.base_url = os.getenv("LOKI_URL", "http://localhost:3100")
        self.api_version = "v1"

    def _build_query_url(self) -> str:
        return f"{self.base_url}/loki/api/{self.api_version}/query_range"

    def _format_time(self, dt: datetime) -> str:
        """Convert datetime to nanosecond timestamp string."""
        return str(int(dt.timestamp() * 1e9))

    def fetch_logs(self, 
                  service: str, 
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None) -> List[str]:
        """
        Fetch logs from Loki for a specific service within a time range.
        
        Args:
            service: Name of the service to fetch logs for
            start_time: Start time for log query (optional)
            end_time: End time for log query (optional)
        
        Returns:
            List of log entries as strings
        """
        params = {
            "query": f'{{service="{service}"}}',
            "limit": 1000  # Adjust based on your needs
        }

        if start_time:
            params["start"] = self._format_time(start_time)
        if end_time:
            params["end"] = self._format_time(end_time)

        try:
            response = requests.get(
                self._build_query_url(),
                params=params,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract log lines from Loki response
            log_entries = []
            for stream in data.get("data", {}).get("result", []):
                for value in stream.get("values", []):
                    log_entries.append(value[1])  # value[1] contains the log message
            
            return log_entries

        except requests.exceptions.RequestException as e:
            print(f"Error fetching logs from Loki: {str(e)}")
            return []

# Create a singleton instance
loki_client = LokiClient()

def fetch_logs(service: str, 
               start_time: Optional[datetime] = None,
               end_time: Optional[datetime] = None) -> List[str]:
    """
    Convenience function to fetch logs using the singleton LokiClient instance.
    """
    return loki_client.fetch_logs(service, start_time, end_time)

# AI-Powered Log Analysis and RCA System

This system provides an intelligent log analysis and Root Cause Analysis (RCA) solution that integrates with Loki for log management and uses LangChain with Ollama for advanced analysis.

## Features

- 🤖 Natural Language RCA Queries
- 📊 Intelligent Log Analysis
- ⏱️ Time-based Log Querying
- 🔍 Service-specific Analysis
- 🧠 AI-powered Root Cause Analysis
- 📈 Impact Assessment
- 🛠️ Preventive Recommendations

## Prerequisites

- Python 3.8+
- Loki instance running and accessible
- Ollama installed with llama2 model

## Detailed Environment Setup

### 1. Python Environment Setup

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
## On Windows
venv\Scripts\activate
## On macOS/Linux
source venv/bin/activate

# Verify Python version
python --version  # Should be 3.8 or higher
```

### 2. Ollama Setup

```bash
# Install Ollama (macOS/Linux)
curl https://ollama.ai/install.sh | sh

# For Windows, download from:
# https://ollama.ai/download/windows

# Pull the llama2 model
ollama pull llama2

# Verify Ollama installation
ollama list  # Should show llama2 in the list
```

### 3. Loki Setup

#### Using Docker (Recommended for local development)
```bash
# Create a docker-compose.yml file
cat << EOF > docker-compose.yml
version: "3"
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./loki-config.yaml:/etc/loki/local-config.yaml
EOF

# Create a basic Loki configuration
cat << EOF > loki-config.yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-05-15
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 168h

storage_config:
  boltdb:
    directory: /tmp/loki/index
  filesystem:
    directory: /tmp/loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
EOF

# Start Loki
docker-compose up -d

# Verify Loki is running
curl http://localhost:3100/ready
```

### 4. Project Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-layer
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
# Create .env file
cat << EOF > .env
# Loki Configuration
LOKI_URL=http://localhost:3100

# Optional configurations
LOG_LEVEL=INFO
MAX_LOG_ENTRIES=1000
CACHE_DURATION=3600
EOF
```

4. Verify the setup:
```bash
# Check if all required packages are installed
pip list | grep -E "fastapi|uvicorn|langchain|requests"

# Check if environment variables are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('LOKI_URL'))"
```

## Usage

1. Start the FastAPI application:
```bash
uvicorn app:app --reload
```

2. The API will be available at `http://localhost:8000`

### Available Endpoints

#### 1. Log Analysis Endpoint
```http
GET /analyze_logs?service={service_name}
```
Provides a summary of logs for a specific service.

#### 2. RCA Chat Endpoint
```http
GET /chat_rca?question={your_question}
```
Performs root cause analysis based on natural language questions.

Example questions:
- "Why did the checkout-service fail yesterday?"
- "What caused the high latency in payment-service this morning?"
- "Why were there errors in the inventory-service in the last 2 hours?"

### Example Response

```json
{
  "service": "checkout-service",
  "time_range": {
    "start": "2024-03-19T00:00:00",
    "end": "2024-03-20T00:00:00"
  },
  "analysis": {
    "root_cause": "Database connection timeout due to connection pool exhaustion",
    "timeline": "Issue started at 14:23 UTC...",
    "impact": "Approximately 150 failed transactions...",
    "recommendations": "1. Increase connection pool size..."
  }
}
```

## Components

### 1. RCA Handler (`rca_handler.py`)
- Manages the RCA logic using LangChain and Ollama
- Extracts time ranges and service names from questions
- Provides structured analysis with root cause, timeline, impact, and recommendations

### 2. Loki Client (`loki_client.py`)
- Handles communication with Loki log management system
- Supports time-based queries
- Provides error handling and response processing

### 3. FastAPI Application (`app.py`)
- Exposes REST API endpoints
- Handles request validation and response formatting
- Provides API documentation via Swagger UI

## Supported Services

The system currently supports the following services:
- checkout-service
- payment-service
- inventory-service

To add more services, update the `common_services` list in `rca_handler.py`.

## Time Range Processing

The system supports various time-based queries:
- "yesterday"
- Default: last 24 hours if no time range is specified

## API Documentation

Access the interactive API documentation at:
```
http://localhost:8000/docs
```

## Error Handling

The system provides clear error messages for common scenarios:
- Service not found in the question
- No logs found for the specified time range
- Loki connection issues

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Future Enhancements

- Add more sophisticated NLP for question understanding
- Enhance the prompt template for better analysis
- Implement additional time range parsing options
- Add support for more services
- Implement caching for frequent queries
- Add authentication and rate limiting

## License

[Add your license information here]

## Testing the Setup

1. Test Loki Connection:
```bash
curl -X GET "http://localhost:3100/ready"
# Should return 'ready'
```

2. Test the API:
```bash
# Test log analysis endpoint
curl -X GET "http://localhost:8000/analyze_logs?service=checkout-service"

# Test RCA chat endpoint
curl -X GET "http://localhost:8000/chat_rca?question=Why%20did%20the%20checkout-service%20fail%20yesterday?"
```

3. Monitor the logs:
```bash
# View application logs
tail -f app.log

# View Loki logs (if using Docker)
docker-compose logs -f loki
```

## Troubleshooting

### Common Issues and Solutions

1. Loki Connection Issues:
```bash
# Check if Loki is running
curl http://localhost:3100/ready

# Check Loki logs
docker-compose logs loki

# Verify environment variables
echo $LOKI_URL
```

2. Ollama Issues:
```bash
# Check Ollama status
ollama list

# Restart Ollama service
sudo systemctl restart ollama  # Linux
brew services restart ollama   # macOS
```

3. API Connection Issues:
```bash
# Check if FastAPI is running
curl http://localhost:8000/docs

# Check application logs
tail -f app.log
``` 
# Dockerfile
# Builds a container for the multi-agent research system.
#
# Build:  docker build -t research-agent .
# Run:    docker run --env-file .env research-agent
# Custom: docker run --env-file .env research-agent python main.py "your topic"

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (cached layer — only rebuilds if requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Default command — runs the pipeline with the default topic
CMD ["python", "main.py"]

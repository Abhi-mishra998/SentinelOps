#!/bin/bash
set -e

echo "Starting Kubernetes SRE Agent..."

# Activate venv
source .venv/bin/activate

# Check services
echo "Checking services..."
docker compose ps

# Start Ollama (if not running)
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
  echo "Starting Ollama..."
  ollama serve &
  sleep 5
fi

# Start FastAPI app
echo "Starting FastAPI server..."
python main.py



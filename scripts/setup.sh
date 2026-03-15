#!/bin/bash

set -e

echo \"Setting up Kubernetes SRE Agent...\"

# Start Docker services (Postgres & Redis)
echo \"Starting Postgres and Redis containers...\"
docker compose up -d postgres redis

# Wait for Postgres to be healthy
echo "Waiting for Postgres to be ready..."
timeout=60
counter=0
until docker compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
  counter=$((counter + 1))
  if [ $counter -gt $timeout ]; then
    echo "Error: Postgres not ready after ${timeout}s"
    docker compose logs postgres
    exit 1
  fi
  echo "Postgres not ready yet... (attempt ${counter}/${timeout})"
  sleep 1
done

# Wait for role to be fully created
echo "Creating k8s-agent role and sre_agent database..."
docker compose exec -T postgres psql -U postgres -d postgres << EOF
  CREATE USER "k8s-agent" WITH SUPERUSER CREATEDB PASSWORD 'password';
  CREATE DATABASE "sre_agent" OWNER "k8s-agent";
  GRANT ALL PRIVILEGES ON DATABASE "sre_agent" TO "k8s-agent";
\\q
EOF
echo "k8s-agent role and sre_agent database ready!"

echo "Waiting for k8s-agent auth ready..."
timeout_role=30
counter_role=0
until docker compose exec -T postgres psql -U "k8s-agent" -d "sre_agent" -c "SELECT 1" > /dev/null 2>&1; do
  counter_role=$((counter_role + 1))
  if [ $counter_role -gt $timeout_role ]; then
    echo "Error: k8s-agent not ready after ${timeout_role}s"
    docker compose logs postgres
    exit 1
  fi
  echo "Role not ready... waiting (attempt ${counter_role}/${timeout_role})"
  sleep 1
done
echo "k8s-agent fully ready!"

echo \"Postgres is ready!\"

# Create virtual environment
if [ ! -d \".venv\" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Run Alembic migrations
echo \"Running database migrations...\"
alembic upgrade head

# Pull Ollama model (optional, runs in background)
echo \"Pulling Qwen2.5 14B model (this may take a while if not present)...\"
ollama pull qwen2.5:14b &

echo \"Setup complete!\"
echo \"\"
echo \"Services running:\"
echo \"  Postgres/Redis: docker compose ps\"
echo \"  Ollama: ollama serve (in separate terminal)\"
echo \"\"
echo \"Run agent: source .venv/bin/activate && ./run_agent.sh\"


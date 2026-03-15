# Autonomous SRE Agent

A production-grade platform that automatically detects, investigates, diagnoses, and remediates Kubernetes infrastructure failures using deterministic workflows and AI-assisted reasoning.

**Target MTTR:** 5–10 seconds (down from 15–60 minutes)

---

## Quick Start

### 1. Prerequisites

```bash
# Python 3.11+, Docker, a running Kubernetes cluster (local or remote)
python3 --version   # must be 3.11+
docker --version
kubectl cluster-info
```

### 2. Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env — set AI_BACKEND, SLACK_WEBHOOK_URL, DATABASE_URL etc.
```

### 4. Start Supporting Services

```bash
docker-compose up -d        # starts Postgres, Redis, and Ollama
```

### 5. Pull the LLM Model (for local inference)

```bash
docker exec -it $(docker ps -qf "name=ollama") ollama pull qwen2.5:14b
```

### 6. Run Database Migrations

```bash
alembic upgrade head
```

### 7. Start the Agent

```bash
python main.py
```

The agent starts two concurrent tasks:
- **Incident Loop** — watches Kubernetes events in real time
- **FastAPI Server** — listens on `http://localhost:8080`

---

## Dashboard

```bash
cd dashboard/frontend
npm install
npm run dev     # http://localhost:3000
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/incident/analyze` | Trigger investigation for a pod |
| `POST` | `/incident/approve` | Approve or reject a proposed fix |
| `GET`  | `/incident/history` | Paginated incident history |
| `GET`  | `/cluster/status`  | Live pod health summary |
| `GET`  | `/playbooks`       | List all playbooks |
| `PUT`  | `/playbooks/{name}`| Update a playbook (admin only) |
| `WS`   | `/ws/incidents`    | Real-time incident WebSocket feed |
| `GET`  | `/metrics`         | Prometheus endpoint |
| `GET`  | `/health`          | Healthcheck |

---

## Deploy to Kubernetes

```bash
# Build image
docker build -t sre-agent:latest .

# Create namespace and secrets
kubectl apply -f k8s/cluster-agent-deployment.yaml

# Create the secrets (update values first)
kubectl create secret generic sre-agent-secrets \
  --from-literal=control_plane_url=http://your-control-plane \
  --from-literal=database_url=postgresql+asyncpg://... \
  --from-literal=slack_webhook_url=https://hooks.slack.com/... \
  -n sre-system
```

---

## Running Tests

```bash
pytest tests/unit/ -v
```

---

## Architecture

```
Detection → Router → Playbook Engine → Evidence Collector (parallel)
                                     → Pattern Layer (fast path)
                                     → AI Engine (LLM analysis)
                   → Safety Gate → Engineer Approval → Remediation → Validation
```

> All cluster mutations require **engineer approval** before execution.  
> `delete_namespace` and `delete_deployment` are permanently blocked.

---

## AI Backends

Set `AI_BACKEND` in `.env`:

| Value | Notes |
|-------|-------|
| `ollama` | Local — default dev. Requires `OLLAMA_HOST` + `OLLAMA_MODEL` |
| `openai` | Cloud — requires `OPENAI_API_KEY` |
| `anthropic` | Cloud — requires `ANTHROPIC_API_KEY` |

---

## Project Structure

```
sre-agent/
├── main.py                     # Entrypoint
├── config.py                   # Pydantic settings
├── api/                        # FastAPI routes + auth + websocket
├── agent/                      # Router, Playbooks, Patterns, Safety
├── detection/                  # Kubernetes event watcher
├── infrastructure/             # K8s client, Evidence, Remediation, Validation
├── ai/                         # LLM engine + backends
├── models/                     # SQLAlchemy ORM
├── notifications/              # Slack, Email, PagerDuty
├── observability/              # Prometheus metrics
├── playbooks/                  # YAML playbook definitions
├── knowledge/                  # Pattern knowledge base
├── dashboard/frontend/         # React 18 + TypeScript dashboard
├── k8s/                        # Kubernetes manifests
├── tests/                      # Unit + integration tests
└── migrations/                 # Alembic DB migrations
```

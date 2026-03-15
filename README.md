<div align="center">

<br/>

```
███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗      ██████╗ ██████╗ ███████╗
██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     ██╔═══██╗██╔══██╗██╔════╝
███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     ██║   ██║██████╔╝███████╗
╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     ██║   ██║██╔═══╝ ╚════██║
███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗╚██████╔╝██║     ███████║
╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝ ╚═════╝ ╚═╝     ╚══════╝
```

### Autonomous AI-Powered SRE Platform for Kubernetes Reliability

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3b82f6?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)
[![GitHub Stars](https://img.shields.io/github/stars/yourusername/sentinelops?style=flat-square)](https://github.com/yourusername/sentinelops/stargazers)
[![Contributors](https://img.shields.io/github/contributors/yourusername/sentinelops?style=flat-square)](https://github.com/yourusername/sentinelops/graphs/contributors)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.gg/sentinelops)

<br/>

> **SentinelOps detects, diagnoses, and remediates Kubernetes incidents autonomously —**  
> **cutting MTTR from 60 minutes to under 10 seconds.**

<br/>

[**Get Started**](#-quick-start) · [**Architecture**](#-architecture) · [**API Docs**](#-api-reference) · [**Contributing**](#-contributing) · [**Roadmap**](#-roadmap)

<br/>

</div>

---

## 🧠 What is SentinelOps?

SentinelOps is an **open-source autonomous SRE platform** that brings AI-native incident management to Kubernetes. It watches your cluster 24/7, catches failures the moment they happen, performs deep root-cause analysis using a hybrid of deterministic logic and large language models, and proposes safe, human-approved remediations — all within seconds.

It is not just another alerting tool. SentinelOps closes the loop: from **detection → diagnosis → decision → action → validation**, with a full audit trail and real-time dashboard.

```
Traditional SRE Workflow          SentinelOps Workflow
─────────────────────────         ─────────────────────────
Alert fires (2–5 min)             Event detected (<1 sec)
↓                                 ↓
Engineer paged (5–10 min)         AI collects evidence (<2 sec)
↓                                 ↓
Triage & investigation            Root cause analyzed (<5 sec)
(15–30 min)                       ↓
↓                                 Remediation proposed (<7 sec)
Manual remediation                ↓
(10–20 min)                       Engineer approves (1-click)
↓                                 ↓
Verify & close                    Cluster restored (<10 sec)
(5–10 min)

MTTR: 37–75 minutes               MTTR: 5–10 seconds
```

---

## ✨ Core Capabilities

### 🔭 Real-Time Kubernetes Monitoring
Continuously watches the Kubernetes event stream and pod states. No polling delays. Instant detection.

| Incident Type | Detection Method |
|---|---|
| `CrashLoopBackOff` | Container exit code + restart count analysis |
| `ErrImagePull` / `ImagePullBackOff` | Registry event pattern matching |
| `OOMKilled` | Memory limit breach + container termination signal |
| `Pending` pods | Scheduling failure + resource constraint analysis |
| Deployment failures | Rollout status + replica health monitoring |

---

### 🤖 AI-Assisted Root Cause Analysis

A two-stage analysis pipeline that maximises accuracy while minimising latency:

```
Stage 1: Deterministic Pattern Detection
  ├─ Pod logs analysis
  ├─ Container exit code lookup
  ├─ Known error pattern matching
  └─ Confidence scoring (>85% → direct result)
         ↓ (if inconclusive)
Stage 2: LLM-Assisted Deep Analysis
  ├─ Full evidence context injection
  ├─ Multi-source correlation
  ├─ Structured reasoning chain
  └─ Remediation proposal with explanation
```

**Evidence collected per incident:**
- Pod logs (last N lines, configurable)
- Pod status and container states
- Kubernetes events (namespace-scoped)
- Container exit codes and restart history
- Deployment and ReplicaSet configuration

**Supported AI backends:**

| Backend | Mode | Best For |
|---|---|---|
| [Ollama](https://ollama.com) + `qwen2.5:14b` | Local / Air-gapped | Privacy, offline clusters |
| OpenAI `gpt-4o` | Cloud | High accuracy at scale |
| Anthropic `claude-3-5-sonnet` | Cloud | Reasoning-heavy analysis |

---

### 📋 Playbook-Driven Investigation

All investigations follow structured YAML playbooks — making every analysis deterministic, testable, and auditable.

```yaml
# playbooks/crashloop.yaml
name: crashloop_investigation
triggers:
  - CrashLoopBackOff

steps:
  - collect_logs
  - collect_events
  - check_exit_codes
  - pattern_match:
      patterns:
        - OOMKilled
        - config_error
        - dependency_failure
  - ai_analysis:
      fallback_only: true
  - propose_remediation
```

Custom playbooks can be added and updated at runtime via the API.

---

### 🛡️ Human-in-the-Loop Remediation

SentinelOps **never mutates your cluster without explicit engineer approval.** Every proposed action passes through a safety gate.

**Supported remediation actions:**
- `restart_pod` — Delete and let controller recreate
- `rollback_deployment` — Revert to last stable revision
- `scale_deployment` — Adjust replica count
- `recreate_workload` — Full teardown and redeploy

**Permanently blocked operations** (hardcoded, cannot be overridden):

```python
BLOCKED_OPERATIONS = [
    "delete_namespace",
    "delete_deployment",
    "delete_persistent_volume",
    "drain_node",
]
```

---

### 📊 Incident History & Observability

Full audit trail stored in PostgreSQL. Every incident includes:

| Field | Description |
|---|---|
| `timestamp` | Detection time (microsecond precision) |
| `pod_name` / `namespace` | Affected workload |
| `root_cause` | AI-determined cause |
| `confidence_score` | Analysis confidence (0–1) |
| `remediation_action` | Action taken or proposed |
| `approved_by` | Engineer who approved |
| `resolution_time` | Time from detection to cluster recovery |

Prometheus metrics available at `/metrics` for Grafana integration.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                        │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│   │   Pod    │  │   Pod    │  │   Pod    │  │   Pod    │       │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└────────┼─────────────┼─────────────┼─────────────┼─────────────┘
         │             │             │             │
         └─────────────┴──────┬──────┴─────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Event Watcher     │
                    │  (K8s Watch Stream)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Incident Detection  │
                    │   + Deduplication    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Playbook Engine    │
                    │  (YAML workflows)    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Evidence Collector  │
                    │  logs/events/status  │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼─────────────────┐
              │                │                  │
   ┌──────────▼──────┐  ┌──────▼──────┐  ┌───────▼──────┐
   │Pattern Detection│  │ AI Analysis │  │  Confidence  │
   │  (deterministic)│  │(LLM backend)│  │    Scorer    │
   └──────────┬──────┘  └──────┬──────┘  └───────┬──────┘
              └────────────────┴─────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Safety Gate       │
                    │ (block list check)   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Engineer Approval   │◄──── Dashboard / API
                    │   (1-click via UI)   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Remediation Engine  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Validation Engine   │
                    │ (confirms recovery)  │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼─────────────────┐
              │                │                  │
   ┌──────────▼──────┐  ┌──────▼──────┐  ┌───────▼──────┐
   │   PostgreSQL     │  │  Prometheus │  │  WebSocket   │
   │  Incident Store  │  │   Metrics   │  │  Dashboard   │
   └─────────────────┘  └─────────────┘  └──────────────┘
```

---

## 📁 Project Structure

```
sentinelops/
├── main.py                    # Entrypoint — boots watcher + API server
├── config.py                  # Centralised configuration + env vars
│
├── agent/                     # Core autonomous agent logic
│   ├── incident_handler.py
│   ├── remediation_engine.py
│   └── validation_engine.py
│
├── detection/                 # Incident detection layer
│   ├── event_watcher.py       # K8s watch stream consumer
│   ├── pattern_matcher.py     # Deterministic pattern library
│   └── deduplicator.py
│
├── ai/                        # AI backend abstraction
│   ├── base.py                # Abstract AI interface
│   ├── ollama.py
│   ├── openai.py
│   └── anthropic.py
│
├── api/                       # FastAPI application
│   ├── routers/
│   │   ├── incident.py
│   │   ├── cluster.py
│   │   ├── playbooks.py
│   │   └── auth.py
│   └── websocket.py           # Real-time incident stream
│
├── infrastructure/            # Kubernetes client wrappers
│   ├── k8s_client.py
│   ├── evidence_collector.py
│   └── executor.py
│
├── models/                    # SQLAlchemy ORM models
│   ├── incident.py
│   └── approval.py
│
├── playbooks/                 # YAML investigation playbooks
│   ├── crashloop.yaml
│   ├── image_pull.yaml
│   ├── oom.yaml
│   └── pending.yaml
│
├── notifications/             # Alerting integrations
│   ├── slack.py
│   └── base.py
│
├── observability/             # Prometheus metrics
│   └── metrics.py
│
├── dashboard/
│   └── frontend/              # React dashboard
│       ├── src/
│       ├── package.json
│       └── vite.config.ts
│
├── k8s/                       # Kubernetes manifests
│   ├── cluster-agent-deployment.yaml
│   ├── rbac.yaml
│   └── service.yaml
│
├── migrations/                # Alembic DB migrations
├── tests/                     # Test suite
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── requirements.txt
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Core runtime |
| Docker + Compose | Latest | Infrastructure services |
| kubectl | 1.28+ | Kubernetes access |
| Node.js | 18+ | React dashboard |
| A running Kubernetes cluster | — | Local (kind/minikube) or remote |

Verify your setup:
```bash
python3 --version    # Python 3.11+
docker --version
kubectl cluster-info
node --version       # v18+
```

---

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/sentinelops.git
cd sentinelops
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Database
DATABASE_URL=postgresql+asyncpg://k8s-agent:password@localhost:5432/sre_agent

# AI Backend: ollama | openai | anthropic
AI_BACKEND=ollama
OLLAMA_MODEL=qwen2.5:14b

# Optional: cloud AI fallback
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Auth
SECRET_KEY=your-secret-key-here
```

### 4. Start Infrastructure

```bash
docker compose up -d postgres redis
```

For local AI inference (optional):
```bash
docker compose up -d ollama
docker exec -it $(docker ps -qf "name=ollama") ollama pull qwen2.5:14b
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Start SentinelOps

```bash
python main.py
```

You should see:
```
✓ Database connection established
✓ Kubernetes client initialised
✓ Playbooks loaded (4 playbooks)
✓ AI backend: ollama (qwen2.5:14b)
✓ Incident watcher started
✓ API server running at http://localhost:8080

SentinelOps is watching your cluster.
```

### 7. Start the Dashboard

```bash
cd dashboard/frontend
npm install
npm run dev
```

Open **http://localhost:3000**

---

## 🖥️ Dashboard

The React dashboard provides a real-time view of your cluster health:

- **Overview Panel** — Healthy pods, failing pods, active incidents, MTTR trend
- **Incident Feed** — Live stream of detected incidents with severity badges
- **Approval Queue** — 1-click approve or reject proposed remediations
- **Incident History** — Searchable log with full AI reasoning and resolution timeline
- **Playbook Editor** — View and update investigation playbooks in-browser

Real-time updates are powered by WebSocket at `/ws/incidents`.

---

## 📡 API Reference

Swagger UI: **http://localhost:8080/docs**  
ReDoc: **http://localhost:8080/redoc**

### Authentication

```bash
curl -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'
```

### Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/incident/analyze` | Trigger investigation for a pod |
| `POST` | `/incident/approve` | Approve or reject a remediation |
| `GET` | `/incident/history` | Paginated incident history |
| `GET` | `/incident/activity` | Incident timeline feed |
| `GET` | `/cluster/status` | Live cluster health metrics |
| `GET` | `/playbooks` | List all investigation playbooks |
| `PUT` | `/playbooks/{name}` | Update a playbook |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/health` | Service health check |
| `WS` | `/ws/incidents` | Real-time incident stream |

### Example: Trigger an Investigation

```bash
curl -X POST http://localhost:8080/incident/analyze \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "pod_name": "payment-service-7f9b4",
    "namespace": "production"
  }'
```

**Response:**
```json
{
  "incident_id": "inc_01J8X...",
  "pod_name": "payment-service-7f9b4",
  "root_cause": "ImagePullBackOff — image tag 'v2.1.4' does not exist in registry",
  "confidence": 0.97,
  "evidence": {
    "exit_code": null,
    "last_event": "Failed to pull image: manifest unknown",
    "restart_count": 0
  },
  "proposed_action": "rollback_deployment",
  "proposed_revision": 3,
  "requires_approval": true
}
```

### Example: Approve Remediation

```bash
curl -X POST http://localhost:8080/incident/approve \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "inc_01J8X...",
    "action": "rollback_deployment",
    "approved_by": "alice@company.com",
    "approved": true
  }'
```

---

## 🧪 Testing

### Unit & Integration Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=sentinelops --cov-report=html
```

### Simulate a Live Incident

**Image pull failure:**
```bash
kubectl run bad-image --image=nginx:nonexistent-tag
```

**CrashLoopBackOff:**
```bash
kubectl run crash-test \
  --image=busybox \
  --restart=Never \
  -- /bin/sh -c "exit 1"
```

**OOMKilled (requires memory limits set):**
```bash
kubectl run oom-test \
  --image=polinux/stress \
  --limits='memory=50Mi' \
  -- stress --vm 1 --vm-bytes 100M
```

Watch SentinelOps detect and respond in real time:
```bash
# Terminal 1 — watch pods
kubectl get pods -w

# Terminal 2 — watch agent logs
python main.py

# Terminal 3 — poll incident history
watch -n 2 'curl -s http://localhost:8080/incident/history | jq .'
```

---

## ☸️ Deploying to Kubernetes

### Build & Push Image

```bash
docker build -t your-registry/sentinelops:latest .
docker push your-registry/sentinelops:latest
```

### Create Namespace and Secrets

```bash
kubectl create namespace sre-system

kubectl create secret generic sentinelops-secrets \
  --from-literal=database_url="postgresql+asyncpg://..." \
  --from-literal=slack_webhook_url="https://hooks.slack.com/..." \
  --from-literal=secret_key="your-secret-key" \
  -n sre-system
```

### Deploy

```bash
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/cluster-agent-deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Verify

```bash
kubectl get pods -n sre-system
kubectl logs -f deployment/sentinelops -n sre-system
```

> **RBAC Note:** SentinelOps requires `get`, `list`, `watch` on pods, events, deployments, and replicasets. The `k8s/rbac.yaml` manifest creates the minimum required ClusterRole.

---

## 📈 Observability

### Prometheus Metrics

Metrics available at `GET /metrics`:

| Metric | Type | Description |
|---|---|---|
| `sentinelops_incidents_total` | Counter | Total incidents detected |
| `sentinelops_incidents_by_type` | Counter | Incidents broken down by type |
| `sentinelops_remediation_success_total` | Counter | Successful remediations |
| `sentinelops_ai_analysis_latency_seconds` | Histogram | AI analysis duration |
| `sentinelops_detection_to_approval_seconds` | Histogram | Time from detection to engineer approval |
| `sentinelops_cluster_healthy_pods` | Gauge | Current healthy pod count |
| `sentinelops_cluster_failing_pods` | Gauge | Current failing pod count |

### Grafana Dashboard

Import the pre-built Grafana dashboard from `observability/grafana-dashboard.json`.

---

## 🔒 Security Model

| Layer | Control |
|---|---|
| Cluster mutations | Require explicit engineer approval — no autonomous execution |
| Destructive operations | Hardcoded block list — cannot be enabled via config |
| API access | JWT-based authentication |
| Audit logging | Every action (detection, approval, remediation) is persisted |
| RBAC | Minimum-privilege ClusterRole for Kubernetes access |
| Secrets | Loaded from environment — never hardcoded |

SentinelOps is designed on the principle of **humans staying in control of all destructive decisions.** The AI proposes; engineers decide.

---

## 🗺️ Roadmap

> Community contributions are welcome on all roadmap items. See [CONTRIBUTING.md](CONTRIBUTING.md).

**v1.1 — Multi-Cluster Support**
- [ ] Federated incident dashboard across multiple clusters
- [ ] Per-cluster remediation policies

**v1.2 — Enhanced Intelligence**
- [ ] Predictive incident detection (ML-based anomaly scoring)
- [ ] Automated playbook generation from historical incidents
- [ ] Correlation of cross-service incidents

**v1.3 — Integrations**
- [ ] PagerDuty / OpsGenie auto-ticketing
- [ ] Jira incident ticket creation
- [ ] GitHub Actions workflow triggering post-remediation
- [ ] Datadog / New Relic metric ingestion

**v2.0 — Autonomous Mode (optional, opt-in)**
- [ ] Configurable trust levels for low-risk automated remediations
- [ ] Scheduled maintenance window awareness
- [ ] Full GitOps integration

---

## 🤝 Contributing

SentinelOps is built in the open. All contributions — code, docs, playbooks, bug reports — are welcome.

### How to Contribute

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/your-feature`
3. **Make your changes** with tests
4. **Run the test suite**: `pytest tests/ -v`
5. **Submit a pull request** with a clear description

### Good First Issues

Look for issues tagged [`good first issue`](https://github.com/yourusername/sentinelops/issues?q=is%3Aissue+label%3A%22good+first+issue%22) — these are well-scoped and documented.

### Areas We Need Help

- 🧠 **AI / ML** — Improving pattern detection accuracy, adding new incident classifiers
- 🎨 **Frontend** — Dashboard UX improvements, mobile responsiveness
- 📋 **Playbooks** — Writing playbooks for more incident types (StatefulSets, CronJobs, Ingress failures)
- 🌍 **Integrations** — New AI backends, notification channels, ticketing systems
- 📖 **Documentation** — Tutorials, architecture deep-dives, deployment guides
- 🧪 **Testing** — Expanding test coverage, adding chaos engineering tests

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## 💬 Community

- **Discord**: [Join the SentinelOps server](https://discord.gg/sentinelops) — #general, #help, #contributions
- **GitHub Discussions**: [Ask questions, share ideas](https://github.com/yourusername/sentinelops/discussions)
- **Twitter/X**: [@SentinelOps](https://twitter.com/sentinelops) for releases and updates

---

## 🙏 Acknowledgements

SentinelOps builds on the shoulders of excellent open-source projects:

- [kubernetes/client-python](https://github.com/kubernetes-client/python)
- [FastAPI](https://fastapi.tiangolo.com)
- [SQLAlchemy](https://www.sqlalchemy.org)
- [Ollama](https://ollama.com)
- [Alembic](https://alembic.sqlalchemy.org)

---

## 📄 License

SentinelOps is licensed under the **MIT License** — free to use, modify, and distribute. See [LICENSE](LICENSE) for full terms.

---

<div align="center">

**Built with ❤️ by [Abhishek Mishra](https://github.com/yourusername) and contributors**

*DevOps Engineer · Cloud Infrastructure · Kubernetes · AI Systems*

<br/>

⭐ **If SentinelOps saves your team time, give it a star — it helps others discover the project.**

<br/>

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/sentinelops&type=Date)](https://star-history.com/#yourusername/sentinelops&Date)

</div>

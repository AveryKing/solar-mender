# Solar Mender - CI/CD Repair Agent

> **Self-Healing CI/CD System** that automatically diagnoses, fixes, and opens PRs for GitHub Actions failures using Google Vertex AI and LangGraph.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.10+-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Vertex AI](https://img.shields.io/badge/Vertex%20AI-Gemini%201.5-blue.svg)](https://cloud.google.com/vertex-ai)

## Overview

**Solar Mender** (formerly Diviora Systems CI/CD Repair Agent) is an intelligent automation system that monitors GitHub Actions workflows, diagnoses failures using Google Vertex AI (Gemini models), and automatically creates pull requests with fixes. Built with FastAPI, LangGraph, and Google Cloud Platform.

### Key Features

- **🤖 Autonomous Diagnosis**: Analyzes CI/CD failure logs using Gemini 1.5 Flash
- **🎯 Smart File Location**: Identifies the exact file that needs fixing
- **🛠️ Automated Fixes**: Generates code fixes using Gemini 1.5 Pro
- **📝 PR Creation**: Automatically opens draft PRs with fixes and confidence scores
- **🔒 Safety First**: Confidence thresholds and human-in-the-loop by default
- **💰 Cost Tracking**: Monitors Vertex AI usage with daily cost limits
- **📊 Observability**: Integrated with Langfuse for tracing and monitoring
- **🔄 Async Processing**: Google Cloud Tasks for reliable job queuing

## Architecture

```
┌─────────────────┐
│  GitHub Actions │
│   (Webhook)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   Webhook       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Cloud Tasks    │─────▶│   Worker API     │
│    Queue        │      │  (LangGraph)     │
└─────────────────┘      └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │ Diagnose │─▶│ Locate   │─▶│   Fix    │
            │  (Flash) │  │ (Flash)  │  │  (Pro)   │
            └──────────┘  └──────────┘  └────┬─────┘
                                              │
                                              ▼
                                      ┌──────────────┐
                                      │   PR Node    │
                                      │ (GitHub API) │
                                      └──────────────┘
```

### Technology Stack

- **API Framework**: FastAPI (async)
- **Agent Framework**: LangGraph
- **LLM**: Google Vertex AI (Gemini 1.5 Flash/Pro) via `langchain-google-vertexai`
- **Database**: SQLAlchemy (async) with SQLite (dev) / PostgreSQL (prod)
- **Queue**: Google Cloud Tasks
- **Deployment**: Google Cloud Run
- **Observability**: Langfuse
- **Validation**: Pydantic V2

## Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud Project with billing enabled
- GitHub Personal Access Token (PAT)
- Google Cloud SDK (`gcloud` CLI)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd solar-mender
```

2. **Install dependencies**:
```bash
make install
# or
pip install -r requirements.txt
```

3. **Configure environment variables**:
```bash
cp env.example .env
# Edit .env with your configuration
```

4. **Run locally**:
```bash
make dev
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

The API will be available at `http://localhost:8080` with interactive docs at `http://localhost:8080/docs`.

### Configuration

Key environment variables (see `env.example` for full list):

- **GitHub**: `GITHUB_TOKEN`, `GITHUB_SECRET`
- **Google Cloud**: `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`
- **Database**: `DATABASE_URL`
- **Cloud Tasks**: `CLOUD_TASKS_QUEUE`, `SERVICE_URL`
- **Langfuse**: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`

For detailed configuration, see [Configuration](#configuration) section.

## Deployment

For complete deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

**Quick deployment summary**:
1. Run `scripts/setup_gcp.sh` to set up GCP infrastructure
2. Configure GitHub webhook pointing to your Cloud Run service
3. Set up Workload Identity Federation (WIF) for secure CI/CD
4. Configure environment variables in Cloud Run
5. Deploy using the included GitHub Actions workflow

## How It Works

### Agent Workflow

The repair agent uses a LangGraph-based state machine with the following nodes:

1. **Diagnose Node**: 
   - Fetches GitHub Actions failure logs
   - Uses Gemini 1.5 Flash to identify root cause
   - Returns structured diagnosis with confidence score

2. **Classify Node**:
   - Categorizes failure (dependency, syntax, test, config, etc.)
   - Determines if failure is auto-fixable
   - Routes to fix or abort based on confidence threshold

3. **Locate Node**:
   - Uses Gemini 1.5 Flash to identify target file
   - Gathers related context files (imports, tests, configs)
   - Stores context for the fix node

4. **Fix Node**:
   - Uses Gemini 1.5 Pro to generate fixed code
   - Returns structured response with fix, explanation, and confidence
   - Validates fix quality

5. **PR Node**:
   - Creates new branch
   - Commits fix
   - Opens draft PR with metadata and confidence scores

### Structured Outputs

The agent uses Pydantic models for type-safe LLM responses:

- `DiagnoseResponse`: Root cause and confidence
- `LocateResponse`: Target file path
- `FixResponse`: Fixed content, explanation, and confidence

This ensures reliable parsing and eliminates fragile JSON parsing logic.

## Development

### Project Structure

```
solar-mender/
├── agent/                 # LangGraph agent implementation
│   ├── nodes/            # Agent workflow nodes
│   ├── graph.py          # LangGraph workflow definition
│   ├── llm.py            # Vertex AI client wrapper
│   ├── schemas.py        # Pydantic models for LLM responses
│   ├── state.py          # Agent state definition
│   └── utils.py          # Utilities (cost estimation, etc.)
├── app/                  # FastAPI application
│   ├── api/              # API routes and endpoints
│   ├── core/             # Configuration, logging, cost control
│   ├── db/               # Database models and session management
│   └── schemas/          # Pydantic request/response schemas
├── scripts/              # Deployment and setup scripts
├── tests/                # Test suite
└── requirements.txt      # Python dependencies
```

### Code Quality

```bash
# Lint code
make lint

# Format code (auto-fix)
make format

# Clean Python cache
make clean
```

### Development Workflow

1. Create feature branch
2. Make changes following coding standards (type hints, docstrings, async)
3. Run linter: `make lint`
4. Test locally with `make dev`
5. Commit using conventional commits
6. Open pull request

## Configuration

### Agent Settings

Configurable via environment variables or `app/core/config.py`:

- `MIN_CONFIDENCE_THRESHOLD`: Minimum confidence (0.0-1.0) to proceed with fix (default: 0.7)
- `AUTO_MERGE_ENABLED`: Enable automatic PR merging (default: False)
- `PR_DRAFT_BY_DEFAULT`: Open PRs as drafts (default: True)

### Cost Controls

- `DAILY_COST_LIMIT`: Maximum Vertex AI cost per day in USD (default: 100.0)
- `COST_ALERT_THRESHOLD`: Alert when cost reaches this percentage (default: 0.8)

### Database

- Development: SQLite (`sqlite+aiosqlite:///./local.db`)
- Production: PostgreSQL (`postgresql+asyncpg://user:pass@host:port/db`)

## API Documentation

Interactive API documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc) when running the server.

### Key Endpoints

- `POST /api/v1/webhook/github`: GitHub webhook endpoint
- `POST /api/v1/worker/run`: Cloud Tasks worker endpoint
- `GET /api/v1/metrics`: Job metrics and statistics
- `GET /`: Health check and info

## Monitoring & Observability

### Langfuse Integration

The agent integrates with Langfuse for tracing and monitoring:

- Tracks all LLM calls
- Records token usage and costs
- Monitors agent execution flow
- Provides debugging insights

### Logging

Structured logging via Python's `logging` module:

- Log level configurable via `LOG_LEVEL` environment variable
- Cloud Run logs accessible via `gcloud logging read`

### Metrics

Job metrics available via `/api/v1/metrics`:

- Total jobs processed
- Success/failure rates
- Average confidence scores
- Cost tracking

## Safety Features

- **Infinite Loop Prevention**: Detects and prevents fixing agent's own failures
- **Confidence Thresholds**: Only fixes failures above minimum confidence
- **Draft PRs**: All PRs created as drafts by default for review
- **Cost Limits**: Daily cost limits prevent runaway spending
- **Error Handling**: Comprehensive error handling with graceful degradation

## Troubleshooting

Common issues and solutions:

1. **Webhook 403 Forbidden**: Verify `GITHUB_SECRET` matches in both GitHub and Cloud Run
2. **Vertex AI 403 Permission Denied**: Ensure Vertex AI API is enabled and service account has `roles/aiplatform.user`
3. **Cloud Tasks Failures**: Verify service account has `roles/cloudtasks.enqueuer`
4. **Database Errors**: Check `DATABASE_URL` format and connection

For more details, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#troubleshooting--monitoring).

## Contributing

1. Follow the coding standards in `.cursorrules`
2. Use type hints and docstrings
3. Write async code for I/O operations
4. Run linter before committing
5. Update documentation as needed

## License

[Add your license here]

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ by Diviora Systems**

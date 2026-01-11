# Implementation Plan: Solar Mender CI/CD Repair Agent

This document outlines the technical implementation details, architecture decisions, and development approach for the Solar Mender project.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Component Breakdown](#component-breakdown)
4. [Data Flow](#data-flow)
5. [Database Schema](#database-schema)
6. [Agent Workflow](#agent-workflow)
7. [LLM Integration](#llm-integration)
8. [Security & Safety](#security--safety)
9. [Development Workflow](#development-workflow)
10. [Testing Strategy](#testing-strategy)
11. [Deployment Architecture](#deployment-architecture)
12. [Future Enhancements](#future-enhancements)

## Architecture Overview

Solar Mender is built as a cloud-native, event-driven system that processes GitHub Actions failures through an intelligent agent pipeline.

### High-Level Architecture

```
GitHub Actions → Webhook → FastAPI → Cloud Tasks → Worker → LangGraph Agent → GitHub API
                                      ↓
                                   Database
                                      ↓
                                  Langfuse
```

### Design Principles

1. **Event-Driven**: Asynchronous processing via Cloud Tasks queue
2. **Resilient**: Graceful error handling, retries, and state tracking
3. **Observable**: Comprehensive logging and tracing via Langfuse
4. **Safe**: Human-in-the-loop, confidence thresholds, cost controls
5. **Scalable**: Stateless workers, horizontal scaling on Cloud Run

## Technology Stack

### Core Framework

- **FastAPI 0.109+**: Modern, fast async web framework
- **Python 3.11+**: Required for modern async features and type hints

### Agent Framework

- **LangGraph 0.0.10+**: State machine framework for agent workflows
- **LangChain**: Base framework for LLM integration
- **langchain-google-vertexai**: Google Vertex AI integration for LangChain

### LLM Provider

- **Google Vertex AI**: 
  - Gemini 1.5 Flash (diagnosis, file location)
  - Gemini 1.5 Pro (code fixes)
- **Structured Outputs**: Pydantic models via `with_structured_output()`

### Data Layer

- **SQLAlchemy 2.0+**: Async ORM
- **aiosqlite**: SQLite async driver (development)
- **asyncpg**: PostgreSQL async driver (production)

### Infrastructure

- **Google Cloud Run**: Serverless container hosting
- **Google Cloud Tasks**: Reliable job queue
- **Artifact Registry**: Container image storage
- **Cloud SQL (optional)**: Managed PostgreSQL for production

### Observability

- **Langfuse**: LLM tracing and monitoring
- **Cloud Logging**: Application logs
- **Python logging**: Structured logging

### Validation

- **Pydantic V2**: Data validation and settings management
- **pydantic-settings**: Environment variable configuration

## Component Breakdown

### Agent Module (`agent/`)

The agent module contains the LangGraph-based repair workflow.

#### Core Files

- **`agent/graph.py`**: Defines the LangGraph state machine workflow
- **`agent/state.py`**: TypedDict definition for agent state
- **`agent/llm.py`**: ChatVertexAI client wrapper with lazy initialization
- **`agent/schemas.py`**: Pydantic models for structured LLM outputs
- **`agent/utils.py`**: Utilities (cost estimation, etc.)

#### Nodes (`agent/nodes/`)

Each node represents a step in the repair workflow:

1. **`diagnose.py`**: 
   - Fetches GitHub Actions logs
   - Uses Gemini 1.5 Flash with `DiagnoseResponse` schema
   - Returns root cause and confidence

2. **`classify.py`**: 
   - Categorizes failure type
   - Determines if auto-fixable
   - Routes based on confidence

3. **`locate.py`**: 
   - Uses Gemini 1.5 Flash with `LocateResponse` schema
   - Identifies target file
   - Gathers context files

4. **`fix.py`**: 
   - Uses Gemini 1.5 Pro with `FixResponse` schema
   - Generates fixed code
   - Returns fix with explanation

5. **`github_pr.py`**: 
   - Creates branch
   - Commits fix
   - Opens draft PR

#### Supporting Modules

- **`agent/classification.py`**: Failure category classification logic
- **`agent/context.py`**: Context file gathering utilities
- **`agent/prompts.py`**: Prompt templates for LLM calls

### Application Module (`app/`)

FastAPI application with API routes, database models, and core services.

#### API Layer (`app/api/`)

- **`router.py`**: API route registration
- **`webhook.py`**: GitHub webhook handler with signature verification
- **`worker.py`**: Cloud Tasks worker endpoint that executes the agent
- **`metrics.py`**: Metrics and statistics endpoints
- **`deps.py`**: Dependency injection (database sessions, etc.)

#### Core Services (`app/core/`)

- **`config.py`**: Pydantic Settings for configuration management
- **`logging.py`**: Logging configuration
- **`cost_control.py`**: Cost tracking and limits
- **`cloud_tasks.py`**: Cloud Tasks client utilities

#### Database Layer (`app/db/`)

- **`base.py`**: SQLAlchemy base, engine, session factory
- **`models.py`**: Database models (RepairJob, JobStatus enum)

#### Schemas (`app/schemas/`)

- **`webhook.py`**: GitHub webhook payload schemas
- **`job.py`**: Repair job request/response schemas

## Data Flow

### 1. Webhook Reception

```
GitHub Actions Failure
  ↓
GitHub Webhook (POST /api/v1/webhook/github)
  ↓
Signature Verification (HMAC)
  ↓
Parse Payload (Pydantic validation)
  ↓
Create RepairJob (Database)
  ↓
Enqueue Cloud Task
  ↓
Return 200 OK
```

### 2. Agent Execution

```
Cloud Tasks → Worker Endpoint
  ↓
Load RepairJob from Database
  ↓
Initialize LangGraph Agent
  ↓
Execute Workflow:
  ├─ Diagnose Node
  ├─ Classify Node
  ├─ Locate Node
  ├─ Fix Node
  └─ PR Node
  ↓
Update RepairJob Status
  ↓
Return Success/Failure
```

### 3. LLM Interaction Flow

```
Node → Get Model (ChatVertexAI)
  ↓
Configure Structured Output (Pydantic schema)
  ↓
Build Prompt
  ↓
Invoke LLM (async)
  ↓
Parse Structured Response
  ↓
Extract Token Usage
  ↓
Estimate Cost
  ↓
Update State
```

## Database Schema

### RepairJob Model

```python
class RepairJob(Base):
    id: int (PK)
    repo_name: str (indexed)
    run_id: str (indexed)
    status: JobStatus (enum: PENDING, FIXING, PR_OPENED, FAILED)
    
    # Analysis Results
    error_log_summary: str (nullable)
    root_cause: str (nullable)
    diagnosis_confidence: float (nullable)
    fix_confidence: float (nullable)
    failure_category: str (nullable)
    
    # Output
    pr_url: str (nullable)
    pr_draft: bool
    
    # Cost Tracking
    vertex_cost_est: float
    
    # Audit
    reasoning_log: str (nullable)
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

## Agent Workflow

### LangGraph State Machine

```
START
  ↓
[Diagnose] → Fetch logs, analyze with Gemini Flash
  ↓
[Classify] → Categorize, check confidence
  ↓
  ├─ FAILED → END
  └─ SUCCESS → [Locate]
                ↓
                [Fix] → Generate fix with Gemini Pro
                ↓
                [PR] → Create pull request
                ↓
                END
```

### State Schema

```python
class AgentState(TypedDict):
    # Core IDs
    job_id: int
    run_id: str
    repo_name: str
    
    # Context
    error_logs: Optional[str]
    root_cause: Optional[str]
    target_file_path: Optional[str]
    original_content: Optional[str]
    fixed_content: Optional[str]
    context_files: Optional[dict]
    
    # Metrics
    diagnosis_confidence: Optional[float]
    fix_confidence: Optional[float]
    failure_category: Optional[str]
    total_cost: float
    
    # Status
    status: Optional[str]
    error: Optional[str]
    
    # Output
    pr_url: Optional[str]
    pr_draft: bool
    commit_author: Optional[str]
```

## LLM Integration

### Vertex AI Client

The `VertexAIClient` class provides a singleton wrapper around ChatVertexAI:

- **Lazy Initialization**: Models initialized on first use
- **Model Selection**: Flash (fast, cheap) vs Pro (powerful, expensive)
- **Configuration**: Project, location, temperature, max tokens

### Structured Outputs

All LLM calls use Pydantic schemas via `with_structured_output()`:

- **Type Safety**: Validated responses, no JSON parsing errors
- **Documentation**: Schema fields serve as LLM instructions
- **Reliability**: Eliminates fragile string parsing

### Cost Estimation

Token usage extracted from `usage_metadata`:

- Input/output token counts
- Per-model pricing (Flash vs Pro)
- Aggregated per-job cost tracking

## Security & Safety

### Webhook Security

- **HMAC Signature Verification**: `X-Hub-Signature-256` header validation
- **Secret Management**: Environment variable for webhook secret

### Agent Safety

- **Infinite Loop Prevention**: Checks commit author to prevent self-fixes
- **Confidence Thresholds**: Configurable minimum confidence (default: 0.7)
- **Draft PRs**: All PRs created as drafts by default
- **Category Filtering**: Skips infrastructure/timeout failures

### Cost Controls

- **Daily Limits**: Maximum cost per day (default: $100)
- **Alert Thresholds**: Alert at 80% of limit
- **Token Tracking**: Accurate cost estimation per job

### Authentication

- **GitHub**: Personal Access Token (PAT) or fine-grained token
- **GCP**: Workload Identity Federation (WIF) for CI/CD
- **Service Accounts**: Least-privilege IAM roles

## Development Workflow

### Code Standards

1. **Type Hints**: Required for all functions, variables, return types
2. **Docstrings**: Google-style docstrings for modules, classes, functions
3. **Async/Await**: Use async for all I/O operations
4. **Error Handling**: Custom exceptions, Pydantic validation
5. **Linting**: Ruff for code quality

### Directory Structure

- `agent/`: Agent implementation (LangGraph, nodes, LLM)
- `app/`: FastAPI application (API, database, core services)
- `scripts/`: Deployment and setup scripts
- `tests/`: Test suite
- `.tasks/`: Task tracking markdown files

### Git Workflow

1. Feature branches from `main`
2. Conventional commit messages
3. Pull requests for review
4. CI/CD via GitHub Actions

## Testing Strategy

### Unit Tests

- Node functions with mocked dependencies
- Classification logic
- Cost estimation utilities
- Schema validation

### Integration Tests

- Agent workflow execution
- Database operations
- API endpoints
- Cloud Tasks integration

### E2E Tests

- Full webhook → agent → PR flow
- Error scenarios
- Cost limit enforcement

## Deployment Architecture

### Google Cloud Platform

- **Cloud Run**: Serverless container hosting
  - Auto-scaling
  - HTTPS by default
  - Environment variables for config

- **Cloud Tasks**: Job queue
  - Reliable delivery
  - Retry logic
  - Rate limiting

- **Artifact Registry**: Container images
  - Docker image storage
  - Versioning

### GitHub Integration

- **Webhook**: Configured in repository settings
- **Workload Identity Federation**: Secure authentication for CI/CD
- **GitHub Actions**: Automated deployment workflow

### Environment Configuration

- **Development**: SQLite, local testing
- **Production**: PostgreSQL, Cloud Run, Cloud Tasks

## Future Enhancements

### Short-Term

1. **Enhanced Log Fetching**: Real GitHub Actions log retrieval (currently mocked)
2. **Multi-File Fixes**: Support for fixing multiple files in one PR
3. **Test Generation**: Generate/update tests for fixes
4. **Better Context**: Improved context file gathering with AST parsing

### Medium-Term

1. **Multi-Repository Support**: Process failures across multiple repos
2. **Custom Prompts**: Allow repository-specific prompt customization
3. **Fix Validation**: Run tests/linters before creating PR
4. **PR Comments**: Add detailed explanations as PR comments

### Long-Term

1. **Learning System**: Track fix success rates and improve prompts
2. **Multi-Agent Architecture**: Specialized agents for different failure types
3. **Cost Optimization**: Model selection based on failure complexity
4. **Integration Extensions**: Support for GitLab, Bitbucket, etc.

## Implementation Status

### Completed ✅

- Core agent workflow (diagnose, classify, locate, fix, PR)
- Vertex AI integration with structured outputs
- FastAPI webhook and worker endpoints
- Database models and async session management
- Cost tracking and estimation
- Langfuse integration for observability
- Deployment scripts and documentation

### In Progress 🔄

- Enhanced log fetching from GitHub Actions
- Comprehensive test suite
- Production database migration scripts

### Planned 📋

- Multi-file fix support
- Fix validation before PR creation
- Custom prompt configuration
- Advanced context gathering

---

**Last Updated**: 2025-01-XX
**Version**: 1.0.0

# Solar Mender MCP Implementation

This document provides implementation details for the MCP (Model Context Protocol) integration in Solar Mender.

## Overview

The MCP integration allows IDE agents (like Cursor) to delegate tasks to Solar Mender's server-side agents via standardized tools and resources. This document covers the technical implementation.

## Architecture Components

### 1. Base Agent Interface

**File**: `agent/base.py`

All agents implement the `BaseAgent` interface which includes:

```python
def get_mcp_tools(self) -> List[Dict[str, Any]]:
    """Return MCP tools this agent exposes."""
    return []

def get_mcp_resources(self) -> List[Dict[str, Any]]:
    """Return MCP resources this agent exposes."""
    return []
```

### 2. MCP Tool Handler

**File**: `app/api/mcp.py`

The unified handler for all MCP tool invocations:

- **Endpoint**: `POST /api/v1/mcp/invoke`
- **Request Model**: `MCPToolRequest` with `tool_name` and `arguments`
- **Response Model**: `MCPToolResponse` with `success`, `result`, and `error`

**Flow**:
1. Receive tool invocation request
2. Discover tool across all registered agents
3. Route to specialized handler
4. Execute tool via agent's `invoke()` method
5. Return structured response

### 3. MCP Resource Handler

**File**: `app/api/resources.py`

Handles MCP resource access:

- **Endpoints**:
  - `GET /api/v1/resources/audit/latest` - Latest audit results
  - `GET /api/v1/resources/audit/recent` - Recent audit runs

Resources are served as JSON with appropriate MIME types.

## Implemented Agents

### RepairAgent

**File**: `agent/repair/agent.py`

**MCP Tools**:
- `repair_ci_failure` - Original repair tool
- `mender.monitor_deployment` - NEW: Deployment monitoring delegation

**Implementation**:
- Creates job record in database
- Monitors GitHub Actions run status
- Triggers repair agent automatically on failure
- Returns job ID for status tracking

### CommitmentAgent

**File**: `agent/commitment/agent.py`

**MCP Tools**:
- `mender.craft_commit` - Generate high-fidelity commit messages

**Implementation**:
- Uses `CommitmentAgent` graph with `craft_commit_node`
- Leverages Gemini 1.5 Pro for message generation
- Follows guidelines from `.workflows/commit.md`
- Returns commit message with logical groups

### AuditAgent

**File**: `agent/audit/agent.py`

**MCP Tools**:
- `mender.run_audit` - Trigger codebase audit

**MCP Resources**:
- `mender://audit/latest` - Latest audit results
- `mender://audit/recent` - Recent audit runs

**Implementation Status**: Base structure in place, full implementation pending.

## Database Schema

MCP tool invocations create job records using the existing `RepairJob` model:

```python
class RepairJob(Base):
    id: int
    repo_name: str
    run_id: str
    status: JobStatus
    vertex_cost_est: float
    # ... other fields
```

## Error Handling

All MCP tool invocations:

1. **Validate input** using Pydantic schemas
2. **Catch exceptions** and return structured error responses
3. **Log errors** with full context for debugging
4. **Return appropriate status codes** (404 for not found, 500 for server errors)

## Async Patterns

MCP handlers use async/await throughout:

- All database operations are async
- Agent invocations are async
- External API calls (GitHub, Vertex AI) are async
- Cloud Tasks creation uses `run_in_executor` for sync SDK

## Testing Considerations

### Unit Tests
- Test tool discovery logic
- Test specialized handlers
- Test error handling

### Integration Tests
- Test tool invocation end-to-end
- Test agent registration
- Test resource access

### Mocking
- Mock GitHub API calls
- Mock Vertex AI calls
- Mock database operations
- Mock Cloud Tasks

## Configuration

MCP integration uses existing configuration from `app/core/config.py`:

- `GITHUB_TOKEN` - For GitHub API access
- `GOOGLE_CLOUD_PROJECT` - For Cloud Tasks
- `SERVICE_URL` - For Cloud Tasks callbacks
- Vertex AI settings for LLM calls

## Security Considerations

1. **Authentication**: MCP endpoints should be protected in production
2. **Rate Limiting**: Implement rate limiting for tool invocations
3. **Input Validation**: All inputs validated via Pydantic
4. **Error Messages**: Don't expose internal errors to clients
5. **Resource Access**: Implement access control for resources

## Performance

1. **Caching**: Consider caching audit results
2. **Async Execution**: All I/O operations are async
3. **Connection Pooling**: Database connections pooled
4. **Batching**: Batch operations where possible

## Monitoring

Monitor:

1. **Tool invocation latency**
2. **Error rates by tool**
3. **Agent execution times**
4. **Cost tracking per tool invocation**

## Future Enhancements

1. **WebSocket Support**: Real-time updates for long-running operations
2. **Tool Versioning**: Version MCP tools for backward compatibility
3. **Tool Discovery**: More sophisticated tool discovery and routing
4. **Resource Pagination**: Pagination for resource lists
5. **Streaming Responses**: Stream large responses
6. **Authentication**: OAuth/JWT for MCP endpoints
7. **Rate Limiting**: Per-tool rate limiting
8. **Metrics**: Prometheus/OpenTelemetry integration

## Code Organization

```
app/
  api/
    mcp.py              # MCP tool handler
    resources.py        # MCP resource handler
    router.py           # Route registration
agent/
  base.py              # BaseAgent interface
  repair/
    agent.py           # RepairAgent with MCP tools
  commitment/
    agent.py           # CommitmentAgent with MCP tools
  audit/
    agent.py           # AuditAgent with MCP tools/resources
docs/
  MCP_INTEGRATION.md   # User-facing documentation
  WORKFLOW_EVOLUTION.md # Strategic overview
  MCP_IMPLEMENTATION.md # This file
```

## See Also

- [MCP Integration Guide](MCP_INTEGRATION.md) - User-facing API documentation
- [Workflow Evolution](WORKFLOW_EVOLUTION.md) - Strategic overview
- [Base Agent Interface](../agent/base.py) - Implementation reference

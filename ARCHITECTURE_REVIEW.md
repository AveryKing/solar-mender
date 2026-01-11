# Architecture Review: Preparing for Multi-Agent MCP System

This document reviews the current architecture and provides recommendations for transitioning to a multi-agent system with MCP (Model Context Protocol) integration.

## Current Architecture Assessment

### Strengths ✅

1. **Clean Separation of Concerns**
   - API layer (`app/api/`) is separate from agent logic (`agent/`)
   - Database models are well-structured
   - Configuration management via Pydantic Settings

2. **Async-First Design**
   - FastAPI with async/await throughout
   - SQLAlchemy async ORM
   - LangGraph async execution

3. **Scalable Infrastructure**
   - Cloud Run for horizontal scaling
   - Cloud Tasks for reliable job queuing
   - Stateless workers

4. **Observability**
   - Langfuse integration for LLM tracing
   - Structured logging
   - Cost tracking

5. **Type Safety**
   - Pydantic V2 for validation
   - Type hints throughout
   - Structured LLM outputs

### Critical Issues for Multi-Agent MCP System ⚠️

#### 1. **Monolithic Agent Design**

**Problem:**
- Single hardcoded agent (`repair_agent`) in `agent/graph.py`
- No agent abstraction or interface
- Worker endpoint (`app/api/worker.py`) directly imports and calls `repair_agent`

**Impact:**
- Cannot add new agents without code changes
- No agent discovery or routing mechanism
- Difficult to support multiple agent types

**Current Code:**
```python
# agent/graph.py
repair_agent = create_repair_graph()  # Singleton, hardcoded

# app/api/worker.py
from agent.graph import repair_agent  # Direct import
final_state = await repair_agent.ainvoke(initial_state)
```

#### 2. **No Agent Registry**

**Problem:**
- No mechanism to register/discover agents
- No agent metadata (name, description, capabilities)
- Cannot route requests to appropriate agents

**Impact:**
- IDE agent (MCP client) cannot discover available agents
- No way to query agent capabilities
- Manual configuration required for each agent

#### 3. **No MCP Integration**

**Problem:**
- No MCP server capability
- No MCP client capability for inter-agent communication
- Agents cannot expose tools/resources via MCP

**Impact:**
- IDE agent (Cursor) cannot communicate with agents via MCP
- Agents cannot communicate with each other
- Missing standard protocol for agent-to-agent interaction

#### 4. **Specific State Schema**

**Problem:**
- `AgentState` is specific to repair workflow
- Hardcoded fields (error_logs, root_cause, target_file_path, etc.)
- Not extensible for other agent types

**Current State:**
```python
class AgentState(TypedDict):
    job_id: int
    run_id: str
    repo_name: str
    error_logs: Optional[str]  # Repair-specific
    root_cause: Optional[str]  # Repair-specific
    # ... more repair-specific fields
```

**Impact:**
- Each new agent type needs its own state schema
- No common state interface
- Difficult to share state between agents

#### 5. **Database Schema Too Specific**

**Problem:**
- `RepairJob` model is specific to repair workflow
- Hardcoded fields (error_log_summary, diagnosis_confidence, etc.)
- Not generic enough for other job types

**Impact:**
- Need separate tables for each agent type
- Difficult to query across agent types
- No unified job management

#### 6. **No Inter-Agent Communication**

**Problem:**
- Agents cannot call other agents
- No message broker or event system
- No agent-to-agent API

**Impact:**
- Agents cannot collaborate
- Cannot build agent hierarchies
- Missing orchestration layer

#### 7. **Tight Coupling to GitHub**

**Problem:**
- Webhook handler is GitHub-specific
- State assumes GitHub repository structure
- Hardcoded GitHub API calls in nodes

**Impact:**
- Difficult to support other platforms (GitLab, Bitbucket)
- Platform-specific logic scattered throughout
- Not platform-agnostic

## Recommended Architecture for Multi-Agent MCP System

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    IDE Agent (Cursor)                    │
│                   (MCP Client)                          │
└────────────────────┬────────────────────────────────────┘
                     │ MCP Protocol
                     │ (JSON-RPC over stdio/HTTP)
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Agent Orchestration Layer                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │          MCP Server                              │  │
│  │  - Exposes agent tools/resources                 │  │
│  │  - Routes requests to agents                     │  │
│  │  - Handles agent discovery                       │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Agent Registry                          │  │
│  │  - Agent metadata                                │  │
│  │  - Capabilities                                  │  │
│  │  - Routing rules                                 │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌───────────┐ ┌───────────┐ ┌───────────┐
│  Repair   │ │   Test    │ │   Review  │
│  Agent    │ │   Agent   │ │   Agent   │
│ (MCP)     │ │  (MCP)    │ │  (MCP)    │
└─────┬─────┘ └─────┬─────┘ └─────┬─────┘
      │             │             │
      └─────────────┼─────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
  ┌─────────┐ ┌─────────┐ ┌─────────┐
  │ Vertex  │ │ GitHub  │ │  DB     │
  │   AI    │ │   API   │ │         │
  └─────────┘ └─────────┘ └─────────┘
```

### Core Components

#### 1. **Agent Interface/Abstraction**

Create a base agent interface that all agents implement:

```python
# agent/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langgraph.graph import CompiledGraph

class BaseAgent(ABC):
    """Base interface for all agents."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Agent identifier."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Agent description."""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> list[str]:
        """List of agent capabilities."""
        pass
    
    @property
    @abstractmethod
    def graph(self) -> CompiledGraph:
        """LangGraph compiled graph."""
        pass
    
    @abstractmethod
    async def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent with given state."""
        pass
    
    @abstractmethod
    def get_mcp_tools(self) -> list[Dict[str, Any]]:
        """Return MCP tools this agent exposes."""
        pass
    
    @abstractmethod
    def get_mcp_resources(self) -> list[Dict[str, Any]]:
        """Return MCP resources this agent exposes."""
        pass
```

#### 2. **Agent Registry**

Central registry for agent discovery:

```python
# agent/registry.py
from typing import Dict, Optional
from agent.base import BaseAgent

class AgentRegistry:
    """Registry for managing agents."""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
    
    def register(self, agent: BaseAgent) -> None:
        """Register an agent."""
        self._agents[agent.name] = agent
    
    def get(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name."""
        return self._agents.get(name)
    
    def list_agents(self) -> list[BaseAgent]:
        """List all registered agents."""
        return list(self._agents.values())
    
    def get_agent_metadata(self) -> list[Dict[str, Any]]:
        """Get metadata for all agents (for MCP discovery)."""
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "tools": agent.get_mcp_tools(),
                "resources": agent.get_mcp_resources(),
            }
            for agent in self._agents.values()
        ]
```

#### 3. **MCP Server Integration**

MCP server to expose agents to IDE:

```python
# app/mcp/server.py
from mcp.server import Server
from agent.registry import AgentRegistry

class AgentMCPServer:
    """MCP server for exposing agents."""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.server = Server("solar-mender-agents")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP handlers for agent tools/resources."""
        # Tools: agent actions
        # Resources: agent state/status
        pass
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request and route to appropriate agent."""
        pass
```

#### 4. **Generic Job Model**

Replace `RepairJob` with generic `AgentJob`:

```python
# app/db/models.py
class AgentJob(Base):
    """Generic job model for all agent types."""
    
    id: int
    agent_name: str  # Which agent handles this
    job_type: str  # Type of job (repair, test, review, etc.)
    status: JobStatus
    input_data: JSON  # Generic input (flexible schema)
    output_data: Optional[JSON]  # Generic output
    metadata: JSON  # Agent-specific metadata
    # ... timestamps, cost tracking, etc.
```

#### 5. **Generic Agent State**

Use a flexible state schema:

```python
# agent/state.py
from typing import TypedDict, Dict, Any, Optional

class GenericAgentState(TypedDict):
    """Generic agent state that all agents can use."""
    
    # Common fields
    job_id: int
    agent_name: str
    status: str
    error: Optional[str]
    
    # Flexible data storage
    data: Dict[str, Any]  # Agent-specific data
    
    # Metadata
    metadata: Dict[str, Any]
    total_cost: float
```

#### 6. **Agent Router/Dispatcher**

Router to dispatch jobs to appropriate agents:

```python
# app/core/router.py
from agent.registry import AgentRegistry
from app.db.models import AgentJob

class AgentRouter:
    """Routes jobs to appropriate agents."""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
    
    async def route_job(self, job: AgentJob) -> Dict[str, Any]:
        """Route job to appropriate agent."""
        agent = self.registry.get(job.agent_name)
        if not agent:
            raise ValueError(f"Agent {job.agent_name} not found")
        
        initial_state = {
            "job_id": job.id,
            "agent_name": job.agent_name,
            "status": "RUNNING",
            "data": job.input_data,
            "metadata": job.metadata,
            "total_cost": 0.0,
        }
        
        return await agent.invoke(initial_state)
```

## Migration Path

### Phase 1: Agent Abstraction (Short-term)

1. Create `BaseAgent` interface
2. Refactor `repair_agent` to implement `BaseAgent`
3. Create `AgentRegistry`
4. Register repair agent in registry

**Changes:**
- `agent/base.py` - New base agent interface
- `agent/registry.py` - New agent registry
- `agent/repair_agent.py` - Refactor repair agent to implement BaseAgent
- `app/api/worker.py` - Use registry instead of direct import

### Phase 2: Generic Models (Short-term)

1. Create generic `AgentJob` model
2. Migrate `RepairJob` data to `AgentJob`
3. Update API endpoints to use `AgentJob`
4. Create migration script

**Changes:**
- `app/db/models.py` - Add `AgentJob`, deprecate `RepairJob`
- Database migration
- API updates

### Phase 3: MCP Integration (Medium-term)

1. Add MCP server dependency (`mcp` package)
2. Implement `AgentMCPServer`
3. Expose agents as MCP tools/resources
4. Test with Cursor/MCP client

**Changes:**
- `app/mcp/server.py` - New MCP server
- `requirements.txt` - Add MCP dependency
- Update deployment for MCP server

### Phase 4: Inter-Agent Communication (Long-term)

1. Implement MCP client for agent-to-agent calls
2. Add message broker (Pub/Sub or similar)
3. Create agent orchestration layer
4. Support agent hierarchies

**Changes:**
- `app/mcp/client.py` - MCP client for agents
- Message broker integration
- Orchestration layer

## Specific Recommendations

### 1. Immediate Actions

1. **Create Agent Abstraction Layer**
   - Define `BaseAgent` interface
   - Refactor current agent to implement interface
   - Create `AgentRegistry`

2. **Make State Generic**
   - Use `Dict[str, Any]` for flexible data
   - Keep common fields separate
   - Allow agents to define their own schema

3. **Separate Platform Logic**
   - Extract GitHub-specific code to `app/integrations/github/`
   - Create platform abstraction
   - Support multiple platforms

### 2. Database Changes

1. **Generic Job Model**
   - `AgentJob` with JSON fields for flexibility
   - `agent_name` for routing
   - `job_type` for categorization

2. **Agent Metadata Table**
   - Store agent capabilities
   - Track agent versions
   - Store configuration

### 3. API Changes

1. **Agent Discovery Endpoint**
   - `GET /api/v1/agents` - List all agents
   - `GET /api/v1/agents/{name}` - Get agent details
   - `GET /api/v1/agents/{name}/tools` - Get MCP tools

2. **Generic Worker Endpoint**
   - Accept `agent_name` in payload
   - Route to appropriate agent via registry
   - Support multiple job types

### 4. MCP Integration Points

1. **Agent Tools**
   - Each agent exposes tools via MCP
   - IDE can call agent actions
   - Tools correspond to agent capabilities

2. **Agent Resources**
   - Agent state/status as resources
   - Job results as resources
   - Real-time updates via MCP

3. **MCP Server**
   - Standalone MCP server process
   - Or integrate into FastAPI (HTTP transport)
   - Support stdio and HTTP transports

## File Structure Recommendations

```
solar-mender/
├── agent/
│   ├── base.py              # BaseAgent interface (NEW)
│   ├── registry.py          # AgentRegistry (NEW)
│   ├── repair/
│   │   ├── __init__.py
│   │   ├── agent.py         # RepairAgent (refactored)
│   │   ├── graph.py         # Repair graph
│   │   ├── nodes/           # Repair nodes
│   │   └── state.py         # Repair-specific state
│   ├── test/                # Test agent (NEW)
│   │   └── ...
│   └── review/              # Review agent (NEW)
│       └── ...
├── app/
│   ├── mcp/                 # MCP integration (NEW)
│   │   ├── server.py        # MCP server
│   │   ├── client.py        # MCP client (for agents)
│   │   └── handlers.py      # MCP request handlers
│   ├── integrations/        # Platform integrations (NEW)
│   │   ├── github/
│   │   └── gitlab/
│   └── ...
└── ...
```

## Summary

### Current Architecture: 6/10 for Multi-Agent MCP

**Strengths:**
- Good foundation (async, type-safe, scalable)
- Clean separation of concerns
- Observability built-in

**Critical Gaps:**
- No agent abstraction
- No agent registry
- No MCP integration
- Too specific (state, database, platform)
- No inter-agent communication

### Recommended Priority

1. **High Priority** (Blockers for multi-agent):
   - Agent abstraction layer
   - Agent registry
   - Generic job/state models

2. **Medium Priority** (Required for MCP):
   - MCP server implementation
   - Agent tool/resource exposure
   - Discovery endpoints

3. **Low Priority** (Nice to have):
   - Inter-agent communication
   - Agent orchestration
   - Advanced routing

### Estimated Effort

- **Phase 1** (Agent Abstraction): 1-2 days
- **Phase 2** (Generic Models): 1-2 days
- **Phase 3** (MCP Integration): 3-5 days
- **Phase 4** (Inter-Agent Communication): 5-10 days

**Total**: ~2-3 weeks for full multi-agent MCP system

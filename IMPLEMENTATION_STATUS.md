# Multi-Agent MCP Architecture Implementation Status

This document tracks the implementation status of the multi-agent MCP architecture migration.

## Completed ✅

### Phase 1: Agent Abstraction Layer

- ✅ **BaseAgent Interface** (`agent/base.py`)
  - Abstract base class for all agents
  - Defines required methods: `name`, `description`, `capabilities`, `graph`, `invoke`
  - MCP integration hooks: `get_mcp_tools()`, `get_mcp_resources()`

- ✅ **Agent Registry** (`agent/registry.py`)
  - Central registry for agent discovery
  - Agent registration and lookup
  - Metadata access for MCP discovery
  - Global singleton pattern

- ✅ **Repair Agent Refactored** (`agent/repair/agent.py`)
  - Implements `BaseAgent` interface
  - Moved to `agent/repair/` directory
  - Exposes MCP tools and resources
  - Maintains backward compatibility

- ✅ **Repair Agent Structure**
  - `agent/repair/graph.py` - LangGraph workflow definition
  - `agent/repair/state.py` - RepairAgentState TypedDict
  - `agent/repair/nodes/` - All repair nodes (updated imports)
  - `agent/repair/utils.py` - Langfuse callback helper

- ✅ **Worker Updated** (`app/api/worker.py`)
  - Uses `AgentRegistry` instead of direct import
  - Routes to appropriate agent based on `agent_name`
  - Supports generic and repair-specific states
  - Backward compatible (defaults to "repair" agent)

- ✅ **Agent Discovery Endpoints** (`app/api/agents.py`)
  - `GET /api/v1/agents` - List all agents
  - `GET /api/v1/agents/{agent_name}` - Get agent metadata
  - `GET /api/v1/agents/{agent_name}/tools` - Get MCP tools
  - `GET /api/v1/agents/{agent_name}/resources` - Get MCP resources

- ✅ **Agent Registration** (`app/core/agents.py`)
  - `register_agents()` function
  - Called during application startup
  - Registers repair agent

- ✅ **Generic State** (`agent/state.py`)
  - Generic `AgentState` TypedDict
  - Flexible `data` and `metadata` fields
  - Agent-specific states can extend this

## In Progress 🔄

None - Core implementation complete

## Pending 📋

### Phase 2: Generic Models (Optional - can be done incrementally)

- ⏳ **Generic AgentJob Model**
  - Replace `RepairJob` with generic `AgentJob`
  - JSON fields for flexibility
  - Migration script needed

- ⏳ **Update Database Schema**
  - Migrate existing `RepairJob` data
  - Support multiple job types
  - Backward compatibility layer

### Phase 3: MCP Server Integration (Future)

- ⏳ **MCP Server Implementation**
  - Add `mcp` package dependency
  - Implement MCP server (`app/mcp/server.py`)
  - Expose agents as MCP tools/resources
  - Support stdio and HTTP transports

- ⏳ **MCP Client for Agents**
  - Agent-to-agent communication
  - MCP client implementation
  - Inter-agent tool calling

### Phase 4: Advanced Features (Future)

- ⏳ **Agent Orchestration**
  - Multi-agent workflows
  - Agent hierarchies
  - Coordinated execution

- ⏳ **Platform Abstraction**
  - Extract GitHub-specific code
  - Support GitLab, Bitbucket
  - Platform-agnostic agents

## Architecture Changes Summary

### File Structure

```
agent/
├── base.py              # NEW: BaseAgent interface
├── registry.py          # NEW: AgentRegistry
├── state.py             # UPDATED: Generic AgentState
├── repair/              # NEW: Repair agent module
│   ├── __init__.py
│   ├── agent.py         # NEW: RepairAgent class
│   ├── graph.py         # MOVED: From agent/graph.py
│   ├── state.py         # MOVED: RepairAgentState
│   ├── utils.py         # NEW: Langfuse helper
│   └── nodes/           # MOVED: From agent/nodes/
│       ├── diagnose.py
│       ├── classify.py
│       ├── locate.py
│       ├── fix.py
│       └── github_pr.py
├── nodes/               # OLD: Kept for reference (can be removed)
└── graph.py             # OLD: Deprecated (can be removed)

app/
├── api/
│   ├── agents.py        # NEW: Agent discovery endpoints
│   ├── worker.py        # UPDATED: Uses registry
│   └── router.py        # UPDATED: Includes agents router
├── core/
│   └── agents.py        # NEW: Agent registration
└── main.py              # UPDATED: Calls register_agents()
```

### Breaking Changes

**None** - The implementation maintains backward compatibility:
- Worker defaults to "repair" agent if `agent_name` not provided
- Repair agent maintains same state structure
- Existing webhook payloads work unchanged

### New Features

1. **Agent Discovery**: `/api/v1/agents` endpoints for listing and querying agents
2. **Agent Registry**: Centralized agent management
3. **MCP Ready**: Agents expose MCP tools/resources (ready for MCP server integration)
4. **Extensible**: Easy to add new agents by implementing `BaseAgent`

## Testing Checklist

- [ ] Verify repair agent still works end-to-end
- [ ] Test agent discovery endpoints
- [ ] Verify agent registration on startup
- [ ] Check backward compatibility (webhook → worker → repair agent)
- [ ] Test with missing agent_name (should default to "repair")

## Next Steps

1. **Test the Implementation**
   - Run the application
   - Test repair agent workflow
   - Test agent discovery endpoints

2. **Optional: Generic Models** (Phase 2)
   - Create `AgentJob` model
   - Migration script
   - Update API endpoints

3. **Future: MCP Server** (Phase 3)
   - Add MCP dependency
   - Implement MCP server
   - Test with Cursor/MCP client

4. **Future: Additional Agents**
   - Create new agent (e.g., test agent, review agent)
   - Implement `BaseAgent` interface
   - Register in `register_agents()`

## Notes

- The old `agent/graph.py` and `agent/nodes/` can be removed after verification
- MCP server implementation requires the `mcp` Python package
- Generic models (Phase 2) are optional and can be done incrementally
- The architecture is now ready for multi-agent support and MCP integration

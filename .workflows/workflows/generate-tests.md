---
description: Generate comprehensive test coverage for LangGraph agents, tools, and async pipelines
---

# Test Generation Workflow

This workflow generates test files for the project following the "Verification-Through-Execution" principle. Tests are not just documentation—they are executable proof that the system works.

## Philosophy

- **Test What Matters**: Focus on agent behavior, tool reliability, state transitions, and async processing
- **Real Execution**: Use actual LangGraph runtime and Cloud Tasks simulation, minimize mocks
- **Observable Results**: Every test should produce traceable output in Langfuse
- **Incremental Coverage**: Start with critical paths, expand to edge cases
- **Cost-Aware Testing**: Use recorded API responses to avoid burning through $300 GCP credit

## 1. Discovery Phase

// turbo-all
1. **Identify Test Gaps**: Scan the codebase for untested components
   ```bash
   find src/ -name "*.ts" ! -path "*/node_modules/*" ! -name "*.test.ts" | while read file; do
     test_file="${file%.ts}.test.ts"
     test_file="${test_file/src\//tests\/}"
     if [ ! -f "$test_file" ]; then
       echo "❌ Missing: $test_file (source: $file)"
     fi
   done
   ```

2. **Analyze Current Tests**: Review existing test patterns
   ```bash
   if [ -d "tests/" ]; then
     echo "📊 Current test files:"
     find tests/ -name "*.test.ts" -exec echo "  ✅ {}" \;
     echo ""
     echo "📈 Test coverage:"
     npm run test:coverage 2>/dev/null || echo "  ⚠️  Coverage not configured"
   else
     echo "⚠️  No tests directory found. Creating structure..."
     mkdir -p tests/{unit,integration,e2e,processors,utils,mocks}
   fi
   ```

3. **Prioritize**: Determine test priority based on:
   - **Critical Path**: Agents that handle user-facing workflows (`assistant.ts`, `prospecting.ts`)
   - **External Dependencies**: Tools that call APIs (`google-search.ts`, `vertex-ai.ts`)
   - **State Management**: Graph nodes that modify shared state
   - **Async Processing**: Cloud Tasks handlers (`lead-processor.ts`)
   - **Error Handling**: Code paths with try/catch blocks

## 2. Test Strategy Selection

For each component, choose the appropriate test type:

### A. Unit Tests (Tools & Utilities)
**When**: Pure functions, data transformers, validators  
**Speed**: <100ms per test  
**Example**: `src/tools/url-parser.ts` → `tests/unit/tools/url-parser.test.ts`

**Pattern**:
```typescript
import { describe, it, expect } from 'vitest';
import { parseCompanyUrl } from '@/tools/url-parser';

describe('URL Parser', () => {
  it('should extract domain from full URL', () => {
    const result = parseCompanyUrl('https://example.com/about');
    expect(result.domain).toBe('example.com');
  });

  it('should handle URLs without protocol', () => {
    const result = parseCompanyUrl('example.com');
    expect(result.domain).toBe('example.com');
  });

  it('should handle invalid URLs gracefully', () => {
    expect(() => parseCompanyUrl('not a url')).not.toThrow();
  });
});
```

### B. Integration Tests (Agents & Nodes)
**When**: LangGraph nodes, agent logic, state transitions  
**Speed**: <5s per test  
**Example**: `src/agents/prospecting.ts` → `tests/integration/agents/prospecting.test.ts`

**Pattern**:
```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { prospectingNode } from '@/agents/prospecting';
import { createMockState } from '@/tests/utils/mock-state';
import { mockVertexAI, mockGoogleSearch } from '@/tests/mocks/api-mocks';

describe('Prospecting Agent', () => {
  beforeAll(() => {
    mockVertexAI.start();
    mockGoogleSearch.start();
  });

  afterAll(() => {
    mockVertexAI.stop();
    mockGoogleSearch.stop();
  });

  it('should discover leads for a valid niche', async () => {
    const initialState = createMockState({
      niche: 'B2B AI Automation agencies',
      leads: []
    });

    const result = await prospectingNode(initialState);
    
    expect(result.leads.length).toBeGreaterThan(0);
    expect(result.leads[0]).toHaveProperty('company_name');
    expect(result.leads[0]).toHaveProperty('website');
  });

  it('should handle search failures gracefully', async () => {
    mockGoogleSearch.mockFailure();
    
    const initialState = createMockState({ niche: 'Test Niche' });
    const result = await prospectingNode(initialState);
    
    expect(result.leads).toEqual([]);
    expect(result.error).toBeDefined();
  });
});
```

### C. Async Pipeline Tests (Cloud Tasks Simulation)
**When**: Testing the Processing Brain (Visionary, Closer, Lead Processor)  
**Speed**: <10s per test  
**Example**: `src/processors/lead-processor.ts` → `tests/processors/lead-processor.test.ts`

**Pattern**:
```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { processSingleLead } from '@/processors/lead-processor';
import { mockPuppeteer, mockVertexAI } from '@/tests/mocks/api-mocks';
import { createMockLead } from '@/tests/utils/mock-data';

describe('Lead Processor (Async Pipeline)', () => {
  beforeEach(() => {
    mockPuppeteer.reset();
    mockVertexAI.reset();
  });

  it('should process lead with screenshot and draft', async () => {
    const mockLead = createMockLead({
      url: 'https://example.com',
      company_name: 'Example Corp'
    });

    const result = await processSingleLead(mockLead);
    
    expect(result.screenshot_url).toBeDefined();
    expect(result.visual_vibe_score).toBeGreaterThan(0);
    expect(result.email_draft).toContain('Example Corp');
  });

  it('should handle screenshot capture failure gracefully', async () => {
    mockPuppeteer.mockFailure('timeout');
    
    const mockLead = createMockLead({ url: 'https://slow-site.test' });
    const result = await processSingleLead(mockLead);
    
    // Should not throw, should log error and mark lead as failed
    expect(result.status).toBe('failed');
    expect(result.error).toContain('screenshot');
    expect(result.screenshot_url).toBeNull();
  });

  it('should retry on transient Vertex AI errors', async () => {
    mockVertexAI.mockTransientFailure(2); // Fail twice, then succeed
    
    const mockLead = createMockLead({ url: 'https://example.com' });
    const result = await processSingleLead(mockLead);
    
    expect(result.status).toBe('completed');
    expect(mockVertexAI.callCount).toBe(3); // 2 failures + 1 success
  });

  it('should respect rate limits via Cloud Tasks throttling', async () => {
    const leads = Array.from({ length: 10 }, (_, i) => 
      createMockLead({ company_name: `Company ${i}` })
    );

    const startTime = Date.now();
    await Promise.all(leads.map(processSingleLead));
    const duration = Date.now() - startTime;

    // Should take at least 9 seconds (10 leads at 1/sec throttle)
    expect(duration).toBeGreaterThan(9000);
  });
});
```

### D. End-to-End Tests (Full Graph Execution)
**When**: Complete user workflows, multi-agent orchestration  
**Speed**: <60s per test  
**Example**: `tests/e2e/hunt-workflow.test.ts`

**Pattern**:
```typescript
import { describe, it, expect } from 'vitest';
import { graph } from '@/assistant';
import { mockAllExternalAPIs } from '@/tests/mocks/api-mocks';

describe.skip('Hunt Workflow E2E', () => {
  // Skip by default, run only in CI or with --run-e2e flag
  
  it('should complete full hunt from niche to outreach', async () => {
    mockAllExternalAPIs();
    
    const result = await graph.invoke({
      messages: [{ role: 'user', content: 'Hunt for B2B AI agencies' }],
      niche: null,
      leads: [],
      approvals: {}
    });

    // Verify state transitions
    expect(result.niche).toBeDefined();
    expect(result.leads.length).toBeGreaterThan(0);
    expect(result.leads[0].email_draft).toBeDefined();
  }, { timeout: 60000 });
});
```

## 3. Test Data Strategy

### Environment-Based Testing

Create `.env.test` with mock credentials:
```bash
# .env.test - Safe for CI/CD, no real API calls
GOOGLE_CLOUD_PROJECT=test-project
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=test-anon-key
LANGFUSE_PUBLIC_KEY=test-public-key
LANGFUSE_SECRET_KEY=test-secret-key
```

### API Call Mocking Strategy

**For expensive/rate-limited APIs** (Vertex AI, Google Search, Puppeteer):

1. **First Run**: Record real API responses using `nock` or `msw`
2. **Subsequent Runs**: Replay recorded responses
3. **Update Recordings**: Monthly or when API contracts change

**Implementation** (`tests/mocks/api-mocks.ts`):
```typescript
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import fs from 'fs';
import path from 'path';

const RECORDINGS_DIR = path.join(__dirname, '../fixtures/recordings');

export const mockVertexAI = setupServer(
  http.post('https://*/v1/projects/*/locations/*/publishers/*/models/*:generateContent', async ({ request }) => {
    const body = await request.json();
    const recordingPath = path.join(RECORDINGS_DIR, 'vertex-ai', `${hashRequest(body)}.json`);
    
    // Use recording if exists, otherwise make real call and save
    if (fs.existsSync(recordingPath)) {
      return HttpResponse.json(JSON.parse(fs.readFileSync(recordingPath, 'utf-8')));
    }
    
    // In test mode, return mock data instead of real call
    return HttpResponse.json({
      predictions: [{ content: 'Mock response' }]
    });
  })
);

export const mockGoogleSearch = setupServer(
  http.get('https://www.googleapis.com/customsearch/v1', () => {
    return HttpResponse.json({
      items: [
        { title: 'Test Company', link: 'https://test.com' }
      ]
    });
  })
);

export const mockPuppeteer = {
  mockFailure: (reason: string) => {
    // Inject failure into Puppeteer mock
  },
  reset: () => {
    // Reset to normal behavior
  }
};
```

### Test Fixtures

Create reusable test data (`tests/utils/mock-data.ts`):
```typescript
import { Lead, Niche, GraphState } from '@/types';

export const createMockLead = (overrides?: Partial<Lead>): Lead => ({
  id: 'test-lead-123',
  company_name: 'Test Company',
  url: 'https://test.com',
  niche_id: 'test-niche-123',
  screenshot_url: null,
  visual_vibe_score: null,
  email_draft: null,
  created_at: new Date().toISOString(),
  ...overrides
});

export const createMockState = (overrides?: Partial<GraphState>): GraphState => ({
  messages: [],
  niche: null,
  leads: [],
  approvals: {},
  ...overrides
});
```

## 4. Test Execution Strategy

### Execution Tiers

Tests are categorized by speed and cost:

| Tier | Types | When to Run | Max Duration | API Calls |
|------|-------|-------------|--------------|-----------|
| **Fast** | Unit | Every commit | 30s | None (mocked) |
| **Medium** | Integration | Every PR | 5min | Mocked/Recorded |
| **Slow** | E2E, Processors | Merge to main | 15min | Mocked/Recorded |
| **Smoke** | E2E (real APIs) | Daily cron | 30min | Real (limited) |

### Vitest Configuration

Update `vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['tests/**/*.test.ts'],
    exclude: ['tests/e2e/**/*.test.ts'], // Skip E2E by default
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json'],
      exclude: ['tests/**', 'node_modules/**']
    },
    setupFiles: ['./tests/setup.ts'],
    testTimeout: 10000, // 10s default
    hookTimeout: 30000  // 30s for beforeAll/afterAll
  }
});
```

### NPM Scripts

Add to `package.json`:
```json
{
  "scripts": {
    "test": "vitest",
    "test:unit": "vitest run tests/unit",
    "test:integration": "vitest run tests/integration",
    "test:e2e": "vitest run tests/e2e --no-coverage",
    "test:coverage": "vitest run --coverage",
    "test:watch": "vitest watch",
    "test:ci": "vitest run --coverage --reporter=verbose"
  }
}
```

## 5. CI/CD Configuration

### GitHub Actions Workflow

Create `.github/workflows/test.yml`:
```yaml
name: Test Suite

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install Chrome Dependencies (for Puppeteer)
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            libnss3 libatk-bridge2.0-0 libdrm2 \
            libxkbcommon0 libgbm1 libxshmfence1
      
      - name: Install Dependencies
        run: npm ci
      
      - name: Run Unit Tests
        run: npm run test:unit
        env:
          NODE_ENV: test
      
      - name: Run Integration Tests
        run: npm run test:integration
        env:
          NODE_ENV: test
      
      - name: Run E2E Tests (main branch only)
        if: github.ref == 'refs/heads/main'
        run: npm run test:e2e
        env:
          NODE_ENV: test
      
      - name: Generate Coverage Report
        run: npm run test:coverage
      
      - name: Upload Coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
          flags: unittests
          name: codecov-umbrella
```

### Pre-Commit Hook

Create `.husky/pre-commit`:
```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Run fast tests only (unit tests)
npm run test:unit -- --run --reporter=dot

# Run type check
npm run type-check
```

## 6. Test Generation Process

For each identified gap:

1. **Read Source File**: Understand the component's purpose, inputs, and outputs
2. **Identify Test Cases**:
   - **Happy Path**: Normal execution with valid inputs
   - **Edge Cases**: Boundary conditions (empty arrays, null values, extreme inputs)
   - **Error Cases**: Invalid inputs, API failures, timeout scenarios
   - **Retry Logic**: Transient failures, exponential backoff
3. **Draft Test File**: Create the test file with appropriate structure
4. **Run Test**: Execute the test to verify it works
   ```bash
   npm test -- tests/path/to/test.test.ts
   ```
5. **Fix Failures**: If the test fails, determine if it's:
   - **Test Issue**: Fix the test logic
   - **Code Issue**: Fix the source code (and document the bug found!)
   - **Mock Issue**: Update mock data or API recordings
6. **Document Coverage**: Update `tests/README.md` with new test coverage

## 7. Test Utilities Setup

Create essential test utilities:

### `tests/setup.ts` (Global Setup)
```typescript
import { beforeAll, afterAll, afterEach } from 'vitest';
import { mockVertexAI, mockGoogleSearch } from './mocks/api-mocks';

beforeAll(() => {
  // Start all API mocks
  mockVertexAI.listen({ onUnhandledRequest: 'warn' });
  mockGoogleSearch.listen({ onUnhandledRequest: 'warn' });
});

afterEach(() => {
  // Reset mocks between tests
  mockVertexAI.resetHandlers();
  mockGoogleSearch.resetHandlers();
});

afterAll(() => {
  // Clean up
  mockVertexAI.close();
  mockGoogleSearch.close();
});
```

### `tests/utils/mock-state.ts` (State Factory)
```typescript
import { GraphState } from '@/types/graph-state';

export const createMockState = (overrides?: Partial<GraphState>): GraphState => ({
  messages: [],
  niche: null,
  leads: [],
  approvals: {},
  currentNode: null,
  error: null,
  ...overrides
});
```

### `tests/mocks/supabase-mock.ts` (In-Memory Supabase)
```typescript
import { createClient } from '@supabase/supabase-js';

export const createMockSupabaseClient = () => {
  const mockData = {
    niches: [],
    leads: []
  };

  return {
    from: (table: string) => ({
      select: () => Promise.resolve({ data: mockData[table], error: null }),
      insert: (data: any) => {
        mockData[table].push(data);
        return Promise.resolve({ data, error: null });
      },
      update: (data: any) => Promise.resolve({ data, error: null }),
      delete: () => Promise.resolve({ data: null, error: null })
    })
  };
};
```

## 8. Coverage Targets

| Component Type | Target Coverage | Priority |
|----------------|-----------------|----------|
| **Critical Agents** (assistant, prospecting) | >90% | 🔴 High |
| **Tools** (API clients, parsers) | >85% | 🟡 Medium |
| **Processors** (lead-processor) | >80% | 🔴 High |
| **Utilities** (helpers, validators) | >75% | 🟢 Low |
| **Types** (interfaces, schemas) | N/A | - |

## 9. Test Maintenance

- **After Every Feature**: Add tests for new agents/tools
- **After Every Bug Fix**: Add regression test to prevent recurrence
- **Weekly**: Review test execution times, optimize slow tests
- **Monthly Audit**: 
  - Review test coverage and identify gaps
  - Update API recordings
  - Remove obsolete tests
  - Update test fixtures with real-world examples

## Output Artifacts

1. **Test Files**: `tests/{unit,integration,e2e,processors}/[component].test.ts`
2. **Test Utilities**: `tests/utils/`, `tests/mocks/`
3. **Coverage Report**: `coverage/index.html`
4. **Test Documentation**: `tests/README.md` with coverage matrix
5. **CI Integration**: `.github/workflows/test.yml`

## Example Test Coverage Matrix

Create or update `tests/README.md`:

```markdown
# Test Coverage

Last Updated: 2026-01-11

## Coverage by Component

| Component | Type | Coverage | Tests | Status |
|-----------|------|----------|-------|--------|
| `assistant.ts` | Integration | 85% | 12 | ✅ |
| `prospecting.ts` | Integration | 90% | 15 | ✅ |
| `lead-processor.ts` | Processor | 80% | 10 | ✅ |
| `vertex-ai.ts` | Unit | 95% | 8 | ✅ |
| `google-search.ts` | Unit | 100% | 6 | ✅ |
| `cloud-tasks.ts` | Integration | 75% | 5 | ⚠️ Needs improvement |
| `visionary.ts` | Integration | 60% | 4 | ⚠️ Needs improvement |
| `closer.ts` | Integration | 0% | 0 | ❌ Missing |

## Test Execution Times

- **Unit Tests**: 2.3s (45 tests)
- **Integration Tests**: 18.7s (32 tests)
- **E2E Tests**: 47.2s (3 tests)
- **Total**: 68.2s (80 tests)

## Recent Failures

None ✅
```

## When to Run This Workflow

- **Before Production Deploy**: Ensure all critical paths are tested
- **After Major Refactor**: Verify nothing broke
- **When Adding New Agent**: Generate tests alongside implementation
- **Monthly Maintenance**: Expand coverage incrementally
- **After Bug Discovery**: Add regression tests
- **Before Architectural Changes**: Establish baseline behavior

## Success Criteria

- ✅ All critical agents have integration tests (>90% coverage)
- ✅ All tools have unit tests (>85% coverage)
- ✅ All async processors have pipeline tests (>80% coverage)
- ✅ At least one E2E test per user workflow
- ✅ Tests run in CI/CD pipeline on every PR
- ✅ Coverage report generated and reviewed
- ✅ No failing tests in main branch
- ✅ Test execution time <2min for fast tests
- ✅ API mocks prevent accidental quota consumption

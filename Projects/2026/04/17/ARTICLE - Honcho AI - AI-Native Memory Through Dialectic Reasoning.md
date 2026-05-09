---
title: "Honcho AI - AI-Native Memory Through Dialectic Reasoning"
aliases:
  - Honcho
  - Honcho AI
  - Plastic Labs Honcho
  - Honcho Memory
  - Peer Paradigm
tags:
  - article
  - ai
  - memory
  - agents
  - plastic-labs
  - honcho
  - dialectic
  - reasoning
  - user-modeling
  - peer-paradigm
status: active
type: article
created: 2026-04-17
repo: /home/manuel/code/wesen/2026-04-16--hermes-agent-setup/honcho
---

# Honcho AI - AI-Native Memory Through Dialectic Reasoning

Honcho is an AI-native memory library built by Plastic Labs that enables stateful, long-term memory for AI agents. It was built to solve a fundamental problem: traditional memory systems only store facts, but users and agents are more than facts. Delivering the context that actually matters requires reasoning.

This article explores Honcho's architecture, the Peer Paradigm, the Dialectic API, and how it differs from traditional RAG systems. The reference implementation is the plastic-labs/honcho repository on GitHub.

## The Memory Problem

Traditional RAG (Retrieval-Augmented Generation) systems have a fundamental limitation: they retrieve what was explicitly said, but miss what matters most — the insights only accessible through rigorous thinking about your data.

Consider a conversation:

```
User: "I'm trying to reduce my carbon footprint. I've been taking the bus to work instead of driving."
Assistant: "That's great! What motivated this change?"
User: "My daughter keeps asking me why the ice caps are melting."
Assistant: "That's a powerful motivator. Children often inspire environmental awareness in parents."
```

A traditional RAG system would store:
- "User takes bus instead of driving"
- "User has a daughter"
- "User is environmentally conscious"

But it would miss the deeper insights:
- **Causality**: The daughter is the catalyst, not abstract environmental concern
- **Values**: Family relationships drive decisions more than ideology
- **Prediction**: Future eco-friendly decisions may similarly be relationship-driven

> [!summary]
> - **Peer Paradigm**: Both users AND agents are first-class "Peers" with persistent state
> - **Dialectic API**: Multi-level reasoning using formal logic to extract latent insights
> - **Continual Learning**: Understands that entities change over time
> - **Pareto Frontier**: Balances recall, reasoning depth, storage efficiency, and accuracy
> - **Multi-Provider**: Gemini for quick reasoning, Claude for deep analysis

## The Peer Paradigm

The most distinctive aspect of Honcho is its entity model. In traditional systems, you have "users" and "assistants" — asymmetric relationships where only users get memory.

Honcho treats both as **Peers**:

```mermaid
flowchart LR
    U[User<br/>Peer] <--> A[Agent<br/>Peer]
    
    U --> UP[Persistent State]
    A --> AP[Persistent State]
    
    UP --> UP1[Personality]
    UP --> UP2[Preferences]
    UP --> UP3[Behavioral Patterns]
    UP --> UP4[Evolving Understanding]
    
    AP --> AP1[Behavior Model]
    AP --> AP2[Response Patterns]
    AP --> AP3[Capability Growth]
    AP --> AP4[Self-Knowledge]
```

This symmetry enables:

1. **Agents understand users**: Traditional personalization
2. **Users understand agents**: Users can ask "Why did you recommend that?"
3. **Multi-participant sessions**: Multiple humans and agents can interact
4. **Configurable observation**: Peers can choose what to reveal to other Peers

### Data Model

```
┌─────────────────────────────────────────────────────────────┐
│                   Honcho Data Model                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Workspaces                                                  │
│  └── Peers                                                   │
│      └── Sessions (many-to-many)                             │
│          └── Messages                                        │
│      └── Collections                                         │
│          └── Documents (vector-embedded)                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

| Entity | Description |
|--------|-------------|
| **Workspace** | Top-level isolation, multi-tenant capabilities |
| **Peer** | Users or agents with persistent, evolving state |
| **Session** | Set of interactions between peers |
| **Message** | Atomic communication unit |
| **Collection** | Named group of vector-embedded documents |
| **Document** | Vector data for RAG applications |

## The Dialectic API

The Dialectic API is Honcho's flagship feature. It enables multi-level reasoning by applying formal logic to derive insights from raw conversation data.

### Why "Dialectic"?

Dialectics is a method of reasoning that seeks truth through the interaction of opposing ideas. Honcho applies this principle to memory:

1. **Thesis**: What was said
2. **Antithesis**: Contradictions, implications, context
3. **Synthesis**: Derived insights that go beyond what was explicitly stated

### Reasoning Levels

Honcho supports five reasoning levels, each with different complexity and cost:

| Level | Use Case | Default Model | Latency | Cost |
|-------|----------|--------------|----------|------|
| **minimal** | Quick facts | Gemini 2.0 Flash | ~100ms | Low |
| **low** | Simple insights | Gemini 2.0 Flash | ~200ms | Low |
| **medium** | Complex reasoning | Claude Sonnet 4 | ~1s | Medium |
| **high** | Deep analysis | Claude Sonnet 4 | ~3s | High |
| **max** | Comprehensive | Claude Opus 4 | ~10s | Highest |

The levels are composable — you can use minimal for real-time suggestions and max for weekly user reports.

### API Usage

```python
from honcho import Honcho

honcho = Honcho(workspace_id="my-app")
alice = honcho.peer("alice")

# Ask a reasoning question about the user
response = alice.chat(
    "What learning styles does the user respond to best?",
    level="medium"  # Use medium reasoning
)
# Returns: "The user responds best to concrete examples and 
# step-by-step explanations. They ask clarifying questions when
# concepts are abstract..."

# Get a quick representation for low-latency needs
representation = alice.representation(session_id="recent-session")
# Returns a structured document with key insights
```

### The Reasoning Pipeline

```mermaid
flowchart TD
    A[Messages Created] --> B[Derivation Tasks Enqueued]
    
    B --> C[Session Queue]
    B --> D[Peer Queue]
    
    C --> E[Session Summarizer]
    D --> F[Peer Reasoner]
    
    E --> G[Session Summary]
    F --> H[Peer Representation]
    
    G --> I[Stored in Database]
    H --> I
    
    I --> J[Context API]
    I --> K[Dialectic API]
    I --> L[Search API]
```

## Storage Architecture

### PostgreSQL with pgvector

Honcho uses PostgreSQL for relational data and pgvector for vector similarity search:

```python
from sqlalchemy import Column, String, ForeignKey
from pgvector.sqlalchemy import Vector

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True)
    content = Column(String)
    embedding = Column(Vector(1536))  # OpenAI ada-002 dimensions
    token_count = Column(Integer, default=0)
    peer_name = Column(String, index=True)
    workspace_name = Column(String, index=True)
```

### Vector Store Backends

Honcho supports multiple vector backends:

| Backend | Use Case | Deployment |
|---------|----------|------------|
| **pgvector** | Default, self-hosted | Local/Cloud PostgreSQL |
| **Turbopuffer** | Cloud-native | Managed service |
| **LanceDB** | Local/edge | Embedded database |

```toml
# config.toml
[vector_store]
TYPE = "pgvector"  # or turborpuffer, lancedb

[db]
CONNECTION_URI = "postgresql+psycopg://user:pass@host:5432/honcho"
```

## The Deriver System

The **deriver** is a background worker that processes reasoning tasks asynchronously:

```bash
# Start the deriver worker
uv run python -m src.deriver

# Scale to multiple workers for better throughput
uv run python -m src.deriver &
uv run python -m src.deriver &
```

### Task Types

| Task | Purpose | Frequency |
|------|---------|-----------|
| **representation** | Update peer representations | On every message |
| **summary** | Create session summaries | On session close/idle |
| **peer_card** | Build comprehensive peer profiles | Daily/weekly |
| **dream** | Predictive modeling | On-demand |

### Queue Processing

Tasks are processed in order with session-based queueing:

```python
# src/deriver/process.py (simplified)
async def process_task(task: DerivationTask):
    if task.type == TaskType.REPRESENTATION:
        # Fetch recent messages for peer
        messages = await get_peer_messages(task.peer_id, limit=50)
        
        # Run reasoning
        reasoning = await dialectic.analyze(
            messages,
            level=determine_level(task)
        )
        
        # Store result
        await save_representation(task.peer_id, reasoning)
```

## Integration with Hermes Agent

Honcho and Hermes Agent are complementary systems:

```mermaid
flowchart LR
    subgraph Hermes[Hermes Agent]
        H1[Tool Calling]
        H2[Skills System]
        H3[Gateway]
    end
    
    subgraph Honcho[Honcho Memory]
        N1[Peer Model]
        N2[Dialectic API]
        N3[Session DB]
    end
    
    H1 -->|Context| N3
    H2 -->|Procedures| N3
    H3 -->|Messages| N1
    
    N1 -->|User Insights| H1
    N2 -->|Deep Reasoning| H3
    N3 -->|Recall| H2
```

### Setup

```bash
# In Hermes Agent
hermes honcho setup

# Configure in ~/.hermes/config.yaml
honcho:
  enabled: true
  api_key: "your-honcho-api-key"
  workspace_id: "your-workspace"
```

### Benefits for Hermes

| Without Honcho | With Honcho |
|----------------|-------------|
| MEMORY.md/USER.md only | Rich peer model |
| Manual memory updates | Automatic reasoning |
| Surface-level recall | Deep insights |
| Static understanding | Evolving understanding |

## Benchmarking: The Pareto Frontier

Honcho has defined the **Pareto Frontier of Agent Memory** — balancing competing objectives:

| Dimension | Description | Honcho's Approach |
|-----------|-------------|-------------------|
| **Recall** | What was said | FTS5 + vector search |
| **Reasoning** | What was meant | Multi-level dialectic |
| **Storage** | Token efficiency | Bounded memory + summarization |
| **Accuracy** | Correct insights | Formal logic inference |

The key insight: testing recall on benchmark data that fits in frontier context windows is no longer meaningful. Beyond simple recall, Honcho enables frontier models to reason across more tokens than their context windows support.

## Comparison with Other Memory Systems

| Feature | Honcho | MemGPT | Zep | Mem0 |
|---------|--------|--------|-----|------|
| **Reasoning** | ✅ Multi-level dialectic | ❌ Retrieval only | ❌ Basic | ❌ Basic |
| **Peer Paradigm** | ✅ First-class | ❌ User/Assistant | ❌ User only | ❌ User only |
| **Continual Learning** | ✅ Automatic | ❌ Manual | ❌ Basic | ❌ Basic |
| **Open Source** | ✅ AGPL-3.0 | ❌ Proprietary | ❌ Proprietary | ❌ Proprietary |
| **Agent Integration** | ✅ Hermes, any | ⚠️ Limited | ⚠️ Limited | ⚠️ Limited |

## Technical Architecture

### FastAPI Server

```python
# src/main.py
from fastapi import FastAPI

app = FastAPI(
    title="Honcho API",
    summary="The Identity Layer for the Agentic World",
    version="3.0.6"
)

app.include_router(workspaces.router, prefix="/v3")
app.include_router(peers.router, prefix="/v3")
app.include_router(sessions.router, prefix="/v3")
app.include_router(messages.router, prefix="/v3")
app.include_router(conclusions.router, prefix="/v3")
```

### SDK Usage

**Python**:
```python
from honcho import Honcho

honcho = Honcho(workspace_id="my-app")
alice = honcho.peer("alice")
session = honcho.session("session-1")

session.add_messages([
    alice.message("Can you help with my homework?"),
])

# Get enriched context
context = session.context(summary=True, tokens=10_000)
openai_messages = context.to_openai(assistant=tutor)
```

**TypeScript**:
```typescript
import { Honcho } from "@honcho-ai/sdk";

const honcho = new Honcho({ workspaceId: "my-app" });
const alice = honcho.peer("alice");

await alice.sendMessage("Hello!");
const response = await alice.chat("What topics has the user discussed?");
```

## Deployment Options

### Self-Hosting

```bash
# Clone and setup
git clone https://github.com/plastic-labs/honcho.git
cd honcho
uv sync

# Database
cp docker-compose.yml.example docker-compose.yml
docker compose up -d database

# Configure
cp .env.template .env
# Add API keys

# Run migrations
uv run alembic upgrade head

# Start services
uv run fastapi dev src/main.py  # API server
uv run python -m src.deriver   # Background worker
```

### Managed Service

Sign up at **app.honcho.dev** for:
- $100 free credits
- Managed PostgreSQL + pgvector
- Automatic scaling
- Built-in monitoring

## Open Questions

1. **Reasoning cost**: Deep dialectic reasoning is expensive. What is the cost-quality tradeoff at scale?
2. **Privacy**: How does Honcho handle sensitive conversations in the reasoning pipeline?
3. **Consistency**: How does Honcho handle conflicting information across sessions?
4. **Evaluation**: How do you measure if reasoning is producing correct insights?

## Related Notes

- [[ARTICLE - Hermes Agent - Self-Improving AI Agent with Persistent Memory and Skills]]
- [[PROJ - Hermes Agent Setup]]

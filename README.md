# Hermes Hybrid Memory

Two-layer memory for [Hermes Agent](https://hermes-agent.nousresearch.com/):
**self-hosted Honcho** for user memory + **Holographic** for project/entity facts.

Bypasses Hermes' `MemoryManager` limitation of one external memory provider by registering Holographic tools directly through `PluginContext`.

---

## The Problem

Hermes' `MemoryManager` allows **only one external memory provider** at a time:
```python
self._providers = [builtin] + [ONE_EXTERNAL]
```

If you set `memory.provider = honcho`, you lose access to `fact_store` / `fact_feedback` from Holographic. If you keep Holographic, you lose Honcho L4 memory.

## The Solution

1. Deploy **self-hosted Honcho** (Postgres + pgvector + Redis).
2. Set `memory.provider = honcho` in Hermes.
3. Install a tiny **standalone plugin** that imports Holographic and registers its tools directly via `PluginContext.register_tool(..., override=True)`.

The plugin is declared as `kind: standalone`, so Hermes does **not** treat it as an exclusive memory provider and still loads it normally.

---

## Quick Start

### 1. Deploy Honcho

```bash
cd docker
cp .env.example .env
# edit .env: set OLLAMA_CLOUD_API_KEY and OLLAMA_LOCAL_API_KEY
docker compose up -d
```

Honcho API will be available at `http://localhost:8000`.

### 2. Configure Hermes

In `~/.hermes/config.yaml`:
```yaml
memory:
  provider: honcho

plugins:
  enabled:
    - memory-holographic-tools
```

In `~/.hermes/.env`:
```bash
HONCHO_BASE_URL=http://localhost:8000
HONCHO_API_KEY=your-honcho-api-key
```

### 3. Install the plugin

```bash
cp -r plugin/memory-holographic-tools ~/.hermes/plugins/
```

### 4. Add memory discipline to your SOUL.md

Copy `SOUL.example.md` into `~/.hermes/SOUL.md` (or merge with your existing identity).

---

## Memory Discipline

| Source | Use for | Tools |
|---|---|---|
| **Honcho** | User preferences, identity, habits, recurring corrections, session context | `honcho_profile`, `honcho_search`, `honcho_context`, `honcho_reasoning`, `honcho_conclude` |
| **Holographic** | Projects, infrastructure, codebases, external systems, named entities, relationships | `fact_store`, `fact_feedback` |

This separation prevents the model from confusing where to read/write facts.

---

## Repository Structure

```
.
├── docker/                         # Self-hosted Honcho stack
│   ├── docker-compose.yml
│   ├── config.toml
│   └── .env.example
├── plugin/                         # Holographic bypass plugin
│   └── memory-holographic-tools/
│       ├── plugin.yaml
│       └── __init__.py
├── SOUL.example.md                 # System-prompt memory rules
└── README.md
```

---

## License

MIT

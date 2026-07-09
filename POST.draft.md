# Draft: How we tricked Hermes Agent core into remembering both the user and the projects (self-hosted Honcho + Holographic)

**TL;DR:** Hermes allows only one external memory provider, but we wanted both Honcho L4 user memory and Holographic project facts. We solved it with a `kind: standalone` plugin that injects Holographic tools directly into the global registry via `PluginContext.register_tool(..., override=True)`. Fully local stack, zero cloud lock-in.

---

## The limitation

In Hermes Agent, `MemoryManager` keeps exactly one external memory provider:

```python
self._providers = [builtin] + [ONE_EXTERNAL]
```

So the choice looks binary:
- `memory.provider = honcho` → you get `honcho_search`, `honcho_profile`, etc., but lose `fact_store` / `fact_feedback`.
- `memory.provider = holographic` → you keep project facts, but miss Honcho's dialectic user memory.

We wanted both.

## The hack

Hermes plugins load through `PluginContext`. Normal memory providers call `ctx.register_memory_provider()`, which lands them under `MemoryManager` and triggers the one-provider rule.

But ordinary plugins can call `ctx.register_tool()` directly. That path bypasses `MemoryManager` entirely.

So we built a tiny wrapper plugin `memory-holographic-tools` that:
1. Imports `HolographicMemoryProvider` from the bundled `plugins.memory.holographic`.
2. Registers its `fact_store` and `fact_feedback` schemas as regular tools under the `memory` toolset.
3. Uses `kind: standalone` in `plugin.yaml` so Hermes does not auto-detect it as an exclusive memory provider.

Result: `memory.provider = honcho` and the `memory` toolset still contains `fact_store` / `fact_feedback`.

## The stack

| Layer | Role | Tools |
|---|---|---|
| **Honcho** (self-hosted) | User memory, identity, preferences, session context | `honcho_profile`, `honcho_search`, `honcho_context`, `honcho_reasoning`, `honcho_conclude` |
| **Holographic** (bypass plugin) | Project/entity graph, infrastructure facts, relationships | `fact_store`, `fact_feedback` |

Honcho runs locally in Docker:
- PostgreSQL 15 + pgvector
- Redis
- Honcho API on `localhost:8000`

LLM uses Ollama Cloud, embeddings run on the local Ollama instance (`nomic-embed-text:latest`, 768 dims).

## Why this matters

- **No vendor lock-in.** Everything lives on your own Proxmox / bare-metal box.
- **No paid cloud memory API.** Ollama Cloud is pay-per-token cheap; local embeddings are free.
- **Clean mental model for the LLM.** We added explicit rules to `SOUL.md`: Honcho = user facts, Holographic = project facts. The model no longer guesses where to write.

## Repository

`hermes-hybrid-memory` — ready to use:
- `docker/` — compose + config for local Honcho
- `plugin/` — drop-in wrapper plugin
- `SOUL.example.md` — copy-paste memory discipline rules

GitHub: `https://github.com/yegorgaidar/hermes-hybrid-memory` (placeholder — replace with real URL)

---

*If you're running Hermes Agent and hesitated between Honcho and Holographic — you don't have to choose anymore.*

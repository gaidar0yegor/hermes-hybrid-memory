# LinkedIn post draft

**How we taught Hermes Agent to remember both the user *and* the projects — without rewriting its core.**

Hermes Agent has a hard limit: `MemoryManager` allows only one external memory provider at a time. Choose Honcho for user memory, and you lose `fact_store` from Holographic. Choose Holographic, and you miss Honcho's L4 reasoning.

We didn't accept the binary choice.

What we did:
1. Deployed self-hosted Honcho on our Proxmox box (Postgres + pgvector + Redis).
2. Set `memory.provider = honcho` in Hermes.
3. Built a tiny `kind: standalone` plugin that imports Holographic and registers `fact_store` / `fact_feedback` directly via `PluginContext.register_tool(..., override=True)`.

Result: both memory stores work simultaneously. Honcho owns user identity, preferences, and session context. Holographic keeps the project/entity graph.

To keep the LLM sane, we added explicit rules to the agent's `SOUL.md`:
- User facts → Honcho (`honcho_conclude`, `honcho_profile`, `honcho_search`).
- Project/infrastructure facts → Holographic (`fact_store`, `fact_feedback`).

No cloud lock-in. No paid memory API. Fully local stack on PVE.

Repository is public: https://github.com/gaidar0yegor/hermes-hybrid-memory

Includes:
- Docker compose for local Honcho
- Drop-in Hermes plugin
- `SOUL.md` memory-discipline template
- Habr/X/VC post draft

If you're running Hermes and hesitated between Honcho and Holographic — you don't have to choose anymore.

---

#aiagents #hermesagent #honcho #holographic #opensource #proxmox #selfhosted #llm #memory #architecture

**IMAGE:** architecture diagram showing Hermes, Honcho, Holographic, PluginContext bridge, Docker stack.

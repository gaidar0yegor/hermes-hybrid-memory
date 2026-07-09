# X / Twitter thread draft

**Tweet 1:**
Hermes Agent only allows ONE external memory provider. We wanted both Honcho (user memory) and Holographic (project facts).

So we built a tiny `kind: standalone` plugin that bypasses MemoryManager and registers Holographic tools directly via PluginContext.

Now the `memory` toolset has:
- honcho_profile / honcho_search / honcho_conclude
- fact_store / fact_feedback

Repo: https://github.com/gaidar0yegor/hermes-hybrid-memory

#HermesAgent #Honcho #Holographic #LLM #OpenSource

**Tweet 2 (reply):**
The trick: plugin.yaml declares `kind: standalone`, so Hermes doesn't auto-detect the plugin as an exclusive memory provider. Then `ctx.register_tool(..., override=True)` forces Holographic tools into the registry.

Everything runs self-hosted on Proxmox. No cloud memory API fees.

[IMAGE: architecture diagram]

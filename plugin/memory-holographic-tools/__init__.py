"""Holographic tools wrapper — keeps fact_store/fact_feedback available
regardless of which MemoryProvider is active.

This plugin bypasses MemoryManager's one-external-provider limit by
registering the Holographic fact tools directly via PluginContext,
so Honcho can own L4 memory while Holographic continues serving
structured project/preference facts from its SQLite store.
"""

from __future__ import annotations

import logging
import json

logger = logging.getLogger(__name__)


def register(ctx) -> None:
    """Register Holographic fact tools directly into the global tool registry."""
    # Import inside register() so the top-level module never mentions
    # MemoryProvider / register_memory_provider. Otherwise Hermes
    # auto-detects this directory as an exclusive memory provider and
    # skips normal plugin loading.
    from plugins.memory.holographic import HolographicMemoryProvider, _load_plugin_config

    config = _load_plugin_config()
    provider = HolographicMemoryProvider(config=config)
    provider.initialize(session_id="holographic-tools-wrapper")

    schemas = provider.get_tool_schemas()

    def _make_handler(tool_name: str):
        def handler(args: dict, **kwargs) -> str:
            return provider.handle_tool_call(tool_name, args)
        return handler

    for schema in schemas:
        name = schema.get("name")
        if not name:
            continue
        # Inject into the built-in 'memory' toolset so the model sees
        # fact_store / fact_feedback alongside the active memory provider's
        # tools. override=True forces registration even if Honcho already
        # registered tools under the same toolset name.
        ctx.register_tool(
            name=name,
            toolset="memory",
            schema=schema,
            handler=_make_handler(name),
            description=schema.get("description", ""),
            override=True,
        )
        logger.debug("Registered Holographic tool via wrapper: %s", name)

    logger.info(
        "memory-holographic-tools wrapper registered %d tools from Holographic",
        len(schemas),
    )

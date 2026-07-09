# Habr / VC article draft

**Заголовок:** Как мы обманули ядро Hermes Agent и научили его помнить и пользователя, и проекты одновременно (Self-hosted Honcho + Holographic)

---

## Введение

Hermes Agent — мощный open-source AI-оркестратор от Nous Research. У него есть встроенная система долговременной памяти, но с ограничением: `MemoryManager` позволяет активировать только **один внешний memory-провайдер**.

Если выбрать `memory.provider = honcho`, получаем `honcho_profile`, `honcho_search`, `honcho_conclude` — отличные инструменты для user memory. Но при этом теряем `fact_store` и `fact_feedback` от Holographic, которые хранят факты о проектах, инфраструктуре и сущностях.

Мы не хотели терять ни одну из двух систем. И нашли способ сохранить обе.

---

## Проблема

```python
# agent/memory_manager.py
self._providers = [builtin] + [ONE_EXTERNAL]
```

Это значит, что второй external-провайдер не попадёт в `_providers`, и его инструменты исчезнут из агента. В конфиге `memory.provider` может быть только один.

---

## Решение

В Hermes есть два пути регистрации инструментов:

1. `ctx.register_memory_provider()` — используется memory-провайдерами и попадает под фильтр MemoryManager.
2. `ctx.register_tool()` — используется обычными плагинами и прокидывает инструменты напрямую в `tools.registry`, минуя MemoryManager.

Мы создали wrapper-плагин `memory-holographic-tools`, который:

- Импортирует `HolographicMemoryProvider` из встроенного `plugins.memory.holographic`.
- Явно объявляет `kind: standalone` в `plugin.yaml`, чтобы Hermes не распознал его как exclusive memory-провайдер.
- Через `register(ctx)` вызывает `ctx.register_tool(name=..., toolset="memory", schema=..., handler=..., override=True)` для `fact_store` и `fact_feedback`.

В итоге toolset `memory` содержит одновременно инструменты Honcho и Holographic.

---

## Стек

Развернуто на Proxmox VE:

| Сервис | Роль |
|---|---|
| PostgreSQL 15 + pgvector | База Honcho с векторным поиском |
| Redis | Кэш/очередь |
| Honcho API | REST API на `localhost:8000` |
| Local Ollama | Эмбеддинги `nomic-embed-text:latest` (768 dims) |
| Ollama Cloud | LLM (`qwen3-coder-next`, `deepseek-v4-flash`, `glm-5.1`) |

Honcho работает полностью локально. Платим только за токены в Ollama Cloud.

---

## Дисциплина памяти для LLM

Два хранилища — два назначения. Чтобы модель не путалась, мы вписали правила в `SOUL.md`:

- **Honcho** — факты о пользователе: предпочтения, привычки, идентичность, коррекции, контекст сессии.
- **Holographic** — факты о проектах, инфраструктуре, кодовых базах, внешних системах, сущностях и связях.

Пример теста:
- «I prefer dark mode» → `honcho_conclude` ✅
- «WTTJ dashboard lives at /opt/wttj-dashboard» → `fact_store(action=add)` ✅

---

## Репозиторий

https://github.com/gaidar0yegor/hermes-hybrid-memory

Внутри:
- `docker/` — готовый compose + config.toml для self-hosted Honcho.
- `plugin/memory-holographic-tools/` — drop-in плагин для Hermes.
- `SOUL.example.md` — шаблон разделения ролей памяти.
- `POST.draft.md` — черновики постов.

---

## Заключение

Это не форк ядра Hermes. Это архитектурный хак на уровне плагинов: мы использовали существующий `PluginContext` так, как он и предназначен для обычных инструментов, и сохранили обе системы памяти без переписывания `MemoryManager`.

Если вы используете Hermes Agent и выбирали между Honcho и Holographic — теперь выбирать не нужно.

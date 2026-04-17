# Gain Tech Bot — Developer Guide

## 1) Project purpose

Telegram bot for Gain Tech (aiogram 3) with:
- menu/navigation,
- qualification funnel (3 questions -> contact -> name),
- LLM replies (OpenRouter / Anthropic / Ollama / io.net),
- lightweight in-memory user state and facts.

Primary runtime entrypoint: `bot.py`.


## 2) Dependencies and libraries

Defined in `requirements.txt`:
- `aiogram==3.13.1` — Telegram bot framework.
- `httpx==0.27.2` — async HTTP client for LLM API calls.
- `python-dotenv==1.0.1` — loading `.env`.

Standard library used heavily:
- `asyncio`, `logging`, `re`, `os`, `datetime`, `collections.defaultdict`, `pathlib.Path`.


## 3) File map

- `bot.py` — Telegram handlers, dialog/funnel logic, prompt assembly, main polling.
- `llm.py` — provider clients and routing (`openrouter`, `anthropic`, `ollama`, `ionet`) + `polish_ru`.
- `memory.py` — in-memory store, dialog stage machine, facts extraction, stats.
- `config.py` — environment loading and all config constants.
- `knowledge_base.py` — `KB_TEXT`, injected into system prompt.
- `.env` — runtime secrets and selected model/provider.


## 4) Configuration (`config.py`)

Important env variables:

- Telegram:
  - `BOT_TOKEN`

- Provider selection:
  - `LLM_PROVIDER` = `openrouter` | `anthropic` | `ollama` | `ionet`
  - `LLM_MODEL` (used for OpenRouter)
  - `MAX_TOKENS`, `TEMPERATURE`

- OpenRouter:
  - `OPENROUTER_API_KEY`
  - `LLM_BASE_URL` (hardcoded `https://openrouter.ai/api/v1`)

- Anthropic:
  - `ANTHROPIC_API_KEY`
  - `ANTHROPIC_MODEL`
  - `LLM_FALLBACK_OLLAMA` (optional)

- Ollama:
  - `OLLAMA_URL`
  - `OLLAMA_MODEL`

- io.net:
  - `IONET_API_KEY`
  - `IONET_BASE_URL`
  - `IONET_MODEL`

- Russian polish:
  - `LLM_RU_POLISH` (`1`/`0`)

Notes:
- `config.py` calls `load_dotenv(override=True)`.
- There is a fallback reader `_read_env_value_from_file()` for `OPENROUTER_API_KEY` if env is empty.


## 5) `bot.py` — runtime flow and functions

### Core globals
- `bot = Bot(token=BOT_TOKEN)`
- `dp = Dispatcher()`
- `memory = MemoryManager()`
- Keyboards: `MAIN_MENU`, `CONTACT_KB`
- Main prompt: `SYSTEM_PROMPT_BASE` (includes `KB_TEXT`)

### Helper functions
- `get_user_key(message) -> str`
- `_normalize_for_check(s) -> str`
- `is_name_ok(name) -> bool`
  - validates user name (regex, anti-spam/obscene checks).
- `build_system_prompt(user_id) -> str`
  - adds hidden developer context (`stage`, `order_q`, `has_contact`, etc.).

### Handlers
- `cmd_start` (`/start`)
  - resets conversation (without dropping counters), sends welcome + main keyboard.

- `cmd_stats` (`/stats`)
  - prints messages/leads/facts from memory.

- `cmd_reset` (`/reset`)
  - clears conversation state, keeps global counters.

- `handle_about`
- `handle_portfolio`
- `handle_order`
- `handle_contact`

- `handle_contact_share` (`@dp.message(F.contact)`)
  - stores contact, switches to `await_name`.

- `handle_chat` (`@dp.message(F.text)`)
  - central text pipeline:
  1. command-like checks (`Отмена`, `хочу консультацию`)
  2. funnel state machine (`order_q1/q2/q3`, `await_contact`, `await_name`)
  3. generic chat:
     - typing action,
     - `history = memory.get_history(user_id)`,
     - `reply = await ask_llm(...)`,
     - `clean_reply = await polish_ru(clean_reply)`,
     - save via `memory.add_turn()` and `memory.extract_facts()`,
     - answer user.

- `main()`
  - starts aiogram polling.


## 6) Funnel state machine

State values (in `memory.py`):
- `general_chat`
- `order_q1`, `order_q2`, `order_q3`
- `await_contact`
- `await_name`

Happy path:
1. User clicks "Оформить заказ" or writes "хочу консультацию".
2. Bot asks 3 qualification questions.
3. Bot requests Telegram contact (`request_contact=True` button).
4. Bot asks for name + surname, validates with `is_name_ok`.
5. Lead is counted: `memory.add_lead(...)`.


## 7) `memory.py` — storage and methods

Class: `MemoryManager`

### Session/state
- `reset_session(user_id)`
- `reset_conversation(user_id)` (keeps `messages`, `paid`, `leads`)
- `get_stage`, `set_stage`
- `reset_order_flow`
- `save_order_answer`, `set_order_q`, `get_order_q`, `get_order_answers`
- `set_contact`, `has_contact`
- `inc_name_attempts`, `reset_name_attempts`
- `bump_offtopic`, `reset_offtopic`

### Quota and stats
- `has_quota(user_id)` -> always `True` (no user cap in current implementation)
- `get_stats(user_id)` -> includes `free_left: "∞"`

### Dialog memory/facts
- `get_history(user_id)` (full history; no trimming)
- `add_turn(user_id, user_text, bot_text, is_lead=False)`
- `extract_facts(...)` (rule-based niche/tariff/budget parsing)
- `get_facts(user_id)`


## 8) `llm.py` — provider functions and routing

### Provider clients
- `_ask_openrouter(messages)`
  - endpoint: `POST {LLM_BASE_URL}/chat/completions`
  - requires non-empty `OPENROUTER_API_KEY`.

- `_ask_anthropic(messages)`
  - endpoint: `POST https://api.anthropic.com/v1/messages`
  - transforms system + messages via `_split_system_and_messages`.
  - retries on `429`/`5xx`.

- `_ask_ollama(messages)`
  - endpoint: `POST {OLLAMA_URL}/api/chat`
  - retries on server/network errors.

- `_ask_ionet(messages)`
  - OpenAI-compatible: `POST {IONET_BASE_URL}/chat/completions`.

### Routing
- `ask_llm(system, history, user_message)`
  - builds unified message list
  - dispatches by `LLM_PROVIDER`.

### Post-processing
- `polish_ru(text)`
  - optional second pass (controlled by `LLM_RU_POLISH`)
  - preserves Gain Tech role, blocks meta "I am an editor/model" outputs.


## 9) Prompt and product content

Where to edit behavior:
- Main behavior/tone/rules:
  - `bot.py` -> `SYSTEM_PROMPT_BASE`

- Product/business knowledge:
  - `knowledge_base.py` -> `KB_TEXT`

Recommendation:
- Keep rules in `SYSTEM_PROMPT_BASE`.
- Keep factual business data in `KB_TEXT`.


## 10) Common troubleshooting

### A) `TelegramConflictError: terminated by other getUpdates request`
Cause: multiple bot processes running.
Fix: stop all duplicate Python processes and run one `py bot.py`.

### B) `TelegramUnauthorizedError` / `SESSION_REVOKED`
Cause: bot token was revoked/rotated in BotFather.
Fix: put fresh `BOT_TOKEN` into `.env`, restart bot.

### C) `LLM error ... 404 No endpoints found for <model>`
Cause: selected model ID is not available for your API key/account.
Fix: query provider models list and set available model in `.env`.

### D) `OPENROUTER_API_KEY пустой` or `Illegal header value b'Bearer '`
Cause: empty/invalid key loaded from env.
Fix: check `.env`, save file, restart process.


## 11) Current practical run commands

From project root:

```bash
py bot.py
```

Quick config sanity:

```bash
py -c "import config; print(config.LLM_PROVIDER, config.LLM_MODEL, len(config.OPENROUTER_API_KEY))"
```


## 12) Notes for next developer

- This project currently uses in-memory state only; bot restart clears dialog memory.
- For production, move session/history/facts to persistent storage (Redis/Postgres).
- Avoid editing secrets in docs or committed files.
- Keep only one active polling process per bot token.

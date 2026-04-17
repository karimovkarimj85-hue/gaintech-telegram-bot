# Gain Tech Bot — карта системы (modules / functions / взаимодействия)

Этот файл — краткая “карта” проекта: **что за что отвечает**, **какие функции ключевые**, и **как модули взаимодействуют**.

## 1) Архитектура в 15 секунд

- Пользователь пишет в Telegram → `aiogram` вызывает хендлеры в `bot.py`
- `bot.py` ведёт **воронку** (стадии в `memory.py`) и/или обычный чат
- Для обычного чата: `bot.py` формирует `system` (персона + правила + `KB_TEXT`) → зовёт `ask_llm()` из `llm.py`
- Ответ проходит пост-обработку (`polish_ru()` при включении) → сохраняется в `memory.py` → отправляется пользователю
- Для заявок/консультаций: собираются ответы → `notifications.py` шлёт уведомление в `NOTIFY_CHANNEL_ID`
- Для Mini App: `gaintech-portfolio/index.html` может отправить `web_app_data`, который принимает `bot.py`

## 2) Состав проекта (файлы и ответственность)

### `bot.py` — главный runtime, хендлеры Telegram, воронка, prompt
**Отвечает за:**
- создание `Bot`, `Dispatcher`, подключение админ-хендлеров
- клавиатуры (`MAIN_MENU`, `CONTACT_KB`, `BACK_KB`, `CANCEL_KB`)
- “персона/роль” и правила общения: `SYSTEM_PROMPT_BASE`
- state machine воронки (заказ / консультация)
- вызов LLM (`ask_llm`) и запись истории/фактов в память
- приём данных из Mini App (`F.web_app_data`)

**Ключевые функции/блоки:**
- `get_user_key(message) -> str`: единый ключ пользователя (строка `from_user.id`)
- `is_name_ok(name) -> bool`: валидация имени (regex + анти-спам/мат)
- `build_system_prompt(user_id) -> str`:
  - берёт `SYSTEM_PROMPT_BASE`
  - добавляет скрытый “developer context” (stage, answers, наличие контакта)
- `detect_order_intent(text) -> bool`: эвристика, понимает “хочу заказать/сколько стоит…”
- `extract_order_context(history_text) -> dict`: LLM-экстракция “что/бюджет/сроки” из истории

**Хендлеры (главные):**
- `/start` → `cmd_start()`: сброс диалога (не всех счётчиков) + главное меню
- `/reset` → `cmd_reset()`: сброс сессии диалога/воронки
- `F.text == "Оформить заказ"` → старт воронки заказов
- `F.contact` → получение контакта (кнопка request_contact)
- `F.text` → `handle_chat()`: центральная логика (навигация, воронка, затем LLM-чат)
- `F.web_app_data` → `handle_webapp()`: заявки из Telegram WebApp

---

### `config.py` — конфигурация и env
**Отвечает за:**
- загрузку `.env` через `python-dotenv` (`load_dotenv(override=True)`)
- чтение переменных окружения (`_env()`)
- fallback-чтение `OPENROUTER_API_KEY` напрямую из файла `.env` (если окружение пустое)
- экспорт констант: токены, модели, лимиты, provider

**Ключевые переменные:**
- `BOT_TOKEN`: токен Telegram
- `LLM_PROVIDER`: `openrouter | ollama | anthropic | ionet`
- `OPENROUTER_API_KEY`, `LLM_MODEL`
- `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `LLM_FALLBACK_OLLAMA`
- `IONET_API_KEY`, `IONET_BASE_URL`, `IONET_MODEL`
- `OLLAMA_URL`, `OLLAMA_MODEL`
- `NOTIFY_CHANNEL_ID`
- лимиты: `MAX_HISTORY`, `MAX_TOKENS`, `TEMPERATURE`

---

### `llm.py` — работа с LLM (4 провайдера) + “полировка русского”
**Отвечает за:**
- единый интерфейс `ask_llm(system, history, user_message) -> str`
- маршрутизацию по `LLM_PROVIDER`
- HTTP вызовы провайдеров (`httpx.AsyncClient`)
- `polish_ru(text) -> str` (опционально): второй проход для исправления русского

**Ключевые функции:**
- `ask_llm(...)`:
  - строит `messages = [system] + history + [user]`
  - вызывает один из: `_ask_openrouter`, `_ask_ollama`, `_ask_anthropic`, `_ask_ionet`
- `_ask_openrouter(messages)`:
  - `POST {LLM_BASE_URL}/chat/completions`
  - требует `OPENROUTER_API_KEY`
- `_ask_anthropic(messages)`:
  - `POST https://api.anthropic.com/v1/messages`
  - преобразует формат сообщений (Anthropic не принимает `role=system` в messages)
  - ретраи на `429` / `5xx`
- `_ask_ollama(messages)`:
  - `POST {OLLAMA_URL}/api/chat`
  - `stream=False`
  - ретраи на сетевые/5xx
- `_ask_ionet(messages)`:
  - OpenAI-compatible `POST {IONET_BASE_URL}/chat/completions`

**Пост-обработка:**
- `polish_ru()` включается env `LLM_RU_POLISH=1`
- содержит простые “предохранители” от мета-ответов (“я редактор…”) и “экзотических” алфавитов

---

### `memory.py` — состояние/память (in-memory)
**Отвечает за:**
- хранение истории диалога, стадии, ответов воронки, контакта, фактов
- сбор статистики (messages, leads)

**Ключевые методы:**
- `get_stage(user_id) / set_stage(user_id, stage)`
- `reset_order_flow(user_id)`: старт 3-вопросной воронки
- `save_order_answer(user_id, q, text)` и `get_order_answers(user_id)`
- `set_contact(user_id, contact)` и `has_contact(user_id)` / `get_contact(user_id)`
- `add_turn(user_id, user_text, bot_text, is_lead=False)`:
  - добавляет 2 сообщения в history (user + assistant)
  - увеличивает счётчик `messages`
- `extract_facts(user_id, user_text, bot_text)`:
  - rule-based извлечение (ниша, интерес к цене/тарифу, объём обращений)

**Важно про прод:**
- это **RAM-only**, после рестарта всё (стадии/история/факты) исчезает
- история сейчас не режется по длине → при долгой работе процесса RAM будет расти

---

### `knowledge_base.py` — контент компании (факты)
**Отвечает за:**
- `KB_TEXT`: единый текст с услугами, ценами, возражениями, процессом работы
- используется в `SYSTEM_PROMPT_BASE` внутри `bot.py`

---

### `notifications.py` — уведомления о лидах (заказ/консультация)
**Отвечает за:**
- `send_order_notification(bot, user_data)`
- `send_consultation_notification(bot, user_data)`
- форматирование сообщения + отправка в `NOTIFY_CHANNEL_ID`

**Входные данные (`user_data`):**
- `name`, `phone`, `username`, `user_id`
- для заказа: `answer_1/answer_2/answer_3`
- для консультации: `question`

---

### `admin.py` — админка (MVP)
**Отвечает за:**
- `register_admin_handlers(dp, memory)`:
  - `/admin` + inline callbacks
- проверка `ADMIN_IDS` из env

---

### `gaintech-portfolio/index.html` — Telegram Mini App (портфолио)
**Отвечает за:**
- статическая витрина портфолио (карточки, фильтры)
- кнопка “Оформить заказ” вызывает `Telegram.WebApp.sendData(...)`

**Важная связка:**
- данные, которые отправляет Mini App, должны совпадать с тем, что ждёт `bot.py` в `handle_webapp`

## 3) Потоки данных (flows)

### A) Обычный чат (LLM)
1. Telegram update → `handle_chat()` (когда не сработали ветки воронки/навигации)
2. `history = memory.get_history(user_id, max_pairs=MAX_HISTORY)`
3. `system = build_system_prompt(user_id)`
4. `reply = await ask_llm(system, history, user_text)`
5. `clean_reply = await polish_ru(...)` (если включено)
6. `memory.add_turn(...)` + `memory.extract_facts(...)`
7. `message.answer(clean_reply)`

### B) Заказ (воронка 3 вопроса → контакт → имя → уведомление)
1. “Оформить заказ” → `reset_order_flow()` → stage `order_q1`
2. `order_q1` → `order_q2` → `order_q3`
3. если контакта нет → stage `await_contact` (request_contact)
4. stage `await_name` (валидация `is_name_ok`)
5. `notifications.send_order_notification(...)`
6. `memory.reset_history(user_id)` (очищает историю/факты/воронку)

### C) Консультация (короткий путь)
1. текст “хочу консультацию” → stage `consult_q1`
2. после вопроса → контакт → имя → `send_consultation_notification`

### D) Mini App (WebApp)
1. Mini App вызывает `Telegram.WebApp.sendData(JSON.stringify(payload))`
2. Telegram присылает update `web_app_data`
3. `handle_webapp()` парсит JSON и шлёт уведомление

## 4) Зависимости (библиотеки) и где используются

- **aiogram 3** (`aiogram`, `Dispatcher`, фильтры `F`, types):
  - только в `bot.py` и `admin.py`
- **httpx**:
  - только в `llm.py` (вызовы внешних API)
- **python-dotenv**:
  - только в `config.py`

## 5) Конфигурация для деплоя (минимум)

В окружении должны быть заданы:
- `BOT_TOKEN`
- один из ключей провайдера:
  - OpenRouter: `OPENROUTER_API_KEY` (+ `LLM_MODEL` опционально)
  - Anthropic: `ANTHROPIC_API_KEY`
  - io.net: `IONET_API_KEY`
  - Ollama: нужен доступ к локальному `OLLAMA_URL` (на Render обычно не вариант)
- `NOTIFY_CHANNEL_ID` (если нужны уведомления в канал/группу)
- `ADMIN_IDS` (если нужна админка)

## 6) Где обычно “ломается” (типовые проблемы)

- **Polling на хостинге**:
  - конфликт “два процесса polling” → `terminated by other getUpdates request`
- **Рестарт процесса**:
  - сброс стадий/истории (память в RAM)
- **Mini App ↔ `handle_webapp` mismatch**:
  - payload не совпадает → заявки приходят пустыми/не теми полями
- **Пустой LLM ключ**:
  - `OPENROUTER_API_KEY пустой` и т.п.
- **Таймауты внешнего API**:
  - `httpx` timeout, 5xx/429 → временная деградация ответов


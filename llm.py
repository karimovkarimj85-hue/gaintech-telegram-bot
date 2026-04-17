import logging
import time
import asyncio
import httpx
from config import (
    LLM_PROVIDER,
    OPENROUTER_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    OLLAMA_URL,
    OLLAMA_MODEL,
    LLM_RU_POLISH,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    LLM_FALLBACK_OLLAMA,
    IONET_API_KEY,
    IONET_BASE_URL,
    IONET_MODEL,
)

logger = logging.getLogger(__name__)

HEADERS = {
    "Content-Type": "application/json",
    "HTTP-Referer": "https://gaintech.ru",
    "X-Title": "Gain Tech Bot",
}

OLLAMA_HEADERS = {"Content-Type": "application/json"}

IONET_HEADERS_BASE = {"Content-Type": "application/json"}

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_HEADERS_BASE = {
    "Content-Type": "application/json",
    "anthropic-version": "2023-06-01",
}


def _split_system_and_messages(messages: list) -> tuple[str | None, list]:
    """OpenAI-стиль: system + user/assistant → Anthropic: system + messages без system."""
    system_parts: list[str] = []
    convo: list = []
    for m in messages:
        role = m.get("role")
        content = (m.get("content") or "").strip()
        if role == "system":
            if content:
                system_parts.append(content)
        elif role in ("user", "assistant"):
            convo.append({"role": role, "content": content})
    system = "\n\n".join(system_parts) if system_parts else None
    return system, convo


async def _ask_anthropic(messages: list) -> str:
    """Claude через официальный Messages API (stream отключён)."""
    key = (ANTHROPIC_API_KEY or "").strip()
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY не задан в окружении")

    system, convo = _split_system_and_messages(messages)
    if not convo:
        raise RuntimeError("Anthropic: нет сообщений пользователя/ассистента")

    payload: dict = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": convo,
        "temperature": TEMPERATURE,
        "stream": False,
    }
    if system:
        payload["system"] = system

    headers = {**ANTHROPIC_HEADERS_BASE, "x-api-key": key}
    url = ANTHROPIC_MESSAGES_URL
    last_err: str | None = None

    for attempt in range(1, 4):
        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(url, headers=headers, json=payload)

            latency_ms = int((time.perf_counter() - t0) * 1000)

            if response.status_code == 429 or response.status_code >= 500:
                last_err = f"http {response.status_code}: {(response.text or '')[:200]}"
                logger.warning(
                    f"[LLM] provider=anthropic model={ANTHROPIC_MODEL} "
                    f"attempt={attempt} latency_ms={latency_ms} err={last_err}"
                )
                await asyncio.sleep(0.6 * attempt)
                continue

            response.raise_for_status()
            data = response.json()
            blocks = data.get("content") or []
            parts: list[str] = []
            for b in blocks:
                if isinstance(b, dict) and b.get("type") == "text":
                    parts.append(b.get("text") or "")
            text = "\n".join(parts).strip()
            logger.info(
                f"[LLM] provider=anthropic model={ANTHROPIC_MODEL} attempt={attempt} latency_ms={latency_ms}"
            )
            return text
        except httpx.HTTPStatusError as e:
            latency_ms = int((time.perf_counter() - t0) * 1000)
            last_err = f"{e.response.status_code}: {(e.response.text or '')[:200]}"
            logger.warning(
                f"[LLM] provider=anthropic model={ANTHROPIC_MODEL} attempt={attempt} latency_ms={latency_ms} err={last_err}"
            )
            await asyncio.sleep(0.6 * attempt)
        except Exception as e:
            latency_ms = int((time.perf_counter() - t0) * 1000)
            last_err = f"{type(e).__name__}: {e}"
            logger.warning(
                f"[LLM] provider=anthropic model={ANTHROPIC_MODEL} attempt={attempt} latency_ms={latency_ms} err={last_err}"
            )
            await asyncio.sleep(0.6 * attempt)

    raise RuntimeError(f"Anthropic call failed: {last_err}")


async def _ask_openrouter(messages: list) -> str:
    key = (OPENROUTER_API_KEY or "").strip()
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY пустой (проверьте .env и перезапустите бота).")

    headers = {**HEADERS, "Authorization": f"Bearer {key}"}
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{LLM_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    text = data["choices"][0]["message"]["content"].strip()

    usage = data.get("usage", {})
    if usage:
        logger.info(
            f"[LLM] provider=openrouter model={LLM_MODEL} "
            f"in={usage.get('prompt_tokens',0)} "
            f"out={usage.get('completion_tokens',0)} tokens"
        )

    return text


async def _ask_ionet(messages: list) -> str:
    """
    IO Intelligence API (io.net) — OpenAI-compatible endpoint.
    Docs: https://io.net/docs/reference/ai-models/get-started-with-io-intelligence-api.md
    """
    key = (IONET_API_KEY or "").strip()
    if not key:
        raise RuntimeError("IONET_API_KEY не задан в окружении")

    base = (IONET_BASE_URL or "").strip().rstrip("/")
    if not base:
        raise RuntimeError("IONET_BASE_URL пустой")

    payload = {
        "model": IONET_MODEL,
        "messages": messages,
        "temperature": TEMPERATURE,
        "stream": False,
        # У io.net в примере фигурирует max_completion_tokens; чтобы не ломать совместимость
        # с их схемой, передаём оба — сервер обычно игнорирует лишнее.
        "max_tokens": MAX_TOKENS,
        "max_completion_tokens": MAX_TOKENS,
    }
    headers = {**IONET_HEADERS_BASE, "Authorization": f"Bearer {key}"}

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(f"{base}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    text = data["choices"][0]["message"]["content"].strip()

    usage = data.get("usage", {})
    if usage:
        logger.info(
            f"[LLM] provider=ionet model={IONET_MODEL} "
            f"in={usage.get('prompt_tokens',0)} "
            f"out={usage.get('completion_tokens',0)} tokens"
        )
    return text


async def _ask_ollama(messages: list) -> str:
    # Ollama expects model + messages; system prompt is just a message with role=system.
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": messages,
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": MAX_TOKENS,
        },
    }

    url = f"{OLLAMA_URL.rstrip('/')}/api/chat"
    last_err: str | None = None
    for attempt in range(1, 4):
        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, headers=OLLAMA_HEADERS, json=payload)

            latency_ms = int((time.perf_counter() - t0) * 1000)

            # 5xx: ретраи
            if response.status_code >= 500:
                last_err = f"server {response.status_code}: {(response.text or '')[:200]}"
                logger.warning(
                    f"[LLM] provider=ollama model={OLLAMA_MODEL} "
                    f"attempt={attempt} latency_ms={latency_ms} err={last_err}"
                )
                await asyncio.sleep(0.6 * attempt)
                continue

            response.raise_for_status()
            data = response.json()
            text = (data.get("message") or {}).get("content") or ""
            text = text.strip()
            logger.info(
                f"[LLM] provider=ollama model={OLLAMA_MODEL} attempt={attempt} latency_ms={latency_ms}"
            )
            return text
        except Exception as e:
            latency_ms = int((time.perf_counter() - t0) * 1000)
            last_err = f"{type(e).__name__}: {e}"
            logger.warning(
                f"[LLM] provider=ollama model={OLLAMA_MODEL} attempt={attempt} latency_ms={latency_ms} err={last_err}"
            )
            await asyncio.sleep(0.6 * attempt)

    raise RuntimeError(f"Ollama call failed: {last_err}")


def _fallback_ollama_enabled() -> bool:
    return str(LLM_FALLBACK_OLLAMA or "0").strip().lower() in {"1", "true", "yes", "on"}


async def ask_llm(system: str, history: list, user_message: str) -> str:
    """
    Отправляет запрос к LLM (OpenRouter, Ollama или Anthropic) и возвращает текст ответа.
    history — список {"role": "user"/"assistant", "content": "..."}
    """
    messages = [{"role": "system", "content": system}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    provider = (LLM_PROVIDER or "openrouter").strip().lower()
    if provider == "ollama":
        return await _ask_ollama(messages)
    if provider == "anthropic":
        try:
            return await _ask_anthropic(messages)
        except Exception as e:
            if _fallback_ollama_enabled():
                logger.warning(f"[LLM] anthropic failed, fallback ollama: {e}")
                return await _ask_ollama(messages)
            raise
    if provider == "ionet":
        return await _ask_ionet(messages)
    return await _ask_openrouter(messages)


async def polish_ru(text: str) -> str:
    """
    Второй проход: та же роль — техподдержка/консультант Gain Tech.
    Только выправляет русский (грамматика, склонения), без смены роли и без мета-фраз.
    """
    enabled = str(LLM_RU_POLISH or "0").strip() not in {"0", "false", "False", "no", "NO"}
    if not enabled:
        return text

    draft = (text or "").strip()
    if not draft:
        return text

    system = (
        "Ты — тот же AI-агент Gain Tech: техподдержка, консультант, продажи. "
        "Тебе дали черновик ответа клиенту — перепиши его грамотно по-русски.\n"
        "Верни ТОЛЬКО готовый ответ клиенту, одним сообщением.\n"
        "Запрещено: представляться «редактором», «языковой моделью», менять роль на что угодно, кроме агента Gain Tech; "
        "любые вступления про себя как про постороннюю роль; объяснения правок; мета про промпты.\n"
        "Правила:\n"
        "- Только русский, без английских вставок и без чужих алфавитов.\n"
        "- Сохрани смысл, факты и тон поддержки/консультации; не добавляй новых обещаний и цифр.\n"
        "- Лёгкий сленг допустим умеренно.\n"
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": draft},
    ]

    provider = (LLM_PROVIDER or "openrouter").strip().lower()
    try:
        if provider == "ollama":
            polished = await _ask_ollama(messages)
        elif provider == "anthropic":
            try:
                polished = await _ask_anthropic(messages)
            except Exception:
                if _fallback_ollama_enabled():
                    polished = await _ask_ollama(messages)
                else:
                    raise
        elif provider == "ionet":
            polished = await _ask_ionet(messages)
        else:
            polished = await _ask_openrouter(messages)

        polished = (polished or "").strip()
        low = polished.lower()
        # Защита от "мета" и самопрезентаций редактора.
        if any(
            bad in low
            for bad in (
                "я редактор",
                "как редактор",
                "редактор русского языка",
                "как языковая модель",
                "я — редактор",
                "язык модель",
            )
        ):
            return text
        # Если редактор внезапно смешал алфавиты (например, деванагари) — откат.
        if any(ord(ch) > 127 and ch not in "«»—–…№ёЁ“”’‘" for ch in polished):
            # допускаем русские/типографику, но если пошла экзотика — не применяем
            # (простая эвристика).
            if any("\u0900" <= ch <= "\u097f" for ch in polished):  # деванагари
                return text
        return polished
    except Exception:
        return text

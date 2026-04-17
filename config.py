import os
import logging
from pathlib import Path
try:
    from dotenv import load_dotenv

    # Важно: переопределять переменные из окружения, чтобы после правки .env
    # (или прошлых пустых значений) приложение гарантированно использовало актуальный ключ.
    load_dotenv(override=True)
except ModuleNotFoundError:
    # python-dotenv может быть ещё не установлен (до pip install -r requirements.txt)
    pass


def _read_env_value_from_file(path: str, name: str) -> str:
    """
    Надёжный fallback-парсер для ключей из .env.
    Иногда python-dotenv/окружение может не подхватить значение корректно.
    """
    try:
        p = Path(path)
        if not p.exists():
            return ""
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        needle = f"{name}="
        value = ""
        for line in lines:
            if line.startswith(needle):
                value = line[len(needle) :].strip()
        return value
    except Exception:
        return ""

def _env(name: str, default: str = "") -> str:
    v = os.getenv(name, default)
    if v is None:
        return default
    v = v.strip()
    if (len(v) >= 2) and ((v[0] == v[-1]) and v[0] in ("'", '"')):
        v = v[1:-1].strip()
    return v


# If OPENROUTER_API_KEY был "пустым" из окружения, но значение есть в .env,
# то берём его напрямую из файла.
_env_path = str(Path(__file__).resolve().parent / ".env")
if not (os.getenv("OPENROUTER_API_KEY") or "").strip():
    file_val = _read_env_value_from_file(_env_path, "OPENROUTER_API_KEY")
    if file_val:
        os.environ["OPENROUTER_API_KEY"] = file_val

# ── Telegram ──────────────────────────────────
BOT_TOKEN = _env("BOT_TOKEN", "ВСТАВЬТЕ_НОВЫЙ_ТОКЕН_БОТА")

# ── OpenRouter / LLM ─────────────────────────
OPENROUTER_API_KEY = _env("OPENROUTER_API_KEY", "ВСТАВЬТЕ_НОВЫЙ_КЛЮЧ")
LLM_MODEL = _env("LLM_MODEL", "openai/gpt-4o-mini")   # дешёвая модель по умолчанию
LLM_BASE_URL = "https://openrouter.ai/api/v1"
LLM_PROVIDER = _env("LLM_PROVIDER", "openrouter")  # openrouter | ollama | anthropic | ionet

# ── io.net (IO Intelligence, OpenAI-compatible) ──────────────────────
IONET_API_KEY = _env("IONET_API_KEY", "")
IONET_BASE_URL = _env("IONET_BASE_URL", "https://api.intelligence.io.solutions/api/v1")
IONET_MODEL = _env("IONET_MODEL", "meta-llama/Llama-3.3-70B-Instruct")

# ── Anthropic (Claude API, Messages API) ─────
ANTHROPIC_API_KEY = _env("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = _env("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
# При ошибке Claude (сеть, 5xx) один раз пробовать локальную Ollama (нужен LLM_PROVIDER=anthropic и рабочий Ollama)
LLM_FALLBACK_OLLAMA = _env("LLM_FALLBACK_OLLAMA", "0")

# ── Ollama (локальный LLM) ───────────────────
OLLAMA_URL = _env("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = _env("OLLAMA_MODEL", "llama3.2:3b")
LLM_RU_POLISH = _env("LLM_RU_POLISH", "0")  # 1|0: второй проход "редактор русского" (выключен: ломает роль без контекста)

# ── Лимиты ───────────────────────────────────
FREE_LIMIT = 5          # бесплатных ответов на пользователя
MAX_HISTORY = 10        # последних сообщений в контексте
MAX_TOKENS = 512        # макс. токенов ответа
TEMPERATURE = 0.7

# ── Уведомления ──────────────────────────────
NOTIFY_CHANNEL_ID = _env("NOTIFY_CHANNEL_ID", "")
if not NOTIFY_CHANNEL_ID:
    logging.warning("[CONFIG] NOTIFY_CHANNEL_ID не задан! Уведомления не будут отправляться.")
else:
    logging.info(f"[CONFIG] NOTIFY_CHANNEL_ID загружен: {NOTIFY_CHANNEL_ID}")

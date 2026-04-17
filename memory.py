from collections import defaultdict

from config import MAX_HISTORY



class MemoryManager:
    """
    In-memory хранилище для MVP.
    В продакшене заменить на Redis (сессии) + Postgres (факты/история).
    """

    def __init__(self):
        # {user_id: {"history": [...], "facts": {}, "messages": 0, "leads": 0, "paid": False}}
        self._store: dict = defaultdict(self._default_state)

    @staticmethod
    def _default_state():
        return {
            "history": [],      # [{role, content}, ...]
            "facts": {},        # извлечённые факты
            "messages": 0,      # всего сообщений
            "leads": 0,         # лидов
            "paid": False,      # оплачен тариф
            "flow_type": "order",
            "stage": "general_chat",
            "order_q": 0,
            "order_answers": {},
            "has_contact": False,
            "contact": {},
            "name_attempts": 0,
            "offtopic_strikes": 0,
        }

    # ── Сессия ───────────────────────────────
    def reset_session(self, user_id: str):
        self._store[user_id] = self._default_state()

    def reset_history(self, user_id: str):
        """
        Сброс после завершения воронки: очищает историю и факты, обнуляет поля воронки.
        Не трогает: messages, leads, paid, flow_type, has_contact, contact.
        """
        s = self._store[user_id]
        s["history"] = []
        s["facts"] = {}
        s["stage"] = "general_chat"
        s["order_q"] = 0
        s["order_answers"] = {}
        s["name_attempts"] = 0
        s["offtopic_strikes"] = 0

    def reset_conversation(self, user_id: str):
        """
        Полный сброс сессии для /start и /reset: новое состояние как у нового пользователя,
        но сохраняются счётчик сообщений (messages), лиды (leads) и оплата (paid).
        """
        s = self._store[user_id]
        keep_messages = s.get("messages", 0)
        keep_paid = s.get("paid", False)
        keep_leads = s.get("leads", 0)
        self._store[user_id] = self._default_state()
        self._store[user_id]["messages"] = keep_messages
        self._store[user_id]["paid"] = keep_paid
        self._store[user_id]["leads"] = keep_leads

    # ── State machine (воронка) ───────────────
    def get_stage(self, user_id: str) -> str:
        return self._store[user_id].get("stage", "general_chat")

    def set_stage(self, user_id: str, stage: str):
        self._store[user_id]["stage"] = stage

    def reset_order_flow(self, user_id: str):
        s = self._store[user_id]
        s["stage"] = "order_q1"
        s["order_q"] = 1
        s["order_answers"] = {}
        s["name_attempts"] = 0

    def save_order_answer(self, user_id: str, q: int, text: str):
        s = self._store[user_id]
        s["order_answers"][f"q{q}"] = text
        s["order_q"] = q

    def set_order_q(self, user_id: str, q: int):
        self._store[user_id]["order_q"] = int(q)

    def get_order_q(self, user_id: str) -> int:
        return int(self._store[user_id].get("order_q") or 0)

    def get_order_answers(self, user_id: str) -> dict:
        return dict(self._store[user_id].get("order_answers") or {})

    def set_flow_type(self, user_id: str, flow_type: str):
        self._store[user_id]["flow_type"] = (flow_type or "order").strip().lower()

    def get_flow_type(self, user_id: str) -> str:
        return str(self._store[user_id].get("flow_type") or "order")

    def set_contact(self, user_id: str, contact: dict):
        s = self._store[user_id]
        s["has_contact"] = True
        s["contact"] = contact or {}

    def has_contact(self, user_id: str) -> bool:
        return bool(self._store[user_id].get("has_contact"))

    def get_contact(self, user_id: str) -> dict:
        return dict(self._store[user_id].get("contact") or {})

    def bump_offtopic(self, user_id: str) -> int:
        s = self._store[user_id]
        s["offtopic_strikes"] = int(s.get("offtopic_strikes") or 0) + 1
        return s["offtopic_strikes"]

    def reset_offtopic(self, user_id: str):
        self._store[user_id]["offtopic_strikes"] = 0

    def inc_name_attempts(self, user_id: str) -> int:
        s = self._store[user_id]
        s["name_attempts"] = int(s.get("name_attempts") or 0) + 1
        return s["name_attempts"]

    def reset_name_attempts(self, user_id: str):
        self._store[user_id]["name_attempts"] = 0

    def is_paid(self, user_id: str) -> bool:
        return self._store[user_id]["paid"]

    def set_paid(self, user_id: str):
        self._store[user_id]["paid"] = True

    # ── Квота ────────────────────────────────
    def has_quota(self, user_id: str) -> bool:
        return True

    def _get(self, user_id: str) -> dict:
        return self._store[user_id]

    # ── История диалога ───────────────────────
    def get_history(self, user_id: str, max_pairs: int = 10) -> list:
        history = self._store[user_id]["history"]
        if max_pairs and len(history) > max_pairs * 2:
            return history[-(max_pairs * 2):]
        return history

    def get_history_text(self, user_id: str) -> str:
        """Последние 10 реплик из истории диалога как plain text."""
        data = self._get(user_id)
        msgs = data.get("history", [])[-10:]
        lines = []
        for m in msgs:
            role = "Клиент" if m.get("role") == "user" else "Аврора"
            lines.append(f"{role}: {m.get('content', '')}")
        return "\n".join(lines)

    def add_turn(self, user_id: str, user_text: str, bot_text: str, is_lead: bool = False):
        s = self._store[user_id]
        s["history"].append({"role": "user", "content": user_text})
        s["history"].append({"role": "assistant", "content": bot_text})
        MAX_KEEP = (MAX_HISTORY or 10) * 2
        if len(s["history"]) > MAX_KEEP:
            s["history"] = s["history"][-MAX_KEEP:]
        s["messages"] += 1
        if is_lead:
            s["leads"] += 1
        # Память не режем.

    def add_lead(self, user_id: str):
        self._store[user_id]["leads"] += 1

    # ── Факты (долгосрочная память) ──────────
    def get_facts(self, user_id: str) -> dict:
        return self._store[user_id]["facts"]

    def extract_facts(self, user_id: str, user_text: str, bot_text: str):
        """Простое извлечение фактов из диалога (rule-based для MVP)."""
        facts = self._store[user_id]["facts"]
        lower = user_text.lower()

        # Ниша
        niches = {
            "медицина":   ["клиник", "врач", "медицин", "стоматолог", "запись к"],
            "e-commerce": ["магазин", "товар", "доставк", "интернет-магазин", "маркетплейс"],
            "образование": ["курс", "обучени", "школ", "онлайн-школ", "тренинг"],
            "агентство":  ["агентств", "студия", "маркетинг", "smm", "реклам"],
            "b2b":        ["b2b", "корпоратив", "предприят", "завод", "оптов"],
            "ресторан":   ["кафе", "ресторан", "доставка еды", "дарккитчен"],
        }
        for niche, keywords in niches.items():
            if any(k in lower for k in keywords):
                facts["ниша"] = niche
                break

        # Интерес к тарифу
        if any(k in lower for k in ["стартер", "starter", "9900", "9 900"]):
            facts["тариф"] = "Starter 9 900₽"
        elif any(k in lower for k in ["growth", "24900", "24 900"]):
            facts["тариф"] = "Growth 24 900₽"
        elif any(k in lower for k in ["про", "pro", "49900", "49 900", "агентств"]):
            facts["тариф"] = "Pro 49 900₽"

        # Объём обращений
        import re
        match = re.search(r"(\d+)\s*(обращени|заявк|сообщени|лидов|клиент)", lower)
        if match:
            facts["объём/мес"] = f"~{match.group(1)}"

        # Бюджет
        if any(k in lower for k in ["бюджет", "стоимость", "сколько стоит", "цена"]):
            facts["интерес"] = "уточняет цену"

    # ── Статистика ───────────────────────────
    def get_stats(self, user_id: str) -> dict:
        s = self._store[user_id]
        return {
            "messages":  s["messages"],
            "leads":     s["leads"],
            "free_left": "∞",
            "paid":      True,
        }

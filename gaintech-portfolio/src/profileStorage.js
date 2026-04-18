const KEY = 'gaintech_miniapp_profile_v1';

/** @returns {{ name: string, phone: string } | null} */
export function loadProfile() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const o = JSON.parse(raw);
    const name = (o.name || '').trim();
    const phone = (o.phone || '').trim();
    if (!name && !phone) return null;
    return { name, phone };
  } catch {
    return null;
  }
}

export function saveProfile({ name, phone }) {
  const payload = {
    name: (name || '').trim(),
    phone: (phone || '').trim(),
    updatedAt: Date.now(),
  };
  localStorage.setItem(KEY, JSON.stringify(payload));
}

export function clearProfile() {
  localStorage.removeItem(KEY);
}

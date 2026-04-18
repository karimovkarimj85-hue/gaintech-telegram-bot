import { useState, useEffect } from 'react';

/**
 * true — открыто внутри Telegram Mini App (или WebView Telegram).
 * false — обычный браузер: показываем публичный сайт.
 *
 * initData иногда приходит с задержкой; дублируем проверку после WebApp.ready().
 * User-Agent в клиенте Telegram часто содержит «Telegram» — запасной признак.
 */
export function useIsTelegramMiniApp() {
  const [isMiniApp, setIsMiniApp] = useState(() => readIsTelegramMiniApp());

  useEffect(() => {
    const update = () => setIsMiniApp(readIsTelegramMiniApp());
    update();

    const tw = window.Telegram?.WebApp;
    if (tw?.ready) {
      tw.ready(() => {
        update();
      });
    }

    const t0 = setTimeout(update, 0);
    const t1 = setTimeout(update, 120);
    const t2 = setTimeout(update, 400);
    const t3 = setTimeout(update, 1000);

    return () => {
      clearTimeout(t0);
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, []);

  return isMiniApp;
}

function readIsTelegramMiniApp() {
  if (typeof window === 'undefined') return false;
  try {
    const ua = typeof navigator !== 'undefined' ? navigator.userAgent || '' : '';
    if (/Telegram/i.test(ua)) return true;

    const tw = window.Telegram?.WebApp;
    if (!tw) return false;

    if (typeof tw.initData === 'string' && tw.initData.length > 0) return true;

    const unsafe = tw.initDataUnsafe;
    if (unsafe && typeof unsafe === 'object') {
      if (unsafe.user && typeof unsafe.user.id === 'number') return true;
      if (unsafe.auth_date != null) return true;
      if (unsafe.query_id != null) return true;
    }

    return false;
  } catch {
    return false;
  }
}

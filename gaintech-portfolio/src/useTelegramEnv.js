import { useState, useEffect } from 'react';

/**
 * true — страница открыта внутри Telegram Mini App (есть initData).
 * false — обычный браузер (Chrome и т.д.): можно показывать другой UI.
 */
export function useIsTelegramMiniApp() {
  const [isMiniApp, setIsMiniApp] = useState(() => readIsTelegramMiniApp());

  useEffect(() => {
    setIsMiniApp(readIsTelegramMiniApp());
  }, []);

  return isMiniApp;
}

function readIsTelegramMiniApp() {
  if (typeof window === 'undefined') return false;
  try {
    const data = window.Telegram?.WebApp?.initData;
    return typeof data === 'string' && data.length > 0;
  } catch {
    return false;
  }
}

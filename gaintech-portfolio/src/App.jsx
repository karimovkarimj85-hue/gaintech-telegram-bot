import { useState, useEffect, useMemo, useCallback } from 'react';
import Waves from './components/Waves';
import TextType from './components/TextType';
import MagicBento from './components/MagicBento';
import ReflectiveCard from './components/ReflectiveCard';
import Dock from './components/Dock';
import PublicNav from './components/PublicNav';
import PublicFooter from './components/PublicFooter';
import { PROJECTS, BENTO_ITEMS, typeLabel } from './projects';
import { loadProfile, saveProfile, clearProfile } from './profileStorage';
import { useIsTelegramMiniApp } from './useTelegramEnv';
import './App.css';

const PUBLIC_BOT_URL = 'https://t.me/gaintech_bot';

/** На ПК (широкий экран) — одна длинная страница; в мини-приложении узкий экран — как раньше, две «вкладки». */
function useDesktopMerge() {
  const query = '(min-width: 1024px)';
  const [matches, setMatches] = useState(() =>
    typeof window !== 'undefined' ? window.matchMedia(query).matches : false,
  );
  useEffect(() => {
    const mql = window.matchMedia(query);
    const onChange = () => setMatches(mql.matches);
    mql.addEventListener('change', onChange);
    setMatches(mql.matches);
    return () => mql.removeEventListener('change', onChange);
  }, []);
  return matches;
}

/** 2D-фон (canvas), общий для «О нас» и «Работы» */
const WAVES_BG_PROPS = {
  lineColor: 'rgba(255, 255, 255, 0.12)',
  backgroundColor: 'transparent',
  waveSpeedX: 0.0125,
  waveSpeedY: 0.01,
  waveAmpX: 40,
  waveAmpY: 20,
  friction: 0.9,
  tension: 0.01,
  maxCursorMove: 120,
  xGap: 12,
  yGap: 36,
};

function IconGrid() {
  return (
    <svg viewBox="0 0 24 24" strokeWidth="1.5">
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
    </svg>
  );
}
function IconInfo() {
  return (
    <svg viewBox="0 0 24 24" strokeWidth="1.5">
      <circle cx="12" cy="12" r="10" />
      <path d="M12 16v-4M12 8h.01" strokeLinecap="round" />
    </svg>
  );
}

function PreviewImg({ src, fallback }) {
  const [failed, setFailed] = useState(false);
  if (failed) {
    return <img src={fallback} alt="" />;
  }
  return <img src={src} alt="" onError={() => setFailed(true)} />;
}

function sendTelegramData(payload) {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.sendData(JSON.stringify(payload));
  }
}

export default function App() {
  const isTelegram = useIsTelegramMiniApp();
  const desktopMerged = useDesktopMerge();
  /** В браузере всегда одна длинная страница; в Telegram — как раньше на узком экране. */
  const mergedLayout = !isTelegram || desktopMerged;
  const [page, setPage] = useState('about');
  const [orderOpen, setOrderOpen] = useState(false);
  const [consultOpen, setConsultOpen] = useState(false);
  const [profile, setProfile] = useState(() => loadProfile());

  const [fName, setFName] = useState('');
  const [fPhone, setFPhone] = useState('');
  const [fService, setFService] = useState('');
  const [fDesc, setFDesc] = useState('');
  const [fBudget, setFBudget] = useState('');
  const [fQuestion, setFQuestion] = useState('');
  const [err, setErr] = useState('');
  const [projectFilter, setProjectFilter] = useState('all');

  const filteredProjects = useMemo(() => {
    if (projectFilter === 'all') return PROJECTS;
    return PROJECTS.filter((p) => p.type === projectFilter);
  }, [projectFilter]);

  const projectCounts = useMemo(() => {
    const all = PROJECTS.length;
    const site = PROJECTS.filter((p) => p.type === 'site').length;
    const bot = PROJECTS.filter((p) => p.type === 'bot').length;
    const other = PROJECTS.filter((p) => p.type === 'other').length;
    return { all, site, bot, other };
  }, []);

  useEffect(() => {
    if (!isTelegram || !window.Telegram?.WebApp) return;
    const tw = window.Telegram.WebApp;
    tw.ready();
    tw.expand();
    tw.setHeaderColor('#080808');
    tw.setBackgroundColor('#080808');
  }, [isTelegram]);

  useEffect(() => {
    const p = loadProfile();
    if (p) {
      setFName(p.name || '');
      setFPhone(p.phone || '');
    }
  }, [orderOpen, consultOpen]);

  const scrollToSection = useCallback((id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, []);

  /** Подсветка раздела при прокрутке (док в Telegram или шапка на сайте). */
  useEffect(() => {
    if (!mergedLayout) return;
    const worksEl = document.getElementById('section-works');
    if (!worksEl) return;
    const onScroll = () => {
      const top = worksEl.getBoundingClientRect().top;
      const threshold = window.innerHeight * 0.38;
      const next = top <= threshold ? 'projects' : 'about';
      setPage((prev) => (prev === next ? prev : next));
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener('scroll', onScroll);
  }, [mergedLayout]);

  function openOrder() {
    if (!isTelegram) {
      window.open(PUBLIC_BOT_URL, '_blank', 'noopener,noreferrer');
      return;
    }
    setErr('');
    const p = loadProfile();
    setFName(p?.name || '');
    setFPhone(p?.phone || '');
    setFService('');
    setFDesc('');
    setFBudget('');
    setOrderOpen(true);
  }

  function openConsult() {
    if (!isTelegram) {
      window.open(PUBLIC_BOT_URL, '_blank', 'noopener,noreferrer');
      return;
    }
    setErr('');
    const p = loadProfile();
    setFName(p?.name || '');
    setFPhone(p?.phone || '');
    setFQuestion('');
    setConsultOpen(true);
  }

  function submitOrder(e) {
    e.preventDefault();
    const name = fName.trim();
    const phone = fPhone.trim().replace(/\s|-/g, '');
    const desc = fDesc.trim();
    if (name.length < 2) {
      setErr('Укажите имя и фамилию.');
      return;
    }
    if (phone.length < 7) {
      setErr('Укажите корректный телефон.');
      return;
    }
    if (desc.length < 5) {
      setErr('Кратко опишите задачу.');
      return;
    }
    saveProfile({ name, phone });
    setProfile(loadProfile());
    sendTelegramData({
      action: 'order',
      name,
      phone,
      service: fService.trim() || '—',
      desc,
      budget: fBudget.trim() || '—',
    });
    setOrderOpen(false);
  }

  function submitConsult(e) {
    e.preventDefault();
    const name = fName.trim();
    const phone = fPhone.trim().replace(/\s|-/g, '');
    const question = fQuestion.trim();
    if (name.length < 2) {
      setErr('Укажите имя и фамилию.');
      return;
    }
    if (phone.length < 7) {
      setErr('Укажите корректный телефон.');
      return;
    }
    if (question.length < 5) {
      setErr('Опишите вопрос или задачу.');
      return;
    }
    saveProfile({ name, phone });
    setProfile(loadProfile());
    sendTelegramData({
      action: 'consult',
      type: 'consult',
      name,
      phone,
      question,
    });
    setConsultOpen(false);
  }

  const goAbout = () => {
    setPage('about');
    if (mergedLayout) scrollToSection('section-about');
  };
  const goWorks = () => {
    setPage('projects');
    if (mergedLayout) scrollToSection('section-works');
  };

  const dockItems = [
    {
      icon: <IconInfo />,
      label: 'О нас',
      className: page === 'about' ? 'dock-item--active' : '',
      onClick: goAbout,
    },
    {
      icon: <IconGrid />,
      label: 'Работы',
      className: page === 'projects' ? 'dock-item--active' : '',
      onClick: goWorks,
    },
  ];

  const hideAboutMobile = isTelegram && !desktopMerged && page !== 'about';
  const hideProjectsMobile = isTelegram && !desktopMerged && page !== 'projects';

  return (
    <div className={`app${!isTelegram ? ' app--public' : ''}`}>
      {(page === 'about' || page === 'projects') && (
        <div className="app__waves app__waves--about" aria-hidden>
          <Waves {...WAVES_BG_PROPS} />
        </div>
      )}

      {!isTelegram && <PublicNav activeSection={page} onAbout={goAbout} onWorks={goWorks} />}

      <div className={`app__main${mergedLayout ? ' app__main--desktop-merge' : ''}`}>
        <div
          id="section-about"
          className={`about-page${hideAboutMobile ? ' app-section--hide-mobile' : ''}`}
        >
            <header className="header header--about about-page__intro">
              <div className="brand">Gain Tech</div>
              <TextType
                as="h1"
                className="about-kicker"
                text={['Automate growth', 'Боты, сайты, автоматизация', 'Заявки без рутины в Telegram']}
                typingSpeed={48}
                pauseDuration={2200}
                deletingSpeed={36}
                showCursor
                cursorCharacter="|"
                cursorBlinkDuration={0.55}
                loop
                initialDelay={500}
              />
              <p className="about-lead">
                Telegram-боты, сайты и автоматизация под ваш бизнес. Founder —{' '}
                <a href="https://t.me/krm_kmb" target="_blank" rel="noreferrer">
                  @krm_kmb
                </a>
                . Ответим в течение 2 часов в рабочее время.
              </p>
            </header>

            <div className="about-page__layout">
              <div className="about-page__primary">
                <section className="about-hero">
                  <ReflectiveCard blurStrength={16} overlayColor="rgba(0,0,0,0.42)" />
                  <div className="about-hero__inner">
                    <p className="about-hero__eyebrow">
                      {isTelegram ? 'Заявка из мини-приложения' : 'Связь и заявки'}
                    </p>
                    <p className="about-hero__text">
                      {isTelegram
                        ? 'Имя и телефон сохраняются на устройстве — не нужно вводить их заново при каждой консультации или заказе.'
                        : 'Заявки и консультации ведём через Telegram-бота: нажмите кнопку ниже или откройте бота по ссылке в шапке.'}
                    </p>
                    {profile && (
                      <p className="about-hero__profile">
                        Сохранено: <strong>{profile.name}</strong> · {profile.phone}
                      </p>
                    )}
                  </div>
                </section>

                <div className="about-cta">
                  <button type="button" className="cta-btn cta-btn--primary" onClick={openConsult}>
                    {isTelegram ? 'Записаться на консультацию' : 'Консультация в Telegram'}
                  </button>
                  <button type="button" className="cta-btn cta-btn--ghost" onClick={openOrder}>
                    {isTelegram ? 'Оформить заказ' : 'Заказ через бота'}
                  </button>
                </div>
              </div>

              <aside className="about-page__aside" aria-label="Услуги">
                <p className="about-bento-label">Что делаем</p>
                <div className="bento-wrap bento-wrap--compact">
                  <MagicBento
                    items={BENTO_ITEMS}
                    textAutoHide
                    enableStars
                    enableSpotlight
                    enableBorderGlow
                    enableTilt={false}
                    enableMagnetism={false}
                    clickEffect
                    spotlightRadius={320}
                    particleCount={10}
                    glowColor="132, 0, 255"
                    disableAnimations={false}
                  />
                </div>
              </aside>
            </div>
        </div>

        <div
          id="section-works"
          className={`projects-page${hideProjectsMobile ? ' app-section--hide-mobile' : ''}`}
        >
            <header className="header header--projects">
              <div className="brand">Gain Tech</div>
              <div className="header-title header-title--sm">
                Кейсы
                <br />
                <span>и проекты</span>
              </div>
              <p className="header-sub">Боты, сайты, CRM и AI — сюда будем добавлять новые работы по мере запуска.</p>
            </header>

            <div className="filters-wrap">
              <div className="filters">
                {[
                  ['all', 'Все'],
                  ['bot', 'Боты'],
                  ['site', 'Сайты'],
                  ['other', 'Другое'],
                ].map(([k, label]) => (
                  <button
                    key={k}
                    type="button"
                    className={`filter-btn ${projectFilter === k ? 'active' : ''}`}
                    onClick={() => setProjectFilter(k)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div className="stats">
              <div className="stat">
                <div className="stat-num">{projectCounts.all}</div>
                <div className="stat-label">Всего</div>
              </div>
              <div className="stat">
                <div className="stat-num">{projectCounts.bot}</div>
                <div className="stat-label">Боты</div>
              </div>
              <div className="stat">
                <div className="stat-num">{projectCounts.site}</div>
                <div className="stat-label">Сайты</div>
              </div>
              <div className="stat">
                <div className="stat-num">{projectCounts.other}</div>
                <div className="stat-label">AI</div>
              </div>
            </div>

            <div className="grid">
              {filteredProjects.length === 0 ? (
                <div className="grid-empty">В этой категории пока пусто — загляните в «Все» или позже.</div>
              ) : (
                filteredProjects.map((item, index) => (
                <article key={item.id} className={'card' + (item.featured ? ' featured' : '')} style={{ animationDelay: `${index * 40}ms` }}>
                  <div className="card-preview">
                    <PreviewImg src={item.preview} fallback={item.previewFallback} />
                  </div>
                  <div className="card-body">
                    <div className="card-meta">
                      <span className="card-tag">{typeLabel[item.type]}</span>
                      <span className="card-year">{item.year}</span>
                    </div>
                    <div className="card-title">{item.title}</div>
                    <div className="card-desc">{item.desc}</div>
                    <div className="card-tech">
                      {item.tech.map((t) => (
                        <span key={t} className="tech-pill">
                          {t}
                        </span>
                      ))}
                    </div>
                    {item.url && item.url !== '#' ? (
                      <a className="card-link" href={item.url} target="_blank" rel="noreferrer">
                        {item.type === 'bot' ? 'Открыть бота' : 'Открыть'}
                      </a>
                    ) : null}
                  </div>
                </article>
                ))
              )}
            </div>

            <div className={`cta-row cta-row--tight${mergedLayout ? ' cta-row--desktop-merge-hide' : ''}`}>
              <button type="button" className="cta-btn secondary" onClick={goAbout}>
                ← О компании
              </button>
            </div>
        </div>
      </div>

      {!isTelegram && <PublicFooter />}

      {isTelegram && <Dock items={dockItems} panelHeight={56} baseItemSize={46} magnification={58} distance={180} />}

      {isTelegram && orderOpen && (
        <div className="modal-overlay" role="dialog" onClick={(e) => e.target === e.currentTarget && setOrderOpen(false)}>
          <div className="modal-sheet">
            <h3>Заявка</h3>
            <p className="modal-hint">
              Данные сохраняются в этом мини-приложении — не нужно вводить телефон каждый раз. Нажмите «Отправить», чтобы
              передать заявку боту.
            </p>
            <form onSubmit={submitOrder}>
              <div className="modal-field">
                <label htmlFor="oName">Имя и фамилия *</label>
                <input id="oName" value={fName} onChange={(e) => setFName(e.target.value)} autoComplete="name" placeholder="Иван Иванов" />
              </div>
              <div className="modal-field">
                <label htmlFor="oPhone">Телефон *</label>
                <input id="oPhone" value={fPhone} onChange={(e) => setFPhone(e.target.value)} inputMode="tel" autoComplete="tel" placeholder="+998901234567" />
              </div>
              <div className="modal-field">
                <label htmlFor="oSvc">Тип задачи</label>
                <select id="oSvc" value={fService} onChange={(e) => setFService(e.target.value)}>
                  <option value="">Выберите</option>
                  <option value="Сайт / лендинг">Сайт / лендинг</option>
                  <option value="Telegram-бот">Telegram-бот</option>
                  <option value="CRM / автоматизация">CRM / автоматизация</option>
                  <option value="AI / интеграция">AI / интеграция</option>
                  <option value="Другое">Другое</option>
                </select>
              </div>
              <div className="modal-field">
                <label htmlFor="oDesc">Опишите задачу *</label>
                <textarea id="oDesc" value={fDesc} onChange={(e) => setFDesc(e.target.value)} placeholder="Кратко: что нужно" />
              </div>
              <div className="modal-field">
                <label htmlFor="oBudget">Бюджет / сроки</label>
                <input id="oBudget" value={fBudget} onChange={(e) => setFBudget(e.target.value)} placeholder="По желанию" />
              </div>
              <div className={`modal-err ${err ? 'show' : ''}`}>{err}</div>
              <div className="modal-actions">
                <button type="button" className="modal-cancel" onClick={() => setOrderOpen(false)}>
                  Отмена
                </button>
                <button type="submit" className="modal-submit">
                  Отправить
                </button>
              </div>
              <div className="profile-note">
                <button type="button" onClick={() => { clearProfile(); setProfile(null); setFName(''); setFPhone(''); }}>
                  Забыть сохранённые контакты
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {isTelegram && consultOpen && (
        <div className="modal-overlay" role="dialog" onClick={(e) => e.target === e.currentTarget && setConsultOpen(false)}>
          <div className="modal-sheet">
            <h3>Консультация</h3>
            <p className="modal-hint">Опишите вопрос — менеджер свяжется с вами. Контакты подставляются автоматически.</p>
            <form onSubmit={submitConsult}>
              <div className="modal-field">
                <label htmlFor="cName">Имя и фамилия *</label>
                <input id="cName" value={fName} onChange={(e) => setFName(e.target.value)} autoComplete="name" />
              </div>
              <div className="modal-field">
                <label htmlFor="cPhone">Телефон *</label>
                <input id="cPhone" value={fPhone} onChange={(e) => setFPhone(e.target.value)} inputMode="tel" autoComplete="tel" />
              </div>
              <div className="modal-field">
                <label htmlFor="cQ">Вопрос / задача *</label>
                <textarea id="cQ" value={fQuestion} onChange={(e) => setFQuestion(e.target.value)} placeholder="Что хотите обсудить?" />
              </div>
              <div className={`modal-err ${err ? 'show' : ''}`}>{err}</div>
              <div className="modal-actions">
                <button type="button" className="modal-cancel" onClick={() => setConsultOpen(false)}>
                  Отмена
                </button>
                <button type="submit" className="modal-submit">
                  Отправить
                </button>
              </div>
              <div className="profile-note">
                <button type="button" onClick={() => { clearProfile(); setProfile(null); setFName(''); setFPhone(''); }}>
                  Забыть сохранённые контакты
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

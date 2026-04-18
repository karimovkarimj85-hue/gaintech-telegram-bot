import { useState, useEffect, useMemo } from 'react';
import LineWaves from './components/LineWaves';
import MagicBento from './components/MagicBento';
import ReflectiveCard from './components/ReflectiveCard';
import Dock from './components/Dock';
import { PROJECTS, BENTO_ITEMS, typeLabel } from './projects';
import { loadProfile, saveProfile, clearProfile } from './profileStorage';
import './App.css';

/** Тот же фон LineWaves, что на «О нас» */
const LINE_WAVES_PROPS = {
  speed: 0.28,
  innerLineCount: 28,
  outerLineCount: 32,
  warpIntensity: 1,
  rotation: -45,
  edgeFadeWidth: 0,
  colorCycleSpeed: 0.9,
  brightness: 0.22,
  color1: '#ffffff',
  color2: '#e0e7ff',
  color3: '#a78bfa',
  enableMouseInteraction: true,
  mouseInfluence: 1.8,
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
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready();
      window.Telegram.WebApp.expand();
      window.Telegram.WebApp.setHeaderColor('#080808');
      window.Telegram.WebApp.setBackgroundColor('#080808');
    }
  }, []);

  useEffect(() => {
    const p = loadProfile();
    if (p) {
      setFName(p.name || '');
      setFPhone(p.phone || '');
    }
  }, [orderOpen, consultOpen]);

  function openOrder() {
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

  const dockItems = [
    {
      icon: <IconInfo />,
      label: 'О нас',
      className: page === 'about' ? 'dock-item--active' : '',
      onClick: () => setPage('about'),
    },
    {
      icon: <IconGrid />,
      label: 'Работы',
      className: page === 'projects' ? 'dock-item--active' : '',
      onClick: () => setPage('projects'),
    },
  ];

  return (
    <div className="app">
      {(page === 'about' || page === 'projects') && (
        <div className="app__waves app__waves--about" aria-hidden>
          <LineWaves {...LINE_WAVES_PROPS} />
        </div>
      )}

      <div className="app__main">
        {page === 'about' && (
          <div className="about-page">
            <header className="header header--about">
              <div className="brand">Gain Tech</div>
              <h1 className="about-kicker">Automate growth</h1>
              <p className="about-lead">
                Telegram-боты, сайты и автоматизация под ваш бизнес. Founder —{' '}
                <a href="https://t.me/krm_kmb" target="_blank" rel="noreferrer">
                  @krm_kmb
                </a>
                . Ответим в течение 2 часов в рабочее время.
              </p>
            </header>

            <section className="about-hero">
              <ReflectiveCard blurStrength={16} overlayColor="rgba(0,0,0,0.42)" />
              <div className="about-hero__inner">
                <p className="about-hero__eyebrow">Заявка из мини-приложения</p>
                <p className="about-hero__text">
                  Имя и телефон сохраняются на устройстве — не нужно вводить их заново при каждой консультации или заказе.
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
                Записаться на консультацию
              </button>
              <button type="button" className="cta-btn cta-btn--ghost" onClick={openOrder}>
                Оформить заказ
              </button>
            </div>

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
          </div>
        )}

        {page === 'projects' && (
          <div className="projects-page">
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

            <div className="cta-row cta-row--tight">
              <button type="button" className="cta-btn secondary" onClick={() => setPage('about')}>
                ← О компании
              </button>
            </div>
          </div>
        )}
      </div>

      <Dock items={dockItems} panelHeight={56} baseItemSize={46} magnification={58} distance={180} />

      {orderOpen && (
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

      {consultOpen && (
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

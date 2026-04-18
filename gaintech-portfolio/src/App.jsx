import { useState, useEffect, useMemo } from 'react';
import LineWaves from './components/LineWaves';
import MagicBento from './components/MagicBento';
import ReflectiveCard from './components/ReflectiveCard';
import Dock from './components/Dock';
import { PROJECTS, BENTO_ITEMS, typeLabel } from './projects';
import { loadProfile, saveProfile, clearProfile } from './profileStorage';
import './App.css';

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

function sendTelegramData(payload) {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.sendData(JSON.stringify(payload));
  }
}

export default function App() {
  const [page, setPage] = useState('projects');
  const [filter, setFilter] = useState('all');
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

  const filtered = useMemo(() => {
    if (filter === 'all') return PROJECTS;
    return PROJECTS.filter((i) => i.type === filter);
  }, [filter]);

  const counts = useMemo(() => {
    const all = PROJECTS.length;
    const site = PROJECTS.filter((i) => i.type === 'site').length;
    const bot = PROJECTS.filter((i) => i.type === 'bot').length;
    const other = PROJECTS.filter((i) => i.type === 'other').length;
    return { all, site, bot, other };
  }, []);

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
    const payload = {
      action: 'order',
      name,
      phone,
      service: fService.trim() || '—',
      desc,
      budget: fBudget.trim() || '—',
    };
    sendTelegramData(payload);
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
      icon: <IconGrid />,
      label: 'Проекты',
      onClick: () => setPage('projects'),
    },
    {
      icon: <IconInfo />,
      label: 'О нас',
      onClick: () => setPage('about'),
    },
  ];

  return (
    <div className="app">
      {page === 'projects' && (
        <div className="app__waves" aria-hidden>
          <LineWaves
            speed={0.3}
            innerLineCount={32}
            outerLineCount={36}
            warpIntensity={1}
            rotation={-45}
            edgeFadeWidth={0}
            colorCycleSpeed={1}
            brightness={0.18}
            color1="#ffffff"
            color2="#ffffff"
            color3="#a78bfa"
            enableMouseInteraction
            mouseInfluence={1.5}
          />
        </div>
      )}

      <div className="app__main">
        {page === 'projects' && (
          <>
            <header className="header">
              <div className="brand">Gain Tech</div>
              <div className="header-title">
                Our
                <br />
                <span>Work.</span>
              </div>
              <p className="header-sub">
                Сайты, боты и AI — кейсы команды. Заявки и консультация сохраняют ваши контакты в этом приложении.
              </p>
            </header>

            <div className="filters-wrap">
              <div className="filters">
                {[
                  ['all', 'Все работы'],
                  ['site', 'Сайты'],
                  ['bot', 'Боты'],
                  ['other', 'Другое'],
                ].map(([k, label]) => (
                  <button
                    key={k}
                    type="button"
                    className={`filter-btn ${filter === k ? 'active' : ''}`}
                    onClick={() => setFilter(k)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div className="stats">
              <div className="stat">
                <div className="stat-num">{counts.all}</div>
                <div className="stat-label">Проектов</div>
              </div>
              <div className="stat">
                <div className="stat-num">{counts.site}</div>
                <div className="stat-label">Сайтов</div>
              </div>
              <div className="stat">
                <div className="stat-num">{counts.bot}</div>
                <div className="stat-label">Ботов</div>
              </div>
              <div className="stat">
                <div className="stat-num">{counts.other}</div>
                <div className="stat-label">AI</div>
              </div>
            </div>

            <div className="grid">
              {filtered.map((item, index) => (
                <article key={item.id} className={'card' + (item.featured ? ' featured' : '')} style={{ animationDelay: `${index * 40}ms` }}>
                  <div className="card-preview">
                    {item.preview ? (
                      <img src={item.preview} alt="" />
                    ) : (
                      <div className="card-preview-placeholder">
                        <span>Скоро превью</span>
                      </div>
                    )}
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
                        Открыть в Telegram
                      </a>
                    ) : null}
                  </div>
                </article>
              ))}
            </div>

            <div className="cta-row">
              <button type="button" className="cta-btn" onClick={openOrder}>
                Оформить заказ
              </button>
              <button type="button" className="cta-btn secondary" onClick={openConsult}>
                Записаться на консультацию
              </button>
            </div>
          </>
        )}

        {page === 'about' && (
          <>
            <header className="header">
              <div className="brand">Gain Tech</div>
              <div className="header-title">
                О
                <br />
                <span>команде</span>
              </div>
            </header>

            <div className="about-hero">
              <ReflectiveCard blurStrength={14} overlayColor="rgba(0,0,0,0.35)" />
              <div className="about-hero__inner">
                <h2>Automate growth</h2>
                <p>
                  Мы делаем Telegram-ботов, сайты и CRM под задачи бизнеса. Founder — Каримов Каримбек (@krm_kmb). Ответим в
                  течение 2 часов в рабочее время.
                </p>
                {profile && (
                  <p style={{ marginTop: 12, fontSize: 13, color: '#888' }}>
                    Контакты в приложении сохранены: {profile.name} · {profile.phone}
                  </p>
                )}
              </div>
            </div>

            <div className="bento-wrap">
              <MagicBento
                items={BENTO_ITEMS}
                textAutoHide
                enableStars
                enableSpotlight
                enableBorderGlow
                enableTilt={false}
                enableMagnetism={false}
                clickEffect
                spotlightRadius={400}
                particleCount={12}
                glowColor="132, 0, 255"
                disableAnimations={false}
              />
            </div>

            <div className="cta-row">
              <button type="button" className="cta-btn" onClick={openOrder}>
                Оформить заказ
              </button>
              <button type="button" className="cta-btn secondary" onClick={openConsult}>
                Консультация
              </button>
            </div>
          </>
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

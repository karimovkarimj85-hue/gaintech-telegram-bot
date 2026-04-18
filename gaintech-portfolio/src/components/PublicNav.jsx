import './PublicNav.css';

const BOT_URL = 'https://t.me/gaintech_bot';

export default function PublicNav({ activeSection, onAbout, onWorks }) {
  return (
    <header className="public-nav">
      <div className="public-nav__inner">
        <a className="public-nav__logo" href="#section-about" onClick={(e) => { e.preventDefault(); onAbout(); }}>
          Gain Tech
        </a>
        <nav className="public-nav__links" aria-label="Разделы">
          <button
            type="button"
            className={`public-nav__link ${activeSection === 'about' ? 'public-nav__link--active' : ''}`}
            onClick={onAbout}
          >
            О нас
          </button>
          <button
            type="button"
            className={`public-nav__link ${activeSection === 'projects' ? 'public-nav__link--active' : ''}`}
            onClick={onWorks}
          >
            Работы
          </button>
          <a className="public-nav__cta" href={BOT_URL} target="_blank" rel="noreferrer">
            Telegram-бот
          </a>
        </nav>
      </div>
    </header>
  );
}

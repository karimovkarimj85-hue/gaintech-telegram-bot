import './PublicFooter.css';

export default function PublicFooter() {
  return (
    <footer className="public-footer">
      <div className="public-footer__inner">
        <span className="public-footer__brand">Gain Tech</span>
        <span className="public-footer__sep">·</span>
        <span>Боты, сайты, автоматизация</span>
      </div>
      <a className="public-footer__link" href="https://t.me/gaintech_bot" target="_blank" rel="noreferrer">
        Открыть в Telegram
      </a>
    </footer>
  );
}

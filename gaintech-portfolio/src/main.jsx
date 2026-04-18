import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { err: null };
  }

  static getDerivedStateFromError(err) {
    return { err };
  }

  componentDidCatch(err, info) {
    console.error('[portfolio]', err, info);
  }

  render() {
    if (this.state.err) {
      return (
        <div
          style={{
            minHeight: '100vh',
            padding: 24,
            background: '#111',
            color: '#eee',
            fontFamily: 'system-ui, sans-serif',
            fontSize: 15,
            lineHeight: 1.5,
          }}
        >
          <p>Не удалось загрузить интерфейс. Закройте мини-приложение и откройте снова.</p>
          <p style={{ color: '#888', fontSize: 13 }}>Если повторяется — напишите в поддержку бота.</p>
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);

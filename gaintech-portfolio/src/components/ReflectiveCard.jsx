import './ReflectiveCard.css';

/**
 * «Стекло» без WebGL: backdrop-filter + блик (аналог ReflectiveCard из React Bits).
 */
export default function ReflectiveCard({
  overlayColor = 'rgba(0, 0, 0, 0.2)',
  blurStrength = 12,
  className = '',
  style = {},
}) {
  return (
    <div
      className={`reflective-card-wrap ${className}`}
      style={{
        ...style,
        '--blur': `${blurStrength}px`,
        background: overlayColor,
      }}
    >
      <div className="reflective-card" />
    </div>
  );
}

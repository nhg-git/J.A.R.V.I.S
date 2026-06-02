export default function ResearchPanel({ sources, onClose }) {
  const show = sources && sources.length > 0

  return (
    <div className={`research-panel ${show ? '' : 'hidden'}`}>
      {show && (
        <>
          <div className="research-panel__header">
            <span>⬡ INTELLIGENCE SOURCES</span>
            <button
              onClick={onClose}
              style={{
                background: 'none', border: 'none',
                color: 'var(--c-dim)', cursor: 'pointer',
                fontSize: 14, lineHeight: 1,
              }}
              title="Close sources"
            >
              ✕
            </button>
          </div>
          <div className="research-panel__body">
            <div style={{
              fontSize: 11,
              color: 'var(--c-dim)',
              letterSpacing: '0.06em',
              padding: '2px 0 6px',
            }}>
              {sources.length} source{sources.length !== 1 ? 's' : ''} accessed
            </div>
            {sources.map(src => (
              <SourceCard key={src.index} source={src} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

function SourceCard({ source }) {
  return (
    <div className="source-card">
      <span className="source-card__index">
        SOURCE [{String(source.index).padStart(2, '0')}]
      </span>
      <span className="source-card__title">{source.title}</span>
      <span className="source-card__domain">◈ {source.domain}</span>
      {source.snippet && (
        <span className="source-card__snippet">{source.snippet}</span>
      )}
      {source.url && (
        <a
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="source-card__link"
        >
          ↗ OPEN SOURCE
        </a>
      )}
    </div>
  )
}

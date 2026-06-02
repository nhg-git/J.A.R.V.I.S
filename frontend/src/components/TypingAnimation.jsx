export default function TypingAnimation() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '4px 0' }}>
      <span style={{ color: 'var(--c-primary)', fontSize: 11, letterSpacing: '0.1em' }}>
        JARVIS
      </span>
      <span style={{ color: 'var(--c-dim)', fontSize: 11 }}>is processing</span>
      <span style={{
        display: 'inline-flex',
        gap: 3,
        alignItems: 'center',
      }}>
        {[0, 1, 2].map(i => (
          <span
            key={i}
            style={{
              display: 'inline-block',
              width: 5,
              height: 5,
              borderRadius: '50%',
              background: 'var(--c-primary)',
              animation: `blink 1.2s ease-in-out ${i * 0.25}s infinite`,
              boxShadow: 'var(--glow-sm)',
            }}
          />
        ))}
      </span>
    </div>
  )
}

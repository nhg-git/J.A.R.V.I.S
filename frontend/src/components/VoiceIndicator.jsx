export default function VoiceIndicator({ isRecording }) {
  if (!isRecording) return null

  return (
    <div className="voice-indicator">
      <div className="voice-indicator__bar">
        {[...Array(5)].map((_, i) => (
          <span key={i} />
        ))}
      </div>
      <span>RECORDING</span>
      <div className="voice-indicator__bar" style={{ transform: 'scaleX(-1)' }}>
        {[...Array(5)].map((_, i) => (
          <span key={i} />
        ))}
      </div>
    </div>
  )
}

import { useState, useEffect } from 'react'

export default function StatusBar({ connected }) {
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  const timeStr = time.toLocaleTimeString('en-GB', { hour12: false })
  const dateStr = time.toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
  }).toUpperCase()

  return (
    <div className="status-bar">
      <div className="status-bar__left">
        <span className="status-bar__title">J.A.R.V.I.S</span>
        <span className={`status-pill ${connected ? 'online' : 'offline'}`}>
          {connected ? '● ONLINE' : '○ OFFLINE'}
        </span>
      </div>
      <div className="status-bar__right">
        <span className="status-pill">{dateStr}</span>
        <span className="status-bar__clock">{timeStr}</span>
      </div>
    </div>
  )
}

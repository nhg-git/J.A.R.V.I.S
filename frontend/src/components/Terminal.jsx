import { useRef, useEffect, useState, useCallback } from 'react'
import TypingAnimation from './TypingAnimation.jsx'
import VoiceIndicator from './VoiceIndicator.jsx'
import { useVoice } from '../hooks/useVoice.js'

/* ── Tiny markdown-to-HTML renderer (no external deps) ──────── */
function renderMarkdown(text) {
  if (!text) return ''
  let html = text
    // Code blocks
    .replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) =>
      `<pre><code class="lang-${lang}">${escHtml(code.trim())}</code></pre>`
    )
    // Inline code
    .replace(/`([^`]+)`/g, (_, c) => `<code>${escHtml(c)}</code>`)
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.+?)__/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/_(.+?)_/g, '<em>$1</em>')
    // Headers
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bullet points
    .replace(/^[\-\*] (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, s => `<ul>${s}</ul>`)
    // Numbered lists
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Blockquotes
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    // Horizontal rules
    .replace(/^─{3,}$/gm, '<hr style="border-color:var(--border);margin:10px 0">')
    // Newlines to <br> (skip inside block elements)
    .replace(/\n/g, '<br>')
    // Links
    .replace(
      /\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
    )

  return html
}

function escHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

/* ── JARVIS ASCII logo ──────────────────────────────────────── */
const LOGO = `
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝`.trimStart()

const BOOT_MESSAGES = [
  '> Initialising J.A.R.V.I.S core systems...',
  '> Loading neural language modules...',
  '> Voice synthesis ready.',
  '> Research protocols armed.',
  '> Memory banks online.',
  '> All systems nominal. Good to see you, sir.',
]

export default function Terminal({
  messages,
  isTyping,
  status,
  connected,
  ttsEnabled,
  onToggleTTS,
  onSend,
  onResearch,
  onAudio,
}) {
  const [input, setInput]           = useState('')
  const [bootDone, setBootDone]     = useState(false)
  const [bootLines, setBootLines]   = useState([])
  const [showBoot, setShowBoot]     = useState(true)
  const messagesEndRef              = useRef(null)
  const inputRef                    = useRef(null)
  const textareaRef                 = useRef(null)

  /* ── Boot sequence animation ─────────────────────────────── */
  useEffect(() => {
    let i = 0
    const id = setInterval(() => {
      if (i < BOOT_MESSAGES.length) {
        setBootLines(prev => [...prev, BOOT_MESSAGES[i]])
        i++
      } else {
        clearInterval(id)
        setTimeout(() => {
          setBootDone(true)
          setTimeout(() => setShowBoot(false), 600)
        }, 400)
      }
    }, 260)
    return () => clearInterval(id)
  }, [])

  /* ── Auto-scroll to bottom ───────────────────────────────── */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  /* ── Focus input on load ─────────────────────────────────── */
  useEffect(() => {
    if (!showBoot) inputRef.current?.focus()
  }, [showBoot])

  /* ── Voice hook ──────────────────────────────────────────── */
  const { isRecording, error: voiceError, supported: voiceSupported, toggleRecording } = useVoice(onAudio)

  /* ── Handle send ─────────────────────────────────────────── */
  const handleSend = useCallback(() => {
    const text = input.trim()
    if (!text || !connected) return
    onSend(text)
    setInput('')
  }, [input, connected, onSend])

  const handleResearch = useCallback(() => {
    const text = input.trim()
    if (!text || !connected) return
    onResearch(text)
    setInput('')
  }, [input, connected, onResearch])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  /* ── Render a single message ─────────────────────────────── */
  const renderMessage = (msg) => {
    const isJarvis = msg.role === 'assistant'
    const isUser   = msg.role === 'user'
    const isSystem = msg.role === 'system'

    const roleLabel = isJarvis ? 'JARVIS' : isSystem ? 'SYSTEM' : 'YOU'
    const roleClass = isJarvis ? 'jarvis' : isSystem ? 'system' : isUser ? 'user' : 'error'

    const timeStr = msg.timestamp
      ? new Date(msg.timestamp).toLocaleTimeString('en-GB', { hour12: false })
      : ''

    return (
      <div key={msg.id} className={`message ${msg.role}`}>
        <div className="message__header">
          <span className={`message__role ${roleClass}`}>[ {roleLabel} ]</span>
          {timeStr && <span className="message__time">{timeStr}</span>}
          {msg.type === 'research' && (
            <span style={{ fontSize: 10, color: 'var(--c-system)', letterSpacing: '0.08em' }}>
              ⬡ RESEARCH
            </span>
          )}
          {msg.type === 'voice' && (
            <span style={{ fontSize: 10, color: 'var(--c-user)', letterSpacing: '0.08em' }}>
              ◉ VOICE
            </span>
          )}
        </div>

        {isJarvis ? (
          <div
            className="message__content md-content"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
          />
        ) : (
          <div className="message__content">{msg.content}</div>
        )}
      </div>
    )
  }

  /* ── Boot overlay ────────────────────────────────────────── */
  if (showBoot) {
    return (
      <div style={{
        flex: 1,
        background: 'var(--bg-terminal)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'flex-start',
        padding: '40px 60px',
        overflow: 'hidden',
        position: 'relative',
      }}>
        <div className="corner-brackets" />
        <pre style={{
          color: 'var(--c-primary)',
          textShadow: 'var(--glow-md)',
          fontSize: 11,
          lineHeight: 1.3,
          marginBottom: 28,
          letterSpacing: '0.04em',
        }}>
          {LOGO}
        </pre>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {bootLines.map((line, i) => (
            <div
              key={i}
              className="boot-line"
              style={{
                color: i === bootLines.length - 1 ? 'var(--c-system)' : 'var(--c-dim)',
                fontSize: 13,
                animationDelay: `${i * 0.05}s`,
                letterSpacing: '0.04em',
              }}
            >
              {line}
              {i === bootLines.length - 1 && !bootDone && (
                <span className="typing-cursor" />
              )}
            </div>
          ))}
        </div>
      </div>
    )
  }

  /* ── Main terminal ───────────────────────────────────────── */
  return (
    <div className="terminal">
      <div className="corner-brackets" />

      {/* Logo header */}
      <div className="terminal-logo">
        <pre className="logo-ascii" style={{ fontSize: 10, lineHeight: 1.35 }}>{LOGO}</pre>
        <div className="logo-tagline">
          JUST A RATHER VERY INTELLIGENT SYSTEM  ·  v2.0.0
        </div>
      </div>

      {/* Messages */}
      <div className="messages-container">
        {/* Welcome if no messages */}
        {messages.length === 0 && (
          <div className="message system">
            <div className="message__header">
              <span className="message__role system">[ SYSTEM ]</span>
            </div>
            <div className="message__content">
              All systems online. How can I assist you today, sir?{'\n'}
              Speak or type your query. Use the ⬡ RESEARCH button for live web search.
            </div>
          </div>
        )}

        {messages.map(renderMessage)}

        {isTyping && (
          <div className="message assistant" style={{ opacity: 0.8 }}>
            <div className="message__header">
              <span className="message__role jarvis">[ JARVIS ]</span>
            </div>
            <TypingAnimation />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Live status */}
      {status && (
        <div className="terminal-status">
          <div className="terminal-status__dot" />
          <span>{status}</span>
        </div>
      )}

      {/* Input row */}
      <div className="input-area">
        <span className="input-prompt">›</span>

        <textarea
          ref={inputRef}
          className="input-field"
          rows={1}
          value={input}
          onChange={e => {
            setInput(e.target.value)
            // Auto-resize
            e.target.style.height = 'auto'
            e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
          }}
          onKeyDown={handleKeyDown}
          placeholder={connected ? 'Query JARVIS… (Enter to send, Shift+Enter for newline)' : 'Connecting to JARVIS…'}
          disabled={!connected}
          spellCheck={false}
          autoComplete="off"
        />

        <div className="input-buttons">
          <button
            className="btn btn--research"
            onClick={handleResearch}
            disabled={!input.trim() || !connected}
            title="Force web search"
          >
            ⬡ SEARCH
          </button>

          {/* TTS toggle */}
          <button
            className="btn"
            onClick={onToggleTTS}
            title={ttsEnabled ? 'JARVIS voice ON — click to mute' : 'JARVIS voice OFF — click to unmute'}
            style={{
              borderColor: ttsEnabled
                ? 'rgba(0, 245, 212, 0.5)'
                : 'rgba(239, 71, 111, 0.4)',
              color: ttsEnabled
                ? 'var(--c-system)'
                : 'var(--c-error)',
              fontSize: 15,
              padding: '5px 10px',
            }}
          >
            {ttsEnabled ? '🔊' : '🔇'}
          </button>

          <button
            className={`btn btn--voice ${isRecording ? 'recording' : ''}`}
            onClick={() => toggleRecording(onSend)}
            title={
              voiceSupported === false
                ? 'Voice not supported — use Chrome or Edge'
                : isRecording
                ? 'Stop recording (click to stop)'
                : 'Start voice input'
            }
            disabled={voiceSupported === false}
          >
            {isRecording ? '◉' : '🎤'}
          </button>

          <button
            className="btn btn--send"
            onClick={handleSend}
            disabled={!input.trim() || !connected}
          >
            SEND ↵
          </button>
        </div>
      </div>

      {/* Voice error message */}
      {voiceError && (
        <div style={{
          position: 'fixed',
          bottom: 80,
          left: '50%',
          transform: 'translateX(-50%)',
          background: 'rgba(4,4,14,0.95)',
          border: '1px solid var(--c-error)',
          color: 'var(--c-error)',
          padding: '8px 20px',
          borderRadius: 20,
          fontSize: 12,
          letterSpacing: '0.04em',
          zIndex: 100,
          pointerEvents: 'none',
          maxWidth: 460,
          textAlign: 'center',
        }}>
          ⚠ {voiceError}
        </div>
      )}

      <VoiceIndicator isRecording={isRecording} />
    </div>
  )
}

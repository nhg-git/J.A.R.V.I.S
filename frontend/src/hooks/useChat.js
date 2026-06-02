import { useState, useEffect, useRef, useCallback } from 'react'

const WS_URL = `ws://${window.location.hostname}:8000/ws`

// ── Unlock audio on first user interaction ──────────────────────
// Chrome blocks autoplay until the user has clicked something
let audioUnlocked = false
const unlockAudio = () => {
  if (audioUnlocked) return
  const ctx = new (window.AudioContext || window.webkitAudioContext)()
  ctx.resume().then(() => { audioUnlocked = true })
}
document.addEventListener('click', unlockAudio, { once: false })
document.addEventListener('keydown', unlockAudio, { once: false })

export function useChat() {
  const [messages, setMessages]         = useState([])
  const [isTyping, setIsTyping]         = useState(false)
  const [status, setStatus]             = useState('')
  const [sources, setSources]           = useState([])
  const [conversationId, setConversationId] = useState(null)
  const [connected, setConnected]       = useState(false)
  const [llmProvider, setLlmProvider]   = useState('OFFLINE')
  const [ttsEnabled, setTtsEnabled]     = useState(true)
  const ttsEnabledRef                   = useRef(true)  // ref avoids stale closure in WS handler

  const toggleTTS = useCallback(() => {
    setTtsEnabled(prev => {
      ttsEnabledRef.current = !prev
      return !prev
    })
  }, [])

  const ws                = useRef(null)
  const currentMsgRef     = useRef('')
  const currentMsgIdRef   = useRef(null)
  const reconnectTimer    = useRef(null)

  const genId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`

  const addMessage = useCallback((role, content, type = 'text', id = null) => {
    const msgId = id || genId()
    setMessages(prev => [...prev, { id: msgId, role, content, type, timestamp: new Date() }])
    return msgId
  }, [])

  const updateMessage = useCallback((id, content) => {
    setMessages(prev => prev.map(m => (m.id === id ? { ...m, content } : m)))
  }, [])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimer.current)
      ws.current?.close()
    }
  }, [])

  function connect() {
    const socket = new WebSocket(WS_URL)
    ws.current = socket

    socket.onopen = () => {
      setConnected(true)
      socket.send(JSON.stringify({ type: 'history' }))
    }

    socket.onclose = () => {
      setConnected(false)
      setStatus('Reconnecting...')
      reconnectTimer.current = setTimeout(connect, 3000)
    }

    socket.onerror = () => {
      setStatus('Cannot reach backend — is python run.py running?')
    }

    socket.onmessage = (event) => {
      try { handleServerMessage(JSON.parse(event.data)) }
      catch (e) { console.error('WS parse error:', e) }
    }
  }

  function handleServerMessage(msg) {
    switch (msg.type) {

      case 'connected':
        setConversationId(msg.conversation_id)
        setStatus('SYSTEMS ONLINE')
        setConnected(true)
        fetch('/api/health')
          .then(r => r.json())
          .then(d => {
            const p = d.llm?.provider?.toUpperCase() || 'UNKNOWN'
            const m = d.llm?.model || ''
            setLlmProvider(`${p} / ${m}`)
          })
          .catch(() => setLlmProvider('UNKNOWN'))
        setTimeout(() => setStatus(''), 2000)
        break

      case 'history':
        if (msg.messages?.length) {
          setMessages(msg.messages.map(m => ({
            id: m.id || genId(),
            role: m.role,
            content: m.content,
            type: m.type || 'text',
            timestamp: new Date(m.timestamp || Date.now()),
          })))
        }
        break

      case 'typing_start':
        currentMsgRef.current   = ''
        currentMsgIdRef.current = genId()
        setIsTyping(true)
        setMessages(prev => [...prev, {
          id: currentMsgIdRef.current,
          role: 'assistant',
          content: '',
          type: 'text',
          timestamp: new Date()
        }])
        break

      case 'text_chunk':
        currentMsgRef.current += msg.content
        updateMessage(currentMsgIdRef.current, currentMsgRef.current)
        break

      case 'status':
        setStatus(msg.content)
        break

      case 'research_sources':
        setSources(msg.sources || [])
        break

      case 'audio':
        if (msg.data && ttsEnabledRef.current) playBase64Audio(msg.data)
        break

      case 'voice_text':
        addMessage('user', msg.content, 'voice')
        break

      case 'done':
        setIsTyping(false)
        setStatus('')
        currentMsgRef.current   = ''
        currentMsgIdRef.current = null
        break

      case 'error':
        setIsTyping(false)
        setStatus(`ERROR: ${msg.content}`)
        addMessage('system', `⚠ ${msg.content}`, 'error')
        break

      case 'pong': break
      default: console.log('Unknown WS msg:', msg.type)
    }
  }

  const sendMessage = useCallback((text, type = 'chat') => {
    if (!text.trim() || !ws.current) return
    if (ws.current.readyState !== WebSocket.OPEN) {
      setStatus('Not connected yet — try again in a moment.')
      return
    }
    addMessage('user', text)
    setSources([])
    setStatus('')
    ws.current.send(JSON.stringify({ type, content: text, conversation_id: conversationId }))
  }, [conversationId, addMessage])

  const sendResearch = useCallback((text) => sendMessage(text, 'research'), [sendMessage])

  const sendAudio = useCallback((base64Audio) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) return
    setSources([])
    ws.current.send(JSON.stringify({ type: 'voice', audio: base64Audio, conversation_id: conversationId }))
  }, [conversationId])

  return {
    messages, isTyping, status, sources,
    conversationId, connected, llmProvider,
    ttsEnabled, toggleTTS,
    sendMessage, sendResearch, sendAudio,
  }
}

// ── TTS audio playback ────────────────────────────────────────
async function playBase64Audio(b64) {
  try {
    const binary = atob(b64)
    const bytes  = new Uint8Array(binary.length)
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)

    // Use AudioContext (bypasses autoplay restrictions better than Audio element)
    const ctx    = new (window.AudioContext || window.webkitAudioContext)()
    await ctx.resume()
    const buffer = await ctx.decodeAudioData(bytes.buffer)
    const source = ctx.createBufferSource()
    source.buffer = buffer
    source.connect(ctx.destination)
    source.start(0)
    source.onended = () => ctx.close()
  } catch (e) {
    // Fallback to plain Audio element
    try {
      const binary = atob(b64)
      const bytes  = new Uint8Array(binary.length)
      for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
      const blob   = new Blob([bytes], { type: 'audio/mp3' })
      const url    = URL.createObjectURL(blob)
      const audio  = new Audio(url)
      audio.onended = () => URL.revokeObjectURL(url)
      await audio.play()
    } catch (e2) {
      console.warn('Audio playback failed:', e2.message)
    }
  }
}

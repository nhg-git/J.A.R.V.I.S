import { useState, useRef, useCallback, useEffect } from 'react'

export function useVoice(onAudioReady) {
  const [isRecording, setIsRecording]   = useState(false)
  const [error, setError]               = useState(null)
  const [supported, setSupported]       = useState(null) // null = unchecked
  const recorderRef                     = useRef(null)
  const chunksRef                       = useRef([])
  const recognitionRef                  = useRef(null)

  // ── Detect browser support on mount ──────────────────────────
  useEffect(() => {
    const hasSpeech  = !!(window.SpeechRecognition || window.webkitSpeechRecognition)
    const hasMedia   = !!(navigator.mediaDevices?.getUserMedia)
    setSupported(hasSpeech || hasMedia)
  }, [])

  // ── Clear error after 5s ─────────────────────────────────────
  useEffect(() => {
    if (!error) return
    const t = setTimeout(() => setError(null), 5000)
    return () => clearTimeout(t)
  }, [error])

  // ── Browser Web Speech API ────────────────────────────────────
  const startBrowserSTT = useCallback((onResult) => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) return false

    try {
      const recognition = new SpeechRecognition()
      recognitionRef.current = recognition
      recognition.continuous      = false
      recognition.interimResults  = false
      recognition.lang            = 'en-US'
      recognition.maxAlternatives = 1

      recognition.onstart  = () => { setIsRecording(true);  setError(null) }
      recognition.onend    = () => { setIsRecording(false) }

      recognition.onerror  = (e) => {
        setIsRecording(false)
        const msgs = {
          'not-allowed':   'Microphone access denied. Allow mic in browser settings.',
          'no-speech':     'No speech detected. Try again.',
          'network':       'Network error during recognition.',
          'aborted':       null,   // user cancelled — no message needed
        }
        const msg = msgs[e.error] ?? `Voice error: ${e.error}`
        if (msg) setError(msg)
      }

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript.trim()
        if (transcript) onResult(transcript)
      }

      recognition.start()
      return true
    } catch (e) {
      setError(`Could not start voice: ${e.message}`)
      return false
    }
  }, [])

  // ── Stop browser STT ─────────────────────────────────────────
  const stopBrowserSTT = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
      recognitionRef.current = null
    }
  }, [])

  // ── MediaRecorder → Whisper (fallback) ───────────────────────
  const startWhisperRecording = useCallback(async () => {
    try {
      setError(null)
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      chunksRef.current = []

      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/ogg;codecs=opus'

      const recorder = new MediaRecorder(stream, { mimeType })
      recorderRef.current = recorder

      recorder.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data) }
      recorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop())
        const blob   = new Blob(chunksRef.current, { type: mimeType })
        const buffer = await blob.arrayBuffer()
        const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)))
        onAudioReady(base64)
        setIsRecording(false)
      }

      recorder.start()
      setIsRecording(true)
    } catch (e) {
      const msg = e.name === 'NotAllowedError'
        ? 'Microphone access denied. Click the lock icon in your browser address bar to allow it.'
        : `Mic error: ${e.message}`
      setError(msg)
      setIsRecording(false)
    }
  }, [onAudioReady])

  const stopWhisperRecording = useCallback(() => {
    if (recorderRef.current && recorderRef.current.state !== 'inactive') {
      recorderRef.current.stop()
    }
  }, [])

  // ── Toggle ───────────────────────────────────────────────────
  const toggleRecording = useCallback((onTextResult) => {
    if (isRecording) {
      stopBrowserSTT()
      stopWhisperRecording()
      return
    }

    const usedBrowser = startBrowserSTT(onTextResult)
    if (!usedBrowser) {
      startWhisperRecording()
    }
  }, [isRecording, startBrowserSTT, stopBrowserSTT, startWhisperRecording, stopWhisperRecording])

  return { isRecording, error, supported, toggleRecording }
}

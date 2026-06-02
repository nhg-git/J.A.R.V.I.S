import Terminal from '../components/Terminal.jsx'
import ResearchPanel from '../components/ResearchPanel.jsx'
import StatusBar from '../components/StatusBar.jsx'
import { useChat } from '../hooks/useChat.js'
import { useState } from 'react'

export default function Home() {
  const {
    messages,
    isTyping,
    status,
    sources,
    conversationId,
    connected,
    llmProvider,
    ttsEnabled,
    toggleTTS,
    sendMessage,
    sendResearch,
    sendAudio,
  } = useChat()

  const [sourcesVisible, setSourcesVisible] = useState(true)

  const handleCloseSources = () => setSourcesVisible(false)

  // Re-open when new sources arrive
  const visibleSources = sourcesVisible ? sources : []

  return (
    <div className="jarvis-layout">
      <StatusBar
        connected={connected}
        llmProvider={llmProvider}
        conversationId={conversationId}
      />
      <div className="jarvis-body">
        <Terminal
          messages={messages}
          isTyping={isTyping}
          status={status}
          connected={connected}
          ttsEnabled={ttsEnabled}
          onToggleTTS={toggleTTS}
          onSend={sendMessage}
          onResearch={(text) => {
            setSourcesVisible(true)
            sendResearch(text)
          }}
          onAudio={sendAudio}
        />
        <ResearchPanel
          sources={visibleSources}
          onClose={handleCloseSources}
        />
      </div>
    </div>
  )
}

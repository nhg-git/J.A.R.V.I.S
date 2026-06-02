const BASE = 'http://localhost:8000/api'

export const api = {
  async health() {
    const r = await fetch(`${BASE}/health`)
    return r.json()
  },

  async newConversation(title) {
    const r = await fetch(`${BASE}/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    })
    return r.json()
  },

  async getConversations() {
    const r = await fetch(`${BASE}/conversations`)
    return r.json()
  },

  async getMessages(conversationId) {
    const r = await fetch(`${BASE}/conversations/${conversationId}/messages`)
    return r.json()
  },
}

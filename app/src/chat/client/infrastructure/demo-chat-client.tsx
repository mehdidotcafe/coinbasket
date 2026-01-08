import type { ChatClient } from '../chat-client'
import data from './demo-data.json' assert { type: 'json' }

export const demoChatClient: ChatClient = {
  fetchMessages: async () => {
    return (data as any)['https://agent-warren.coinbasket.ai'] ?? []
  },

  addMessage: async (message) => {
    return {
      id: message.id,
      role: message.role,
      isInterrupting: false,
      ui: undefined,
      content: message.content as string,
      createdAt: message.createdAt,
    }
  },
}

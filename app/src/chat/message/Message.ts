import type { MessageUi } from './MessageUi'

export interface Message {
  id: string
  role: 'data' | 'user' | 'assistant' | 'system'
  isInterrupting?: boolean
  ui?: MessageUi
  content?: string
  createdAt?: Date
}

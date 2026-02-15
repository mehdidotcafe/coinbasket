import type { Message } from '../message/Message'
import type { QueryMessage } from '../message/QueryMessage'

export interface ChatClient {
  fetchMessages: () => Promise<Message[]>
  addMessage: (message: QueryMessage) => Promise<Message[]>
}

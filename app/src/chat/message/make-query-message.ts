import type { QueryMessage } from './QueryMessage'

export function makeQueryMessage(content: QueryMessage['content'], isResuming: QueryMessage['isResuming']): QueryMessage {
  return {
    isResuming,
    role: 'user',
    content,
    createdAt: new Date(),
    id: Math.random().toString(36).substring(2, 15),
  }
}

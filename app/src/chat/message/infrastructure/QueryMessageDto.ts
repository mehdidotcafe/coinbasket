import type { QueryMessage } from '../QueryMessage'

export interface QueryMessageRequest {
  id: string
  role: 'user'
  is_resuming: boolean
  content: string
  created_at?: string
}

function mapQueryMessageContentToQueryMessageRequestContent(content: QueryMessage['content']) {
  if (typeof content === 'string') {
    return content
  }

  return JSON.stringify({
    status: content.status,
    signable_order_id: content.signableOrderId,
    transaction_hash: content.transactionHash,
  })
}

function mapQueryMessageRequestContentToQueryMessageContent(content: QueryMessageRequest['content']) {
  // JSON not supported for now
  return content
}

export class QueryMessageDto {
  static toRequest(message: QueryMessage): QueryMessageRequest {
    return {
      id: message.id,
      role: message.role,
      is_resuming: message.isResuming,
      content: mapQueryMessageContentToQueryMessageRequestContent(message.content),
      created_at: message.createdAt?.toISOString(),
    }
  }

  static fromRequest(message: QueryMessageRequest): QueryMessage {
    return {
      id: message.id,
      role: message.role,
      isResuming: message.is_resuming,
      content: mapQueryMessageRequestContentToQueryMessageContent(message.content),
      createdAt: message.created_at ? new Date(message.created_at) : undefined,
    }
  }
}

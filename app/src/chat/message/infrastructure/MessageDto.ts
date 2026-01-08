import type { Message } from '../Message'
import * as z from 'zod'
import { MessageUiDto, MessageUiResponseSchema } from './MessageUiDto'

export const MessageResponseSchema = z.object({
  id: z.string(),
  role: z.string(),
  is_interrupting: z.boolean(),
  ui: MessageUiResponseSchema.optional().nullable(),
  content: z.string().optional().nullable(),
  created_at: z.string(),
})

type MessageResponse = z.infer<typeof MessageResponseSchema>

export class MessageDto {
  static fromResponse(message: MessageResponse): Message {
    return {
      id: message.id,
      role: message.role as Message['role'],
      isInterrupting: message.is_interrupting,
      ui: message.ui ? MessageUiDto.fromResponse(message.ui) : undefined,
      content: message.content ?? undefined,
      createdAt: new Date(message.created_at),
    }
  }
}

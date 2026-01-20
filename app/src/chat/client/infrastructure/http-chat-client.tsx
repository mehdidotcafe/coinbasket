import type { ChatClient } from '../chat-client'
import urlJoin from 'url-join'
import * as z from 'zod'
import { MessageDto, MessageResponseSchema } from '@/chat/message/infrastructure/MessageDto'
import { QueryMessageDto } from '@/chat/message/infrastructure/QueryMessageDto'

const MessagesResponseSchema = z.object({
  messages: z.array(MessageResponseSchema),
})

type MessagesResponse = z.infer<typeof MessagesResponseSchema>

const defaultHeaders = {
  'Content-Type': 'application/json',
  'accept': 'application/json',
}

export function httpChatClient(baseUrl: string): ChatClient {
  return {
    fetchMessages: async () => {
      return fetch(urlJoin(baseUrl, 'conversation', 'messages'), {
        method: 'POST',
        credentials: 'include',
        headers: {
          ...defaultHeaders,
        },
      }).then((res) => {
        if (!res.ok) {
          throw new Error('Network response was not ok')
        }

        return res.json()
      }).then((maybeMessagesResponse) => {
        return MessagesResponseSchema.parseAsync(maybeMessagesResponse)
      }).then(async (messagesResponse: MessagesResponse) => {
        return messagesResponse.messages.map((message) => {
          return MessageDto.fromResponse(message)
        })
      }).catch((e) => {
        console.error('Error fetching messages:', e)
        throw e
      })
    },

    addMessage: async (message) => {
      return fetch(urlJoin(baseUrl, 'conversation'), {
        method: 'POST',
        credentials: 'include',
        headers: {
          ...defaultHeaders,
        },
        body: JSON.stringify({
          message: QueryMessageDto.toRequest(message),
        }),
      }).then((res) => {
        if (!res.ok) {
          throw new Error('Network response was not ok')
        }
        return res.json()
      }).then((data) => {
        return MessageDto.fromResponse(data)
      })
    },

  }
}

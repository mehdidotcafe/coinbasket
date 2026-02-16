import type { UIMessage } from 'ai'
import { useChat as useAIChat } from '@ai-sdk/react'
import { DefaultChatTransport } from 'ai'
import { useEffect, useMemo, useRef } from 'react'
import urlJoin from 'url-join'
import { useAuthentication } from '@/authentication/use-authentication'
import { useEnv } from '@/env/use-env'

async function fetchInitialMessages(apiUrl: string): Promise<UIMessage[]> {
  const res = await fetch(urlJoin(apiUrl, 'conversation', 'messages'), {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
  })

  if (!res.ok) {
    throw new Error('Failed to fetch messages')
  }

  return res.json()
}

export function useChat() {
  const authentication = useAuthentication()
  const { API_URL } = useEnv()
  const isAuthenticated = authentication.authStatus === 'authenticated'

  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: urlJoin(API_URL, 'conversation'),
        credentials: 'include',
        prepareSendMessagesRequest: ({ messages, body }) => {
          const lastMessage = messages[messages.length - 1]
          const textPart = lastMessage.parts.find(p => p.type === 'text')
          const text = textPart && 'text' in textPart ? textPart.text : ''

          const isResuming = (body as Record<string, unknown> | undefined)?.is_resuming === true

          return {
            body: {
              message: {
                id: lastMessage.id,
                role: 'user',
                is_resuming: isResuming,
                content: text,
                created_at: new Date().toISOString(),
              },
            },
          }
        },
      }),
    [API_URL],
  )

  const { messages, sendMessage, status, setMessages } = useAIChat({
    transport,
  })

  const hasFetchedRef = useRef(false)

  useEffect(() => {
    if (!isAuthenticated || hasFetchedRef.current)
      return
    hasFetchedRef.current = true

    fetchInitialMessages(API_URL).then((initialMessages) => {
      setMessages(initialMessages)
    }).catch((err) => {
      console.error('Error fetching initial messages:', err)
    })
  }, [isAuthenticated, API_URL, setMessages])

  const lastMessage = messages.length > 0 ? messages[messages.length - 1] : undefined
  const isInterrupted = lastMessage?.parts.some(p => p.type.startsWith('data-interrupt')) ?? false
  const isWaitingMessage = status === 'submitted'
  const isFetching = !hasFetchedRef.current && isAuthenticated

  return {
    isInterrupted,
    isWaitingMessage,
    isFetching,
    isPending: isFetching,
    isEnabled: isAuthenticated,
    messages: messages.map(message => structuredClone(message)),
    sendMessage,
    status,
  }
}

import type { Message } from './message/Message'
import type { QueryMessage } from './message/QueryMessage'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback } from 'react'
import { useAuthentication } from '@/authentication/use-authentication'
import { useRegistry } from '../registry/use-registry'
import { makeQueryMessage } from './message/make-query-message'

export function useChat() {
  const authentication = useAuthentication()
  const {
    chatClient,
  } = useRegistry()
  const queryClient = useQueryClient()
  const keys = authentication.authStatus === 'authenticated' ? [`chat:${authentication.address}:messages`] : []

  const { data: messages = [], isFetching, isPending, isEnabled } = useQuery({
    queryKey: keys,
    queryFn: () => chatClient.fetchMessages(),
    refetchOnWindowFocus: false,
    enabled: authentication.authStatus === 'authenticated',
  })

  const addMessageMutation = useMutation({
    mutationFn: (message: QueryMessage) => chatClient.addMessage(message),
    onMutate: async (newMessageContent) => {
      await queryClient.cancelQueries({ queryKey: keys })

      const previousMessages = queryClient.getQueryData<Message[]>(keys)

      if (typeof newMessageContent.content === 'string') {
        const newMessage = makeQueryMessage(newMessageContent.content, false) as Message

        queryClient.setQueryData<Message[]>(keys, old => [...(old || []), newMessage])
      }

      return { previousMessages }
    },

    onSuccess: (newMessages) => {
      queryClient.setQueryData<Message[]>(keys, old => [...(old || []), ...newMessages])
    },
    onError: (_err, _newMessage, context) => {
      if (context?.previousMessages) {
        queryClient.setQueryData<Message[]>(keys, context.previousMessages)
      }
    },
  })

  const addMessage = useCallback(
    (message: QueryMessage) => addMessageMutation.mutateAsync(message),
    [addMessageMutation],
  )

  return {
    isInterrupted: (messages.length > 0 && messages[messages.length - 1].isInterrupting) ?? false,
    isWaitingMessage: (messages.length > 0 && messages[messages.length - 1].role === 'user') ?? false,
    isFetching,
    isPending,
    isEnabled,
    messages,
    addMessage,
  }
}

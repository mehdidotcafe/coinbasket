'use client'
import type { Message } from '../message/Message'
import type { QueryMessage } from '../message/QueryMessage'
import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { Suspense, useEffect, useRef } from 'react'
import { Disclaimer } from '@/components/disclaimer'
import { EmptyConversationScreen } from '@/components/empty-conversation-screen'
import { LoadingScreen } from '@/components/screen/loading-screen'
import { Loader } from '@/loader'
import { makeQueryMessage } from '../message/make-query-message'
import { useChat } from '../use-chat'
import { MessageList } from './message-list'
import { PromptForm } from './prompt-form'

function computePromptFormStatus(isWaitingMessage: boolean, isInterrupted: boolean) {
  if (isInterrupted) {
    return 'waiting_user_response'
  }

  if (isWaitingMessage) {
    return 'waiting_ai_response'
  }
  return 'ready'
}

function FlashMessageHandler({
  addMessage,
}: {
  addMessage: (message: QueryMessage) => Promise<Message>
}) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const hasProcessedFlash = useRef(false)

  useEffect(() => {
    if (hasProcessedFlash.current)
      return

    const flash = searchParams.get('f')
    if (!flash)
      return

    hasProcessedFlash.current = true

    router.replace(pathname, { scroll: false })
    addMessage(makeQueryMessage(decodeURIComponent(flash), false))
  }, [searchParams, router, pathname, addMessage])

  return null
}

function MessageListContainer({ messages, addMessage, isWaitingMessage, isInterrupted }: { messages: Message[], addMessage: (message: QueryMessage) => Promise<Message>, isWaitingMessage: boolean, isInterrupted: boolean }) {
  const messageEndAnchor = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (messageEndAnchor.current) {
      messageEndAnchor.current.scrollIntoView({
        behavior: 'smooth',
        block: 'end',
      })
    }
  }, [messages])

  return (
    <>
      <Suspense><FlashMessageHandler addMessage={addMessage} /></Suspense>
      {messages.length === 0
        ? (
          <EmptyConversationScreen onSubmit={addMessage} />
        )
        : (
            <section className="relative flex align-center">
              <div className="flex flex-col pt-16 w-6/7 md:w-2/3 xl:w-1/2 mx-auto max-w-6/7 md:max-w-2/3 xl:max-w-1/2 overflow-hidden break-all">
                <MessageList messages={messages} onMessage={addMessage} />
                {
                  isWaitingMessage
                    ? (
                      <div className="my-8">
                        <Loader
                          width={36}
                          height={36}
                        />
                      </div>

                    )
                    : null
                }
                <div ref={messageEndAnchor} className="h-32" />
                <div className="fixed bottom-0 left-0 right-0 w-full md:w-2/3 xl:w-1/2 mx-auto">
                  <div>
                    <PromptForm size="small" onSubmit={addMessage} status={computePromptFormStatus(isWaitingMessage, isInterrupted)} />
                    <div className="text-center w-full pt-1 bg-background pb-2">
                      <Disclaimer />
                    </div>
                  </div>
                </div>
              </div>
            </section>
        )}
    </>
  )
}

export function Chat() {
  const { messages, addMessage, isFetching, isPending, isInterrupted, isWaitingMessage, isEnabled } = useChat()

  if (isEnabled && (isFetching || isPending)) {
    return <LoadingScreen />
  }

  return (
    <MessageListContainer
      messages={messages}
      addMessage={addMessage}
      isWaitingMessage={isWaitingMessage}
      isInterrupted={isInterrupted}
    />
  )
}

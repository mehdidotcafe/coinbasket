'use client'
import type { UIMessage } from 'ai'
import type { OrderConfirmation } from './generative-ui/pricer/pricer'
import type { Authentication } from '@/authentication/authentication'
import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { Suspense, useCallback, useEffect, useMemo, useRef } from 'react'
import { useAuthentication } from '@/authentication/use-authentication'
import { Disclaimer } from '@/components/disclaimer'
import { EmptyConversationScreen } from '@/components/empty-conversation-screen'
import { LoadingScreen } from '@/components/screen/loading-screen'
import { Loader } from '@/loader'
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
  onSubmit,
}: {
  onSubmit: (text: string) => void
}) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const hasProcessedFlash = useRef(false)

  useEffect(() => {
    if (hasProcessedFlash.current)
      return

    const flash = searchParams.get('flash')
    if (!flash)
      return

    hasProcessedFlash.current = true

    router.replace(pathname, { scroll: false })
    onSubmit(decodeURIComponent(flash))
  }, [searchParams, router, pathname, onSubmit])

  return null
}

function MessageListContainer({ authentication, messages, onSubmit, onResume, isWaitingMessage, isInterrupted }: {
  authentication: Authentication
  messages: UIMessage[]
  onSubmit: (text: string) => void
  onResume: (result: OrderConfirmation) => void
  isWaitingMessage: boolean
  isInterrupted: boolean
}) {
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
      <Suspense><FlashMessageHandler onSubmit={onSubmit} /></Suspense>
      {
        authentication.authStatus === 'unauthenticated' || messages.length === 0
          ? (<EmptyConversationScreen onSubmit={onSubmit} />)
          : (
            <section className="relative flex align-center">
              <div className="flex flex-col pt-16 w-6/7 md:w-2/3 xl:w-1/2 mx-auto max-w-6/7 md:max-w-2/3 xl:max-w-1/2 overflow-hidden">
                <MessageList messages={messages} onResume={onResume} />
                {
                  isWaitingMessage
                    ? (
                      <div className="mb-4">
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
                    <PromptForm size="small" onSubmit={onSubmit} status={computePromptFormStatus(isWaitingMessage, isInterrupted)} hasMessageHistory={messages.length > 0} />
                    <div className="text-center w-full pt-1 bg-background pb-2">
                      <Disclaimer />
                    </div>
                  </div>
                </div>
              </div>
            </section>
          )
      }
    </>
  )
}

export function Chat() {
  const authentication = useAuthentication()
  const { messages, sendMessage, isFetching, isPending, isInterrupted, isWaitingMessage, isEnabled } = useChat()

  const handleSubmit = useCallback((text: string) => {
    sendMessage({ text })
  }, [sendMessage])

  const handleResume = useCallback((result: OrderConfirmation) => {
    const content = JSON.stringify({
      status: result.status,
      signable_order_id: result.signableOrderId,
      transaction_hash: result.transactionHash,
    })
    sendMessage({ text: content, metadata: { isResuming: true } }, { body: { is_resuming: true } })
  }, [sendMessage])

  if (isEnabled && (isFetching || isPending)) {
    return <LoadingScreen />
  }

  return (
    <MessageListContainer
      authentication={authentication}
      messages={messages}
      onSubmit={handleSubmit}
      onResume={handleResume}
      isWaitingMessage={isWaitingMessage}
      isInterrupted={isInterrupted}
    />
  )
}

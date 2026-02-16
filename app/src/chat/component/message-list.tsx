import type { UIMessage } from 'ai'
import type { OrderConfirmation } from './generative-ui/pricer/pricer'
import { MemoMessageBubble } from './message-bubble'

export interface Props {
  messages: UIMessage[]
  onResume?: (result: OrderConfirmation) => void
}

export function MessageList({
  messages,
  onResume,
}: Props) {
  return (
    <>
      {messages.map(message => (
        <div key={message.id}><MemoMessageBubble message={message} onResume={onResume} /></div>
      ))}
    </>
  )
}

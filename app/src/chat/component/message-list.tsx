import type { UIMessage } from 'ai'
import type { OrderConfirmation } from './generative-ui/pricer/pricer'
import { MessageBubble } from './message-bubble'

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
      {messages.map(message => {
        return message.parts.length > 0 ? (
          <MessageBubble message={message} onResume={onResume} key={message.id} />
        ) : null
      })}
    </>
  )
}

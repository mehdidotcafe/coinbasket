import type { Message } from '../message/Message'
import type { QueryMessage } from '../message/QueryMessage'
import { MessageBubble } from './message-bubble'

export interface Props {
  messages: Message[]
  onMessage?: (message: QueryMessage) => void
}

export function MessageList({
  messages,
  onMessage,
}: Props) {
  return (
    <>
      {messages.map(message => (
        <div className="my-8" key={message.id}>
          <MessageBubble message={message} onMessage={onMessage} />
        </div>
      ))}
    </>
  )
}

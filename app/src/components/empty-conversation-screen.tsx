import type { QueryMessage } from '@/chat/message/QueryMessage'
import { PromptForm } from '@/chat/component/prompt-form'
import { ScreenContainer } from './screen/screen-container'
import { ScreenTitle } from './screen/screen-title'
import { UserHeadingText } from './screen/user-heading-text'

interface Props {
  onSubmit: (message: QueryMessage) => void
}

export function EmptyConversationScreen({ onSubmit }: Props) {
  return (
    <ScreenContainer>
      <ScreenTitle>
        <UserHeadingText />
        <br />
        {' '}
        How can I help?
      </ScreenTitle>
      <div className="w-full md:w-2/3 lg:w-5/6 mx-auto">
        <PromptForm size="large" onSubmit={onSubmit} status="ready" />
      </div>
    </ScreenContainer>
  )
}

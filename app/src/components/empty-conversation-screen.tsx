import { HeroPromptForm } from '@/chat/component/hero-prompt-form'
import { ScreenContainer } from './screen/screen-container'
import { ScreenTitle } from './screen/screen-title'
import { UserHeadingText } from './screen/user-heading-text'

interface Props {
  onSubmit?: (text: string) => void
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
      <HeroPromptForm
        size="large"
        onSubmit={onSubmit}
      />
    </ScreenContainer>
  )
}

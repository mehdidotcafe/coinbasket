'use client'

import type { Props } from './prompt-form'
import { useTypingPlaceholder } from '@/app/landing/use-typing-placeholder'
import precraftPrompts from '../precraft-prompts'
import { PromptForm } from './prompt-form'

export function HeroPromptForm({
  size,
  onSubmit,
}: Pick<Props, 'size'> & { onSubmit?: Props['onSubmit'] }) {
  const placeholder = useTypingPlaceholder({
    placeholders: precraftPrompts.flatMap(group => group.prompts),
  })

  return (
    <div className="[&>*]:text-2xl min-w-[33vw] max-w-[800px]">
      <PromptForm
        status="ready"
        size={size}
        placeholder={placeholder}
        onSubmit={onSubmit}
      />
    </div>
  )
}

'use client'

import type { Props } from './prompt-form'
import { useTypingPlaceholder } from '@/app/landing/use-typing-placeholder'
import { PromptForm } from './prompt-form'

export function HeroPromptForm({
  size,
  onSubmit,
}: Pick<Props, 'size'> & { onSubmit?: Props['onSubmit'] }) {
  const placeholder = useTypingPlaceholder({
    placeholders: [
      'Buy 0.1 BTC',
      'Sell all my tokens and baskets',
      'Swap half of my ETH to DOGE',
      'Buy 1 share of the CMC20 basket',
      'Show my global portfolio in dollars',
    ],
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

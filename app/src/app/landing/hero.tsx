'use client'

import { useRouter } from 'next/navigation'
import { PromptForm } from '@/chat/component/prompt-form'
import { useTypingPlaceholder } from './use-typing-placeholder'

export function Hero() {
  const router = useRouter()

  const placeholder = useTypingPlaceholder({
    placeholders: [
      'Buy 0.1 BTC',
      'Sell all my assets',
      'Swap half of my ETH to DOGE',
      'Buy 1 share of the CMC20 basket',
      'Show me my global portfolio in dollars',
    ],
  })

  return (
    <section className="items-center flex flex-col px-8 md:px-24 xl:px-64 2xl:px-96 mb-48">
      <h1 className="text-6xl mt-32 md:mt-64 font-sofia-sans mb-8 text-center">
        AI-Powered Crypto Orders
        <br />
        One Prompt Away
      </h1>
      <div className="[&>*]:text-2xl min-w-[33vw]">
        <PromptForm status="ready" size="large" placeholder={placeholder} onSubmit={msg => router.push(`/c?f=${encodeURIComponent(msg.content as string)}`)} />
      </div>
    </section>
  )
}

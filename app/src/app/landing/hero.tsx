import { HeroPromptForm } from '@/chat/component/hero-prompt-form'

export function Hero() {
  return (
    <section className="items-center flex flex-col px-8 md:px-24 xl:px-64 2xl:px-96 mb-48">
      <h1 className="text-6xl mt-32 md:mt-64 font-sofia-sans mb-8 text-center">
        AI-Powered Crypto Orders
        <br />
        One Prompt Away
      </h1>
      <HeroPromptForm size="large" />
    </section>
  )
}

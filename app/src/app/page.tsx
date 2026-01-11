import { Card, CardContent } from '@/components/ui/card'
import { Footer } from './landing/footer'
import { Hero } from './landing/hero'
import { ChainSection } from './landing/section/chain-section'
import { FeeSection } from './landing/section/fee-section'
import { OverviewSection } from './landing/section/overview-section'
import { PrivacySection } from './landing/section/privacy-section'

export default function MainPage() {
  return (
    <>
      <main className="min-h-screen pt-16 flex flex-col w-full">
        <Hero />
        <Card className="rounded-t-[32px] md:rounded-t-[64px] rounded-b-none pb-0">
          <CardContent className="p-0">
            <OverviewSection />
            <PrivacySection />
            <FeeSection />
            <ChainSection />
          </CardContent>
        </Card>
      </main>
      <Footer />
    </>
  )
}

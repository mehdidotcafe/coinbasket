/* eslint-disable node/prefer-global/process */
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { MetricCard } from '../metric-card'

export function Coinbasket() {
  return (
    <span className="font-extrabold">
      coin
      <span className="text-secondary">basket</span>
    </span>
  )
}

export function PrivacySection() {
  return (
    <section className="min-h-128 bg-tertiary py-16 px-8 md:px-24 xl:px-64 2xl:px-96 max-w-screen overflow-x-hidden">
      <h2 className="text-6xl font-sofia-sans mb-1">Trade Freely. No Accounts. No KYC.</h2>
      <h3 className="text-2xl font-sofia-sans mb-16">
        An open-source, non-custodial DEX and Portfolio manager.
        <br />
        Just connect your wallet and trade.
      </h3>
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <MetricCard value="0" descriptions={['Sign-Ups', 'KYC']} />
        <MetricCard value="100%" descriptions={['Open Source']} />
        <div></div>
        <div>
          <Button asChild variant="outline" className="text-md md:text-2xl" size="lg" id="3">
            <a href={process.env.NEXT_PUBLIC_GITHUB_URL!} rel="noopener noreferrer" target="_blank">
              Star
              <Coinbasket />
              {' '}
              on GitHub
              <Image
                src="/github.svg"
                alt="GitHub logo"
                width={24}
                height={24}
                className="inline ml-1"
              />
            </a>
          </Button>
        </div>
      </div>
    </section>
  )
}

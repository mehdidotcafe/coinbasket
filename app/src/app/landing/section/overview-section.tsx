import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export function OverviewSection() {
  return (
    <section className="min-h-128 py-16 px-8 md:px-24 xl:px-64 2xl:px-96">
      <h2 className="text-6xl font-sofia-sans mb-1">From Prompt to On-Chain Action</h2>
      <Tabs defaultValue="overview" className="text-2xl">
        <TabsList className="mb-8">
          <TabsTrigger value="overview" className="text-2xl">Overview</TabsTrigger>
          <TabsTrigger value="dex" className="text-2xl">DEX</TabsTrigger>
          <TabsTrigger value="portfolio" className="text-2xl">Portfolio</TabsTrigger>
        </TabsList>
        <TabsContent value="overview">
          Coinbasket is an AI-powered, non-custodial Web3 trading and portfolio platform that turns natural language into on-chain actions. Powered by large language models, Coinbasket understands what you want to do, whether it is
          {' '}
          <i>“Swap half my ETH for DOGE”</i>
          ,
          {' '}
          <i>“Invest in the CMC20 basket”</i>
          {' '}
          or
          {' '}
          <i>“What's my portfolio worth in dollars?”</i>
          {' '}
          and executes it instantly. There are no accounts, no KYC, and no platform fees. Just connect your wallet on BNB Chain and trade freely through an open-source, fully automated experience.
        </TabsContent>
        <TabsContent value="dex">
          At its core, Coinbasket functions as a next-generation DEX where prompts replace complex interfaces. You can place orders across more than 3,000 tokens, swap assets, or invest in carefully cherry-picked baskets backed by Reserve DTF structures. Smart routing finds the most efficient execution path across multiple liquidity sources, ensuring optimal pricing without hidden costs. From single-token swaps to diversified thematic baskets like AI, DeFi, or stablecoins, Coinbasket makes advanced DeFi trading simple and intuitive.
        </TabsContent>
        <TabsContent value="portfolio">
          Coinbasket also acts as an intelligent portfolio reader, giving you real-time insights through simple questions. Ask
          {' '}
          <i>“How much BNB do I hold?”</i>
          ,
          {' '}
          <i>“Give me Bitcoin price”</i>
          {' '}
          or
          {' '}
          <i>“What's my global portfolio value in dollars?”</i>
          {' '}
          and get instant answers. Track token and basket prices, monitor holdings, and understand your exposure without dashboards or manual calculations. Your portfolio becomes conversational, clear, transparent, and always under your control.
        </TabsContent>
      </Tabs>
    </section>
  )
}

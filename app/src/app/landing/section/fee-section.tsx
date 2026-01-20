import { MetricCard } from '../metric-card'

export function Coinbasket() {
  return (
    <span className="font-extrabold">
      coin
      <span className="text-secondary">basket</span>
    </span>
  )
}

export function FeeSection() {
  return (
    <section className="min-h-128 py-16 px-8 md:px-24 xl:px-64 2xl:px-96">
      <h2 className="text-6xl font-sofia-sans mb-16">Pay Less. Trade Smarter.</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-16">
        <MetricCard value="0" descriptions={[<h2 className="text-md md:text-4xl xl:text-6xl font-sofia-sans">Platform fees</h2>]} />
        <ul className="flex flex-col justify-end gap-2 text-4xl mb-[36px]" id="2">
          <li className="mb-16">
            <h3 className="text-4xl font-sofia-sans">
              No Platform Fees
            </h3>
            <span className="text-2xl">We don't charge on your trades.</span>
          </li>
          <li>
            <h3 className="text-4xl font-sofia-sans">
              Smart Routing
            </h3>
            <span className="text-2xl">Finds the most efficient execution path across liquidity sources.</span>
          </li>
        </ul>
      </div>
    </section>
  )
}

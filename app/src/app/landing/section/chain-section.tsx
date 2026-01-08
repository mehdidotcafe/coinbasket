import Image from 'next/image'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'

export function Coinbasket() {
  return (
    <span className="font-extrabold">
      coin
      <span className="text-secondary">basket</span>
    </span>
  )
}

export function ChainSection() {
  return (
    <section className="min-h-128 py-16 px-8 md:px-24 xl:px-64 2xl:px-96 bg-tertiary">
      <h2 className="text-6xl font-sofia-sans mb-16">Live on BNB Chain</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="flex flex-row items-end gap-2" id="1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Image
                src="/bnb.svg"
                alt="BNB Chain logo"
                width={200}
                height={200}
                className="inline"
              />
            </TooltipTrigger>
            <TooltipContent>
              <p className="text-xl">Live now on BNB Chain</p>
            </TooltipContent>
          </Tooltip>
        </div>
        <div className="flex flex-row items-end gap-2 justify-center" id="2">
          <Tooltip>
            <TooltipTrigger asChild>
              <Image
                className="rounded-full bg-white inline grayscale opacity-50 cursor-not-allowed"
                src="/ethereum.png"
                alt="Ethereum logo"
                width={200}
                height={200}
              />
            </TooltipTrigger>
            <TooltipContent>
              <p className="text-xl">Ethereum - coming soon</p>
            </TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Image
                className="rounded-full bg-white inline grayscale opacity-50 cursor-not-allowed ml-8"
                src="/arbitrum.png"
                alt="Arbitrum logo"
                width={200}
                height={200}
              />
            </TooltipTrigger>
            <TooltipContent>
              <p className="text-xl">Arbitrum - coming soon</p>
            </TooltipContent>
          </Tooltip>
        </div>

      </div>
    </section>
  )
}

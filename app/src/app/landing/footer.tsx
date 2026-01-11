/* eslint-disable node/prefer-global/process */
import Image from 'next/image'
import { HeroPromptForm } from '@/chat/component/hero-prompt-form'

export function Footer() {
  return (
    <footer className="bg-primary">
      <div className="border-y py-8  md:px-24  px-8  xl:px-64 2xl:px-96">
        <h3 className="text-4xl font-sofia-sans mb-4">
          Try a prompt now
        </h3>
        <div className="[&>*]:text-2xl min-w-[33vw] max-w-[800px]">
          <HeroPromptForm size="small" />
        </div>
      </div>
      <div className="px-8 md:px-24 xl:px-64 2xl:px-96 flex flex-col pb-4 pt-8">
        <div className="grid grid-cols-2 grid-rows-5 gap-1">
          <div className="col-start-1 row-start-1 font-extrabold mb-1">
            Links
          </div>
          <a href={process.env.NEXT_PUBLIC_APP_LIVE_URL!} target="_blank" rel="noopener noreferrer" className="opacity-75 col-start-1 row-start-2">
            Coinbasket App
          </a>
          <a href={process.env.NEXT_PUBLIC_APP_DEMO_URL!} target="_blank" rel="noopener noreferrer" className="opacity-75 col-start-1 row-start-3">
            Coinbasket Live Demo
          </a>
          <a href={process.env.NEXT_PUBLIC_GITHUB_URL!} target="_blank" rel="noopener noreferrer" className="opacity-75 col-start-1 row-start-4">
            Github
          </a>
          <a href={process.env.NEXT_PUBLIC_X_URL!} target="_blank" rel="noopener noreferrer" className="opacity-75 col-start-1 row-start-5">
            X
          </a>
          <div className="col-start-2 row-start-1 font-extrabold mb-1">
            Partners
          </div>
          <div className="col-start-2 row-start-2">
            <a href={process.env.NEXT_PUBLIC_0X_PROTOCOL_URL!} target="_blank" rel="noopener noreferrer" className="opacity-75">
              0x Protocol
            </a>
          </div>

          <div className="col-start-2 row-start-3">
            <a href={process.env.NEXT_PUBLIC_BNB_CHAIN_URL!} target="_blank" rel="noopener noreferrer" className="opacity-75">
              BNB Chain
            </a>
          </div>
          <div className="col-start-2 row-start-4">
            <a href={process.env.NEXT_PUBLIC_MEHDIDOTCAFE_URL!} target="_blank" rel="noopener noreferrer" className="opacity-75">
              mehdidotcafe
            </a>
          </div>
        </div>

        <div className="flex mt-auto pt-4 items-end">
          © 2026 coinbasket. All rights reserved.
          <div className="ml-auto grid grid-flow-col gap-4">
            <a href={process.env.NEXT_PUBLIC_GITHUB_URL!} target="_blank" rel="noopener noreferrer" className="hover:brightness-125 transition-all duration-300">
              <Image src="/github.svg" alt="GitHub logo" width={32} height={32} />
            </a>
            <a href={process.env.NEXT_PUBLIC_X_URL!} target="_blank" rel="noopener noreferrer" className="hover:brightness-125 transition-all duration-300">
              <Image src="/x.svg" alt="X logo" width={32} height={32} />
            </a>
            <a href={process.env.NEXT_PUBLIC_MEHDIDOTCAFE_URL!} target="_blank" rel="noopener noreferrer" className="hover:brightness-125 transition-all duration-300">
              <Image src="/mehdidotcafe.svg" alt="mehdidotcafe logo" width={32} height={32} />
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}

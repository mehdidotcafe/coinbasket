'use client'

import type { Theme } from '@rainbow-me/rainbowkit'
import { ConnectButton, darkTheme, RainbowKitProvider } from '@rainbow-me/rainbowkit'
import merge from 'lodash.merge'
import Image from 'next/image'

export const theme = merge(darkTheme(), {
  colors: {
    accentColor: 'var(--secondary)',
    accentColorForeground: 'var(--primary-foreground)',
    modalBackground: 'var(--primary)',
    connectButtonText: 'var(--primary-foreground)',
    connectButtonInnerBackground: 'var(--primary)',
    generalBorder: '0',
    profileActionHover: 'none',
    connectButtonBackground: 'var(--secondary)',
  },
  radii: {
    connectButton: 'var(--radius)',
  },
} as Theme)

function CoinbasketLogo() {
  return (
    <Image
      src="/logo/coinbasket.svg"
      alt="coinbasket logo"
      width={48}
      height={48}
    />
  )
}

export function Coinbasket() {
  return (
    <span className="font-extrabold text-xl ml-2">
      coin
      <span className="text-secondary">basket</span>
    </span>
  )
}

export function Header() {
  return (
    <header className="fixed flex items-center h-16 md:h-auto p-1 md:p-4 top-0 left-0 right-0 z-2 align-center bg-primary md:bg-inherit border-b md:border-b-0 px-4 md:px-16">
      <CoinbasketLogo />
      <Coinbasket />
      <div className="ml-auto">
        <RainbowKitProvider locale="en-US" theme={theme}>
          <ConnectButton showBalance={{ smallScreen: false, largeScreen: false }} accountStatus="address" chainStatus="icon" />
        </RainbowKitProvider>
      </div>
    </header>
  )
}

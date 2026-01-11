/* eslint-disable node/prefer-global/process */
'use client'

import type { Theme } from '@rainbow-me/rainbowkit'
import type { Registry } from './registry/Registry'
import { darkTheme, getDefaultConfig, RainbowKitProvider } from '@rainbow-me/rainbowkit'
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister'
import { QueryClient } from '@tanstack/react-query'
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client'
import merge from 'lodash.merge'
import { http } from 'viem'
import { bsc } from 'viem/chains'
import { WagmiProvider } from 'wagmi'
import { AuthenticationProvider } from '@/authentication/authentication-provider'
import { demoSiweClient } from '@/authentication/infrastructure/demo-siwe-client'
import { httpSiweClient } from '@/authentication/infrastructure/http-siwe-client'
import { TooltipProvider } from '@/components/ui/tooltip'
import { demoApiClient } from './api/infrastructure/demo-api-client'
import { httpApiClient } from './api/infrastructure/http-api-client'
import { demoChatClient } from './chat/client/infrastructure/demo-chat-client'
import { httpChatClient } from './chat/client/infrastructure/http-chat-client'
import { Toaster } from './components/ui/sonner'
import { EnvProvider } from './env/env-provider'
import { useMode } from './mode/use-mode'
import { demoPricerClient } from './price/client/infrastructure/demo-pricer-client'
import { httpPricerClient } from './price/client/infrastructure/http-pricer-client'
import { PromptInputProvider } from './prompt-input/prompt-input-context'
import { RegistryProvider } from './registry/registry-provider'
import { idbStorage } from './storage/infrastructure/idb-storage'
import '@rainbow-me/rainbowkit/styles.css'

const API_URL = process.env.NEXT_PUBLIC_API_URL!

export const wagmiConfig = getDefaultConfig({
  appName: process.env.NEXT_PUBLIC_APP_NAME!,
  projectId: process.env.NEXT_PUBLIC_APP_NAME!,
  chains: [bsc],
  ssr: true,
  transports: {
    [bsc.id]: http(process.env.NEXT_PUBLIC_BSC_RPC_URL),
  },
})

const liveRegistry: Registry = {
  apiClient: httpApiClient(API_URL),
  chatClient: httpChatClient(API_URL),
  pricerClient: httpPricerClient(API_URL),
  siweClient: httpSiweClient(API_URL),
}

const demoRegistry: Registry = {
  apiClient: demoApiClient,
  chatClient: demoChatClient,
  pricerClient: demoPricerClient,
  siweClient: demoSiweClient,
}

const rawEnv = {
  'PORTFOLIO_TOKEN_NAME': process.env.NEXT_PUBLIC_PORTFOLIO_TOKEN_NAME,
  'PORTFOLIO_TOKEN_DISPLAY_NAME': process.env.NEXT_PUBLIC_PORTFOLIO_TOKEN_DISPLAY_NAME,
  'PORTFOLIO_TOKEN_TICKER': process.env.NEXT_PUBLIC_PORTFOLIO_TOKEN_TICKER,
  'PORTFOLIO_TOKEN_SYMBOL': process.env.NEXT_PUBLIC_PORTFOLIO_TOKEN_SYMBOL,
  'PORTFOLIO_TOKEN_ID': process.env.NEXT_PUBLIC_PORTFOLIO_TOKEN_ID,
  'PORTFOLIO_TOKEN_ADDRESS': process.env.NEXT_PUBLIC_PORTFOLIO_TOKEN_ADDRESS,
  'PORTFOLIO_TOKEN_DECIMALS': process.env.NEXT_PUBLIC_PORTFOLIO_TOKEN_DECIMALS,
  'APP_MODE': process.env.NEXT_PUBLIC_APP_MODE,
  'APP_LIVE_URL': process.env.NEXT_PUBLIC_APP_LIVE_URL,
  'APP_DEMO_URL': process.env.NEXT_PUBLIC_APP_DEMO_URL,
  'API_URL': process.env.NEXT_PUBLIC_API_URL,
  'REPOSITORY_URL': process.env.NEXT_PUBLIC_REPOSITORY_URL!,
  'CACHE_VERSION': process.env.NEXT_PUBLIC_CACHE_VERSION!,
  'BSC_RPC_URL': process.env.NEXT_PUBLIC_BSC_RPC_URL!,
  '0X_PROTOCOL_URL': process.env.NEXT_PUBLIC_0X_PROTOCOL_URL!,
  'GITHUB_URL': process.env.NEXT_PUBLIC_GITHUB_URL!,
  'X_URL': process.env.NEXT_PUBLIC_X_URL!,
  'BNB_CHAIN_URL': process.env.NEXT_PUBLIC_BNB_CHAIN_URL!,
  'MEHDIDOTCAFE_URL': process.env.NEXT_PUBLIC_MEHDIDOTCAFE_URL!,
}

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
    modalBorder: 'var(--border)',
  },
  radii: {
    connectButton: 'var(--radius)',
  },
} as Theme)

const queryClient = new QueryClient()

function NestedProviders({ children }: { children: React.ReactNode }) {
  const { mode } = useMode()

  return (
    <WagmiProvider config={wagmiConfig}>
      <PersistQueryClientProvider
        client={queryClient}
        persistOptions={{
          persister: createAsyncStoragePersister({
            storage: idbStorage(mode),
          }),
          buster: `${process.env.NEXT_PUBLIC_APP_NAME!}:${process.env.NEXT_PUBLIC_APP_MODE!}:${process.env.NEXT_PUBLIC_CACHE_VERSION!}`,
        }}
      >
        <RegistryProvider registry={mode === 'demo' ? demoRegistry : liveRegistry}>
          <AuthenticationProvider>
            <TooltipProvider>
              <RainbowKitProvider locale="en-US" theme={theme}>
                <PromptInputProvider>
                  {children}
                </PromptInputProvider>
              </RainbowKitProvider>
            </TooltipProvider>
          </AuthenticationProvider>
        </RegistryProvider>
      </PersistQueryClientProvider>
    </WagmiProvider>
  )
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <EnvProvider env={rawEnv}>
      <NestedProviders>
        {children}
      </NestedProviders>
      <Toaster position="top-right" />
    </EnvProvider>
  )
}

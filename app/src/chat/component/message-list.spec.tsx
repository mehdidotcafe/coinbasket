import type { UIMessage } from '@ai-sdk/react'
import type { Props } from './message-list'
import { getDefaultConfig } from '@rainbow-me/rainbowkit'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import { bsc, mainnet } from 'viem/chains'
import { expect, it } from 'vitest'
import { WagmiProvider } from 'wagmi'
import { MessageList } from './message-list'

const queryClient = new QueryClient()

function renderComponent(props: Props) {
  return render(
    <WagmiProvider config={getDefaultConfig({
      appName: 'test',
      projectId: 'test',
      chains: [bsc, mainnet],
      ssr: true,
    })}
    >
      <QueryClientProvider client={queryClient}>
        <MessageList {...props} />
      </QueryClientProvider>
    </WagmiProvider>,
  )
}

it('should render a message list', () => {
  const messages: UIMessage[] = [
    { id: '1', role: 'user', parts: [{ type: 'text', text: 'Hello' }], metadata: { createdAt: new Date('2020-01-01') } },
    { id: '2', role: 'assistant', parts: [{ type: 'text', text: 'Hi there!' }], metadata: { createdAt: new Date('2020-01-01') } },
  ]

  const { getAllByRole } = renderComponent({ messages })

  expect(getAllByRole('article')).toHaveLength(2)
})

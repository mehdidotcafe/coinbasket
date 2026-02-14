import type { Meta, StoryObj } from '@storybook/react'
import Big from 'big.js'
import { bnbToken, btcToken, ethToken, usdtToken } from '@/asset/fixture/token'
import { AssetPriceCard } from './asset-price-card'

const meta = {
  component: AssetPriceCard,
} satisfies Meta<typeof AssetPriceCard>

export default meta

type Story = StoryObj<typeof meta>

export const Bitcoin: Story = {
  args: {
    sellBalance: {
      asset: btcToken,
      amount: Big('1'),
    },
    buyBalance: {
      asset: usdtToken,
      amount: Big('1.5432'),
    },
  },
}

export const Ethereum: Story = {
  args: {
    sellBalance: {
      asset: ethToken,
      amount: Big('1'),
    },
    buyBalance: {
      asset: usdtToken,
      amount: Big('3000.5432'),
    },
  },
}

export const BNB: Story = {
  args: {
    sellBalance: {
      asset: bnbToken,
      amount: Big('1'),
    },
    buyBalance: {
      asset: usdtToken,
      amount: Big('653.3494'),
    },
  },
}

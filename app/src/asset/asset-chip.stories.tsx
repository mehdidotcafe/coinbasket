import type { Meta, StoryObj } from '@storybook/react'
import { AssetChip } from './asset-chip'
import { aiBasket } from './fixture/basket'
import { btcToken } from './fixture/token'

const meta = {
  component: AssetChip,
} satisfies Meta<typeof AssetChip>

export default meta

type Story = StoryObj<typeof meta>

export const WithToken: Story = {
  args: {
    asset: btcToken,
  },
}

export const WithBasket: Story = {
  args: {
    asset: aiBasket,
  },
}

export const WithoutLogo: Story = {
  args: {
    asset: { ...btcToken, logoUri: undefined, name: 'Unknown Token', displayName: 'Unknown Token', ticker: 'UNK' },
  },
}

'use client'

import type { Meta, StoryObj } from '@storybook/react'
import Big from 'big.js'
import { bnbToken, btcToken } from '@/asset/fixture/token'
import { Providers } from '@/providers'
import { Pricer } from './pricer'

const meta = {
  component: Pricer,
  decorators: [
    Story => (
      <Providers>
        <Story />
      </Providers>
    ),
  ],
} satisfies Meta<typeof Pricer>

export default meta

type Story = StoryObj<typeof meta>

export const BuyTokenWithSellToken: Story = {
  args: {
    plannedOrder: {
      id: 'order-1',
      buyAssetWithAmount: {
        asset: btcToken,
        amount: Big('10.1282'),
        availableAmount: Big('5.1283'),
      },
      sellAssetWithAmount: {
        asset: bnbToken,
        amount: Big('52.28349'),
        availableAmount: Big('90.48534'),
      },
      fees: {
        gasFee: {
          amount: Big('0.0005'),
          asset: bnbToken,
          amountAtomic: BigInt(50000),
        },
        providerFee: {
          amount: Big('0.25'),
          asset: btcToken,
          amountAtomic: BigInt(25000000),
        },
        platformFee: {
          amount: Big('1.5'),
          asset: btcToken,
          amountAtomic: BigInt(150000000),
        },
      },
    },
    onSubmit: async (_result) => {
      return new Promise<void>((resolve) => {
        setTimeout(() => {
          resolve()
        }, 2000)
      })
    },
  },
}

export const BuyTokenWithSellTokenErrorSubmitting: Story = {
  args: {
    plannedOrder: {
      id: 'order-1',
      buyAssetWithAmount: {
        asset: btcToken,
        amount: Big('10.1282'),
        availableAmount: Big('5.1283'),
      },
      sellAssetWithAmount: {
        asset: bnbToken,
        amount: Big('52.28349'),
        availableAmount: Big('90.48534'),
      },
      fees: {
        gasFee: {
          amount: Big('0.0005'),
          asset: bnbToken,
          amountAtomic: BigInt(50000),
        },
        providerFee: {
          amount: Big('0.25'),
          asset: btcToken,
          amountAtomic: BigInt(25000000),
        },
        platformFee: {
          amount: Big('1.5'),
          asset: btcToken,
          amountAtomic: BigInt(150000000),
        },
      },
    },
    onSubmit: () => {
      return new Promise((_resolve, reject) => {
        setTimeout(() => {
          reject(new Error('Something went wrong with the API'))
        }, 2000)
      })
    },
  },
}

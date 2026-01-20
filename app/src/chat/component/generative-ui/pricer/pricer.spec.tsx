import type { Props } from './pricer'
import type { Registry } from '@/registry/Registry'
import { setTimeout } from 'node:timers/promises'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Big from 'big.js'
import { afterAll, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest'
import { WagmiProvider } from 'wagmi'
import { aiBasket } from '@/asset/fixture/basket'
import { bnbToken, ethToken, solToken, usdtToken } from '@/asset/fixture/token'
import { wagmiConfig } from '@/providers'
import { RegistryProvider } from '@/registry/registry-provider'
import { Pricer } from './pricer'

// TODO: Use registry to mock
// Mock Wagmi hooks
vi.mock('wagmi', async () => {
  const actual = await vi.importActual('wagmi')

  return {
    ...actual,
    useAccount: vi.fn(() => ({
      address: '0x1234567890123456789012345678901234567890',
      isConnected: true,
    })),
    useSignTypedData: vi.fn(() => ({
      signTypedData: vi.fn(),
      data: undefined,
      isPending: false,
      error: null,
    })),
    useWaitForTransactionReceipt: vi.fn((config: any) => {
      const hasHash = !!config?.hash
      // Simulate transaction confirmation when hash is present
      // Return isConfirming briefly, then isConfirmed
      return {
        isLoading: hasHash, // This triggers isConfirming state
        isSuccess: hasHash, // This triggers isConfirmed state
        error: null,
      }
    }),
    useWalletClient: vi.fn(() => ({
      data: {
        sendTransaction: vi.fn(async () => '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890'),
      },
    })),
  }
})

const registry: Pick<Registry, 'pricerClient' | 'apiClient'> = {
  pricerClient: {
    getPrice: vi.fn().mockImplementation(async ({ buyAsset, sellAsset, sellAssetAmount }) => {
      const fees = {
        platformFee: {
          asset: ethToken,
          amount: Big('0.2'),
          amountAtomic: BigInt('200000000000000000'),
          decimals: ethToken.decimals,
        },
        providerFee: {
          asset: solToken,
          amount: Big('0.00018'),
          amountAtomic: BigInt('180000000000000'),
          decimals: solToken.decimals,
        },
        gasFee: {
          asset: bnbToken,
          amount: Big('0.00042'),
          amountAtomic: BigInt('420000000000000'),
          decimals: bnbToken.decimals,
        },
      }

      if (buyAsset.ticker === 'ETH' && sellAsset.ticker === 'BNB') {
        return {
          buyBalance: {
            asset: ethToken,
            amount: Big('75'),
          },
          sellBalance: {
            asset: bnbToken,
            amount: sellAssetAmount,
          },
          fees,
        }
      }

      if (buyAsset.ticker === 'BNB' && sellAsset.ticker === 'ETH') {
        return {
          sellBalance: {
            asset: ethToken,
            amount: sellAssetAmount,
          },
          buyBalance: {
            asset: bnbToken,
            amount: Big(90),
          },
          fees,
        }
      }

      if (buyAsset.ticker === 'SOL' && sellAsset.ticker === 'USDT') {
        await setTimeout(20000)

        return {
          buyBalance: {
            asset: solToken,
            amount: Big('0.5'),
          },
          sellBalance: {
            asset: usdtToken,
            amount: sellAssetAmount,
          },
          fees,
        }
      }

      return {
        sellBalance: {
          asset: sellAsset,
          amount: sellAssetAmount,
        },
        buyBalance: {
          asset: buyAsset,
          amount: Big('0'),
        },
        fees,
      }
    }),
  },
  apiClient: {
    getSignableOrder: vi.fn().mockResolvedValue({
      id: '1',
      transaction: {
        toAddress: '0x1234567890123456789012345678901234567890',
        data: '0xabcd',
        amount: BigInt(0),
        gas: {
          gas: BigInt(21000),
          gas_price: BigInt(1000000000),
        },
      },
      signaturePayload: null,
    }),
  } as any,
}

const queryClient = new QueryClient()

function renderComponent(props: Props) {
  return render(
    <WagmiProvider config={wagmiConfig}>
      <QueryClientProvider client={queryClient}>
        <RegistryProvider registry={registry as Registry}>
          <Pricer {...props} />
        </RegistryProvider>
      </QueryClientProvider>
    </WagmiProvider>,
  )
}

beforeEach(() => {
  registry.pricerClient.getPrice.mockClear()
})

it('should render', () => {
  const { container } = renderComponent({
    plannedOrder: {
      id: 'planned-order-1',
      buyAssetWithAmount: {
        asset: aiBasket,
        amount: Big(0),
        availableAmount: Big(0),
      },
      sellAssetWithAmount: {
        asset: bnbToken,
        amount: Big(0),
        availableAmount: Big(0),
      },
    },
  })

  expect(container).toBeDefined()
})

describe('validation', () => {
  it('should render disabled swap button when buy amount is not provided', async () => {
    const { getByRole, getByLabelText } = renderComponent({
      plannedOrder: {
        id: 'planned-order-1',
        buyAssetWithAmount: {
          asset: aiBasket,
          amount: undefined,
          availableAmount: Big(0),
        },
        sellAssetWithAmount: {
          asset: bnbToken,
          amount: Big(5),
          availableAmount: Big(10),
        },
      },
    })

    const sellAssetInput = getByLabelText('Sell') as HTMLInputElement

    await userEvent.clear(sellAssetInput)

    const swapButton = getByRole('button', { name: /sell/i }) as HTMLButtonElement

    expect(swapButton).to.have.property('disabled', true)
  })

  it('should render disabled swap button when sell amount is not provided', async () => {
    const { getByRole, getByLabelText } = renderComponent({
      plannedOrder: {
        id: 'planned-order-1',
        buyAssetWithAmount: {
          asset: aiBasket,
          amount: Big(10),
          availableAmount: Big(20),
        },
        sellAssetWithAmount: {
          asset: bnbToken,
          amount: undefined,
          availableAmount: Big(0),
        },
      },
    })

    const sellAssetInput = getByLabelText('Sell') as HTMLInputElement

    await userEvent.clear(sellAssetInput)

    const swapButton = getByRole('button', { name: /buy/i }) as HTMLButtonElement

    expect(swapButton).to.have.property('disabled', true)
  })

  it('should render disabled swap button when user cleans an amount input', async () => {
    const { getByLabelText, getByRole } = renderComponent({
      plannedOrder: {
        id: 'planned-order-1',
        buyAssetWithAmount: {
          asset: aiBasket,
          amount: Big('10'),
          availableAmount: Big('20'),
        },
        sellAssetWithAmount: {
          asset: bnbToken,
          amount: Big('5'),
          availableAmount: Big('10'),
        },
      },
    })

    const sellAssetInput = getByLabelText('Sell') as HTMLInputElement

    await userEvent.clear(sellAssetInput)

    await waitFor(() => {
      const swapButton = getByRole('button', { name: /confirm/i }) as HTMLButtonElement
      expect(swapButton).to.have.property('disabled', true)
    })
  })
})

describe('amount inputs', () => {
  it('should render sell and buy asset inputs for each step', () => {
    const { getByLabelText } = renderComponent({
      plannedOrder: {
        id: 'planned-order-1',
        buyAssetWithAmount: {
          asset: aiBasket,
          amount: Big(10),
          availableAmount: Big(20),
        },
        sellAssetWithAmount: {
          asset: bnbToken,
          amount: Big(5),
          availableAmount: Big(10),
        },
      },
    })

    const sellAssetInput = getByLabelText('Sell') as HTMLInputElement
    const buyAssetInput = getByLabelText('Buy') as HTMLInputElement

    expect(sellAssetInput.value).to.equal('5')
    expect(buyAssetInput.value).to.equal('10')
  })

  describe('when updating an input', () => {
    const plannedOrder = {
      id: 'planned-order-1',
      buyAssetWithAmount: {
        asset: ethToken,
        amount: Big(10),
        availableAmount: Big(20),
      },
      sellAssetWithAmount: {
        asset: bnbToken,
        amount: Big(5),
        availableAmount: Big(10),
      },
    }

    it('should call pricer client only once when SELL input is typed several times in a row', async () => {
      const { getByLabelText } = renderComponent({
        plannedOrder,
      })

      const sellAssetInput = getByLabelText('Sell') as HTMLInputElement

      await userEvent.clear(sellAssetInput)
      await userEvent.type(sellAssetInput, '20')
      await userEvent.type(sellAssetInput, '.3883')

      await waitFor(() => {
        expect(registry.pricerClient.getPrice).toHaveBeenCalledOnce()
      })
    })

    it('should update both input values and call pricer client when SELL asset is changed', async () => {
      const { getByLabelText } = renderComponent({
        plannedOrder,
      })

      const sellAssetInput = getByLabelText('Sell') as HTMLInputElement

      await userEvent.clear(sellAssetInput)
      await userEvent.type(sellAssetInput, '20.3883')

      await waitFor(() => {
        expect(sellAssetInput.value).to.equal('20.3883')
        const buyAssetInput = getByLabelText('Buy') as HTMLInputElement
        expect(buyAssetInput.value).to.equal('75')
      })
    })

    it('should display loader when fetching price after manual input', async () => {
      const { getByLabelText, getByRole } = renderComponent({
        plannedOrder: {
          id: 'planned-order-1',
          buyAssetWithAmount: {
            asset: solToken,
            amount: Big(10),
            availableAmount: Big(20),
          },
          sellAssetWithAmount: {
            asset: usdtToken,
            amount: Big(5),
            availableAmount: Big(10),
          },
        },
      })

      const sellAssetInput = getByLabelText('Sell') as HTMLInputElement

      await userEvent.clear(sellAssetInput)
      await userEvent.type(sellAssetInput, '20.3883')

      waitFor(() => {
        const loader = getByRole('status')
        expect(loader).toBeDefined()
      })
    })

    describe('buy token auto update', () => {
      beforeAll(() => {
        vi.useFakeTimers()
      })

      afterAll(() => {
        vi.useRealTimers()
      })

      it('should update buy asset automatically after 20 seconds', async () => {
        const { getByLabelText } = renderComponent({
          plannedOrder,
        })

        await vi.advanceTimersByTimeAsync(21000)

        const buyAssetInput = getByLabelText('Buy') as HTMLInputElement
        expect(buyAssetInput.value).to.equal('75')
      })
    })

    describe('when submitting the form', () => {
      const plannedOrder = {
        id: 'planned-order-1',
        buyAssetWithAmount: {
          asset: ethToken,
          amount: Big(10.29834),
          availableAmount: Big(20),
        },
        sellAssetWithAmount: {
          asset: bnbToken,
          amount: Big(5.23883),
          availableAmount: Big(10),
        },
      }

      it('should submit the form with status confirm and correct values', async () => {
        const onSubmit = vi.fn()
        const { findByRole } = renderComponent({
          plannedOrder,
          onSubmit,
        })

        const swapButton = await findByRole('button', { name: /confirm/i }) as HTMLButtonElement

        await userEvent.click(swapButton)

        await waitFor(() => {
          expect(onSubmit).toHaveBeenCalledWith({
            status: 'CONFIRM',
            signableOrderId: '1',
            transactionHash: '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
          })
        })
      })

      it('should submit the form with status cancel and empty steps', async () => {
        const onSubmit = vi.fn()
        const { findByRole } = renderComponent({
          plannedOrder,
          onSubmit,
        })

        const cancelButton = await findByRole('button', { name: /cancel/i }) as HTMLButtonElement

        await userEvent.click(cancelButton)

        expect(onSubmit).toHaveBeenCalledWith({
          status: 'CANCEL',
        })
      })
    })

    it('should display disclaimer', () => {
      const { getByText } = renderComponent({
        plannedOrder: {
          id: 'planned-order-1',
          buyAssetWithAmount: {
            asset: aiBasket,
            amount: Big(0),
            availableAmount: Big(0),
          },
          sellAssetWithAmount: {
            asset: bnbToken,
            amount: Big(0),
            availableAmount: Big(0),
          },
        },
      })

      expect(getByText(/coinbasket can make mistakes/i)).toBeDefined()
      expect(getByText(/Please do your own research and check token addresses before proceeding with any transaction/i)).toBeDefined()
    })
  })
})

describe('fee estimation', () => {
  const plannedOrder = {
    id: 'planned-order-1',
    buyAssetWithAmount: {
      asset: ethToken,
      amount: Big(10),
      availableAmount: Big(20),
    },
    sellAssetWithAmount: {
      asset: bnbToken,
      amount: Big(5),
      availableAmount: Big(10),
    },
    fees: {
      gasFee: {
        asset: bnbToken,
        amount: Big(0.00021),
        amountAtomic: BigInt(210000000),
        decimals: 18,
      },
      providerFee: {
        asset: ethToken,
        amount: Big(0.00009),
        amountAtomic: BigInt(90000000),
        decimals: 18,
      },
      platformFee: {
        asset: ethToken,
        amount: Big(0.1),
        amountAtomic: BigInt(100000000000000000),
        decimals: 18,
      },
    },
  }

  it('should display estimated gas fee on render', () => {
    const { getByLabelText, getByText } = renderComponent({
      plannedOrder,
    })

    const feeElement = getByText(/Network cost/i)
    const feeValue = getByLabelText(/Network cost/i)

    expect(feeElement).toBeDefined()
    expect(feeValue.textContent).to.equal('0.00021000 BNB')
  })

  it('should display estimated provider fee on render', () => {
    const { getByLabelText, getByText } = renderComponent({
      plannedOrder,
    })

    const feeElement = getByText(/Provider fee/i)
    const feeValue = getByLabelText(/Provider fee/i)

    expect(feeElement).toBeDefined()
    expect(feeValue.textContent).to.equal('0.00009000 ETH')
  })

  it('should display estimated platform fee on render', () => {
    const { getByLabelText, getByText } = renderComponent({
      plannedOrder,
    })

    const feeElement = getByText(/Platform fee/i)
    const feeValue = getByLabelText(/Platform fee/i)

    expect(feeElement).toBeDefined()
    expect(feeValue.textContent).to.equal('0.10000000 ETH')
  })

  it('should display "Free" when a fee is undefined', () => {
    const { getByLabelText, getByText } = renderComponent({
      plannedOrder: {
        ...plannedOrder,
        fees: {
          gasFee: undefined,
          providerFee: undefined,
          platformFee: undefined,
        },
      },
    })

    const providerFeeElement = getByText(/Provider fee/i)
    const providerFeeValue = getByLabelText(/Provider fee/i)

    expect(providerFeeElement).toBeDefined()
    expect(providerFeeValue.textContent).to.equal('Free')
  })

  it('should update fees when sell amount is changed', async () => {
    const { getByLabelText } = renderComponent({
      plannedOrder,
    })

    const sellAssetInput = getByLabelText('Sell') as HTMLInputElement

    await userEvent.clear(sellAssetInput)
    await userEvent.type(sellAssetInput, '20')

    await waitFor(() => {
      const gasFeeValue = getByLabelText(/Network cost/i)
      expect(gasFeeValue.textContent).to.equal('0.00042000 BNB')

      const providerFeeValue = getByLabelText(/Provider fee/i)
      expect(providerFeeValue.textContent).to.equal('0.00018000 SOL')

      const platformFeeValue = getByLabelText(/Platform fee/i)
      expect(platformFeeValue.textContent).to.equal('0.20000000 ETH')
    })
  })
})

describe('slippage', () => {
  it('should display max slippage', () => {
    const { getByText, getByLabelText } = renderComponent({
      plannedOrder: {
        id: 'planned-order-1',
        buyAssetWithAmount: {
          asset: aiBasket,
          amount: Big(10),
          availableAmount: Big(20),
        },
        sellAssetWithAmount: {
          asset: bnbToken,
          amount: Big(5),
          availableAmount: Big(10),
        },
        fees: {
          gasFee: undefined,
          providerFee: undefined,
          platformFee: undefined,
        },
      },
    })

    const slippageElement = getByText(/Max slippage/i)
    const slippageValue = getByLabelText(/Max slippage/i)

    expect(slippageElement).toBeDefined()
    expect(slippageValue.textContent).to.equal('1.00%')
  })
})

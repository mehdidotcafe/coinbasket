import type { ChangeEvent } from 'react'
import type { Control, FieldValues, Path, UseFormReturn } from 'react-hook-form'
import type { Asset } from '@/asset/Asset'
import type { Fees } from '@/fee/fees'
import type { ConfirmedOrder } from '@/invest/order/confirmed-order'
import type { PlannedOrder } from '@/invest/order/planned-order'
import type { SignableOrder } from '@/invest/order/signable-order'
import { zodResolver } from '@hookform/resolvers/zod'
import Big from 'big.js'
import Image from 'next/image'
import { useEffect, useReducer, useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { NumericFormat } from 'react-number-format'
import { toast } from 'sonner'
import { useDebouncedCallback } from 'use-debounce'
import { concat, numberToHex, size, TransactionExecutionError } from 'viem'
import { useAccount, useSignTypedData, useWaitForTransactionReceipt, useWalletClient } from 'wagmi'
import * as z from 'zod'
import { AssetLogo } from '@/asset/asset-logo'
import { AssetName } from '@/asset/asset-name'
import { useResettableInterval } from '@/chat/use-resettable-interval'
import { SwapDisclaimer } from '@/components/disclaimer'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Form } from '@/components/ui/form'
import { Separator } from '@/components/ui/separator'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import WaitingEllipsis from '@/components/waiting-ellipsis'
import { Loader } from '@/loader'
import { usePricer } from '@/price/use-pricer'
import { useRegistry } from '@/registry/use-registry'

const tokenFormSchema = z.object({
  name: z.string(),
  displayName: z.string(),
  ticker: z.string(),
  id: z.string(),
  address: z.string(),
  description: z.string(),
  decimals: z.number(),
  categories: z.array(z.string()),
  type: z.literal('TOKEN'),
  logoUri: z.string().optional(),
})

const basketFormSchema = z.object({
  name: z.string(),
  displayName: z.string(),
  ticker: z.string(),
  id: z.string(),
  address: z.string(),
  description: z.string(),
  decimals: z.number(),
  categories: z.array(z.string()),
  type: z.literal('BASKET'),
  logoUri: z.string().optional(),
})

const assetFormSchema = z.union([tokenFormSchema, basketFormSchema])

const AMOUNT_REGEX = /^\d+(\.\d+)?$/

const assetWithAmountFormSchema = z.object({
  asset: assetFormSchema,
  amount: z.string().regex(AMOUNT_REGEX),
  availableAmount: z.string().optional(),
})

const balanceAtomicSchema = z.object({
  asset: assetFormSchema,
  amount: z.instanceof(Big),
  amountAtomic: z.bigint(),
}).optional()

const feesSchema = z.object({
  platformFee: balanceAtomicSchema,
  providerFee: balanceAtomicSchema,
  gasFee: balanceAtomicSchema,
}).optional()

const formSchema = z.object({
  buyAssetWithAmount: assetWithAmountFormSchema,
  sellAssetWithAmount: assetWithAmountFormSchema,
  fees: feesSchema,
}).superRefine((data, ctx) => {
  if (!data.sellAssetWithAmount.availableAmount) {
    return
  }

  const availableAmount = Big(data.sellAssetWithAmount.availableAmount)
  const sellAmount = Big(data.sellAssetWithAmount.amount || 0)

  if (sellAmount.gt(availableAmount)) {
    ctx.addIssue({
      code: 'custom',
      message: `Insufficient ${data.sellAssetWithAmount.asset.displayName} (${data.sellAssetWithAmount.asset.ticker}) balance`,
      path: ['sellAssetWithAmount', 'amount'],
    })
  }
})

type FormData = z.infer<typeof formSchema>

type TransactionStep = 'idle' | 'signing-permit' | 'waiting-permit' | 'confirming-permit' | 'sending-transaction' | 'waiting-transaction' | 'confirming-transaction' | 'completed' | 'canceled' | 'error'

interface TransactionState {
  currentStep: TransactionStep
  error: string | null
}

type TransactionAction = { type: 'START_SIGNING_PERMIT' }
  | { type: 'PERMIT_SIGNED' }
  | { type: 'START_SENDING_TRANSACTION' }
  | { type: 'TRANSACTION_SENT' }
  | { type: 'START_CONFIRMING' }
  | { type: 'TRANSACTION_CONFIRMED' }
  | { type: 'CANCEL' }
  | { type: 'ERROR', error: string }
  | { type: 'RESET' }

function transactionReducer(state: TransactionState, action: TransactionAction): TransactionState {
  switch (action.type) {
    case 'START_SIGNING_PERMIT':
      return { ...state, currentStep: 'signing-permit', error: null }
    case 'PERMIT_SIGNED':
      return { ...state, currentStep: 'confirming-permit' }
    case 'START_SENDING_TRANSACTION':
      return { ...state, currentStep: 'sending-transaction', error: null }
    case 'TRANSACTION_SENT':
      return { ...state, currentStep: 'waiting-transaction' }
    case 'START_CONFIRMING':
      return { ...state, currentStep: 'confirming-transaction' }
    case 'TRANSACTION_CONFIRMED':
      return { ...state, currentStep: 'completed' }
    case 'CANCEL':
      return { ...state, currentStep: 'canceled', error: null }
    case 'ERROR':
      return { currentStep: 'idle', error: action.error }
    case 'RESET':
      return { currentStep: 'idle', error: null }
    default:
      return state
  }
}

interface AssetInputProps<T extends FieldValues> {
  asset: Asset
  availableAmount?: string
  control: Control<T>
  name: Path<T>
  preLabel: string
  onChange?: (e: ChangeEvent<HTMLInputElement>) => void
  disabled: boolean
  hasError: boolean
}

const NB_DECIMALS = 8

function AssetInput<T extends FieldValues>({ asset, availableAmount, control, name, preLabel, onChange, disabled, hasError }: AssetInputProps<T>) {
  const debouncedOnChange = useDebouncedCallback((e: ChangeEvent<HTMLInputElement>) => onChange?.(e), 300)

  return (
    <section className={`border ${hasError ? 'border-destructive' : ''} rounded-lg shadow-md bg-primary w-full p-4 ${disabled ? 'cursor-not-allowed' : ''}`}>
      <div className="flex items-center justify-between mb-1">
        <label htmlFor={name} className="block text-sm font-medium text-muted-foreground">
          {preLabel}
        </label>
      </div>
      <div className="flex">
        <div className="flex-1">
          <Controller
            control={control}
            name={name}
            render={({ field }) => (
              <NumericFormat
                className={`text-left border-none outline-none w-full ${disabled ? 'cursor-not-allowed' : ''}  bg-transparent focus:ring-0 focus:ring-offset-0`}
                inputMode="decimal"
                pattern={AMOUNT_REGEX.source}
                value={typeof field.value === 'undefined' ? '' : field.value}
                thousandSeparator={false}
                allowedDecimalSeparators={['.', ',']}
                allowNegative={false}
                valueIsNumericString
                placeholder="0.0"
                name={name}
                min={0}
                id={name}
                decimalScale={NB_DECIMALS}
                disabled={disabled}
                onChange={(e) => {
                  const newValue = e?.currentTarget?.value

                  if (newValue === field.value) {
                    return
                  }

                  field.onChange(e)

                  debouncedOnChange?.(e)
                }}
              />
            )}
          />
        </div>
        <div className="flex items-center gap-2 ml-4 border rounded-full p-1 pr-2 bg-secondary/10">
          <AssetLogo asset={asset} />
          <AssetName asset={asset} />
        </div>
      </div>

      <div className="flex mt-4 text-right justify-end">
        {
          availableAmount
            ? (
              <span className="text-sm text-muted-foreground flex items-center gap-1 justify-center">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-4">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a2.25 2.25 0 0 0-2.25-2.25H15a3 3 0 1 1-6 0H5.25A2.25 2.25 0 0 0 3 12m18 0v6a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 18v-6m18 0V9M3 12V9m18 0a2.25 2.25 0 0 0-2.25-2.25H5.25A2.25 2.25 0 0 0 3 9m18 0V6a2.25 2.25 0 0 0-2.25-2.25H5.25A2.25 2.25 0 0 0 3 6v3" />
                    </svg>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Balance</p>
                  </TooltipContent>
                </Tooltip>

                {Big(availableAmount).toFixed(NB_DECIMALS, Big.roundDown)}
              </span>
            )
            : null
        }
      </div>
    </section>
  )
}

function mapPlannedOrderToForm(plannedOrder: PlannedOrder): FormData {
  return {
    buyAssetWithAmount: {
      asset: plannedOrder.buyAssetWithAmount.asset,
      amount: plannedOrder.buyAssetWithAmount.amount?.toFixed() ?? '',
      availableAmount: plannedOrder.buyAssetWithAmount.availableAmount.toFixed(),
    },
    sellAssetWithAmount: {
      asset: plannedOrder.sellAssetWithAmount.asset,
      amount: plannedOrder.sellAssetWithAmount.amount?.toFixed() ?? '',
      availableAmount: plannedOrder.sellAssetWithAmount.availableAmount.toFixed(),
    },
    fees: plannedOrder.fees,
  }
}

interface OrderPricerProps {
  form: UseFormReturn<FormData>
  order: FormData
  disabled: boolean
  setFormLoading: (loading: boolean) => void
}

function BottomSwapArrow() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="min-w-[20px] min-h-[20px] max-w-[20px] max-h-[20px]">
      <path fillRule="evenodd" d="M10 3a.75.75 0 0 1 .75.75v10.638l3.96-4.158a.75.75 0 1 1 1.08 1.04l-5.25 5.5a.75.75 0 0 1-1.08 0l-5.25-5.5a.75.75 0 1 1 1.08-1.04l3.96 4.158V3.75A.75.75 0 0 1 10 3Z" clipRule="evenodd" />
    </svg>

  )
}

interface AmountRowProps {
  label: string
  amountElement: React.ReactNode
  tooltip?: string
  icon?: string
}

function FeeAmount({ amount, asset, label }: { amount?: Big, asset?: { ticker: string }, label: string }) {
  return (
    <span className="text-sm" aria-label={label}>
      {amount && asset ? `${amount.toFixed(NB_DECIMALS)} ${asset.ticker}` : <span className="text-secondary font-sofia-sans font-bold">Free</span>}
    </span>
  )
}

function AmountRow({ label, amountElement, tooltip, icon }: AmountRowProps) {
  return (
    <div className="flex items-center justify-between py-1">
      <div className="flex items-center justify-center gap-1 text-sm text-muted-foreground">
        {icon
          ? (
            <Image
              className="rounded-full bg-white border shadow-sm mr-1 w-[20px] h-[20px]"
              width={20}
              height={20}
              src={icon}
              alt="Fee icon"
            />
          )
          : <span className="w-[20px] h-[20px] mr-1" />}
        <label className="min-w-[85px]">{label}</label>
        {tooltip && (
          <Tooltip>
            <TooltipTrigger asChild>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="size-4">
                <path fillRule="evenodd" d="M15 8A7 7 0 1 1 1 8a7 7 0 0 1 14 0ZM9 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM6.75 8a.75.75 0 0 0 0 1.5h.75v1.75a.75.75 0 0 0 1.5 0v-2.5A.75.75 0 0 0 8.25 8h-1.5Z" clipRule="evenodd" />
              </svg>

            </TooltipTrigger>
            <TooltipContent>
              <p>{tooltip}</p>
            </TooltipContent>
          </Tooltip>
        )}
      </div>
      {amountElement}
    </div>
  )
}

interface FeesDisplayProps {
  fees?: Fees
}

function FeesDisplay({ fees }: FeesDisplayProps) {
  return (
    <div className="w-full mt-4">
      <AmountRow
        label="Platform fee"
        amountElement={(
          <FeeAmount
            amount={fees?.platformFee?.amount}
            asset={fees?.platformFee?.asset}
            label="Platform fee"
          />
        )}
        tooltip="Fee charged by coinbasket"
        icon="/logo/coinbasket-icon.png"
      />
      <AmountRow
        label="Provider fee"
        amountElement={(
          <FeeAmount
            amount={fees?.providerFee?.amount}
            asset={fees?.providerFee?.asset}
            label="Provider fee"
          />
        )}
        tooltip="Fee charged by the smart router provider"
        icon="/logo/0x.svg"
      />
      <AmountRow
        label="Network cost"
        amountElement={(
          <FeeAmount
            amount={fees?.gasFee?.amount}
            asset={fees?.gasFee?.asset}
            label="Network cost"
          />
        )}
        tooltip="Estimated gas fee for the transaction"
        icon="/logo/bnb.svg"
      />
      <AmountRow
        label="Max slippage"
        amountElement={(
          <span className="text-sm" aria-label="Max slippage">
            1.00%
          </span>
        )}
        tooltip="Maximum allowed slippage for the transaction. If the price changes more than this value, the transaction will revert."
      />
    </div>
  )
}

function useFormPricer({
  form,
  order,
  disabled,
  setFormLoading,
}: {
  form: UseFormReturn<FormData>
  order: FormData
  disabled: boolean
  setFormLoading: (loading: boolean) => void
}) {
  const { getPrice } = usePricer()

  const updateFromAsset = (asset1: 'sellAssetWithAmount' | 'buyAssetWithAmount', asset2: 'sellAssetWithAmount' | 'buyAssetWithAmount') => async (sellAssetAmount: Big | undefined, blockingReload: boolean) => {
    if (!sellAssetAmount) {
      form.setValue(`${asset2}.amount`, '')
      form.setValue('fees', undefined)
    }
    else {
      if (blockingReload) {
        setFormLoading(true)
      }

      try {
        const { buyBalance, fees: newFees } = await getPrice({
          sellAsset: order[asset1].asset,
          buyAsset: order[asset2].asset,
          sellAssetAmount,
        })
        form.setValue(`${asset2}.amount`, buyBalance.amount.toFixed())
        form.setValue('fees', newFees)
      }
      finally {
        if (blockingReload) {
          setFormLoading(false)
        }
      }
    }
    form.trigger()
  }

  const updateFromSellAsset = updateFromAsset('sellAssetWithAmount', 'buyAssetWithAmount')
  const updateFromBuyAsset = updateFromAsset('buyAssetWithAmount', 'sellAssetWithAmount')

  // Fetch buy price if sell price is provided
  // Fetch sell price if buy price is provided
  // If both price are provided fetch buy price
  // Updates the form with the value
  const { resetInterval } = useResettableInterval(() => {
    if (disabled) {
      return
    }
    const sellAmount = form.getValues('sellAssetWithAmount.amount')
    const buyAmount = form.getValues('buyAssetWithAmount.amount')

    // If both are empty, do nothing
    if (!sellAmount && !buyAmount)
      return

    // If both are provided, fetch buy price (priority to buy)
    if (sellAmount && buyAmount) {
      updateFromSellAsset(Big(sellAmount), false)
      return
    }

    // If only sell is provided, fetch buy price
    if (sellAmount) {
      updateFromSellAsset(Big(sellAmount), false)
      return
    }

    // If only buy is provided, fetch sell price
    if (buyAmount) {
      updateFromBuyAsset(Big(buyAmount), false)
    }
  }, 20_000)

  return {
    updateFromSellAsset,
    updateFromBuyAsset,
    resetInterval,
  }
}

function useTransactionFlow({
  onTransactionConfirmed,
}: {
  onTransactionConfirmed: (transactionHash: string, signableOrderId: string) => void
}) {
  const [state, dispatch] = useReducer(transactionReducer, {
    currentStep: 'idle',
    error: null,
  })

  const [signableOrder, setSignableOrder] = useState<SignableOrder | null>(null)
  const hasPermit = !!signableOrder?.signaturePayload

  const { address } = useAccount()
  const { data: walletClient } = useWalletClient()

  const [txHash, setTxHash] = useState<`0x${string}` | undefined>()

  // Permit2 signature handling
  const {
    signTypedData: signPermit,
    data: permitSignature,
    isPending: isSigningPermit,
    error: permitError,
  } = useSignTypedData()

  // Transaction confirmation handling
  const {
    isLoading: isConfirming,
    isSuccess: isConfirmed,
    error: confirmError,
  } = useWaitForTransactionReceipt({
    hash: txHash,
  })

  const makeEncodedInput = (transactionData: string, signature?: `0x${string}`): string => {
    if (!signature || !hasPermit) {
      return transactionData
    }

    const signatureLengthInHex = numberToHex(size(signature), {
      signed: false,
      size: 32,
    })

    const result = concat([
      transactionData as `0x${string}`,
      signatureLengthInHex,
      signature,
    ])

    return result
  }

  const handleSignAndSendTransaction = async (order: SignableOrder) => {
    if (!walletClient || !address) {
      dispatch({ type: 'ERROR', error: 'Wallet not connected' })
      return
    }

    const transaction = order.transaction

    if (!transaction?.toAddress) {
      dispatch({ type: 'ERROR', error: 'Transaction address is missing' })
      return
    }

    try {
      const data = makeEncodedInput(
        transaction.data,
        permitSignature as `0x${string}`,
      )

      const hash = await walletClient.sendTransaction({
        to: transaction.toAddress as `0x${string}`,
        data: data as `0x${string}`,
        value: transaction.amount,
        gas: transaction.gas?.gas,
        gasPrice: transaction.gas?.gas_price,
      })

      setTxHash(hash)
      dispatch({ type: 'TRANSACTION_SENT' })
    }
    catch (error: any) {
      if (error instanceof TransactionExecutionError && error.shortMessage) {
        dispatch({ type: 'ERROR', error: error.shortMessage || 'Transaction failed' })
      }
      else {
        dispatch({ type: 'ERROR', error: error.message || 'Transaction failed' })
      }
    }
  }

  // Handle permit signature flow
  useEffect(() => {
    if (isSigningPermit && state.currentStep === 'idle') {
      dispatch({ type: 'START_SIGNING_PERMIT' })
    }
    else if (permitSignature && state.currentStep === 'signing-permit' && signableOrder) {
      dispatch({ type: 'PERMIT_SIGNED' })
      dispatch({ type: 'START_SENDING_TRANSACTION' })
      handleSignAndSendTransaction(signableOrder)
    }
    else if (permitError) {
      dispatch({ type: 'ERROR', error: permitError.message })
    }
  }, [isSigningPermit, permitSignature, permitError, state.currentStep, signableOrder])

  // Handle transaction confirmation flow
  useEffect(() => {
    if (isConfirming && state.currentStep === 'waiting-transaction') {
      dispatch({ type: 'START_CONFIRMING' })
    }
    else if (isConfirmed && state.currentStep === 'confirming-transaction') {
      dispatch({ type: 'TRANSACTION_CONFIRMED' })
      onTransactionConfirmed(txHash!, signableOrder!.id)
    }
    else if (confirmError && state.currentStep !== 'canceled') {
      dispatch({ type: 'ERROR', error: confirmError.message })
    }
  }, [isConfirming, isConfirmed, confirmError, state.currentStep, onTransactionConfirmed])

  const startTransaction = (order: SignableOrder) => {
    if (!order) {
      dispatch({ type: 'ERROR', error: 'No signable order available' })
      return
    }

    setSignableOrder(order)
    dispatch({ type: 'RESET' })

    const orderHasPermit = !!order.signaturePayload

    if (orderHasPermit) {
      try {
        const permitData = order.signaturePayload! as any
        signPermit(permitData)
      }
      catch {
        dispatch({ type: 'ERROR', error: 'Failed to parse permit data' })
      }
    }
    else {
      dispatch({ type: 'START_SENDING_TRANSACTION' })
      handleSignAndSendTransaction(order)
    }
  }

  const cancelTransaction = () => {
    dispatch({ type: 'CANCEL' })
  }

  return {
    currentStep: state.currentStep,
    error: state.error,
    startTransaction,
    cancelTransaction,
  }
}

function OrderPricer({ form, order, disabled, setFormLoading }: OrderPricerProps) {
  const {
    updateFromBuyAsset,
    updateFromSellAsset,
    resetInterval,
  } = useFormPricer({
    form,
    order,
    disabled,
    setFormLoading,
  })

  const fieldError = form.formState.errors?.sellAssetWithAmount?.amount
  const hasFieldError = fieldError?.type === 'custom'

  return (
    <div className="flex flex-col items-center gap-2">
      <AssetInput
        asset={order.sellAssetWithAmount.asset}
        availableAmount={order.sellAssetWithAmount.availableAmount}
        control={form.control}
        name="sellAssetWithAmount.amount"
        disabled={disabled}
        preLabel="Sell"
        onChange={(e) => {
          resetInterval()

          if (!e.target?.value) {
            updateFromSellAsset(undefined, true)
            return
          }

          updateFromSellAsset(Big(e.target.value), true)
        }}
        hasError={hasFieldError}
      />
      <BottomSwapArrow />
      <AssetInput
        disabled={true}
        asset={order.buyAssetWithAmount.asset}
        availableAmount={order.buyAssetWithAmount.availableAmount}
        control={form.control}
        name="buyAssetWithAmount.amount"
        preLabel="Buy"
        onChange={(e) => {
          if (!e.target?.value)
            return
          resetInterval()
          updateFromBuyAsset(Big(e.target.value), true)
        }}
        hasError={false}
      />
    </div>
  )
}

export interface OrderConfirmation {
  status: 'CONFIRM' | 'CANCEL'
  signableOrderId?: string
  transactionHash?: string
}

export interface Props {
  plannedOrder: PlannedOrder
  onSubmit?: (result: OrderConfirmation) => Promise<void>
}

function getSubmitText(plannedOrder: PlannedOrder) {
  const hasSellAmount = plannedOrder.sellAssetWithAmount?.amount?.gt(0)
  const hasBuyAmount = plannedOrder.buyAssetWithAmount?.amount?.gt(0)

  if (hasSellAmount && hasBuyAmount) {
    return 'Confirm'
  }

  if (hasSellAmount) {
    return 'Sell'
  }

  return 'Buy'
}

function FormActionButtons({
  currentStep,
  form,
  onCancel,
  plannedOrder,
  isFormLoading,
}: {
  currentStep: TransactionStep
  form: UseFormReturn<FormData>
  onCancel: () => void
  plannedOrder: PlannedOrder
  isFormLoading: boolean
}) {
  if (isFormLoading) {
    return (
      <Loader
        width={36}
        height={36}
      />
    )
  }

  switch (currentStep) {
    case 'idle':
      return (
        <>
          <Button type="submit" variant="secondary" disabled={!form.formState.isValid} className="w-32">
            {getSubmitText(plannedOrder)}
          </Button>
          <Button variant="outline" type="button" onClick={onCancel} className="w-18">
            Cancel
          </Button>
        </>
      )
    case 'signing-permit':
      return (
        <Button variant="secondary" className="pointer-events-none w-32">
          Signing
          <WaitingEllipsis />
        </Button>
      )
    case 'confirming-permit':
    case 'sending-transaction':
    case 'waiting-transaction':
    case 'confirming-transaction':
      return (
        <Button variant="secondary" className="pointer-events-none w-32">
          Confirming
          <WaitingEllipsis />
        </Button>
      )
    case 'completed':
      return (
        <Button variant="success" className="pointer-events-none w-32">
          Completed
        </Button>
      )
    case 'canceled':
      return (
        <Button variant="outline" className="pointer-events-none">
          Cancelled
        </Button>
      )
    default:
      return null
  }
}

export function Pricer({ plannedOrder, onSubmit }: Props) {
  const defaultForm = mapPlannedOrderToForm(plannedOrder)
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: defaultForm,
  })
  const { apiClient } = useRegistry()
  const [isFormLoading, setIsFormLoading] = useState(false)
  const fees = form.watch('fees')

  const { currentStep, error, startTransaction, cancelTransaction } = useTransactionFlow({
    onTransactionConfirmed: (transactionHash, signableOrderId) => {
      onSubmit?.({
        status: 'CONFIRM',
        signableOrderId,
        transactionHash,
      })
    },
  })

  useEffect(() => {
    form.trigger()
  }, [])

  const onFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!form.formState.isValid) {
      return
    }

    try {
      setIsFormLoading(true)

      // Convert PlannedOrder to SignableOrder
      const formValues = form.getValues()
      const confirmedOrder: ConfirmedOrder = {
        plannedOrderId: plannedOrder.id,
        sellBalance: {
          asset: formValues.sellAssetWithAmount.asset,
          amount: Big(formValues.sellAssetWithAmount.amount),
        },
        buyBalance: {
          asset: formValues.buyAssetWithAmount.asset,
          amount: Big(formValues.buyAssetWithAmount.amount),
        },
      }

      const signable = await apiClient.getSignableOrder(confirmedOrder)

      setIsFormLoading(false)

      // Start the transaction flow
      startTransaction(signable)
    }
    catch (e: unknown) {
      console.error(e)
      setIsFormLoading(false)
      toast('An error has occurred when preparing the order')
    }
  }

  const onFormCancel = () => {
    cancelTransaction()
    onSubmit?.({
      status: 'CANCEL',
    })
  }

  const getStepMessage = (): string | null => {
    switch (currentStep) {
      case 'signing-permit':
        return 'Please sign the approval in your wallet...'
      case 'sending-transaction':
        return 'Please confirm the order in your wallet...'
      default:
        return null
    }
  }

  // Get form field error (validation error like insufficient balance)
  const fieldError = form.formState.errors?.sellAssetWithAmount?.amount
  const fieldErrorMessage = fieldError?.type === 'custom' ? fieldError.message : undefined

  // Consolidate all errors: prioritize transaction errors over field errors
  const displayError = error || fieldErrorMessage

  const isWaitingForWallet = currentStep === 'signing-permit' || currentStep === 'sending-transaction'
  const stepMessage = getStepMessage()
  const isFormDisabled = currentStep !== 'idle'

  return (
    <Card>
      <CardHeader>
        <CardTitle className="mb-4 font-sofia-sans text-2xl">Place Order</CardTitle>
        <Separator />
      </CardHeader>
      <Form {...form}>
        <form onSubmit={onFormSubmit}>
          <CardContent>
            <div className="py-2">
              <OrderPricer
                form={form}
                order={defaultForm}
                disabled={isFormDisabled}
                setFormLoading={setIsFormLoading}
              />
            </div>
            <FeesDisplay fees={fees} />
            {displayError && (
              <div className="w-full mt-4 p-3 rounded-lg text-sm bg-destructive text-destructive-foreground">
                {displayError}
              </div>
            )}
            {stepMessage
              ? (
                <div className={`w-full mt-4 p-3 rounded-lg text-sm ${isWaitingForWallet
                  ? 'bg-accent text-accent-foreground'
                  : 'bg-primary text-primary-foreground'
                  }`}
                >
                  {stepMessage}
                </div>
              )
              : null}
            <Separator className="my-4" />
          </CardContent>
          <CardFooter className="flex-col">
            <div className="flex items-center justify-center w-full gap-4 mb-6">
              <FormActionButtons
                currentStep={currentStep}
                form={form}
                onCancel={onFormCancel}
                plannedOrder={plannedOrder}
                isFormLoading={isFormLoading}
              />
            </div>
            <SwapDisclaimer />
          </CardFooter>
        </form>
      </Form>

    </Card>
  )
}

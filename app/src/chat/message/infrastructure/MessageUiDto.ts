import type { MessageUi } from '../MessageUi'
import Big from 'big.js'
import * as z from 'zod'
import { AssetDto, AssetResponseSchema } from '@/asset/infrastructure/AssetDto'
import { BalanceAtomicDto, BalanceAtomicSchema } from '@/balance/infrastructure/BalanceAtomicDto'

const AssetWithAmountResponseSchema = z.object({
  asset: AssetResponseSchema,
  amount: z.string().optional().nullable(),
  available_amount: z.string(),
})

const FeesResponseSchema = z.object({
  gas_fee: BalanceAtomicSchema.nullable(),
  provider_fee: BalanceAtomicSchema.nullable(),
  platform_fee: BalanceAtomicSchema.nullable(),
})

const MessageUiConfirmPlannedOrderResponseSchema = z.object({
  id: z.literal('confirm_planned_order'),
  args: z.object({
    planned_order: z.object({
      id: z.string(),
      buy_asset_with_amount: AssetWithAmountResponseSchema,
      sell_asset_with_amount: AssetWithAmountResponseSchema,
      fees: FeesResponseSchema,
    }),
  }),
})

export const MessageUiResponseSchema = z.union([MessageUiConfirmPlannedOrderResponseSchema])

const isDefined = (value: string | null | undefined): value is string => value !== undefined && value !== null

type MessageUiResponse = z.infer<typeof MessageUiResponseSchema>

export class MessageUiDto {
  static fromResponse(messageUi: MessageUiResponse): MessageUi {
    if (messageUi.id === 'confirm_planned_order') {
      return {
        id: messageUi.id,
        args: {
          plannedOrder: {
            id: messageUi.args.planned_order.id,
            buyAssetWithAmount: {
              asset: AssetDto.fromResponse(messageUi.args.planned_order.buy_asset_with_amount.asset),
              amount: isDefined(messageUi.args.planned_order.buy_asset_with_amount.amount) ? Big(messageUi.args.planned_order.buy_asset_with_amount.amount) : undefined,
              availableAmount: Big(messageUi.args.planned_order.buy_asset_with_amount.available_amount),
            },
            sellAssetWithAmount: {
              asset: AssetDto.fromResponse(messageUi.args.planned_order.sell_asset_with_amount.asset),
              amount: isDefined(messageUi.args.planned_order.sell_asset_with_amount.amount) ? Big(messageUi.args.planned_order.sell_asset_with_amount.amount) : undefined,
              availableAmount: Big(messageUi.args.planned_order.sell_asset_with_amount.available_amount),
            },
            fees: {
              gasFee: messageUi.args.planned_order.fees.gas_fee ? BalanceAtomicDto.fromResponse(messageUi.args.planned_order.fees.gas_fee) : undefined,
              providerFee: messageUi.args.planned_order.fees.provider_fee ? BalanceAtomicDto.fromResponse(messageUi.args.planned_order.fees.provider_fee) : undefined,
              platformFee: messageUi.args.planned_order.fees.platform_fee ? BalanceAtomicDto.fromResponse(messageUi.args.planned_order.fees.platform_fee) : undefined,
            },
          },
        },
      }
    }
    throw new Error(`Unsupported MessageUi id: ${messageUi.id}`)
  }
}

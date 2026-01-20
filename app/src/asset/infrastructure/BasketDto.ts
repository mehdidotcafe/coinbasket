import type { Basket } from '../Basket'
import * as z from 'zod'

export const BasketResponseSchema = z.object({
  name: z.string(),
  display_name: z.string(),
  ticker: z.string(),
  id: z.string(),
  address: z.string(),
  categories: z.array(z.string()),
  decimals: z.number(),
  description: z.string(),
  type: z.literal('BASKET'),
  logo_uri: z.string().nullable(),
})

type BasketResponse = z.infer<typeof BasketResponseSchema>

export class BasketDto {
  static toResponse(basket: Basket): BasketResponse {
    return {
      name: basket.name,
      display_name: basket.displayName,
      ticker: basket.ticker,
      id: basket.id,
      address: basket.address,
      categories: basket.categories,
      decimals: basket.decimals,
      description: basket.description,
      type: 'BASKET',
      logo_uri: basket.logoUri ?? null,
    }
  }

  static fromResponse(basketResponse: BasketResponse): Basket {
    return {
      name: basketResponse.name,
      displayName: basketResponse.display_name,
      ticker: basketResponse.ticker,
      id: basketResponse.id,
      address: basketResponse.address,
      categories: basketResponse.categories,
      decimals: basketResponse.decimals,
      description: basketResponse.description,
      type: 'BASKET',
      logoUri: basketResponse.logo_uri ?? undefined,
    }
  }
}

import type { Token } from '../Token'
import * as z from 'zod'

export const TokenResponseSchema = z.object({
  name: z.string(),
  display_name: z.string(),
  ticker: z.string(),
  id: z.string(),
  address: z.string(),
  categories: z.array(z.string()),
  decimals: z.number(),
  description: z.string(),
  type: z.literal('TOKEN'),
  logo_uri: z.string().nullable(),
})

type TokenResponse = z.infer<typeof TokenResponseSchema>

export type TokenRequest = TokenResponse

export class TokenDto {
  static toRequest(token: Token): TokenRequest {
    return this.toResponse(token)
  }

  static toResponse(token: Token): TokenResponse {
    return {
      name: token.name,
      display_name: token.displayName,
      ticker: token.ticker,
      id: token.id,
      address: token.address,
      categories: token.categories,
      decimals: token.decimals,
      description: token.description,
      type: 'TOKEN',
      logo_uri: token.logoUri ?? null,
    }
  }

  static fromResponse(tokenResponse: TokenResponse): Token {
    return {
      name: tokenResponse.name,
      displayName: tokenResponse.display_name,
      ticker: tokenResponse.ticker,
      id: tokenResponse.id,
      address: tokenResponse.address,
      categories: tokenResponse.categories,
      decimals: tokenResponse.decimals,
      description: tokenResponse.description,
      type: 'TOKEN',
      logoUri: tokenResponse.logo_uri ?? undefined,
    }
  }
}

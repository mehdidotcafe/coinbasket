import type { Asset } from '../Asset'
import * as z from 'zod'
import { BasketDto, BasketResponseSchema } from './BasketDto'
import { TokenDto, TokenResponseSchema } from './TokenDto'

export const AssetResponseSchema = z.union([TokenResponseSchema, BasketResponseSchema])

export type AssetResponse = z.infer<typeof AssetResponseSchema>

export type AssetRequest = AssetResponse

export class AssetDto {
  static toRequest(asset: Asset): AssetRequest {
    return this.toResponse(asset)
  }

  static toResponse(asset: Asset): AssetResponse {
    if (asset.type === 'BASKET') {
      return BasketDto.toResponse(asset)
    }
    return TokenDto.toResponse(asset)
  }

  static fromResponse(assetResponse: AssetResponse): Asset {
    if (assetResponse.type === 'BASKET') {
      return BasketDto.fromResponse(assetResponse)
    }
    return TokenDto.fromResponse(assetResponse)
  }
}

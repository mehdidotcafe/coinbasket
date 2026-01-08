import type { Asset } from '@/asset/Asset'
import type { ConvertedBalance } from '@/portfolio/portfolio'

export interface AssetSwapPriceInfo {
  buyAsset: Asset
  sellAsset: Asset
  sellAssetAmount: Big
}

export interface GetAssetSwapPriceParams {
  priceInfo: AssetSwapPriceInfo
  appKey: string
}

export interface PricerClient {
  getPrice: (priceInfo: AssetSwapPriceInfo) => Promise<ConvertedBalance>
}

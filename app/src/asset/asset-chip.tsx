import type { Asset } from './Asset'
import { AssetLogo } from './asset-logo'
import { AssetName } from './asset-name'

interface Props {
  asset: Asset
}

export function AssetChip({
  asset,
}: Props) {
  return (
    <div className="flex items-center gap-2 ml-4 border rounded-full p-1 pr-2 bg-secondary/10">
      <AssetLogo asset={asset} />
      <AssetName asset={asset} />
    </div>
  )
}

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
    <span className="flex items-center gap-2 border rounded-full p-1 pr-2 bg-secondary/10 w-fit">
      <AssetLogo asset={asset} />
      <AssetName asset={asset} />
    </span>
  )
}

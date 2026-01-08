import type { Asset } from './Asset'
import Image from 'next/image'

export function AssetLogo({
  asset,
}: { asset: Asset }) {
  const isToken = 'logoUri' in asset
  const logoUri = isToken ? asset.logoUri : undefined

  if (!logoUri) {
    return null
  }

  return (
    <div className="rounded-full bg-primary border overflow-hidden">
      <Image
        src={logoUri}
        alt={asset.ticker}
        width={25}
        height={25}
      />
    </div>
  )
}

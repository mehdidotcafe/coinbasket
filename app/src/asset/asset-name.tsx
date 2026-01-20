import type { Asset } from './Asset'

function isNativeToken(asset: Asset) {
  return 'address' in asset && asset.address.toLowerCase() === '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'.toLowerCase()
}

export function AssetName({ asset }: { asset: Asset }) {
  const assetNameWithTicker = (
    <>
      {asset.displayName}
      {' '}
      (
      {asset.ticker}
      )
    </>
  )

  if (isNativeToken(asset)) {
    return assetNameWithTicker
  }
  return (
    <a href={`https://bscscan.com/token/${asset.address}`} target="_blank" rel="noopener noreferrer" className="text-secondary font-sofia-sans">
      {assetNameWithTicker}
    </a>
  )
}

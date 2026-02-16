import type { Asset } from './Asset'
import Image from 'next/image'
import { ErrorBoundary } from 'react-error-boundary'

export function AssetLogo({
  asset,
}: { asset: Asset }) {
  const isToken = 'logoUri' in asset
  const logoUri = isToken ? asset.logoUri : undefined

  if (!logoUri) {
    return null
  }

  return (
    <div className="rounded-full bg-primary overflow-hidden max-w-[24px] max-h-[24px] w-[24px] h-[24px] flex items-center justify-center">
      <ErrorBoundary fallback={<div></div>}>
        <Image
          src={logoUri}
          alt={asset.ticker}
          width={24}
          height={24}
        />
      </ErrorBoundary>
    </div>
  )
}

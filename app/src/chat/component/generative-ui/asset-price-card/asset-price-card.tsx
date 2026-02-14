import type { Balance } from '@/balance/Balance'
import { AssetLogo } from '@/asset/asset-logo'
import { AssetName } from '@/asset/asset-name'
import { Card, CardContent } from '@/components/ui/card'

interface Props {
  sellBalance: Balance
  buyBalance: Balance
}

export function AssetPriceCard({ sellBalance, buyBalance }: Props) {
  return (
    <Card>
      <CardContent className="flex flex-col items-start gap-8 text-xl">
        <div className="flex gap-2 items-center">
          <AssetLogo asset={sellBalance.asset} />
          <AssetName asset={sellBalance.asset} />
        </div>
        <div className="font-sofia-sans text-2xl font-bold">
          {buyBalance.amount.toFixed(6)}
          {' '}
          {buyBalance.asset.ticker}
        </div>
      </CardContent>
    </Card>
  )
}

import type { Balance } from '@/balance/Balance'
import { AssetChip } from '@/asset/asset-chip'
import { Card, CardContent } from '@/components/ui/card'

interface Props {
  sellBalance: Balance
  buyBalance: Balance
}

export function AssetPriceCard({ sellBalance, buyBalance }: Props) {
  return (
    <Card>
      <CardContent className="flex flex-row justify-between gap-16 items-center">
        <AssetChip asset={sellBalance.asset} />
        <div className="font-sofia-sans text-xl">
          {buyBalance.amount.toFixed(6)}
          {' '}
          {buyBalance.asset.ticker}
        </div>
      </CardContent>
    </Card>
  )
}

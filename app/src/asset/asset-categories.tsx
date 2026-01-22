import type { Asset } from './Asset'
import { Badge } from '@/components/ui/badge'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'

export function AssetCategories({
  asset,
}: {
  asset: Asset
}) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Badge variant="secondary" className="cursor-pointer rounded-full aspect-square p-1">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="size-4">
            <path fillRule="evenodd" d="M4.5 2A2.5 2.5 0 0 0 2 4.5v2.879a2.5 2.5 0 0 0 .732 1.767l4.5 4.5a2.5 2.5 0 0 0 3.536 0l2.878-2.878a2.5 2.5 0 0 0 0-3.536l-4.5-4.5A2.5 2.5 0 0 0 7.38 2H4.5ZM5 6a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" clipRule="evenodd" />
          </svg>

        </Badge>
      </PopoverTrigger>
      <PopoverContent>
        <div className="flex flex-col gap-1">
          {
            asset.categories.map(category => (
              <Badge variant="default" key={category}>
                {category.toUpperCase()}
              </Badge>
            ))
          }
        </div>
      </PopoverContent>
    </Popover>
  )
}

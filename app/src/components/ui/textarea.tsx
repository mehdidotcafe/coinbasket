import * as React from 'react'

import { cn } from '@/lib/utils'

function Textarea({ className, ...props }: React.ComponentProps<'textarea'>) {
  return (
    <textarea
      rows={1}
      data-slot="textarea"
      className={cn(
        'border-input placeholder:text-muted-foreground flex field-sizing-content min-h-8 rounded-md border bg-transparent px-3 py-2 text-base shadow-xs transition-[color,box-shadow] disabled:cursor-not-allowed disabled:opacity-50 md:text-sm resize-none w-full border-none outline-none',
        className,
      )}
      {...props}
    />
  )
}

export { Textarea }

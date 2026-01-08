'use client'

import Link from 'next/link'
import { useSearchParams } from 'next/navigation'

function mergeQueryParams(currentSearch: string, href: string) {
  try {
    const url = new URL(href, 'http://coinbasket.ai')
    const mergedParams = new URLSearchParams(currentSearch)

    for (const [key, value] of url.searchParams.entries()) {
      mergedParams.set(key, value)
    }

    const search = mergedParams.toString()
    return url.pathname + (search ? `?${search}` : '')
  }
  catch (e: unknown) {
    console.error('Error merging query params:', e)
    return href
  }
}

export function RetainQueryLink({ href, ...props }: { href: string } & React.ComponentProps<typeof Link>) {
  const searchParams = useSearchParams()
  const currentSearch = searchParams.toString()
  const mergedHref = mergeQueryParams(currentSearch, href)

  return <Link href={mergedHref} {...props} />
}

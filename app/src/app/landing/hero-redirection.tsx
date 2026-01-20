'use client'

import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { useAuthentication } from '@/authentication/use-authentication'

export function HeroRedirection() {
  const router = useRouter()
  const authentication = useAuthentication()

  useEffect(() => {
    if (authentication.authStatus === 'authenticated') {
      router.push('/c')
    }
  }, [authentication.authStatus])

  return null
}

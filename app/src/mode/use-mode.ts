import { useEnv } from '@/env/use-env'

interface Mode {
  mode: 'demo' | 'live'
}

export function useMode(): Mode {
  const env = useEnv()

  return {
    mode: env.APP_MODE,
  }
}

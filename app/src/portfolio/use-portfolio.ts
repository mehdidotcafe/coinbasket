import type { Portfolio } from '../portfolio/portfolio'
import { useQuery } from '@tanstack/react-query'
import { useAuthentication } from '@/authentication/use-authentication'
import { useEnv } from '@/env/use-env'
import { useRegistry } from '../registry/use-registry'

export function usePortfolio() {
  const {
    PORTFOLIO_TOKEN_ID,
    PORTFOLIO_TOKEN_ADDRESS,
    PORTFOLIO_TOKEN_TICKER,
    PORTFOLIO_TOKEN_NAME,
    PORTFOLIO_TOKEN_DISPLAY_NAME,
    PORTFOLIO_TOKEN_DECIMALS,
  } = useEnv()
  const { apiClient } = useRegistry()
  const authentication = useAuthentication()

  if (authentication.authStatus !== 'authenticated') {
    return {
      portfolio: undefined,
      isFetching: false,
      isPending: false,
    }
  }

  const { data: portfolio, isFetching, isPending } = useQuery({
    queryKey: ['portfolio', authentication.address],
    queryFn: async (): Promise<Portfolio> => {
      return apiClient.getPortfolio({
        name: PORTFOLIO_TOKEN_NAME,
        displayName: PORTFOLIO_TOKEN_DISPLAY_NAME,
        ticker: PORTFOLIO_TOKEN_TICKER,
        id: PORTFOLIO_TOKEN_ID,
        address: PORTFOLIO_TOKEN_ADDRESS,
        decimals: PORTFOLIO_TOKEN_DECIMALS,
        categories: [],
        description: '',
        type: 'TOKEN',
        logoUri: undefined,
      })
    },
    refetchInterval: 60_000,
  })

  return {
    portfolio,
    isFetching,
    isPending,
  }
}

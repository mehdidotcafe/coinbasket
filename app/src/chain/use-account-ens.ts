import { useAccount, useEnsName } from 'wagmi'

export function useAccountEns() {
  const { address } = useAccount()
  const { data: ensName } = useEnsName({
    address,
    chainId: 1,
    query: {
      enabled: Boolean(address),
    },
  })

  return { ensName, address }
}

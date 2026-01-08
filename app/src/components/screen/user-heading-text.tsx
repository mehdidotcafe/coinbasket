import { useAccountEns } from '@/chain/use-account-ens'

export function UserHeadingText() {
  const { address, ensName } = useAccountEns()

  if (ensName) {
    return (
      <>
        Hello,
        {' '}
        {ensName}
      </>
    )
  }
  if (address) {
    return (
      <>
        Hello,
        {' '}
        {address.slice(0, 6)}
        ...
        {address.slice(-5)}
        .
      </>
    )
  }
  return <>Hello,</>
}

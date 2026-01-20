import { useAuthentication } from '@/authentication/use-authentication'
import { useAccountEns } from '@/chain/use-account-ens'

export function UserHeadingText() {
  const authentication = useAuthentication()
  const { ensName } = useAccountEns()

  if (authentication.authStatus === 'authenticated' && ensName) {
    return (
      <>
        Hello,
        {' '}
        {ensName}
      </>
    )
  }
  if (authentication.authStatus === 'authenticated') {
    return (
      <>
        Hello,
        {' '}
        {authentication.address.slice(0, 6)}
        ...
        {authentication.address.slice(-5)}
        .
      </>
    )
  }
  return <>Hello,</>
}

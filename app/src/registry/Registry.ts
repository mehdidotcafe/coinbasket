import type { ApiClient } from '../api/api-client'
import type { ChatClient } from '../chat/client/chat-client'
import type { SiweClient } from '@/authentication/siwe-client'
import type { PricerClient } from '@/price/client/pricer-client'

export interface Registry {
  apiClient: ApiClient
  chatClient: ChatClient
  pricerClient: PricerClient
  siweClient: SiweClient
}

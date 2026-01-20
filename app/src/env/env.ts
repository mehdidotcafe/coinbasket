import * as z from 'zod'

export type NotValidatedEnv = Record<string, unknown>

const envSchema = z.object({
  'PORTFOLIO_TOKEN_NAME': z.string(),
  'PORTFOLIO_TOKEN_DISPLAY_NAME': z.string(),
  'PORTFOLIO_TOKEN_TICKER': z.string(),
  'PORTFOLIO_TOKEN_SYMBOL': z.string(),
  'PORTFOLIO_TOKEN_ID': z.string(),
  'PORTFOLIO_TOKEN_ADDRESS': z.string(),
  'PORTFOLIO_TOKEN_DECIMALS': z.coerce.number(),
  'APP_MODE': z.enum(['demo', 'live']),
  'APP_LIVE_URL': z.url(),
  'APP_DEMO_URL': z.url(),
  'API_URL': z.url(),
  'REPOSITORY_URL': z.url(),
  'CACHE_VERSION': z.string(),
  'BSC_RPC_URL': z.url(),
  '0X_PROTOCOL_URL': z.url(),
  'GITHUB_URL': z.url(),
  'X_URL': z.url(),
  'BNB_CHAIN_URL': z.url(),
  'MEHDIDOTCAFE_URL': z.url(),
})

export type Env = z.infer<typeof envSchema>

export function validateEnv(env: NotValidatedEnv): Env {
  const result = envSchema.safeParse(env)

  if (!result.success) {
    console.error('Invalid environment variables:', result.error.format())
    throw new Error('Invalid environment variables', { cause: result.error })
  }

  return result.data
}

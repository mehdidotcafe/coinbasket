import type { Token } from '@/asset/Token'

export const nearToken: Token = {
  id: 'bsc:0x1Fa4a73a3F0133f0025378af00236f3aBDEE5D63',
  name: 'NEAR Protocol',
  displayName: 'NEAR Protocol',
  ticker: 'NEAR',
  address: '0x1Fa4a73a3F0133f0025378af00236f3aBDEE5D63',
  categories: ['bridgeable'],
  description: 'NEAR is a decentralized application platform designed to make apps usable on the web.',
  decimals: 18,
  type: 'TOKEN',
}

export const filecoinToken: Token = {
  id: 'bsc:0x0D8Ce2A99Bb6e3B7Db580eD848240e4a0F9aE153',
  name: 'Filecoin',
  displayName: 'Filecoin',
  ticker: 'FIL',
  address: '0x0D8Ce2A99Bb6e3B7Db580eD848240e4a0F9aE153',
  categories: ['bridgeable'],
  description: 'Filecoin is a decentralized storage network designed to store humanity\'s most important information.',
  decimals: 18,
  type: 'TOKEN',
}

export const fetchToken: Token = {
  id: 'bsc:0x031b41e504677879370e9DBcF937283A8691Fa7f',
  name: 'FetchToken',
  displayName: 'Fetch.ai',
  ticker: 'FET',
  address: '0x031b41e504677879370e9DBcF937283A8691Fa7f',
  categories: ['bridgeable'],
  description: 'Fetch.ai is a decentralized machine learning platform based on a distributed ledger.',
  decimals: 18,
  type: 'TOKEN',
}

export const injectiveToken: Token = {
  id: 'bsc:0xa2b726b1145a4773f68593cf171187d8ebe4d495',
  name: 'Injective',
  displayName: 'Injective',
  ticker: 'INJ',
  address: '0xa2b726b1145a4773f68593cf171187d8ebe4d495',
  categories: ['bridgeable'],
  description: 'Injective Protocol is a decentralized exchange protocol that enables fully decentralized trading.',
  decimals: 18,
  type: 'TOKEN',
}

export const bnbToken: Token = {
  id: 'bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
  name: 'Binance Coin',
  displayName: 'Binance Coin',
  ticker: 'BNB',
  address: '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
  categories: ['native'],
  description: 'Binance Coin is the native token of the Binance blockchain.',
  decimals: 18,
  logoUri: 'https://coin-images.coingecko.com/coins/images/12591/small/binance-coin-logo.png',
  type: 'TOKEN',
}

export const wbnbToken: Token = {
  id: 'bsc:0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
  name: 'WBNB Token',
  displayName: 'Binance Coin',
  ticker: 'WBNB',
  address: '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
  categories: ['wrapped'],
  description: 'Wrapped Binance Coin is a tokenized version of Binance Coin (BNB) on the Binance Smart Chain.',
  decimals: 18,
  type: 'TOKEN',
}

export const ethToken: Token = {
  id: 'bsc:0x2170Ed0880ac9A755fd29B2688956BD959F933F8',
  name: 'Binance Pegged Ethereum',
  displayName: 'Ethereum',
  ticker: 'ETH',
  address: '0x2170Ed0880ac9A755fd29B2688956BD959F933F8',
  categories: ['bridgeable'],
  description: 'Binance Pegged Ethereum is a tokenized version of Ethereum (ETH) on the Binance Smart Chain.',
  decimals: 18,
  logoUri: 'https://assets.coingecko.com/coins/images/39580/small/weth.png?1723006716',
  type: 'TOKEN',
}

export const btcToken: Token = {
  id: 'bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c',
  name: 'Binance Pegged Bitcoin',
  displayName: 'Bitcoin',
  ticker: 'BTC',
  address: '0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c',
  categories: ['bridgeable'],
  description: 'Binance Pegged Bitcoin is a tokenized version of Bitcoin (BTC) on the Binance Smart Chain.',
  decimals: 18,
  logoUri: 'https://assets.coingecko.com/coins/images/14108/small/Binance-bitcoin.png?1696513829',
  type: 'TOKEN',
}

export const solToken: Token = {
  id: 'bsc:0x570A5D26f7765Ecb712C0924E4De545B89fD43dF',
  name: 'SOLANA',
  displayName: 'Solana',
  ticker: 'SOL',
  address: '0x570A5D26f7765Ecb712C0924E4De545B89fD43dF',
  categories: ['bridgeable'],
  description: 'Solana is a high-performance blockchain supporting builders around the world creating crypto apps that scale today.',
  decimals: 18,
  logoUri: 'https://assets.coingecko.com/coins/images/54582/small/wsol.png?1740542147',
  type: 'TOKEN',
}

export const usdtToken: Token = {
  id: 'bsc:0x55d398326f99059ff775485246999027b3197955',
  name: 'Tether USD',
  displayName: 'Tether USD',
  ticker: 'USDT',
  address: '0x55d398326f99059ff775485246999027b3197955',
  categories: ['stablecoin'],
  description: 'Tether is a stablecoin pegged to the US Dollar, designed to maintain a stable value.',
  decimals: 18,
  logoUri: 'https://assets.coingecko.com/coins/images/35021/small/USDT.png?1707233575',
  type: 'TOKEN',
}

import type { Portfolio } from '@/portfolio/portfolio'
import Big from 'big.js'

interface Data {
  portfolio: Portfolio
}

const data: Data[] = [
  {
    portfolio: {
      availableBalance: {
        nativeBalance: {
          asset: {
            name: 'SOLANA',
            displayName: 'Solana',
            ticker: 'SOL',
            id: 'bsc:0x570A5D26f7765Ecb712C0924E4De545B89fD43dF',
            address: '0x570A5D26f7765Ecb712C0924E4De545B89fD43dF',
            categories: ['bridgeable'],
            decimals: 18,
            description: 'Solana is a high-performance blockchain supporting builders around the world creating crypto apps that scale today.',
            type: 'TOKEN',

          },
          amount: Big('1000'),
          amountAtomic: BigInt(1000000000000000000000),
        },
        convertedBalance: {
          asset: {
            name: 'Tether USD',
            displayName: 'Tether USD',
            ticker: 'USDT',
            id: 'bsc:0x55d398326f99059ff775485246999027b3197955',
            address: '0x55d398326f99059ff775485246999027b3197955',
            categories: ['stablecoin'],
            decimals: 18,
            description: 'Tether is a stablecoin pegged to the US Dollar, designed to maintain a stable value.',
            type: 'TOKEN',
          },
          amount: Big('153000'),
          amountAtomic: BigInt(153000000000000000000000),
        },
      },
      holdingBalances: [],
      totalBalance: {
        asset: {
          name: 'Tether USD',
          displayName: 'Tether USD',
          ticker: 'USDT',
          id: 'bsc:0x55d398326f99059ff775485246999027b3197955',
          address: '0x55d398326f99059ff775485246999027b3197955',
          categories: ['stablecoin'],
          decimals: 18,
          description: 'Tether is a stablecoin pegged to the US Dollar, designed to maintain a stable value.',
          type: 'TOKEN',
        },
        amount: Big('153000'),
        amountAtomic: BigInt(153000000000000000000000),
      },
    },
  },
  {
    portfolio: {
      availableBalance: {
        nativeBalance: {
          asset: {
            name: 'BNB',
            displayName: 'BNB',
            ticker: 'BNB',
            id: 'bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
            address: '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
            categories: ['native'],
            decimals: 18,
            description: 'Binance Coin (BNB) is the native cryptocurrency of the Binance blockchain, used for transaction fees and various applications within the Binance ecosystem.',
            type: 'TOKEN',
          },
          amount: Big('0.0037267166'),
          amountAtomic: BigInt('37267166'),
        },
        convertedBalance: {
          asset: {
            name: 'Tether USD',
            displayName: 'Tether USD',
            ticker: 'USDT',
            id: 'bsc:0x55d398326f99059fF775485246999027B3197955',
            address: '0x55d398326f99059fF775485246999027B3197955',
            categories: ['stablecoin'],
            decimals: 18,
            description: 'Tether is a stablecoin pegged to the US Dollar, designed to maintain a stable value.',
            type: 'TOKEN',
          },
          amount: Big('2.36615921291441617'),
          amountAtomic: BigInt('236615921291441617'),
        },
      },
      holdingBalances: [
        {
          nativeBalance: {
            asset: {
              name: 'Bitcoin',
              displayName: 'Bitcoin',
              ticker: 'BTCB',
              id: 'bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c',
              address: '0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c',
              categories: ['bridgeable'],
              decimals: 18,
              description: 'Binance Pegged Bitcoin is a tokenized version of Bitcoin (BTC) on the Binance Smart Chain.',
              type: 'TOKEN',
            },
            amount: Big('0.625881078732322445'),
            amountAtomic: BigInt('625881078732322445'),
          },
          convertedBalance: {
            asset: {
              name: 'Tether USD',
              displayName: 'Tether USD',
              ticker: 'USDT',
              id: 'bsc:0x55d398326f99059fF775485246999027B3197955',
              address: '0x55d398326f99059fF775485246999027B3197955',
              categories: ['stablecoin'],
              decimals: 18,
              description: 'Tether is a stablecoin pegged to the US Dollar, designed to maintain a stable value.',
              type: 'TOKEN',
            },
            amount: Big('63139.10151659231187416'),
            amountAtomic: BigInt('6313910151659231187416'),
          },
        },
      ],
      totalBalance: {
        asset: {
          name: 'Tether USD',
          displayName: 'Tether USD',
          ticker: 'USDT',
          id: 'bsc:0x55d398326f99059fF775485246999027B3197955',
          address: '0x55d398326f99059fF775485246999027B3197955',
          categories: ['stablecoin'],
          decimals: 18,
          description: 'Tether is a stablecoin pegged to the US Dollar, designed to maintain a stable value.',
          type: 'TOKEN',
        },
        amount: Big('63141.46767580522629033'),
        amountAtomic: BigInt('6314146767580522629033'),
      },
    },
  },
  {
    portfolio: {
      availableBalance: {
        nativeBalance: {
          asset: {
            name: 'BNB',
            displayName: 'BNB',
            ticker: 'BNB',
            id: 'bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
            address: '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
            categories: ['native'],
            decimals: 18,
            description: 'Binance Coin (BNB) is the native cryptocurrency of the Binance blockchain, used for transaction fees and various applications within the Binance ecosystem.',
            type: 'TOKEN',
          },
          amount: Big('19.771918896606722422'),
          amountAtomic: BigInt('19771918896606722422'),
        },
        convertedBalance: {
          asset: {
            name: 'Tether USD',
            displayName: 'Tether USD',
            ticker: 'USDT',
            id: 'bsc:0x55d398326f99059fF775485246999027B3197955',
            address: '0x55d398326f99059fF775485246999027B3197955',
            categories: ['stablecoin'],
            decimals: 18,
            description: 'Tether is a stablecoin pegged to the US Dollar, designed to maintain a stable value.',
            type: 'TOKEN',
          },
          amount: Big('12665.33528702410649836'),
          amountAtomic: BigInt('1266533528702410649836'),
        },
      },
      holdingBalances: [],
      totalBalance: {
        asset: {
          name: 'Tether USD',
          displayName: 'Tether USD',
          ticker: 'USDT',
          id: 'bsc:0x55d398326f99059fF775485246999027B3197955',
          address: '0x55d398326f99059fF775485246999027B3197955',
          categories: ['stablecoin'],
          decimals: 18,
          description: 'Tether is a stablecoin pegged to the US Dollar, designed to maintain a stable value.',
          type: 'TOKEN',
        },
        amount: Big('12665.33528702410649836'),
        amountAtomic: BigInt('1266533528702410649836'),
      },
    },
  },
]

export default data

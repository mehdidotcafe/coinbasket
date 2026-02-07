/* eslint-disable node/prefer-global/process */
import type { Metadata } from 'next'
import { Analytics } from '@vercel/analytics/next'
import { Providers } from '../providers'
import { Header } from './header'
import './globals.css'

const title = 'coinbasket'
const description = 'AI-Powered crypto orders, one prompt away.'

export const metadata: Metadata = {
  title,
  description,
  icons: {
    icon: 'favicon/favicon.ico',
    shortcut: 'favicon/favicon.ico',
    apple: 'favicon/apple-touch-icon.png',
    other: {
      rel: 'apple-touch-icon',
      sizes: '180x180',
      url: 'favicon/apple-touch-icon.png',
    },
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_LIVE_URL!),
  openGraph: {
    title,
    description,
    url: process.env.NEXT_PUBLIC_APP_LIVE_URL,
    siteName: 'coinbasket',
    images: [{ url: '/logo/coinbasket-og-banner.jpg', width: 1200, height: 630, alt: 'coinbasket banner' }],
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title,
    description,
    images: ['/logo/coinbasket-og-banner.jpg'],
    site: '@coinbasketai',
    creator: '@coinbasketai',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body
        className="antialiased"
      >
        <Providers>
          <div className="flex flex-col w-full">
            <Header />
            {children}
          </div>
        </Providers>
        <Analytics />
      </body>
    </html>
  )
}

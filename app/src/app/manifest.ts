import type { MetadataRoute } from 'next'

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'coinbasket',
    short_name: 'coinbasket',
    description: 'AI-Powered Crypto Orders. One Prompt Away',
    start_url: '/',
    display: 'standalone',
    background_color: '#f98500',
    theme_color: '#f98500',
    icons: [
      {
        src: '/web-app-manifest-192x192.png',
        sizes: '192x192',
        type: 'image/png',
        purpose: 'maskable',
      },
      {
        src: '/web-app-manifest-512x512.png',
        sizes: '512x512',
        type: 'image/png',
        purpose: 'maskable',
      },
    ],
  }
}

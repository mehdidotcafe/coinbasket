import type { UIMessage } from 'ai'
import type { OrderConfirmation } from './generative-ui/pricer/pricer'
import type { Asset } from '@/asset/Asset'
import Markdown from 'markdown-to-jsx'
import Image from 'next/image'
import React from 'react'
import { useEnsAvatar } from 'wagmi'
import { AssetChip } from '@/asset/asset-chip'
import { useAccountEns } from '@/chain/use-account-ens'
import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { MessageUiDto } from '../message/infrastructure/MessageUiDto'
import { AssetPriceCard } from './generative-ui/asset-price-card/asset-price-card'
import { Pricer } from './generative-ui/pricer/pricer'

interface Props {
  message: UIMessage
  onResume?: (result: OrderConfirmation) => void
}

const markdownOptions = {
  overrides: {
    token: {
      component: ({ display_name, ticker, address, logo_uri }: { display_name?: string, ticker?: string, address?: string, logo_uri?: string }) => {
        if (!display_name || !ticker || !address) {
          return display_name || ticker || address
        }

        const asset: Asset = {
          id: `bsc:${address.toLowerCase()}`,
          name: display_name,
          displayName: display_name,
          ticker,
          address,
          logoUri: logo_uri,
          description: '',
          decimals: 0,
          trustScore: 100,
          categories: [],
          type: 'TOKEN',
        }

        return <span className="inline-block align-middle mx-1"><AssetChip asset={asset} /></span>
      },
    },
    a: {
      component: ({ href, children, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement>) => (
        <a href={href} target="_blank" rel="noopener noreferrer" {...props} className="text-secondary font-sofia-sans">
          {children}
        </a>
      ),
    },
  },
}

function MarkdownView({ children }: { children: string }) {
  return (
    <div className="prose prose-default max-w-none prose-strong:font-extrabold prose-headings:font-extrabold prose-strong:font-sofia-sans prose-headings:font-sofia-sans prose-a:font-sofia-sans">
      <Markdown options={markdownOptions}>{children}</Markdown>
    </div>
  )
}

export const MemoMessageBubble = React.memo(MessageBubble, (prevProps, nextProps) => {
  // Only re-render if the message content has changed
  return JSON.stringify(prevProps.message.parts) === JSON.stringify(nextProps.message.parts)
})

export function MessageBubble({
  message,
  onResume,
}: Props) {
  if (message.role === 'user' && !(message.metadata as Record<string, unknown>)?.isResuming) {
    return <UserMessageBubble message={message} />
  }
  else if (message.role === 'assistant') {
    return <AssistantMessageBubble message={message} onResume={onResume} />
  }
  // Don't display responses to interrupts
  return null
}

function UserMessageBubble({
  message,
}: { message: UIMessage }) {
  const { ensName } = useAccountEns()
  const { data: avatar } = useEnsAvatar({
    name: ensName!,
    chainId: 1,
    query: {
      enabled: !!ensName,
    },
  })

  const textContent = message.parts
    .filter(p => p.type === 'text')
    .map(p => 'text' in p ? p.text : '')
    .join('')

  return (
    <article className={cn('flex justify-end my-4', avatar && 'md:-mr-[32px]')}>
      <Card className="text-white p-1 rounded-xl shadow-sm bg-secondary/10">
        <CardContent>
          <MarkdownView>{textContent}</MarkdownView>
        </CardContent>
      </Card>
      {
        avatar
          ? (
            <Image
              width={32}
              height={32}
              loader={() => avatar}
              src={avatar}
              alt="User Avatar"
              className="rounded-full shadow-m ml-2 mt-1 h-[32px] w-[32px]"
            />
          )
          : null
      }
    </article>
  )
}

function AssistantMessageBubble({
  message,
  onResume,
}: { message: UIMessage, onResume?: (result: OrderConfirmation) => void }) {
  return (
    <article className="flex flex-col justify-start leading-[1.75] my-4">
      {message.parts.map((part, i) => {
        if (part.type === 'text') {
          return <MarkdownView key={i}>{part.text}</MarkdownView>
        }

        if (part.type.startsWith('data-') && 'data' in part) {
          const data = part.data as Record<string, unknown>

          if (part.type === 'data-interrupt') {
            const uiRaw = data.ui as { id: string, args: Record<string, unknown> } | null
            if (uiRaw) {
              try {
              const ui = MessageUiDto.fromResponse(uiRaw as any)
              if (ui.id === 'confirm_planned_order') {
                return (
                  <div key={i} className="w-fit">
                    <Pricer
                      plannedOrder={ui.args.plannedOrder}
                      onSubmit={async (result) => {
                        onResume?.(result)
                      }}
                    />
                  </div>
                )
                }
              }
              catch (e) {
                console.error('Failed to parse UI from interrupt message part', e)
              }
            }
            return null
          }

          if (part.type === 'data-asset_price_card') {
            const ui = MessageUiDto.fromResponse({ id: 'asset_price_card', args: data.args } as any)
            if (ui.id === 'asset_price_card') {
              return (
                <div key={i} className="w-fit my-0.5">
                  <AssetPriceCard sellBalance={ui.args.sellBalance} buyBalance={ui.args.buyBalance} />
                </div>
              )
            }
          }

          if (part.type === 'data-confirm_planned_order') {
            const ui = MessageUiDto.fromResponse({ id: 'confirm_planned_order', args: data.args } as any)
            if (ui.id === 'confirm_planned_order') {
              return (
                <div key={i} className="w-fit">
                  <Pricer
                    plannedOrder={ui.args.plannedOrder}
                    onSubmit={async (result) => {
                      onResume?.(result)
                    }}
                  />
                </div>
              )
            }
          }
        }

        return null
      })}
    </article>
  )
}

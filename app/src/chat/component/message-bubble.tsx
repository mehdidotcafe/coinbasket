import type { Message } from '../message/Message'
import type { MessageUi } from '../message/MessageUi'
import type { QueryMessage } from '../message/QueryMessage'
import type { Asset } from '@/asset/Asset'
import Markdown from 'markdown-to-jsx'
import Image from 'next/image'
import { useEnsAvatar } from 'wagmi'
import { AssetChip } from '@/asset/asset-chip'
import { useAccountEns } from '@/chain/use-account-ens'
import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { makeQueryMessage } from '../message/make-query-message'
import { Pricer } from './generative-ui/pricer/pricer'

interface Props {
  message: Message
  onMessage?: (message: QueryMessage) => void
}

const markdownOptions = {
  overrides: {
    token: {
      component: ({ name, ticker, address, logo_uri, description, decimals }: { name: string, ticker: string, address: string, logo_uri?: string, description?: string, decimals: string }) => {
        const asset: Asset = {
          id: `bsc:${address.toLowerCase()}`,
          name,
          displayName: name,
          ticker,
          address,
          logoUri: logo_uri,
          description: description || '',
          decimals: Number.parseInt(decimals, 10),
          trustScore: 100,
          categories: [],
          type: 'TOKEN',
        }

        return (<AssetChip asset={asset} />)
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

export function MessageBubble({
  message,
  onMessage,
}: Props) {
  if (message.role === 'user') {
    return <UserMessageBubble message={message} />
  }
  return <AssistantMessageBubble message={message} onMessage={onMessage} />
}

function UserMessageBubble({
  message,
}: { message: Message }) {
  const { ensName } = useAccountEns()
  const { data: avatar } = useEnsAvatar({
    name: ensName!,
    chainId: 1,
    query: {
      enabled: !!ensName,
    },
  })

  return (
    <article className={cn('flex justify-end', avatar && 'md:-mr-[32px]')}>
      <Card className="text-white p-1 rounded-xl shadow-sm bg-secondary/10">
        <CardContent>
          <MarkdownView>{message.content!}</MarkdownView>
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

function AssistantUiMessage({
  ui,
  onMessage,
}: { ui: MessageUi, onMessage?: (message: QueryMessage) => void }) {
  if (ui.id === 'confirm_planned_order') {
    return (
      <Pricer
        plannedOrder={ui.args.plannedOrder}
        onSubmit={async (result) => {
          onMessage?.(makeQueryMessage(
            result,
            true,
          ))
        }}
      />
    )
  }

  return null
}

function AssistantTextMessage({
  content,
}: { content: string }) {
  return (
    <MarkdownView>{content}</MarkdownView>
  )
}

function AssistantMessageBubble({
  message,
  onMessage,
}: { message: Message, onMessage?: (message: QueryMessage) => void }) {
  return (
    <article className="flex justify-start leading-[1.75] m-w-full">
      {
        message.ui ? <AssistantUiMessage ui={message.ui} onMessage={onMessage} /> : null
      }
      {
        message.content ? <AssistantTextMessage content={message.content} /> : null
      }
    </article>
  )
}

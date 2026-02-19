'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useConnectModal } from '@rainbow-me/rainbowkit'
import { useEffect, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import * as z from 'zod'
import { useAuthentication } from '@/authentication/use-authentication'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { Form, FormControl, FormField, FormItem } from '@/components/ui/form'
import { Textarea } from '@/components/ui/textarea'
import { cn } from '@/lib/utils'
import { usePromptInput } from '@/prompt-input/prompt-input-context'
import precraftPrompts from '../precraft-prompts'

type PromptStatus = 'waiting_user_response' | 'waiting_ai_response' | 'ready'

export interface Props {
  status: PromptStatus
  onSubmit?: (text: string) => void
  size: 'large' | 'small'
  placeholder?: string
  hasMessageHistory?: boolean
}

const FormSchema = z.object({
  content: z
    .string()
    .min(1),
})

export function PromptForm({ onSubmit, status, size, placeholder = 'Ask something', hasMessageHistory = false }: Props) {
  const { openConnectModal } = useConnectModal()
  const { authStatus } = useAuthentication()
  const { promptInput, setPromptInput } = usePromptInput()

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      content: promptInput,
    },
  })
  const hasSubmittedFormWithPromptInput = useRef(false)
  const buttonDisabled = status !== 'ready'

  const onSubmitForm = (data: z.infer<typeof FormSchema>) => {
    if (authStatus !== 'authenticated' && openConnectModal) {
      openConnectModal()
    }
    else {
      form.reset()
      setPromptInput('')
      onSubmit?.(data.content)
    }
  }

  const askCapabilities = () => {
    form.setValue('content', 'What can you do?')
    form.trigger('content')
    form.handleSubmit(onSubmitForm)()
  }

  const askAvailableBaskets = () => {
    form.setValue('content', 'What are the available baskets?')
    form.trigger('content')
    form.handleSubmit(onSubmitForm)()
  }

  const askPortfolio = () => {
    form.setValue('content', 'What is my portfolio?')
    form.trigger('content')
    form.handleSubmit(onSubmitForm)()
  }

  const handleKeyDown = async (
    e: React.KeyboardEvent<HTMLTextAreaElement>,
  ) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (status === 'ready') {
        const isValid = await form.trigger()
        if (isValid) {
          form.handleSubmit(onSubmitForm)()
        }
      }
      else if (status === 'waiting_ai_response') {
        toast('Please wait Agent response')
      }
      else if (status === 'waiting_user_response') {
        toast('Please submit or cancel your current action')
      }
    }
  }

  // Send prompt input if any on first render when authenticated and no message history
  useEffect(() => {
    if (promptInput !== '' && authStatus === 'authenticated' && !hasSubmittedFormWithPromptInput.current) {
      hasSubmittedFormWithPromptInput.current = true

      if (hasMessageHistory === false) {
        const promptInputToSubmit = promptInput
        form.reset()

        setPromptInput('')
        onSubmit?.(promptInputToSubmit)
      }
    }
  }, [])

  // Keep form input in sync with prompt input state
  useEffect(() => {
    const subscription = form.watch((value) => {
      setPromptInput(value.content || '')
    })
    return () => subscription.unsubscribe()
  }, [form.watch, setPromptInput])

  // Keep form value in sync when prompt input changes externally (first render mostly)
  useEffect(() => {
    if (promptInput !== form.getValues('content')) {
      form.setValue('content', promptInput)
    }
  }, [promptInput])

  return (
    <div className="border bg-primary rounded-lg shadow-xl w-full p-2">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmitForm)} className="flex flex-col">
          <FormField
            control={form.control}
            name="content"
            render={({ field }) => (
              <FormItem>
                <FormControl>
                  <Textarea {...field} placeholder={placeholder} onKeyDown={handleKeyDown} className={size === 'large' ? '!text-lg' : ''} />
                </FormControl>
              </FormItem>
            )}
          />
          <div className={cn('flex items-end gap-2 flex-wrap', size === 'large' ? 'mt-4' : 'mt-1')}>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="badge" size="badge" className={cn('cursor-pointer align-middle leading-none py-1', size === 'large' ? 'text-lg' : '')} onClick={askCapabilities} disabled={buttonDisabled}>
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
                  </svg>
                  Try a prompt
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {
                  precraftPrompts.map((group, idx) => (
                    <div key={group.category}>
                      {idx > 0 ? <DropdownMenuSeparator /> : null}

                      <DropdownMenuLabel>{group.category}</DropdownMenuLabel>
                      {
                        group.prompts.map(prompt => (
                          <DropdownMenuItem
                            className="cursor-pointer"
                            key={prompt}
                            onClick={() => {
                              form.setValue('content', prompt)
                              form.trigger('content')
                              form.handleSubmit(onSubmitForm)()
                            }}
                          >
                            {prompt}
                          </DropdownMenuItem>
                        ))
                      }
                    </div>
                  ))
                }
              </DropdownMenuContent>
            </DropdownMenu>
            <Button variant="badge" size="badge" className={cn('cursor-pointer align-middle leading-none py-1', size === 'large' ? 'text-lg' : '')} onClick={askCapabilities} disabled={buttonDisabled}>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={size === 'large' ? 'size-8' : 'size-6'}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
              </svg>
              Ask AI capabilities
            </Button>
            <Button variant="badge" size="badge" className={cn('cursor-pointer align-middle leading-none py-1', size === 'large' ? 'text-lg' : '')} onClick={askAvailableBaskets} disabled={buttonDisabled}>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={size === 'large' ? 'size-8' : 'size-6'}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
              </svg>
              Ask AI baskets
            </Button>
            <Button
              variant="badge"
              size="badge"
              className={cn('hidden mr-4 cursor-pointer align-middle leading-none py-1', size === 'large' ? 'text-lg' : '')}
              onClick={askPortfolio}
              disabled={buttonDisabled}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={size === 'large' ? 'size-8' : 'size-6'}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a2.25 2.25 0 0 0-2.25-2.25H15a3 3 0 1 1-6 0H5.25A2.25 2.25 0 0 0 3 12m18 0v6a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 18v-6m18 0V9M3 12V9m18 0a2.25 2.25 0 0 0-2.25-2.25H5.25A2.25 2.25 0 0 0 3 9m18 0V6a2.25 2.25 0 0 0-2.25-2.25H5.25A2.25 2.25 0 0 0 3 6v3" />
              </svg>
              Ask portfolio
            </Button>
            <Button type="submit" variant="secondary" className="ml-auto mr-0" aria-label="Send" disabled={buttonDisabled}>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={size === 'large' ? 'size-8' : 'size-6'}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
              </svg>
            </Button>
          </div>
        </form>
      </Form>
    </div>
  )
}

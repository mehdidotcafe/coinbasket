/* eslint-disable no-console */
'use client'

import type { Meta, StoryObj } from '@storybook/react'
import { Providers } from '@/providers'
import { PromptForm } from './prompt-form'

const meta = {
  component: PromptForm,
  decorators: [
    Story => (
      <Providers>
        <Story />
      </Providers>
    ),
  ],
} satisfies Meta<typeof PromptForm>

export default meta

type Story = StoryObj<typeof meta>

export const ReadyLarge: Story = {
  args: {
    status: 'ready',
    size: 'large',
    placeholder: 'Ask something',
    hasMessageHistory: false,
    onSubmit: (message) => {
      console.log('Submitted:', message)
    },
  },
}

export const ReadySmall: Story = {
  args: {
    status: 'ready',
    size: 'small',
    placeholder: 'Ask something',
    hasMessageHistory: false,
    onSubmit: (message) => {
      console.log('Submitted:', message)
    },
  },
}

export const WaitingAIResponse: Story = {
  args: {
    status: 'waiting_ai_response',
    size: 'large',
    placeholder: 'Ask something',
    hasMessageHistory: true,
    onSubmit: (message) => {
      console.log('Submitted:', message)
    },
  },
}

export const WaitingUserResponse: Story = {
  args: {
    status: 'waiting_user_response',
    size: 'large',
    placeholder: 'Ask something',
    hasMessageHistory: true,
    onSubmit: (message) => {
      console.log('Submitted:', message)
    },
  },
}

export const WithMessageHistory: Story = {
  args: {
    status: 'ready',
    size: 'small',
    placeholder: 'Continue the conversation...',
    hasMessageHistory: true,
    onSubmit: (message) => {
      console.log('Submitted:', message)
    },
  },
}

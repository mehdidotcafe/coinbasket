'use client'

import type { Meta, StoryObj } from '@storybook/react'
import { Providers } from '@/providers'
import { Footer } from './footer'

const meta = {
  component: Footer,
  decorators: [
    Story => (
      <Providers>
        <Story />
      </Providers>
    ),
  ],
} satisfies Meta<typeof Footer>

export default meta

type Story = StoryObj<typeof meta>

export const Default: Story = {}

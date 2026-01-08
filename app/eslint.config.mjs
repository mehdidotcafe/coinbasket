import antfu from '@antfu/eslint-config'

import nextPlugin from '@next/eslint-plugin-next'
// For more info, see https://github.com/storybookjs/eslint-plugin-storybook#configuration-flat-config-format
import storybook from 'eslint-plugin-storybook'

export default antfu({
  plugins: {
    '@next/next': nextPlugin,
  },
  rules: {
    ...nextPlugin.configs.recommended.rules,
    ...nextPlugin.configs['core-web-vitals'].rules,
    'style/indent': 'off',
  },
})

import type { Storage } from '../storage'
import { del, get, set } from 'idb-keyval'

const makeKey = (prefix: string, key: string) => `${prefix}:${key}`

export function idbStorage(prefix: string): Storage {
  return {
    getItem: (key: string) => {
      return get(makeKey(prefix, key))
    },
    setItem: (key: string, value: string) => {
      return set(makeKey(prefix, key), value)
    },
    removeItem: (key: string) => {
      return del(makeKey(prefix, key))
    },
  }
}

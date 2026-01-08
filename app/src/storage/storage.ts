export interface Storage {
  getItem: (key: string) => Promise<string | undefined>
  setItem: (key: string, value: string) => Promise<void>
  removeItem: (key: string) => Promise<void>
}

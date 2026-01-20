import type { SiweClient } from '../siwe-client'

export const demoSiweClient: SiweClient = {
  getNonce: async () => {
    return Promise.resolve('Y5WhT4JKiJr')
  },

  verifySignature: async () => {
    return Promise.resolve('eyJhbGciOiJIUzI1NiJ9.eyJhZGRyZXNzIjoiMHh0ZXN0YWRkcmVzcyIsImV4cCI6IjAifQ.dPHCC94mGrm5H-Y5OOhyNs4EAW_u4uTqLeqf2dBrMao')
  },

  signOut: async () => {
    return Promise.resolve(true)
  },
}

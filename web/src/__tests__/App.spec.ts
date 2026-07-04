import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'

import { mount } from '@vue/test-utils'
import App from '../App.vue'
import appRouter from '../router'

beforeEach(() => {
  // HomeView/DriverView fetch CSVs on mount -- stub it so the test doesn't
  // depend on a real dev server or network access
  vi.stubGlobal(
    'fetch',
    vi.fn(() => Promise.resolve({ text: () => Promise.resolve('') }) as unknown as typeof fetch),
  )
})

describe('App', () => {
  it('mounts and renders the F1 Elo nav', () => {
    const testRouter = createRouter({ history: createMemoryHistory(), routes: appRouter.getRoutes() })
    const wrapper = mount(App, {
      global: { plugins: [createPinia(), testRouter] },
    })
    expect(wrapper.text()).toContain('F1')
    expect(wrapper.text()).toContain('Elo')
  })
})

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const createWrapper = (children: React.ReactNode) => {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

// Mock the store
vi.mock('../store', () => ({
  useAuthStore: vi.fn(() => ({
    token: null,
    user: null,
    setAuth: vi.fn(),
    logout: vi.fn(),
  })),
  api: vi.fn().mockResolvedValue([]),
}))

describe('ErrorBoundary', () => {
  it('renders children normally', async () => {
    const { default: ErrorBoundary } = await import('../components/ErrorBoundary')
    const { container } = render(
      <ErrorBoundary>
        <div data-testid="child">Hello</div>
      </ErrorBoundary>
    )
    expect(screen.getByTestId('child')).toBeTruthy()
  })

  it('catches errors and shows fallback', async () => {
    const { default: ErrorBoundary } = await import('../components/ErrorBoundary')
    const ThrowError = () => { throw new Error('Test error') }
    // Suppress console.error for this test
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})
    render(<ErrorBoundary><ThrowError /></ErrorBoundary>)
    expect(screen.getByText(/Something went wrong/i)).toBeTruthy()
    spy.mockRestore()
  })
})

describe('Login page', () => {
  it('renders login form', async () => {
    const { default: Login } = await import('../pages/Login')
    render(createWrapper(<Login />))
    expect(screen.getByText(/Sign in/i) || screen.getByText(/Login/i)).toBeTruthy()
  })
})

describe('Store', () => {
  it('api function exists', async () => {
    const { api } = await import('../store')
    expect(typeof api).toBe('function')
  })

  it('useAuthStore exists', async () => {
    const { useAuthStore } = await import('../store')
    expect(typeof useAuthStore).toBe('function')
  })
})

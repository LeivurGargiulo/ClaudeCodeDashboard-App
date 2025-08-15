import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from '../App'

// Mock the API client to avoid network calls
vi.mock('../api/client', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: [] }),
    post: vi.fn().mockResolvedValue({ data: {} }),
    put: vi.fn().mockResolvedValue({ data: {} }),
    delete: vi.fn().mockResolvedValue({ data: {} }),
  },
  instancesApi: {
    getAll: vi.fn().mockResolvedValue({ data: [] }),
    get: vi.fn().mockResolvedValue({ data: {} }),
    create: vi.fn().mockResolvedValue({ data: {} }),
    update: vi.fn().mockResolvedValue({ data: {} }),
    delete: vi.fn().mockResolvedValue({ data: {} }),
    health: vi.fn().mockResolvedValue({ data: {} }),
  },
  chatApi: {
    send: vi.fn().mockResolvedValue({ data: {} }),
    getHistory: vi.fn().mockResolvedValue({ data: [] }),
    clearHistory: vi.fn().mockResolvedValue({ data: {} }),
    export: vi.fn().mockResolvedValue({ data: {} }),
  },
  dockerApi: {
    getStatus: vi.fn().mockResolvedValue({ data: {} }),
    getContainers: vi.fn().mockResolvedValue({ data: [] }),
    start: vi.fn().mockResolvedValue({ data: {} }),
    stop: vi.fn().mockResolvedValue({ data: {} }),
    discover: vi.fn().mockResolvedValue({ data: {} }),
  },
  authApi: {
    login: vi.fn().mockResolvedValue({ data: {} }),
    logout: vi.fn().mockResolvedValue({ data: {} }),
    isAuthenticated: vi.fn().mockReturnValue(false),
    setToken: vi.fn(),
    getToken: vi.fn().mockReturnValue(null),
  },
  apiUtils: {
    handleError: vi.fn().mockReturnValue(new Error('Mocked error')),
    formatError: vi.fn().mockReturnValue('Mocked error message'),
    isNetworkError: vi.fn().mockReturnValue(false),
  }
}))

const AppWithRouter = () => (
  <BrowserRouter>
    <App />
  </BrowserRouter>
)

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders without crashing', () => {
    render(<AppWithRouter />)
    expect(document.body).toBeInTheDocument()
  })

  it('renders the main application structure', async () => {
    render(<AppWithRouter />)
    // The app should render without throwing errors
    expect(document.body).toBeInTheDocument()
    // We could check for specific elements if needed, but keeping it simple
    expect(document.querySelector('div')).toBeInTheDocument()
  })
})
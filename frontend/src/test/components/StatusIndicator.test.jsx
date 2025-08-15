import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatusIndicator from '../../components/StatusIndicator'

describe('StatusIndicator', () => {
  it('renders online status correctly', () => {
    render(<StatusIndicator status="online" />)
    const statusText = screen.getByText('Online')
    expect(statusText).toBeInTheDocument()
    const container = statusText.closest('span')
    expect(container).toHaveClass('text-green-600')
  })

  it('renders offline status correctly', () => {
    render(<StatusIndicator status="offline" />)
    const statusText = screen.getByText('Offline')
    expect(statusText).toBeInTheDocument()
    const container = statusText.closest('span')
    expect(container).toHaveClass('text-red-600')
  })

  it('renders error status correctly', () => {
    render(<StatusIndicator status="error" />)
    const statusText = screen.getByText('Error')
    expect(statusText).toBeInTheDocument()
    const container = statusText.closest('span')
    expect(container).toHaveClass('text-yellow-600')
  })

  it('renders unknown status correctly', () => {
    render(<StatusIndicator status="unknown" />)
    const statusText = screen.getByText('Unknown')
    expect(statusText).toBeInTheDocument()
    const container = statusText.closest('span')
    expect(container).toHaveClass('text-gray-600')
  })

  it('displays status text', () => {
    render(<StatusIndicator status="online" />)
    expect(screen.getByText('Online')).toBeInTheDocument()
  })
})
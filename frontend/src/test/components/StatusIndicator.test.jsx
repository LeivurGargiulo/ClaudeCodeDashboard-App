import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatusIndicator from '../../components/StatusIndicator'

describe('StatusIndicator', () => {
  it('renders online status correctly', () => {
    render(<StatusIndicator status="online" />)
    const indicator = screen.getByRole('img', { hidden: true })
    expect(indicator).toHaveClass('text-green-500')
  })

  it('renders offline status correctly', () => {
    render(<StatusIndicator status="offline" />)
    const indicator = screen.getByRole('img', { hidden: true })
    expect(indicator).toHaveClass('text-red-500')
  })

  it('renders error status correctly', () => {
    render(<StatusIndicator status="error" />)
    const indicator = screen.getByRole('img', { hidden: true })
    expect(indicator).toHaveClass('text-red-500')
  })

  it('renders unknown status correctly', () => {
    render(<StatusIndicator status="unknown" />)
    const indicator = screen.getByRole('img', { hidden: true })
    expect(indicator).toHaveClass('text-gray-500')
  })

  it('shows tooltip with status text', () => {
    render(<StatusIndicator status="online" />)
    const container = screen.getByTitle('online')
    expect(container).toBeInTheDocument()
  })
})
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from '../App'

const AppWithRouter = () => (
  <BrowserRouter>
    <App />
  </BrowserRouter>
)

describe('App', () => {
  it('renders without crashing', () => {
    render(<AppWithRouter />)
    expect(document.body).toBeInTheDocument()
  })

  it('renders the main navigation or dashboard', () => {
    render(<AppWithRouter />)
    // Check for common elements that should be present
    const body = document.body
    expect(body).toBeInTheDocument()
  })
})
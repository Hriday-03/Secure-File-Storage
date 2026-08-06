import { Component } from 'react'
import type { ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCcw } from 'lucide-react'

interface ErrorBoundaryProps {
  children: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
}

export default class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('Unhandled UI error:', error, errorInfo)
  }

  private handleReset = () => {
    this.setState({ hasError: false })
  }

  private handleReload = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-slate-950 p-6">
          <div className="max-w-md rounded-2xl border border-slate-800 bg-slate-900/50 p-8 text-center">
            <AlertTriangle className="mx-auto h-12 w-12 text-amber-400" />
            <h1 className="mt-4 text-xl font-bold text-slate-100">Something went wrong</h1>
            <p className="mt-2 text-sm text-slate-400">
              An unexpected error occurred while rendering this page. Please try again.
            </p>
            <div className="mt-6 flex items-center justify-center gap-3">
              <button
                type="button"
                onClick={this.handleReset}
                className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-slate-800"
              >
                <RefreshCcw className="h-4 w-4" />
                Try again
              </button>
              <button
                type="button"
                onClick={this.handleReload}
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-500"
              >
                Reload page
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
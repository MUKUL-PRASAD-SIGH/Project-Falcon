import { Component } from 'react'

/**
 * ErrorBoundary — catches unhandled render errors in any child subtree.
 *
 * Shows a console-style 500 panel with a retry button.
 * Each major page section (map, graph, dashboard, chat) should be wrapped
 * in its own ErrorBoundary so one failing widget can't crash the whole app.
 *
 * Usage:
 *   <ErrorBoundary label="Crime Map">
 *     <CrimeMap />
 *   </ErrorBoundary>
 */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    console.error('[Falcon ErrorBoundary]', error, info)
  }

  render() {
    if (this.state.error) {
      const { label = 'Component', onRetry } = this.props
      return (
        <div className="panel p-6 flex flex-col items-center justify-center gap-4 min-h-[200px]">
          <div className="font-mono text-alert text-sm">500 — {label} render error</div>
          <p className="text-ink-dim text-xs text-center max-w-sm">
            {this.state.error?.message ?? 'An unexpected error occurred.'}
          </p>
          <button
            className="btn-ghost text-xs"
            onClick={() => {
              this.setState({ error: null })
              onRetry?.()
            }}
          >
            Retry
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

import { useState } from 'react'
import { exportEvidencePDF } from '@/api/endpoints'

/**
 * ExportButton — SmartBrowz Evidence Trail PDF export (Step 4.1c, Req #9).
 *
 * Posts the current chat messages + FIR citations to /api/export/pdf
 * and triggers a browser file download.
 *
 * Props:
 *   messages   — array of chat message objects
 *   citations  — flat array of all FIR IDs cited in the conversation
 */
export default function ExportButton({ messages, citations }) {
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  async function handleExport() {
    setLoading(true)
    setError(null)
    try {
      const blob = await exportEvidencePDF(messages, citations)
      const url  = URL.createObjectURL(blob)
      const a    = document.createElement('a')
      a.href     = url
      a.download = `falcon-evidence-trail-${Date.now()}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      setError('PDF export unavailable (SmartBrowz pending)')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative">
      <button
        type="button"
        onClick={handleExport}
        disabled={loading || messages.length === 0}
        className="btn-ghost text-xs flex items-center gap-1.5 disabled:opacity-40 disabled:cursor-not-allowed"
        title="Export Evidence Trail as PDF (SmartBrowz)"
      >
        {loading ? (
          <span className="font-mono animate-pulse">Generating…</span>
        ) : (
          <>
            <span>⬇</span>
            <span>Evidence PDF</span>
          </>
        )}
      </button>
      {error && (
        <div className="absolute bottom-full right-0 mb-1 text-[10px] font-mono text-alert bg-navy-900 border border-alert/30 px-2 py-1 rounded-sm whitespace-nowrap z-10">
          {error}
        </div>
      )}
    </div>
  )
}

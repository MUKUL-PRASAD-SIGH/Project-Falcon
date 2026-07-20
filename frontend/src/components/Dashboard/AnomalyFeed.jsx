/**
 * AnomalyFeed — live anomaly alert panel.
 *
 * Adapts title and severity language based on the signed-in role:
 *   Investigator → "Alerts Needing Attention" / Urgent / Watch / Info
 *   Analyst/Admin → "Live Anomaly Feed" / High / Medium / Low
 *
 * Props:
 *   alerts  — array from useCatalystSignals()
 *   onClear — callback to dismiss all alerts
 */
import { useRoleVoice } from '@/hooks/useRoleVoice'

function timeAgo(isoStr) {
  const diff = (Date.now() - new Date(isoStr).getTime()) / 1000
  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  return `${Math.floor(diff / 3600)}h ago`
}

export default function AnomalyFeed({ alerts = [], onClear }) {
  const voice = useRoleVoice()
  const hasUrgent = alerts.some((a) => a.severity === 'High')

  return (
    <div className="panel p-4 flex flex-col h-full">

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {hasUrgent && <div className="pulse-dot" />}
          <h2 className="font-display text-sm tracking-wide text-ink-dim uppercase">
            {voice.anomalyTitle}
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="case-tag">Live</span>
          {alerts.length > 0 && (
            <button
              onClick={onClear}
              className="text-[10px] text-ink-dim hover:text-ink transition-colors font-mono"
              title="Clear alerts"
            >
              [clear]
            </button>
          )}
        </div>
      </div>

      {/* Feed body */}
      {alerts.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-ink-dim text-xs italic font-mono">
          {voice.anomalyEmpty}
        </div>
      ) : (
        <div className="space-y-3 overflow-y-auto scroll-thin flex-1">
          {alerts.map((a) => {
            const isUrgent = a.severity === 'High'
            return (
              <div
                key={`${a.id}-${a.ts}`}
                className={`border-l-2 pl-3 py-1.5 rounded-r-md transition-colors ${
                  isUrgent
                    ? 'border-[#D8503A] bg-[rgba(216,80,58,0.04)]'
                    : 'border-[rgba(255,255,255,0.12)]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="text-sm text-ink font-medium">{a.district}</div>
                  <span className="text-[10px] font-mono text-ink-dim">{timeAgo(a.ts)}</span>
                </div>
                <div className="text-xs text-ink-dim mt-0.5">{a.crimeType}</div>
                <div className="flex items-center gap-2 mt-1.5">
                  <span className="case-tag">FIR #{a.id}</span>
                  <span className={`text-[10px] font-mono font-semibold ${
                    isUrgent ? 'text-[#D8503A]' : 'text-ink-dim'
                  }`}>
                    {a.firCount} FIRs · {voice.severityLabel(a.severity)}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

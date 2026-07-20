import LoadingSkeleton from '@/components/common/LoadingSkeleton'

/**
 * StatCard — KPI metric card for the command dashboard.
 *
 * Props:
 *   icon      — emoji or string used as visual anchor (e.g. "📁")
 *   label     — metric name, role-adaptive from useRoleVoice
 *   value     — formatted value string
 *   tag       — service tag displayed as a case-tag chip
 *   trend     — optional "up" | "down" directional indicator
 *   isLoading — renders shimmer skeleton when true
 *   alert     — when true, tints card border red/orange
 */
export default function StatCard({ label, value, tag, trend, isLoading, alert }) {
  return (
    <div
      className={`panel p-5 cursor-default transition-all duration-200 hover:-translate-y-0.5 relative overflow-hidden ${
        alert
          ? 'border-[rgba(216,80,58,0.35)] hover:border-[rgba(216,80,58,0.55)]'
          : 'hover:border-[rgba(255,255,255,0.13)]'
      }`}
    >
      {/* Subtle left accent stripe */}
      <div
        className="absolute left-0 top-4 bottom-4 w-[2px] rounded-r-full"
        style={{ background: alert ? '#D8503A' : 'var(--role-accent)', opacity: 0.6 }}
      />

      {/* Label */}
      <div className="text-[11px] uppercase tracking-wider text-ink-dim font-medium pl-1">
        {label}
      </div>

      {/* Value */}
      {isLoading ? (
        <div className="mt-2">
          <LoadingSkeleton className="h-8 w-3/4" />
        </div>
      ) : (
        <div className="flex items-baseline gap-2 mt-1.5 pl-1">
          <div className={`font-display text-[1.7rem] font-bold leading-none ${
            alert ? 'text-[#D8503A]' : 'text-ink'
          }`}>
            {value}
          </div>
          {trend === 'up'   && <span className="text-xs text-[#D8503A] font-mono">+</span>}
          {trend === 'down' && <span className="text-xs text-emerald-400 font-mono">−</span>}
        </div>
      )}

      {/* Service tag */}
      <div className="mt-3 pl-1">
        <span className="case-tag">{tag}</span>
      </div>
    </div>
  )
}

/**
 * AnalystDashboard — data-dense command centre for Intelligence Analysts.
 *
 * Keeps the original stats + chart + anomaly-feed + district-table layout.
 * Role accent: Gold (#C9A227). Technical jargon. No hero map.
 */
import { useState, useEffect } from 'react'
import StatCard from './StatCard'
import ForecastChart from './ForecastChart'
import AnomalyFeed from './AnomalyFeed'
import DistrictTable from './DistrictTable'
import { useCatalystSignals } from '@/hooks/useCatalystSignals'
import { useRoleVoice } from '@/hooks/useRoleVoice'
import { fetchDistricts, fetchForecast, fetchStats } from '@/api/endpoints'
import policeEmblem from '@/assets/police.png'

export default function AnalystDashboard() {
  const { alerts, clearAlerts } = useCatalystSignals()
  const voice = useRoleVoice()

  const [districts,  setDistricts]  = useState(null)
  const [forecast,   setForecast]   = useState(null)
  const [stats,      setStats]      = useState(null)
  const [loadingMap, setLoadingMap] = useState(true)

  useEffect(() => {
    let cancelled = false
    Promise.allSettled([fetchDistricts(), fetchForecast(), fetchStats()]).then(([dRes, fRes, sRes]) => {
      if (cancelled) return
      if (dRes.status === 'fulfilled') setDistricts(dRes.value)
      if (fRes.status === 'fulfilled') setForecast(fRes.value)
      if (sRes.status === 'fulfilled') setStats(sRes.value.data)
      setLoadingMap(false)
    })
    return () => { cancelled = true }
  }, [])

  const getStatValue = (key, mock) => {
    if (!stats) return mock;
    switch (key) {
      case 'activeFirs': return stats.total_firs?.toLocaleString() || mock;
      case 'avgRisk': return stats.avg_risk_score ? `${stats.avg_risk_score} / 100` : mock;
      case 'anomalyCount': return stats.anomaly_count?.toLocaleString() || mock;
      case 'p95Latency': return stats.api_latency_ms || mock;
      default: return mock;
    }
  }

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8 space-y-5">

      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <img
            src={policeEmblem}
            alt="KSP"
            className="w-10 h-10 object-contain opacity-80"
            style={{ filter: 'drop-shadow(0 0 6px rgba(201,162,39,0.4))' }}
          />
          <div>
            <h1 className="font-display font-bold text-ink leading-tight">Command Center</h1>
            <div className="text-[10px] font-mono uppercase tracking-widest text-ink-dim">
              Karnataka State Police &mdash; Intelligence Analytics
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="case-tag">
            {import.meta.env.VITE_API_BASE_URL ? 'Live Data' : 'Mock Data'}
          </span>
          <div
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-mono uppercase tracking-wider"
            style={{ background: 'rgba(201,162,39,0.08)', border: '1px solid rgba(201,162,39,0.2)', color: '#C9A227' }}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#C9A227] animate-pulse" />
            ವಿಶ್ಲೇಷಕ / Analyst Session
          </div>
        </div>
      </div>

      {/* ── KPI stat cards ─────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {voice.stats.map((s) => (
          <StatCard
            key={s.key}
            label={s.label}
            value={getStatValue(s.key, s.mock)}
            tag={s.tag}
            alert={s.alert}
          />
        ))}
      </div>

      {/* ── Chart row: SARIMA forecast + anomaly feed ───────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="panel p-5 lg:col-span-2">
          <div className="flex items-start justify-between mb-4 gap-2">
            <div>
              <h2 className="font-display text-sm tracking-wide text-ink-dim uppercase">
                {voice.chartTitle}
              </h2>
              {voice.chartSubtitle && (
                <p className="text-[11px] text-ink-dim/70 mt-0.5">{voice.chartSubtitle}</p>
              )}
            </div>
            {voice.chartTag && <span className="case-tag shrink-0">{voice.chartTag}</span>}
          </div>
          <ForecastChart data={forecast} isLoading={loadingMap && !forecast} />
        </div>

        <AnomalyFeed alerts={alerts} onClear={clearAlerts} />
      </div>

      {/* ── District risk table ─────────────────────────────────── */}
      <DistrictTable districts={districts} isLoading={loadingMap && !districts} />
    </div>
  )
}

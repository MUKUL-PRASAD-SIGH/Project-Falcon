import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import StatCard from './StatCard'
import ForecastChart from './ForecastChart'
import AnomalyFeed from './AnomalyFeed'
import DistrictTable from './DistrictTable'
import CitationChip from '@/components/Chat/CitationChip'
import { useCatalystSignals } from '@/hooks/useCatalystSignals'
import { useRoleVoice, getTimeOfDay } from '@/hooks/useRoleVoice'
import { useAuth } from '@/context/AuthContext'
import { fetchDistricts, fetchForecast, fetchStats, fetchClusters } from '@/api/endpoints'
import policeEmblem from '@/assets/police.png'

// Fix Leaflet icon paths
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const KARNATAKA_CENTER = [14.5, 75.7]
const RISK_COLORS = { High: '#D8503A', Medium: '#C9A227', Low: '#4A9EDB' }
const MOCK_CLUSTERS = [
  { id: 'C001', lat: 12.95, lng: 77.64, risk: 'High',   label: 'Electronic City',  count: 47, crimeHead: 'Property' },
  { id: 'C002', lat: 12.98, lng: 77.59, risk: 'High',   label: 'Whitefield',       count: 38, crimeHead: 'Property' },
  { id: 'C003', lat: 12.97, lng: 77.56, risk: 'High',   label: 'MG Road',          count: 31, crimeHead: 'Crimes Against Body' },
  { id: 'C004', lat: 12.30, lng: 76.65, risk: 'Medium', label: 'Mysuru Central',   count: 22, crimeHead: 'Public Order' },
  { id: 'C005', lat: 12.91, lng: 74.86, risk: 'Medium', label: 'Mangaluru Port',   count: 18, crimeHead: 'Cyber' },
  { id: 'C006', lat: 15.86, lng: 74.50, risk: 'Low',    label: 'Belagavi Market',  count: 11, crimeHead: 'Property' },
  { id: 'C007', lat: 17.33, lng: 76.82, risk: 'Low',    label: 'Kalaburagi North', count: 8,  crimeHead: 'Crimes Against Body' },
  { id: 'C008', lat: 13.32, lng: 77.10, risk: 'High',   label: 'Tumakuru bypass',  count: 29, crimeHead: 'Property' },
]

function FlyTo({ target }) {
  const map = useMap()
  useEffect(() => { if (target) map.flyTo(target, 12, { duration: 1.2 }) }, [target, map])
  return null
}

/* ─────────────────────────────────────────────────────────────────────────── */
/*  TABS — what sections are visible in the main area below the hero map       */
/* ─────────────────────────────────────────────────────────────────────────── */
const TABS = ['Overview', 'Districts', 'Forecast']

export default function Dashboard() {
  const { alerts, clearAlerts } = useCatalystSignals()
  const voice = useRoleVoice()
  const { user } = useAuth()
  const [activeTab,    setActiveTab]    = useState('Overview')
  const [flyTarget,    setFlyTarget]    = useState(null)
  const [drillCluster, setDrillCluster] = useState(null)
  const [districts,    setDistricts]    = useState(null)
  const [forecast,     setForecast]     = useState(null)
  const [stats,        setStats]        = useState(null)
  const [clusters,     setClusters]     = useState(null)
  const [loadingMap,   setLoadingMap]   = useState(true)

  useEffect(() => {
    let cancelled = false
    Promise.allSettled([fetchDistricts(), fetchForecast(), fetchStats(), fetchClusters()]).then(([dRes, fRes, sRes, cRes]) => {
      if (cancelled) return
      if (dRes.status === 'fulfilled') setDistricts(dRes.value)
      if (fRes.status === 'fulfilled') setForecast(fRes.value)
      if (sRes.status === 'fulfilled') setStats(sRes.value.data)
      if (cRes.status === 'fulfilled') setClusters(cRes.value.features || [])
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
      case 'p95Latency': return voice.roleLabel === 'Field Investigator' ? stats.system_status : stats.api_latency_ms;
      default: return mock;
    }
  }

  const officerName = (user?.firstName && user.firstName !== 'Dev') ? user.firstName : 'Officer'

  return (
    <div className="flex flex-col" style={{ minHeight: 'calc(100vh - 52px)' }}>

      {/* ═══════════════════════════════════════════════════════════════════ */}
      {/*  HERO SECTION — Full-width map with overlaid header                */}
      {/* ═══════════════════════════════════════════════════════════════════ */}
      <div className="relative flex-none" style={{ height: '62vh' }}>

        {/* Leaflet map fills the entire hero */}
        <MapContainer
          center={KARNATAKA_CENTER}
          zoom={7}
          style={{ height: '100%', width: '100%' }}
          zoomControl={false}
        >
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {flyTarget && <FlyTo target={flyTarget} />}
          {(clusters || MOCK_CLUSTERS).map((c) => {
            const isMock = !c.properties;
            const lat = isMock ? c.lat : c.geometry.coordinates[1];
            const lng = isMock ? c.lng : c.geometry.coordinates[0];
            const id = isMock ? c.id : c.properties.cluster_id;
            const risk = isMock ? c.risk : c.properties.risk_level;
            const label = isMock ? c.label : c.properties.district;
            const count = isMock ? c.count : c.properties.incident_count;
            const crimeHead = isMock ? c.crimeHead : c.properties.crime_type;
            return (
            <CircleMarker
              key={id}
              center={[lat, lng]}
              radius={risk === 'High' ? 14 : risk === 'Medium' ? 10 : 7}
              pathOptions={{
                color:       RISK_COLORS[risk] || RISK_COLORS['Medium'],
                fillColor:   RISK_COLORS[risk] || RISK_COLORS['Medium'],
                fillOpacity: 0.45,
                weight:      risk === 'High' ? 2.5 : 1.5,
              }}
              eventHandlers={{ click: () => { 
                const data = { id, lat, lng, risk, label, count, crimeHead }
                setDrillCluster(data); 
                setFlyTarget([lat, lng]) 
              } }}
            >
              <Popup>
                <div className="text-sm font-semibold">{label}</div>
                <div className="text-xs text-gray-400 mt-0.5">{crimeHead} · {count} FIRs</div>
                <div className="mt-1.5"><CitationChip firId={id} /></div>
              </Popup>
            </CircleMarker>
            )
          })}
        </MapContainer>

        {/* Gradient vignette — bottom fade so content below reads cleanly */}
        <div
          className="absolute bottom-0 left-0 right-0 h-28 pointer-events-none z-[400]"
          style={{ background: 'linear-gradient(to bottom, transparent 0%, #060D1A 100%)' }}
        />

        {/* ── Top overlay bar ────────────────────────────────────────────── */}
        <div className="absolute top-0 left-0 right-0 z-[500] pointer-events-none">
          <div
            className="px-6 py-4 flex items-center justify-between"
            style={{ background: 'linear-gradient(to bottom, rgba(4,9,20,0.85) 0%, transparent 100%)' }}
          >
            {/* Left: emblem + title */}
            <div className="flex items-center gap-4 pointer-events-auto">
              <img
                src={policeEmblem}
                alt="KSP"
                className="w-10 h-10 object-contain"
                style={{ filter: 'drop-shadow(0 0 8px rgba(201,162,39,0.5)) brightness(1.1)' }}
              />
              <div>
                <div className="font-display text-lg font-bold tracking-widest text-white uppercase leading-tight">
                  Karnataka State Police
                </div>
                <div className="text-[10px] font-mono tracking-widest uppercase" style={{ color: 'var(--role-accent)' }}>
                  Project Falcon &mdash; {voice.roleLabel}
                </div>
              </div>
            </div>

            {/* Right: quick stat badges */}
            <div className="flex items-center gap-3 pointer-events-auto">
              {voice.stats.slice(0, 3).map((s) => (
                <div
                  key={s.key}
                  className="px-3 py-1.5 rounded-lg text-center"
                  style={{
                    background: 'rgba(4,9,20,0.7)',
                    border: `1px solid ${s.alert ? 'rgba(216,80,58,0.4)' : 'rgba(255,255,255,0.1)'}`,
                    backdropFilter: 'blur(8px)',
                  }}
                >
                  <div className={`font-display text-base font-bold leading-tight ${s.alert ? 'text-[#D8503A]' : 'text-white'}`}>
                    {getStatValue(s.key, s.mock)}
                  </div>
                  <div className="text-[9px] font-mono uppercase tracking-wider text-gray-400 mt-0.5">
                    {s.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Active cluster drill-down card ──────────────────────────────── */}
        {drillCluster && (
          <div
            className="absolute bottom-8 left-6 z-[500] rounded-xl p-4 min-w-[220px]"
            style={{
              background: 'rgba(4,9,20,0.88)',
              border: `1px solid ${RISK_COLORS[drillCluster.risk]}55`,
              backdropFilter: 'blur(16px)',
            }}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-sm font-semibold text-white">{drillCluster.label}</div>
                <div className="text-xs text-gray-400 mt-0.5">{drillCluster.crimeHead}</div>
                <div
                  className="text-xs font-mono font-semibold mt-2 px-2 py-0.5 rounded inline-block"
                  style={{ color: RISK_COLORS[drillCluster.risk], background: `${RISK_COLORS[drillCluster.risk]}18` }}
                >
                  {drillCluster.risk} Risk &mdash; {drillCluster.count} FIRs
                </div>
              </div>
              <button
                onClick={() => setDrillCluster(null)}
                className="text-gray-500 hover:text-white text-xs font-mono"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* ── Risk legend (bottom-right of map) ───────────────────────────── */}
        <div
          className="absolute bottom-8 right-6 z-[500] rounded-xl px-4 py-3 space-y-1.5"
          style={{ background: 'rgba(4,9,20,0.75)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(12px)' }}
        >
          {Object.entries(RISK_COLORS).map(([tier, color]) => (
            <div key={tier} className="flex items-center gap-2 text-[11px] text-gray-400">
              <span className="w-2 h-2 rounded-full shrink-0" style={{ background: color }} />
              {tier} Risk
            </div>
          ))}
        </div>

        {/* ── Greeting (Investigator only, bottom-left) ───────────────────── */}
        {voice.showGreeting && (
          <div
            className="absolute bottom-8 left-1/2 -translate-x-1/2 z-[500] rounded-xl px-5 py-3 text-center"
            style={{ background: 'rgba(4,9,20,0.75)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(12px)' }}
          >
            <h1 className="font-display font-bold text-ink">
              Good {getTimeOfDay()}, {officerName}.
            </h1>
            <p className="text-sm text-ink-dim mt-1 max-w-md">
              Here's today's operations overview for Karnataka State Police.
            </p>
            <p className="text-[10px] text-ink-dim/60 font-mono mt-1">
              ಕರ್ನಾಟಕ ರಾಜ್ಯ ಪೊಲೀಸ್ — ಇಂದಿನ ಕಾರ್ಯಾಚರಣೆ ಅವಲೋಕನ
            </p>
          </div>
        )}
      </div>

      {/* ═══════════════════════════════════════════════════════════════════ */}
      {/*  CONTENT AREA — Tab-switched panels below the map                  */}
      {/* ═══════════════════════════════════════════════════════════════════ */}
      <div className="flex-1 px-6 pb-8 -mt-2">

        {/* Section tab bar */}
        <div className="flex items-center justify-between mb-5">
          <div
            className="flex items-center gap-1 p-1 rounded-xl"
            style={{ background: 'rgba(9,16,33,0.8)', border: '1px solid rgba(255,255,255,0.07)' }}
          >
            {TABS.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className="px-4 py-1.5 rounded-lg text-sm font-medium transition-all"
                style={
                  activeTab === tab
                    ? { background: 'var(--role-accent)', color: '#060D1A' }
                    : { color: '#93A0B8' }
                }
              >
                {tab}
              </button>
            ))}
          </div>
          <span className="case-tag">{import.meta.env.VITE_API_BASE_URL ? 'Live Data' : 'Mock Data'}</span>
        </div>

        {/* ── Overview Tab ─────────────────────────────────────────────── */}
        {activeTab === 'Overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Stat cards — 2×2 left column */}
            <div className="lg:col-span-1 grid grid-cols-2 lg:grid-cols-1 gap-4">
              {voice.stats.map((s) => (
                <StatCard key={s.key} label={s.label} value={getStatValue(s.key, s.mock)} tag={s.tag} alert={s.alert} />
              ))}
            </div>

            {/* Anomaly feed — right 2 columns */}
            <div className="lg:col-span-2">
              <AnomalyFeed alerts={alerts} onClear={clearAlerts} />
            </div>
          </div>
        )}

        {/* ── Districts Tab ─────────────────────────────────────────────── */}
        {activeTab === 'Districts' && (
          <DistrictTable districts={districts} isLoading={loadingMap && !districts} />
        )}

        {/* ── Forecast Tab ─────────────────────────────────────────────── */}
        {activeTab === 'Forecast' && (
          <div className="panel p-5">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="font-display text-sm tracking-wide text-ink-dim uppercase">{voice.chartTitle}</h2>
                {voice.chartSubtitle && <p className="text-[11px] text-ink-dim/70 mt-0.5">{voice.chartSubtitle}</p>}
              </div>
              {voice.chartTag && <span className="case-tag">{voice.chartTag}</span>}
            </div>
            <ForecastChart data={forecast} isLoading={loadingMap && !forecast} />
          </div>
        )}
      </div>
    </div>
  )
}

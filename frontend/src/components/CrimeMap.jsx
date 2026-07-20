import { useState, useEffect, useRef } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import CitationChip from '@/components/Chat/CitationChip'
import LoadingSkeleton from '@/components/common/LoadingSkeleton'

// Fix Leaflet default icon paths broken by Vite bundling
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png'
})

const KARNATAKA_CENTER = [14.5, 75.7]
const DEFAULT_ZOOM     = 7
const TIME_BUCKETS     = ['All', 'AM', 'PM', 'Night']
const CRIME_HEADS      = ['All', 'Crimes Against Body', 'Property', 'Public Order', 'Cyber']
const RISK_COLORS      = { High: '#D8503A', Medium: '#C9A227', Low: '#4A9EDB' }

const MOCK_CLUSTERS = [
  { id: 'C001', lat: 12.95, lng: 77.64, risk: 'High',   label: 'Electronic City',   count: 47, fir: '104430006202600231', crimeHead: 'Property' },
  { id: 'C002', lat: 12.98, lng: 77.59, risk: 'High',   label: 'Whitefield',        count: 38, fir: '104430006202600198', crimeHead: 'Property' },
  { id: 'C003', lat: 12.97, lng: 77.56, risk: 'High',   label: 'MG Road',           count: 31, fir: '104430006202600155', crimeHead: 'Crimes Against Body' },
  { id: 'C004', lat: 12.30, lng: 76.65, risk: 'Medium', label: 'Mysuru Central',    count: 22, fir: '104430006202600210', crimeHead: 'Public Order' },
  { id: 'C005', lat: 12.91, lng: 74.86, risk: 'Medium', label: 'Mangaluru Port',    count: 18, fir: '104430006202600175', crimeHead: 'Cyber' },
  { id: 'C006', lat: 15.86, lng: 74.50, risk: 'Low',    label: 'Belagavi Market',   count: 11, fir: '104430006202600190', crimeHead: 'Property' },
  { id: 'C007', lat: 17.33, lng: 76.82, risk: 'Low',    label: 'Kalaburagi North',  count: 8,  fir: '104430006202600201', crimeHead: 'Crimes Against Body' },
  { id: 'C008', lat: 13.32, lng: 77.10, risk: 'High',   label: 'Tumakuru Bypass',   count: 29, fir: '104430006202600220', crimeHead: 'Property' }
]

function FlyTo({ target }) {
  const map = useMap()
  useEffect(() => { if (target) map.flyTo(target, 12, { duration: 1.2 }) }, [target, map])
  return null
}

export default function CrimeMap() {
  const [activeTime,    setActiveTime]    = useState('All')
  const [activeHeads,   setActiveHeads]   = useState(new Set(['All']))
  const [clusters,      setClusters]      = useState(MOCK_CLUSTERS)
  const [drillDistrict, setDrillDistrict] = useState(null)
  const [flyTarget,     setFlyTarget]     = useState(null)
  const [loading,       setLoading]       = useState(false)
  const [sidebarOpen,   setSidebarOpen]   = useState(true)

  useEffect(() => {
    const url = import.meta.env.VITE_STRATUS_CLUSTERS_URL
    if (!url) return
    setLoading(true)
    fetch(`${url}${activeTime !== 'All' ? `?time=${activeTime}` : ''}`)
      .then((r) => r.json())
      .then((data) => { setClusters(data.features ?? data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [activeTime])

  function toggleHead(head) {
    setActiveHeads((prev) => {
      const next = new Set(prev)
      if (head === 'All') return new Set(['All'])
      next.delete('All')
      next.has(head) ? next.delete(head) : next.add(head)
      if (next.size === 0) return new Set(['All'])
      return next
    })
  }

  const visible = clusters.filter((c) =>
    activeHeads.has('All') || activeHeads.has(c.crimeHead)
  )

  function handleMarkerClick(cluster) {
    setDrillDistrict(cluster)
    setFlyTarget([cluster.lat, cluster.lng])
  }

  return (
    /* Full-bleed layout — no max-w constraint so the map fills the page */
    <div className="flex flex-col" style={{ height: 'calc(100vh - 52px)' }}>

      {/* ── Page title bar ──────────────────────────────────────────── */}
      <div
        className="flex items-center justify-between px-6 py-3 shrink-0"
        style={{ borderBottom: '1px solid rgba(255,255,255,0.07)', background: 'rgba(4,9,20,0.7)', backdropFilter: 'blur(8px)' }}
      >
        <div>
          <h1 className="font-display text-lg font-bold tracking-wide text-ink">Crime Map</h1>
          <div className="text-[9px] font-mono uppercase tracking-widest text-ink-dim">
            ಅಪರಾಧ ನಕ್ಷೆ · AppSail · DBSCAN + K-Means
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="case-tag">Karnataka</span>
          <button
            onClick={() => setSidebarOpen((o) => !o)}
            className="btn-ghost text-xs py-1 px-3"
          >
            {sidebarOpen ? 'Hide Filters' : 'Show Filters'}
          </button>
        </div>
      </div>

      {/* ── Main content: map + optional sidebar ───────────────────── */}
      <div className="flex flex-col md:flex-row flex-1 overflow-hidden relative">

        {/* MAP — fills all remaining space */}
        <div className="flex-1 relative overflow-hidden min-h-[40vh] md:min-h-0">
          {loading ? (
            <LoadingSkeleton className="h-full w-full" />
          ) : (
            <MapContainer
              center={KARNATAKA_CENTER}
              zoom={DEFAULT_ZOOM}
              style={{ height: '100%', width: '100%' }}
              zoomControl={true}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://openstreetmap.org">OpenStreetMap</a>'
              />
              {flyTarget && <FlyTo target={flyTarget} />}
              {visible.map((c) => (
                <CircleMarker
                  key={c.id}
                  center={[c.lat, c.lng]}
                  radius={c.risk === 'High' ? 15 : c.risk === 'Medium' ? 11 : 8}
                  pathOptions={{
                    color:       RISK_COLORS[c.risk],
                    fillColor:   RISK_COLORS[c.risk],
                    fillOpacity: 0.45,
                    weight:      c.risk === 'High' ? 2.5 : 1.5
                  }}
                  eventHandlers={{ click: () => handleMarkerClick(c) }}
                >
                  <Popup>
                    <div className="text-sm font-semibold">{c.label}</div>
                    <div className="text-xs text-gray-400 mt-0.5">{c.crimeHead} · {c.count} FIRs</div>
                    <div className="mt-2"><CitationChip firId={c.fir} /></div>
                  </Popup>
                </CircleMarker>
              ))}
            </MapContainer>
          )}

          {/* Drill-down card — floating over the map bottom-left */}
          {drillDistrict && (
            <div
              className="absolute bottom-6 left-4 z-[500] rounded-xl p-4 min-w-[210px] max-w-[260px]"
              style={{
                background: 'rgba(4,9,20,0.88)',
                border: `1px solid ${RISK_COLORS[drillDistrict.risk]}55`,
                backdropFilter: 'blur(16px)',
              }}
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="text-sm font-semibold text-white">{drillDistrict.label}</div>
                  <div className="text-xs text-gray-400 mt-0.5">{drillDistrict.crimeHead}</div>
                  <div
                    className="text-xs font-mono font-semibold mt-2 px-2 py-0.5 rounded inline-block"
                    style={{ color: RISK_COLORS[drillDistrict.risk], background: `${RISK_COLORS[drillDistrict.risk]}20` }}
                  >
                    {drillDistrict.risk} Risk &mdash; {drillDistrict.count} FIRs
                  </div>
                  <div className="mt-2"><CitationChip firId={drillDistrict.fir} /></div>
                </div>
                <button
                  onClick={() => setDrillDistrict(null)}
                  className="text-gray-500 hover:text-white text-xs font-mono mt-0.5"
                >✕</button>
              </div>
            </div>
          )}

          {/* Risk legend — floating bottom-right of map */}
          <div
            className="absolute bottom-6 right-4 z-[500] rounded-xl px-4 py-3 space-y-1.5"
            style={{ background: 'rgba(4,9,20,0.75)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(12px)' }}
          >
            <div className="text-[9px] uppercase tracking-widest text-gray-500 mb-2 font-mono">ಅಪಾಯ ಮಟ್ಟ / Risk</div>
            {Object.entries(RISK_COLORS).map(([tier, color]) => (
              <div key={tier} className="flex items-center gap-2 text-[11px] text-gray-400">
                <span className="w-2 h-2 rounded-full shrink-0" style={{ background: color }} />
                {tier}
              </div>
            ))}
          </div>
        </div>

        {/* SIDEBAR — slides in/out, overlaps the map on the right */}
        <div
          className={`shrink-0 overflow-y-auto scroll-thin transition-all duration-200 space-y-3
            ${sidebarOpen ? 'w-full md:w-[240px] h-[35vh] md:h-full p-4 border-t md:border-t-0 md:border-l' : 'w-0 h-0 p-0 overflow-hidden'}
          `}
          style={{
            background: 'rgba(4,9,20,0.85)',
            backdropFilter: 'blur(16px)',
            borderColor: 'rgba(255,255,255,0.07)',
          }}
        >
          {sidebarOpen && (
            <>
              {/* Time of day */}
              <div>
                <div className="text-[10px] uppercase tracking-widest text-ink-dim mb-2 font-mono">Time of Day</div>
                <div className="flex flex-wrap gap-1.5">
                  {TIME_BUCKETS.map((t) => (
                    <button
                      key={t}
                      onClick={() => setActiveTime(t)}
                      className="text-xs px-2.5 py-1 rounded-md border transition-all"
                      style={
                        activeTime === t
                          ? { borderColor: 'var(--role-accent)', color: 'var(--role-accent)', background: 'var(--role-accent-dim)' }
                          : { borderColor: 'rgba(255,255,255,0.1)', color: '#93A0B8' }
                      }
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              {/* Crime head filter */}
              <div>
                <div className="text-[10px] uppercase tracking-widest text-ink-dim mb-2 font-mono">Crime Head</div>
                <div className="space-y-2">
                  {CRIME_HEADS.map((c) => (
                    <label key={c} className="flex items-center gap-2 text-sm text-ink-dim cursor-pointer hover:text-ink transition-colors">
                      <input
                        type="checkbox"
                        checked={c === 'All' ? activeHeads.has('All') : activeHeads.has(c)}
                        onChange={() => toggleHead(c)}
                        className="accent-[#C9A227] w-3.5 h-3.5"
                      />
                      {c}
                    </label>
                  ))}
                </div>
              </div>

              {/* Active filter summary */}
              <div
                className="rounded-lg px-3 py-2"
                style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}
              >
                <div className="text-[10px] uppercase tracking-widest text-ink-dim mb-1 font-mono">
                  Visible Clusters
                </div>
                <div className="font-display text-2xl font-bold" style={{ color: 'var(--role-accent)' }}>
                  {visible.length}
                </div>
                <div className="text-[10px] text-ink-dim mt-0.5">of {clusters.length} total</div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

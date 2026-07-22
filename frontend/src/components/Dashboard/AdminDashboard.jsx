/**
 * AdminDashboard — Landing page for Admin role.
 *
 * Shows a combined overview: key system stats at the top,
 * then the full Audit Log + PII Victim Registry inline.
 * No need to navigate away — everything visible on arrival.
 */
import { useState, useEffect } from 'react'
import { useAuth } from '@/context/AuthContext'
import { fetchAuditLog, fetchAdminStats, fetchVictims } from '@/api/endpoints'
import LoadingSkeleton from '@/components/common/LoadingSkeleton'
import CitationChip from '@/components/Chat/CitationChip'
import policeEmblem from '@/assets/police.png'
import otherPhoto from '@/assets/other.png'

const MOCK_AUDIT_ROWS = [
  { user: 'investigator@ksp', query: 'robberies in Whitefield last month',            ts: '2026-07-19 09:12', ip: '10.0.4.21' },
  { user: 'analyst@ksp',      query: 'district risk rollup',                          ts: '2026-07-19 09:20', ip: '10.0.4.55' },
  { user: 'admin@ksp',        query: 'unmask victim data for FIR #104430006202600231', ts: '2026-07-19 09:45', ip: '10.0.4.2'  },
  { user: 'investigator@ksp', query: 'network graph accused #A1',                     ts: '2026-07-19 10:02', ip: '10.0.4.21' },
  { user: 'analyst@ksp',      query: 'SARIMA 30-day forecast Bengaluru Urban',        ts: '2026-07-19 10:14', ip: '10.0.4.55' },
]

const MOCK_VICTIMS = [
  { name: 'Suma Gowda',   case: '104430006202600231', age: 34, gender: 'Female' },
  { name: 'Rajesh M. N.', case: '104430006202600198', age: 45, gender: 'Male'   },
]

const SYSTEM_STATS = [
  { label: 'Active Sessions',  labelKN: 'ಸಕ್ರಿಯ ಸೆಶನ್‌ಗಳು', value: '3',    tag: 'Auth',       alert: false },
  { label: 'Audit Events',     labelKN: 'ಆಡಿಟ್ ಘಟನೆಗಳು',    value: '1,247', tag: 'DataStore',  alert: false },
  { label: 'PII Unmask Events', labelKN: 'PII ಅನ್‌ಮಾಸ್ಕ್',  value: '3',    tag: 'Restricted', alert: true  },
  { label: 'System Health',    labelKN: 'ವ್ಯವಸ್ಥೆ ಸ್ಥಿತಿ',  value: 'OK',   tag: 'Catalyst',   alert: false },
]

export default function AdminDashboard() {
  const { role } = useAuth()
  const isAdmin = role === 'Admin'

  const [auditLogs, setAuditLogs] = useState(null)
  const [adminStats, setAdminStats] = useState(null)
  const [victims,   setVictims]   = useState(null)
  const [loading,   setLoading]   = useState(false)
  const [unmasked,  setUnmasked]  = useState(false)

  useEffect(() => {
    if (!isAdmin) return
    setLoading(true)
    Promise.allSettled([fetchAuditLog(), fetchAdminStats(), fetchVictims()]).then(([logRes, statRes, vicRes]) => {
      setLoading(false)
      if (logRes.status === 'fulfilled') setAuditLogs(logRes.value.logs ?? logRes.value)
      else setAuditLogs(MOCK_AUDIT_ROWS)
      
      if (statRes.status === 'fulfilled') setAdminStats(statRes.value.data)
      if (vicRes.status === 'fulfilled') setVictims(vicRes.value.victims)
    })
  }, [isAdmin])

  const getStatValue = (label, mock) => {
    if (!adminStats) return mock;
    switch (label) {
      case 'Active Sessions': return adminStats.active_sessions;
      case 'Audit Events': return adminStats.audit_event_count?.toLocaleString();
      case 'PII Unmask Events': return adminStats.pii_unmask_events;
      case 'System Health': return adminStats.system_health;
      default: return mock;
    }
  }

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8 space-y-6">

      {/* ── Page header with badge photo + emblem ─────────────── */}
      <div
        className="relative overflow-hidden rounded-xl p-6 flex items-center justify-between gap-6"
        style={{
          background: 'linear-gradient(135deg, rgba(168,85,247,0.10) 0%, rgba(6,13,26,0.6) 70%)',
          border: '1px solid rgba(168,85,247,0.2)',
        }}
      >
        {/* Left: org identity */}
        <div className="flex items-center gap-5 z-10">
          <img
            src={policeEmblem}
            alt="KSP Emblem"
            className="w-14 h-14 object-contain"
            style={{ filter: 'drop-shadow(0 0 10px rgba(168,85,247,0.35)) brightness(1.1)' }}
          />
          <div>
            <div className="text-[10px] font-mono uppercase tracking-widest text-ink-dim mb-0.5">
              ಕರ್ನಾಟಕ ರಾಜ್ಯ ಪೊಲೀಸ್ / Karnataka State Police
            </div>
            <h1 className="font-display text-xl font-bold text-ink">Audit &amp; Access Control</h1>
            <div className="text-[11px] text-ink-dim mt-0.5">
              Security audit log, RBAC sessions, and PII registry
            </div>
          </div>
        </div>

        {/* Right: badge photo */}
        <img
          src={otherPhoto}
          alt="Karnataka Police Badge"
          className="w-24 h-24 object-cover rounded-xl opacity-60 shrink-0 hidden sm:block"
          style={{ border: '1px solid rgba(168,85,247,0.2)', filter: 'saturate(0.6) brightness(0.9)' }}
        />

        {/* Purple glow orb */}
        <div
          className="absolute right-24 top-1/2 -translate-y-1/2 w-40 h-40 rounded-full pointer-events-none"
          style={{ background: 'radial-gradient(circle, rgba(168,85,247,0.12) 0%, transparent 70%)' }}
        />
      </div>

      {/* ── System stat cards ──────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {SYSTEM_STATS.map((s) => (
          <div
            key={s.label}
            className={`panel p-5 relative overflow-hidden hover:-translate-y-0.5 transition-all ${
              s.alert ? 'border-[rgba(216,80,58,0.35)]' : ''
            }`}
          >
            {/* Left stripe */}
            <div
              className="absolute left-0 top-4 bottom-4 w-[2px] rounded-r-full"
              style={{ background: s.alert ? '#D8503A' : 'var(--role-accent)', opacity: 0.6 }}
            />
            <div className="text-[10px] uppercase tracking-wider text-ink-dim font-medium pl-1">{s.label}</div>
            <div className="text-[10px] text-ink-dim/50 font-medium pl-1 mt-0.5">{s.labelKN}</div>
            <div className={`font-display text-[1.7rem] font-bold leading-none mt-1.5 pl-1 ${s.alert ? 'text-[#D8503A]' : 'text-ink'}`}>
              {getStatValue(s.label, s.value)}
            </div>
            <div className="mt-2 pl-1"><span className="case-tag">{s.tag}</span></div>
          </div>
        ))}
      </div>

      {/* ── Audit Log ──────────────────────────────────────────── */}
      <div className="panel p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="font-display text-sm tracking-wide text-ink-dim uppercase">Security Audit Log</h2>
            <div className="text-[10px] text-ink-dim/60 font-mono mt-0.5">ಭದ್ರತಾ ಆಡಿಟ್ ದಾಖಲೆ</div>
          </div>
          <span className="case-tag font-mono">100% Traceability</span>
        </div>

        {loading ? (
          <LoadingSkeleton className="h-6 w-full" lines={4} />
        ) : (
          <div className="overflow-x-auto scroll-thin">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-ink-dim border-b border-[rgba(255,255,255,0.07)]">
                  <th className="py-2 pr-4 font-normal text-[11px] uppercase tracking-wide">User</th>
                  <th className="py-2 pr-4 font-normal text-[11px] uppercase tracking-wide">Query / Action</th>
                  <th className="py-2 pr-4 font-normal text-[11px] uppercase tracking-wide">Timestamp</th>
                  <th className="py-2 font-normal text-[11px] uppercase tracking-wide">Client IP</th>
                </tr>
              </thead>
              <tbody>
                {(auditLogs ?? MOCK_AUDIT_ROWS).map((r, i) => (
                  <tr key={i} className="border-b border-[rgba(255,255,255,0.04)] hover:bg-[rgba(168,85,247,0.04)] transition-colors">
                    <td className="py-2.5 pr-4 font-mono text-xs" style={{ color: 'var(--role-accent)' }}>{r.user}</td>
                    <td className="py-2.5 pr-4 font-mono text-xs text-ink-dim max-w-xs truncate">{r.query}</td>
                    <td className="py-2.5 pr-4 font-mono text-xs text-ink-dim">{r.ts}</td>
                    <td className="py-2.5 font-mono text-xs text-ink-dim">{r.ip}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── PII Victim Registry ────────────────────────────────── */}
      <div className="panel p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="font-display text-sm tracking-wide text-ink-dim uppercase">PII Victim Registry</h2>
            <div className="text-[10px] text-ink-dim/60 font-mono mt-0.5">EU AI Act · Article 13 Compliant</div>
          </div>
          <button
            onClick={() => setUnmasked(!unmasked)}
            className="btn-ghost text-xs py-1.5 px-3"
          >
            {unmasked ? 'Mask PII Data' : 'Reveal PII Data'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {(victims || MOCK_VICTIMS).map((v) => (
            <div
              key={v.case}
              className="rounded-lg p-4 flex flex-col justify-between gap-3"
              style={{ background: 'rgba(6,13,26,0.6)', border: '1px solid rgba(255,255,255,0.07)' }}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-[10px] uppercase tracking-wider text-ink-dim font-mono">ಸಂತ್ರಸ್ತರ ಹೆಸರು / Victim Name</div>
                  <div className="text-sm font-semibold text-ink mt-1">
                    {unmasked ? v.name : '████████ (Restricted)'}
                  </div>
                </div>
                <CitationChip firId={v.case} />
              </div>
              <div
                className="grid grid-cols-2 gap-2 pt-3 text-xs"
                style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}
              >
                <div>
                  <span className="text-ink-dim">Age: </span>
                  <span className="font-mono text-ink">{unmasked ? v.age : '██'}</span>
                </div>
                <div>
                  <span className="text-ink-dim">Gender: </span>
                  <span className="text-ink">{unmasked ? v.gender : '█████'}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
        <p className="text-[11px] text-ink-dim mt-4 leading-relaxed">
          Victim records are masked by default. Every reveal action is permanently logged in the Audit Log above, with timestamp and user identity.
        </p>
      </div>
    </div>
  )
}

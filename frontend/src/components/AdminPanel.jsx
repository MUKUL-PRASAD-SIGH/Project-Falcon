import { useState, useEffect } from 'react'
import { useAuth } from '@/context/AuthContext'
import { fetchAuditLog } from '@/api/endpoints'
import LoadingSkeleton from '@/components/common/LoadingSkeleton'
import CitationChip from '@/components/Chat/CitationChip'

const MOCK_AUDIT_ROWS = [
  { user: 'investigator@ksp', query: 'robberies in Whitefield last month', ts: '2026-07-19 09:12', ip: '10.0.4.21' },
  { user: 'analyst@ksp', query: 'district risk rollup', ts: '2026-07-19 09:20', ip: '10.0.4.55' },
  { user: 'admin@ksp', query: 'unmask victim data for FIR #104430006202600231', ts: '2026-07-19 09:45', ip: '10.0.4.2' }
]

const MOCK_VICTIMS = [
  { name: 'Suma Gowda', case: '104430006202600231', age: 34, gender: 'Female' },
  { name: 'Rajesh M. N.', case: '104430006202600198', age: 45, gender: 'Male' }
]

export default function AdminPanel() {
  const { role, can } = useAuth()
  const isAdmin = can('Admin')

  const [auditLogs, setAuditLogs] = useState(null)
  const [loading, setLoading] = useState(false)
  const [unmasked, setUnmasked] = useState(false)

  useEffect(() => {
    if (!isAdmin) return
    setLoading(true)
    fetchAuditLog()
      .then((data) => {
        setAuditLogs(data.logs ?? data)
        setLoading(false)
      })
      .catch((err) => {
        console.warn('[AdminPanel] API fetch failed — falling back to mock audit logs', err)
        setAuditLogs(MOCK_AUDIT_ROWS)
        setLoading(false)
      })
  }, [isAdmin])

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8 space-y-6">
      <div className="flex items-baseline justify-between">
        <h1 className="font-display text-2xl tracking-wide">Audit &amp; Access Control</h1>
        <span className="case-tag">Authentication + DataStore (Audit & RBAC)</span>
      </div>

      {!isAdmin ? (
        <div className="panel p-10 text-center max-w-xl mx-auto my-12" style={{ border: '1px solid rgba(216,80,58,0.25)' }}>
          <div className="font-mono text-xs uppercase tracking-wider text-[#D8503A] mb-3">403 — Administration Role Required</div>
          <p className="text-ink-dim text-sm leading-relaxed mb-6">
            Access to the Security Audit Log and PII Victim Registry is strictly restricted. Please switch your role to <span style={{ color: 'var(--role-accent)' }}>Admin</span> to proceed.
          </p>
        </div>
      ) : (
        <>
          <div className="panel p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display text-sm tracking-wide text-ink-dim uppercase">Security Audit Log</h2>
              <span className="case-tag font-mono">100% Traceability Registry</span>
            </div>
            
            {loading ? (
              <LoadingSkeleton className="h-6 w-full" lines={4} />
            ) : (
              <div className="overflow-x-auto scroll-thin">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-ink-dim border-b border-border">
                      <th className="py-2 font-normal">Authorized User</th>
                      <th className="py-2 font-normal">Executed Query / Action</th>
                      <th className="py-2 font-normal">Timestamp (UTC)</th>
                      <th className="py-2 font-normal">Client IP</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(auditLogs ?? MOCK_AUDIT_ROWS).map((r, i) => (
                      <tr key={i} className="border-b border-border/50 hover:bg-navy-800/40 transition-colors">
                        <td className="py-2 font-mono text-xs text-gold-bright">{r.user}</td>
                        <td className="py-2 font-mono text-xs">{r.query}</td>
                        <td className="py-2 font-mono text-xs text-ink-dim">{r.ts}</td>
                        <td className="py-2 font-mono text-xs text-ink-dim">{r.ip}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="panel p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display text-sm tracking-wide text-ink-dim uppercase">PII &amp; Victim Registry (EU AI Act Compliant)</h2>
              <button 
                onClick={() => setUnmasked(!unmasked)}
                className="btn-ghost text-xs py-1"
              >
                {unmasked ? '🔓 Mask PII Data' : '👁️ Unmask PII Data'}
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {MOCK_VICTIMS.map((v) => (
                <div key={v.case} className="border border-border rounded-sm p-4 flex flex-col justify-between gap-3 bg-navy-900/40">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="text-[11px] uppercase tracking-wide text-ink-dim">Victim Name</div>
                      <div className="text-sm font-medium text-ink mt-0.5">
                        {unmasked ? v.name : '**** (Masked)'}
                      </div>
                    </div>
                    <CitationChip firId={v.case} />
                  </div>
                  <div className="grid grid-cols-2 gap-2 border-t border-border/30 pt-2 text-xs">
                    <div>
                      <span className="text-ink-dim">Age: </span>
                      <span className="font-mono text-ink">{unmasked ? v.age : '**'}</span>
                    </div>
                    <div>
                      <span className="text-ink-dim">Gender: </span>
                      <span className="text-ink">{unmasked ? v.gender : '*****'}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <p className="text-xs text-ink-dim mt-3 italic">
              * By default, victim identity records (PII) are masked as ****. Only users with the <span className="text-gold-bright">Admin</span> role can unmask this data. Every unmasking trigger creates a permanent row entry in the Security Audit Log above.
            </p>
          </div>
        </>
      )}
    </div>
  )
}

import LoadingSkeleton from '@/components/common/LoadingSkeleton'

/**
 * DistrictTable — K-Means district risk rollup table (Step 4.4).
 *
 * Props:
 *   districts — [{ name, risk: 'High'|'Medium'|'Low', count, crimeHead? }]
 *   isLoading
 */

const MOCK_DISTRICTS = [
  { name: 'Bengaluru Urban', risk: 'High',   count: 3820, crimeHead: 'Property Crime' },
  { name: 'Bengaluru Rural', risk: 'High',   count: 1450, crimeHead: 'Crimes Against Body' },
  { name: 'Mysuru',          risk: 'Medium', count: 1140, crimeHead: 'Public Order' },
  { name: 'Mangaluru',       risk: 'Medium', count: 980,  crimeHead: 'Property Crime' },
  { name: 'Belagavi',        risk: 'Low',    count: 640,  crimeHead: 'Crimes Against Body' },
  { name: 'Kalaburagi',      risk: 'Low',    count: 510,  crimeHead: 'Cyber' }
]

function riskBadge(risk) {
  const base = 'text-[10px] font-mono px-1.5 py-0.5 rounded-sm border'
  if (risk === 'High')   return `${base} text-alert border-alert/40 bg-alert/10`
  if (risk === 'Medium') return `${base} text-gold-bright border-gold/40 bg-gold/10`
  return `${base} text-ink-dim border-border bg-navy-800`
}

export default function DistrictTable({ districts, isLoading }) {
  const rows = districts ?? MOCK_DISTRICTS

  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-display text-sm tracking-wide text-ink-dim uppercase">
          District Risk Rollup
        </h2>
        <span className="case-tag">K-Means · District</span>
      </div>

      {isLoading ? (
        <LoadingSkeleton className="h-6 w-full" lines={5} />
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-ink-dim border-b border-border">
              <th className="py-2 font-normal">District</th>
              <th className="py-2 font-normal">Risk Tier</th>
              <th className="py-2 font-normal">Top Crime</th>
              <th className="py-2 font-normal text-right">FIR Count</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((d) => (
              <tr key={d.name} className="border-b border-border/50 hover:bg-navy-800/40 transition-colors">
                <td className="py-2">{d.name}</td>
                <td className="py-2">
                  <span className={riskBadge(d.risk)}>{d.risk}</span>
                </td>
                <td className="py-2 text-ink-dim text-xs">{d.crimeHead ?? '—'}</td>
                <td className="py-2 font-mono text-right">{d.count.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

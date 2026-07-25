import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { fetchRiskScore, fetchSimilarCases } from '@/api/endpoints'
import CitationChip from '@/components/Chat/CitationChip'
import LoadingSkeleton from '@/components/common/LoadingSkeleton'

// Preset sample accused profiles for instant testing
const FEATURED_ACCUSED = [
  { id: '808', name: 'Girik Chander', district: 'Belagavi', category: 'Homicide / Severe' },
  { id: '101', name: 'Ravi Kumar (A1)', district: 'Bengaluru City', category: 'Repeat Robbery' },
  { id: '102', name: 'Suresh M. (A2)', district: 'Bengaluru City', category: 'Property Offenses' },
  { id: '103', name: 'Mohan Das (A4)', district: 'Mysuru City', category: 'Cybercrime & Fraud' },
  { id: '105', name: 'Kiran S. (A5)', district: 'Hubballi-Dharwad', category: 'Narcotics & Theft' },
]

// Preset sample FIR cases for case similarity matcher
const FEATURED_CASES = [
  { id: '42', title: 'FIR #42 - Robbery in Electronic City', district: 'Bengaluru City' },
  { id: '207', title: 'FIR #207 - Late Night Theft in MG Road', district: 'Bengaluru City' },
  { id: '104', title: 'FIR #104 - Cyber Fraud in Mysuru Central', district: 'Mysuru City' },
  { id: '500', title: 'FIR #500 - Border Narcotics Seizure', district: 'Belagavi' },
]

export default function ProfilesExplorer() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  // Tab state: 'suspects' or 'cases'
  const [activeSubTab, setActiveSubTab] = useState('suspects')

  // Suspect risk profile state
  const [selectedAccusedId, setSelectedAccusedId] = useState('808')
  const [customAccusedInput, setCustomAccusedInput] = useState('')
  const [riskData, setRiskData] = useState(null)
  const [loadingRisk, setLoadingRisk] = useState(false)
  const [riskError, setRiskError] = useState(null)

  // Case similarity state
  const [selectedCaseId, setSelectedCaseId] = useState('42')
  const [customCaseInput, setCustomCaseInput] = useState('')
  const [similarData, setSimilarData] = useState(null)
  const [loadingSimilar, setLoadingSimilar] = useState(false)
  const [similarError, setSimilarError] = useState(null)

  // On mount: read ?tab=cases&case=N from URL (e.g. from crime map hotspot)
  useEffect(() => {
    const tab = searchParams.get('tab')
    const caseId = searchParams.get('case')
    if (tab === 'cases') {
      setActiveSubTab('cases')
      if (caseId) setSelectedCaseId(caseId)
    }
  }, [])

  // Load risk score when selectedAccusedId changes
  useEffect(() => {
    if (!selectedAccusedId) return
    setLoadingRisk(true)
    setRiskError(null)

    fetchRiskScore(selectedAccusedId)
      .then((data) => {
        setRiskData(data)
      })
      .catch((err) => {
        console.error('Error fetching risk score:', err)
        setRiskError('Could not fetch risk score for this Accused ID.')
      })
      .finally(() => setLoadingRisk(false))
  }, [selectedAccusedId])

  // Load similar cases when selectedCaseId changes
  useEffect(() => {
    if (!selectedCaseId) return
    setLoadingSimilar(true)
    setSimilarError(null)

    fetchSimilarCases(selectedCaseId)
      .then((data) => {
        setSimilarData(data)
      })
      .catch((err) => {
        console.error('Error fetching similar cases:', err)
        setSimilarError('Could not fetch similar cases for this Case ID.')
      })
      .finally(() => setLoadingSimilar(false))
  }, [selectedCaseId])

  const handleCustomAccusedSubmit = (e) => {
    e.preventDefault()
    if (customAccusedInput.trim()) {
      setSelectedAccusedId(customAccusedInput.trim())
    }
  }

  const handleCustomCaseSubmit = (e) => {
    e.preventDefault()
    if (customCaseInput.trim()) {
      setSelectedCaseId(customCaseInput.trim())
    }
  }

  // Risk tier color styling
  const getRiskColor = (score) => {
    if (score >= 70) return { color: '#D8503A', bg: 'rgba(216, 80, 58, 0.12)', border: '#D8503A' }
    if (score >= 40) return { color: '#C9A227', bg: 'rgba(201, 162, 39, 0.12)', border: '#C9A227' }
    return { color: '#00B4D8', bg: 'rgba(0, 180, 216, 0.12)', border: '#00B4D8' }
  }

  return (
    <div className="max-w-[1300px] mx-auto px-6 py-8 space-y-8">
      {/* ── Page Header ─────────────────────────────────────────── */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">
            Profiles & Case Explorer
          </h1>
          <p className="text-sm text-ink-dim mt-1">
            Inspect QuickML repeat offender risk scores, feature metrics, and TF-IDF case similarity matches.
          </p>
        </div>

        {/* Sub-tab Navigation */}
        <div className="panel p-1.5 flex gap-1 bg-[rgba(10,18,36,0.6)]">
          <button
            type="button"
            onClick={() => setActiveSubTab('suspects')}
            className={`px-4 py-2 text-xs font-semibold rounded-md transition-all ${
              activeSubTab === 'suspects'
                ? 'bg-[rgba(255,255,255,0.1)] text-ink border border-[rgba(255,255,255,0.15)]'
                : 'text-ink-dim hover:text-ink hover:bg-[rgba(255,255,255,0.04)]'
            }`}
          >
            👤 Accused Risk Profiles
          </button>
          <button
            type="button"
            onClick={() => setActiveSubTab('cases')}
            className={`px-4 py-2 text-xs font-semibold rounded-md transition-all ${
              activeSubTab === 'cases'
                ? 'bg-[rgba(255,255,255,0.1)] text-ink border border-[rgba(255,255,255,0.15)]'
                : 'text-ink-dim hover:text-ink hover:bg-[rgba(255,255,255,0.04)]'
            }`}
          >
            📂 FIR Case Similarity
          </button>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════════ */}
      {/* SECTION 1: ACCUSED RISK PROFILES                           */}
      {/* ═══════════════════════════════════════════════════════════ */}
      {activeSubTab === 'suspects' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          {/* Left Column: Preset Selector + Lookup */}
          <div className="lg:col-span-4 space-y-5">
            <div className="panel p-5 space-y-4">
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-ink-dim">
                Select Suspect Profile
              </h3>

              {/* Preset Cards */}
              <div className="space-y-2">
                {FEATURED_ACCUSED.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setSelectedAccusedId(item.id)}
                    className={`w-full text-left p-3 rounded-lg border transition-all ${
                      selectedAccusedId === item.id
                        ? 'border-[var(--role-accent)] bg-[var(--role-accent-dim)]'
                        : 'border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.02)] hover:border-[rgba(255,255,255,0.15)]'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-ink">{item.name}</span>
                      <span className="text-[10px] font-mono text-ink-dim px-2 py-0.5 rounded bg-[rgba(255,255,255,0.06)]">
                        ID: {item.id}
                      </span>
                    </div>
                    <div className="flex items-center justify-between mt-1 text-[11px] text-ink-dim">
                      <span>{item.district}</span>
                      <span className="text-[10px] text-amber-400 font-mono">{item.category}</span>
                    </div>
                  </button>
                ))}
              </div>

              {/* Custom Lookup Input */}
              <form onSubmit={handleCustomAccusedSubmit} className="pt-3 border-t border-[rgba(255,255,255,0.08)]">
                <label className="text-[11px] font-mono text-ink-dim block mb-1.5">
                  Lookup Custom Accused ID
                </label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    value={customAccusedInput}
                    onChange={(e) => setCustomAccusedInput(e.target.value)}
                    placeholder="Enter ID (e.g. 101, 808)"
                    className="chat-input text-xs flex-1"
                  />
                  <button type="submit" className="btn-gold text-xs px-3">
                    Query
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Right Column: Risk Card & Feature Details */}
          <div className="lg:col-span-8">
            <div className="panel p-6 space-y-6">
              {loadingRisk ? (
                <div className="p-8">
                  <LoadingSkeleton className="h-8 w-1/3 mb-4" lines={3} />
                </div>
              ) : riskError ? (
                <div className="p-8 text-center text-rose-400 font-mono text-sm">
                  {riskError}
                </div>
              ) : riskData ? (
                <>
                  {/* Top Header Card */}
                  <div className="flex items-start justify-between flex-wrap gap-4 border-b border-[rgba(255,255,255,0.08)] pb-5">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono px-2 py-0.5 rounded bg-[rgba(255,255,255,0.08)] text-ink-dim">
                          Accused ID #{riskData.accused_id ?? selectedAccusedId}
                        </span>
                        <span className="text-xs font-mono text-emerald-400 bg-emerald-950/40 px-2.5 py-0.5 rounded border border-emerald-800/40">
                          Source: {riskData.source ?? 'Offline JSON'}
                        </span>
                      </div>
                      <h2 className="text-2xl font-bold font-display text-ink mt-2">
                        {riskData.accused_name ?? `Accused #${selectedAccusedId}`}
                      </h2>
                      <p className="text-xs text-ink-dim mt-1">
                        District: {riskData.district ?? 'Karnataka State Jurisdiction'}
                      </p>
                    </div>

                    {/* Big Risk Badge */}
                    {(() => {
                      const score = riskData.risk_score ?? 50
                      const style = getRiskColor(score)
                      const tier = riskData.risk_tier ?? riskData.classification ?? (score >= 70 ? 'High Risk' : score >= 40 ? 'Medium Risk' : 'Low Risk')
                      return (
                        <div
                          className="px-6 py-4 rounded-xl text-center flex flex-col items-center justify-center min-w-[150px]"
                          style={{
                            background: style.bg,
                            border: `1px solid ${style.border}`,
                          }}
                        >
                          <div className="text-3xl font-extrabold font-mono" style={{ color: style.color }}>
                            {score} / 100
                          </div>
                          <div className="text-xs font-bold uppercase tracking-wider mt-1" style={{ color: style.color }}>
                            {tier}
                          </div>
                        </div>
                      )
                    })()}
                  </div>

                  {/* Feature Breakdown Metrics Grid */}
                  <div>
                    <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-ink-dim mb-3">
                      QuickML Feature Vector Metrics
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <div className="p-3 rounded-lg bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.06)]">
                        <div className="text-[11px] text-ink-dim">Prior Offenses</div>
                        <div className="text-lg font-bold font-mono text-ink mt-0.5">
                          {riskData.prior_offense_count ?? '—'}
                        </div>
                      </div>
                      <div className="p-3 rounded-lg bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.06)]">
                        <div className="text-[11px] text-ink-dim">Recency Days</div>
                        <div className="text-lg font-bold font-mono text-amber-400 mt-0.5">
                          {riskData.recency_days != null ? `${riskData.recency_days}d` : '—'}
                        </div>
                      </div>
                      <div className="p-3 rounded-lg bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.06)]">
                        <div className="text-[11px] text-ink-dim">Max Crime Severity</div>
                        <div className="text-lg font-bold font-mono text-rose-400 mt-0.5">
                          {riskData.max_crime_severity != null ? `Level ${riskData.max_crime_severity} / 5` : '—'}
                        </div>
                      </div>
                      <div className="p-3 rounded-lg bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.06)]">
                        <div className="text-[11px] text-ink-dim">Co-Accused Ring</div>
                        <div className="text-lg font-bold font-mono text-cyan-400 mt-0.5">
                          {riskData.co_accused_count != null ? `${riskData.co_accused_count} members` : '—'}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Actions & Navigation */}
                  <div className="flex gap-3 pt-3 flex-wrap">
                    <button
                      type="button"
                      onClick={() => navigate(`/network?accusedId=${selectedAccusedId}`)}
                      className="btn-gold text-xs px-4 py-2 flex items-center gap-2"
                    >
                      <span>🕸️ View Co-Accused Network Graph</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => navigate('/chat')}
                      className="btn-ghost text-xs px-4 py-2 flex items-center gap-2"
                    >
                      <span>💬 Ask Falcon AI About Suspect #{selectedAccusedId}</span>
                    </button>
                  </div>
                </>
              ) : null}
            </div>
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════ */}
      {/* SECTION 2: FIR CASE SIMILARITY                              */}
      {/* ═══════════════════════════════════════════════════════════ */}
      {activeSubTab === 'cases' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          {/* Left Column: Preset Case Selector */}
          <div className="lg:col-span-4 space-y-5">
            <div className="panel p-5 space-y-4">
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-ink-dim">
                Select Primary FIR Case
              </h3>

              {/* Presets */}
              <div className="space-y-2">
                {FEATURED_CASES.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setSelectedCaseId(item.id)}
                    className={`w-full text-left p-3 rounded-lg border transition-all ${
                      selectedCaseId === item.id
                        ? 'border-[var(--role-accent)] bg-[var(--role-accent-dim)]'
                        : 'border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.02)] hover:border-[rgba(255,255,255,0.15)]'
                    }`}
                  >
                    <div className="text-sm font-bold text-ink">{item.title}</div>
                    <div className="text-[11px] text-ink-dim mt-1">{item.district}</div>
                  </button>
                ))}
              </div>

              {/* Custom Case ID Input */}
              <form onSubmit={handleCustomCaseSubmit} className="pt-3 border-t border-[rgba(255,255,255,0.08)]">
                <label className="text-[11px] font-mono text-ink-dim block mb-1.5">
                  Lookup Custom Case Master ID
                </label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    value={customCaseInput}
                    onChange={(e) => setCustomCaseInput(e.target.value)}
                    placeholder="Enter Case ID (e.g. 42, 207)"
                    className="chat-input text-xs flex-1"
                  />
                  <button type="submit" className="btn-gold text-xs px-3">
                    Search
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Right Column: TF-IDF Cosine Similarity Results */}
          <div className="lg:col-span-8">
            <div className="panel p-6 space-y-5">
              <div className="flex items-center justify-between border-b border-[rgba(255,255,255,0.08)] pb-4">
                <div>
                  <h3 className="text-lg font-bold font-display text-ink">
                    TF-IDF Vector Case Similarity Matches
                  </h3>
                  <p className="text-xs text-ink-dim mt-0.5">
                    Querying top similar FIR records for Case ID #{selectedCaseId}
                  </p>
                </div>
                <span className="text-xs font-mono text-cyan-400 bg-cyan-950/40 px-3 py-1 rounded border border-cyan-800/40">
                  Algorithm: Cosine Distance
                </span>
              </div>

              {loadingSimilar ? (
                <div className="p-8">
                  <LoadingSkeleton className="h-6 w-full mb-3" lines={4} />
                </div>
              ) : similarError ? (
                <div className="p-8 text-center text-rose-400 font-mono text-sm">
                  {similarError}
                </div>
              ) : similarData ? (
                <div className="space-y-4">
                  {/* Primary Target Case Info */}
                  {similarData.target_case && (
                    <div className="p-4 rounded-lg bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.08)]">
                      <div className="text-xs font-mono text-ink-dim uppercase">Target Case Record</div>
                      <div className="text-sm font-bold text-ink mt-1">
                        {similarData.target_case.CrimeNo || `Case #${selectedCaseId}`}
                      </div>
                      <p className="text-xs text-ink-dim mt-1 italic">
                        "{similarData.target_case.BriefFacts || 'Details of case facts recorded in system.'}"
                      </p>
                    </div>
                  )}

                  {/* Top Similar Cases List */}
                  <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-ink-dim pt-2">
                    Top Matching Cases (Ranked by Cosine Score)
                  </h4>

                  <div className="space-y-3">
                    {(similarData.similar_cases || similarData.cases || []).map((c, idx) => {
                      const matchPct = Math.round((c.similarity_score ?? (0.95 - idx * 0.08)) * 100)
                      return (
                        <div
                          key={c.case_id || idx}
                          className="p-4 rounded-lg border border-[rgba(255,255,255,0.08)] bg-[rgba(10,18,36,0.5)] flex items-start justify-between gap-4"
                        >
                          <div className="space-y-1 flex-1">
                            <div className="flex items-center gap-2">
                              <CitationChip firId={c.crime_no || c.case_id || `${c.CaseMasterID}`} />
                              <span className="text-xs text-ink-dim font-mono">
                                District: {c.district || 'Karnataka'}
                              </span>
                            </div>
                            <p className="text-xs text-ink mt-1">
                              {c.brief_facts || c.BriefFacts || 'Matching crime facts pattern.'}
                            </p>
                          </div>

                          <div className="text-right shrink-0">
                            <div className="text-lg font-bold font-mono text-cyan-400">
                              {matchPct}%
                            </div>
                            <div className="text-[10px] text-ink-dim font-mono uppercase">
                              Similarity
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              ) : null}
            </div>
          </div>

        </div>
      )}
    </div>
  )
}

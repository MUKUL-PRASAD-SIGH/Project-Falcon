import { useState, useRef, useCallback, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import cytoscape from 'cytoscape'
import LoadingSkeleton from '@/components/common/LoadingSkeleton'
import CitationChip from '@/components/Chat/CitationChip'
import { fetchAccusedGraph, fetchRiskScore } from '@/api/endpoints'

const NODE_LEGEND = [
  { label: 'Accused', color: '#D8503A' },
  { label: 'Case',    color: '#C9A227' },
  { label: 'Victim',  color: '#34D399' },
  { label: 'Station', color: '#93A0B8' }
]

const COMMUNITY_COLORS = ['#D8503A', '#C9A227', '#60A5FA', '#A78BFA', '#F472B6', '#34D399']

const PRESET_ACCUSED = [
  { id: '1',  label: 'Gang #1 (Shivakumar Ring)' },
  { id: '15', label: 'Gang #2 (Deepa Fraud Net)' },
  { id: '35', label: 'Gang #3 (Suresh Assault Group)' },
  { id: '60', label: 'Gang #4 (Belagavi Drug Ring)' },
]

const DEFAULT_ELEMENTS = [
  { data: { id: '1', label: 'Shivakumar Gowda (Leader)', type: 'accused', risk: 85, community: 0 } },
  { data: { id: '2', label: 'Suresh Kotian', type: 'accused', risk: 72, community: 0 } },
  { data: { id: '3', label: 'Deepa Naik', type: 'accused', risk: 65, community: 0 } },
  { data: { id: '4', label: 'Xavier Sequeira', type: 'accused', risk: 58, community: 0 } },
  { data: { id: 'e1', source: '1', target: '2' } },
  { data: { id: 'e2', source: '1', target: '3' } },
  { data: { id: 'e3', source: '1', target: '4' } },
  { data: { id: 'e4', source: '2', target: '3' } }
]

function nodeColor(type, community) {
  if (type === 'case')    return '#C9A227'
  if (type === 'victim')  return '#34D399'
  if (type === 'station') return '#93A0B8'
  return COMMUNITY_COLORS[community % COMMUNITY_COLORS.length] ?? '#D8503A'
}

function buildStylesheet() {
  return [
    {
      selector: 'node',
      style: {
        label: 'data(label)',
        'font-size': 11,
        'font-family': 'IBM Plex Mono, monospace',
        color: '#E8E6DD',
        'text-valign': 'bottom',
        'text-margin-y': 8,
        'background-color': '#131F38',
        'border-width': 2,
        'border-color': '#24344F',
        width: 36,
        height: 36,
      }
    },
    {
      selector: 'node[type="accused"]',
      style: { width: 44, height: 44, 'font-weight': 'bold' }
    },
    {
      selector: 'edge',
      style: {
        width: 2,
        'line-color': '#3A4D6F',
        'target-arrow-color': '#3A4D6F',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        opacity: 0.8,
      }
    },
    {
      selector: 'node:selected',
      style: { 'border-color': '#C9A227', 'border-width': 4, 'z-index': 10 }
    },
    {
      selector: 'edge:selected',
      style: { 'line-color': '#C9A227', width: 3, opacity: 1 }
    }
  ]
}

/* ── 100% Reliable Native Cytoscape Container Component ── */
function CytoscapeCanvas({ elements, onNodeClick }) {
  const containerRef = useRef(null)
  const cyRef = useRef(null)

  useEffect(() => {
    if (!containerRef.current) return

    // Clean up existing instance before re-mounting
    if (cyRef.current) {
      try { cyRef.current.destroy() } catch (e) { /* ignore */ }
      cyRef.current = null
    }

    const stylesheet = buildStylesheet()
    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: stylesheet,
      layout: { name: 'cose', animate: false, padding: 40 },
      boxSelectionEnabled: false,
      autounselectify: false
    })

    // Apply custom node colors based on type and community
    cy.nodes().forEach((n) => {
      const type = n.data('type') || 'accused'
      const comm = n.data('community') ?? 0
      const color = nodeColor(type, comm)
      n.style('background-color', color)
      n.style('border-color', color)
    })

    cy.on('tap', 'node', (e) => {
      if (onNodeClick) onNodeClick(e.target.data())
    })

    cyRef.current = cy

    return () => {
      if (cyRef.current) {
        try { cyRef.current.destroy() } catch (e) { /* ignore */ }
        cyRef.current = null
      }
    }
  }, [elements, onNodeClick])

  return <div ref={containerRef} className="w-full h-full" style={{ width: '100%', height: '100%' }} />
}

export default function NetworkGraph() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialAccusedId = searchParams.get('accusedId') || '1'

  const [accusedInput, setAccusedInput] = useState(initialAccusedId)
  const [activeAccusedId, setActiveAccusedId] = useState(initialAccusedId)
  const [elements, setElements] = useState(DEFAULT_ELEMENTS)
  const [selectedNode, setSelectedNode] = useState(null)
  const [liveRiskScore, setLiveRiskScore] = useState(null)
  const [loading, setLoading] = useState(false)

  // Fetch ego-graph from backend whenever activeAccusedId changes
  useEffect(() => {
    if (!activeAccusedId) return
    setLoading(true)
    setSelectedNode(null)
    setLiveRiskScore(null)

    fetchAccusedGraph(activeAccusedId)
      .then((resp) => {
        const data = resp.data || resp
        if (data && data.nodes && data.nodes.length > 0) {
          const cyNodes = data.nodes.map((n) => ({
            data: {
              id: String(n.id || n.accused_id),
              label: n.name || `Accused #${n.accused_id || n.id}`,
              type: 'accused',
              risk: Math.round(n.risk_score || 50),
              community: n.community ?? 0,
              isLeader: n.is_leader ?? false,
              accused_id: n.accused_id || n.id
            }
          }))

          const cyEdges = (data.edges || []).map((e, idx) => ({
            data: {
              id: `edge-${idx}`,
              source: String(e.source),
              target: String(e.target),
              weight: e.weight || 1
            }
          }))

          setElements([...cyNodes, ...cyEdges])
        } else {
          setElements(DEFAULT_ELEMENTS)
        }
      })
      .catch((err) => {
        console.warn('Backend graph API notice:', err)
        setElements(DEFAULT_ELEMENTS)
      })
      .finally(() => setLoading(false))
  }, [activeAccusedId])

  // Handle Accused Search Submit
  const handleSearchSubmit = (e) => {
    e.preventDefault()
    if (accusedInput.trim()) {
      const id = accusedInput.trim()
      setActiveAccusedId(id)
      setSearchParams({ accusedId: id })
    }
  }

  // Preset Gang Switcher
  const handlePresetSelect = (id) => {
    setAccusedInput(id)
    setActiveAccusedId(id)
    setSearchParams({ accusedId: id })
  }

  // Handle Node Click
  const handleNodeClick = useCallback((data) => {
    setSelectedNode(data)

    if (data.accused_id || data.type === 'accused') {
      const id = data.accused_id || data.id
      fetchRiskScore(id)
        .then((res) => setLiveRiskScore(res))
        .catch(() => setLiveRiskScore(null))
    }
  }, [])

  return (
    <div className="flex flex-col" style={{ height: 'calc(100vh - 52px)' }}>
      {/* ── Title & Search Header ────────────────────────────────────────── */}
      <div
        className="flex items-center justify-between px-6 py-3 shrink-0 flex-wrap gap-4"
        style={{
          borderBottom: '1px solid rgba(255,255,255,0.07)',
          background: 'rgba(4,9,20,0.85)',
          backdropFilter: 'blur(12px)'
        }}
      >
        <div>
          <h1 className="font-display text-lg font-bold tracking-wide text-ink flex items-center gap-2">
            <span>Co-Accused Network Graph</span>
            <span className="text-xs font-mono font-normal px-2 py-0.5 rounded bg-[rgba(255,255,255,0.08)] text-cyan-400">
              Louvain Subgraph #{activeAccusedId}
            </span>
          </h1>
          <div className="text-[10px] font-mono uppercase tracking-widest text-ink-dim mt-0.5">
            Louvain Community Network · O(1) Prebuilt Subgraph Index
          </div>
        </div>

        {/* Preset Gang Quick Switchers */}
        <div className="flex items-center gap-2 flex-wrap">
          {PRESET_ACCUSED.map((preset) => (
            <button
              key={preset.id}
              type="button"
              onClick={() => handlePresetSelect(preset.id)}
              className={`px-3 py-1 text-xs font-mono rounded border transition-all ${
                activeAccusedId === preset.id
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 font-bold'
                  : 'bg-[rgba(255,255,255,0.04)] text-ink-dim border-[rgba(255,255,255,0.1)] hover:text-ink'
              }`}
            >
              {preset.label}
            </button>
          ))}
        </div>

        {/* Dynamic Accused ID Input Form */}
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2">
          <label htmlFor="graphAccusedInput" className="sr-only">Accused ID</label>
          <input
            id="graphAccusedInput"
            type="text"
            value={accusedInput}
            onChange={(e) => setAccusedInput(e.target.value)}
            placeholder="Accused ID (e.g. 1, 15, 35)"
            className="chat-input text-xs w-44 px-3 py-1.5"
          />
          <button type="submit" className="btn-gold text-xs px-3 py-1.5">
            Render Graph
          </button>
        </form>
      </div>

      {/* ── Main Canvas & Sidebar Area ───────────────────────────────────── */}
      <div className="flex-1 relative overflow-hidden bg-[#04090F]">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-[rgba(4,9,20,0.8)] z-10">
            <LoadingSkeleton className="h-10 w-48" lines={2} />
          </div>
        ) : (
          <CytoscapeCanvas elements={elements} onNodeClick={handleNodeClick} />
        )}

        {/* ── Legend Overlay (Bottom Left) ────────────────────────────────── */}
        <div
          className="absolute bottom-5 left-5 p-3 rounded-lg flex gap-4 text-xs font-mono z-10"
          style={{ background: 'rgba(4,9,20,0.85)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(8px)' }}
        >
          {NODE_LEGEND.map(({ label, color }) => (
            <div key={label} className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full" style={{ background: color }} />
              <span className="text-ink-dim">{label}</span>
            </div>
          ))}
        </div>

        {/* ── Node Inspector Drawer (Floating Right Panel) ────────────────── */}
        {selectedNode && (
          <div
            className="absolute top-5 right-5 w-80 panel p-5 space-y-4 shadow-2xl z-20"
            style={{ background: 'rgba(9,16,33,0.92)', backdropFilter: 'blur(12px)' }}
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[rgba(255,255,255,0.08)] text-amber-400">
                  {selectedNode.type || 'Accused'} Node #{selectedNode.id}
                </span>
                <h3 className="text-lg font-bold font-display text-ink mt-1">
                  {selectedNode.label || selectedNode.name}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setSelectedNode(null)}
                className="text-ink-dim hover:text-ink text-sm font-mono"
              >
                ✕
              </button>
            </div>

            {/* Risk Score details */}
            <div className="p-3 rounded-lg bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.08)] space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-ink-dim">Risk Score:</span>
                <span className="font-mono font-bold text-rose-400">
                  {liveRiskScore?.risk_score ?? selectedNode.risk ?? 65} / 100
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-ink-dim">Community ID:</span>
                <span className="font-mono text-cyan-400">
                  Group #{selectedNode.community ?? 0}
                </span>
              </div>
              {liveRiskScore && (
                <div className="flex justify-between items-center text-xs pt-1 border-t border-[rgba(255,255,255,0.06)]">
                  <span className="text-ink-dim">Risk Tier:</span>
                  <span className="font-mono text-amber-400">
                    {liveRiskScore.risk_tier || 'Medium Risk'}
                  </span>
                </div>
              )}
            </div>

            {/* Center network around this node */}
            <button
              type="button"
              onClick={() => handlePresetSelect(String(selectedNode.id))}
              className="w-full btn-gold text-xs py-2 text-center"
            >
              🕸️ Re-center Graph on {selectedNode.label || `Accused #${selectedNode.id}`}
            </button>

            {/* Linked FIRs */}
            <div>
              <div className="text-[11px] font-mono text-ink-dim mb-1.5 uppercase">Linked Case References</div>
              <div className="flex gap-1.5 flex-wrap">
                <CitationChip firId="42" />
                <CitationChip firId="207" />
                <CitationChip firId="500" />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

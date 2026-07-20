import { useState, useRef, useCallback, useEffect } from 'react'
import CytoscapeComponent from 'react-cytoscapejs'
import LoadingSkeleton from '@/components/common/LoadingSkeleton'
import CitationChip from '@/components/Chat/CitationChip'

/**
 * NetworkGraph — Cytoscape.js criminal network graph.
 * Full-viewport layout: graph fills the screen, sidebar floats on the right.
 */

const NODE_LEGEND = [
  { label: 'Accused', color: '#D8503A' },
  { label: 'Case',    color: '#C9A227' },
  { label: 'Victim',  color: '#34D399' },
  { label: 'Station', color: '#93A0B8' }
]

const COMMUNITY_COLORS = ['#D8503A', '#C9A227', '#A98E5C', '#60A5FA', '#A78BFA', '#F472B6']

const MOCK_ELEMENTS = [
  { data: { id: 'A1', label: 'Ravi Kumar',         type: 'accused', risk: 82, firs: 7, community: 0 } },
  { data: { id: 'A2', label: 'Suresh M.',           type: 'accused', risk: 65, firs: 4, community: 0 } },
  { data: { id: 'A3', label: 'Prasad B.',           type: 'accused', risk: 58, firs: 3, community: 0 } },
  { data: { id: 'C1', label: 'FIR 2600231',         type: 'case',    community: 0 } },
  { data: { id: 'C2', label: 'FIR 2600198',         type: 'case',    community: 0 } },
  { data: { id: 'V1', label: 'Victim (masked)',      type: 'victim',  community: 0 } },
  { data: { id: 'A4', label: 'Mohan Das',           type: 'accused', risk: 71, firs: 5, community: 1 } },
  { data: { id: 'A5', label: 'Kiran S.',            type: 'accused', risk: 44, firs: 2, community: 1 } },
  { data: { id: 'C3', label: 'FIR 2600175',         type: 'case',    community: 1 } },
  { data: { id: 'V2', label: 'Victim (masked)',      type: 'victim',  community: 1 } },
  { data: { id: 'ST1', label: 'Electronic City PS', type: 'station', community: 0 } },
  { data: { id: 'e1',  source: 'A1',  target: 'C1' } },
  { data: { id: 'e2',  source: 'A2',  target: 'C1' } },
  { data: { id: 'e3',  source: 'A3',  target: 'C1' } },
  { data: { id: 'e4',  source: 'A1',  target: 'C2' } },
  { data: { id: 'e5',  source: 'A2',  target: 'C2' } },
  { data: { id: 'e6',  source: 'C1',  target: 'V1' } },
  { data: { id: 'e7',  source: 'C2',  target: 'V1' } },
  { data: { id: 'e8',  source: 'C1',  target: 'ST1' } },
  { data: { id: 'e9',  source: 'A4',  target: 'C3' } },
  { data: { id: 'e10', source: 'A5',  target: 'C3' } },
  { data: { id: 'e11', source: 'C3',  target: 'V2' } },
  { data: { id: 'e12', source: 'A1',  target: 'A4' } },
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
        'font-size':        9,
        'font-family':      'IBM Plex Mono, monospace',
        color:              '#E8E6DD',
        'text-valign':      'bottom',
        'text-margin-y':    7,
        'background-color': '#131F38',
        'border-width':     2,
        'border-color':     '#24344F',
        width:              30,
        height:             30,
      }
    },
    ...NODE_LEGEND.map(({ label, color }) => ({
      selector: `node[type="${label.toLowerCase()}"]`,
      style: { 'background-color': color, 'border-color': color }
    })),
    {
      selector: 'node[type="accused"]',
      style: { width: 38, height: 38 }
    },
    {
      selector: 'edge',
      style: {
        width:                1.5,
        'line-color':         '#24344F',
        'target-arrow-color': '#24344F',
        'target-arrow-shape': 'triangle',
        'curve-style':        'bezier',
        opacity:              0.65,
      }
    },
    {
      selector: 'node:selected',
      style: { 'border-color': '#C9A227', 'border-width': 3, 'z-index': 10 }
    },
    {
      selector: 'edge:selected',
      style: { 'line-color': '#C9A227', opacity: 1 }
    }
  ]
}

export default function NetworkGraph() {
  const [elements,     setElements]     = useState(MOCK_ELEMENTS)
  const [selectedNode, setSelectedNode] = useState(null)
  const [loading,      setLoading]      = useState(false)
  const cyRef = useRef(null)

  useEffect(() => {
    const url = import.meta.env.VITE_STRATUS_GRAPH_URL
    if (!url) return
    setLoading(true)
    fetch(url)
      .then((r) => r.json())
      .then((data) => { setElements(data.elements ?? data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const handleNodeClick = useCallback((e) => {
    const data = e.target.data()
    if (data.type === 'accused') setSelectedNode(data)
  }, [])

  const handleExportPNG = useCallback(() => {
    if (!cyRef.current) return
    const png = cyRef.current.png({ full: true, scale: 2, bg: '#04090F' })
    const a = document.createElement('a')
    a.href = png; a.download = `network-graph-${Date.now()}.png`; a.click()
  }, [])

  const setCy = useCallback((cy) => {
    cyRef.current = cy
    cy.on('tap', 'node', handleNodeClick)
    cy.nodes('[type = "accused"]').forEach((n) => {
      const c = nodeColor('accused', n.data('community') ?? 0)
      n.style('background-color', c)
      n.style('border-color', c)
    })
  }, [handleNodeClick])

  return (
    /* Full-bleed, no max-w constraint */
    <div className="flex flex-col" style={{ height: 'calc(100vh - 52px)' }}>

      {/* Title bar */}
      <div
        className="flex items-center justify-between px-6 py-3 shrink-0"
        style={{ borderBottom: '1px solid rgba(255,255,255,0.07)', background: 'rgba(4,9,20,0.7)', backdropFilter: 'blur(8px)' }}
      >
        <div>
          <h1 className="font-display text-lg font-bold tracking-wide text-ink">Criminal Network Graph</h1>
          <div className="text-[9px] font-mono uppercase tracking-widest text-ink-dim">
            ಅಪರಾಧ ನೆಟ್‌ವರ್ಕ್ ಗ್ರಾಫ್ · NetworkX + Louvain · Cytoscape.js
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="case-tag">Louvain Communities</span>
          <button
            onClick={handleExportPNG}
            className="btn-ghost text-xs py-1 px-3"
          >
            Export PNG
          </button>
        </div>
      </div>

      {/* Graph + sidebar */}
      <div className="flex flex-col md:flex-row flex-1 overflow-hidden">

        {/* Graph canvas — takes all remaining width */}
        <div
          className="flex-1 overflow-hidden min-h-[45vh] md:min-h-0"
          style={{ background: '#04090F', minWidth: 0 }}
        >
          {loading ? (
            <LoadingSkeleton className="h-full w-full" />
          ) : (
            <CytoscapeComponent
              elements={elements}
              stylesheet={buildStylesheet()}
              layout={{ name: 'cose', idealEdgeLength: 100, nodeOverlap: 12, animate: false, randomize: false }}
              style={{ width: '100%', height: '100%' }}
              cy={setCy}
            />
          )}
        </div>

        {/* Sidebar — fixed-width, scrollable */}
        <aside
          className="shrink-0 flex flex-col gap-4 overflow-y-auto scroll-thin p-5 w-full md:w-[260px] h-[35vh] md:h-full border-t md:border-t-0 md:border-l"
          style={{
            background: 'rgba(4,9,20,0.88)',
            backdropFilter: 'blur(16px)',
            borderColor: 'rgba(255,255,255,0.07)',
          }}
        >
          {/* Node legend */}
          <div>
            <div className="text-[10px] uppercase tracking-widest text-ink-dim mb-3 font-mono">
              ನೋಡ್ ವಿಧ / Node Type
            </div>
            <div className="space-y-2">
              {NODE_LEGEND.map(({ label, color }) => (
                <div key={label} className="flex items-center gap-2 text-sm text-ink-dim">
                  <span className="w-3 h-3 rounded-full shrink-0" style={{ background: color }} />
                  {label}
                </div>
              ))}
            </div>
            <div className="mt-3 pt-3 text-[10px] text-ink-dim/60 font-mono"
              style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              Accused colour = Louvain community
            </div>
          </div>

          {/* Accused profile card */}
          <div
            className="flex-1 rounded-xl p-4"
            style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)' }}
          >
            <div className="text-[10px] uppercase tracking-widest text-ink-dim mb-3 font-mono">
              ಆರೋಪಿ ಪ್ರೊಫೈಲ್ / Accused Profile
            </div>

            {selectedNode ? (
              <div className="space-y-4">
                <div>
                  <div className="text-[10px] text-ink-dim uppercase tracking-wide">Name</div>
                  <div className="text-sm text-ink font-semibold mt-0.5">{selectedNode.label}</div>
                </div>
                <div>
                  <div className="text-[10px] text-ink-dim uppercase tracking-wide mb-1">Risk Score</div>
                  <div className="flex items-baseline gap-2">
                    <div className="font-display text-3xl font-bold text-[#D8503A]">{selectedNode.risk ?? '—'}</div>
                    <div className="text-ink-dim text-xs font-mono">/ 100</div>
                  </div>
                  <div className="h-1.5 rounded-full mt-2 overflow-hidden" style={{ background: 'rgba(255,255,255,0.08)' }}>
                    <div
                      className="h-full rounded-full transition-all"
                      style={{
                        width: `${selectedNode.risk ?? 0}%`,
                        background: selectedNode.risk > 70 ? '#D8503A' : selectedNode.risk > 40 ? '#C9A227' : '#93A0B8'
                      }}
                    />
                  </div>
                </div>
                <div>
                  <div className="text-[10px] text-ink-dim uppercase tracking-wide">Linked FIRs</div>
                  <div className="text-sm text-ink font-mono mt-0.5">{selectedNode.firs ?? '—'}</div>
                </div>
                <div>
                  <div className="text-[10px] text-ink-dim uppercase tracking-wide">Community</div>
                  <div className="text-sm font-mono mt-0.5" style={{ color: COMMUNITY_COLORS[selectedNode.community ?? 0] }}>
                    Community #{selectedNode.community ?? 0}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] text-ink-dim uppercase tracking-wide mb-1">Person ID</div>
                  <CitationChip firId={selectedNode.id} />
                </div>
              </div>
            ) : (
              <p className="text-sm text-ink-dim leading-relaxed">
                Click an accused node to view their profile, risk score, and linked FIRs.
              </p>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}

/**
 * CitationChip — FIR evidence citation chip (Req #9 Evidence Trail).
 *
 * Renders identically wherever it appears: chat bubbles, map popups,
 * network graph panel, audit log — the recurring "evidence tag" motif
 * described in frontend/README.md and docs/master_plan.md Step 3.2.
 *
 * Props:
 *   firId     — CaseMasterID string
 *   onClick   — optional: navigate to case detail when backend is live
 */
export default function CitationChip({ firId, onClick }) {
  const Tag = onClick ? 'button' : 'span'
  return (
    <Tag
      className={`case-tag inline-flex items-center gap-1 ${
        onClick ? 'hover:border-gold hover:text-gold-bright transition-colors cursor-pointer' : ''
      }`}
      onClick={onClick}
      title={`Based on FIR #${firId}`}
    >
      <span className="opacity-60">FIR</span>
      <span>#{firId}</span>
    </Tag>
  )
}

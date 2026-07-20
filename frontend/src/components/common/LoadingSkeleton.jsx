/**
 * LoadingSkeleton — animated shimmer placeholder for async data sections.
 * Uses the .skeleton CSS class defined in index.css.
 *
 * Props:
 *   className  — additional Tailwind classes (width/height overrides)
 *   lines      — render N stacked skeleton rows (for tables/lists)
 */
export default function LoadingSkeleton({ className = 'h-8 w-full', lines = 1 }) {
  if (lines === 1) {
    return <div className={`skeleton ${className}`} aria-hidden="true" />
  }
  return (
    <div className="space-y-2" aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={`skeleton ${className}`}
          style={{ opacity: 1 - i * 0.12 }} // progressively fade lower rows
        />
      ))}
    </div>
  )
}

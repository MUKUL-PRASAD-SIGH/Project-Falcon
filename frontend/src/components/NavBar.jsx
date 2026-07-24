import { NavLink } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { useCatalystSignals } from '@/hooks/useCatalystSignals'
import { useRoleVoice } from '@/hooks/useRoleVoice'
import policeEmblem from '@/assets/police.png'
import otherPhoto from '@/assets/other.png'

const ALL_PATHS = ['/', '/chat', '/map', '/network', '/profiles', '/admin']
const DEV_ROLES = ['Investigator', 'Analyst', 'Admin']

/** Kannada role labels */
const KN_ROLE = {
  Investigator: 'ತನಿಖಾಧಿಕಾರಿ',
  Analyst:      'ವಿಶ್ಲೇಷಕ',
  Admin:        'ನಿರ್ವಾಹಕ',
}

export default function NavBar() {
  const { role, can, isDev, switchRole, logout, demoMode, toggleDemoMode } = useAuth()
  const { alerts } = useCatalystSignals()
  const voice = useRoleVoice()

  const highAlertCount = alerts.filter((a) => a.severity === 'High').length

  const tabs = ALL_PATHS
    .filter((path) => path !== '/admin' || can('Admin'))
    .map((path) => ({
      to:    path,
      end:   path === '/',
      label: voice.navLabels[path] ?? path,
    }))

  return (
    <header className="sticky top-0 z-20 border-b border-[rgba(255,255,255,0.07)] bg-[rgba(4,9,20,0.88)] backdrop-blur-xl">
      <div className="max-w-[1400px] mx-auto px-6 py-2.5 flex items-center gap-5">

        {/* ── Police emblem + wordmark ──────────────────────── */}
        <div className="flex items-center gap-3 shrink-0">
          <img
            src={policeEmblem}
            alt="Karnataka State Police"
            className="w-8 h-8 object-contain opacity-90"
            style={{ filter: `drop-shadow(0 0 5px var(--role-accent))` }}
          />
          <div className="leading-tight hidden sm:block">
            <div className="font-display text-sm font-semibold tracking-widest text-ink uppercase">
              Project Falcon
            </div>
            {/* Kannada subtitle */}
            <div className="text-[9px] text-ink-dim font-mono tracking-wider">
              ಕ.ರಾ.ಪೊ · {KN_ROLE[role] ?? 'Guest'}
            </div>
          </div>
        </div>

        {/* ── Navigation tabs ───────────────────────────────── */}
        <nav className="flex items-center gap-0.5 ml-2 overflow-x-auto scroll-thin flex-1">
          {tabs.map((tab) => (
            <NavLink
              key={tab.to}
              to={tab.to}
              end={tab.end}
              className={({ isActive }) =>
                `nav-tab relative px-3 py-1.5 text-sm font-medium rounded-md transition-all whitespace-nowrap ${
                  isActive
                    ? 'text-ink bg-[rgba(255,255,255,0.08)]'
                    : 'text-ink-dim hover:text-ink hover:bg-[rgba(255,255,255,0.05)]'
                }`
              }
            >
              {tab.label}
              {tab.to === '/' && highAlertCount > 0 && (
                <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-[#D8503A] text-[8px] font-mono text-white flex items-center justify-center leading-none">
                  {highAlertCount > 9 ? '9+' : highAlertCount}
                </span>
              )}
            </NavLink>
          ))}
        </nav>

        {/* ── Right-side: badge photo + role chip + sign out ─── */}
        <div className="flex items-center gap-2.5 shrink-0 ml-auto">

          {/* Karnataka Police badge — subtle, decorative */}
          <img
            src={otherPhoto}
            alt=""
            aria-hidden="true"
            className="w-7 h-7 object-cover rounded-full opacity-40 hidden md:block"
            style={{ border: '1px solid rgba(255,255,255,0.12)' }}
          />

          {isDev ? (
            <select
              value={role ?? ''}
              onChange={(e) => switchRole(e.target.value)}
              className="bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] text-xs px-2 py-1.5 rounded-md font-mono text-ink-dim focus:outline-none cursor-pointer"
              aria-label="Switch role (dev mode)"
            >
              {DEV_ROLES.map((r) => (
                <option key={r} value={r}>{r} — {KN_ROLE[r]}</option>
              ))}
            </select>
          ) : (
            <div className="role-pill">{voice.roleLabel} · {KN_ROLE[role]}</div>
          )}

          {/* Mode Toggle */}
          <button
            onClick={toggleDemoMode}
            className={`text-xs px-2.5 py-1.5 rounded-md font-mono transition-colors border ${
              demoMode
                ? 'bg-blue-500/10 text-blue-400 border-blue-500/20 hover:bg-blue-500/20'
                : 'bg-green-500/10 text-green-400 border-green-500/20 hover:bg-green-500/20'
            }`}
            title="Toggle between Synthetic Demo Data and Real Production Data"
          >
            {demoMode ? 'MODE: DEMO' : 'MODE: PROD'}
          </button>

          <button
            onClick={logout}
            className="btn-ghost text-xs py-1 px-2.5 hover:text-[#D8503A]"
            title="Sign out"
          >
            ಹೊರಹೋಗಿ
          </button>
        </div>
      </div>
    </header>
  )
}

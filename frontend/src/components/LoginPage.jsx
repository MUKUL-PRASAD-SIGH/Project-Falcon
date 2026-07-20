import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import policeEmblem from '@/assets/police.png'

export default function LoginPage() {
  const { loginDev } = useAuth()
  const [isSdkAvailable, setIsSdkAvailable] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    if (window.catalyst && typeof window.catalyst.auth !== 'undefined') {
      setIsSdkAvailable(true)
      try {
        const config = { service_url: '/app/index.html' }
        window.catalyst.auth.signIn('loginDivElementId', config)
      } catch (err) {
        console.error('Error rendering Catalyst Auth Sign In:', err)
      }
    } else {
      setIsSdkAvailable(false)
    }
  }, [])

  const handleDevLogin = (devRole) => {
    loginDev(devRole)
    navigate('/')
  }

  const isLocalhost =
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1'

  const roles = [
    {
      role: 'Investigator',
      title: 'Field Investigator',
      desc: 'Search cases, view live alerts and crime maps.',
      accent: '#00B4D8',
      accentDim: 'rgba(0,180,216,0.08)',
    },
    {
      role: 'Analyst',
      title: 'Intelligence Analyst',
      desc: 'Forecast models, network graphs, and data queries.',
      accent: '#C9A227',
      accentDim: 'rgba(201,162,39,0.08)',
    },
    {
      role: 'Admin',
      title: 'System Administrator',
      desc: 'Audit logs and sensitive records management.',
      accent: '#A855F7',
      accentDim: 'rgba(168,85,247,0.08)',
    },
  ]

  return (
    <div className="min-h-screen flex">
      {/* ── Left panel: branding ─────────────────────────────── */}
      <div
        className="hidden lg:flex flex-col items-center justify-center w-[44%] shrink-0 relative overflow-hidden"
        style={{
          background: 'linear-gradient(160deg, #050C1C 0%, #0A1428 55%, #070E20 100%)',
          borderRight: '1px solid rgba(255,255,255,0.05)',
        }}
      >
        {/* Emblem watermark */}
        <div
          className="absolute inset-0 flex items-center justify-center pointer-events-none"
          aria-hidden="true"
        >
          <img
            src={policeEmblem}
            alt=""
            className="w-[380px] opacity-[0.06] select-none"
            style={{ filter: 'grayscale(0.2) brightness(1.4)' }}
          />
        </div>

        {/* Foreground content */}
        <div className="relative z-10 flex flex-col items-center text-center px-12 gap-6">
          <img
            src={policeEmblem}
            alt="Karnataka State Police"
            className="w-24 h-24 object-contain drop-shadow-[0_0_24px_rgba(201,162,39,0.18)]"
          />
          <div>
            <div className="font-display text-2xl font-bold tracking-widest text-ink uppercase">
              Project Falcon
            </div>
            <div className="text-[11px] text-ink-dim font-mono tracking-widest uppercase mt-1.5">
              Karnataka State Police
            </div>
            <div className="text-[11px] text-ink-dim font-mono tracking-widest uppercase">
              Intelligence &amp; Crime Analytics Console
            </div>
          </div>
          <div
            className="mt-4 px-5 py-3 rounded-lg text-[11px] text-ink-dim leading-relaxed max-w-[280px]"
            style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}
          >
            Authorised access only. All activity is monitored and recorded in compliance with applicable laws.
          </div>
        </div>
      </div>

      {/* ── Right panel: login form ───────────────────────────── */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-10">
        {/* Mobile logo */}
        <div className="flex lg:hidden flex-col items-center mb-8 gap-3">
          <img src={policeEmblem} alt="Karnataka State Police" className="w-14 h-14 object-contain" />
          <div className="text-center">
            <div className="font-display text-lg font-bold tracking-widest text-ink uppercase">Project Falcon</div>
            <div className="text-[10px] text-ink-dim font-mono tracking-widest uppercase">Karnataka State Police</div>
          </div>
        </div>

        <div className="w-full max-w-[400px] space-y-5">
          <div className="mb-1">
            <h2 className="font-display text-xl font-bold">Sign in</h2>
            <p className="text-sm text-ink-dim mt-0.5">
              {isSdkAvailable
                ? 'Use your Zoho Catalyst credentials to continue.'
                : 'Select a profile to enter the console.'}
            </p>
          </div>

          {/* ── Catalyst SDK auth form ──────────────────────── */}
          {isSdkAvailable ? (
            <div className="space-y-4">
              <div
                id="loginDivElementId"
                className="w-full min-h-[380px]"
              />
              <p className="text-center text-[10px] text-ink-dim font-mono">
                Secured by Zoho Catalyst · Single Sign-On
              </p>
            </div>
          ) : (
            /* ── Dev fallback: role selector ─────────────── */
            <div className="space-y-3">
              <div
                className="px-3 py-2 rounded-md text-[10px] font-mono uppercase tracking-wider text-center"
                style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', color: '#93A0B8' }}
              >
                Developer Mode — Catalyst SDK not detected
              </div>

              {roles.map(({ role, title, desc, accent, accentDim }) => (
                <button
                  key={role}
                  onClick={() => handleDevLogin(role)}
                  className="w-full text-left p-4 rounded-lg transition-all flex justify-between items-center group cursor-pointer"
                  style={{
                    border: '1px solid rgba(255,255,255,0.08)',
                    background: 'rgba(9,16,33,0.5)',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = `${accent}55`
                    e.currentTarget.style.background = accentDim
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'
                    e.currentTarget.style.background = 'rgba(9,16,33,0.5)'
                  }}
                >
                  <div className="space-y-0.5">
                    <div className="text-sm font-semibold text-ink">{title}</div>
                    <div className="text-[11px] text-ink-dim font-normal leading-snug">{desc}</div>
                  </div>
                  <span
                    className="text-[10px] font-mono font-semibold px-2.5 py-1 rounded-md shrink-0 ml-4"
                    style={{ color: accent, background: `${accent}18`, border: `1px solid ${accent}30` }}
                  >
                    Enter
                  </span>
                </button>
              ))}
            </div>
          )}

          {/* ── Dev bypass when SDK is loaded locally ──────── */}
          {isSdkAvailable && isLocalhost && (
            <div
              className="pt-4 space-y-3"
              style={{ borderTop: '1px solid rgba(255,255,255,0.07)' }}
            >
              <p className="text-[10px] text-ink-dim font-mono text-center uppercase tracking-wider">
                Developer Role Bypass
              </p>
              <div className="grid grid-cols-3 gap-2">
                {roles.map(({ role, accent }) => (
                  <button
                    key={role}
                    onClick={() => handleDevLogin(role)}
                    className="py-2 px-1 text-center rounded-md text-[11px] font-medium text-ink-dim transition-all cursor-pointer"
                    style={{ border: '1px solid rgba(255,255,255,0.08)', background: 'rgba(255,255,255,0.03)' }}
                    onMouseEnter={(e) => { e.currentTarget.style.color = accent; e.currentTarget.style.borderColor = `${accent}40` }}
                    onMouseLeave={(e) => { e.currentTarget.style.color = ''; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)' }}
                  >
                    {role}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

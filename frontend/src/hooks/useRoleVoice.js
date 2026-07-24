/**
 * useRoleVoice — Role-adaptive UI strings hook.
 *
 * Returns all display text, stat definitions, and chat config
 * appropriate for the currently signed-in role.
 *
 * Components should consume this instead of hardcoding labels,
 * so Investigators see plain English and Analysts see technical terms.
 */
import { useAuth } from '@/context/AuthContext'

/** Returns the greeting based on current hour */
export function getTimeOfDay() {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 17) return 'afternoon'
  return 'evening'
}

/* ─── Investigator Voice ─────────────────────────────────────────── */
const INVESTIGATOR = {
  homeTitle: "Today's Operations",
  showGreeting: true,
  roleLabel: 'Field Investigator',

  navLabels: {
    '/':        'Overview',
    '/chat':    'Ask Falcon',
    '/map':     'Crime Map',
    '/network': 'Connections',
    '/profiles': 'Profiles & Cases',
    '/admin':   'Admin',
  },

  stats: [
    { key: 'activeFirs',   label: 'Open Cases',          tag: 'Live',      mock: '12,438' },
    { key: 'avgRisk',      label: 'High-Risk Suspects',  tag: 'AI Scored', mock: '41 / 100' },
    { key: 'anomalyCount', label: 'Active Alerts',       tag: 'Urgent',    mock: '63', alert: true },
    { key: 'p95Latency',   label: 'System Status',       tag: 'Online',    mock: 'Operational' },
  ],

  chartTitle:    'Crime Trend This Month',
  chartSubtitle: 'AI-predicted cases for the next 7 days',
  chartTag:      null,

  anomalyTitle: 'Alerts Needing Attention',
  anomalyEmpty: 'All clear — no active alerts right now',
  severityLabel: (s) => ({ High: 'Urgent', Medium: 'Watch', Low: 'Info' }[s] ?? s),

  chatHeader:        'Ask Falcon',
  chatSubtitle:      'Get instant answers about cases, suspects, and crime patterns',
  chatTag:           null,
  chatPlaceholder:   'Ask anything — e.g. "robberies in Whitefield last month"',
  chatPlaceholderKN: 'ಪ್ರಶ್ನೆ ಕೇಳಿ…',

  seedMessages: [
    { role: 'user', text: 'Show me recent incidents in Electronic City this month.' },
    {
      role: 'ai',
      text: 'Found 3 high-activity areas in Electronic City with a spike in robbery reports, mostly on weekend nights. The situation is worsening — a 12% increase is expected next week. One known suspect (#A1) is linked to these incidents.',
      citations: ['104430006202600231', '104430006202600198'],
    },
  ],

  suggestedPrompts: [
    'Show nearby incidents in my district',
    'Look up a high-risk suspect',
    'What happened this week?',
    'Where are the crime hotspots?',
  ],
}

/* ─── Analyst Voice ──────────────────────────────────────────────── */
const ANALYST = {
  homeTitle: 'Command Center',
  showGreeting: false,
  roleLabel: 'Intelligence Analyst',

  navLabels: {
    '/':        'Command Center',
    '/chat':    'Intelligence Chat',
    '/map':     'Crime Map',
    '/network': 'Network Graph',
    '/profiles': 'Profiles & Cases',
    '/admin':   'Audit & Access',
  },

  stats: [
    { key: 'activeFirs',   label: 'Active FIRs',                tag: 'DataStore',      mock: '12,438' },
    { key: 'avgRisk',      label: 'Repeat-Offender Risk (avg)', tag: 'Zia AutoML',     mock: '41 / 100' },
    { key: 'anomalyCount', label: 'Flagged Anomalies (7d)',     tag: 'Zia AutoML',     mock: '63', alert: true },
    { key: 'p95Latency',   label: 'API p95 Latency',            tag: 'Catalyst Cache', mock: '318ms' },
  ],

  chartTitle:    'Crime Trend — SARIMA Forecast',
  chartSubtitle: null,
  chartTag:      'AppSail · SARIMA',

  anomalyTitle: 'Live Anomaly Feed',
  anomalyEmpty: 'No active anomalies',
  severityLabel: (s) => s,

  chatHeader:        'Intelligence Chat',
  chatSubtitle:      'QuickML NL-to-SQL + RAG · Circuits Pipeline',
  chatTag:           'QuickML · RAG · Circuits',
  chatPlaceholder:   'Ask about cases, districts, accused, hotspots…',
  chatPlaceholderKN: 'ಪ್ರಶ್ನೆ ಕೇಳಿ… (Zia Services)',

  seedMessages: [
    { role: 'user', text: 'Show robbery hotspots in Electronic City, last 6 months.' },
    {
      role: 'ai',
      text: 'Identified 3 clusters in Electronic City with elevated robbery frequency, concentrated on weekend nights. Risk tier: High. SARIMA 7-day forecast shows continued upward trend (+12%). Nearest confirmed network node: Accused ID #A1.',
      citations: ['104430006202600231', '104430006202600198'],
    },
  ],

  suggestedPrompts: [
    'DBSCAN clusters in Bengaluru — last 7 days',
    'Network graph for accused #A1',
    'SARIMA 30-day forecast by district',
    'Repeat offender risk score distribution',
  ],
}

/* ─── Admin inherits Analyst voice with purple accent ───────────── */
const ADMIN = {
  ...ANALYST,
  roleLabel: 'System Administrator',
}

const VOICE_MAP = {
  Investigator: INVESTIGATOR,
  Analyst:      ANALYST,
  Admin:        ADMIN,
}

/** Hook — returns role-adaptive UI config for the current signed-in user */
export function useRoleVoice() {
  const { role } = useAuth()
  return VOICE_MAP[role] ?? INVESTIGATOR
}

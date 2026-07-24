/**
 * Named API call functions — one for every backend endpoint defined in master_plan.md.
 * All calls go through the shared Axios client (auth interceptors included).
 *
 * Phase 2 complete: all ML + forensics + cache endpoints wired.
 */
import client from './client'

/* ── Dashboard / Command Center ─────────────────────────────────── */

/** GET /api/stats — KPI metrics from ML outputs */
export const fetchStats = () =>
  client.get('/api/stats').then((r) => r.data)

/**
 * GET /api/districts — K-Means district risk stats.
 * Served from Catalyst Cache (p95 < 500ms target).
 * Returns: { status, source, cache_ttl_s?, latency_ms?, districts: [] }
 */
export const fetchDistricts = () =>
  client.get('/api/districts').then((r) => r.data)

/** GET /api/anomalies?min_score=0.5 — QuickML flagged FIR anomalies */
export const fetchAnomalies = (minScore = 0.5) =>
  client.get('/api/anomalies', { params: { min_score: minScore } }).then((r) => r.data)

/** GET /api/forecast?district={name} — SARIMA 7d + 30d prediction */
export const fetchForecast = (district) =>
  client.get('/api/forecast', { params: district ? { district } : undefined }).then((r) => r.data)

/* ── Crime Map ──────────────────────────────────────────────────── */

/**
 * GET /api/clusters?time={bucket}&district={name} — DBSCAN crime clusters GeoJSON.
 * Cache-backed (TTL = 30 min).
 */
export const fetchClusters = (time = 'All', district = null) => {
  const params = {}
  if (time && time !== 'All') params.time = time
  if (district) params.district = district
  return client.get('/api/clusters', { params }).then((r) => r.data)
}

/* ── Network Graph ──────────────────────────────────────────────── */

/** GET /api/graph/accused/{accusedId}?depth={1-3} — Louvain subgraph JSON */
export const fetchAccusedGraph = (accusedId, depth = 2) =>
  client.get(`/api/graph/accused/${accusedId}`, { params: { depth } }).then((r) => r.data)

/** GET /api/graph/gangs — Gang network community overview */
export const fetchGangs = () =>
  client.get('/api/graph/gangs').then((r) => r.data)

/* ── Risk & Anomalies ───────────────────────────────────────────── */

/** GET /api/offender/risk/{accusedId} — QuickML 0-100 risk score */
export const fetchRiskScore = (accusedId) =>
  client.get(`/api/offender/risk/${accusedId}`).then((r) => r.data?.data ?? r.data)

/* ── Case Similarity ────────────────────────────────────────────── */

/** GET /api/cases/similar?case_id={id} — TF-IDF cosine top-5 similar cases */
export const fetchSimilarCases = (caseId) =>
  client.get('/api/cases/similar', { params: { case_id: caseId } }).then((r) => r.data)

/**
 * POST /api/chat/query — FALCON AI Circuits (RAG + GLM-4.7-Flash).
 * Returns: { answer, citations: string[], is_live, model }
 */
export const postQuery = (text, sessionId, language = 'EN') =>
  client
    .post('/api/chat/query', { query: text, session_id: sessionId })
    .then((r) => ({
      answer:    r.data.response ?? 'No response received.',
      citations: (r.data.retrieved_nodes ?? []).map((n) => n.document_id ?? n.document_title),
      is_live:   r.data.is_live ?? false,
      model:     r.data.model ?? 'offline',
    }))

/* ── Forensic Evidence Verification (Kapoun Criteria) ───────────── */

/**
 * POST /api/forensics/verify
 *
 * Body: {
 *   urls: [{ url: string, label?: string, case_id?: number }],
 *   case_context?: string,
 *   analyst?: string
 * }
 *
 * Returns ranked evidence list with Kapoun scores (0-100 each).
 * Grade: A (85+), B (70+), C (55+), D (40+), F (<40)
 */
export const verifyEvidence = (urls, caseContext = null, analyst = null) =>
  client.post('/api/forensics/verify', {
    urls,
    case_context: caseContext,
    analyst: analyst || 'analyst@ksp.gov.in',
  }).then((r) => r.data)

/** GET /api/forensics/criteria — Kapoun Criteria rubric definition */
export const fetchKapounCriteria = () =>
  client.get('/api/forensics/criteria').then((r) => r.data)

/** GET /api/forensics/case/{caseId} — Evidence refs linked to a case */
export const fetchCaseEvidence = (caseId) =>
  client.get(`/api/forensics/case/${caseId}`).then((r) => r.data)

/* ── Cache Management ───────────────────────────────────────────── */

/** POST /api/cache/invalidate — Flush district + cluster cache (Admin) */
export const invalidateGeoCache = () =>
  client.post('/api/cache/invalidate').then((r) => r.data)

/* ── Voice (Zia STT) ────────────────────────────────────────────── */

/**
 * POST /api/voice/transcribe — Zia Services speech-to-text.
 * Sends FormData with an audio Blob.
 */
export const transcribeAudio = (audioBlob, language = 'EN') => {
  const form = new FormData()
  form.append('audio', audioBlob, 'recording.webm')
  form.append('language', language)
  return client.post('/api/voice/transcribe', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }).then((r) => r.data)
}

/* ── SmartBrowz PDF Export ──────────────────────────────────────── */

/**
 * POST /api/export/pdf — SmartBrowz Evidence Trail PDF.
 * Returns a Blob that can be downloaded by the browser.
 */
export const exportEvidencePDF = (messages, citations) =>
  client.post(
    '/api/export/pdf',
    { messages, citations },
    { responseType: 'blob' }
  ).then((r) => r.data)

/* ── Admin ──────────────────────────────────────────────────────── */

/** GET /api/admin/audit — full audit log (Admin role only) */
export const fetchAuditLog = () =>
  client.get('/api/admin/audit').then((r) => r.data)

/** GET /api/admin/users — user list (Admin role only) */
export const fetchUsers = () =>
  client.get('/api/admin/users').then((r) => r.data)

/** GET /api/admin/stats — system health stats (Admin role only) */
export const fetchAdminStats = () =>
  client.get('/api/admin/stats').then((r) => r.data)

/** GET /api/admin/victims — PII victim registry (Admin role only) */
export const fetchVictims = () =>
  client.get('/api/admin/victims').then((r) => r.data)

/** GET /health — Lightweight backend health probe */
export const fetchHealth = () =>
  client.get('/health').then((r) => r.data)

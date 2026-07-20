/**
 * Named API call functions — one for every backend endpoint defined in master_plan.md.
 * All calls go through the shared Axios client (auth interceptors included).
 *
 * Replace mock data fallbacks with real calls as each AppSail endpoint comes online.
 */
import client from './client'

/* ── Dashboard / Command Center ─────────────────────────────────── */

/** GET /api/districts — district risk stats (Catalyst Cache p95 < 500ms) */
export const fetchDistricts = () =>
  client.get('/api/districts').then((r) => r.data)

/** GET /api/anomalies — Zia AutoML flagged FIR anomalies */
export const fetchAnomalies = () =>
  client.get('/api/anomalies').then((r) => r.data)

/** GET /api/forecast?district={id} — SARIMA 7d + 30d prediction */
export const fetchForecast = (districtId) =>
  client.get('/api/forecast', { params: { district: districtId } }).then((r) => r.data)

/* ── Crime Map ──────────────────────────────────────────────────── */

/** GET /api/clusters?time={bucket} — DBSCAN crime clusters GeoJSON */
export const fetchClusters = (time = 'All') =>
  client.get('/api/clusters', { params: { time } }).then((r) => r.data)

/* ── Network Graph ──────────────────────────────────────────────── */

/** GET /api/graph/accused/{accusedId} — Louvain subgraph JSON */
export const fetchAccusedGraph = (accusedId) =>
  client.get(`/api/graph/accused/${accusedId}`).then((r) => r.data)

/** GET /api/risk/{accusedId} — Zia AutoML 0-100 risk score */
export const fetchRiskScore = (accusedId) =>
  client.get(`/api/risk/${accusedId}`).then((r) => r.data)

/* ── Intelligence Chat ──────────────────────────────────────────── */

/**
 * POST /api/query — Catalyst Circuits pipeline.
 * Returns: { answer, citations: string[], intent, map_trigger, graph_trigger }
 */
export const postQuery = (text, sessionId, language = 'EN') =>
  client.post('/api/query', { text, session_id: sessionId, language }).then((r) => r.data)

/** GET /api/cases/similar?case_id={id} — TF-IDF top-5 similar cases */
export const fetchSimilarCases = (caseId) =>
  client.get('/api/cases/similar', { params: { case_id: caseId } }).then((r) => r.data)

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

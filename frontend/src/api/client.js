import axios from 'axios'

/**
 * Axios client for Project Falcon.
 *
 * Base URL from VITE_API_BASE_URL (set in .env.local / .env.production).
 * When Catalyst Auth JWT is live (Step 4.6), attach the token in
 * the request interceptor below.
 */
const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/* ── Request interceptor: attach JWT ─────────────────────────────── */
client.interceptors.request.use(
  (config) => {
    // TODO (Step 4.6): read token from Catalyst Auth SDK
    // const token = catalystAuth.getToken()
    // if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

/* ── Response interceptor: handle 401 / 403 / 429 ──────────────── */
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    if (status === 401) {
      // Token expired — trigger re-login when Auth is wired
      console.warn('[Falcon API] 401 Unauthorised — re-authentication required')
    }
    if (status === 403) {
      console.warn('[Falcon API] 403 Forbidden — insufficient role')
    }
    if (status === 429) {
      console.warn('[Falcon API] 429 Rate limited by Catalyst API Gateway (100 req/min)')
    }
    return Promise.reject(error)
  }
)

export default client

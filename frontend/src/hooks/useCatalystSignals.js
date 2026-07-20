import { useEffect, useRef, useState, useCallback } from 'react'

/**
 * useCatalystSignals — subscribes to the Catalyst Push Notification WebSocket
 * for real-time `anomaly_spike` events (Step 3.6 / 4.5).
 *
 * Usage:
 *   const { alerts, clearAlerts } = useCatalystSignals()
 *
 * Each alert shape: { id, district, crimeType, firCount, severity, ts }
 *
 * While VITE_PUSH_WS_URL is not set (pre-Step 3.6), returns mock alerts
 * so the Dashboard anomaly panel is immediately functional.
 */

const MOCK_ALERTS = [
  {
    id: '104430006202600231',
    district: 'Electronic City',
    crimeType: 'Property Crime',
    firCount: 47,
    severity: 'High',
    ts: new Date().toISOString()
  },
  {
    id: '104430006202600198',
    district: 'Whitefield',
    crimeType: 'Robbery',
    firCount: 23,
    severity: 'High',
    ts: new Date(Date.now() - 12 * 60_000).toISOString()
  }
]

export function useCatalystSignals() {
  const [alerts, setAlerts] = useState(MOCK_ALERTS)
  const wsRef = useRef(null)
  const wsUrl = import.meta.env.VITE_PUSH_WS_URL

  useEffect(() => {
    if (!wsUrl) return // no WS URL yet — using mock data

    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data)
        if (payload.type === 'anomaly_spike') {
          setAlerts((prev) => [
            {
              id: payload.case_master_id,
              district: payload.district,
              crimeType: payload.crime_type,
              firCount: payload.fir_count,
              severity: payload.severity,
              ts: payload.timestamp ?? new Date().toISOString()
            },
            ...prev.slice(0, 19) // keep latest 20
          ])
        }
      } catch {
        console.warn('[useCatalystSignals] Failed to parse Push payload', event.data)
      }
    }

    ws.onerror = () => console.warn('[useCatalystSignals] WebSocket error — check VITE_PUSH_WS_URL')

    return () => {
      ws.close()
      wsRef.current = null
    }
  }, [wsUrl])

  const clearAlerts = useCallback(() => setAlerts([]), [])

  return { alerts, clearAlerts }
}

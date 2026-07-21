import { createContext, useContext, useState, useCallback, useEffect } from 'react'

const AuthContext = createContext(null)
const VALID_ROLES = ['Investigator', 'Analyst', 'Admin']

export function AuthProvider({ children }) {
  const [role, setRole] = useState(null)
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isDev, setIsDev] = useState(true)
  const [demoMode, setDemoMode] = useState(() => {
    return localStorage.getItem('falcon_demo_mode') !== 'false'
  })

  // Initialize authentication state
  useEffect(() => {
    // 1. Check for local developer session override (useful for testing on localhost)
    const cachedRole = localStorage.getItem('falcon_dev_role')
    if (cachedRole && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
      setIsDev(true)
      setRole(cachedRole)
      setUser({ email: `${cachedRole.toLowerCase()}@ksp.test`, firstName: 'Dev', lastName: 'User' })
      setLoading(false)
      return
    }

    // 2. Otherwise, verify Catalyst session
    if (window.catalyst && typeof window.catalyst.auth !== 'undefined') {
      setIsDev(false)
      window.catalyst.auth.isUserAuthenticated()
        .then((response) => {
          const userObj = response && (response.content || response)
          if (userObj) {
            setUser(userObj)
            // Fetch user's role from get_user_role serverless function
            return window.catalyst.function.execute('get_user_role')
              .then((result) => {
                let roleVal = 'Investigator' // safe default
                try {
                  const data = typeof result === 'string' ? JSON.parse(result) : result
                  roleVal = data.role || data.output || 'Investigator'
                } catch (e) {
                  roleVal = result?.role || result || 'Investigator'
                }
                
                if (VALID_ROLES.includes(roleVal)) {
                  setRole(roleVal)
                } else {
                  setRole('Investigator')
                }
              })
              .catch((err) => {
                console.error('Failed to resolve role via get_user_role function:', err)
                setRole('Investigator') // fallback to minimum role if ZCQL lookup fails
              })
          } else {
            setUser(null)
            setRole(null)
          }
        })
        .catch((err) => {
          // A promise reject here simply means the user is not authenticated (normal flow)
          setUser(null)
          setRole(null)
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      // Pure Dev Mode (no SDK loaded)
      setIsDev(true)
      setUser(null)
      setRole(null)
      setLoading(false)
    }
  }, [])

  const loginDev = useCallback((devRole) => {
    if (VALID_ROLES.includes(devRole)) {
      localStorage.setItem('falcon_dev_role', devRole)
      setRole(devRole)
      setUser({ email: `${devRole.toLowerCase()}@ksp.test`, firstName: 'Dev', lastName: 'User' })
    }
  }, [])

  const logout = useCallback(() => {
    if (isDev) {
      localStorage.removeItem('falcon_dev_role')
      setRole(null)
      setUser(null)
    } else {
      setLoading(true)
      window.catalyst.auth.signOut('/app/index.html')
    }
  }, [isDev])

  // Direct state toggle for dev selector in NavBar
  const switchRole = useCallback((newRole) => {
    if (isDev) {
      loginDev(newRole)
    } else {
      console.warn('Manual role switching is disabled in Catalyst Auth mode. Access is governed by Database roles.')
    }
  }, [isDev, loginDev])

  const toggleDemoMode = useCallback(() => {
    setDemoMode((prev) => {
      const newVal = !prev
      localStorage.setItem('falcon_demo_mode', String(newVal))
      return newVal
    })
  }, [])

  /** Returns true when the signed-in role has at least the given permission level */
  const can = useCallback((requiredRole) => {
    if (!role) return false
    const levels = { Investigator: 0, Analyst: 1, Admin: 2 }
    return (levels[role] ?? -1) >= (levels[requiredRole] ?? 99)
  }, [role])

  return (
    <AuthContext.Provider value={{ role, user, loading, isDev, loginDev, logout, switchRole, can, demoMode, toggleDemoMode }}>
      {!loading && children}
    </AuthContext.Provider>
  )
}

/** Hook — throws if used outside <AuthProvider> */
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}

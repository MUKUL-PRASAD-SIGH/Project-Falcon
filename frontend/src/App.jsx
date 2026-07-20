import { Routes, Route } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/context/AuthContext'
import RouteGuard from '@/auth/RouteGuard'
import NavBar from '@/components/NavBar'
import LoginPage from '@/components/LoginPage'
import InvestigatorDashboard from '@/components/Dashboard/Dashboard'
import AnalystDashboard from '@/components/Dashboard/AnalystDashboard'
import AdminDashboard from '@/components/Dashboard/AdminDashboard'
import ChatWindow from '@/components/Chat/ChatWindow'
import CrimeMap from '@/components/CrimeMap'
import NetworkGraph from '@/components/NetworkGraph'
import AdminPanel from '@/components/AdminPanel'
import ErrorBoundary from '@/components/common/ErrorBoundary'

/**
 * Role-adaptive root — returns the right dashboard component for the
 * signed-in role so each role gets a completely different layout.
 *
 *   Investigator → hero-map command view
 *   Analyst      → data-dense stats / chart layout (old dashboard)
 *   Admin        → audit overview + PII registry
 */
function RoleDashboard() {
  const { role } = useAuth()
  if (role === 'Admin')    return <AdminDashboard />
  if (role === 'Analyst')  return <AnalystDashboard />
  return <InvestigatorDashboard />   // default / Investigator
}

function AppContent() {
  const { role } = useAuth()

  return (
    <div className="flex flex-col min-h-screen" data-role={role ?? ''}>
      {role && <NavBar />}
      <main className="flex-1 flex flex-col">
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route
            path="/"
            element={
              <RouteGuard>
                <ErrorBoundary label="Dashboard">
                  <RoleDashboard />
                </ErrorBoundary>
              </RouteGuard>
            }
          />
          <Route
            path="/chat"
            element={
              <RouteGuard>
                <ErrorBoundary label="Intelligence Chat">
                  <ChatWindow />
                </ErrorBoundary>
              </RouteGuard>
            }
          />
          <Route
            path="/map"
            element={
              <RouteGuard>
                <ErrorBoundary label="Crime Map">
                  <CrimeMap />
                </ErrorBoundary>
              </RouteGuard>
            }
          />
          <Route
            path="/network"
            element={
              <RouteGuard>
                <ErrorBoundary label="Network Graph">
                  <NetworkGraph />
                </ErrorBoundary>
              </RouteGuard>
            }
          />
          <Route
            path="/admin"
            element={
              <RouteGuard requiredRole="Admin">
                <ErrorBoundary label="Audit & Access">
                  <AdminPanel />
                </ErrorBoundary>
              </RouteGuard>
            }
          />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

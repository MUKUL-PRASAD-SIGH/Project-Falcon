import { Navigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'

/**
 * RouteGuard — Auth and RBAC route protection.
 *
 * If the user is not authenticated (role is null), redirects to `/login`.
 * If `requiredRole` is specified and the user does not have sufficient permissions,
 * redirects to the home page `/`.
 */
export default function RouteGuard({ requiredRole, redirectTo = '/login', children }) {
  const { role, can } = useAuth()

  // 1. Not authenticated
  if (!role) {
    return <Navigate to={redirectTo} replace />
  }

  // 2. Insufficient permissions for RBAC
  if (requiredRole && !can(requiredRole)) {
    return <Navigate to="/" replace />
  }

  return children
}

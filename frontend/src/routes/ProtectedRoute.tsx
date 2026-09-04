
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../lib/useAuth'

export const ProtectedRoute = () => {
  const { session, loading } = useAuth()

  if (loading) {
    return (
      <div style={{ display: 'grid', placeItems: 'center', height: '100vh', background: 'var(--cream)' }}>
        <p style={{ fontFamily: 'var(--font-mono)' }}>Loading...</p>
      </div>
    )
  }

  if (!session) {
    return <Navigate to="/auth" replace />
  }

  return <Outlet />
}

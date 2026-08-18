import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { LoadingScreen } from '@/components/ui/Spinner'

export function RequireAuth() {
  const { isAuthenticated, isPending } = useAuth()
  const location = useLocation()

  if (isPending) return <LoadingScreen message="Waking the server" />
  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  return <Outlet />
}

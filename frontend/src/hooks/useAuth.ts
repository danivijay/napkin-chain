import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'

export function useAuth() {
  const query = useQuery({
    queryKey: ['auth'],
    queryFn: api.me,
    staleTime: 5 * 60_000,
  })

  return {
    ...query,
    user: query.data?.user ?? null,
    isAuthenticated: query.data?.authenticated ?? false,
    googleEnabled: query.data?.googleEnabled ?? false,
    devLoginEnabled: query.data?.devLoginEnabled ?? false,
  }
}

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.logout,
    onSuccess: () => queryClient.clear(),
  })
}

export function useDevLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ email, name }: { email: string; name: string }) => api.devLogin(email, name),
    onSuccess: (data) => queryClient.setQueryData(['auth'], data),
  })
}

import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from '@/routes/AppLayout'
import { ChallengeLibrary } from '@/routes/ChallengeLibrary'
import { ChallengeOverview } from '@/routes/ChallengeOverview'
import { ConceptDetailPage } from '@/routes/ConceptDetail'
import { Home } from '@/routes/Home'
import { Landing } from '@/routes/Landing'
import { LearnLibrary } from '@/routes/LearnLibrary'
import { Login } from '@/routes/Login'
import { Privacy } from '@/routes/Privacy'
import { Profile } from '@/routes/Profile'
import { ProgressDashboard } from '@/routes/ProgressDashboard'
import { RequireAuth } from '@/routes/RequireAuth'
import { Result } from '@/routes/Result'
import { Workspace } from '@/routes/Workspace'

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/privacy" element={<Privacy />} />

      <Route element={<RequireAuth />}>
        {/* The workspace owns the whole viewport - no app chrome competing with the napkin. */}
        <Route path="/app/challenges/:slug/build" element={<Workspace />} />

        <Route path="/app" element={<AppLayout />}>
          <Route index element={<Home />} />
          <Route path="challenges" element={<ChallengeLibrary />} />
          <Route path="challenges/:slug" element={<ChallengeOverview />} />
          <Route path="challenges/:slug/result" element={<Result />} />
          <Route path="learn" element={<LearnLibrary />} />
          <Route path="learn/:conceptId" element={<ConceptDetailPage />} />
          <Route path="progress" element={<ProgressDashboard />} />
          <Route path="profile" element={<Profile />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

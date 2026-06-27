import { Navigate, Route, Routes } from 'react-router-dom'
import { Box, CssBaseline, ThemeProvider } from '@mui/material'

import { AppShell } from './components/AppShell'
import { useThemeMode } from './context/ThemeModeContext'
import { DashboardPage } from './pages/DashboardPage'
import { ContentAnalysisPage } from './pages/ContentAnalysisPage'
import { ModeratorQueuePage } from './pages/ModeratorQueuePage'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { ExplanationsPage } from './pages/ExplanationsPage'
import { createAppTheme } from './theme'

export default function App() {
  const { mode } = useThemeMode()
  const theme = createAppTheme(mode)

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', background: theme.palette.background.default }}>
        <AppShell>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/analysis" element={<ContentAnalysisPage />} />
            <Route path="/queue" element={<ModeratorQueuePage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/explanations" element={<ExplanationsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AppShell>
      </Box>
    </ThemeProvider>
  )
}

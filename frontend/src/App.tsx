import React, { useMemo, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material'
import Dashboard from './pages/Dashboard'
import ContentAnalysis from './pages/ContentAnalysis'
import ModeratorQueue from './pages/ModeratorQueue'
import Analytics from './pages/Analytics'
import Explanations from './pages/Explanations'
import Header from './components/Header'

export default function App() {
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    const v = localStorage.getItem('ms:dark')
    return v ? v === '1' : true
  })

  const theme = useMemo(
    () =>
      createTheme({
        palette: { mode: darkMode ? 'dark' : 'light' },
      }),
    [darkMode]
  )

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Header darkMode={darkMode} setDarkMode={(v) => { setDarkMode(v); localStorage.setItem('ms:dark', v ? '1' : '0') }} />
      <main style={{ padding: 16 }}>
        <Routes>
          <Route path='/' element={<Navigate to='/dashboard' replace />} />
          <Route path='/dashboard' element={<Dashboard />} />
          <Route path='/analysis' element={<ContentAnalysis />} />
          <Route path='/queue' element={<ModeratorQueue />} />
          <Route path='/analytics' element={<Analytics />} />
          <Route path='/explanations' element={<Explanations />} />
        </Routes>
      </main>
    </ThemeProvider>
  )
}
import { Navigate, Route, Routes } from 'react-router-dom'
import { Box } from '@mui/material'

import { AppShell } from './components/AppShell'
import { useThemeMode } from './context/ThemeModeContext'
import { DashboardPage } from './pages/DashboardPage'
import { ContentAnalysisPage } from './pages/ContentAnalysisPage'
import { ModeratorQueuePage } from './pages/ModeratorQueuePage'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { ExplanationsPage } from './pages/ExplanationsPage'
import { createAppTheme } from './theme'
import { ThemeProvider } from '@mui/material/styles'

export default function App() {
  const { mode } = useThemeMode()
  const theme = createAppTheme(mode)

  return (
    <ThemeProvider theme={theme}>
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

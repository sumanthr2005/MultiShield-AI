import { createContext, useContext, useEffect, useState } from 'react'

import type { ReactNode } from 'react'
import type { ThemeMode } from '../theme'

type ThemeModeContextValue = {
  mode: ThemeMode
  toggleMode: () => void
}

const ThemeModeContext = createContext<ThemeModeContextValue | undefined>(undefined)

export function ThemeModeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<ThemeMode>(() => {
    const stored = window.localStorage.getItem('multishield-theme')
    return stored === 'light' ? 'light' : 'dark'
  })

  useEffect(() => {
    window.localStorage.setItem('multishield-theme', mode)
  }, [mode])

  return (
    <ThemeModeContext.Provider
      value={{
        mode,
        toggleMode: () => setMode((current) => (current === 'dark' ? 'light' : 'dark')),
      }}
    >
      {children}
    </ThemeModeContext.Provider>
  )
}

export function useThemeMode() {
  const value = useContext(ThemeModeContext)
  if (!value) {
    throw new Error('useThemeMode must be used within ThemeModeProvider')
  }
  return value
}

import { alpha, createTheme } from '@mui/material/styles'

export type ThemeMode = 'dark' | 'light'

export function createAppTheme(mode: ThemeMode) {
  const isDark = mode === 'dark'

  return createTheme({
    palette: {
      mode,
      primary: {
        main: isDark ? '#7ce7ff' : '#005f73',
      },
      secondary: {
        main: isDark ? '#ff8fab' : '#bb3e03',
      },
      background: {
        default: isDark ? '#07111f' : '#f4f7fb',
        paper: isDark ? '#0d1a2d' : '#ffffff',
      },
      success: { main: '#2ec4b6' },
      warning: { main: '#ffb703' },
      error: { main: '#ef476f' },
      text: {
        primary: isDark ? '#ecf4ff' : '#10212f',
        secondary: isDark ? '#9fb4c9' : '#4a6178',
      },
    },
    typography: {
      fontFamily: ['Inter', 'system-ui', 'sans-serif'].join(','),
      h4: { fontWeight: 800, letterSpacing: -0.8 },
      h5: { fontWeight: 750, letterSpacing: -0.5 },
      h6: { fontWeight: 700 },
    },
    shape: { borderRadius: 18 },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            backgroundImage: isDark
              ? 'radial-gradient(circle at top left, rgba(124, 231, 255, 0.12), transparent 28%), radial-gradient(circle at top right, rgba(255, 143, 171, 0.10), transparent 22%)'
              : 'radial-gradient(circle at top left, rgba(0, 95, 115, 0.08), transparent 25%), radial-gradient(circle at top right, rgba(187, 62, 3, 0.06), transparent 22%)',
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backdropFilter: 'blur(18px)',
            border: `1px solid ${alpha(isDark ? '#88d7ff' : '#99aabb', 0.16)}`,
          },
        },
      },
    },
  })
}

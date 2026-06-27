import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import {
  AppBar,
  Avatar,
  Box,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import DashboardIcon from '@mui/icons-material/Dashboard'
import InsightsIcon from '@mui/icons-material/Insights'
import QueueIcon from '@mui/icons-material/Rule'
import AnalyticsIcon from '@mui/icons-material/QueryStats'
import DescriptionIcon from '@mui/icons-material/Description'
import DarkModeIcon from '@mui/icons-material/DarkMode'
import LightModeIcon from '@mui/icons-material/LightMode'
import MenuIcon from '@mui/icons-material/Menu'
import ShieldIcon from '@mui/icons-material/Shield'

import { useThemeMode } from '../context/ThemeModeContext'

const navItems = [
  { to: '/', label: 'Dashboard', icon: <DashboardIcon fontSize="small" /> },
  { to: '/analysis', label: 'Content Analysis', icon: <InsightsIcon fontSize="small" /> },
  { to: '/queue', label: 'Moderator Queue', icon: <QueueIcon fontSize="small" /> },
  { to: '/analytics', label: 'Analytics', icon: <AnalyticsIcon fontSize="small" /> },
  { to: '/explanations', label: 'Explanations', icon: <DescriptionIcon fontSize="small" /> },
]

export function AppShell({ children }: { children: React.ReactNode }) {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const { mode, toggleMode } = useThemeMode()
  const [mobileOpen, setMobileOpen] = useState(false)

  const drawer = (
    <Box sx={{ width: 280, p: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, px: 1, py: 1 }}>
        <Avatar sx={{ bgcolor: 'primary.main', width: 44, height: 44 }}>
          <ShieldIcon />
        </Avatar>
        <Box>
          <Typography variant="h6">MultiShield AI</Typography>
          <Typography variant="body2" color="text.secondary">
            Moderation dashboard
          </Typography>
        </Box>
      </Box>
      <Divider />
      <List sx={{ display: 'grid', gap: 0.75 }}>
        {navItems.map((item) => (
          <ListItemButton
            key={item.to}
            component={NavLink}
            to={item.to}
            onClick={() => setMobileOpen(false)}
            sx={{
              borderRadius: 3,
              '&.active': {
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                '& .MuiListItemIcon-root': { color: 'inherit' },
              },
            }}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
      <Box sx={{ mt: 'auto', p: 1.5, borderRadius: 3, bgcolor: 'background.default' }}>
        <Typography variant="subtitle2">Current mode</Typography>
        <Typography variant="body2" color="text.secondary">
          {mode === 'dark' ? 'Dark' : 'Light'} mode enabled
        </Typography>
      </Box>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar position="fixed" elevation={0} sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Toolbar sx={{ gap: 2 }}>
          {isMobile && (
            <IconButton color="inherit" edge="start" onClick={() => setMobileOpen((open) => !open)}>
              <MenuIcon />
            </IconButton>
          )}
          <Typography variant="h6" sx={{ flexGrow: 1, letterSpacing: -0.3 }}>
            MultiShield AI Dashboard
          </Typography>
          <IconButton color="inherit" onClick={toggleMode} aria-label="toggle color mode">
            {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
          </IconButton>
        </Toolbar>
      </AppBar>

      <Box component="nav" sx={{ width: { md: 280 }, flexShrink: { md: 0 } }}>
        {isMobile ? (
          <Drawer open={mobileOpen} onClose={() => setMobileOpen(false)}>
            {drawer}
          </Drawer>
        ) : (
          <Drawer variant="permanent" open sx={{ '& .MuiDrawer-paper': { width: 280, boxSizing: 'border-box' } }}>
            {drawer}
          </Drawer>
        )}
      </Box>

      <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, sm: 3 }, pt: { xs: 10, sm: 11 }, width: '100%' }}>
        {children}
      </Box>
    </Box>
  )
}

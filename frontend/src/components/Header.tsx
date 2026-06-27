import React from 'react'
import { AppBar, Toolbar, Typography, IconButton, Switch } from '@mui/material'
import DarkModeIcon from '@mui/icons-material/DarkMode'
import Brightness7Icon from '@mui/icons-material/Brightness7'
import { Link as RouterLink } from 'react-router-dom'

export default function Header({ darkMode, setDarkMode }: { darkMode: boolean; setDarkMode: (v: boolean) => void }) {
  return (
    <AppBar position='static'>
      <Toolbar>
        <Typography variant='h6' component={RouterLink} to='/dashboard' style={{ color: 'inherit', textDecoration: 'none', flex: 1 }}>
          MultiShield AI
        </Typography>
        <nav style={{ display: 'flex', gap: 12 }}>
          <RouterLink to='/dashboard' style={{ color: 'inherit', textDecoration: 'none' }}>Dashboard</RouterLink>
          <RouterLink to='/analysis' style={{ color: 'inherit', textDecoration: 'none' }}>Content Analysis</RouterLink>
          <RouterLink to='/queue' style={{ color: 'inherit', textDecoration: 'none' }}>Moderator Queue</RouterLink>
          <RouterLink to='/analytics' style={{ color: 'inherit', textDecoration: 'none' }}>Analytics</RouterLink>
          <RouterLink to='/explanations' style={{ color: 'inherit', textDecoration: 'none' }}>Explanations</RouterLink>
        </nav>
        <IconButton color='inherit' onClick={() => setDarkMode(!darkMode)}>
          {darkMode ? <DarkModeIcon /> : <Brightness7Icon />}
        </IconButton>
      </Toolbar>
    </AppBar>
  )
}

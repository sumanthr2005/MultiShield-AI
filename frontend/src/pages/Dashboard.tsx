import React from 'react'
import { Container, Grid, Paper, Typography } from '@mui/material'

export default function Dashboard() {
  return (
    <Container maxWidth='lg'>
      <Typography variant='h4' gutterBottom>Dashboard</Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>Overview cards (placeholder)</Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>Recent activity (placeholder)</Paper>
        </Grid>
      </Grid>
    </Container>
  )
}

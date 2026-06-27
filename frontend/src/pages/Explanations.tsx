import React from 'react'
import { Container, Typography, Paper } from '@mui/material'

export default function Explanations() {
  return (
    <Container maxWidth='lg'>
      <Typography variant='h4' gutterBottom>Explanations</Typography>
      <Paper sx={{ p: 2 }}>Explainability output and model attributions will show here.</Paper>
    </Container>
  )
}

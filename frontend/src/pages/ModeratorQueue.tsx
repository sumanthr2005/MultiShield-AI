import React from 'react'
import { Container, Typography, Paper, Button } from '@mui/material'

export default function ModeratorQueue() {
  return (
    <Container maxWidth='lg'>
      <Typography variant='h4' gutterBottom>Moderator Queue</Typography>
      <Paper sx={{ p: 2 }}>Queue UI placeholder — integrate with backend moderation records.</Paper>
      <Button sx={{ mt: 2 }} variant='contained'>Refresh</Button>
    </Container>
  )
}

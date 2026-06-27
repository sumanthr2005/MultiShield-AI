import React, { useState } from 'react'
import { Container, Typography, Box } from '@mui/material'
import UploadForm from '../components/UploadForm'
import AnalysisCard from '../components/AnalysisCard'

export default function ContentAnalysis() {
  const [result, setResult] = useState<any | null>(null)

  return (
    <Container maxWidth='md'>
      <Typography variant='h4' gutterBottom>Content Analysis</Typography>
      <UploadForm onResult={(r) => setResult(r)} />
      <Box sx={{ mt: 2 }}>{result ? <AnalysisCard result={result} /> : null}</Box>
    </Container>
  )
}

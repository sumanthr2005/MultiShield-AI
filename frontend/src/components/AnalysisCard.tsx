import React from 'react'
import { Card, CardContent, Typography, Chip, Box } from '@mui/material'

export default function AnalysisCard({ result }: { result: any }) {
  const score = result?.fusion_result?.risk_score ?? result?.text_result?.risk_score ?? 0
  const label = score >= 0.75 ? 'High' : score >= 0.4 ? 'Medium' : 'Low'
  const color = score >= 0.75 ? 'error' : score >= 0.4 ? 'warning' : 'success'

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Typography variant='h6'>Risk: {score.toFixed(2)}</Typography>
          <Chip label={label} color={color as any} />
        </Box>
        <Typography variant='body2' sx={{ mt: 1 }}>{result?.fusion_result?.explanation ?? result?.text_result?.explanation}</Typography>
      </CardContent>
    </Card>
  )
}

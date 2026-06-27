import { useState } from 'react'
import { Alert, Card, CardContent, Grid, MenuItem, Paper, Stack, TextField, Typography } from '@mui/material'

import { ExplanationPanel } from '../components/ExplanationPanel'
import { useAnalysisStore } from '../context/AnalysisContext'
import { getExplainability } from '../api/client'
import type { ExplainabilityResponse } from '../api/types'

export function ExplanationsPage() {
  const { history } = useAnalysisStore()
  const [selectedId, setSelectedId] = useState(history[0]?.id ?? '')
  const selected = history.find((item) => item.id === selectedId)
  const [explanation, setExplanation] = useState<ExplainabilityResponse | null>(selected?.result.explainability_result ?? null)
  const [error, setError] = useState<string | null>(null)

  const refreshExplanation = async (id: string) => {
    const item = history.find((entry) => entry.id === id)
    if (!item?.result.fusion_result) return
    try {
      setError(null)
      setExplanation(await getExplainability(item.result.fusion_result))
    } catch (explanationError) {
      setError(explanationError instanceof Error ? explanationError.message : 'Unable to fetch explanation')
    }
  }

  return (
    <Stack spacing={3}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4">Explanations</Typography>
        <Typography color="text.secondary">Review model reasoning and next steps for moderators and auditors.</Typography>
      </Paper>

      <Grid container spacing={2}>
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Stack spacing={2}>
                <TextField
                  select
                  label="Analysis run"
                  value={selectedId}
                  onChange={(event) => {
                    const next = event.target.value
                    setSelectedId(next)
                    void refreshExplanation(next)
                  }}
                  fullWidth
                >
                  {history.map((item) => (
                    <MenuItem key={item.id} value={item.id}>
                      {item.channelLabel} · {new Date(item.createdAt).toLocaleString()}
                    </MenuItem>
                  ))}
                </TextField>
                <Typography variant="body2" color="text.secondary">
                  Select an analysis to inspect the backend explanation payload.
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} lg={8}>
          {error && <Alert severity="error">{error}</Alert>}
          {selected ? <ExplanationPanel explanation={explanation ?? selected.result.explainability_result} /> : <Alert severity="info">Run an analysis to generate explanations.</Alert>}
        </Grid>
      </Grid>
    </Stack>
  )
}

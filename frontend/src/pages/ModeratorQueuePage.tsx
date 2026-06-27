import { useState } from 'react'
import { Alert, Card, CardContent, Chip, Grid, Paper, Stack, Typography } from '@mui/material'

import { getModeration } from '../api/client'
import { ModeratorActionBar } from '../components/ModeratorActionBar'
import { RiskChip } from '../components/RiskChip'
import { useAnalysisStore } from '../context/AnalysisContext'

export function ModeratorQueuePage() {
  const { queue, updateQueueStatus, clearQueueItem } = useAnalysisStore()
  const [message, setMessage] = useState<string | null>(null)

  const handleEscalate = async (id: string) => {
    const item = queue.find((entry) => entry.id === id)
    if (!item?.result.fusion_result) return
    const moderation = await getModeration(item.result.fusion_result)
    updateQueueStatus(id, 'escalated')
    setMessage(`Escalated to moderators: ${moderation.rationale}`)
  }

  const handleApprove = (id: string) => {
    updateQueueStatus(id, 'approved')
    setMessage('Message approved and removed from the active queue.')
    clearQueueItem(id)
  }

  const handleReject = (id: string) => {
    updateQueueStatus(id, 'rejected')
    setMessage('Message rejected and removed from the active queue.')
    clearQueueItem(id)
  }

  return (
    <Stack spacing={3}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4">Moderator Queue</Typography>
        <Typography color="text.secondary">Review flagged items and decide whether to approve, reject, or escalate.</Typography>
      </Paper>

      {message && <Alert severity="info">{message}</Alert>}

      <Grid container spacing={2}>
        {queue.map((item) => {
          const risk = item.result.fusion_result?.risk_score ?? 0
          const explanation = item.result.explainability_result?.explanation ?? item.result.fusion_result?.explanation ?? 'No explanation available.'
          return (
            <Grid item xs={12} md={6} key={item.id}>
              <Card>
                <CardContent>
                  <Stack spacing={2}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="h6">{item.channelLabel}</Typography>
                      <Chip label={item.status} size="small" />
                    </Stack>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      <RiskChip risk={risk} />
                      <Chip label={`Confidence ${(item.result.fusion_result?.confidence ?? 0).toFixed(2)}`} size="small" />
                    </Stack>
                    <Typography variant="body2" color="text.secondary">
                      {explanation}
                    </Typography>
                    <ModeratorActionBar
                      onApprove={() => handleApprove(item.id)}
                      onReject={() => handleReject(item.id)}
                      onEscalate={() => void handleEscalate(item.id)}
                    />
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          )
        })}
      </Grid>

      {!queue.length && <Alert severity="success">There are no pending queue items.</Alert>}
    </Stack>
  )
}

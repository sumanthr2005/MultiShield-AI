import { Grid, Paper, Stack, Typography } from '@mui/material'

import { StatCard } from '../components/StatCard'
import { useAnalysisStore } from '../context/AnalysisContext'
import { RiskChip } from '../components/RiskChip'

export function DashboardPage() {
  const { history } = useAnalysisStore()
  const total = history.length
  const pending = history.filter((item) => item.status === 'pending').length
  const escalated = history.filter((item) => item.status === 'escalated').length
  const highRisk = history.filter((item) => (item.result.fusion_result?.risk_score ?? 0) >= 0.75).length

  return (
    <Stack spacing={3}>
      <Paper sx={{ p: 3, background: 'linear-gradient(135deg, rgba(124,231,255,0.18), rgba(255,143,171,0.10))' }}>
        <Typography variant="overline" color="text.secondary">
          MultiShield AI
        </Typography>
        <Typography variant="h4" sx={{ mb: 1 }}>
          Moderation overview
        </Typography>
        <Typography color="text.secondary">
          Monitor text and image analysis, confidence levels, and moderator actions from one place.
        </Typography>
      </Paper>

      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard label="Analyses" value={String(total)} hint="Workflow runs captured locally" accent="#7ce7ff" />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard label="Pending queue" value={String(pending)} hint="Awaiting moderator action" accent="#ffb703" />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard label="Escalated" value={String(escalated)} hint="Needs senior review" accent="#ff8fab" />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard label="High risk" value={String(highRisk)} hint="Risk score above 0.75" accent="#ef476f" />
        </Grid>
      </Grid>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Latest results
        </Typography>
        <Stack spacing={1.5}>
          {history.slice(0, 5).map((item) => (
            <Stack key={item.id} direction="row" spacing={2} alignItems="center" justifyContent="space-between">
              <Stack>
                <Typography fontWeight={700}>{item.channelLabel}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {new Date(item.createdAt).toLocaleString()}
                </Typography>
              </Stack>
              <Stack direction="row" spacing={1} alignItems="center">
                <RiskChip risk={item.result.fusion_result?.risk_score ?? 0} />
                <Typography variant="body2" color="text.secondary">
                  {(item.result.fusion_result?.confidence ?? item.result.confidence_score).toFixed(2)} confidence
                </Typography>
              </Stack>
            </Stack>
          ))}
          {!history.length && <Typography color="text.secondary">Run a content analysis to populate the dashboard.</Typography>}
        </Stack>
      </Paper>
    </Stack>
  )
}

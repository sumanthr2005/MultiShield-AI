import { useEffect, useState } from 'react'
import { Alert, Card, CardContent, Chip, CircularProgress, Grid, Paper, Stack, Typography } from '@mui/material'
import { ArcElement, BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, LineElement, PointElement, Tooltip } from 'chart.js'
import { Bar, Doughnut, Line } from 'react-chartjs-2'

import { api } from '../api/client'

ChartJS.register(ArcElement, BarElement, CategoryScale, Legend, LinearScale, LineElement, PointElement, Tooltip)

type AnalyticsSummary = {
  window_days: number
  total_analyses: number
  total_feedback: number
  active_feedback: number
  total_users: number
  total_api_keys: number
  total_retraining_jobs: number
  open_retraining_jobs: number
  decision_breakdown: Record<string, number>
  role_breakdown: Record<string, number>
  feedback_breakdown: Record<string, number>
  usage_by_route: Record<string, number>
}

const defaultSummary: AnalyticsSummary = {
  window_days: 30,
  total_analyses: 0,
  total_feedback: 0,
  active_feedback: 0,
  total_users: 0,
  total_api_keys: 0,
  total_retraining_jobs: 0,
  open_retraining_jobs: 0,
  decision_breakdown: {},
  role_breakdown: {},
  feedback_breakdown: {},
  usage_by_route: {},
}

export function AnalyticsPage() {
  const [summary, setSummary] = useState<AnalyticsSummary>(defaultSummary)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true

    async function loadSummary() {
      try {
        const { data } = await api.get<AnalyticsSummary>('/v1/analytics/summary')
        if (mounted) {
          setSummary(data)
          setError(null)
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to load analytics summary')
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }

    void loadSummary()
    return () => {
      mounted = false
    }
  }, [])

  const decisionData = {
    labels: ['Safe', 'Review', 'Block'],
    datasets: [
      {
        data: [summary.decision_breakdown.safe ?? 0, summary.decision_breakdown.review ?? 0, summary.decision_breakdown.block ?? 0],
        backgroundColor: ['#2ec4b6', '#ffb703', '#ef476f'],
      },
    ],
  }

  const feedbackData = {
    labels: ['New', 'Triaged', 'Accepted', 'Rejected'],
    datasets: [
      {
        data: [summary.feedback_breakdown.new ?? 0, summary.feedback_breakdown.triaged ?? 0, summary.feedback_breakdown.accepted ?? 0, summary.feedback_breakdown.rejected ?? 0],
        backgroundColor: ['#7ce7ff', '#8d99ae', '#2ec4b6', '#ef476f'],
      },
    ],
  }

  const routeData = {
    labels: Object.keys(summary.usage_by_route),
    datasets: [
      {
        label: 'Requests',
        data: Object.values(summary.usage_by_route),
        backgroundColor: '#7ce7ff',
      },
    ],
  }

  return (
    <Stack spacing={3}>
      <Paper sx={{ p: 3 }}>
        <Stack spacing={1}>
          <Chip label={`Last ${summary.window_days} days`} sx={{ width: 'fit-content' }} />
          <Typography variant="h4">Enterprise analytics</Typography>
          <Typography color="text.secondary">
            Track usage, feedback ingestion, moderation outcomes, identity growth, and retraining activity.
          </Typography>
        </Stack>
      </Paper>

      {error ? <Alert severity="warning">Analytics endpoint unavailable: {error}</Alert> : null}
      {loading ? <CircularProgress /> : null}

      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} lg={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary">Analyses</Typography>
              <Typography variant="h4">{summary.total_analyses}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary">Feedback</Typography>
              <Typography variant="h4">{summary.total_feedback}</Typography>
              <Typography variant="body2" color="text.secondary">
                {summary.active_feedback} actionable
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary">Users and keys</Typography>
              <Typography variant="h4">
                {summary.total_users}/{summary.total_api_keys}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                moderators, analysts, auditors, and admins
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary">Retraining</Typography>
              <Typography variant="h4">{summary.total_retraining_jobs}</Typography>
              <Typography variant="body2" color="text.secondary">
                {summary.open_retraining_jobs} open jobs
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Decision mix
              </Typography>
              <Doughnut data={decisionData} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} lg={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Feedback lifecycle
              </Typography>
              <Doughnut data={feedbackData} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Usage by route
              </Typography>
              <Bar data={routeData} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Identity and governance
              </Typography>
              <Line
                data={{
                  labels: ['Users', 'API Keys', 'Retraining Jobs'],
                  datasets: [
                    {
                      label: 'Enterprise objects',
                      data: [summary.total_users, summary.total_api_keys, summary.total_retraining_jobs],
                      borderColor: '#7ce7ff',
                      backgroundColor: 'rgba(124, 231, 255, 0.16)',
                    },
                  ],
                }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  )
}

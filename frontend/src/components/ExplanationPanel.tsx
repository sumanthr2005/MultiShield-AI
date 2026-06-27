import { Alert, Box, Card, CardContent, Chip, Stack, Typography } from '@mui/material'

import type { ExplainabilityResponse } from '../api/types'

export function ExplanationPanel({ explanation }: { explanation: ExplainabilityResponse | null }) {
  if (!explanation) {
    return <Alert severity="info">Run an analysis to populate the explanation panel.</Alert>
  }

  return (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <Box>
            <Typography variant="overline" color="text.secondary">
              Explainability
            </Typography>
            <Typography variant="h6">Why the model made this call</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            {explanation.explanation}
          </Typography>
          <Stack spacing={1}>
            {explanation.contributing_factors.map((factor) => (
              <Chip key={factor} label={factor} variant="outlined" />
            ))}
          </Stack>
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Recommended next steps
            </Typography>
            <Stack spacing={0.75}>
              {explanation.recommended_next_steps.map((step) => (
                <Typography key={step} variant="body2" color="text.secondary">
                  • {step}
                </Typography>
              ))}
            </Stack>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  )
}

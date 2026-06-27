import { alpha, Card, CardContent, Stack, Typography, useTheme } from '@mui/material'

export function StatCard({ label, value, hint, accent }: { label: string; value: string; hint: string; accent: string }) {
  const theme = useTheme()
  return (
    <Card sx={{ height: '100%', background: `linear-gradient(135deg, ${alpha(accent, 0.18)}, ${theme.palette.background.paper})` }}>
      <CardContent>
        <Stack spacing={0.5}>
          <Typography variant="overline" color="text.secondary">
            {label}
          </Typography>
          <Typography variant="h4">{value}</Typography>
          <Typography variant="body2" color="text.secondary">
            {hint}
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  )
}

import { Chip } from '@mui/material'

export function RiskChip({ risk }: { risk: number }) {
  const color = risk >= 0.75 ? 'error' : risk >= 0.45 ? 'warning' : 'success'
  const label = risk >= 0.75 ? 'High risk' : risk >= 0.45 ? 'Review' : 'Low risk'
  return <Chip size="small" color={color} label={`${label} · ${(risk * 100).toFixed(0)}%`} />
}

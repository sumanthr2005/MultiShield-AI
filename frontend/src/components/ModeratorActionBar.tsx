import { Button, Stack } from '@mui/material'

export function ModeratorActionBar({
  onApprove,
  onReject,
  onEscalate,
}: {
  onApprove: () => void
  onReject: () => void
  onEscalate: () => void
}) {
  return (
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
      <Button variant="contained" color="success" onClick={onApprove}>
        Approve
      </Button>
      <Button variant="outlined" color="error" onClick={onReject}>
        Reject
      </Button>
      <Button variant="outlined" color="warning" onClick={onEscalate}>
        Escalate
      </Button>
    </Stack>
  )
}

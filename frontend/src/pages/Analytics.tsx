import React from 'react'
import { Container, Typography, Paper } from '@mui/material'
import { Bar } from 'react-chartjs-2'
import { Chart, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'

Chart.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const sampleData = {
  labels: ['Low', 'Medium', 'High'],
  datasets: [{ label: 'Detections', data: [120, 45, 12], backgroundColor: ['#4caf50', '#ff9800', '#f44336'] }]
}

export default function Analytics() {
  return (
    <Container maxWidth='lg'>
      <Typography variant='h4' gutterBottom>Analytics</Typography>
      <Paper sx={{ p: 2 }}>
        <Bar data={sampleData} />
      </Paper>
    </Container>
  )
}

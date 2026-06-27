import { useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  Grid,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material'

import { runWorkflow, type AnalysisRequest, type WorkflowResponse } from '../api/client'
import { ImageHeatmap } from '../components/ImageHeatmap'
import { ExplanationPanel } from '../components/ExplanationPanel'
import { RiskChip } from '../components/RiskChip'
import { ToxicTextHighlighter } from '../components/ToxicTextHighlighter'
import { useAnalysisStore } from '../context/AnalysisContext'
import { getExplainability } from '../api/client'
import type { ExplainabilityResponse } from '../api/types'

const channelOptions = [
  { label: 'Dashboard', value: 'dashboard' },
  { label: 'Discord text', value: 'discord-text' },
  { label: 'Discord image', value: 'discord-image' },
]

function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(new Error('Unable to read image file'))
    reader.readAsDataURL(file)
  })
}

export function ContentAnalysisPage() {
  const { addAnalysis } = useAnalysisStore()
  const [text, setText] = useState('')
  const [ocrText, setOcrText] = useState('')
  const [channelType, setChannelType] = useState('dashboard')
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [imageReference, setImageReference] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [response, setResponse] = useState<WorkflowResponse | null>(null)
  const [explanation, setExplanation] = useState<ExplainabilityResponse | null>(null)

  const handleImageUpload = async (file: File | null) => {
    if (!file) return
    const dataUrl = await fileToDataUrl(file)
    setImagePreview(dataUrl)
    setImageReference(dataUrl)
  }

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    try {
      const request: AnalysisRequest = {
        text: text.trim() || undefined,
        imageReference: imageReference ?? undefined,
        ocrText: ocrText.trim() || undefined,
        metadata: {
          channelType,
          source: 'dashboard',
        },
      }
      const result = await runWorkflow(request)
      setResponse(result)
      addAnalysis(request, result)
      if (result.fusion_result) {
        const explain = await getExplainability(result.fusion_result)
        setExplanation(explain)
      }
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const risk = response?.fusion_result?.risk_score ?? 0
  const confidence = response?.fusion_result?.confidence ?? response?.confidence_score ?? 0

  return (
    <Stack spacing={3}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4">Content Analysis</Typography>
        <Typography color="text.secondary">
          Upload text or an image to run MultiShield AI and review risk, confidence, heatmaps, and toxic highlights.
        </Typography>
      </Paper>

      <Grid container spacing={2}>
        <Grid item xs={12} lg={7}>
          <Card>
            <CardContent>
              <Stack spacing={2}>
                <TextField
                  select
                  fullWidth
                  label="Source"
                  value={channelType}
                  onChange={(event) => setChannelType(event.target.value)}
                >
                  {channelOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>

                <TextField
                  label="Text input"
                  multiline
                  minRows={6}
                  value={text}
                  onChange={(event) => setText(event.target.value)}
                  placeholder="Paste the message to analyze."
                />

                <TextField
                  label="OCR text (optional)"
                  multiline
                  minRows={3}
                  value={ocrText}
                  onChange={(event) => setOcrText(event.target.value)}
                  placeholder="Use OCR text from the image if available."
                />

                <Box>
                  <Button variant="outlined" component="label">
                    Upload image
                    <input hidden type="file" accept="image/*" onChange={(event) => void handleImageUpload(event.target.files?.[0] ?? null)} />
                  </Button>
                </Box>

                {imagePreview && <ImageHeatmap src={imagePreview} risk={risk} />}

                <Button variant="contained" onClick={handleSubmit} disabled={loading}>
                  {loading ? 'Analyzing...' : 'Run analysis'}
                </Button>

                {error && <Alert severity="error">{error}</Alert>}
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={5}>
          <Stack spacing={2}>
            <Card>
              <CardContent>
                <Stack spacing={1.5}>
                  <Typography variant="h6">Results</Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap">
                    <RiskChip risk={risk} />
                    <Alert severity={risk >= 0.75 ? 'error' : risk >= 0.45 ? 'warning' : 'success'} sx={{ py: 0 }}>
                      Confidence {(confidence * 100).toFixed(0)}%
                    </Alert>
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    {response?.fusion_result?.explanation ?? 'No analysis submitted yet.'}
                  </Typography>
                  <Divider />
                  {text && <ToxicTextHighlighter text={text} />}
                </Stack>
              </CardContent>
            </Card>

            <ExplanationPanel explanation={explanation} />
          </Stack>
        </Grid>
      </Grid>
    </Stack>
  )
}

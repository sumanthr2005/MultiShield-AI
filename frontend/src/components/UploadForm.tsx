import React, { useState } from 'react'
import { Box, Button, TextField, Typography } from '@mui/material'
import { analyzeWorkflow } from '../api/client'

export default function UploadForm({ onResult }: { onResult?: (data: any) => void }) {
  const [text, setText] = useState('')
  const [imageUrl, setImageUrl] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const submit = async () => {
    setLoading(true)
    try {
      const payload: any = { metadata: {} }
      if (text) payload.text = text
      if (imageUrl) payload.image_reference = imageUrl
      const res = await analyzeWorkflow(payload)
      onResult?.(res)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{ display: 'grid', gap: 2, maxWidth: 800 }}>
      <Typography variant='subtitle1'>Paste text and/or an image URL to analyze</Typography>
      <TextField label='Text' multiline minRows={3} value={text} onChange={(e) => setText(e.target.value)} />
      <TextField label='Image URL' value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} placeholder='https://...' />
      <Box>
        <Button variant='contained' onClick={submit} disabled={loading}>Analyze</Button>
      </Box>
    </Box>
  )
}

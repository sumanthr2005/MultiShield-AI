import { Box, Chip, Typography } from '@mui/material'

import { findToxicTerms, highlightText } from '../utils/text'

export function ToxicTextHighlighter({ text }: { text: string }) {
  const toxicTerms = findToxicTerms(text)
  const segments = highlightText(text)

  return (
    <Box>
      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
        {toxicTerms.length ? toxicTerms.map((term) => <Chip key={term} label={term} size="small" color="error" variant="outlined" />) : <Chip size="small" label="No toxic terms detected" />}
      </Box>
      <Typography variant="body2" sx={{ lineHeight: 1.8 }}>
        {segments.map((segment, index) =>
          segment.type === 'mark' ? (
            <Box
              component="mark"
              key={`${segment.value}-${index}`}
              sx={{ px: 0.4, borderRadius: 0.75, bgcolor: 'rgba(239, 71, 111, 0.22)', color: 'inherit' }}
            >
              {segment.value}
            </Box>
          ) : (
            <Box component="span" key={`${segment.value}-${index}`}>
              {segment.value}
            </Box>
          ),
        )}
      </Typography>
    </Box>
  )
}

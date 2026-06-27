import { Box } from '@mui/material'

function seededPoints(seed: number) {
  const points = []
  for (let index = 0; index < 4; index += 1) {
    const x = ((seed * (index + 2) * 37) % 100) + 5
    const y = ((seed * (index + 3) * 53) % 100) + 5
    points.push({ x, y })
  }
  return points
}

export function ImageHeatmap({ src, risk }: { src: string; risk: number }) {
  const seed = Math.max(1, Math.round(risk * 100))
  const points = seededPoints(seed)
  const opacity = Math.min(0.55, 0.12 + risk * 0.5)

  return (
    <Box sx={{ position: 'relative', borderRadius: 3, overflow: 'hidden', aspectRatio: '16 / 10', bgcolor: 'background.default' }}>
      <Box component="img" src={src} alt="Uploaded content" sx={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
      <Box sx={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
        {points.map((point, index) => (
          <Box
            key={`${point.x}-${point.y}-${index}`}
            sx={{
              position: 'absolute',
              left: `${point.x}%`,
              top: `${point.y}%`,
              width: 110,
              height: 110,
              transform: 'translate(-50%, -50%)',
              borderRadius: '50%',
              background: `radial-gradient(circle, rgba(239,71,111,${opacity}) 0%, rgba(239,71,111,0.16) 36%, transparent 72%)`,
              filter: 'blur(4px)',
              mixBlendMode: 'screen',
            }}
          />
        ))}
      </Box>
    </Box>
  )
}

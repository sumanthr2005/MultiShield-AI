const TOXIC_TERMS = [
  'abuse',
  'harass',
  'threat',
  'dehumanize',
  'hate',
  'slur',
  'kill',
  'attack',
  'stupid',
  'idiot',
]

export function findToxicTerms(text: string): string[] {
  const lower = text.toLowerCase()
  return TOXIC_TERMS.filter((term) => lower.includes(term))
}

export function highlightText(text: string): { type: 'text' | 'mark'; value: string }[] {
  if (!text.trim()) return [{ type: 'text', value: text }]

  const terms = TOXIC_TERMS.join('|')
  const regex = new RegExp(`(${terms})`, 'ig')
  const segments: { type: 'text' | 'mark'; value: string }[] = []
  let lastIndex = 0

  for (const match of text.matchAll(regex)) {
    const index = match.index ?? 0
    if (index > lastIndex) {
      segments.push({ type: 'text', value: text.slice(lastIndex, index) })
    }
    segments.push({ type: 'mark', value: match[0] })
    lastIndex = index + match[0].length
  }

  if (lastIndex < text.length) {
    segments.push({ type: 'text', value: text.slice(lastIndex) })
  }

  return segments.length ? segments : [{ type: 'text', value: text }]
}

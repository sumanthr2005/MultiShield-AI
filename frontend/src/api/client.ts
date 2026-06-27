import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  timeout: 30000,
})

export type WorkflowRequest = {
  text?: string
  image_reference?: string
  metadata?: Record<string, any>
}

export async function analyzeWorkflow(payload: WorkflowRequest) {
  const res = await api.post('/v1/workflow/analyze', payload)
  return res.data
}

export default api
import axios from 'axios'

import type { AnalysisRequest, ExplainabilityResponse, ModerationResponse, WorkflowResponse } from './types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  timeout: 60000,
})

export async function runWorkflow(request: AnalysisRequest): Promise<WorkflowResponse> {
  const payload: Record<string, unknown> = { metadata: request.metadata }
  if (request.text) payload.text = request.text
  if (request.imageReference) payload.image_reference = request.imageReference
  if (request.ocrText) payload.ocr_text = request.ocrText

  const { data } = await api.post<WorkflowResponse>('/v1/workflow/analyze', payload)
  return data
}

export async function getExplainability(analysisResult: unknown): Promise<ExplainabilityResponse> {
  const { data } = await api.post<ExplainabilityResponse>('/v1/explainability/explain', {
    analysis_result: analysisResult,
  })
  return data
}

export async function getModeration(analysisResult: unknown): Promise<ModerationResponse> {
  const { data } = await api.post<ModerationResponse>('/v1/moderation/moderate', {
    analysis_result: analysisResult,
  })
  return data
}

export { api }

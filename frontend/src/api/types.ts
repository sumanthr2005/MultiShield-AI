export type DecisionLabel = 'safe' | 'review' | 'block'
export type EnforcementAction = 'allow' | 'warn' | 'delete'

export interface DetectionEvidence {
  source: string
  snippet?: string | null
  score: number
}

export interface AnalysisResult {
  analysis_id: string
  agent: string
  label: string
  risk_score: number
  confidence: number
  decision: DecisionLabel
  explanation: string
  evidence: DetectionEvidence[]
  metadata: Record<string, unknown>
}

export interface ExplainabilityResponse {
  analysis_id: string
  explanation: string
  contributing_factors: string[]
  recommended_next_steps: string[]
  metadata: Record<string, unknown>
}

export interface ModerationResponse {
  analysis_id: string
  action: DecisionLabel
  rationale: string
  recommended_reviewers: string[]
  metadata: Record<string, unknown>
}

export interface WorkflowResponse {
  workflow_id: string
  route: string
  route_confidence: number
  text_result: AnalysisResult | null
  image_result: AnalysisResult | null
  fusion_result: AnalysisResult | null
  explainability_result: ExplainabilityResponse | null
  moderation_result: ModerationResponse | null
  confidence_score: number
  trace: string[]
  errors: string[]
  status: 'completed' | 'failed'
}

export interface MessageMetadata {
  guild_id: number
  channel_id: number
  message_id: number
  author_id: number
  author_name: string
  message_link: string
  attachment_urls: string[]
  attachment_names: string[]
}

export interface AnalysisRequest {
  text?: string
  imageReference?: string
  ocrText?: string
  metadata: MessageMetadata | Record<string, unknown>
}

export interface AnalysisRecord extends WorkflowResponse {
  id: string
  createdAt: string
}

export interface ModeratorQueueItem {
  id: string
  request: AnalysisRequest
  result: WorkflowResponse
  status: 'pending' | 'approved' | 'rejected' | 'escalated'
  createdAt: string
  channelLabel: string
}

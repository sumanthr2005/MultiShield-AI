import { createContext, useContext, useEffect, useState } from 'react'

import type { ReactNode } from 'react'

import type { AnalysisRequest, ModeratorQueueItem, WorkflowResponse } from '../api/types'

type AnalysisContextValue = {
  history: ModeratorQueueItem[]
  queue: ModeratorQueueItem[]
  addAnalysis: (request: AnalysisRequest, response: WorkflowResponse) => void
  updateQueueStatus: (id: string, status: ModeratorQueueItem['status']) => void
  clearQueueItem: (id: string) => void
}

const AnalysisContext = createContext<AnalysisContextValue | undefined>(undefined)

const STORAGE_KEY = 'multishield-analysis-history'

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [history, setHistory] = useState<ModeratorQueueItem[]>(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY)
    if (!stored) return []
    try {
      return JSON.parse(stored) as ModeratorQueueItem[]
    } catch {
      return []
    }
  })

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(history))
  }, [history])

  const addAnalysis = (request: AnalysisRequest, response: WorkflowResponse) => {
    const item: ModeratorQueueItem = {
      id: response.workflow_id,
      request,
      result: response,
      status: response.fusion_result?.decision === 'block' ? 'pending' : 'pending',
      createdAt: new Date().toISOString(),
      channelLabel:
        typeof request.metadata === 'object' && request.metadata !== null && 'channel_id' in request.metadata
          ? `Channel ${(request.metadata as Record<string, unknown>).channel_id as string | number}`
          : 'Content Analysis',
    }
    setHistory((current) => [item, ...current].slice(0, 100))
  }

  const updateQueueStatus = (id: string, status: ModeratorQueueItem['status']) => {
    setHistory((current) => current.map((item) => (item.id === id ? { ...item, status } : item)))
  }

  const clearQueueItem = (id: string) => {
    setHistory((current) => current.filter((item) => item.id !== id))
  }

  return (
    <AnalysisContext.Provider
      value={{
        history,
        queue: history.filter((item) => item.status === 'pending' || item.status === 'escalated'),
        addAnalysis,
        updateQueueStatus,
        clearQueueItem,
      }}
    >
      {children}
    </AnalysisContext.Provider>
  )
}

export function useAnalysisStore() {
  const value = useContext(AnalysisContext)
  if (!value) {
    throw new Error('useAnalysisStore must be used within AnalysisProvider')
  }
  return value
}

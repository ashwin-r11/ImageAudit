"use client"

import { useCallback, useEffect, useState } from "react"
import { ApiError, fetchHistory, fetchResultById } from "@/lib/image-audit-api"
import type { AnalysisResult, HistoryEntry } from "../types"

interface UseHistoryOptions {
  onSelectResult: (result: AnalysisResult) => void
}

export function useHistory({ onSelectResult }: UseHistoryOptions) {
  const [entries, setEntries] = useState<HistoryEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeId, setActiveId] = useState<number | null>(null)
  const [isFetchingResult, setIsFetchingResult] = useState(false)

  const loadHistory = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await fetchHistory()
      setEntries(data)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load history.")
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadHistory()
  }, [loadHistory])

  const selectEntry = useCallback(
    async (id: number) => {
      setIsFetchingResult(true)
      setActiveId(id)
      try {
        const result = await fetchResultById(id)
        onSelectResult(result)
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Failed to load this result.")
      } finally {
        setIsFetchingResult(false)
      }
    },
    [onSelectResult],
  )

  const prependEntry = useCallback((result: AnalysisResult) => {
    setActiveId(result.id)
    setEntries((prev) => [
      {
        id: result.id,
        quality_label: result.quality_label,
        quality_score: result.quality_score,
        created_at: new Date().toISOString(),
        thumbnail_url: result.imagePreviewUrl || "",
      },
      ...prev.filter((entry) => entry.id !== result.id),
    ])
  }, [])

  return {
    entries,
    isLoading,
    error,
    activeId,
    isFetchingResult,
    selectEntry,
    prependEntry,
    refresh: loadHistory,
  }
}

"use client"

import { memo } from "react"
import { AlertTriangle, ImageOff, Loader2 } from "lucide-react"
import type { AnalysisResult } from "./types"
import { QualityScoreRing } from "./quality-score-ring"
import { QualityBadge } from "./quality-badge"
import { IssueList } from "./issue-list"
import { ImageStatsGrid } from "./image-stats-grid"

interface ResultsPanelProps {
  result: AnalysisResult | null
  isAnalyzing: boolean
  error: string | null
}

export const ResultsPanel = memo(function ResultsPanel({ result, isAnalyzing, error }: ResultsPanelProps) {
  if (isAnalyzing) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 py-16 text-center">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        <p className="text-sm text-gray-400">Analyzing image quality...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 border border-red-500/30 bg-red-500/5 py-16 text-center">
        <AlertTriangle className="h-8 w-8 text-red-400" />
        <p className="max-w-sm text-sm text-red-400">{error}</p>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 py-16 text-center">
        <div className="flex h-12 w-12 items-center justify-center border border-gray-700 bg-black/30">
          <ImageOff className="h-5 w-5 text-gray-500" />
        </div>
        <p className="text-sm text-gray-500">Upload an image and run Analyze to see quality results</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-4 border border-gray-700 bg-black/30 p-4">
        <QualityScoreRing score={result.quality_score} label={result.quality_label} />
        <div className="flex flex-col gap-2">
          <QualityBadge label={result.quality_label} />
          {result.explanation && <p className="text-sm leading-relaxed text-gray-400">{result.explanation}</p>}
        </div>
      </div>

      <IssueList issues={result.issues} />
      <ImageStatsGrid stats={result.image_stats} />
    </div>
  )
})

export type QualityLabel = "ACCEPTABLE" | "DEGRADED" | "DEFECTIVE"

export type IssueSeverity = "low" | "medium" | "high"

export interface DetectedIssue {
  type: string
  severity: IssueSeverity
  confidence: number
}

export interface ImageStats {
  blur_score: number
  brightness_mean: number
  contrast: number
  noise_estimate: number
}

export interface AnalysisResult {
  id: number
  quality_score: number
  quality_label: QualityLabel
  issues: DetectedIssue[]
  image_stats: ImageStats
  explanation?: string
  /** Populated client-side after upload so the result panel can render the source image. */
  imagePreviewUrl?: string
}

export interface HistoryEntry {
  id: number
  quality_label: QualityLabel
  quality_score: number
  created_at: string
  thumbnail_url: string
}

export interface ApiErrorPayload {
  detail?: string
}

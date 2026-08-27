"use client"

import { useCallback, useRef, useState } from "react"
import { analyzeImage, ApiError } from "@/lib/image-audit-api"
import type { AnalysisResult } from "../types"

const ACCEPTED_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"]

export function isAcceptedImageType(file: File): boolean {
  return ACCEPTED_TYPES.includes(file.type)
}

interface UseImageAuditOptions {
  onAnalyzed?: (result: AnalysisResult) => void
}

export function useImageAudit({ onAnalyzed }: UseImageAuditOptions = {}) {
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisError, setAnalysisError] = useState<string | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const previewUrlRef = useRef<string | null>(null)

  const selectFile = useCallback((next: File) => {
    if (!isAcceptedImageType(next)) {
      setUploadError("Please upload a JPG, PNG, or WEBP image.")
      return
    }

    setUploadError(null)
    setAnalysisError(null)
    setResult(null)

    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current)
    }
    const url = URL.createObjectURL(next)
    previewUrlRef.current = url

    setFile(next)
    setPreviewUrl(url)
  }, [])

  const clearFile = useCallback(() => {
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current)
      previewUrlRef.current = null
    }
    setFile(null)
    setPreviewUrl(null)
    setUploadError(null)
    setAnalysisError(null)
    setResult(null)
  }, [])

  const analyze = useCallback(async () => {
    if (!file) return

    setIsAnalyzing(true)
    setAnalysisError(null)

    try {
      const analysis = await analyzeImage(file)
      const withPreview: AnalysisResult = { ...analysis, imagePreviewUrl: previewUrlRef.current || undefined }
      setResult(withPreview)
      onAnalyzed?.(withPreview)
    } catch (err) {
      setAnalysisError(err instanceof ApiError ? err.message : "Something went wrong while analyzing this image.")
    } finally {
      setIsAnalyzing(false)
    }
  }, [file, onAnalyzed])

  const showExternalResult = useCallback((next: AnalysisResult) => {
    setAnalysisError(null)
    setUploadError(null)
    setFile(null)
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current)
      previewUrlRef.current = null
    }
    setPreviewUrl(null)
    setResult(next)
  }, [])

  return {
    file,
    previewUrl,
    uploadError,
    isAnalyzing,
    analysisError,
    result,
    selectFile,
    clearFile,
    analyze,
    showExternalResult,
  }
}

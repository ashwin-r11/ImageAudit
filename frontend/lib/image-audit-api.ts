import type { AnalysisResult, ApiErrorPayload, HistoryEntry } from "@/components/image-audit/types"

export const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/+$/, "")

export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

async function readErrorMessage(res: Response): Promise<string> {
  try {
    const payload = (await res.json()) as ApiErrorPayload
    if (payload?.detail) return payload.detail
  } catch {
    // response body wasn't JSON — fall through to a generic message
  }
  return `Request failed with status ${res.status}`
}

export async function analyzeImage(file: File): Promise<AnalysisResult> {
  const formData = new FormData()
  formData.append("file", file)

  const res = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    body: formData,
  })

  if (!res.ok) {
    throw new ApiError(await readErrorMessage(res), res.status)
  }

  return (await res.json()) as AnalysisResult
}

export async function fetchHistory(): Promise<HistoryEntry[]> {
  const res = await fetch(`${API_BASE_URL}/history`)

  if (!res.ok) {
    throw new ApiError(await readErrorMessage(res), res.status)
  }

  return (await res.json()) as HistoryEntry[]
}

export async function fetchResultById(id: number): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE_URL}/results/${id}`)

  if (!res.ok) {
    throw new ApiError(await readErrorMessage(res), res.status)
  }

  return (await res.json()) as AnalysisResult
}

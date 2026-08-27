"use client"

import { memo } from "react"
import { AlertTriangle, Clock, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import type { HistoryEntry } from "./types"
import { QUALITY_LABEL_META } from "./status-colors"

interface HistoryListProps {
  entries: HistoryEntry[]
  isLoading: boolean
  error: string | null
  activeId?: number | null
  onSelect: (id: number) => void
}

function formatTimestamp(iso: string): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  })
}

export const HistoryList = memo(function HistoryList({ entries, isLoading, error, activeId, onSelect }: HistoryListProps) {
  return (
    <div className="flex h-full flex-col gap-3">
      <div className="flex items-center gap-2">
        <Clock className="h-4 w-4 text-gray-400" />
        <h2 className="text-sm font-medium text-gray-300">History</h2>
      </div>

      {isLoading ? (
        <div className="flex flex-1 items-center justify-center py-8">
          <Loader2 className="h-5 w-5 animate-spin text-gray-500" />
        </div>
      ) : error ? (
        <div className="flex flex-1 flex-col items-center justify-center gap-2 py-8 text-center">
          <AlertTriangle className="h-5 w-5 text-red-400" />
          <p className="text-xs text-red-400">{error}</p>
        </div>
      ) : entries.length === 0 ? (
        <div className="flex flex-1 items-center justify-center py-8 text-center">
          <p className="text-xs text-gray-500">No analyses yet</p>
        </div>
      ) : (
        <div className="flex flex-col gap-1.5 overflow-y-auto">
          {entries.map((entry) => {
            const meta = QUALITY_LABEL_META[entry.quality_label]
            const isActive = entry.id === activeId
            return (
              <button
                key={entry.id}
                onClick={() => onSelect(entry.id)}
                className={cn(
                  "flex items-center gap-3 border bg-black/30 px-3 py-2 text-left transition-colors hover:border-gray-500",
                  isActive ? "border-white" : "border-gray-700",
                )}
              >
                <img
                  src={entry.thumbnail_url || "/placeholder.svg"}
                  alt=""
                  className="h-10 w-10 flex-shrink-0 border border-gray-700 object-cover"
                />
                <div className="flex flex-1 flex-col gap-0.5 overflow-hidden">
                  <div className="flex items-center gap-1.5">
                    <span className={cn("h-1.5 w-1.5 flex-shrink-0 rounded-full", meta.dot)} />
                    <span className="truncate text-xs font-medium text-white">{meta.text}</span>
                    <span className="ml-auto flex-shrink-0 text-xs tabular-nums text-gray-500">
                      {Math.round(entry.quality_score)}
                    </span>
                  </div>
                  <span className="truncate text-[11px] text-gray-500">{formatTimestamp(entry.created_at)}</span>
                </div>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
})

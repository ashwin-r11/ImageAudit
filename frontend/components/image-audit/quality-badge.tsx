import { memo } from "react"
import { cn } from "@/lib/utils"
import type { QualityLabel } from "./types"
import { QUALITY_LABEL_META } from "./status-colors"

interface QualityBadgeProps {
  label: QualityLabel
  className?: string
}

export const QualityBadge = memo(function QualityBadge({ label, className }: QualityBadgeProps) {
  const meta = QUALITY_LABEL_META[label]

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 border px-2.5 py-1 text-xs font-semibold uppercase tracking-wide",
        meta.badgeBg,
        meta.badgeText,
        className,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", meta.dot)} />
      {meta.text}
    </span>
  )
})

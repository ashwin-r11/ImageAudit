"use client"

import { memo } from "react"
import type { QualityLabel } from "./types"
import { QUALITY_LABEL_META } from "./status-colors"

interface QualityScoreRingProps {
  score: number
  label: QualityLabel
  size?: number
}

export const QualityScoreRing = memo(function QualityScoreRing({ score, label, size = 112 }: QualityScoreRingProps) {
  const meta = QUALITY_LABEL_META[label]
  const strokeWidth = 8
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const clamped = Math.min(100, Math.max(0, score))
  const offset = circumference - (clamped / 100) * circumference

  return (
    <div className="relative flex-shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth={strokeWidth} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={meta.ring}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-[stroke-dashoffset] duration-700 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-white leading-none">{Math.round(clamped)}</span>
        <span className="text-[10px] uppercase tracking-wide text-gray-500">/ 100</span>
      </div>
    </div>
  )
})

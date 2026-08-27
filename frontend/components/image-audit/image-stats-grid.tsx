import { memo } from "react"
import type { ImageStats } from "./types"

interface ImageStatsGridProps {
  stats: ImageStats
}

export const ImageStatsGrid = memo(function ImageStatsGrid({ stats }: ImageStatsGridProps) {
  const rows: Array<{ label: string; value: string }> = [
    { label: "Sharpness", value: stats.blur_score.toFixed(1) },
    { label: "Brightness", value: stats.brightness_mean.toFixed(1) },
    { label: "Contrast", value: stats.contrast.toFixed(1) },
    { label: "Noise Level", value: stats.noise_estimate.toFixed(1) },
  ]

  return (
    <div className="flex flex-col gap-2">
      <h2 className="text-sm font-medium text-gray-300">Image Stats</h2>
      <div className="grid grid-cols-2 gap-1.5 sm:grid-cols-4">
        {rows.map((row) => (
          <div key={row.label} className="border border-gray-700 bg-black/30 px-3 py-2.5">
            <p className="text-[10px] uppercase tracking-wide text-gray-500">{row.label}</p>
            <p className="text-base font-semibold text-white tabular-nums">{row.value}</p>
          </div>
        ))}
      </div>
    </div>
  )
})

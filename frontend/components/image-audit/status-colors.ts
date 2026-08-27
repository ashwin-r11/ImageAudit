import type { IssueSeverity, QualityLabel } from "./types"

export const QUALITY_LABEL_META: Record<
  QualityLabel,
  { text: string; ring: string; badgeBg: string; badgeText: string; dot: string }
> = {
  ACCEPTABLE: {
    text: "Acceptable",
    ring: "#34d399",
    badgeBg: "bg-emerald-500/15 border-emerald-500/40",
    badgeText: "text-emerald-400",
    dot: "bg-emerald-400",
  },
  DEGRADED: {
    text: "Degraded",
    ring: "#fbbf24",
    badgeBg: "bg-amber-500/15 border-amber-500/40",
    badgeText: "text-amber-400",
    dot: "bg-amber-400",
  },
  DEFECTIVE: {
    text: "Defective",
    ring: "#f87171",
    badgeBg: "bg-red-500/15 border-red-500/40",
    badgeText: "text-red-400",
    dot: "bg-red-400",
  },
}

export const SEVERITY_META: Record<IssueSeverity, { text: string; badgeBg: string; badgeText: string }> = {
  low: { text: "Low", badgeBg: "bg-emerald-500/15 border-emerald-500/40", badgeText: "text-emerald-400" },
  medium: { text: "Medium", badgeBg: "bg-amber-500/15 border-amber-500/40", badgeText: "text-amber-400" },
  high: { text: "High", badgeBg: "bg-red-500/15 border-red-500/40", badgeText: "text-red-400" },
}

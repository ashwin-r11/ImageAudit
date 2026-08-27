import { memo } from "react"
import { cn } from "@/lib/utils"
import type { DetectedIssue } from "./types"
import { SEVERITY_META } from "./status-colors"

interface IssueListProps {
  issues: DetectedIssue[]
}

function formatIssueType(type: string): string {
  return type.charAt(0).toUpperCase() + type.slice(1).replace(/_/g, " ")
}

export const IssueList = memo(function IssueList({ issues }: IssueListProps) {
  return (
    <div className="flex flex-col gap-2">
      <h2 className="text-sm font-medium text-gray-300">Detected Issues</h2>

      {issues.length === 0 ? (
        <div className="border border-gray-700 bg-black/30 px-3 py-4 text-center text-xs text-gray-500">
          No issues detected
        </div>
      ) : (
        <div className="flex flex-col gap-1.5">
          {issues.map((issue, index) => {
            const severity = SEVERITY_META[issue.severity]
            return (
              <div
                key={`${issue.type}-${index}`}
                className="flex items-center justify-between gap-3 border border-gray-700 bg-black/30 px-3 py-2.5"
              >
                <span className="text-sm text-white">{formatIssueType(issue.type)}</span>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span
                    className={cn(
                      "border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide",
                      severity.badgeBg,
                      severity.badgeText,
                    )}
                  >
                    {severity.text}
                  </span>
                  <span className="text-xs text-gray-500 tabular-nums">{Math.round(issue.confidence * 100)}%</span>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
})

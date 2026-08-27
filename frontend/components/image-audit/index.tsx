"use client"

import { useCallback } from "react"
import { ScanEye } from "lucide-react"
import { InputPanel } from "./input-panel"
import { ResultsPanel } from "./results-panel"
import { HistoryList } from "./history-list"
import { AsciiBackground } from "./ascii-background"
import { useImageAudit } from "./hooks/use-image-audit"
import { useHistory } from "./hooks/use-history"
import type { AnalysisResult } from "./types"

export function ImageAudit() {
  const history = useHistory({
    onSelectResult: (result: AnalysisResult) => audit.showExternalResult(result),
  })

  const handleAnalyzed = useCallback(
    (result: AnalysisResult) => {
      history.prependEntry(result)
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  )

  const audit = useImageAudit({ onAnalyzed: handleAnalyzed })

  return (
    <div className="relative flex min-h-screen flex-col bg-black">
      <AsciiBackground />

      <header className="relative z-10 flex items-center gap-2 border-b border-gray-800 bg-black/70 px-6 py-4 backdrop-blur-sm">
        <div className="flex h-8 w-8 items-center justify-center border border-gray-700 bg-black/50">
          <ScanEye className="h-4 w-4 text-white" />
        </div>
        <div className="flex flex-col">
          <h1 className="text-sm font-semibold text-white">ImageAudit</h1>
          <p className="text-xs text-gray-500">Automated image quality inspection</p>
        </div>
      </header>

      <main className="relative z-10 flex flex-1 flex-col gap-6 p-6 lg:flex-row">
        <section className="flex flex-col gap-6 lg:w-[320px] lg:flex-shrink-0">
          <div className="border border-gray-800 bg-black/70 p-4 backdrop-blur-sm">
            <InputPanel
              previewUrl={audit.previewUrl}
              fileName={audit.file?.name ?? null}
              uploadError={audit.uploadError}
              isAnalyzing={audit.isAnalyzing}
              canAnalyze={Boolean(audit.file)}
              onSelectFile={audit.selectFile}
              onClear={audit.clearFile}
              onAnalyze={audit.analyze}
            />
          </div>

          <div className="flex-1 border border-gray-800 bg-black/70 p-4 backdrop-blur-sm">
            <HistoryList
              entries={history.entries}
              isLoading={history.isLoading}
              error={history.error}
              activeId={history.activeId}
              onSelect={history.selectEntry}
            />
          </div>
        </section>

        <section className="flex-1 border border-gray-800 bg-black/70 p-4 backdrop-blur-sm">
          <ResultsPanel result={audit.result} isAnalyzing={audit.isAnalyzing} error={audit.analysisError} />
        </section>
      </main>
    </div>
  )
}

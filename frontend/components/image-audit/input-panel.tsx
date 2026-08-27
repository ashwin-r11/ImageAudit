"use client"

import { memo } from "react"
import { Loader2, ScanSearch } from "lucide-react"
import { Button } from "@/components/ui/button"
import { UploadDropzone } from "./upload-dropzone"

interface InputPanelProps {
  previewUrl: string | null
  fileName: string | null
  uploadError: string | null
  isAnalyzing: boolean
  canAnalyze: boolean
  onSelectFile: (file: File) => void
  onClear: () => void
  onAnalyze: () => void
}

export const InputPanel = memo(function InputPanel({
  previewUrl,
  fileName,
  uploadError,
  isAnalyzing,
  canAnalyze,
  onSelectFile,
  onClear,
  onAnalyze,
}: InputPanelProps) {
  return (
    <div className="flex flex-col gap-3">
      <UploadDropzone
        previewUrl={previewUrl}
        fileName={fileName}
        error={uploadError}
        onSelectFile={onSelectFile}
        onClear={onClear}
      />

      <Button
        onClick={onAnalyze}
        disabled={!canAnalyze || isAnalyzing}
        className="h-11 w-full gap-2 bg-white text-sm font-semibold text-black hover:bg-gray-200 disabled:opacity-40"
      >
        {isAnalyzing ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Analyzing...
          </>
        ) : (
          <>
            <ScanSearch className="h-4 w-4" />
            Analyze
          </>
        )}
      </Button>
    </div>
  )
})

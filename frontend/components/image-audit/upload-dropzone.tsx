"use client"

import type React from "react"
import { memo, useCallback, useId, useState } from "react"
import { ImageUp, X } from "lucide-react"
import { cn } from "@/lib/utils"

interface UploadDropzoneProps {
  previewUrl: string | null
  fileName: string | null
  error: string | null
  onSelectFile: (file: File) => void
  onClear: () => void
}

export const UploadDropzone = memo(function UploadDropzone({
  previewUrl,
  fileName,
  error,
  onSelectFile,
  onClear,
}: UploadDropzoneProps) {
  const inputId = useId()
  const [isDraggingOver, setIsDraggingOver] = useState(false)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDraggingOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDraggingOver(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDraggingOver(false)
      const dropped = e.dataTransfer.files[0]
      if (dropped) onSelectFile(dropped)
    },
    [onSelectFile],
  )

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selected = e.target.files?.[0]
      if (selected) onSelectFile(selected)
      e.target.value = ""
    },
    [onSelectFile],
  )

  const handleClear = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation()
      e.preventDefault()
      onClear()
    },
    [onClear],
  )

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={inputId} className="text-sm font-medium text-gray-300">
        Image
      </label>

      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={cn(
          "relative flex min-h-[180px] flex-col items-center justify-center gap-2 border bg-black/30 p-4 text-center transition-colors",
          previewUrl ? "border-white/80" : "border-gray-600 hover:border-gray-400",
          isDraggingOver && "border-white bg-white/5",
        )}
      >
        {previewUrl ? (
          <div className="relative w-full">
            <button
              onClick={handleClear}
              aria-label="Remove image"
              className="absolute -top-2 -right-2 z-10 border border-white/40 bg-black/90 p-1.5 text-white shadow-lg transition-colors hover:bg-white hover:text-black"
            >
              <X className="h-3.5 w-3.5" />
            </button>
            <img
              src={previewUrl || "/placeholder.svg"}
              alt="Selected upload preview"
              className="mx-auto max-h-40 w-full object-contain"
            />
            {fileName && <p className="mt-2 truncate text-xs text-gray-400">{fileName}</p>}
          </div>
        ) : (
          <label htmlFor={inputId} className="flex cursor-pointer flex-col items-center gap-2 py-4">
            <div className="flex h-10 w-10 items-center justify-center border border-gray-600 bg-black/50">
              <ImageUp className="h-5 w-5 text-gray-400" />
            </div>
            <p className="text-sm text-gray-300">Upload Image or drag &amp; drop</p>
            <p className="text-xs text-gray-500">JPG, PNG, or WEBP</p>
          </label>
        )}

        <input
          id={inputId}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          onChange={handleInputChange}
        />
      </div>

      {error && (
        <p role="alert" className="text-xs text-red-400">
          {error}
        </p>
      )}
    </div>
  )
})

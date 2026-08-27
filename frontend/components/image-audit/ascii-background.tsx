"use client"

import { useEffect, useRef } from "react"

const CHARS = "01.:+*#%@"
const CELL = 14

/**
 * Subtle animated ASCII noise field rendered on a fixed canvas behind the app content.
 * Pure decoration — respects prefers-reduced-motion and stays low-opacity so it never
 * competes with foreground content.
 */
export function AsciiBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches

    let width = 0
    let height = 0
    let cols = 0
    let rows = 0
    let raf = 0
    let time = 0

    function resize() {
      width = window.innerWidth
      height = window.innerHeight
      canvas.width = width * window.devicePixelRatio
      canvas.height = height * window.devicePixelRatio
      canvas.style.width = `${width}px`
      canvas.style.height = `${height}px`
      ctx.setTransform(window.devicePixelRatio, 0, 0, window.devicePixelRatio, 0, 0)
      cols = Math.ceil(width / CELL) + 1
      rows = Math.ceil(height / CELL) + 1
    }

    function draw() {
      ctx.clearRect(0, 0, width, height)
      ctx.font = `${CELL - 2}px var(--font-mono, monospace)`
      ctx.textBaseline = "top"

      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          // Layered sine noise gives a slow, organic drift instead of static flicker.
          const n =
            Math.sin(x * 0.35 + time * 0.6) * Math.cos(y * 0.4 - time * 0.4) +
            Math.sin((x + y) * 0.15 + time * 0.25)
          const normalized = (n + 2) / 4 // roughly 0..1
          const charIndex = Math.floor(normalized * CHARS.length) % CHARS.length
          const char = CHARS[charIndex]
          const alpha = 0.05 + normalized * 0.16

          ctx.fillStyle = `rgba(255, 255, 255, ${alpha.toFixed(3)})`
          ctx.fillText(char, x * CELL, y * CELL)
        }
      }
    }

    function animate() {
      time += 0.008
      draw()
      raf = requestAnimationFrame(animate)
    }

    resize()
    draw()

    window.addEventListener("resize", resize)

    if (!reduceMotion) {
      raf = requestAnimationFrame(animate)
    }

    return () => {
      window.removeEventListener("resize", resize)
      if (raf) cancelAnimationFrame(raf)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-0 h-full w-full select-none"
    />
  )
}

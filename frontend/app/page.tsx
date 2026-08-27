import type { Metadata } from "next"
import { ImageAudit } from "@/components/image-audit"

export const metadata: Metadata = {
  title: "ImageAudit",
  description: "Automated image quality inspection. Upload an image to detect blur, noise, and exposure issues.",
}

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <ImageAudit />
    </main>
  )
}

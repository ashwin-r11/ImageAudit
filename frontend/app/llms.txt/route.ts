export function GET() {
  const appUrl = process.env.NEXT_PUBLIC_APP_URL || "https://imageaudit.vercel.app"
  const content = `# ImageAudit

> ImageAudit is an automated image quality inspection tool. Upload a photo and it detects blur, noise, exposure, and other defects, returning a quality score, a pass/fail label, and a severity breakdown. Available at ${appUrl}

## About

ImageAudit is a web-based image quality auditing tool. A Next.js frontend sends uploaded images to a FastAPI backend, which analyzes sharpness, brightness, contrast, and noise, then returns a structured quality report. It is designed for anyone who needs to catch defective or degraded images before they ship, such as QA teams, marketplaces, or content pipelines.

Key facts:
- Detects blur, noise, exposure, and contrast issues in uploaded images
- Returns a 0-100 quality score with an ACCEPTABLE / DEGRADED / DEFECTIVE label
- Every analysis is saved to history for later review
- Built with Next.js on the frontend and FastAPI on the backend

## Features

- **Image Upload**: Drag and drop or browse to upload a JPG, PNG, or WEBP image
- **Quality Scoring**: A 0-100 score summarizing overall image quality
- **Quality Labels**: ACCEPTABLE, DEGRADED, or DEFECTIVE classification
- **Issue Detection**: A list of specific detected issues with severity (low/medium/high) and confidence
- **Image Stats**: Sharpness, brightness, contrast, and noise measurements for the analyzed image
- **Analysis History**: Every past analysis is saved and can be reopened from the history panel

## Use Cases

- QA review before publishing product photos on a marketplace or storefront
- Screening user-uploaded images for quality before display
- Auditing large photo batches for blur or exposure problems
- Content pipelines that need automated pre-publish quality checks

## How to Use

1. Go to ${appUrl}
2. Upload an image by dragging it into the upload area or clicking to browse
3. Click "Analyze" to run the quality inspection
4. Review the quality score, label, detected issues, and image stats
5. Browse past analyses from the history panel

## Technology Stack

- **Frontend**: Next.js 16 (App Router)
- **Backend**: FastAPI (Python) exposing /analyze, /history, and /results/:id
- **Hosting**: Vercel

## FAQ

**What image formats are supported?**
JPG, PNG, and WEBP.

**What does the quality score mean?**
A 0-100 score where higher is better. Scores map to one of three labels: ACCEPTABLE, DEGRADED, or DEFECTIVE.

**What kinds of issues does it detect?**
Issues such as blur, noise, and exposure or contrast problems, each with a severity level and confidence percentage.

**Is my analysis history saved?**
Yes. Every analyzed image appears in the history panel and can be reopened to view its full result again.

## Links

- [ImageAudit App](${appUrl}): The live application
- [v0 by Vercel](https://v0.dev): The AI-powered development platform that built this app
`

  return new Response(content, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, max-age=86400, s-maxage=86400",
    },
  })
}

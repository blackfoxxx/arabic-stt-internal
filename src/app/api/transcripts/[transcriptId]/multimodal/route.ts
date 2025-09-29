import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ transcriptId: string }> }
) {
  try {
    const { transcriptId } = await params
    const projectRoot = process.cwd()
    const resultsDir = projectRoot
    
    // Look for multimodal analysis results for this specific transcript
    const files = fs.readdirSync(resultsDir)
    const multimodalFiles = files
      .filter(file => 
        file.startsWith('multimodal_analysis_results_') && 
        file.endsWith('.json') &&
        file.includes(transcriptId.replace('transcript_', ''))
      )
      .map(file => {
        const stats = fs.statSync(path.join(resultsDir, file))
        return {
          name: file,
          path: path.join(resultsDir, file),
          mtime: stats.mtime
        }
      })
      .sort((a, b) => b.mtime.getTime() - a.mtime.getTime())

    if (multimodalFiles.length === 0) {
      // If no specific file found, try to find the latest general file
      const allMultimodalFiles = files
        .filter(file => file.startsWith('multimodal_analysis_results_') && file.endsWith('.json'))
        .map(file => {
          const stats = fs.statSync(path.join(resultsDir, file))
          return {
            name: file,
            path: path.join(resultsDir, file),
            mtime: stats.mtime
          }
        })
        .sort((a, b) => b.mtime.getTime() - a.mtime.getTime())

      if (allMultimodalFiles.length === 0) {
        return NextResponse.json(
          { error: `No multimodal analysis results found for transcript ${transcriptId}` },
          { status: 404 }
        )
      }

      // Use the latest available file
      const latestFile = allMultimodalFiles[0]
      const fileContent = fs.readFileSync(latestFile.path, 'utf-8')
      const results = JSON.parse(fileContent)

      return NextResponse.json({
        ...results,
        metadata: {
          filename: latestFile.name,
          lastModified: latestFile.mtime,
          transcriptId,
          fallbackUsed: true
        }
      })
    }

    // Read the specific file for this transcript
    const specificFile = multimodalFiles[0]
    const fileContent = fs.readFileSync(specificFile.path, 'utf-8')
    const results = JSON.parse(fileContent)

    return NextResponse.json({
      ...results,
      metadata: {
        filename: specificFile.name,
        lastModified: specificFile.mtime,
        transcriptId,
        fallbackUsed: false
      }
    })

  } catch (error) {
    console.error('Error reading multimodal results for transcript:', error)
    return NextResponse.json(
      { error: 'Failed to load multimodal analysis results' },
      { status: 500 }
    )
  }
}

export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  })
}
import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function GET(request: NextRequest) {
  try {
    const projectRoot = process.cwd()
    const resultsDir = projectRoot
    
    // Find all multimodal analysis result files
    const files = fs.readdirSync(resultsDir)
    const multimodalFiles = files
      .filter(file => file.startsWith('multimodal_analysis_results_') && file.endsWith('.json'))
      .map(file => {
        const stats = fs.statSync(path.join(resultsDir, file))
        return {
          name: file,
          path: path.join(resultsDir, file),
          mtime: stats.mtime
        }
      })
      .sort((a, b) => b.mtime.getTime() - a.mtime.getTime()) // Sort by modification time, newest first

    if (multimodalFiles.length === 0) {
      return NextResponse.json(
        { error: 'No multimodal analysis results found' },
        { status: 404 }
      )
    }

    // Read the latest file
    const latestFile = multimodalFiles[0]
    const fileContent = fs.readFileSync(latestFile.path, 'utf-8')
    const results = JSON.parse(fileContent)

    return NextResponse.json({
      ...results,
      metadata: {
        filename: latestFile.name,
        lastModified: latestFile.mtime,
        totalFiles: multimodalFiles.length
      }
    })

  } catch (error) {
    console.error('Error reading multimodal results:', error)
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
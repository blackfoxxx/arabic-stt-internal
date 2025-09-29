import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function GET(request: NextRequest) {
  try {
    const projectRoot = process.cwd()
    const resultsDir = projectRoot
    
    // Find all enhanced truth detection result files
    const files = fs.readdirSync(resultsDir)
    const truthFiles = files
      .filter(file => file.startsWith('enhanced_truth_detection_') && file.endsWith('.json'))
      .map(file => {
        const stats = fs.statSync(path.join(resultsDir, file))
        return {
          name: file,
          path: path.join(resultsDir, file),
          mtime: stats.mtime
        }
      })
      .sort((a, b) => b.mtime.getTime() - a.mtime.getTime()) // Sort by modification time, newest first

    if (truthFiles.length === 0) {
      return NextResponse.json(
        { error: 'No enhanced truth detection results found' },
        { status: 404 }
      )
    }

    // Read the latest file
    const latestFile = truthFiles[0]
    const fileContent = fs.readFileSync(latestFile.path, 'utf-8')
    const results = JSON.parse(fileContent)

    return NextResponse.json({
      ...results,
      metadata: {
        filename: latestFile.name,
        lastModified: latestFile.mtime,
        totalFiles: truthFiles.length
      }
    })

  } catch (error) {
    console.error('Error reading enhanced truth results:', error)
    return NextResponse.json(
      { error: 'Failed to load enhanced truth detection results' },
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
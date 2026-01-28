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
    
    // 1. Try to fetch real transcript from GPU backend
    try {
      const backendResponse = await fetch(`http://localhost:8005/v1/transcripts/${transcriptId}`)
      if (backendResponse.ok) {
        const backendData = await backendResponse.json()
        const transcript = backendData.transcript
        
        if (transcript && transcript.segments) {
            // Map backend data to MultimodalResults structure
            const fullText = transcript.segments.map((s: any) => s.text).join(' ')
            
            // Check for audio file existence with various extensions
            const uploadsDir = path.join(process.cwd(), 'public', 'uploads');
            const extensions = ['.wav', '.mp3', '.m4a', '.mp4', '.ogg', '.flac'];
            let audioFile = `/uploads/${transcriptId}.wav`; // Default
            
            for (const ext of extensions) {
                if (fs.existsSync(path.join(uploadsDir, `${transcriptId}${ext}`))) {
                    audioFile = `/uploads/${transcriptId}${ext}`;
                    break;
                }
            }
            
            // Construct base result
            const result = {
                text_content: fullText,
                full_transcription: fullText,
                segments: transcript.segments,
                audio_file: audioFile,
                transcription_info: {
                    model_used: transcript.model_used,
                    language: transcript.language || 'ar',
                    processing_date: new Date().toISOString(),
                    total_duration: "0:00", // Need to calculate
                    total_characters: fullText.length,
                    total_words: fullText.split(/\s+/).length,
                    total_segments: transcript.segments.length
                },
                // Mock assessment data (or derive from LLM analysis if available)
                final_assessment: {
                    overall_credibility: 0.85,
                    emotional_authenticity: 0.80,
                    stress_level: 0.3,
                    deception_likelihood: 0.1,
                    cognitive_clarity: 0.9,
                    multimodal_consistency: 0.88,
                    voice_quality: 0.85,
                    narrative_coherence: 0.9,
                    confidence_score: 0.95,
                    psychological_wellness: 0.9
                },
                recommendations: [
                    "Transcript generated successfully.",
                    "Review specific segments for accuracy."
                ],
                processing_time: 10, // Mock
                analysis_timestamp: new Date().toISOString(),
                summary: {
                    overall_sentiment: "positive", // Mock or from LLM
                    sentiment_confidence: 0.9,
                    truth_likelihood: 0.85,
                    truth_confidence: 0.9,
                    voice_quality: 0.85,
                    stress_level: "low",
                    deception_likelihood: "low",
                    emotional_authenticity: 0.8,
                    multimodal_consistency: 0.85
                },
                llm_analysis: transcript.llm_analysis // Pass through LLM analysis
            }
            
            // If LLM analysis exists, inject into summary/recommendations
            if (transcript.llm_analysis) {
                if (transcript.llm_analysis.summary) {
                    result.recommendations.unshift(`Summary: ${transcript.llm_analysis.summary}`);
                }
                if (transcript.llm_analysis.keywords) {
                    result.recommendations.push(`Keywords: ${transcript.llm_analysis.keywords}`);
                }
            }
            
            return NextResponse.json(result)
        }
      }
    } catch (e) {
      console.warn('Failed to fetch from backend, falling back to files', e)
    }

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
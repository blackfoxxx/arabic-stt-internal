import { NextRequest, NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import { join } from 'path';
import { existsSync } from 'fs';

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ filename: string }> }
) {
  try {
    const params = await context.params;
    const filename = params.filename;

    console.log('🎵 Serving audio file:', filename);

    // List of possible audio file locations
    const possiblePaths = [
      join(process.cwd(), 'public', filename),
      join(process.cwd(), 'public', 'transcripts', filename),
      join(process.cwd(), 'uploads', filename),
      join(process.cwd(), filename),
      join(process.cwd(), 'data', filename)
    ];

    let audioPath = null;
    let audioBuffer = null;

    // Try to find the audio file in various locations
    for (const path of possiblePaths) {
      if (existsSync(path)) {
        console.log('✅ Found audio file at:', path);
        audioPath = path;
        try {
          audioBuffer = await readFile(path);
          break;
        } catch (error) {
          console.error('❌ Error reading file at', path, ':', error);
          continue;
        }
      }
    }

    // If no file found, create a demo audio response or return 404
    if (!audioBuffer) {
      console.log('❌ Audio file not found:', filename);
      console.log('Searched paths:', possiblePaths);
      
      // Return a 404 response
      return new NextResponse('Audio file not found', { 
        status: 404,
        headers: {
          'Content-Type': 'text/plain',
        }
      });
    }

    // Determine content type based on file extension
    const getContentType = (filename: string) => {
      const ext = filename.toLowerCase().split('.').pop();
      switch (ext) {
        case 'mp3':
          return 'audio/mpeg';
        case 'wav':
          return 'audio/wav';
        case 'm4a':
          return 'audio/mp4';
        case 'ogg':
          return 'audio/ogg';
        case 'flac':
          return 'audio/flac';
        default:
          return 'audio/mpeg';
      }
    };

    const contentType = getContentType(filename);

    console.log('✅ Serving audio file:', {
      filename,
      path: audioPath,
      size: audioBuffer.length,
      contentType
    });

    // Return the audio file with appropriate headers
    return new NextResponse(audioBuffer, {
      status: 200,
      headers: {
        'Content-Type': contentType,
        'Content-Length': audioBuffer.length.toString(),
        'Accept-Ranges': 'bytes',
        'Cache-Control': 'public, max-age=3600',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Range',
      },
    });

  } catch (error) {
    console.error('❌ Error serving audio file:', error);
    return new NextResponse('Internal server error', { 
      status: 500,
      headers: {
        'Content-Type': 'text/plain',
      }
    });
  }
}
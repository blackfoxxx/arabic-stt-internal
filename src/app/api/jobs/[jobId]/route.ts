import { NextRequest, NextResponse } from 'next/server';

interface TranscriptSegment {
  id: string;
  start: number;
  end: number;
  text: string;
  confidence: number;
  speaker_id?: string;
}

interface Speaker {
  id: string;
  name: string;
  segments: number;
}

interface ProcessingInfo {
  model_used: string;
  processing_time: number;
  quality_metrics: Record<string, number>;
}

interface JobResult {
  transcript_id?: string;
  segments?: TranscriptSegment[];
  speakers?: Speaker[];
  processing_info?: ProcessingInfo;
  segments_count?: number;
  speakers_count?: number;
  confidence_score?: number;
  processing_time?: number;
  realtime_factor?: number;
  language_detected?: string;
  model_used?: string;
  audio_duration?: number;
  quality_metrics?: Record<string, unknown>;
  ai_features_used?: string[];
}

interface JobStatus {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message?: string;
  current_step?: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  result?: JobResult;
  created_at?: string;
}

// In-memory job storage for demo (in production this would be in Redis/Database)
const jobs: Map<string, JobStatus> = new Map();

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ jobId: string }> }
) {
  try {
    const params = await context.params;
    const jobId = params.jobId;

    if (!jobId) {
      return NextResponse.json(
        { 
          error: 'validation_error',
          message: 'معرف المهمة مطلوب' 
        },
        { status: 400 }
      );
    }

    // Check if job exists in our demo storage
    let job = jobs.get(jobId);
    
    if (!job) {
      // Create a demo job if it doesn't exist
      job = {
        id: jobId,
        status: 'processing',
        progress: Math.floor(Math.random() * 100),
        message: 'معالجة الملف الصوتي...',
        current_step: 'speech_recognition',
        created_at: new Date().toISOString(),
        started_at: new Date().toISOString()
      };
      
      // Simulate realistic AI processing progression
      const createdTime = Date.now();
      const elapsedTime = Date.now() - createdTime;
      
      if (elapsedTime < 5000) { // First 5 seconds
        job.progress = 10;
        job.message = 'معالجة وتحسين جودة الصوت';
        job.current_step = 'audio_preprocessing';
      } else if (elapsedTime < 15000) { // 5-15 seconds
        job.progress = 30;
        job.message = 'تحويل الكلام إلى نص باستخدام الذكاء الاصطناعي';
        job.current_step = 'speech_recognition';
      } else if (elapsedTime < 25000) { // 15-25 seconds
        job.progress = 60;
        job.message = 'تحديد وفصل المتحدثين';
        job.current_step = 'speaker_diarization';
      } else if (elapsedTime < 30000) { // 25-30 seconds
        job.progress = 80;
        job.message = 'معالجة النص العربي وتحسين الجودة';
        job.current_step = 'text_postprocessing';
      } else if (elapsedTime < 35000) { // 30-35 seconds
        job.progress = 90;
        job.message = 'حفظ النتائج في قاعدة البيانات';
        job.current_step = 'database_storage';
      } else { // After 35 seconds
        job.status = 'completed';
        job.progress = 100;
        job.message = 'اكتملت المعالجة بنجاح';
        job.current_step = 'completed';
        job.completed_at = new Date().toISOString();
        
        // Add realistic AI processing results
        job.result = {
          transcript_id: `transcript_${jobId}`,
          segments_count: 8,
          speakers_count: 2,
          confidence_score: 0.92,
          processing_time: 34.5,
          realtime_factor: 0.76,
          language_detected: 'ar',
          model_used: 'large-v3',
          audio_duration: 45.2,
          quality_metrics: {
            audio_quality: 0.87,
            enhancement_applied: 'medium',
            dialect_detected: 'iraqi',
            accuracy_estimate: '94%'
          },
          ai_features_used: [
            'faster-whisper ASR',
            'pyannote.audio diarization',
            'Arabic text normalization',
            'Quality assessment'
          ]
        };
      }
      
      jobs.set(jobId, job);
    }

    // In production, this would query the database/Redis:
    /*
    const backendResponse = await fetch(`${process.env.API_URL}/v1/jobs/${jobId}`, {
      method: 'GET',
      headers: {
        'Authorization': request.headers.get('Authorization'),
      },
    });

    if (backendResponse.ok) {
      const data = await backendResponse.json();
      return NextResponse.json(data);
    } else {
      const errorData = await backendResponse.json();
      return NextResponse.json(errorData, { status: backendResponse.status });
    }
    */

    return NextResponse.json({
      success: true,
      job: job,
      ai_processing_info: {
        pipeline_stage: job.current_step,
        estimated_completion: job.status === 'completed' ? 'completed' : '2-3 minutes',
        ai_models_active: job.status === 'processing',
        current_ai_operation: job.message
      }
    });

  } catch (error) {
    console.error('Job status API error:', error);
    return NextResponse.json(
      { 
        error: 'server_error',
        message: 'حدث خطأ في استرجاع حالة المهمة' 
      },
      { status: 500 }
    );
  }
}
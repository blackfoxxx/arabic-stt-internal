"use client";

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { demoAIProcessor } from '@/lib/demo-ai-processor';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface TranscriptSegment {
  id: string;
  start: number;
  end: number;
  text: string;
  confidence: number;
  speaker_id?: string;
  speaker_name?: string;
  words?: Array<{
    word: string;
    start: number;
    end: number;
    confidence: number;
  }>;
}

interface Speaker {
  id: string;
  label: string;
  display_name: string;
  total_speaking_time: number;
  segments_count: number;
  confidence_score: number;
}

interface TranscriptData {
  id: string;
  status: string;
  language: string;
  model_used: string;
  confidence_score: number;
  processing_time: number;
  segments: TranscriptSegment[];
  speakers: Speaker[];
  ai_processing_info: {
    realtime_factor: number;
    quality_metrics: any;
    features_used: string[];
  };
}

export default function TranscriptPage() {
  const params = useParams();
  const router = useRouter();
  const transcriptId = params.transcriptId as string;
  
  const [transcript, setTranscript] = useState<TranscriptData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedSegment, setSelectedSegment] = useState<string | null>(null);

  useEffect(() => {
    loadTranscript();
  }, [transcriptId]);

  const loadTranscript = async () => {
    try {
      // Try to get results from demo AI processor first
      const allJobs = demoAIProcessor.getAllJobs();
      const jobWithTranscript = allJobs.find(job => 
        job.result?.transcript_id === transcriptId || 
        job.id.includes(transcriptId.split('_')[0])
      );

      if (jobWithTranscript && jobWithTranscript.result) {
        // Use actual AI processing results
        const result = jobWithTranscript.result;
        
        const transcriptFromAI: TranscriptData = {
          id: transcriptId,
          status: 'completed',
          language: result.language,
          model_used: result.model_used,
          confidence_score: result.confidence_score,
          processing_time: result.processing_time,
          segments: result.segments.map(seg => ({
            id: seg.id,
            start: seg.start,
            end: seg.end,
            text: seg.text,
            confidence: seg.confidence,
            speaker_id: seg.speaker_id,
            speaker_name: seg.speaker_name
          })),
          speakers: result.speakers.map(speaker => ({
            ...speaker,
            segments_count: speaker.segments_count || 0
          })),
          ai_processing_info: {
            realtime_factor: result.processing_time / 60, // Estimate
            quality_metrics: result.quality_metrics,
            features_used: result.ai_features_used
          }
        };

        setTranscript(transcriptFromAI);
        setIsLoading(false);
        return;
      }

      // Fallback to mock data if no AI results available
      setTimeout(() => {
        const mockTranscript: TranscriptData = {
          id: transcriptId,
          status: 'completed',
          language: 'ar',
          model_used: 'large-v3',
          confidence_score: 0.92,
          processing_time: 34.5,
          segments: [
            {
              id: 'seg_1',
              start: 0.0,
              end: 8.5,
              text: 'السلام عليكم ومرحباً بكم في هذا الاجتماع المهم',
              confidence: 0.94,
              speaker_id: 'SPEAKER_00',
              speaker_name: 'المتحدث الأول',
              words: [
                { word: 'السلام', start: 0.0, end: 0.8, confidence: 0.95 },
                { word: 'عليكم', start: 0.8, end: 1.5, confidence: 0.93 },
                { word: 'ومرحباً', start: 1.5, end: 2.3, confidence: 0.92 },
                { word: 'بكم', start: 2.3, end: 2.8, confidence: 0.96 }
              ]
            },
            {
              id: 'seg_2',
              start: 9.0,
              end: 15.5,
              text: 'اليوم سنناقش خطة العمل الجديدة لمشروع التقنية المتقدمة',
              confidence: 0.91,
              speaker_id: 'SPEAKER_01',
              speaker_name: 'المتحدث الثاني',
              words: [
                { word: 'اليوم', start: 9.0, end: 9.5, confidence: 0.94 },
                { word: 'سنناقش', start: 9.5, end: 10.2, confidence: 0.89 },
                { word: 'خطة', start: 10.2, end: 10.7, confidence: 0.92 }
              ]
            },
            {
              id: 'seg_3',
              start: 16.0,
              end: 22.8,
              text: 'شكراً لك على هذا العرض المفصل، لدي بعض الملاحظات المهمة',
              confidence: 0.88,
              speaker_id: 'SPEAKER_00',
              speaker_name: 'المتحدث الأول',
              words: [
                { word: 'شكراً', start: 16.0, end: 16.6, confidence: 0.95 },
                { word: 'لك', start: 16.6, end: 16.9, confidence: 0.97 },
                { word: 'على', start: 16.9, end: 17.2, confidence: 0.94 }
              ]
            }
          ],
          speakers: [
            {
              id: 'SPEAKER_00',
              label: 'SPEAKER_00',
              display_name: 'المتحدث الأول',
              total_speaking_time: 15.3,
              segments_count: 2,
              confidence_score: 0.91
            },
            {
              id: 'SPEAKER_01',
              label: 'SPEAKER_01', 
              display_name: 'المتحدث الثاني',
              total_speaking_time: 6.5,
              segments_count: 1,
              confidence_score: 0.91
            }
          ],
          ai_processing_info: {
            realtime_factor: 0.76,
            quality_metrics: {
              audio_quality: 0.87,
              enhancement_applied: 'medium',
              dialect_detected: 'العربية الفصحى',
              accuracy_estimate: '94%'
            },
            features_used: [
              'faster-whisper ASR',
              'pyannote.audio diarization',
              'Arabic text normalization',
              'Quality assessment'
            ]
          }
        };

        setTranscript(mockTranscript);
        setIsLoading(false);
      }, 1000);

    } catch (error) {
      console.error('Failed to load transcript:', error);
      setIsLoading(false);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.9) return 'bg-green-100 text-green-800';
    if (confidence >= 0.8) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getSpeakerColor = (speakerId: string): string => {
    const colors = {
      'SPEAKER_00': 'bg-blue-100 text-blue-800 border-r-4 border-blue-400',
      'SPEAKER_01': 'bg-green-100 text-green-800 border-r-4 border-green-400',
      'SPEAKER_02': 'bg-purple-100 text-purple-800 border-r-4 border-purple-400',
    };
    return colors[speakerId as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const exportTranscript = (format: string) => {
    if (!transcript) return;
    
    // Generate export data based on format
    let exportData = '';
    
    switch (format) {
      case 'txt':
        exportData = transcript.segments.map(seg => 
          `${seg.speaker_name || 'متحدث'}: ${seg.text}`
        ).join('\n\n');
        break;
      
      case 'srt':
        exportData = transcript.segments.map((seg, index) => {
          const startTime = formatSRT(seg.start);
          const endTime = formatSRT(seg.end);
          return `${index + 1}\n${startTime} --> ${endTime}\n${seg.text}\n`;
        }).join('\n');
        break;
      
      case 'vtt':
        exportData = 'WEBVTT\n\n' + transcript.segments.map(seg => {
          const startTime = formatSRT(seg.start);
          const endTime = formatSRT(seg.end);
          return `${startTime} --> ${endTime}\n${seg.text}\n`;
        }).join('\n');
        break;
    }

    // Download file
    const blob = new Blob([exportData], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcript_${transcriptId}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatSRT = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 1000);
    return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')},${ms.toString().padStart(3, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">جاري تحميل النسخة النصية...</p>
        </div>
      </div>
    );
  }

  if (!transcript) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-red-800">خطأ في التحميل</CardTitle>
            <CardDescription>لم يتم العثور على النسخة النصية</CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Button onClick={() => router.push('/dashboard')}>
              العودة إلى لوحة التحكم
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">عارض النسخة النصية</h1>
              <p className="text-sm text-gray-600">معرف النسخة: {transcriptId}</p>
            </div>
            
            <div className="flex items-center gap-4">
              <Badge className="bg-green-100 text-green-800">
                مكتمل بالذكاء الاصطناعي
              </Badge>
              <Button variant="outline" onClick={() => router.push('/dashboard')}>
                العودة إلى لوحة التحكم
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* AI Processing Results Summary */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>نتائج المعالجة بالذكاء الاصطناعي</CardTitle>
            <CardDescription>
              معلومات شاملة عن عملية التفريغ والمعالجة
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600 mb-1">
                  {Math.round(transcript.confidence_score * 100)}%
                </div>
                <div className="text-sm text-gray-600">دقة التفريغ</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 mb-1">
                  {transcript.segments.length}
                </div>
                <div className="text-sm text-gray-600">مقطع نصي</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600 mb-1">
                  {transcript.speakers.length}
                </div>
                <div className="text-sm text-gray-600">متحدث</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600 mb-1">
                  {Math.round(transcript.processing_time)}s
                </div>
                <div className="text-sm text-gray-600">وقت المعالجة</div>
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-3">تقنيات الذكاء الاصطناعي المستخدمة</h4>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h5 className="text-sm font-medium text-blue-800 mb-2">النماذج المستخدمة:</h5>
                  <div className="space-y-1 text-xs text-blue-700">
                    {transcript.ai_processing_info.features_used.map((feature, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <span className="text-blue-500">•</span>
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h5 className="text-sm font-medium text-blue-800 mb-2">مقاييس الجودة:</h5>
                  <div className="space-y-1 text-xs text-blue-700">
                    <div>جودة الصوت: {Math.round(transcript.ai_processing_info.quality_metrics.audio_quality * 100)}%</div>
                    <div>سرعة المعالجة: {transcript.ai_processing_info.realtime_factor.toFixed(2)}x</div>
                    <div>اللهجة المكتشفة: {transcript.ai_processing_info.quality_metrics.dialect_detected}</div>
                    <div>النموذج: {transcript.model_used}</div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="transcript" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="transcript">النسخة النصية</TabsTrigger>
            <TabsTrigger value="speakers">المتحدثون</TabsTrigger>
            <TabsTrigger value="analytics">التحليلات</TabsTrigger>
            <TabsTrigger value="export">التصدير</TabsTrigger>
          </TabsList>

          {/* Transcript Tab */}
          <TabsContent value="transcript">
            <Card>
              <CardHeader>
                <CardTitle>النسخة النصية مع فصل المتحدثين</CardTitle>
                <CardDescription>
                  نص مُحسَّن بالذكاء الاصطناعي مع تحديد المتحدثين وتوقيتات دقيقة
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* Waveform Placeholder */}
                <div className="mb-6 p-6 bg-gray-100 rounded-lg text-center">
                  <div className="text-gray-500 mb-2">موجة صوتية تفاعلية</div>
                  <div className="h-20 bg-gradient-to-r from-blue-200 via-blue-300 to-blue-200 rounded flex items-center justify-center">
                    <span className="text-blue-700 text-sm">
                      لعرض الموجة الصوتية، ابدأ الخدمات الخلفية
                    </span>
                  </div>
                  <div className="mt-2 text-xs text-gray-500">
                    wavesurfer.js + timeline navigation
                  </div>
                </div>

                {/* Transcript Segments */}
                <div className="space-y-4">
                  {transcript.segments.map((segment) => (
                    <div
                      key={segment.id}
                      className={`p-4 rounded-lg border-r-4 cursor-pointer transition-all ${
                        getSpeakerColor(segment.speaker_id || '')
                      } ${selectedSegment === segment.id ? 'ring-2 ring-blue-500' : ''}`}
                      onClick={() => setSelectedSegment(
                        selectedSegment === segment.id ? null : segment.id
                      )}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <Badge variant="outline" className="text-xs">
                            {formatTime(segment.start)} - {formatTime(segment.end)}
                          </Badge>
                          <Badge className={getConfidenceColor(segment.confidence)}>
                            ثقة: {Math.round(segment.confidence * 100)}%
                          </Badge>
                          {segment.speaker_name && (
                            <Badge variant="secondary">
                              {segment.speaker_name}
                            </Badge>
                          )}
                        </div>
                      </div>
                      
                      <p className="text-right leading-relaxed text-gray-900 mb-2">
                        {segment.text}
                      </p>
                      
                      {selectedSegment === segment.id && segment.words && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <h5 className="text-sm font-medium text-gray-700 mb-2">
                            الكلمات مع التوقيتات (AI Word-level Timestamps):
                          </h5>
                          <div className="flex flex-wrap gap-2">
                            {segment.words.map((word, index) => (
                              <span
                                key={index}
                                className="inline-block px-2 py-1 text-xs bg-gray-100 rounded border"
                                title={`${formatTime(word.start)} - ${formatTime(word.end)} (ثقة: ${Math.round(word.confidence * 100)}%)`}
                              >
                                {word.word}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Speakers Tab */}
          <TabsContent value="speakers">
            <Card>
              <CardHeader>
                <CardTitle>تحليل المتحدثين بالذكاء الاصطناعي</CardTitle>
                <CardDescription>
                  تم تحديد المتحدثين باستخدام pyannote.audio
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  {transcript.speakers.map((speaker) => (
                    <Card key={speaker.id} className="border">
                      <CardHeader>
                        <CardTitle className="text-lg">{speaker.display_name}</CardTitle>
                        <CardDescription>معرف: {speaker.label}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-600">وقت التحدث:</span>
                            <span className="font-medium">{formatTime(speaker.total_speaking_time)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-600">عدد المقاطع:</span>
                            <span className="font-medium">{speaker.segments_count}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-600">دقة التحديد:</span>
                            <Badge className={getConfidenceColor(speaker.confidence_score)}>
                              {Math.round(speaker.confidence_score * 100)}%
                            </Badge>
                          </div>
                          
                          {/* Speaking time visualization */}
                          <div>
                            <div className="text-sm text-gray-600 mb-1">نسبة التحدث:</div>
                            <Progress 
                              value={(speaker.total_speaking_time / transcript.segments.reduce((total, seg) => total + (seg.end - seg.start), 0)) * 100}
                            />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>إحصائيات الجودة</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>دقة التفريغ الإجمالية</span>
                        <span>{Math.round(transcript.confidence_score * 100)}%</span>
                      </div>
                      <Progress value={transcript.confidence_score * 100} />
                    </div>
                    
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>جودة الصوت الأصلي</span>
                        <span>{Math.round(transcript.ai_processing_info.quality_metrics.audio_quality * 100)}%</span>
                      </div>
                      <Progress value={transcript.ai_processing_info.quality_metrics.audio_quality * 100} />
                    </div>

                    <div className="text-sm space-y-2">
                      <div className="flex justify-between">
                        <span>النموذج المستخدم:</span>
                        <Badge>{transcript.model_used}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span>اللغة المكتشفة:</span>
                        <span>{transcript.language}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>سرعة المعالجة:</span>
                        <span>{transcript.ai_processing_info.realtime_factor.toFixed(2)}x</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>تفاصيل المعالجة</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">مراحل المعالجة المكتملة:</h4>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-green-500">✓</span>
                          <span>تحسين جودة الصوت</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-green-500">✓</span>
                          <span>تحويل الكلام إلى نص (faster-whisper)</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-green-500">✓</span>
                          <span>فصل المتحدثين (pyannote.audio)</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-green-500">✓</span>
                          <span>معالجة النص العربي</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-green-500">✓</span>
                          <span>تقييم الجودة والدقة</span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">إحصائيات النص:</h4>
                      <div className="text-sm space-y-1">
                        <div>إجمالي الكلمات: {transcript.segments.reduce((total, seg) => total + seg.text.split(' ').length, 0)}</div>
                        <div>متوسط طول المقطع: {Math.round(transcript.segments.reduce((total, seg) => total + (seg.end - seg.start), 0) / transcript.segments.length)} ثانية</div>
                        <div>أقل ثقة: {Math.round(Math.min(...transcript.segments.map(seg => seg.confidence)) * 100)}%</div>
                        <div>أعلى ثقة: {Math.round(Math.max(...transcript.segments.map(seg => seg.confidence)) * 100)}%</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Export Tab */}
          <TabsContent value="export">
            <Card>
              <CardHeader>
                <CardTitle>تصدير النسخة النصية</CardTitle>
                <CardDescription>
                  احفظ النسخة النصية بصيغ مختلفة للاستخدام في تطبيقات أخرى
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-medium text-gray-900">صيغ التصدير المتاحة</h4>
                    
                    <div className="space-y-3">
                      <Button 
                        variant="outline" 
                        className="w-full justify-start"
                        onClick={() => exportTranscript('txt')}
                      >
                        <span className="mr-3">📄</span>
                        نص عادي (.txt)
                      </Button>
                      
                      <Button 
                        variant="outline" 
                        className="w-full justify-start"
                        onClick={() => exportTranscript('srt')}
                      >
                        <span className="mr-3">🎬</span>
                        ترجمات للفيديو (.srt)
                      </Button>
                      
                      <Button 
                        variant="outline" 
                        className="w-full justify-start"
                        onClick={() => exportTranscript('vtt')}
                      >
                        <span className="mr-3">🌐</span>
                        ترجمات الويب (.vtt)
                      </Button>
                      
                      <Button 
                        variant="outline" 
                        className="w-full justify-start"
                        disabled
                      >
                        <span className="mr-3">📋</span>
                        مستند Word (.docx) - قريباً
                      </Button>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-4">معاينة التصدير</h4>
                    <div className="bg-gray-50 p-4 rounded-lg text-sm">
                      <div className="text-gray-600 mb-2">مثال - صيغة SRT:</div>
                      <pre className="text-xs text-right overflow-auto">
{`1
00:00:00,000 --> 00:00:08,500
${transcript.segments[0]?.text}

2  
00:00:09,000 --> 00:00:15,500
${transcript.segments[1]?.text}`}
                      </pre>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Demo Notice */}
        <Alert className="mt-6">
          <AlertDescription>
            <div className="text-center">
              <strong>نسخة تجريبية مع محاكاة الذكاء الاصطناعي</strong>
              <p className="mt-1 text-sm">
                هذه النتائج مُحاكاة لتوضيح قدرات المنصة. لتفعيل المعالجة الفعلية:
              </p>
              <code className="block bg-gray-100 px-3 py-2 rounded mt-2 text-xs">
                ./start-full-stack.sh
              </code>
              <p className="text-xs mt-1">
                سيؤدي هذا إلى تشغيل نماذج الذكاء الاصطناعي الفعلية (faster-whisper + pyannote.audio)
              </p>
            </div>
          </AlertDescription>
        </Alert>
      </div>
    </div>
  );
}
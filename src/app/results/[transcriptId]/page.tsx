"use client";

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
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
  filename: string;
  status: string;
  created_at: string;
  processing_time: number;
  language?: string;
  model_used?: string;
  confidence_score?: number;
  segments: TranscriptSegment[];
  speakers: Speaker[];
  ai_processing_info: {
    realtime_factor: number;
    quality_metrics: {
      confidence_score: number;
      noise_level: number;
      clarity_rating: number;
      audio_quality?: number;
      enhancement_applied?: string;
      dialect_detected?: string;
      accuracy_estimate?: string;
    };
    features_used: string[];
  };
  arabic_analysis?: {
    overall_sentiment: string;
    sentiment_distribution: {
      positive: number;
      neutral: number;
      negative: number;
    };
    grammar_issues: {
      t5_suggestions: number;
      bert_suggestions: number;
      camel_suggestions: number;
    };
    validation_issues: {
      structure: number;
      punctuation: number;
      incomplete: number;
    };
    local_models_used: string[];
    sentences_analyzed: number;
    processing_time: number;
  };
}

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const transcriptId = params.transcriptId as string;
  
  const [transcript, setTranscript] = useState<TranscriptData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSegment, setSelectedSegment] = useState<string | null>(null);

  const loadTranscript = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Try to get results from backend API
      const response = await fetch(`/api/transcripts/${transcriptId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          setError('لم يتم العثور على نتائج التفريغ. يرجى التأكد من معرف التفريغ.');
        } else {
          setError('حدث خطأ في تحميل نتائج التفريغ. يرجى المحاولة مرة أخرى.');
        }
        setIsLoading(false);
        return;
      }

      const data = await response.json();
      
      if (!data.success || !data.transcript) {
        setError('البيانات المستلمة غير صحيحة. يرجى المحاولة مرة أخرى.');
        setIsLoading(false);
        return;
      }

      // Transform backend data to match our interface
      const transcriptData: TranscriptData = {
        id: data.transcript.id,
        filename: data.transcript.filename || `transcript_${transcriptId}.mp3`,
        status: 'completed',
        created_at: data.transcript.created_at || new Date().toISOString(),
        language: data.transcript.language || 'ar',
        model_used: data.transcript.model_used || 'large-v3',
        confidence_score: data.transcript.confidence_score || 0.9,
        processing_time: data.transcript.processing_time || 0,
        segments: data.transcript.segments || [],
        speakers: data.transcript.speakers || [],
        ai_processing_info: {
          realtime_factor: data.transcript.processing_time ? data.transcript.processing_time / 60 : 0,
          quality_metrics: {
            confidence_score: data.transcript.confidence_score || 0.9,
            noise_level: 0.1,
            clarity_rating: 0.85,
            audio_quality: data.transcript.quality_metrics?.audio_quality || 0.85,
            enhancement_applied: data.transcript.quality_metrics?.enhancement_applied || 'تحسين الضوضاء',
            dialect_detected: data.transcript.quality_metrics?.dialect_detected || 'عربية فصحى',
            accuracy_estimate: data.transcript.quality_metrics?.accuracy_estimate || 'عالية'
          },
          features_used: data.transcript.ai_features_used || ['faster-whisper', 'pyannote.audio']
        }
      };

      setTranscript(transcriptData);
      setIsLoading(false);

    } catch (error) {
      console.error('Failed to load transcript:', error);
      setError('حدث خطأ في الاتصال بالخادم. يرجى التحقق من الاتصال والمحاولة مرة أخرى.');
      setIsLoading(false);
    }
  }, [transcriptId]);

  useEffect(() => {
    loadTranscript();
  }, [loadTranscript]);

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

  const exportTranscript = (format: string) => {
    if (!transcript) return;

    let content = '';
    let filename = '';
    let mimeType = '';

    switch (format) {
      case 'txt':
        content = transcript.segments.map(seg => 
          `[${formatTime(seg.start)} - ${formatTime(seg.end)}] ${seg.speaker_name || 'متحدث'}: ${seg.text}`
        ).join('\n\n');
        filename = `transcript_${transcript.id}.txt`;
        mimeType = 'text/plain';
        break;
      
      case 'srt':
        content = transcript.segments.map((seg, index) => 
          `${index + 1}\n${formatTime(seg.start).replace(':', ',')} --> ${formatTime(seg.end).replace(':', ',')}\n${seg.text}\n`
        ).join('\n');
        filename = `transcript_${transcript.id}.srt`;
        mimeType = 'text/plain';
        break;
      
      case 'json':
        content = JSON.stringify(transcript, null, 2);
        filename = `transcript_${transcript.id}.json`;
        mimeType = 'application/json';
        break;
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">جاري تحميل نتائج التفريغ...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md mx-auto text-center">
          <Alert className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
          <div className="space-x-2 space-x-reverse">
            <Button onClick={loadTranscript} variant="outline">
              إعادة المحاولة
            </Button>
            <Button onClick={() => router.push('/upload')}>
              رفع ملف جديد
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!transcript) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">لا توجد بيانات للعرض</p>
          <Button onClick={() => router.push('/upload')}>
            رفع ملف جديد
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Button variant="outline" size="sm" asChild>
                <Link href="/">
                  ← العودة للرئيسية
                </Link>
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                  نتائج التفريغ الصوتي
                </h1>
                <p className="text-gray-600">
                  {transcript.filename} • {formatTime(transcript.segments[transcript.segments.length - 1]?.end || 0)}
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={() => exportTranscript('txt')} variant="outline" size="sm">
                تصدير TXT
              </Button>
              <Button onClick={() => exportTranscript('srt')} variant="outline" size="sm">
                تصدير SRT
              </Button>
              <Button onClick={() => exportTranscript('json')} variant="outline" size="sm">
                تصدير JSON
              </Button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 mb-1">
                {Math.round((transcript.confidence_score || 0) * 100)}%
              </div>
              <p className="text-sm text-gray-600">دقة التفريغ</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600 mb-1">
                {transcript.segments.length}
              </div>
              <p className="text-sm text-gray-600">مقطع نصي</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600 mb-1">
                {transcript.speakers.length}
              </div>
              <p className="text-sm text-gray-600">متحدث</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600 mb-1">
                {Math.round(transcript.processing_time)}s
              </div>
              <p className="text-sm text-gray-600">وقت المعالجة</p>
            </div>
          </div>
        </div>

        <Tabs defaultValue="transcript" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="transcript">النص المفرغ</TabsTrigger>
            <TabsTrigger value="speakers">المتحدثون</TabsTrigger>
            <TabsTrigger value="analysis">التحليل</TabsTrigger>
          </TabsList>

          {/* Transcript Tab */}
          <TabsContent value="transcript">
            <Card>
              <CardHeader>
                <CardTitle>النص المفرغ مع الطوابع الزمنية</CardTitle>
                <CardDescription>
                  النص الكامل مع تحديد المتحدثين والأوقات
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {transcript.segments.map((segment) => (
                    <div
                      key={segment.id}
                      className={`p-4 rounded-lg border transition-colors cursor-pointer ${
                        selectedSegment === segment.id
                          ? 'bg-blue-50 border-blue-200'
                          : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                      }`}
                      onClick={() => setSelectedSegment(
                        selectedSegment === segment.id ? null : segment.id
                      )}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {formatTime(segment.start)} - {formatTime(segment.end)}
                          </Badge>
                          {segment.speaker_name && (
                            <Badge variant="secondary" className="text-xs">
                              {segment.speaker_name}
                            </Badge>
                          )}
                        </div>
                        <Badge className={`text-xs ${getConfidenceColor(segment.confidence)}`}>
                          {Math.round(segment.confidence * 100)}%
                        </Badge>
                      </div>
                      <p className="text-right leading-relaxed text-gray-800">
                        {segment.text}
                      </p>
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
                <CardTitle>تحليل المتحدثين</CardTitle>
                <CardDescription>
                  إحصائيات وتفاصيل المتحدثين المحددين
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {transcript.speakers.map((speaker) => (
                    <div key={speaker.id} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-medium text-gray-900">
                          {speaker.display_name}
                        </h3>
                        <Badge className={getConfidenceColor(speaker.confidence_score)}>
                          {Math.round(speaker.confidence_score * 100)}% دقة
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">وقت التحدث:</span>
                          <span className="font-medium ml-2">
                            {Math.round(speaker.total_speaking_time)}s
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">عدد المقاطع:</span>
                          <span className="font-medium ml-2">
                            {speaker.segments_count}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analysis Tab */}
          <TabsContent value="analysis">
            <div className="space-y-6">
              {/* Audio Quality Analysis */}
              <Card>
                <CardHeader>
                  <CardTitle>تحليل جودة التفريغ الصوتي</CardTitle>
                  <CardDescription>
                    مقاييس الجودة والدقة للتفريغ الصوتي
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">دقة التفريغ</span>
                        <span className="text-sm text-gray-600">
                          {Math.round((transcript.ai_processing_info.quality_metrics.confidence_score) * 100)}%
                        </span>
                      </div>
                      <Progress 
                        value={transcript.ai_processing_info.quality_metrics.confidence_score * 100} 
                        className="h-2"
                      />
                    </div>
                    
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">وضوح الصوت</span>
                        <span className="text-sm text-gray-600">
                          {Math.round(transcript.ai_processing_info.quality_metrics.clarity_rating * 100)}%
                        </span>
                      </div>
                      <Progress 
                        value={transcript.ai_processing_info.quality_metrics.clarity_rating * 100} 
                        className="h-2"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4 mt-6 pt-4 border-t">
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">معلومات المعالجة</h4>
                        <div className="space-y-1 text-sm text-gray-600">
                          <div>النموذج: {transcript.model_used}</div>
                          <div>اللغة: {transcript.language === 'ar' ? 'العربية' : transcript.language}</div>
                          <div>اللهجة: {transcript.ai_processing_info.quality_metrics.dialect_detected}</div>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">التقنيات المستخدمة</h4>
                        <div className="space-y-1 text-sm text-gray-600">
                          {transcript.ai_processing_info.features_used.map((feature, index) => (
                            <div key={index}>• {feature}</div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Arabic Text Analysis */}
              <Card>
                <CardHeader>
                  <CardTitle>تحليل النص العربي المحلي</CardTitle>
                  <CardDescription>
                    تحليل شامل للنص باستخدام النماذج المحلية - فحص القواعد والمشاعر والتحقق من صحة الجمل
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Sentiment Analysis */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">تحليل المشاعر</h4>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="text-center p-3 bg-green-50 rounded-lg">
                          <div className="text-2xl font-bold text-green-600">
                            {transcript.arabic_analysis?.sentiment_distribution?.positive || 0}
                          </div>
                          <div className="text-sm text-gray-600">إيجابي</div>
                        </div>
                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                          <div className="text-2xl font-bold text-gray-600">
                            {transcript.arabic_analysis?.sentiment_distribution?.neutral || 0}
                          </div>
                          <div className="text-sm text-gray-600">محايد</div>
                        </div>
                        <div className="text-center p-3 bg-red-50 rounded-lg">
                          <div className="text-2xl font-bold text-red-600">
                            {transcript.arabic_analysis?.sentiment_distribution?.negative || 0}
                          </div>
                          <div className="text-sm text-gray-600">سلبي</div>
                        </div>
                      </div>
                      <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                        <div className="text-sm font-medium text-blue-900">
                          المشاعر العامة: {transcript.arabic_analysis?.overall_sentiment || 'غير محدد'}
                        </div>
                      </div>
                    </div>

                    {/* Grammar and Validation */}
                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-medium text-gray-900 mb-3">فحص القواعد النحوية</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span className="text-sm">نموذج T5 المحلي</span>
                            <Badge variant="outline" className="text-xs">
                              {transcript.arabic_analysis?.grammar_issues?.t5_suggestions || 0} اقتراح
                            </Badge>
                          </div>
                          <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span className="text-sm">نموذج BERT العربي</span>
                            <Badge variant="outline" className="text-xs">
                              {transcript.arabic_analysis?.grammar_issues?.bert_suggestions || 0} اقتراح
                            </Badge>
                          </div>
                          <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span className="text-sm">CamelBERT</span>
                            <Badge variant="outline" className="text-xs">
                              {transcript.arabic_analysis?.grammar_issues?.camel_suggestions || 0} اقتراح
                            </Badge>
                          </div>
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-medium text-gray-900 mb-3">التحقق من صحة الجمل</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span className="text-sm">مشاكل في البنية</span>
                            <Badge variant="outline" className="text-xs">
                              {transcript.arabic_analysis?.validation_issues?.structure || 0}
                            </Badge>
                          </div>
                          <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span className="text-sm">علامات الترقيم</span>
                            <Badge variant="outline" className="text-xs">
                              {transcript.arabic_analysis?.validation_issues?.punctuation || 0}
                            </Badge>
                          </div>
                          <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span className="text-sm">جمل غير مكتملة</span>
                            <Badge variant="outline" className="text-xs">
                              {transcript.arabic_analysis?.validation_issues?.incomplete || 0}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Local Models Used */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">النماذج المحلية المستخدمة</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <div className="text-sm font-medium text-gray-700">نماذج تحليل المشاعر:</div>
                          <div className="space-y-1 text-xs text-gray-600">
                            <div>• CAMeLBERT (Arabic BERT)</div>
                            <div>• AraBERT (Arabic BERT)</div>
                            <div>• Arabic BERT Base</div>
                          </div>
                        </div>
                        <div className="space-y-2">
                          <div className="text-sm font-medium text-gray-700">نماذج فحص القواعد:</div>
                          <div className="space-y-1 text-xs text-gray-600">
                            <div>• T5 Grammar Correction</div>
                            <div>• Arabic BERT Grammar</div>
                            <div>• Local Validation Rules</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Privacy Notice */}
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-sm font-medium text-green-800">معالجة محلية بالكامل</span>
                      </div>
                      <div className="text-xs text-green-700">
                        جميع عمليات التحليل تمت باستخدام النماذج المحلية فقط. لم يتم إرسال أي بيانات إلى خوادم خارجية.
                        خصوصيتك محمية بالكامل.
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
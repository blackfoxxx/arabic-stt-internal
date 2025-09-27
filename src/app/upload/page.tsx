"use client";

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { demoAIProcessor, formatFileSize, estimateProcessingTime } from '@/lib/demo-ai-processor';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface UploadState {
  isDragging: boolean;
  isUploading: boolean;
  uploadProgress: number;
  file: File | null;
  jobId: string | null;
  processingStatus: any;
}

interface ProcessingOptions {
  language: string;
  model: string;
  diarization: boolean;
  enhancement_level: string;
  custom_vocabulary: string[];
}

export default function UploadPage() {
  const router = useRouter();
  const [uploadState, setUploadState] = useState<UploadState>({
    isDragging: false,
    isUploading: false,
    uploadProgress: 0,
    file: null,
    jobId: null,
    processingStatus: null
  });

  const [processingOptions, setProcessingOptions] = useState<ProcessingOptions>({
    language: 'ar',
    model: 'large-v3',
    diarization: true,
    enhancement_level: 'medium',
    custom_vocabulary: []
  });

  const [customVocab, setCustomVocab] = useState('');

  // File drop handling
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setUploadState(prev => ({ ...prev, isDragging: true }));
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setUploadState(prev => ({ ...prev, isDragging: false }));
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setUploadState(prev => ({ ...prev, isDragging: false }));
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelection(files[0]);
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log('📁 File input change event triggered');
    const files = e.target.files;
    
    if (files && files.length > 0) {
      const selectedFile = files[0];
      console.log('✅ File selected via input:', {
        name: selectedFile.name,
        size: selectedFile.size,
        type: selectedFile.type
      });
      handleFileSelection(selectedFile as File);
    } else {
      console.warn('⚠️ No files selected or files array empty');
    }
    
    // Reset input to allow selecting the same file again
    e.target.value = '';
  };

  const triggerFileInput = () => {
    console.log('🖱️ File input triggered');
    const fileInput = document.getElementById('file-input') as HTMLInputElement;
    if (fileInput) {
      console.log('📁 File input found, triggering click');
      fileInput.click();
    } else {
      console.error('❌ File input element not found');
      alert('خطأ: لم يتم العثور على عنصر اختيار الملف. يرجى إعادة تحميل الصفحة.');
    }
  };

  const handleFileSelection = (file: File) => {
    // Validate file type
    const allowedTypes = [
      'audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/flac', 'audio/ogg',
      'video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv'
    ];

    if (!allowedTypes.includes(file.type)) {
      alert('نوع الملف غير مدعوم. يرجى اختيار ملف صوتي أو مرئي صحيح.');
      return;
    }

    // Validate file size (100MB max for demo)
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
      alert('حجم الملف كبير جداً. الحد الأقصى للتجربة: 100 ميجابايت.');
      return;
    }

    console.log('🎵 File selected for AI processing:', {
      name: file.name,
      size: formatFileSize(file.size),
      type: file.type
    });

    // Analyze file and get AI recommendations
    const analysis = demoAIProcessor.analyzeAudioFile(file);
    console.log('🔍 AI File Analysis:', analysis);

    // Auto-recommend model based on file
    setProcessingOptions(prev => ({
      ...prev,
      model: analysis.recommended_model
    }));

    setUploadState(prev => ({ ...prev, file }));
  };

  const startProcessing = async () => {
    if (!uploadState.file) return;

    setUploadState(prev => ({ ...prev, isUploading: true }));

    try {
      // Step 1: Simulate file upload with real file processing
      console.log('Starting AI processing for file:', uploadState.file.name);
      
      // Simulate upload progress
      for (let progress = 0; progress <= 100; progress += 20) {
        setUploadState(prev => ({ ...prev, uploadProgress: progress }));
        await new Promise(resolve => setTimeout(resolve, 300));
      }

        // Step 2: Process real file with AI
      const processFormData = new FormData();
      processFormData.append('file', uploadState.file);
      processFormData.append('options', JSON.stringify(processingOptions));
      
      console.log('🤖 Starting real file processing with AI...');
      
      const processResponse = await fetch('/api/process-file', {
        method: 'POST',
        body: processFormData
      });

      if (!processResponse.ok) {
        throw new Error('فشل في معالجة الملف');
      }

      const processData = await processResponse.json();
      console.log('✅ Real file processed:', processData);

      // Create job from real processing results
      const jobData = {
        job: {
          id: processData.job_id,
          status: 'completed',
          progress: 100,
          result: {
            transcript_id: processData.processing_result.transcript.id,
            segments_count: processData.processing_result.transcript.segments.length,
            speakers_count: processData.processing_result.speakers.length,
            confidence_score: processData.processing_result.confidence_score,
            processing_time: processData.processing_result.processing_time,
            realtime_factor: processData.processing_result.processing_time / processData.file_analysis.estimated_duration,
            ai_features_used: processData.ai_simulation.models_simulated
          }
        }
      };

      // Use the transcription API as backup
      const transcribeResponse = await fetch('/api/jobs/transcribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          media_id: `processed_${processData.job_id}`,
          filename: uploadState.file.name,
          file_size: uploadState.file.size,
          content_type: uploadState.file.type,
          ...processingOptions,
          custom_vocabulary: processingOptions.custom_vocabulary,
          real_file_processing: true,
          file_analysis: processData.file_analysis,
          processing_result: processData.processing_result
        })
      });

       let finalJobData = jobData;
      
      if (transcribeResponse.ok) {
        const transcribeData = await transcribeResponse.json();
        finalJobData = transcribeData;
        console.log('📋 Transcription job created:', transcribeData);
      }
      
      // Create AI processing job
      const aiJob = {
        id: jobData.job.id,
        filename: uploadState.file.name,
        status: 'pending' as const,
        progress: 0,
        message: 'جاري بدء المعالجة...',
        current_step: 'initializing',
        created_at: new Date().toISOString(),
        parameters: processingOptions
      };

        // Create completed AI job with real file data
      const completedAIJob = {
        id: finalJobData.job.id,
        filename: uploadState.file.name,
        status: 'completed' as const,
        progress: 100,
        message: 'تم معالجة الملف الحقيقي بنجاح ✨',
        current_step: 'completed',
        created_at: new Date().toISOString(),
        parameters: processingOptions,
        result: processData.processing_result
      };

       setUploadState(prev => ({ 
        ...prev, 
        jobId: finalJobData.job.id,
        processingStatus: completedAIJob,
        isUploading: false 
      }));

      // Store the real processing results
      demoAIProcessor.jobs.set(finalJobData.job.id, completedAIJob);

      console.log('🎉 Real file processing completed, redirecting to results...');

      // Redirect to results immediately since processing is done
      setTimeout(() => {
        router.push(`/transcripts/${processData.processing_result.transcript.id}`);
      }, 2000);

    } catch (error) {
      console.error('Processing error:', error);
      alert('حدث خطأ في بدء المعالجة. يرجى المحاولة مرة أخرى.');
      setUploadState(prev => ({ ...prev, isUploading: false }));
    }
  };

  const monitorJobProgress = async (jobId: string) => {
    const checkStatus = async () => {
      try {
        // Get status from demo AI processor
        const job = demoAIProcessor.getJob(jobId);
        
        if (job) {
          setUploadState(prev => ({ ...prev, processingStatus: job }));
          
          if (job.status === 'completed') {
            console.log('🎉 AI Processing completed successfully!');
            console.log('📄 Results:', job.result);
            
            // Redirect to results page after a short delay
            setTimeout(() => {
              router.push(`/transcripts/${job.result?.transcript_id}`);
            }, 2000);
          } else if (job.status === 'failed') {
            alert(`فشلت المعالجة: ${job.message}`);
          } else if (job.status === 'processing') {
            // Continue monitoring
            setTimeout(checkStatus, 1000);
          }
        } else {
          // Fallback to API if demo processor doesn't have the job
          const response = await fetch(`/api/jobs/${jobId}`);
          const data = await response.json();
          
          if (data.success) {
            setUploadState(prev => ({ ...prev, processingStatus: data.job }));
          }
          
          setTimeout(checkStatus, 2000);
        }
      } catch (error) {
        console.error('Status check error:', error);
        setTimeout(checkStatus, 3000);
      }
    };

    // Start monitoring
    setTimeout(checkStatus, 1000);
  };

  const addCustomVocabulary = () => {
    if (customVocab.trim()) {
      const newTerms = customVocab.split(',').map(term => term.trim()).filter(term => term);
      setProcessingOptions(prev => ({
        ...prev,
        custom_vocabulary: [...prev.custom_vocabulary, ...newTerms]
      }));
      setCustomVocab('');
    }
  };

  const removeVocabularyTerm = (index: number) => {
    setProcessingOptions(prev => ({
      ...prev,
      custom_vocabulary: prev.custom_vocabulary.filter((_, i) => i !== index)
    }));
  };

  // Show processing status if job is running
  if (uploadState.jobId && uploadState.processingStatus) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="container mx-auto max-w-4xl">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              معالجة الملف الصوتي بالذكاء الاصطناعي
            </h1>
            <p className="text-gray-600">
              جاري تحويل {uploadState.file?.name} إلى نص عربي دقيق
            </p>
          </div>

          {/* Processing Status */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                حالة المعالجة
              </CardTitle>
              <CardDescription>
                {uploadState.processingStatus.message}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>التقدم</span>
                    <span>{uploadState.processingStatus.progress}%</span>
                  </div>
                  <Progress value={uploadState.processingStatus.progress} />
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">تفاصيل المعالجة</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>الحالة:</span>
                        <Badge variant={uploadState.processingStatus.status === 'completed' ? 'default' : 'secondary'}>
                          {uploadState.processingStatus.status === 'processing' ? 'قيد المعالجة' : 
                           uploadState.processingStatus.status === 'completed' ? 'مكتمل' : 'معلق'}
                        </Badge>
                      </div>
                      <div className="flex justify-between">
                        <span>المرحلة الحالية:</span>
                        <span className="text-blue-600">
                          {uploadState.processingStatus.current_step === 'audio_preprocessing' ? 'معالجة الصوت' :
                           uploadState.processingStatus.current_step === 'speech_recognition' ? 'تحويل الكلام' :
                           uploadState.processingStatus.current_step === 'speaker_diarization' ? 'فصل المتحدثين' :
                           uploadState.processingStatus.current_step === 'text_postprocessing' ? 'معالجة النص' :
                           uploadState.processingStatus.current_step === 'database_storage' ? 'حفظ البيانات' :
                           uploadState.processingStatus.current_step === 'completed' ? 'مكتمل' : 'معالجة'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>النموذج المستخدم:</span>
                        <span>{processingOptions.model}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">مميزات الذكاء الاصطناعي</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center gap-2">
                        <span className="text-green-500">✓</span>
                        <span>تحسين جودة الصوت</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-green-500">✓</span>
                        <span>تقنية Whisper للتفريغ</span>
                      </div>
                      {processingOptions.diarization && (
                        <div className="flex items-center gap-2">
                          <span className="text-green-500">✓</span>
                          <span>فصل المتحدثين بالذكاء الاصطناعي</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2">
                        <span className="text-green-500">✓</span>
                        <span>معالجة النص العربي</span>
                      </div>
                    </div>
                  </div>
                </div>

                {uploadState.processingStatus.result && (
                  <div className="mt-6 p-4 bg-green-50 rounded-lg">
                    <h4 className="font-medium text-green-900 mb-2">نتائج المعالجة</h4>
                    <div className="grid md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-green-700">عدد المقاطع:</span>
                        <span className="font-medium"> {uploadState.processingStatus.result.segments_count}</span>
                      </div>
                      <div>
                        <span className="text-green-700">عدد المتحدثين:</span>
                        <span className="font-medium"> {uploadState.processingStatus.result.speakers_count}</span>
                      </div>
                      <div>
                        <span className="text-green-700">دقة التفريغ:</span>
                        <span className="font-medium"> {Math.round(uploadState.processingStatus.result.confidence_score * 100)}%</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* AI Processing Info */}
          <Card>
            <CardHeader>
              <CardTitle>تقنيات الذكاء الاصطناعي المستخدمة</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">نماذج الذكاء الاصطناعي</h4>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-xs font-bold text-blue-700">ASR</span>
                      </div>
                      <div>
                        <h5 className="font-medium">faster-whisper</h5>
                        <p className="text-xs text-gray-600">تحويل الكلام إلى نص بدقة عالية</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                        <span className="text-xs font-bold text-green-700">DIA</span>
                      </div>
                      <div>
                        <h5 className="font-medium">pyannote.audio</h5>
                        <p className="text-xs text-gray-600">تحديد المتحدثين وفصل الأصوات</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                        <span className="text-xs font-bold text-purple-700">ENH</span>
                      </div>
                      <div>
                        <h5 className="font-medium">RNNoise</h5>
                        <p className="text-xs text-gray-600">تحسين جودة الصوت وإزالة الضوضاء</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-3">تحسينات خاصة بالعربية</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="text-blue-500">🎯</span>
                      <span>تحسين خاص للهجات العربية</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-blue-500">📝</span>
                      <span>معالجة النص العربي وتصحيح الأخطاء</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-blue-500">🔤</span>
                      <span>دعم المصطلحات المخصصة</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-blue-500">⚡</span>
                      <span>معالجة سريعة ودقيقة</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="container mx-auto max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            رفع ملف للتفريغ الصوتي
          </h1>
          <p className="text-gray-600">
            ارفع ملفك الصوتي أو المرئي واحصل على نسخة نصية دقيقة بالذكاء الاصطناعي
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Upload Area */}
          <div className="lg:col-span-2">
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>اختيار الملف</CardTitle>
                <CardDescription>
                  اسحب الملف هنا أو انقر لاختياره من جهازك
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 cursor-pointer ${
                    uploadState.isDragging
                      ? 'border-blue-400 bg-blue-50 scale-105'
                      : uploadState.file
                      ? 'border-green-400 bg-green-50'
                      : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
                  }`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={triggerFileInput}
                >
                  {uploadState.file ? (
                    <div>
                      <div className="text-4xl mb-4">
                        {uploadState.file.type.startsWith('audio/') ? '🎵' : '🎬'}
                      </div>
                      <h3 className="text-lg font-medium text-green-900 mb-2">
                        {uploadState.file.name}
                      </h3>
                      <div className="text-sm text-green-700 mb-4 space-y-1">
                        <p>الحجم: {formatFileSize(uploadState.file.size)}</p>
                        <p>النوع: {uploadState.file.type}</p>
                        <p>التقدير: {estimateProcessingTime(uploadState.file.size, processingOptions.model)}</p>
                      </div>
                      
                      {/* AI Analysis Results */}
                      {(() => {
                        const analysis = demoAIProcessor.analyzeAudioFile(uploadState.file);
                        return (
                          <div className="bg-blue-50 p-3 rounded mb-4 text-xs">
                            <h4 className="font-medium text-blue-900 mb-2">🤖 تحليل الذكاء الاصطناعي</h4>
                            <div className="space-y-1 text-blue-800">
                              <div>المدة المقدرة: {Math.round(analysis.duration_estimate)} ثانية</div>
                              <div>جودة الصوت: {Math.round(analysis.quality_score * 100)}%</div>
                              <div>النموذج المقترح: {analysis.recommended_model}</div>
                              <div>وقت المعالجة: {analysis.processing_estimate}</div>
                            </div>
                          </div>
                        );
                      })()}
                      
                      <Button
                        variant="outline"
                        onClick={() => setUploadState(prev => ({ ...prev, file: null }))}
                      >
                        اختيار ملف آخر
                      </Button>
                    </div>
                  ) : (
                    <div>
                      <div className="text-4xl mb-4 animate-bounce">
                        {uploadState.isDragging ? '📥' : '📁'}
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        {uploadState.isDragging ? 'اتركه هنا!' : 'اسحب الملفات هنا أو انقر للتصفح'}
                      </h3>
                      <p className="text-sm text-gray-600 mb-4">
                        يدعم: MP3, WAV, MP4, AVI, MOV, FLAC (حد أقصى 500 ميجابايت)
                      </p>
                      
                      {/* Hidden file input */}
                      <input
                        type="file"
                        accept="audio/*,video/*,.mp3,.wav,.mp4,.avi,.mov,.flac,.ogg,.wmv"
                        onChange={handleFileInput}
                        className="hidden"
                        id="file-input"
                        multiple={false}
                      />
                      
                      <div className="space-y-3">
                        <div className="space-y-2">
                          <Button 
                            type="button" 
                            onClick={triggerFileInput}
                            className="cursor-pointer bg-blue-600 hover:bg-blue-700 transform hover:scale-105 transition-all"
                            size="lg"
                          >
                            🎵 اختيار ملف صوتي أو مرئي
                          </Button>
                          
                          {/* Alternative method */}
                          <div className="text-center">
                            <label 
                              htmlFor="file-input-direct" 
                              className="inline-block cursor-pointer text-sm text-blue-600 hover:text-blue-800 underline"
                            >
                              أو انقر هنا كبديل
                            </label>
                            <input
                              type="file"
                              accept="audio/*,video/*,.mp3,.wav,.mp4,.avi,.mov,.flac,.ogg,.wmv"
                              onChange={handleFileInput}
                              className="hidden"
                              id="file-input-direct"
                            />
                          </div>
                        </div>
                        
                        <div className="text-xs text-gray-500 mt-2">
                          💡 يمكنك أيضاً سحب الملف مباشرة إلى هذه المنطقة
                        </div>

                        {/* Test Demo File */}
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <Button 
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              // Create a demo file for testing
                              console.log('🧪 Creating demo file for testing');
                              const demoFile = new File(
                                ['Demo audio content for Arabic STT processing'], 
                                'demo_meeting.mp3', 
                                { type: 'audio/mpeg' }
                              );
                              console.log('✅ Demo file created:', demoFile);
                              handleFileSelection(demoFile);
                            }}
                            className="w-full"
                          >
                            🧪 استخدام ملف تجريبي للاختبار
                          </Button>
                          <div className="text-xs text-gray-500 mt-1 text-center">
                            ملف وهمي لاختبار عملية الرفع والمعالجة
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {uploadState.isUploading && (
                  <div className="mt-4">
                    <div className="flex justify-between text-sm mb-2">
                      <span>رفع الملف</span>
                      <span>{uploadState.uploadProgress}%</span>
                    </div>
                    <Progress value={uploadState.uploadProgress} />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Processing Options */}
            <Card>
              <CardHeader>
                <CardTitle>خيارات المعالجة بالذكاء الاصطناعي</CardTitle>
                <CardDescription>
                  اختر إعدادات المعالجة المناسبة لملفك
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Language Selection */}
                <div>
                  <Label className="text-base font-medium">اللغة واللهجة</Label>
                  <Select 
                    value={processingOptions.language} 
                    onValueChange={(value) => setProcessingOptions(prev => ({ ...prev, language: value }))}
                  >
                    <SelectTrigger className="mt-2">
                      <SelectValue placeholder="اختر اللغة" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ar">العربية الفصحى</SelectItem>
                      <SelectItem value="ar-IQ">العربية العراقية</SelectItem>
                      <SelectItem value="ar-EG">العربية المصرية</SelectItem>
                      <SelectItem value="ar-SA">العربية السعودية</SelectItem>
                      <SelectItem value="ar-MA">العربية المغربية</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Model Selection */}
                <div>
                  <Label className="text-base font-medium">نموذج الذكاء الاصطناعي</Label>
                  <Select 
                    value={processingOptions.model} 
                    onValueChange={(value) => setProcessingOptions(prev => ({ ...prev, model: value }))}
                  >
                    <SelectTrigger className="mt-2">
                      <SelectValue placeholder="اختر النموذج" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="large-v3">
                        Large-v3 (أعلى دقة - 95%+)
                      </SelectItem>
                      <SelectItem value="medium">
                        Medium (دقة جيدة - 90%+) 
                      </SelectItem>
                      <SelectItem value="small">
                        Small (سرعة عالية - 85%+)
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-gray-500 mt-1">
                    النماذج الأكبر أدق لكنها تستغرق وقتاً أطول
                  </p>
                </div>

                {/* Enhancement Level */}
                <div>
                  <Label className="text-base font-medium">مستوى تحسين الصوت</Label>
                  <Select 
                    value={processingOptions.enhancement_level} 
                    onValueChange={(value) => setProcessingOptions(prev => ({ ...prev, enhancement_level: value }))}
                  >
                    <SelectTrigger className="mt-2">
                      <SelectValue placeholder="اختر مستوى التحسين" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="high">عالي (أفضل جودة)</SelectItem>
                      <SelectItem value="medium">متوسط (متوازن)</SelectItem>
                      <SelectItem value="light">خفيف (أسرع)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Speaker Diarization */}
                <div className="flex items-center space-x-2 space-x-reverse">
                  <Checkbox
                    id="diarization"
                    checked={processingOptions.diarization}
                    onCheckedChange={(checked) => 
                      setProcessingOptions(prev => ({ ...prev, diarization: checked as boolean }))
                    }
                  />
                  <Label htmlFor="diarization" className="text-base font-medium">
                    فصل المتحدثين (Speaker Diarization)
                  </Label>
                </div>
                <p className="text-xs text-gray-500">
                  يحدد المتحدثين المختلفين ويفصل بين أصواتهم باستخدام الذكاء الاصطناعي
                </p>

                {/* Custom Vocabulary */}
                <div>
                  <Label className="text-base font-medium">مصطلحات مخصصة</Label>
                  <div className="mt-2 space-y-3">
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={customVocab}
                        onChange={(e) => setCustomVocab(e.target.value)}
                        placeholder="أدخل مصطلحات مفصولة بفواصل"
                        className="flex-1 px-3 py-2 border rounded text-right"
                        dir="rtl"
                      />
                      <Button onClick={addCustomVocabulary} size="sm">
                        إضافة
                      </Button>
                    </div>
                    
                    {processingOptions.custom_vocabulary.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {processingOptions.custom_vocabulary.map((term, index) => (
                          <Badge 
                            key={index} 
                            variant="secondary" 
                            className="cursor-pointer"
                            onClick={() => removeVocabularyTerm(index)}
                          >
                            {term} ✕
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    أضف أسماء أو مصطلحات مهمة لتحسين دقة التعرف عليها
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div>
            {/* Processing Info */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>معلومات المعالجة</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-sm">
                  <h4 className="font-medium text-gray-900 mb-2">الوقت المتوقع</h4>
                  <div className="space-y-1 text-gray-600">
                    <div>Large-v3: 2-3 دقائق</div>
                    <div>Medium: 1-2 دقيقة</div>
                    <div>Small: 30-60 ثانية</div>
                  </div>
                </div>

                <div className="text-sm">
                  <h4 className="font-medium text-gray-900 mb-2">مراحل المعالجة</h4>
                  <div className="space-y-1 text-gray-600">
                    <div>1. تحسين جودة الصوت</div>
                    <div>2. تحويل الكلام إلى نص</div>
                    <div>3. فصل المتحدثين</div>
                    <div>4. معالجة النص العربي</div>
                    <div>5. حفظ النتائج</div>
                  </div>
                </div>

                <div className="text-sm">
                  <h4 className="font-medium text-gray-900 mb-2">الملفات المدعومة</h4>
                  <div className="space-y-1 text-gray-600">
                    <div>🎵 MP3, WAV, FLAC, OGG</div>
                    <div>🎬 MP4, AVI, MOV, WMV</div>
                    <div>📏 حد أقصى: 500 ميجابايت</div>
                    <div>⏱️ حد أقصى: 3 ساعات</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Start Processing Button */}
            <Button 
              className="w-full h-12 text-lg"
              disabled={!uploadState.file || uploadState.isUploading}
              onClick={startProcessing}
            >
              {uploadState.isUploading ? (
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>بدء المعالجة...</span>
                </div>
              ) : (
                '🚀 بدء المعالجة بالذكاء الاصطناعي'
              )}
            </Button>

            {/* Demo Notice */}
            <Alert className="mt-4">
              <AlertDescription className="text-center">
                <div className="text-sm">
                  <strong>نسخة تجريبية</strong>
                  <p className="mt-1">
                    لتفعيل المعالجة الفعلية بالذكاء الاصطناعي:
                  </p>
                  <code className="block bg-gray-100 px-2 py-1 rounded mt-2 text-xs">
                    ./start-full-stack.sh
                  </code>
                </div>
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </div>
    </div>
  );
}
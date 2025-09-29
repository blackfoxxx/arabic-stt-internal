interface JobResult {
  transcript_id: string;
  segments: Array<{
    id: string;
    start: number;
    end: number;
    text: string;
    confidence: number;
    speaker_id: string;
    speaker_name: string;
  }>;
  speakers: Array<{
    id: string;
    label: string;
    display_name: string;
    total_speaking_time: number;
    segments_count: number;
    confidence_score: number;
  }>;
  processing_time: number;
  confidence_score: number;
  model_used: string;
  language: string;
  ai_features_used: string[];
  arabic_analysis: {
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
    dialect_analysis: {
      detected_dialect: string;
      confidence: number;
      regional_markers: string[];
    };
    linguistic_features: {
      formality_level: string;
      complexity_score: number;
      vocabulary_richness: number;
    };
  };
  quality_metrics: {
    audio_quality: number;
    accuracy_estimate: string;
    dialect_detected: string;
    enhancement_applied: string;
  };
}

interface Job {
  id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  current_step: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  createdAt?: string;
  result?: JobResult;
}

class DemoAIProcessor {
  public jobs: Map<string, Job> = new Map();

  constructor() {
    // Initialize with demo data that matches the statistics-storage transcript IDs
    this.initializeDemoData();
  }

  private initializeDemoData(): void {
    const demoJobs: Job[] = [
      {
        id: 'demo_1',
        filename: 'اجتماع_الإدارة_2024.mp3',
        status: 'completed',
        progress: 100,
        message: 'تم إكمال المعالجة بنجاح',
        current_step: 'مكتمل',
        created_at: '2024-01-15T10:30:00Z',
        completed_at: '2024-01-15T10:32:30Z',
        createdAt: '2024-01-15T10:30:00Z',
        result: {
          transcript_id: 'transcript_1705313550',
          segments: [
            {
              id: 'segment_1',
              start: 0.0,
              end: 8.5,
              text: 'بسم الله الرحمن الرحيم، أهلاً وسهلاً بكم في اجتماع الإدارة لهذا الشهر',
              confidence: 0.95,
              speaker_id: 'speaker_1',
              speaker_name: 'المدير العام'
            },
            {
              id: 'segment_2',
              start: 8.5,
              end: 15.2,
              text: 'سنبدأ اليوم بمراجعة الأداء المالي للربع الأول من هذا العام',
              confidence: 0.92,
              speaker_id: 'speaker_1',
              speaker_name: 'المدير العام'
            },
            {
              id: 'segment_3',
              start: 15.2,
              end: 22.8,
              text: 'شكراً لك، لدينا نتائج إيجابية في معظم القطاعات',
              confidence: 0.89,
              speaker_id: 'speaker_2',
              speaker_name: 'مدير المالية'
            }
          ],
          speakers: [
            {
              id: 'speaker_1',
              label: 'SPEAKER_01',
              display_name: 'المدير العام',
              total_speaking_time: 16.7,
              segments_count: 2,
              confidence_score: 0.935
            },
            {
              id: 'speaker_2',
              label: 'SPEAKER_02',
              display_name: 'مدير المالية',
              total_speaking_time: 7.6,
              segments_count: 1,
              confidence_score: 0.89
            }
          ],
          processing_time: 150,
          confidence_score: 0.92,
          model_used: 'faster-whisper-large-v3',
          language: 'ar',
          ai_features_used: ['faster-whisper', 'pyannote.audio', 'arabic-bert'],
          arabic_analysis: {
            overall_sentiment: 'إيجابي',
            sentiment_distribution: {
              positive: 8,
              neutral: 12,
              negative: 2
            },
            grammar_issues: {
              t5_suggestions: 1,
              bert_suggestions: 0,
              camel_suggestions: 2
            },
            dialect_analysis: {
              detected_dialect: 'عربية فصحى',
              confidence: 0.94,
              regional_markers: ['مصطلحات إدارية', 'لهجة خليجية خفيفة']
            },
            linguistic_features: {
              formality_level: 'رسمي',
              complexity_score: 0.78,
              vocabulary_richness: 0.85
            }
          },
          quality_metrics: {
            audio_quality: 0.88,
            accuracy_estimate: 'عالية',
            dialect_detected: 'عربية فصحى',
            enhancement_applied: 'تحسين الضوضاء'
          }
        }
      },
      {
        id: 'demo_2',
        filename: 'تدريب_الموظفين.mp4',
        status: 'completed',
        progress: 100,
        message: 'تم إكمال المعالجة بنجاح',
        current_step: 'مكتمل',
        created_at: '2024-01-15T09:15:00Z',
        completed_at: '2024-01-15T09:17:51Z',
        createdAt: '2024-01-15T09:15:00Z',
        result: {
          transcript_id: 'transcript_1705311451',
          segments: [
            {
              id: 'segment_1',
              start: 0.0,
              end: 12.3,
              text: 'مرحباً بكم في دورة تدريب الموظفين الجدد، سنتعلم اليوم أساسيات العمل في الشركة',
              confidence: 0.93,
              speaker_id: 'speaker_1',
              speaker_name: 'المدرب'
            },
            {
              id: 'segment_2',
              start: 12.3,
              end: 25.7,
              text: 'أولاً، دعونا نتعرف على قيم الشركة ورؤيتها المستقبلية',
              confidence: 0.91,
              speaker_id: 'speaker_1',
              speaker_name: 'المدرب'
            }
          ],
          speakers: [
            {
              id: 'speaker_1',
              label: 'SPEAKER_01',
              display_name: 'المدرب',
              total_speaking_time: 25.7,
              segments_count: 2,
              confidence_score: 0.92
            }
          ],
          processing_time: 171,
          confidence_score: 0.92,
          model_used: 'faster-whisper-large-v3',
          language: 'ar',
          ai_features_used: ['faster-whisper', 'pyannote.audio'],
          arabic_analysis: {
            overall_sentiment: 'إيجابي',
            sentiment_distribution: {
              positive: 15,
              neutral: 8,
              negative: 1
            },
            grammar_issues: {
              t5_suggestions: 0,
              bert_suggestions: 1,
              camel_suggestions: 1
            },
            dialect_analysis: {
              detected_dialect: 'عربية فصحى',
              confidence: 0.96,
              regional_markers: ['مصطلحات تعليمية']
            },
            linguistic_features: {
              formality_level: 'رسمي',
              complexity_score: 0.72,
              vocabulary_richness: 0.80
            }
          },
          quality_metrics: {
            audio_quality: 0.90,
            accuracy_estimate: 'عالية',
            dialect_detected: 'عربية فصحى',
            enhancement_applied: 'تحسين الصوت'
          }
        }
      },
      {
        id: 'demo_3',
        filename: 'مكالمة_عمل.wav',
        status: 'completed',
        progress: 100,
        message: 'تم إكمال المعالجة بنجاح',
        current_step: 'مكتمل',
        created_at: '2024-01-15T08:45:00Z',
        completed_at: '2024-01-15T08:46:01Z',
        createdAt: '2024-01-15T08:45:00Z',
        result: {
          transcript_id: 'transcript_1705309561',
          segments: [
            {
              id: 'segment_1',
              start: 0.0,
              end: 6.8,
              text: 'السلام عليكم، كيف حالك؟ أتصل بخصوص المشروع الجديد',
              confidence: 0.88,
              speaker_id: 'speaker_1',
              speaker_name: 'العميل'
            },
            {
              id: 'segment_2',
              start: 6.8,
              end: 13.5,
              text: 'وعليكم السلام، أهلاً وسهلاً، نعم المشروع يسير بشكل جيد',
              confidence: 0.90,
              speaker_id: 'speaker_2',
              speaker_name: 'مدير المشروع'
            }
          ],
          speakers: [
            {
              id: 'speaker_1',
              label: 'SPEAKER_01',
              display_name: 'العميل',
              total_speaking_time: 6.8,
              segments_count: 1,
              confidence_score: 0.88
            },
            {
              id: 'speaker_2',
              label: 'SPEAKER_02',
              display_name: 'مدير المشروع',
              total_speaking_time: 6.7,
              segments_count: 1,
              confidence_score: 0.90
            }
          ],
          processing_time: 61,
          confidence_score: 0.89,
          model_used: 'faster-whisper-medium',
          language: 'ar',
          ai_features_used: ['faster-whisper', 'pyannote.audio'],
          arabic_analysis: {
            overall_sentiment: 'محايد',
            sentiment_distribution: {
              positive: 5,
              neutral: 10,
              negative: 0
            },
            grammar_issues: {
              t5_suggestions: 0,
              bert_suggestions: 0,
              camel_suggestions: 1
            },
            dialect_analysis: {
              detected_dialect: 'عربية فصحى مع لهجة محلية',
              confidence: 0.85,
              regional_markers: ['تحيات تقليدية']
            },
            linguistic_features: {
              formality_level: 'غير رسمي',
              complexity_score: 0.65,
              vocabulary_richness: 0.70
            }
          },
          quality_metrics: {
            audio_quality: 0.75,
            accuracy_estimate: 'متوسطة',
            dialect_detected: 'عربية فصحى مع لهجة',
            enhancement_applied: 'تقليل الضوضاء'
          }
        }
      },
      {
        id: 'demo_4',
        filename: 'محاضرة_تقنية.mp3',
        status: 'completed',
        progress: 100,
        message: 'تم إكمال المعالجة بنجاح',
        current_step: 'مكتمل',
        created_at: '2024-01-14T16:20:00Z',
        completed_at: '2024-01-14T16:22:15Z',
        createdAt: '2024-01-14T16:20:00Z',
        result: {
          transcript_id: 'transcript_1705250535',
          segments: [
            {
              id: 'segment_1',
              start: 0.0,
              end: 10.2,
              text: 'اليوم سنتحدث عن الذكاء الاصطناعي وتطبيقاته في المجال التقني',
              confidence: 0.94,
              speaker_id: 'speaker_1',
              speaker_name: 'المحاضر'
            },
            {
              id: 'segment_2',
              start: 10.2,
              end: 18.9,
              text: 'الذكاء الاصطناعي يشمل التعلم الآلي ومعالجة اللغات الطبيعية',
              confidence: 0.96,
              speaker_id: 'speaker_1',
              speaker_name: 'المحاضر'
            }
          ],
          speakers: [
            {
              id: 'speaker_1',
              label: 'SPEAKER_01',
              display_name: 'المحاضر',
              total_speaking_time: 18.9,
              segments_count: 2,
              confidence_score: 0.95
            }
          ],
          processing_time: 135,
          confidence_score: 0.95,
          model_used: 'faster-whisper-large-v3',
          language: 'ar',
          ai_features_used: ['faster-whisper', 'arabic-bert', 'technical-vocabulary'],
          arabic_analysis: {
            overall_sentiment: 'محايد',
            sentiment_distribution: {
              positive: 6,
              neutral: 18,
              negative: 0
            },
            grammar_issues: {
              t5_suggestions: 0,
              bert_suggestions: 0,
              camel_suggestions: 0
            },
            dialect_analysis: {
              detected_dialect: 'عربية فصحى أكاديمية',
              confidence: 0.98,
              regional_markers: ['مصطلحات تقنية', 'أسلوب أكاديمي']
            },
            linguistic_features: {
              formality_level: 'رسمي جداً',
              complexity_score: 0.88,
              vocabulary_richness: 0.92
            }
          },
          quality_metrics: {
            audio_quality: 0.92,
            accuracy_estimate: 'عالية جداً',
            dialect_detected: 'عربية فصحى أكاديمية',
            enhancement_applied: 'تحسين متقدم'
          }
        }
      },
      {
        id: 'demo_5',
        filename: 'مقابلة_شخصية.mp4',
        status: 'completed',
        progress: 100,
        message: 'تم إكمال المعالجة بنجاح',
        current_step: 'مكتمل',
        created_at: '2024-01-15T11:00:00Z',
        completed_at: '2024-01-15T11:01:30Z',
        createdAt: '2024-01-15T11:00:00Z',
        result: {
          transcript_id: 'transcript_1705315290',
          segments: [
            {
              id: 'segment_1',
              start: 0.0,
              end: 7.5,
              text: 'أهلاً وسهلاً، اسمي أحمد وأنا مهتم بالوظيفة المعلن عنها',
              confidence: 0.91,
              speaker_id: 'speaker_1',
              speaker_name: 'المتقدم للوظيفة'
            },
            {
              id: 'segment_2',
              start: 7.5,
              end: 14.8,
              text: 'مرحباً أحمد، حدثنا عن خبرتك في هذا المجال',
              confidence: 0.93,
              speaker_id: 'speaker_2',
              speaker_name: 'مسؤول التوظيف'
            },
            {
              id: 'segment_3',
              start: 14.8,
              end: 25.3,
              text: 'لدي خبرة خمس سنوات في تطوير البرمجيات وإدارة المشاريع التقنية',
              confidence: 0.89,
              speaker_id: 'speaker_1',
              speaker_name: 'المتقدم للوظيفة'
            }
          ],
          speakers: [
            {
              id: 'speaker_1',
              label: 'SPEAKER_01',
              display_name: 'المتقدم للوظيفة',
              total_speaking_time: 17.8,
              segments_count: 2,
              confidence_score: 0.90
            },
            {
              id: 'speaker_2',
              label: 'SPEAKER_02',
              display_name: 'مسؤول التوظيف',
              total_speaking_time: 7.3,
              segments_count: 1,
              confidence_score: 0.93
            }
          ],
          processing_time: 90,
          confidence_score: 0.91,
          model_used: 'faster-whisper-large-v3',
          language: 'ar',
          ai_features_used: ['faster-whisper', 'pyannote.audio', 'arabic-bert'],
          arabic_analysis: {
            overall_sentiment: 'إيجابي',
            sentiment_distribution: {
              positive: 12,
              neutral: 8,
              negative: 0
            },
            grammar_issues: {
              t5_suggestions: 1,
              bert_suggestions: 0,
              camel_suggestions: 1
            },
            dialect_analysis: {
              detected_dialect: 'عربية فصحى مع لهجة محلية',
              confidence: 0.87,
              regional_markers: ['أسلوب مهني', 'تعبيرات رسمية']
            },
            linguistic_features: {
              formality_level: 'رسمي',
              complexity_score: 0.75,
              vocabulary_richness: 0.82
            }
          },
          quality_metrics: {
            audio_quality: 0.85,
            accuracy_estimate: 'عالية',
            dialect_detected: 'عربية فصحى مع لهجة',
            enhancement_applied: 'تحسين الضوضاء'
          }
        }
      }
    ];

    // Add all demo jobs to the processor
    demoJobs.forEach(job => {
      this.jobs.set(job.id, job);
    });

    console.log('📊 Demo AI Processor initialized with', demoJobs.length, 'demo jobs');
  }

  getAllJobs(): Job[] {
    return Array.from(this.jobs.values());
  }

  getJob(jobId: string): Job | undefined {
    return this.jobs.get(jobId);
  }

  addJob(job: Job): void {
    this.jobs.set(job.id, job);
  }

  updateJob(jobId: string, updates: Partial<Job>): void {
    const existingJob = this.jobs.get(jobId);
    if (existingJob) {
      this.jobs.set(jobId, { ...existingJob, ...updates });
    }
  }

  removeJob(jobId: string): void {
    this.jobs.delete(jobId);
  }

  clearAllJobs(): void {
    this.jobs.clear();
  }

  // Method to create demo data for a new transcript ID
  createDemoTranscriptData(transcriptId: string, filename: string = 'ملف_جديد.mp4'): JobResult {
    const demoResult: JobResult = {
      transcript_id: transcriptId,
      segments: [
        {
          id: 'segment_1',
          start: 0.0,
          end: 5.2,
          text: 'مرحباً، هذا ملف تجريبي جديد',
          confidence: 0.95,
          speaker_id: 'speaker_1',
          speaker_name: 'المتحدث الأول'
        },
        {
          id: 'segment_2',
          start: 5.2,
          end: 12.8,
          text: 'تم إنشاء هذا النص تلقائياً لأغراض العرض التوضيحي',
          confidence: 0.92,
          speaker_id: 'speaker_1',
          speaker_name: 'المتحدث الأول'
        },
        {
          id: 'segment_3',
          start: 12.8,
          end: 18.5,
          text: 'شكراً لاستخدام نظام التفريغ الصوتي العربي',
          confidence: 0.89,
          speaker_id: 'speaker_2',
          speaker_name: 'المتحدث الثاني'
        }
      ],
      speakers: [
        {
          id: 'speaker_1',
          label: 'SPEAKER_01',
          display_name: 'المتحدث الأول',
          total_speaking_time: 12.0,
          segments_count: 2,
          confidence_score: 0.935
        },
        {
          id: 'speaker_2',
          label: 'SPEAKER_02',
          display_name: 'المتحدث الثاني',
          total_speaking_time: 5.7,
          segments_count: 1,
          confidence_score: 0.89
        }
      ],
      processing_time: 95,
      confidence_score: 0.92,
      model_used: 'faster-whisper-large-v3',
      language: 'ar',
      ai_features_used: ['faster-whisper', 'pyannote.audio', 'arabic-bert'],
      arabic_analysis: {
        overall_sentiment: 'إيجابي',
        sentiment_distribution: {
          positive: 6,
          neutral: 8,
          negative: 1
        },
        grammar_issues: {
          t5_suggestions: 2,
          bert_suggestions: 1,
          camel_suggestions: 1
        },
        dialect_analysis: {
          detected_dialect: 'عربية فصحى',
          confidence: 0.88,
          regional_markers: ['فصحى حديثة']
        },
        linguistic_features: {
          formality_level: 'رسمي',
          complexity_score: 0.65,
          vocabulary_richness: 0.75
        }
      },
      quality_metrics: {
        audio_quality: 0.85,
        accuracy_estimate: 'عالية',
        dialect_detected: 'عربية فصحى',
        enhancement_applied: 'تحسين الضوضاء'
      }
    };

    // Create a new job with this demo data
    const newJob: Job = {
      id: `job_${Date.now()}`,
      filename: filename,
      status: 'completed',
      progress: 100,
      message: 'تم إكمال المعالجة بنجاح',
      current_step: 'مكتمل',
      created_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      createdAt: new Date().toISOString(),
      result: demoResult
    };

    this.addJob(newJob);
    console.log(`📝 Created demo transcript data for ID: ${transcriptId}`);
    return demoResult;
  }

  getJobByTranscriptId(transcriptId: string): Job | undefined {
    return Array.from(this.jobs.values()).find(job => 
      job.result?.transcript_id === transcriptId
    );
  }
}

// Export a singleton instance
export const demoAIProcessor = new DemoAIProcessor();
"use client";

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 space-x-reverse">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">ع</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">التوثيق الفني</h1>
                <p className="text-sm text-gray-600">دليل المطورين والمستخدمين</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4 space-x-reverse">
              <Button variant="outline" asChild>
                <Link href="/help">المساعدة</Link>
              </Button>
              <Button asChild>
                <Link href="/">الصفحة الرئيسية</Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <Tabs defaultValue="api" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="api">API</TabsTrigger>
              <TabsTrigger value="integration">التكامل</TabsTrigger>
              <TabsTrigger value="deployment">النشر</TabsTrigger>
              <TabsTrigger value="ai-models">نماذج AI</TabsTrigger>
            </TabsList>

            {/* API Documentation */}
            <TabsContent value="api" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>واجهة البرمجة REST API</CardTitle>
                  <CardDescription>
                    دليل شامل لاستخدام واجهة البرمجة للتكامل مع أنظمتك
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Authentication */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Authentication - المصادقة</h4>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h5 className="text-sm font-medium mb-2">تسجيل الدخول</h5>
                        <code className="block bg-black text-green-400 p-3 rounded text-xs">
{`POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "jwt_token_here",
  "refresh_token": "refresh_token_here",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": { ... }
}`}
                        </code>
                      </div>
                    </div>

                    {/* File Upload */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Media Upload - رفع الملفات</h4>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h5 className="text-sm font-medium mb-2">إنشاء رابط رفع</h5>
                        <code className="block bg-black text-green-400 p-3 rounded text-xs">
{`POST /api/media/upload-url
Authorization: Bearer jwt_token
Content-Type: application/json

{
  "filename": "meeting.mp3",
  "content_type": "audio/mpeg",
  "file_size": 2048576
}

Response:
{
  "upload_url": "https://storage.../upload/...",
  "media_file_id": "media_123",
  "expires_at": "2024-01-01T12:00:00Z"
}`}
                        </code>
                      </div>
                    </div>

                    {/* Transcription */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">AI Transcription - التفريغ بالذكاء الاصطناعي</h4>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h5 className="text-sm font-medium mb-2">بدء مهمة تفريغ</h5>
                        <code className="block bg-black text-green-400 p-3 rounded text-xs">
{`POST /api/jobs/transcribe
Authorization: Bearer jwt_token
Content-Type: application/json

{
  "media_id": "media_123",
  "language": "ar",
  "model": "large-v3",
  "diarization": true,
  "enhancement_level": "medium",
  "custom_vocabulary": ["الشركة", "المشروع"]
}

Response:
{
  "job": {
    "id": "job_456",
    "status": "processing",
    "estimated_duration_seconds": 120
  },
  "ai_processing": {
    "model_selected": "large-v3",
    "features_enabled": [...],
    "estimated_steps": [...]
  }
}`}
                        </code>
                      </div>
                    </div>

                    {/* Job Status */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Job Monitoring - مراقبة المهام</h4>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h5 className="text-sm font-medium mb-2">حالة المهمة</h5>
                        <code className="block bg-black text-green-400 p-3 rounded text-xs">
{`GET /api/jobs/{job_id}
Authorization: Bearer jwt_token

Response:
{
  "job": {
    "id": "job_456",
    "status": "processing",
    "progress": 60,
    "message": "تحديد المتحدثين",
    "current_step": "speaker_diarization"
  },
  "ai_processing_info": {
    "pipeline_stage": "speaker_diarization",
    "ai_models_active": true,
    "estimated_completion": "2-3 minutes"
  }
}`}
                        </code>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Integration Guide */}
            <TabsContent value="integration" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>تكامل المنصة مع أنظمتك</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">JavaScript SDK</h4>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <code className="block bg-black text-green-400 p-3 rounded text-xs">
{`// تكامل JavaScript
const client = new ArabicSTTClient({
  apiUrl: 'https://api.yourdomain.com/v1',
  apiKey: 'your_api_key'
});

// رفع ملف
const uploadResult = await client.uploadFile(file);

// بدء التفريغ
const job = await client.startTranscription({
  mediaId: uploadResult.media_id,
  language: 'ar',
  model: 'large-v3'
});

// مراقبة التقدم
client.onProgress(job.id, (progress) => {
  console.log('التقدم:', progress.percentage + '%');
});

// الحصول على النتائج
const transcript = await client.getTranscript(job.transcript_id);`}
                        </code>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Python SDK</h4>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <code className="block bg-black text-green-400 p-3 rounded text-xs">
{`# تكامل Python
from arabic_stt import ArabicSTTClient

client = ArabicSTTClient(
    api_url='https://api.yourdomain.com/v1',
    api_key='your_api_key'
)

# رفع ملف
upload_result = client.upload_file('meeting.mp3')

# بدء التفريغ
job = client.start_transcription(
    media_id=upload_result['media_id'],
    language='ar',
    model='large-v3',
    diarization=True
)

# انتظار الانتهاء
transcript = client.wait_for_completion(job['id'])
print(f"النسخة النصية: {transcript['text']}")`}
                        </code>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Webhooks</h4>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <code className="block bg-black text-green-400 p-3 rounded text-xs">
{`// إعداد Webhook
POST /api/webhooks
{
  "name": "تنبيهات التفريغ",
  "url": "https://yourdomain.com/webhook",
  "events": ["job.completed", "job.failed"],
  "secret": "webhook_secret"
}

// Webhook Payload
{
  "event": "job.completed",
  "data": {
    "job_id": "job_123",
    "transcript_id": "transcript_456",
    "status": "completed",
    "processing_time": 45.2,
    "confidence_score": 0.92
  },
  "timestamp": "2024-01-01T12:00:00Z"
}`}
                        </code>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Deployment */}
            <TabsContent value="deployment" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>نشر المنصة</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">التطوير المحلي</h4>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <code className="block bg-black text-green-400 p-3 rounded text-xs">
{`# تشغيل المنصة كاملة
./start-full-stack.sh

# أو تشغيل الخدمات منفصلة
docker-compose up -d postgres redis minio
docker-compose up -d api worker
docker-compose up -d prometheus grafana

# الخدمات:
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Grafana: http://localhost:3001
# MinIO: http://localhost:9001`}
                        </code>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">النشر للإنتاج</h4>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <code className="block bg-black text-green-400 p-3 rounded text-xs">
{`# نسخ ملف الإعدادات
cp .env.example .env

# تحرير الإعدادات
nano .env

# تشغيل الإنتاج
docker-compose -f docker-compose.prod.yml up -d

# أو Kubernetes
kubectl apply -f k8s/`}
                        </code>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">متطلبات النظام</h4>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="bg-blue-50 p-4 rounded-lg">
                          <h5 className="font-medium text-blue-900 mb-2">الحد الأدنى</h5>
                          <div className="text-sm text-blue-800 space-y-1">
                            <div>CPU: 4 أنوية</div>
                            <div>RAM: 8 جيجابايت</div>
                            <div>Storage: 50 جيجابايت</div>
                            <div>Network: 100 ميجابت/ثانية</div>
                          </div>
                        </div>
                        <div className="bg-green-50 p-4 rounded-lg">
                          <h5 className="font-medium text-green-900 mb-2">موصى به</h5>
                          <div className="text-sm text-green-800 space-y-1">
                            <div>CPU: 8+ أنوية</div>
                            <div>RAM: 32 جيجابايت</div>
                            <div>GPU: RTX 3060+ (اختياري)</div>
                            <div>Storage: 500 جيجابايت SSD</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* AI Models */}
            <TabsContent value="ai-models" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>نماذج الذكاء الاصطناعي</CardTitle>
                  <CardDescription>
                    دليل شامل لنماذج المعالجة والتحسين
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Whisper Models */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-4">نماذج faster-whisper للتفريغ</h4>
                      <div className="grid gap-4">
                        <Card className="border">
                          <CardHeader>
                            <div className="flex items-center justify-between">
                              <CardTitle className="text-lg">Whisper Large-v3</CardTitle>
                              <Badge className="bg-green-100 text-green-800">الأفضل للعربية</Badge>
                            </div>
                          </CardHeader>
                          <CardContent>
                            <div className="grid md:grid-cols-2 gap-4 text-sm">
                              <div>
                                <div className="font-medium text-gray-900 mb-1">الأداء:</div>
                                <div className="text-gray-600 space-y-1">
                                  <div>• دقة: 95%+ للعربية الفصحى</div>
                                  <div>• دقة: 92%+ للهجات المحلية</div>
                                  <div>• سرعة: 0.5-1x الوقت الحقيقي</div>
                                </div>
                              </div>
                              <div>
                                <div className="font-medium text-gray-900 mb-1">المتطلبات:</div>
                                <div className="text-gray-600 space-y-1">
                                  <div>• ذاكرة GPU: 8+ جيجابايت</div>
                                  <div>• ذاكرة النظام: 16+ جيجابايت</div>
                                  <div>• مناسب للإنتاج عالي الجودة</div>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>

                        <Card className="border">
                          <CardHeader>
                            <div className="flex items-center justify-between">
                              <CardTitle className="text-lg">Whisper Medium</CardTitle>
                              <Badge className="bg-blue-100 text-blue-800">متوازن</Badge>
                            </div>
                          </CardHeader>
                          <CardContent>
                            <div className="grid md:grid-cols-2 gap-4 text-sm">
                              <div>
                                <div className="font-medium text-gray-900 mb-1">الأداء:</div>
                                <div className="text-gray-600 space-y-1">
                                  <div>• دقة: 90%+ للعربية</div>
                                  <div>• سرعة: 0.8x الوقت الحقيقي</div>
                                  <div>• توازن جيد بين الدقة والسرعة</div>
                                </div>
                              </div>
                              <div>
                                <div className="font-medium text-gray-900 mb-1">المتطلبات:</div>
                                <div className="text-gray-600 space-y-1">
                                  <div>• ذاكرة GPU: 4+ جيجابايت</div>
                                  <div>• ذاكرة النظام: 8+ جيجابايت</div>
                                  <div>• مناسب للاستخدام العام</div>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </div>

                    {/* Diarization Models */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-4">نماذج فصل المتحدثين</h4>
                      <Card className="border">
                        <CardHeader>
                          <CardTitle className="text-lg">pyannote.audio 3.1</CardTitle>
                          <Badge className="bg-purple-100 text-purple-800">فصل المتحدثين</Badge>
                        </CardHeader>
                        <CardContent>
                          <div className="text-sm space-y-2">
                            <div>• تحديد تلقائي للمتحدثين (1-10 أشخاص)</div>
                            <div>• دقة عالية في التمييز بين الأصوات</div>
                            <div>• محسن للمحادثات العربية</div>
                            <div>• يتطلب توكن HuggingFace للوصول</div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    {/* Audio Enhancement */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-4">تحسين جودة الصوت</h4>
                      <div className="grid md:grid-cols-2 gap-4">
                        <Card className="border">
                          <CardHeader>
                            <CardTitle className="text-lg">RNNoise</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="text-sm text-gray-600 space-y-1">
                              <div>• إزالة الضوضاء بالشبكات العصبية</div>
                              <div>• يحافظ على وضوح الكلام</div>
                              <div>• مناسب للتسجيلات الصاخبة</div>
                            </div>
                          </CardContent>
                        </Card>

                        <Card className="border">
                          <CardHeader>
                            <CardTitle className="text-lg">FFmpeg Enhancement</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="text-sm text-gray-600 space-y-1">
                              <div>• تحسين ديناميكي للصوت</div>
                              <div>• تطبيع مستوى الصوت</div>
                              <div>• ترشيح ترددي للعربية</div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Quick Links */}
          <div className="mt-12">
            <Card>
              <CardHeader>
                <CardTitle>روابط مفيدة</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4">
                  <Button variant="outline" className="h-auto p-4" asChild>
                    <Link href="/help" className="block text-center">
                      <div className="text-2xl mb-2">❓</div>
                      <div className="font-medium">الأسئلة الشائعة</div>
                      <div className="text-xs text-gray-500">حلول سريعة للمشاكل</div>
                    </Link>
                  </Button>
                  
                  <Button variant="outline" className="h-auto p-4" asChild>
                    <Link href="/contact" className="block text-center">
                      <div className="text-2xl mb-2">💬</div>
                      <div className="font-medium">تواصل معنا</div>
                      <div className="text-xs text-gray-500">دعم فني مباشر</div>
                    </Link>
                  </Button>
                  
                  <Button variant="outline" className="h-auto p-4" asChild>
                    <a href="https://github.com/arabic-stt/platform" target="_blank" className="block text-center">
                      <div className="text-2xl mb-2">📚</div>
                      <div className="font-medium">المصدر المفتوح</div>
                      <div className="text-xs text-gray-500">كود المشروع على GitHub</div>
                    </a>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
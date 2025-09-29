"use client";

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function HelpPage() {
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
                <h1 className="text-xl font-bold text-gray-900">مركز المساعدة</h1>
                <p className="text-sm text-gray-600">الأسئلة الشائعة والدعم الفني</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4 space-x-reverse">
              <Button variant="outline" asChild>
                <Link href="/dashboard">لوحة التحكم</Link>
              </Button>
              <Button asChild>
                <Link href="/">الصفحة الرئيسية</Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Quick Help */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            كيف يمكننا مساعدتك؟
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            دليل شامل لاستخدام منصة التفريغ الصوتي العربية وحل المشاكل الشائعة
          </p>
        </div>

        <Tabs defaultValue="getting-started" className="max-w-4xl mx-auto">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="getting-started">البداية</TabsTrigger>
            <TabsTrigger value="upload">رفع الملفات</TabsTrigger>
            <TabsTrigger value="processing">المعالجة</TabsTrigger>
            <TabsTrigger value="troubleshooting">حل المشاكل</TabsTrigger>
          </TabsList>

          {/* Getting Started */}
          <TabsContent value="getting-started" className="mt-8">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>البدء مع المنصة</CardTitle>
                  <CardDescription>خطوات سريعة للبدء في استخدام المنصة</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-start space-x-3 space-x-reverse">
                      <Badge className="bg-blue-100 text-blue-800 min-w-6 h-6 flex items-center justify-center">1</Badge>
                      <div>
                        <h4 className="font-medium text-gray-900">إنشاء حساب أو تسجيل الدخول</h4>
                        <p className="text-sm text-gray-600">استخدم البيانات التجريبية: demo@example.com / demo123</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3 space-x-reverse">
                      <Badge className="bg-blue-100 text-blue-800 min-w-6 h-6 flex items-center justify-center">2</Badge>
                      <div>
                        <h4 className="font-medium text-gray-900">رفع ملف صوتي أو مرئي</h4>
                        <p className="text-sm text-gray-600">اختر ملف بصيغة MP3, WAV, MP4, AVI (حد أقصى 100 ميجابايت)</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3 space-x-reverse">
                      <Badge className="bg-blue-100 text-blue-800 min-w-6 h-6 flex items-center justify-center">3</Badge>
                      <div>
                        <h4 className="font-medium text-gray-900">تكوين خيارات الذكاء الاصطناعي</h4>
                        <p className="text-sm text-gray-600">اختر النموذج واللهجة ومستوى تحسين الصوت</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3 space-x-reverse">
                      <Badge className="bg-blue-100 text-blue-800 min-w-6 h-6 flex items-center justify-center">4</Badge>
                      <div>
                        <h4 className="font-medium text-gray-900">مراقبة المعالجة</h4>
                        <p className="text-sm text-gray-600">تابع تقدم المعالجة بالذكاء الاصطناعي في الوقت الفعلي</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3 space-x-reverse">
                      <Badge className="bg-blue-100 text-blue-800 min-w-6 h-6 flex items-center justify-center">5</Badge>
                      <div>
                        <h4 className="font-medium text-gray-900">مراجعة النتائج وتصديرها</h4>
                        <p className="text-sm text-gray-600">راجع النسخة النصية وحمّلها بصيغ مختلفة</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>للحصول على المعالجة الكاملة</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">تشغيل الخدمات الخلفية</h4>
                    <p className="text-sm text-blue-700 mb-3">
                      لتفعيل المعالجة الفعلية بنماذج الذكاء الاصطناعي:
                    </p>
                    <code className="block bg-blue-100 px-3 py-2 rounded text-sm text-blue-900">
                      ./start-full-stack.sh
                    </code>
                    <p className="text-xs text-blue-600 mt-2">
                      سيشغل faster-whisper + pyannote.audio + RNNoise
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Upload Help */}
          <TabsContent value="upload" className="mt-8">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>إرشادات رفع الملفات</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">الصيغ المدعومة</h4>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <h5 className="text-sm font-medium text-blue-900 mb-1">الملفات الصوتية:</h5>
                          <div className="text-sm text-gray-600 space-y-1">
                            <div>• MP3 (مضغوط، جودة جيدة)</div>
                            <div>• WAV (غير مضغوط، أعلى جودة)</div>
                            <div>• FLAC (مضغوط بدون فقدان)</div>
                            <div>• OGG, M4A</div>
                          </div>
                        </div>
                        <div>
                          <h5 className="text-sm font-medium text-blue-900 mb-1">الملفات المرئية:</h5>
                          <div className="text-sm text-gray-600 space-y-1">
                            <div>• MP4 (الأكثر شيوعاً)</div>
                            <div>• AVI, MOV</div>
                            <div>• WMV, FLV</div>
                            <div>• سيتم استخراج الصوت فقط</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">متطلبات الجودة</h4>
                      <div className="text-sm text-gray-600 space-y-1">
                        <div>• جودة صوت واضحة (تجنب الضوضاء الزائدة)</div>
                        <div>• سرعة تحدث طبيعية (ليس سريع جداً أو بطيء جداً)</div>
                        <div>• تجنب الموسيقى الصاخبة أو الأصوات المتداخلة</div>
                        <div>• للهجات المحلية: اختر اللهجة المناسبة في الإعدادات</div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">حدود الرفع</h4>
                      <div className="text-sm text-gray-600 space-y-1">
                        <div>• الحد الأقصى للحجم: 100 ميجابايت (تجريبي) / 500 ميجابايت (مدفوع)</div>
                        <div>• الحد الأقصى للمدة: 3 ساعات</div>
                        <div>• عدد الملفات: 10 ملفات بالتوازي</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Processing Help */}
          <TabsContent value="processing" className="mt-8">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>فهم عملية المعالجة</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">مراحل المعالجة بالذكاء الاصطناعي</h4>
                      <div className="space-y-3">
                        <div className="flex items-center space-x-3 space-x-reverse">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                            <span className="text-xs font-bold text-blue-700">1</span>
                          </div>
                          <div>
                            <h5 className="font-medium">تحسين جودة الصوت</h5>
                            <p className="text-sm text-gray-600">إزالة الضوضاء وتحسين وضوح الصوت</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3 space-x-reverse">
                          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                            <span className="text-xs font-bold text-green-700">2</span>
                          </div>
                          <div>
                            <h5 className="font-medium">تحويل الكلام إلى نص</h5>
                            <p className="text-sm text-gray-600">استخدام نموذج faster-whisper المُحسَّن للعربية</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3 space-x-reverse">
                          <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                            <span className="text-xs font-bold text-purple-700">3</span>
                          </div>
                          <div>
                            <h5 className="font-medium">فصل المتحدثين</h5>
                            <p className="text-sm text-gray-600">تحديد الأصوات المختلفة باستخدام pyannote.audio</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3 space-x-reverse">
                          <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                            <span className="text-xs font-bold text-orange-700">4</span>
                          </div>
                          <div>
                            <h5 className="font-medium">معالجة النص العربي</h5>
                            <p className="text-sm text-gray-600">تصحيح الأخطاء وتحسين التنسيق</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">اختيار النموذج المناسب</h4>
                      <div className="grid md:grid-cols-3 gap-4">
                        <Card className="border-2">
                          <CardHeader>
                            <CardTitle className="text-lg">Large-v3</CardTitle>
                            <Badge className="bg-green-100 text-green-800">أعلى دقة</Badge>
                          </CardHeader>
                          <CardContent>
                            <div className="text-sm space-y-2">
                              <div>دقة: 95%+</div>
                              <div>السرعة: 2-3 دقائق</div>
                              <div>مناسب للملفات المهمة</div>
                            </div>
                          </CardContent>
                        </Card>

                        <Card className="border-2">
                          <CardHeader>
                            <CardTitle className="text-lg">Medium</CardTitle>
                            <Badge className="bg-blue-100 text-blue-800">متوازن</Badge>
                          </CardHeader>
                          <CardContent>
                            <div className="text-sm space-y-2">
                              <div>دقة: 90%+</div>
                              <div>السرعة: 1-2 دقيقة</div>
                              <div>مناسب للاستخدام العام</div>
                            </div>
                          </CardContent>
                        </Card>

                        <Card className="border-2">
                          <CardHeader>
                            <CardTitle className="text-lg">Small</CardTitle>
                            <Badge className="bg-yellow-100 text-yellow-800">أسرع</Badge>
                          </CardHeader>
                          <CardContent>
                            <div className="text-sm space-y-2">
                              <div>دقة: 85%+</div>
                              <div>السرعة: 30-60 ثانية</div>
                              <div>مناسب للمعالجة السريعة</div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Upload Help */}
          <TabsContent value="upload" className="mt-8">
            <Card>
              <CardHeader>
                <CardTitle>مشاكل رفع الملفات</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">الملف لا يُرفع</h4>
                    <div className="text-sm text-gray-600 space-y-1">
                      <div>• تأكد من أن حجم الملف أقل من 100 ميجابايت</div>
                      <div>• تحقق من نوع الملف (MP3, WAV, MP4, AVI مدعومة)</div>
                      <div>• جرب إعادة تحميل الصفحة</div>
                      <div>• تأكد من اتصال الإنترنت</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">رسالة &quot;نوع الملف غير مدعوم&quot;</h4>
                    <div className="text-sm text-gray-600 space-y-1">
                      <div>• استخدم صيغ صوتية: MP3, WAV, FLAC, OGG</div>
                      <div>• أو صيغ مرئية: MP4, AVI, MOV, WMV</div>
                      <div>• تجنب الصيغ المضغوطة أو النادرة</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">تحسين جودة الرفع</h4>
                    <div className="text-sm text-gray-600 space-y-1">
                      <div>• استخدم Wi-Fi بدلاً من الاتصال المحدود</div>
                      <div>• تجنب رفع ملفات متعددة بنفس الوقت</div>
                      <div>• أغلق التطبيقات الأخرى أثناء الرفع</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Processing Help */}
          <TabsContent value="processing" className="mt-8">
            <Card>
              <CardHeader>
                <CardTitle>تحسين نتائج المعالجة</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">لتحسين دقة التفريغ</h4>
                    <div className="text-sm text-gray-600 space-y-1">
                      <div>• اختر النموذج المناسب (large-v3 للدقة العالية)</div>
                      <div>• حدد اللهجة الصحيحة (عراقية، مصرية، خليجية)</div>
                      <div>• أضف مصطلحات مخصصة للأسماء والكلمات المهمة</div>
                      <div>• استخدم مستوى تحسين عالي للملفات الصاخبة</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">لتسريع المعالجة</h4>
                    <div className="text-sm text-gray-600 space-y-1">
                      <div>• استخدم النموذج Small للمعالجة السريعة</div>
                      <div>• اختر مستوى تحسين خفيف</div>
                      <div>• أوقف فصل المتحدثين إذا لم تكن تحتاجه</div>
                      <div>• قسم الملفات الطويلة إلى أجزاء أصغر</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">فصل المتحدثين</h4>
                    <div className="text-sm text-gray-600 space-y-1">
                      <div>• يعمل بشكل أفضل مع الصوت الواضح</div>
                      <div>• تأكد من وجود فترات صمت بين المتحدثين</div>
                      <div>• قد يحتاج تعديل يدوي للمحادثات السريعة</div>
                      <div>• يدعم حتى 10 متحدثين في التسجيل الواحد</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Troubleshooting */}
          <TabsContent value="troubleshooting" className="mt-8">
            <Card>
              <CardHeader>
                <CardTitle>حل المشاكل الشائعة</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div>
                    <h4 className="font-medium text-red-800 mb-2">المعالجة فشلت أو توقفت</h4>
                    <div className="text-sm text-gray-600 space-y-1 mb-3">
                      <div>• تحقق من جودة الملف الصوتي</div>
                      <div>• جرب نموذج أصغر (Medium أو Small)</div>
                      <div>• قلل مستوى تحسين الصوت</div>
                      <div>• تأكد من أن الملف يحتوي على كلام واضح</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-red-800 mb-2">دقة التفريغ منخفضة</h4>
                    <div className="text-sm text-gray-600 space-y-1 mb-3">
                      <div>• اختر نموذج Large-v3 للدقة العالية</div>
                      <div>• حدد اللهجة الصحيحة</div>
                      <div>• أضف مصطلحات مخصصة للكلمات المهمة</div>
                      <div>• استخدم ملفات صوتية عالية الجودة</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-red-800 mb-2">فصل المتحدثين غير دقيق</h4>
                    <div className="text-sm text-gray-600 space-y-1 mb-3">
                      <div>• تأكد من وجود فروق واضحة بين الأصوات</div>
                      <div>• تجنب الحديث المتداخل</div>
                      <div>• يمكن تعديل تسميات المتحدثين يدوياً بعد المعالجة</div>
                      <div>• للمحادثات السريعة، قد تحتاج مراجعة يدوية</div>
                    </div>
                  </div>

                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h4 className="font-medium text-yellow-900 mb-2">للحصول على أفضل النتائج</h4>
                    <div className="text-sm text-yellow-800 space-y-1">
                      <div>• استخدم تسجيلات عالية الجودة (16kHz أو أعلى)</div>
                      <div>• تجنب الضوضاء الخلفية والموسيقى</div>
                      <div>• تكلم بوضوح وسرعة طبيعية</div>
                      <div>• للهجات المحلية، اختر الإعداد المناسب</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Contact Support */}
        <div className="mt-12 text-center">
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle>تحتاج مساعدة إضافية؟</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4">
                فريق الدعم جاهز لمساعدتك في أي استفسار
              </p>
              <div className="flex justify-center gap-4">
                <Button asChild>
                  <Link href="/contact">تواصل معنا</Link>
                </Button>
                <Button variant="outline" asChild>
                  <Link href="/docs">التوثيق الفني</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
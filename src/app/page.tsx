"use client";

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState('features');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 space-x-reverse">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">ع</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">منصة التفريغ الصوتي العربية</h1>
                <p className="text-sm text-gray-600">Arabic STT SaaS Platform</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4 space-x-reverse">
              <Button variant="ghost" asChild>
                <Link href="/multimodal-results">نتائج التحليل المتقدم</Link>
              </Button>
              <Button variant="ghost" asChild>
                <Link href="/auth/login">تسجيل الدخول</Link>
              </Button>
              <Button asChild>
                <Link href="/auth/register">إنشاء حساب</Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 text-center">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <Badge variant="secondary" className="mb-4">
              للاستخدام الداخلي - مُحسَّن للهجات العربية
            </Badge>
            <h1 className="text-5xl font-bold text-gray-900 mb-6 leading-tight">
              منصة التفريغ الصوتي العربية
              <span className="text-blue-600 block">للاستخدام الداخلي</span>
            </h1>
            <p className="text-xl text-gray-700 mb-8 leading-relaxed">
              نظام داخلي لتحويل التسجيلات الصوتية والمرئية العربية إلى نصوص دقيقة باستخدام تقنيات الذكاء الاصطناعي. 
              يدعم اللهجات العربية المختلفة مع محرر متقدم وتصدير متعدد الصيغ.
            </p>
            
            <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4 sm:space-x-reverse mb-8">
              <Button size="lg" className="px-8 py-3" asChild>
                <Link href="/dashboard">الوصول للنظام</Link>
              </Button>
              <Button variant="outline" size="lg" className="px-8 py-3" asChild>
                <Link href="/auth/login">تسجيل الدخول</Link>
              </Button>
            </div>

            {/* Internal Access Info */}
            <div className="max-w-lg mx-auto mb-12 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
              <div className="text-center">
                <h3 className="font-bold text-blue-900 mb-3">🏢 نظام داخلي</h3>
                <div className="bg-white p-4 rounded-lg border space-y-3">
                  <div className="text-sm">
                    <div className="font-medium text-gray-700 mb-1">بيانات الدخول للنظام:</div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">البريد:</span>
                      <code className="bg-blue-100 px-2 py-1 rounded text-xs text-blue-900">admin@company.com</code>
                    </div>
                    <div className="flex justify-between items-center mt-1">
                      <span className="text-gray-600">كلمة المرور:</span>
                      <code className="bg-blue-100 px-2 py-1 rounded text-xs text-blue-900">admin123</code>
                    </div>
                  </div>
                  <Button size="sm" className="w-full" asChild>
                    <Link href="/auth/login">دخول للنظام</Link>
                  </Button>
                </div>
                <p className="text-xs text-blue-700 mt-3">
                  🔒 نظام آمن للاستخدام الداخلي فقط
                </p>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-2xl mx-auto">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">95%+</div>
                <div className="text-sm text-gray-600">دقة التفريغ</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">5+</div>
                <div className="text-sm text-gray-600">لهجات عربية</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">AI</div>
                <div className="text-sm text-gray-600">معالجة ذكية</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">🔒</div>
                <div className="text-sm text-gray-600">استخدام داخلي</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                ميزات متقدمة للتفريغ الصوتي العربي
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                منصة شاملة تجمع بين أحدث تقنيات الذكاء الاصطناعي والتصميم المُحسَّن للغة العربية
              </p>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="features">المميزات الأساسية</TabsTrigger>
                <TabsTrigger value="editor">المحرر المتقدم</TabsTrigger>
                <TabsTrigger value="dialects">اللهجات العربية</TabsTrigger>
                <TabsTrigger value="export">التصدير والتكامل</TabsTrigger>
              </TabsList>

              <TabsContent value="features" className="mt-8">
                <div className="grid md:grid-cols-3 gap-8">
                  <Card>
                    <CardHeader>
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                        <span className="text-2xl">🎤</span>
                      </div>
                      <CardTitle>تفريغ صوتي دقيق</CardTitle>
                      <CardDescription>
                        تقنية Whisper المُحسَّنة للعربية مع دقة تصل إلى 95%
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2 text-sm text-gray-600">
                        <li>• معالجة الملفات الصوتية والمرئية</li>
                        <li>• تحسين جودة الصوت تلقائياً</li>
                        <li>• كشف النشاط الصوتي المتقدم</li>
                        <li>• دعم ملفات متعددة الصيغ</li>
                      </ul>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                        <span className="text-2xl">👥</span>
                      </div>
                      <CardTitle>فصل المتحدثين</CardTitle>
                      <CardDescription>
                        تحديد المتحدثين تلقائياً وتسمية الأصوات المختلفة
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2 text-sm text-gray-600">
                        <li>• تحديد عدد المتحدثين تلقائياً</li>
                        <li>• تسمية مخصصة للمتحدثين</li>
                        <li>• إحصائيات وقت التحدث</li>
                        <li>• فصل دقيق للأصوات المتداخلة</li>
                      </ul>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                        <span className="text-2xl">⚡</span>
                      </div>
                      <CardTitle>معالجة سريعة</CardTitle>
                      <CardDescription>
                        معالجة فائقة السرعة مع دعم GPU والمعالجة المتوازية
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2 text-sm text-gray-600">
                        <li>• معالجة أسرع من الوقت الحقيقي</li>
                        <li>• دعم GPU لتسريع المعالجة</li>
                        <li>• معالجة ملفات متعددة بالتوازي</li>
                        <li>• تحديثات حية لحالة المعالجة</li>
                      </ul>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="editor" className="mt-8">
                <div className="grid md:grid-cols-2 gap-8 items-center">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-4">
                      محرر متقدم مع دعم كامل للعربية
                    </h3>
                    <div className="space-y-4">
                      <div className="flex items-start space-x-3 space-x-reverse">
                        <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                          <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">موجة صوتية تفاعلية</h4>
                          <p className="text-sm text-gray-600">تصور الصوت مع إمكانية التنقل والتحرير المباشر</p>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3 space-x-reverse">
                        <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                          <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">تحرير مباشر</h4>
                          <p className="text-sm text-gray-600">تحرير النص مباشرة مع حفظ تلقائي ومتابعة التغييرات</p>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3 space-x-reverse">
                        <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                          <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">بحث واستبدال</h4>
                          <p className="text-sm text-gray-600">أدوات بحث متقدمة مع دعم التعبيرات النمطية العربية</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-100 rounded-lg p-6 text-center">
                    <div className="text-gray-500 mb-4">معاينة المحرر</div>
                    <div className="bg-white rounded border p-4 text-right text-sm">
                      <div className="text-blue-600 mb-2">المتحدث الأول (00:15)</div>
                      <p className="text-gray-800 leading-relaxed">
                        مرحباً بكم في هذا الاجتماع المهم. سنناقش اليوم خطة العمل الجديدة...
                      </p>
                      <div className="text-green-600 mb-2 mt-4">المتحدث الثاني (00:45)</div>
                      <p className="text-gray-800 leading-relaxed">
                        شكراً لك على هذا العرض المفصل. لدي بعض الملاحظات على النقاط المطروحة...
                      </p>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="dialects" className="mt-8">
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    دعم شامل للهجات العربية
                  </h3>
                  <p className="text-gray-600 max-w-2xl mx-auto">
                    تم تحسين المنصة خصيصاً للتعامل مع تنوع اللهجات العربية وخصائص كل منطقة
                  </p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <Card className="text-center">
                    <CardHeader>
                      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">🇮🇶</span>
                      </div>
                      <CardTitle>اللهجة العراقية</CardTitle>
                      <CardDescription>تحسين خاص للهجة العراقية</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="text-sm text-gray-600 space-y-1">
                        <div>دقة: 92%+</div>
                        <div>خصائص: شلونك، شكو ماكو، وين</div>
                        <div>مُحسَّن للنبرة والإيقاع العراقي</div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="text-center">
                    <CardHeader>
                      <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">📖</span>
                      </div>
                      <CardTitle>العربية الفصحى</CardTitle>
                      <CardDescription>أعلى دقة للنصوص الرسمية</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="text-sm text-gray-600 space-y-1">
                        <div>دقة: 95%+</div>
                        <div>مثالي للأخبار والمحاضرات</div>
                        <div>تحسين القواعد والإعراب</div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="text-center">
                    <CardHeader>
                      <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">🇪🇬</span>
                      </div>
                      <CardTitle>اللهجة المصرية</CardTitle>
                      <CardDescription>دعم اللهجة المصرية الشائعة</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="text-sm text-gray-600 space-y-1">
                        <div>دقة: 90%+</div>
                        <div>تحسين للإيقاع المصري</div>
                        <div>دعم التعبيرات المحلية</div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="export" className="mt-8">
                <div className="grid md:grid-cols-2 gap-8">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-6">
                      تصدير متعدد الصيغ
                    </h3>
                    <div className="space-y-6">
                      <div className="flex items-center space-x-4 space-x-reverse">
                        <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                          <span className="font-mono text-sm font-bold text-red-700">TXT</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">نص عادي</h4>
                          <p className="text-sm text-gray-600">للاستخدام العام والتحرير</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4 space-x-reverse">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <span className="font-mono text-sm font-bold text-blue-700">SRT</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">ترجمات للفيديو</h4>
                          <p className="text-sm text-gray-600">متوافق مع جميع برامج المونتاج</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4 space-x-reverse">
                        <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                          <span className="font-mono text-sm font-bold text-green-700">VTT</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">ترجمات الويب</h4>
                          <p className="text-sm text-gray-600">للمواقع ومشغلات الفيديو</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4 space-x-reverse">
                        <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                          <span className="font-mono text-sm font-bold text-purple-700">DOC</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">مستند Word</h4>
                          <p className="text-sm text-gray-600">تنسيق احترافي للتقارير</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-6">
                      تكامل مع الأنظمة
                    </h3>
                    <div className="space-y-6">
                      <div className="flex items-center space-x-4 space-x-reverse">
                        <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                          <span className="text-xl">🔗</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">واجهة برمجية REST</h4>
                          <p className="text-sm text-gray-600">تكامل سهل مع أنظمتك الحالية</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4 space-x-reverse">
                        <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                          <span className="text-xl">📡</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Webhooks</h4>
                          <p className="text-sm text-gray-600">إشعارات فورية عند اكتمال المعالجة</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4 space-x-reverse">
                        <div className="w-10 h-10 bg-pink-100 rounded-lg flex items-center justify-center">
                          <span className="text-xl">💾</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">تخزين سحابي</h4>
                          <p className="text-sm text-gray-600">ربط مع خدمات التخزين الشائعة</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4 space-x-reverse">
                        <div className="w-10 h-10 bg-teal-100 rounded-lg flex items-center justify-center">
                          <span className="text-xl">🎬</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">برامج المونتاج</h4>
                          <p className="text-sm text-gray-600">تصدير متوافق مع Adobe وDaVinci</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </section>

      {/* Internal System Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              نظام التفريغ الصوتي الداخلي
            </h2>
            <p className="text-lg text-gray-600 mb-12">
              أداة قوية للاستخدام الداخلي لتحويل التسجيلات الصوتية إلى نصوص دقيقة
            </p>

            <div className="grid md:grid-cols-2 gap-8">
              <Card>
                <CardHeader>
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
                    <span className="text-2xl">🎤</span>
                  </div>
                  <CardTitle className="text-center">معالجة متقدمة</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 text-sm text-gray-600">
                    <li>• تفريغ صوتي بدقة عالية (95%+)</li>
                    <li>• دعم اللهجات العربية المختلفة</li>
                    <li>• فصل المتحدثين تلقائياً</li>
                    <li>• معالجة بالذكاء الاصطناعي</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
                    <span className="text-2xl">🔒</span>
                  </div>
                  <CardTitle className="text-center">أمان وخصوصية</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 text-sm text-gray-600">
                    <li>• معالجة محلية آمنة</li>
                    <li>• لا توجد خدمات خارجية</li>
                    <li>• تحكم كامل في البيانات</li>
                    <li>• امتثال للمعايير الأمنية</li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Access Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-4">
            الوصول للنظام الداخلي
          </h2>
          <p className="text-xl mb-8 text-blue-100 max-w-2xl mx-auto">
            نظام آمن ومحلي لمعالجة التسجيلات الصوتية وتحويلها إلى نصوص دقيقة
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4 sm:space-x-reverse">
            <Button size="lg" variant="secondary" className="px-8 py-3" asChild>
              <Link href="/dashboard">الوصول للنظام</Link>
            </Button>
            <Button size="lg" variant="outline" className="px-8 py-3 text-white border-white hover:bg-white hover:text-blue-600" asChild>
              <Link href="/help">دليل الاستخدام</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center space-x-2 space-x-reverse mb-4">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">ع</span>
                </div>
                <span className="font-bold text-lg">نظام التفريغ العربي الداخلي</span>
              </div>
              <p className="text-gray-400 text-sm">
                نظام داخلي متطور لتحويل التسجيلات الصوتية والمرئية العربية إلى نصوص دقيقة باستخدام الذكاء الاصطناعي.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-4">النظام</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link href="/dashboard" className="hover:text-white transition-colors">لوحة التحكم</Link></li>
                <li><Link href="/upload" className="hover:text-white transition-colors">رفع الملفات</Link></li>
                <li><Link href="/docs" className="hover:text-white transition-colors">التوثيق</Link></li>
                <li><Link href="/help" className="hover:text-white transition-colors">المساعدة</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">الدعم الفني</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link href="/help" className="hover:text-white transition-colors">دليل الاستخدام</Link></li>
                <li><Link href="/docs" className="hover:text-white transition-colors">التوثيق الفني</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">الدعم التقني</Link></li>
                <li><span className="text-gray-500">نظام داخلي آمن</span></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-sm text-gray-400">
            <p>🏢 نظام التفريغ الصوتي العربي - للاستخدام الداخلي</p>
            <p className="mt-2">🔒 معالجة محلية آمنة بدون خدمات خارجية</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
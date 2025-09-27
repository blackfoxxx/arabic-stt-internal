"use client";

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
    type: 'support'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate form submission
    setTimeout(() => {
      setSubmitted(true);
      setIsSubmitting(false);
      console.log('Contact form submitted:', formData);
    }, 1000);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <Card className="max-w-md">
          <CardHeader className="text-center">
            <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-white text-2xl">✓</span>
            </div>
            <CardTitle className="text-xl text-green-800">تم إرسال رسالتك!</CardTitle>
            <CardDescription>سنتواصل معك قريباً</CardDescription>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <p className="text-sm text-gray-600">
              شكراً لتواصلك معنا. سيقوم فريق الدعم بالرد عليك خلال 24 ساعة.
            </p>
            <div className="space-y-2">
              <Button asChild className="w-full">
                <Link href="/dashboard">العودة إلى لوحة التحكم</Link>
              </Button>
              <Button variant="outline" asChild className="w-full">
                <Link href="/">الصفحة الرئيسية</Link>
              </Button>
            </div>
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
            <div className="flex items-center space-x-4 space-x-reverse">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">ع</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">تواصل معنا</h1>
                <p className="text-sm text-gray-600">نحن هنا لمساعدتك</p>
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
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              تواصل مع فريق الدعم
            </h1>
            <p className="text-lg text-gray-600">
              لدينا فريق خبراء جاهز لمساعدتك في أي استفسار حول المنصة
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Contact Form */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>إرسال رسالة</CardTitle>
                  <CardDescription>
                    اكتب استفسارك وسنرد عليك في أقرب وقت
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="name">الاسم الكامل</Label>
                        <Input
                          id="name"
                          name="name"
                          value={formData.name}
                          onChange={handleInputChange}
                          placeholder="أحمد محمد"
                          required
                          className="text-right"
                          dir="rtl"
                        />
                      </div>
                      <div>
                        <Label htmlFor="email">البريد الإلكتروني</Label>
                        <Input
                          id="email"
                          name="email"
                          type="email"
                          value={formData.email}
                          onChange={handleInputChange}
                          placeholder="ahmed@example.com"
                          required
                          className="text-left"
                          dir="ltr"
                        />
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="type">نوع الاستفسار</Label>
                      <Select 
                        value={formData.type} 
                        onValueChange={(value) => setFormData(prev => ({ ...prev, type: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="اختر نوع الاستفسار" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="support">دعم فني</SelectItem>
                          <SelectItem value="billing">الفوترة والاشتراكات</SelectItem>
                          <SelectItem value="feature">طلب ميزة جديدة</SelectItem>
                          <SelectItem value="bug">الإبلاغ عن خطأ</SelectItem>
                          <SelectItem value="sales">الاستفسارات التجارية</SelectItem>
                          <SelectItem value="other">أخرى</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="subject">الموضوع</Label>
                      <Input
                        id="subject"
                        name="subject"
                        value={formData.subject}
                        onChange={handleInputChange}
                        placeholder="موضوع رسالتك"
                        required
                        className="text-right"
                        dir="rtl"
                      />
                    </div>

                    <div>
                      <Label htmlFor="message">الرسالة</Label>
                      <Textarea
                        id="message"
                        name="message"
                        value={formData.message}
                        onChange={handleInputChange}
                        placeholder="اكتب رسالتك هنا..."
                        required
                        rows={6}
                        className="text-right"
                        dir="rtl"
                      />
                    </div>

                    <Button 
                      type="submit" 
                      className="w-full"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? (
                        <div className="flex items-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          <span>جاري الإرسال...</span>
                        </div>
                      ) : (
                        'إرسال الرسالة'
                      )}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Contact Info */}
            <div className="space-y-6">
              {/* Contact Details */}
              <Card>
                <CardHeader>
                  <CardTitle>معلومات التواصل</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center space-x-3 space-x-reverse">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <span className="text-xl">📧</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">البريد الإلكتروني</h4>
                      <p className="text-sm text-gray-600">support@arabicstt.com</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 space-x-reverse">
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <span className="text-xl">💬</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">الدردشة المباشرة</h4>
                      <p className="text-sm text-gray-600">متاح من 9 صباحاً إلى 6 مساءً</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 space-x-reverse">
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <span className="text-xl">📞</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">الهاتف</h4>
                      <p className="text-sm text-gray-600">+966-11-123-4567</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Response Times */}
              <Card>
                <CardHeader>
                  <CardTitle>أوقات الاستجابة</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">الدعم الفني:</span>
                    <span className="text-sm bg-gray-100 px-2 py-1 rounded">24 ساعة</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">الاستفسارات التجارية:</span>
                    <span className="text-sm bg-gray-100 px-2 py-1 rounded">48 ساعة</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">الطلبات العاجلة:</span>
                    <span className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">4 ساعات</span>
                  </div>
                </CardContent>
              </Card>

              {/* Demo Platform Info */}
              <Alert>
                <AlertDescription>
                  <div className="text-center">
                    <strong>نسخة تجريبية</strong>
                    <p className="text-sm mt-1">
                      هذا نموذج لصفحة التواصل. في النسخة الفعلية، ستتصل بنظام إدارة التذاكر.
                    </p>
                  </div>
                </AlertDescription>
              </Alert>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
"use client";

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    organizationName: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('كلمات المرور غير متطابقة');
      setIsLoading(false);
      return;
    }

    if (!agreedToTerms) {
      setError('يجب الموافقة على شروط الاستخدام');
      setIsLoading(false);
      return;
    }

    try {
      // TODO: Implement actual API call when backend is running
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          first_name: formData.firstName,
          last_name: formData.lastName,
          organization_name: formData.organizationName
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess(true);
        // Store token and redirect
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 2000);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'فشل إنشاء الحساب');
      }
    } catch (err) {
      setError('حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.');
      console.error('Registration error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-emerald-50 p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-white text-2xl">✓</span>
            </div>
            <CardTitle className="text-xl text-green-800">تم إنشاء الحساب بنجاح!</CardTitle>
            <CardDescription>
              مرحباً بك في منصة التفريغ الصوتي العربية
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-sm text-gray-600 mb-4">
              سيتم توجيهك إلى لوحة التحكم خلال ثوانِ قليلة...
            </p>
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-500 mx-auto"></div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">ع</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            إنشاء حساب جديد
          </h1>
          <p className="text-gray-600">
            انضم إلى منصة التفريغ الصوتي العربية
          </p>
        </div>

        {/* Registration Form */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl text-center">حساب جديد</CardTitle>
            <CardDescription className="text-center">
              أنشئ حساباً للوصول إلى النظام الداخلي
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Personal Information */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="firstName">الاسم الأول</Label>
                  <Input
                    id="firstName"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    placeholder="أحمد"
                    required
                    disabled={isLoading}
                    className="text-right"
                    dir="rtl"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName">اسم العائلة</Label>
                  <Input
                    id="lastName"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    placeholder="المحمد"
                    required
                    disabled={isLoading}
                    className="text-right"
                    dir="rtl"
                  />
                </div>
              </div>

              {/* Organization */}
              <div className="space-y-2">
                <Label htmlFor="organizationName">اسم المؤسسة</Label>
                <Input
                  id="organizationName"
                  name="organizationName"
                  value={formData.organizationName}
                  onChange={handleInputChange}
                  placeholder="شركة التقنية المتقدمة"
                  required
                  disabled={isLoading}
                  className="text-right"
                  dir="rtl"
                />
              </div>

              {/* Email */}
              <div className="space-y-2">
                <Label htmlFor="email">البريد الإلكتروني</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="example@domain.com"
                  required
                  disabled={isLoading}
                  className="text-left"
                  dir="ltr"
                />
              </div>

              {/* Password */}
              <div className="space-y-2">
                <Label htmlFor="password">كلمة المرور</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="••••••••"
                  required
                  disabled={isLoading}
                  className="text-left"
                  dir="ltr"
                />
                <p className="text-xs text-gray-500">
                  يجب أن تحتوي على 8 أحرف على الأقل
                </p>
              </div>

              {/* Confirm Password */}
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">تأكيد كلمة المرور</Label>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  placeholder="••••••••"
                  required
                  disabled={isLoading}
                  className="text-left"
                  dir="ltr"
                />
              </div>

              {/* Terms Agreement */}
              <div className="flex items-center space-x-2 space-x-reverse">
                <Checkbox
                  id="terms"
                  checked={agreedToTerms}
                  onCheckedChange={(checked) => setAgreedToTerms(checked as boolean)}
                  disabled={isLoading}
                />
                <Label htmlFor="terms" className="text-sm">
                  أوافق على{' '}
                  <Link href="/terms" className="text-blue-600 hover:underline">
                    شروط الاستخدام
                  </Link>
                  {' '}و{' '}
                  <Link href="/privacy" className="text-blue-600 hover:underline">
                    سياسة الخصوصية
                  </Link>
                </Label>
              </div>

              <Button 
                type="submit" 
                className="w-full"
                disabled={isLoading || !agreedToTerms}
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>جاري إنشاء الحساب...</span>
                  </div>
                ) : (
                  'إنشاء حساب جديد'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                لديك حساب بالفعل؟{' '}
                <Link 
                  href="/auth/login" 
                  className="text-blue-600 hover:text-blue-800 font-medium hover:underline"
                >
                  تسجيل الدخول
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Internal System Features */}
        <div className="mt-6 p-4 bg-blue-50 backdrop-blur-sm rounded-lg border border-blue-200">
          <h3 className="font-medium text-blue-900 mb-3 text-center">🏢 مميزات النظام الداخلي:</h3>
          <div className="space-y-2 text-sm">
            <div className="flex items-center space-x-3 space-x-reverse">
              <div className="w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 text-xs">✓</span>
              </div>
              <span className="text-blue-700">معالجة بلا حدود للاستخدام الداخلي</span>
            </div>
            <div className="flex items-center space-x-3 space-x-reverse">
              <div className="w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 text-xs">✓</span>
              </div>
              <span className="text-blue-700">دعم كامل للهجات العربية (عراقية، مصرية، خليجية)</span>
            </div>
            <div className="flex items-center space-x-3 space-x-reverse">
              <div className="w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 text-xs">✓</span>
              </div>
              <span className="text-blue-700">محرر متقدم مع موجة صوتية وتحرير مباشر</span>
            </div>
            <div className="flex items-center space-x-3 space-x-reverse">
              <div className="w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 text-xs">✓</span>
              </div>
              <span className="text-blue-700">تصدير آمن بجميع الصيغ (TXT, SRT, VTT, DOCX)</span>
            </div>
            <div className="flex items-center space-x-3 space-x-reverse">
              <div className="w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 text-xs">✓</span>
              </div>
              <span className="text-blue-700">أمان كامل - معالجة محلية بدون خدمات خارجية</span>
            </div>
          </div>
        </div>

        {/* Back to Home */}
        <div className="mt-8 text-center">
          <Link 
            href="/" 
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-800"
          >
            ← العودة إلى الصفحة الرئيسية
          </Link>
        </div>
      </div>
    </div>
  );
}
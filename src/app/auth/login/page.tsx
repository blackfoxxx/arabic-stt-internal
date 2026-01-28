"use client";

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function LoginPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // TODO: Implement actual API call when backend is running
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        const safeLocalStorage = (typeof window !== 'undefined' && window.localStorage) ? window.localStorage : null;
        if (safeLocalStorage) {
          safeLocalStorage.setItem('access_token', data.access_token);
          safeLocalStorage.setItem('refresh_token', data.refresh_token);
        }
        window.location.href = '/dashboard';
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'فشل تسجيل الدخول');
      }
    } catch (err) {
      setError('حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.');
      console.error('Login error:', err);
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

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">ع</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            تسجيل الدخول
          </h1>
          <p className="text-gray-600">
            ادخل إلى منصة التفريغ الصوتي العربية
          </p>
        </div>

        {/* Login Form */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl text-center">تسجيل الدخول</CardTitle>
            <CardDescription className="text-center">
              أدخل بياناتك للوصول إلى حسابك
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

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
              </div>

              <div className="flex items-center justify-between text-sm">
                <Link 
                  href="/auth/forgot-password" 
                  className="text-blue-600 hover:text-blue-800 hover:underline"
                >
                  نسيت كلمة المرور؟
                </Link>
              </div>

              <Button 
                type="submit" 
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>جاري تسجيل الدخول...</span>
                  </div>
                ) : (
                  'تسجيل الدخول'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                ليس لديك حساب؟{' '}
                <Link 
                  href="/auth/register" 
                  className="text-blue-600 hover:text-blue-800 font-medium hover:underline"
                >
                  إنشاء حساب جديد
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Internal System Credentials */}
        <div className="mt-6 p-4 bg-blue-50 rounded-lg text-center border border-blue-200">
          <h3 className="font-medium text-blue-900 mb-3">🏢 نظام داخلي</h3>
          <div className="bg-white p-3 rounded border space-y-2">
            <div className="text-sm">
              <strong>البريد الإلكتروني:</strong>
              <code className="block bg-gray-100 px-2 py-1 rounded mt-1 text-blue-900">
                admin@company.com
              </code>
            </div>
            <div className="text-sm">
              <strong>كلمة المرور:</strong>
              <code className="block bg-gray-100 px-2 py-1 rounded mt-1 text-blue-900">
                admin123
              </code>
            </div>
          </div>
          <p className="text-xs text-blue-700 mt-3">
            🔒 للاستخدام الداخلي فقط - نظام آمن ومحلي
          </p>
        </div>

        {/* Full Backend Notice */}
        <div className="mt-4 p-4 bg-blue-50 rounded-lg text-center">
          <h4 className="font-medium text-blue-900 mb-2">🚀 تفعيل المعالجة الكاملة</h4>
          <p className="text-sm text-blue-700 mb-2">
            لتشغيل المعالجة الفعلية بالذكاء الاصطناعي (faster-whisper + pyannote.audio):
          </p>
          <code className="bg-blue-100 px-2 py-1 rounded text-xs text-blue-800">
            ./start-full-stack.sh
          </code>
          <p className="text-xs text-blue-600 mt-2">
            سيبدأ تشغيل النماذج الحقيقية للذكاء الاصطناعي
          </p>
        </div>

        {/* Features Preview */}
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500 mb-3">المميزات المتاحة في المنصة:</p>
          <div className="flex justify-center gap-4 text-xs text-gray-600">
            <span>🎤 تفريغ صوتي دقيق</span>
            <span>👥 فصل المتحدثين</span>
            <span>✏️ محرر متقدم</span>
            <span>📄 تصدير متعدد</span>
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
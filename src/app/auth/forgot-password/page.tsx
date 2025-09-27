"use client";

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // TODO: Implement actual API call when backend is running
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (response.ok) {
        setSuccess(true);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'فشل إرسال رابط إعادة تعيين كلمة المرور');
      }
    } catch (err) {
      setError('حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.');
      console.error('Forgot password error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-emerald-50 p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-white text-2xl">📧</span>
            </div>
            <CardTitle className="text-xl text-green-800">تم إرسال الرابط!</CardTitle>
            <CardDescription>
              تحقق من بريدك الإلكتروني
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-sm text-gray-600 mb-4">
              تم إرسال رابط إعادة تعيين كلمة المرور إلى عنوان بريدك الإلكتروني.
              يرجى التحقق من البريد الوارد وصندوق الرسائل المحذوفة.
            </p>
            <div className="space-y-3">
              <Button asChild className="w-full">
                <Link href="/auth/login">العودة لتسجيل الدخول</Link>
              </Button>
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => {
                  setSuccess(false);
                  setEmail('');
                }}
              >
                إرسال رابط آخر
              </Button>
            </div>
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
            نسيت كلمة المرور؟
          </h1>
          <p className="text-gray-600">
            سنرسل لك رابط إعادة تعيين كلمة المرور
          </p>
        </div>

        {/* Forgot Password Form */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl text-center">إعادة تعيين كلمة المرور</CardTitle>
            <CardDescription className="text-center">
              أدخل بريدك الإلكتروني لإرسال رابط إعادة التعيين
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
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="example@domain.com"
                  required
                  disabled={isLoading}
                  className="text-left"
                  dir="ltr"
                />
                <p className="text-xs text-gray-500">
                  سنرسل رابط إعادة تعيين كلمة المرور إلى هذا العنوان
                </p>
              </div>

              <Button 
                type="submit" 
                className="w-full"
                disabled={isLoading || !email}
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>جاري الإرسال...</span>
                  </div>
                ) : (
                  'إرسال رابط إعادة التعيين'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                تذكرت كلمة المرور؟{' '}
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

        {/* Help Info */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium text-gray-900 mb-2 text-center">تحتاج مساعدة؟</h3>
          <div className="space-y-2 text-sm text-gray-600 text-center">
            <p>• تأكد من صحة عنوان البريد الإلكتروني</p>
            <p>• تحقق من صندوق الرسائل المحذوفة (Spam)</p>
            <p>• قد يستغرق وصول الرسالة بضع دقائق</p>
          </div>
          <div className="mt-3 text-center">
            <Link 
              href="/contact" 
              className="text-sm text-blue-600 hover:text-blue-800 hover:underline"
            >
              تواصل مع الدعم الفني
            </Link>
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
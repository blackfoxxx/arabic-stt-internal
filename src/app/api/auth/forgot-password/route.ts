import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email } = body;

    // Basic validation
    if (!email) {
      return NextResponse.json(
        { 
          error: 'validation_error',
          message: 'البريد الإلكتروني مطلوب' 
        },
        { status: 400 }
      );
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { 
          error: 'validation_error',
          message: 'البريد الإلكتروني غير صحيح' 
        },
        { status: 400 }
      );
    }

    // For demo purposes, always return success
    // In production, this would:
    // 1. Check if user exists in database
    // 2. Generate password reset token
    // 3. Send email with reset link
    // 4. Store token in database with expiration

    /*
    const backendResponse = await fetch(`${process.env.API_URL}/v1/auth/forgot-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    if (backendResponse.ok) {
      const data = await backendResponse.json();
      return NextResponse.json(data);
    } else {
      const errorData = await backendResponse.json();
      return NextResponse.json(errorData, { status: backendResponse.status });
    }
    */

    // Demo response
    return NextResponse.json({
      message: 'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني',
      status: 'success'
    });

  } catch (error) {
    console.error('Forgot password API error:', error);
    return NextResponse.json(
      { 
        error: 'server_error',
        message: 'حدث خطأ في الخادم' 
      },
      { status: 500 }
    );
  }
}
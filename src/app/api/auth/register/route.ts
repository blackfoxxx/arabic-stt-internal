import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password, first_name, last_name, organization_name } = body;

    // Basic validation
    if (!email || !password || !first_name || !last_name || !organization_name) {
      return NextResponse.json(
        { 
          error: 'validation_error',
          message: 'جميع الحقول مطلوبة' 
        },
        { status: 400 }
      );
    }

    // Password validation
    if (password.length < 8) {
      return NextResponse.json(
        { 
          error: 'validation_error',
          message: 'كلمة المرور يجب أن تحتوي على 8 أحرف على الأقل' 
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

    // Demo registration - simulate successful registration
    if (email && password) {
      // Generate demo tokens
      const accessToken = 'demo_access_token_' + Date.now();
      const refreshToken = 'demo_refresh_token_' + Date.now();
      
      // Generate demo user ID
      const userId = 'user_' + Date.now();
      const orgId = 'org_' + Date.now();
      
      return NextResponse.json({
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: 'bearer',
        expires_in: 1800,
        user: {
          id: userId,
          email: email,
          first_name: first_name,
          last_name: last_name,
          role: 'owner',
          is_active: true,
          email_verified_at: null,
          organization_id: orgId,
          organization_name: organization_name,
          created_at: new Date().toISOString()
        }
      });
    }

    // For production, this would make a request to the FastAPI backend:
    /*
    const backendResponse = await fetch(`${process.env.API_URL}/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
        first_name,
        last_name,
        organization_name
      }),
    });

    if (backendResponse.ok) {
      const data = await backendResponse.json();
      return NextResponse.json(data);
    } else {
      const errorData = await backendResponse.json();
      return NextResponse.json(errorData, { status: backendResponse.status });
    }
    */

    return NextResponse.json(
      { 
        error: 'demo_mode',
        message: 'في وضع التجربة - يرجى تشغيل الخدمات الخلفية للتسجيل الفعلي' 
      },
      { status: 400 }
    );

  } catch (error) {
    console.error('Registration API error:', error);
    return NextResponse.json(
      { 
        error: 'server_error',
        message: 'حدث خطأ في الخادم' 
      },
      { status: 500 }
    );
  }
}
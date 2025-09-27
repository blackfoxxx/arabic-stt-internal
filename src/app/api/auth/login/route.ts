import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = body;

    // Basic validation
    if (!email || !password) {
      return NextResponse.json(
        { 
          error: 'validation_error',
          message: 'البريد الإلكتروني وكلمة المرور مطلوبان' 
        },
        { status: 400 }
      );
    }

    // Internal system authentication
    if ((email === 'admin@company.com' && password === 'admin123') ||
        (email === 'demo@example.com' && password === 'demo123')) {
      // Generate tokens
      const accessToken = 'internal_access_token_' + Date.now();
      const refreshToken = 'internal_refresh_token_' + Date.now();
      
      const isAdmin = email === 'admin@company.com';
      
      return NextResponse.json({
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: 'bearer',
        expires_in: 1800,
        user: {
          id: isAdmin ? 'admin-user-id' : 'internal-user-id',
          email: email,
          first_name: isAdmin ? 'مدير' : 'مستخدم',
          last_name: isAdmin ? 'النظام' : 'داخلي',
          role: isAdmin ? 'admin' : 'user',
          is_active: true,
          organization_id: 'internal-org-id',
          organization_name: 'النظام الداخلي'
        }
      });
    }

    // For production, this would make a request to the FastAPI backend:
    /*
    const backendResponse = await fetch(`${process.env.API_URL}/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (backendResponse.ok) {
      const data = await backendResponse.json();
      return NextResponse.json(data);
    } else {
      const errorData = await backendResponse.json();
      return NextResponse.json(errorData, { status: backendResponse.status });
    }
    */

    // Default error for internal system
    return NextResponse.json(
      { 
        error: 'invalid_credentials',
        message: 'بيانات الدخول غير صحيحة. استخدم admin@company.com / admin123 للنظام الداخلي' 
      },
      { status: 401 }
    );

  } catch (error) {
    console.error('Login API error:', error);
    return NextResponse.json(
      { 
        error: 'server_error',
        message: 'حدث خطأ في الخادم' 
      },
      { status: 500 }
    );
  }
}
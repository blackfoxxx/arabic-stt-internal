import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    service: 'Arabic STT SaaS Frontend',
    version: '1.0.0'
  });
}
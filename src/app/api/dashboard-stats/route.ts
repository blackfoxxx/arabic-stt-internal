import { NextRequest, NextResponse } from 'next/server';
import { statisticsStorage } from '@/lib/statistics-storage';

export async function GET(request: NextRequest) {
  try {
    // Get real statistics from storage
    const stats = statisticsStorage.getStatistics();
    const recentJobs = statisticsStorage.getRecentJobs(5);
    
    // Convert job records to dashboard format
    const dashboardJobs = recentJobs.map(job => ({
      id: job.id,
      filename: job.filename,
      status: job.status,
      progress: job.progress,
      duration: job.duration,
      createdAt: job.createdAt,
      transcriptId: job.transcriptId
    }));

    // Calculate additional metrics
    const processingJobs = statisticsStorage.getJobsByStatus('processing');
    const pendingJobs = statisticsStorage.getJobsByStatus('pending');
    
    const dashboardStats = {
      totalFiles: stats.totalFiles,
      totalMinutes: stats.totalMinutes,
      completedJobs: stats.completedJobs,
      pendingJobs: stats.pendingJobs + processingJobs.length, // Include processing as pending
      monthlyUsage: 0, // No usage limits for internal system
      monthlyLimit: 0, // No limits for internal system
      averageProcessingTime: stats.averageProcessingTime,
      totalProcessingTime: stats.totalProcessingTime,
      lastUpdated: stats.lastUpdated
    };

    console.log('📊 Dashboard stats requested:', {
      totalFiles: dashboardStats.totalFiles,
      totalMinutes: dashboardStats.totalMinutes,
      completedJobs: dashboardStats.completedJobs,
      recentJobs: dashboardJobs.length
    });

    return NextResponse.json({
      success: true,
      stats: dashboardStats,
      recentJobs: dashboardJobs,
      user: {
        id: 'internal-admin',
        name: 'مدير النظام',
        email: 'admin@company.com',
        organization: 'النظام الداخلي',
        plan: 'نظام داخلي'
      }
    });

  } catch (error) {
    console.error('Dashboard stats error:', error);
    
    // Return fallback data if there's an error
    return NextResponse.json({
      success: true,
      stats: {
        totalFiles: 0,
        totalMinutes: 0,
        completedJobs: 0,
        pendingJobs: 0,
        monthlyUsage: 0,
        monthlyLimit: 0,
        averageProcessingTime: 0,
        totalProcessingTime: 0,
        lastUpdated: new Date().toISOString()
      },
      recentJobs: [],
      user: {
        id: 'internal-admin',
        name: 'مدير النظام',
        email: 'admin@company.com',
        organization: 'النظام الداخلي',
        plan: 'نظام داخلي'
      }
    });
  }
}

// POST endpoint to initialize demo data
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    if (body.action === 'import_demo_data') {
      statisticsStorage.importDemoData();
      
      return NextResponse.json({
        success: true,
        message: 'تم استيراد البيانات التجريبية بنجاح',
        stats: statisticsStorage.getStatistics()
      });
    }
    
    if (body.action === 'clear_data') {
      statisticsStorage.clearAll();
      
      return NextResponse.json({
        success: true,
        message: 'تم مسح جميع البيانات',
        stats: statisticsStorage.getStatistics()
      });
    }

    return NextResponse.json(
      { error: 'إجراء غير مدعوم' },
      { status: 400 }
    );

  } catch (error) {
    console.error('Dashboard stats POST error:', error);
    return NextResponse.json(
      { error: 'حدث خطأ في معالجة الطلب' },
      { status: 500 }
    );
  }
}
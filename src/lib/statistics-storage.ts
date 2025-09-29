/**
 * Statistics Storage System for Arabic STT
 * Tracks real processing statistics and job data
 */

import fs from 'fs';
import path from 'path';

export interface ProcessingStatistics {
  totalFiles: number;
  totalMinutes: number;
  completedJobs: number;
  pendingJobs: number;
  failedJobs: number;
  totalProcessingTime: number; // in seconds
  averageProcessingTime: number; // in seconds
  lastUpdated: string;
}

export interface JobRecord {
  id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  duration: number; // file duration in seconds
  processingTime?: number; // actual processing time in seconds
  createdAt: string;
  completedAt?: string;
  transcriptId?: string;
}

class StatisticsStorage {
  private storageKey = 'arabic-stt-statistics';
  private jobsKey = 'arabic-stt-jobs';
  private dataDir = path.join(process.cwd(), 'data', 'statistics');
  private statisticsFile = path.join(this.dataDir, 'statistics.json');
  private jobsFile = path.join(this.dataDir, 'jobs.json');

  constructor() {
    // Ensure data directory exists
    this.ensureDataDirectory();
  }

  private ensureDataDirectory(): void {
    try {
      if (!fs.existsSync(this.dataDir)) {
        fs.mkdirSync(this.dataDir, { recursive: true });
      }
    } catch (error) {
      console.error('Error creating data directory:', error);
    }
  }

  private isServerSide(): boolean {
    return typeof window === 'undefined';
  }

  // Get current statistics
  getStatistics(): ProcessingStatistics {
    try {
      let stored: string | null = null;
      
      if (this.isServerSide()) {
        // Server-side: use file system
        if (fs.existsSync(this.statisticsFile)) {
          stored = fs.readFileSync(this.statisticsFile, 'utf8');
        }
      } else {
        // Client-side: use localStorage
        stored = localStorage.getItem(this.storageKey);
      }
      
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (error) {
      console.error('Error loading statistics:', error);
    }

    return this.getDefaultStatistics();
  }

  private getDefaultStatistics(): ProcessingStatistics {
    return {
      totalFiles: 0,
      totalMinutes: 0,
      completedJobs: 0,
      pendingJobs: 0,
      failedJobs: 0,
      totalProcessingTime: 0,
      averageProcessingTime: 0,
      lastUpdated: new Date().toISOString()
    };
  }

  // Get all job records
  getJobs(): JobRecord[] {
    try {
      let stored: string | null = null;
      
      if (this.isServerSide()) {
        // Server-side: use file system
        if (fs.existsSync(this.jobsFile)) {
          stored = fs.readFileSync(this.jobsFile, 'utf8');
        }
      } else {
        // Client-side: use localStorage
        stored = localStorage.getItem(this.jobsKey);
      }
      
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (error) {
      console.error('Error loading jobs:', error);
    }
    return [];
  }

  // Add a new job
  addJob(job: Omit<JobRecord, 'id' | 'createdAt'>): JobRecord {
    const newJob: JobRecord = {
      ...job,
      id: `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: new Date().toISOString()
    };

    const jobs = this.getJobs();
    jobs.push(newJob);
    this.saveJobs(jobs);
    this.updateStatistics();
    
    console.log('📊 New job added:', newJob);
    return newJob;
  }

  // Update job status
  updateJob(jobId: string, updates: Partial<JobRecord>): JobRecord | null {
    const jobs = this.getJobs();
    const jobIndex = jobs.findIndex(job => job.id === jobId);
    
    if (jobIndex === -1) {
      console.error('Job not found:', jobId);
      return null;
    }

    const updatedJob = { ...jobs[jobIndex], ...updates };
    
    // Set completion time if status changed to completed
    if (updates.status === 'completed' && !updatedJob.completedAt) {
      updatedJob.completedAt = new Date().toISOString();
    }

    jobs[jobIndex] = updatedJob;
    this.saveJobs(jobs);
    this.updateStatistics();
    
    console.log('📊 Job updated:', updatedJob);
    return updatedJob;
  }

  // Get recent jobs (last 10)
  getRecentJobs(limit: number = 10): JobRecord[] {
    const jobs = this.getJobs();
    return jobs
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, limit);
  }

  // Get jobs by status
  getJobsByStatus(status: JobRecord['status']): JobRecord[] {
    return this.getJobs().filter(job => job.status === status);
  }

  // Calculate and update statistics
  private updateStatistics(): void {
    const jobs = this.getJobs();
    
    const completedJobs = jobs.filter(job => job.status === 'completed');
    const pendingJobs = jobs.filter(job => job.status === 'pending' || job.status === 'processing');
    const failedJobs = jobs.filter(job => job.status === 'failed');
    
    const totalMinutes = Math.round(
      jobs.reduce((sum, job) => sum + (job.duration / 60), 0)
    );
    
    const totalProcessingTime = completedJobs.reduce(
      (sum, job) => sum + (job.processingTime || 0), 0
    );
    
    const averageProcessingTime = completedJobs.length > 0 
      ? Math.round(totalProcessingTime / completedJobs.length)
      : 0;

    const statistics: ProcessingStatistics = {
      totalFiles: jobs.length,
      totalMinutes,
      completedJobs: completedJobs.length,
      pendingJobs: pendingJobs.length,
      failedJobs: failedJobs.length,
      totalProcessingTime: Math.round(totalProcessingTime),
      averageProcessingTime,
      lastUpdated: new Date().toISOString()
    };

    this.saveStatistics(statistics);
  }

  // Save statistics
  private saveStatistics(statistics: ProcessingStatistics): void {
    try {
      const data = JSON.stringify(statistics, null, 2);
      
      if (this.isServerSide()) {
        // Server-side: use file system
        fs.writeFileSync(this.statisticsFile, data, 'utf8');
      } else {
        // Client-side: use localStorage
        localStorage.setItem(this.storageKey, data);
      }
    } catch (error) {
      console.error('Error saving statistics:', error);
    }
  }

  // Save jobs
  private saveJobs(jobs: JobRecord[]): void {
    try {
      const data = JSON.stringify(jobs, null, 2);
      
      if (this.isServerSide()) {
        // Server-side: use file system
        fs.writeFileSync(this.jobsFile, data, 'utf8');
      } else {
        // Client-side: use localStorage
        localStorage.setItem(this.jobsKey, data);
      }
    } catch (error) {
      console.error('Error saving jobs:', error);
    }
  }

  // Clear all data (for testing)
  clearAll(): void {
    try {
      if (this.isServerSide()) {
        // Server-side: remove files
        if (fs.existsSync(this.statisticsFile)) {
          fs.unlinkSync(this.statisticsFile);
        }
        if (fs.existsSync(this.jobsFile)) {
          fs.unlinkSync(this.jobsFile);
        }
      } else {
        // Client-side: remove from localStorage
        localStorage.removeItem(this.storageKey);
        localStorage.removeItem(this.jobsKey);
      }
      console.log('📊 All statistics and jobs cleared');
    } catch (error) {
      console.error('Error clearing data:', error);
    }
  }

  // Import demo data for testing
  importDemoData(): void {
    const demoJobs: JobRecord[] = [
      {
        id: 'demo_1',
        filename: 'اجتماع_الإدارة_2024.mp3',
        status: 'completed',
        progress: 100,
        duration: 1845, // 30.75 minutes
        processingTime: 92, // 1.5 minutes processing
        createdAt: '2024-01-15T10:30:00Z',
        completedAt: '2024-01-15T10:31:32Z',
        transcriptId: 'transcript_1705315892'
      },
      {
        id: 'demo_2',
        filename: 'تدريب_الموظفين.mp4',
        status: 'completed',
        progress: 100,
        duration: 3420, // 57 minutes
        processingTime: 171, // 2.85 minutes processing
        createdAt: '2024-01-15T09:15:00Z',
        completedAt: '2024-01-15T09:17:51Z',
        transcriptId: 'transcript_1705311451'
      },
      {
        id: 'demo_3',
        filename: 'مكالمة_عمل.wav',
        status: 'completed',
        progress: 100,
        duration: 1230, // 20.5 minutes
        processingTime: 61, // 1 minute processing
        createdAt: '2024-01-15T08:45:00Z',
        completedAt: '2024-01-15T08:46:01Z',
        transcriptId: 'transcript_1705309561'
      },
      {
        id: 'demo_4',
        filename: 'محاضرة_تقنية.mp3',
        status: 'completed',
        progress: 100,
        duration: 2700, // 45 minutes
        processingTime: 135, // 2.25 minutes processing
        createdAt: '2024-01-14T16:20:00Z',
        completedAt: '2024-01-14T16:22:15Z',
        transcriptId: 'transcript_1705250535'
      },
      {
        id: 'demo_5',
        filename: 'مقابلة_شخصية.mp4',
        status: 'completed',
        progress: 100,
        duration: 1800, // 30 minutes
        processingTime: 90, // 1.5 minutes processing
        createdAt: '2024-01-15T11:00:00Z',
        completedAt: '2024-01-15T11:01:30Z',
        transcriptId: 'transcript_1705315290'
      }
    ];

    this.saveJobs(demoJobs);
    this.updateStatistics();
    console.log('📊 Demo data imported:', demoJobs.length, 'jobs');
  }
}

// Export singleton instance
export const statisticsStorage = new StatisticsStorage();

// Helper functions
export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  if (minutes === 0) {
    return `${remainingSeconds} ثانية`;
  } else if (remainingSeconds === 0) {
    return `${minutes} دقيقة`;
  } else {
    return `${minutes} دقيقة و ${remainingSeconds} ثانية`;
  }
}

export function formatProcessingTime(seconds: number): string {
  if (seconds < 60) {
    return `${seconds} ثانية`;
  } else {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return remainingSeconds > 0 
      ? `${minutes} دقيقة و ${remainingSeconds} ثانية`
      : `${minutes} دقيقة`;
  }
}
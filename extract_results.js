const { demoAIProcessor } = require('./src/lib/demo-ai-processor.ts');

// Get all jobs
const allJobs = demoAIProcessor.getAllJobs();
console.log('Total jobs found:', allJobs.length);

// Find the specific job
const targetJob = allJobs.find(job => job.result?.transcript_id === 'transcript_1759031089');

if (targetJob && targetJob.result) {
  console.log('Found job with full results!');
  console.log('Segments count:', targetJob.result.segments.length);
  
  // Export all segments to a file
  const fs = require('fs');
  const fullResults = {
    transcript_id: targetJob.result.transcript_id,
    total_segments: targetJob.result.segments.length,
    speakers: targetJob.result.speakers,
    segments: targetJob.result.segments,
    processing_info: {
      confidence_score: targetJob.result.confidence_score,
      processing_time: targetJob.result.processing_time,
      model_used: targetJob.result.model_used || 'large-v3'
    }
  };
  
  fs.writeFileSync('complete_transcription_1759031089.json', JSON.stringify(fullResults, null, 2));
  console.log('Complete results exported to complete_transcription_1759031089.json');
} else {
  console.log('Job not found or no results available');
  console.log('Available jobs:', allJobs.map(j => ({ id: j.id, transcript_id: j.result?.transcript_id })));
}

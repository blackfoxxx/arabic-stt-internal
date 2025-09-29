// Extract complete transcription results from demoAIProcessor
const fs = require('fs');

// Since we can't directly import TypeScript modules in Node.js,
// we'll create a simple API call to get the data
const http = require('http');

async function extractResults() {
  try {
    // Make a request to get the transcript data
    const options = {
      hostname: 'localhost',
      port: 3000,
      path: '/api/transcripts/transcript_1759031089',
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    };

    const req = http.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          
          if (result.segments && result.segments.length > 0) {
            console.log(`Found ${result.segments.length} segments!`);
            
            // Create a comprehensive text file with all segments
            let fullTranscript = `Arabic Speech-to-Text Complete Transcription Results
================================================================

Transcript ID: ${result.id}
Filename: ${result.filename}
Status: ${result.status}
Language: ${result.language}
Model Used: ${result.model_used}
Confidence Score: ${result.confidence_score}
Processing Time: ${result.processing_time}s
Total Segments: ${result.segments.length}
Total Speakers: ${result.speakers ? result.speakers.length : 0}

COMPLETE TRANSCRIPTION:
======================

`;

            // Add all segments
            result.segments.forEach((segment, index) => {
              fullTranscript += `[${index + 1}] ${formatTime(segment.start)} - ${formatTime(segment.end)}\n`;
              fullTranscript += `Speaker: ${segment.speaker_id || 'Unknown'}\n`;
              fullTranscript += `Confidence: ${(segment.confidence * 100).toFixed(1)}%\n`;
              fullTranscript += `Text: ${segment.text}\n`;
              fullTranscript += `\n`;
            });

            // Add speakers information
            if (result.speakers && result.speakers.length > 0) {
              fullTranscript += `\nSPEAKERS INFORMATION:\n`;
              fullTranscript += `========================\n\n`;
              
              result.speakers.forEach((speaker, index) => {
                fullTranscript += `Speaker ${index + 1}:\n`;
                fullTranscript += `ID: ${speaker.id}\n`;
                fullTranscript += `Name: ${speaker.display_name || speaker.label}\n`;
                fullTranscript += `Segments: ${speaker.segments_count || 'Unknown'}\n\n`;
              });
            }

            // Save to file
            fs.writeFileSync('complete_transcription_full_1759031089.txt', fullTranscript, 'utf8');
            console.log('✅ Complete transcription saved to: complete_transcription_full_1759031089.txt');
            
            // Also save JSON version
            fs.writeFileSync('complete_transcription_1759031089.json', JSON.stringify(result, null, 2), 'utf8');
            console.log('✅ JSON data saved to: complete_transcription_1759031089.json');
            
          } else {
            console.log('❌ No segments found in the response');
            console.log('Response:', data);
          }
        } catch (parseError) {
          console.error('❌ Error parsing response:', parseError);
          console.log('Raw response:', data);
        }
      });
    });

    req.on('error', (error) => {
      console.error('❌ Request error:', error);
    });

    req.end();
    
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = (seconds % 60).toFixed(2);
  return `${mins}:${secs.padStart(5, '0')}`;
}

// Run the extraction
extractResults();
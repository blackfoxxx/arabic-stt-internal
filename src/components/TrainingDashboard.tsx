'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Brain, 
  Database, 
  Play, 
  Square, 
  BarChart3, 
  Settings, 
  Upload,
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react';

interface TrainingStatistics {
  total_samples: number;
  by_type: Record<string, number>;
  by_dialect: Record<string, number>;
  quality_distribution: {
    high: number;
    medium: number;
    low: number;
    unrated: number;
  };
}

interface AudioTrainingStatistics {
  total_audio_samples: number;
  average_quality_score: number;
  average_confidence_score: number;
  average_duration: number;
  unique_speakers: number;
  unique_dialects: number;
  quality_distribution: {
    high: number;
    medium: number;
    low: number;
  };
  dialect_distribution: Record<string, number>;
}

interface SpeakerStatistics {
  total_speakers: number;
  total_adaptations: number;
  average_quality: number;
  quality_distribution: {
    high: number;
    medium: number;
    low: number;
  };
  dialect_distribution: Record<string, number>;
  recent_activity: number;
  speakers_with_multiple_sessions: number;
}

interface TrainingStatus {
  is_training: boolean;
  session_id: string | null;
  progress: number;
  status: string;
  results?: any;
  error?: string;
}

interface AvailableModel {
  name: string;
  description: string;
  recommended_batch_size: number;
  memory_requirement: string;
}

const TrainingDashboard: React.FC = () => {
  const [statistics, setStatistics] = useState<TrainingStatistics | null>(null);
  const [audioStatistics, setAudioStatistics] = useState<AudioTrainingStatistics | null>(null);
  const [speakerStatistics, setSpeakerStatistics] = useState<SpeakerStatistics | null>(null);
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatus | null>(null);
  const [availableModels, setAvailableModels] = useState<AvailableModel[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [feedbackForm, setFeedbackForm] = useState({
    original_text: '',
    corrected_text: '',
    quality_score: 0.8
  });

  const [dialectForm, setDialectForm] = useState({
    standard_text: '',
    dialect_text: '',
    dialect_name: 'iraqi',
    quality_score: 0.8
  });

  const [trainingConfig, setTrainingConfig] = useState({
    model_name: 'llama3.1:8b',
    num_train_epochs: 3,
    per_device_train_batch_size: 4,
    learning_rate: 0.0005,
    lora_r: 16,
    lora_alpha: 32,
    lora_dropout: 0.1,
    max_length: 512
  });

  const [trainingFilters, setTrainingFilters] = useState({
    data_type: '',
    dialect: '',
    min_quality: 0.7,
    limit: 1000
  });

  // API base URL
  const API_BASE = 'http://localhost:8001/api';

  // Fetch data on component mount
  useEffect(() => {
    fetchStatistics();
    fetchAudioStatistics();
    fetchSpeakerStatistics();
    fetchTrainingStatus();
    fetchAvailableModels();
    
    // Set up polling for training status
    const interval = setInterval(fetchTrainingStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatistics = async () => {
    try {
      const response = await fetch(`${API_BASE}/data/statistics`);
      const data = await response.json();
      if (data.success) {
        setStatistics(data.statistics);
      }
    } catch (err) {
      console.error('Error fetching statistics:', err);
    }
  };

  const fetchAudioStatistics = async () => {
    try {
      const response = await fetch(`${API_BASE}/audio/training/statistics`);
      const data = await response.json();
      if (data.success) {
        setAudioStatistics(data.statistics);
      }
    } catch (err) {
      console.error('Error fetching audio statistics:', err);
    }
  };

  const fetchSpeakerStatistics = async () => {
    try {
      const response = await fetch(`${API_BASE}/speaker/statistics`);
      const data = await response.json();
      if (data.success) {
        setSpeakerStatistics(data.statistics);
      }
    } catch (err) {
      console.error('Error fetching speaker statistics:', err);
    }
  };

  const fetchTrainingStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/training/status`);
      const data = await response.json();
      if (data.success) {
        setTrainingStatus(data.status);
      }
    } catch (err) {
      console.error('Error fetching training status:', err);
    }
  };

  const fetchAvailableModels = async () => {
    try {
      const response = await fetch(`${API_BASE}/models/available`);
      const data = await response.json();
      if (data.success) {
        setAvailableModels(data.models);
      }
    } catch (err) {
      console.error('Error fetching available models:', err);
    }
  };

  const submitTranscriptionFeedback = async () => {
    if (!feedbackForm.original_text || !feedbackForm.corrected_text) {
      setError('Please fill in both original and corrected text');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/feedback/transcription`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedbackForm)
      });

      const data = await response.json();
      if (data.success) {
        setFeedbackForm({ original_text: '', corrected_text: '', quality_score: 0.8 });
        fetchStatistics(); // Refresh statistics
        alert('Feedback submitted successfully!');
      } else {
        setError('Failed to submit feedback');
      }
    } catch (err) {
      setError('Error submitting feedback');
    } finally {
      setLoading(false);
    }
  };

  const submitDialectSample = async () => {
    if (!dialectForm.standard_text || !dialectForm.dialect_text) {
      setError('Please fill in both standard and dialect text');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/data/dialect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dialectForm)
      });

      const data = await response.json();
      if (data.success) {
        setDialectForm({ 
          standard_text: '', 
          dialect_text: '', 
          dialect_name: 'iraqi', 
          quality_score: 0.8 
        });
        fetchStatistics(); // Refresh statistics
        alert('Dialect sample submitted successfully!');
      } else {
        setError('Failed to submit dialect sample');
      }
    } catch (err) {
      setError('Error submitting dialect sample');
    } finally {
      setLoading(false);
    }
  };

  const startTraining = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/training/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          config: trainingConfig,
          filters: trainingFilters
        })
      });

      const data = await response.json();
      if (data.success) {
        alert('Training session started!');
        fetchTrainingStatus();
      } else {
        setError('Failed to start training');
      }
    } catch (err) {
      setError('Error starting training');
    } finally {
      setLoading(false);
    }
  };

  const stopTraining = async () => {
    try {
      const response = await fetch(`${API_BASE}/training/stop`, {
        method: 'POST'
      });

      const data = await response.json();
      if (data.success) {
        alert('Training session stopped!');
        fetchTrainingStatus();
      }
    } catch (err) {
      setError('Error stopping training');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'training':
      case 'preparing':
        return <Clock className="h-4 w-4 text-blue-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Brain className="h-8 w-8 text-blue-600" />
            LLM Training Dashboard
          </h1>
          <p className="text-gray-600 mt-2">
            Train and fine-tune Arabic language models for better STT post-processing
          </p>
        </div>
      </div>

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="data">Data Collection</TabsTrigger>
          <TabsTrigger value="audio">Audio Training</TabsTrigger>
          <TabsTrigger value="speaker">Speaker Adaptation</TabsTrigger>
          <TabsTrigger value="training">Training</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Text Samples</CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {statistics?.total_samples || 0}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Audio Samples</CardTitle>
                <Database className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {audioStatistics?.total_audio_samples || 0}
                </div>
                <div className="text-xs text-muted-foreground">
                  Avg Quality: {audioStatistics?.average_quality_score?.toFixed(2) || 'N/A'}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">High Quality</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {statistics?.quality_distribution.high || 0}
                </div>
                <div className="text-xs text-muted-foreground">
                  Audio: {audioStatistics?.quality_distribution.high || 0}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Training Status</CardTitle>
                {getStatusIcon(trainingStatus?.status || 'idle')}
              </CardHeader>
              <CardContent>
                <div className="text-sm font-medium capitalize">
                  {trainingStatus?.status || 'Idle'}
                </div>
                {trainingStatus?.is_training && (
                  <Progress value={trainingStatus.progress} className="mt-2" />
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Speakers</CardTitle>
                <Upload className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {audioStatistics?.unique_speakers || 0}
                </div>
                <div className="text-xs text-muted-foreground">
                  Dialects: {audioStatistics?.unique_dialects || 0}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Enhanced Data Distribution */}
          {(statistics || audioStatistics) && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {statistics && (
                <Card>
                  <CardHeader>
                    <CardTitle>Text Data by Type</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {Object.entries(statistics.by_type).map(([type, count]) => (
                      <div key={type} className="flex justify-between items-center">
                        <span className="text-sm capitalize">{type.replace('_', ' ')}</span>
                        <Badge variant="secondary">{count}</Badge>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {audioStatistics && (
                <Card>
                  <CardHeader>
                    <CardTitle>Audio Quality Distribution</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">High Quality (≥0.8)</span>
                      <Badge variant="default" className="bg-green-500">{audioStatistics.quality_distribution.high}</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Medium Quality (0.6-0.8)</span>
                      <Badge variant="secondary">{audioStatistics.quality_distribution.medium}</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Low Quality (&lt;0.6)</span>
                      <Badge variant="destructive">{audioStatistics.quality_distribution.low}</Badge>
                    </div>
                  </CardContent>
                </Card>
              )}

              <Card>
                <CardHeader>
                  <CardTitle>Audio Training Insights</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {audioStatistics && (
                    <>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Avg Duration</span>
                        <Badge variant="outline">{audioStatistics.average_duration?.toFixed(1)}s</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Avg Confidence</span>
                        <Badge variant="outline">{audioStatistics.average_confidence_score?.toFixed(2)}</Badge>
                      </div>
                      {audioStatistics.dialect_distribution && Object.entries(audioStatistics.dialect_distribution).slice(0, 3).map(([dialect, count]) => (
                        <div key={dialect} className="flex justify-between items-center">
                          <span className="text-sm capitalize">{dialect}</span>
                          <Badge variant="secondary">{count}</Badge>
                        </div>
                      ))}
                    </>
                  )}
                  {!audioStatistics && (
                    <div className="text-sm text-muted-foreground">
                      No audio training data available
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        <TabsContent value="data" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Transcription Feedback */}
            <Card>
              <CardHeader>
                <CardTitle>Submit Transcription Feedback</CardTitle>
                <CardDescription>
                  Help improve the model by providing corrections to transcribed text
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="original">Original Text</Label>
                  <Textarea
                    id="original"
                    placeholder="Enter the original transcribed text..."
                    value={feedbackForm.original_text}
                    onChange={(e) => setFeedbackForm({
                      ...feedbackForm,
                      original_text: e.target.value
                    })}
                  />
                </div>
                <div>
                  <Label htmlFor="corrected">Corrected Text</Label>
                  <Textarea
                    id="corrected"
                    placeholder="Enter the corrected text..."
                    value={feedbackForm.corrected_text}
                    onChange={(e) => setFeedbackForm({
                      ...feedbackForm,
                      corrected_text: e.target.value
                    })}
                  />
                </div>
                <div>
                  <Label htmlFor="quality">Quality Score</Label>
                  <Input
                    id="quality"
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={feedbackForm.quality_score}
                    onChange={(e) => setFeedbackForm({
                      ...feedbackForm,
                      quality_score: parseFloat(e.target.value)
                    })}
                  />
                </div>
                <Button 
                  onClick={submitTranscriptionFeedback}
                  disabled={loading}
                  className="w-full"
                >
                  Submit Feedback
                </Button>
              </CardContent>
            </Card>

            {/* Dialect Sample */}
            <Card>
              <CardHeader>
                <CardTitle>Submit Dialect Sample</CardTitle>
                <CardDescription>
                  Contribute dialect variations to improve regional understanding
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="standard">Standard Arabic</Label>
                  <Textarea
                    id="standard"
                    placeholder="Enter standard Arabic text..."
                    value={dialectForm.standard_text}
                    onChange={(e) => setDialectForm({
                      ...dialectForm,
                      standard_text: e.target.value
                    })}
                  />
                </div>
                <div>
                  <Label htmlFor="dialect">Dialect Text</Label>
                  <Textarea
                    id="dialect"
                    placeholder="Enter dialect variation..."
                    value={dialectForm.dialect_text}
                    onChange={(e) => setDialectForm({
                      ...dialectForm,
                      dialect_text: e.target.value
                    })}
                  />
                </div>
                <div>
                  <Label htmlFor="dialect-name">Dialect</Label>
                  <Select
                    value={dialectForm.dialect_name}
                    onValueChange={(value) => setDialectForm({
                      ...dialectForm,
                      dialect_name: value
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="iraqi">Iraqi</SelectItem>
                      <SelectItem value="egyptian">Egyptian</SelectItem>
                      <SelectItem value="levantine">Levantine</SelectItem>
                      <SelectItem value="gulf">Gulf</SelectItem>
                      <SelectItem value="maghrebi">Maghrebi</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button 
                  onClick={submitDialectSample}
                  disabled={loading}
                  className="w-full"
                >
                  Submit Sample
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="audio" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Audio Training Upload */}
            <Card>
              <CardHeader>
                <CardTitle>Upload Audio Training Data</CardTitle>
                <CardDescription>
                  Upload audio files with transcriptions for enhanced training
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="audio-file">Audio File</Label>
                  <Input
                    id="audio-file"
                    type="file"
                    accept="audio/*"
                    onChange={(e) => {
                      // Handle audio file upload
                      const file = e.target.files?.[0];
                      if (file) {
                        console.log('Audio file selected:', file.name);
                      }
                    }}
                  />
                </div>
                <div>
                  <Label htmlFor="audio-transcript">Correct Transcription</Label>
                  <Textarea
                    id="audio-transcript"
                    placeholder="Enter the correct transcription for this audio..."
                    rows={4}
                  />
                </div>
                <div>
                  <Label htmlFor="audio-dialect">Dialect</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select dialect" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="iraqi">Iraqi</SelectItem>
                      <SelectItem value="egyptian">Egyptian</SelectItem>
                      <SelectItem value="levantine">Levantine</SelectItem>
                      <SelectItem value="gulf">Gulf</SelectItem>
                      <SelectItem value="maghrebi">Maghrebi</SelectItem>
                      <SelectItem value="standard">Standard Arabic</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button className="w-full" disabled={loading}>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Audio Training Sample
                </Button>
              </CardContent>
            </Card>

            {/* Continuous Learning Status */}
            <Card>
              <CardHeader>
                <CardTitle>Continuous Learning</CardTitle>
                <CardDescription>
                  Automatic training from transcription results
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></div>
                    <div>
                      <p className="font-medium">Auto-Learning Active</p>
                      <p className="text-sm text-muted-foreground">
                        Processing transcription results automatically
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">New samples collected</span>
                    <Badge variant="secondary">0</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Last training</span>
                    <Badge variant="outline">Never</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Training threshold</span>
                    <Badge variant="outline">100 samples</Badge>
                  </div>
                </div>

                <Button variant="outline" className="w-full">
                  <Settings className="h-4 w-4 mr-2" />
                  Configure Auto-Learning
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Audio Quality Assessment */}
          <Card>
            <CardHeader>
              <CardTitle>Audio Quality Assessment Training</CardTitle>
              <CardDescription>
                Train the system to better assess transcription quality based on audio characteristics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {audioStatistics?.quality_distribution.high || 0}
                  </div>
                  <div className="text-sm text-muted-foreground">High Quality Samples</div>
                  <div className="text-xs text-muted-foreground mt-1">≥ 0.8 confidence</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">
                    {audioStatistics?.quality_distribution.medium || 0}
                  </div>
                  <div className="text-sm text-muted-foreground">Medium Quality Samples</div>
                  <div className="text-xs text-muted-foreground mt-1">0.6 - 0.8 confidence</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {audioStatistics?.quality_distribution.low || 0}
                  </div>
                  <div className="text-sm text-muted-foreground">Low Quality Samples</div>
                  <div className="text-xs text-muted-foreground mt-1">&lt; 0.6 confidence</div>
                </div>
              </div>
              
              <div className="mt-6 flex gap-4">
                <Button variant="outline" className="flex-1">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Analyze Quality Patterns
                </Button>
                <Button variant="outline" className="flex-1">
                  <Brain className="h-4 w-4 mr-2" />
                  Train Quality Classifier
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="speaker" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Speaker Statistics Overview */}
            <Card>
              <CardHeader>
                <CardTitle>Speaker Adaptation Overview</CardTitle>
                <CardDescription>
                  Personalized training statistics and speaker profiles
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {speakerStatistics ? (
                  <>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {speakerStatistics.total_speakers}
                        </div>
                        <div className="text-sm text-gray-600">Total Speakers</div>
                      </div>
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          {speakerStatistics.total_adaptations}
                        </div>
                        <div className="text-sm text-gray-600">Adaptations</div>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Average Quality:</span>
                        <span className="font-medium">{(speakerStatistics.average_quality * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Recent Activity:</span>
                        <span className="font-medium">{speakerStatistics.recent_activity} sessions</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Multi-session Speakers:</span>
                        <span className="font-medium">{speakerStatistics.speakers_with_multiple_sessions}</span>
                      </div>
                    </div>

                    {/* Quality Distribution */}
                    <div className="space-y-2">
                      <h4 className="font-medium">Quality Distribution</h4>
                      <div className="space-y-1">
                        <div className="flex justify-between text-sm">
                          <span>High Quality:</span>
                          <span>{speakerStatistics.quality_distribution.high}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Medium Quality:</span>
                          <span>{speakerStatistics.quality_distribution.medium}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Low Quality:</span>
                          <span>{speakerStatistics.quality_distribution.low}</span>
                        </div>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    No speaker adaptation data available
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Speaker Profile Management */}
            <Card>
              <CardHeader>
                <CardTitle>Speaker Profile Management</CardTitle>
                <CardDescription>
                  Add new speaker data and manage existing profiles
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="speaker-audio">Audio Sample</Label>
                  <Input
                    id="speaker-audio"
                    type="file"
                    accept="audio/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        console.log('Speaker audio selected:', file.name);
                      }
                    }}
                  />
                </div>
                <div>
                  <Label htmlFor="speaker-transcript">Transcription</Label>
                  <Textarea
                    id="speaker-transcript"
                    placeholder="Enter the correct transcription..."
                    rows={3}
                  />
                </div>
                <div>
                  <Label htmlFor="speaker-id">Speaker ID (optional)</Label>
                  <Input
                    id="speaker-id"
                    placeholder="Leave empty for auto-detection"
                  />
                </div>
                <Button className="w-full">
                  <Users className="h-4 w-4 mr-2" />
                  Add Speaker Data
                </Button>
              </CardContent>
            </Card>

            {/* Dialect Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Dialect Distribution</CardTitle>
                <CardDescription>
                  Speaker preferences by dialect
                </CardDescription>
              </CardHeader>
              <CardContent>
                {speakerStatistics && Object.keys(speakerStatistics.dialect_distribution).length > 0 ? (
                  <div className="space-y-2">
                    {Object.entries(speakerStatistics.dialect_distribution).map(([dialect, count]) => (
                      <div key={dialect} className="flex justify-between items-center">
                        <span className="capitalize">{dialect}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ 
                                width: `${(count / Math.max(...Object.values(speakerStatistics.dialect_distribution))) * 100}%` 
                              }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">{count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-gray-500 py-4">
                    No dialect data available
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Personalization Features */}
            <Card>
              <CardHeader>
                <CardTitle>Personalization Features</CardTitle>
                <CardDescription>
                  Advanced speaker adaptation options
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start">
                    <Brain className="h-4 w-4 mr-2" />
                    Generate Speaker Recommendations
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Analyze Speaking Patterns
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Settings className="h-4 w-4 mr-2" />
                    Configure Adaptation Thresholds
                  </Button>
                </div>
                
                <div className="pt-4 border-t">
                  <Button className="w-full">
                    <Play className="h-4 w-4 mr-2" />
                    Start Speaker Adaptation Training
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="training" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Training Configuration */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Training Configuration</CardTitle>
                <CardDescription>
                  Configure the fine-tuning parameters for your model
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="model">Model</Label>
                    <Select
                      value={trainingConfig.model_name}
                      onValueChange={(value) => setTrainingConfig({
                        ...trainingConfig,
                        model_name: value
                      })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {availableModels.map((model) => (
                          <SelectItem key={model.name} value={model.name}>
                            {model.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="epochs">Epochs</Label>
                    <Input
                      id="epochs"
                      type="number"
                      min="1"
                      max="10"
                      value={trainingConfig.num_train_epochs}
                      onChange={(e) => setTrainingConfig({
                        ...trainingConfig,
                        num_train_epochs: parseInt(e.target.value)
                      })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="batch-size">Batch Size</Label>
                    <Input
                      id="batch-size"
                      type="number"
                      min="1"
                      max="16"
                      value={trainingConfig.per_device_train_batch_size}
                      onChange={(e) => setTrainingConfig({
                        ...trainingConfig,
                        per_device_train_batch_size: parseInt(e.target.value)
                      })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="learning-rate">Learning Rate</Label>
                    <Input
                      id="learning-rate"
                      type="number"
                      step="0.0001"
                      value={trainingConfig.learning_rate}
                      onChange={(e) => setTrainingConfig({
                        ...trainingConfig,
                        learning_rate: parseFloat(e.target.value)
                      })}
                    />
                  </div>
                </div>

                <div className="flex gap-4 pt-4">
                  <Button
                    onClick={startTraining}
                    disabled={loading || trainingStatus?.is_training}
                    className="flex items-center gap-2"
                  >
                    <Play className="h-4 w-4" />
                    Start Training
                  </Button>
                  {trainingStatus?.is_training && (
                    <Button
                      onClick={stopTraining}
                      variant="destructive"
                      className="flex items-center gap-2"
                    >
                      <Square className="h-4 w-4" />
                      Stop Training
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Training Status */}
            <Card>
              <CardHeader>
                <CardTitle>Training Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {trainingStatus && (
                  <>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(trainingStatus.status)}
                      <span className="capitalize font-medium">
                        {trainingStatus.status}
                      </span>
                    </div>
                    
                    {trainingStatus.is_training && (
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span>Progress</span>
                          <span>{trainingStatus.progress}%</span>
                        </div>
                        <Progress value={trainingStatus.progress} />
                      </div>
                    )}
                    
                    {trainingStatus.session_id && (
                      <div className="text-sm">
                        <span className="font-medium">Session ID:</span>
                        <br />
                        <code className="text-xs bg-gray-100 px-1 rounded">
                          {trainingStatus.session_id}
                        </code>
                      </div>
                    )}
                    
                    {trainingStatus.error && (
                      <Alert className="border-red-200 bg-red-50">
                        <AlertCircle className="h-4 w-4 text-red-600" />
                        <AlertDescription className="text-red-800 text-sm">
                          {trainingStatus.error}
                        </AlertDescription>
                      </Alert>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Advanced Settings</CardTitle>
              <CardDescription>
                Configure advanced training parameters and data filters
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="lora-r">LoRA Rank (r)</Label>
                  <Input
                    id="lora-r"
                    type="number"
                    min="1"
                    max="64"
                    value={trainingConfig.lora_r}
                    onChange={(e) => setTrainingConfig({
                      ...trainingConfig,
                      lora_r: parseInt(e.target.value)
                    })}
                  />
                </div>
                <div>
                  <Label htmlFor="lora-alpha">LoRA Alpha</Label>
                  <Input
                    id="lora-alpha"
                    type="number"
                    min="1"
                    max="128"
                    value={trainingConfig.lora_alpha}
                    onChange={(e) => setTrainingConfig({
                      ...trainingConfig,
                      lora_alpha: parseInt(e.target.value)
                    })}
                  />
                </div>
                <div>
                  <Label htmlFor="min-quality">Minimum Quality</Label>
                  <Input
                    id="min-quality"
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={trainingFilters.min_quality}
                    onChange={(e) => setTrainingFilters({
                      ...trainingFilters,
                      min_quality: parseFloat(e.target.value)
                    })}
                  />
                </div>
                <div>
                  <Label htmlFor="data-limit">Data Limit</Label>
                  <Input
                    id="data-limit"
                    type="number"
                    min="10"
                    value={trainingFilters.limit}
                    onChange={(e) => setTrainingFilters({
                      ...trainingFilters,
                      limit: parseInt(e.target.value)
                    })}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TrainingDashboard;
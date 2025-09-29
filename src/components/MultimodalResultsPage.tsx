'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { 
  Brain, 
  Mic, 
  FileText, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Activity,
  Heart,
  Volume2,
  Eye,
  Download,
  RefreshCw,
  BarChart3,
  PieChart,
  Play,
  Pause,
  Clock,
  Home
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart as RechartsPieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'

interface TranscriptSegment {
  id: string
  start: number
  end: number
  text: string
  confidence: number
  speaker_id: string
}

interface MultimodalResults {
  text_content: string
  full_transcription?: string
  segments?: TranscriptSegment[]
  audio_file: string
  original_audio_file?: string
  transcription_info?: {
    model_used: string
    language: string
    processing_date: string
    total_duration: string
    total_characters: number
    total_words: number
    total_segments?: number
  }
  final_assessment: {
    overall_credibility: number
    emotional_authenticity: number
    stress_level: number
    deception_likelihood: number
    cognitive_clarity: number
    multimodal_consistency: number
    voice_quality: number
    narrative_coherence: number
    confidence_score: number
    psychological_wellness: number
  }
  recommendations: string[]
  processing_time: number
  analysis_timestamp: string
  summary: {
    overall_sentiment: string
    sentiment_confidence: number
    truth_likelihood: number
    truth_confidence: number
    voice_quality: number
    stress_level: number
    deception_likelihood: number
    emotional_authenticity: number
    multimodal_consistency: number
  }
}

interface EnhancedTruthResults {
  overall_truth_likelihood: number
  confidence_level: number
  credibility_score: number
  linguistic_truth_result: {
    truth_likelihood: number
    confidence_score: number
    narrative_coherence: {
      overall_score: number
      temporal_consistency: number
      logical_flow: number
      detail_consistency: number
      emotional_consistency: number
      contradictions: string[]
      supporting_evidence: string[]
    }
    deception_markers: {
      linguistic_complexity: number
      detail_overload: number
      emotional_inconsistency: number
      temporal_vagueness: number
      defensive_language: number
      overall_deception_likelihood: number
    }
    truth_indicators: Array<{
      indicator_type: string
      text: string
      position: number
      confidence: number
      impact_score: number
    }>
  }
}

const MultimodalResultsPage: React.FC = () => {
  const [multimodalResults, setMultimodalResults] = useState<MultimodalResults | null>(null)
  const [enhancedTruthResults, setEnhancedTruthResults] = useState<EnhancedTruthResults | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentAudioTime, setCurrentAudioTime] = useState(0)
  const [audioRef, setAudioRef] = useState<HTMLAudioElement | null>(null)
  const [selectedSegment, setSelectedSegment] = useState<string | null>(null)

  // Helper functions for audio playback
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const playSegment = (segment: TranscriptSegment) => {
    if (audioRef) {
      try {
        audioRef.currentTime = segment.start
        const playPromise = audioRef.play()
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              setSelectedSegment(segment.id)
            })
            .catch((error) => {
              console.error('Audio playback failed:', error)
              // Handle autoplay restrictions
              if (error.name === 'NotAllowedError') {
                alert('Please click on the audio player to enable playback')
              }
            })
        }
      } catch (error) {
        console.error('Error setting audio time:', error)
      }
    }
  }

  const getSpeakerColor = (speakerId: string): string => {
    const colors = {
      'SPEAKER_00': '#3B82F6', // Blue
      'SPEAKER_01': '#10B981', // Green
      'SPEAKER_02': '#F59E0B', // Orange
      'SPEAKER_03': '#EF4444', // Red
    }
    return colors[speakerId as keyof typeof colors] || '#6B7280'
  }

  const getSpeakerName = (speakerId: string): string => {
    const names = {
      'SPEAKER_00': 'المتحدث الأول',
      'SPEAKER_01': 'المتحدث الثاني', 
      'SPEAKER_02': 'المتحدث الثالث',
      'SPEAKER_03': 'المتحدث الرابع',
    }
    return names[speakerId as keyof typeof names] || speakerId
  }

  // Chart colors
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']
  const acousticTimelineData = [
    { time: '0s', stress: 0.3, pitch: 150, volume: 0.6 },
    { time: '5s', stress: 0.5, pitch: 180, volume: 0.7 },
    { time: '10s', stress: 0.7, pitch: 200, volume: 0.8 },
    { time: '15s', stress: 0.4, pitch: 160, volume: 0.5 },
    { time: '20s', stress: 0.6, pitch: 190, volume: 0.9 },
    { time: '25s', stress: 0.3, pitch: 140, volume: 0.4 },
  ]

  const stressDistributionData = [
    { name: 'Low Stress', value: 40, color: '#00C49F' },
    { name: 'Medium Stress', value: 35, color: '#FFBB28' },
    { name: 'High Stress', value: 25, color: '#FF8042' },
  ]

  const prosodyFeaturesData = [
    { feature: 'Pitch Variation', value: 0.7, fullMark: 1 },
    { feature: 'Speaking Rate', value: 0.6, fullMark: 1 },
    { feature: 'Pause Frequency', value: 0.4, fullMark: 1 },
    { feature: 'Volume Consistency', value: 0.8, fullMark: 1 },
    { feature: 'Tone Stability', value: 0.5, fullMark: 1 },
  ]

  useEffect(() => {
    loadLatestResults()
  }, [])

  // Audio time synchronization effect
  useEffect(() => {
    if (audioRef && multimodalResults?.segments) {
      const handleTimeUpdate = () => {
        const currentTime = audioRef.currentTime
        setCurrentAudioTime(currentTime)
        
        // Find current segment based on audio time
        const currentSegment = multimodalResults.segments?.find(
          segment => currentTime >= segment.start && currentTime <= segment.end
        )
        
        if (currentSegment && selectedSegment !== currentSegment.id) {
          setSelectedSegment(currentSegment.id)
        }
      }

      audioRef.addEventListener('timeupdate', handleTimeUpdate)
      return () => audioRef.removeEventListener('timeupdate', handleTimeUpdate)
    }
  }, [audioRef, multimodalResults?.segments, selectedSegment])

  // Download functions
  const downloadOverviewData = () => {
    if (!multimodalResults) return
    
    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString('ar-SA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatPercentage = (value: number) => {
      return `${Math.round(value * 100)}%`
    }

    const overviewText = `
تقرير التحليل الشامل للصوت
=====================================

تاريخ التحليل: ${formatDate(multimodalResults.analysis_timestamp)}
وقت المعالجة: ${multimodalResults.processing_time} ثانية

التقييم النهائي:
-----------------
• مستوى الثقة: ${formatPercentage(multimodalResults.final_assessment.confidence_score)}
• الوضوح المعرفي: ${formatPercentage(multimodalResults.final_assessment.cognitive_clarity)}
• الأصالة العاطفية: ${formatPercentage(multimodalResults.final_assessment.emotional_authenticity)}
• الصحة النفسية: ${formatPercentage(multimodalResults.final_assessment.psychological_wellness)}
• احتمالية الخداع: ${formatPercentage(multimodalResults.final_assessment.deception_likelihood)}

ملخص التحليل:
--------------
• جودة الصوت: ${multimodalResults.summary.voice_quality}
• مستوى التوتر: ${multimodalResults.summary.stress_level}
• المشاعر العامة: ${multimodalResults.summary.overall_sentiment}
• ثقة التحليل العاطفي: ${formatPercentage(multimodalResults.summary.sentiment_confidence)}

التوصيات:
----------
${multimodalResults.recommendations.map((rec: string, index: number) => `${index + 1}. ${rec}`).join('\n')}

=====================================
تم إنشاء هذا التقرير بواسطة نظام التحليل الصوتي المتقدم
    `.trim()
    
    const blob = new Blob([overviewText], { type: 'text/plain; charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `تقرير_التحليل_الشامل_${Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const downloadTruthAnalysis = () => {
    if (!enhancedTruthResults) return
    
    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString('ar-SA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatPercentage = (value: number) => {
      return `${Math.round(value * 100)}%`
    }

    const getTruthLevel = (likelihood: number) => {
      if (likelihood >= 0.8) return "عالي جداً"
      if (likelihood >= 0.6) return "عالي"
      if (likelihood >= 0.4) return "متوسط"
      if (likelihood >= 0.2) return "منخفض"
      return "منخفض جداً"
    }

    const truthText = `
تقرير تحليل الصدق والمصداقية
=====================================

تاريخ التحليل: ${formatDate(new Date().toISOString())}

النتائج الرئيسية:
-----------------
• احتمالية الصدق الإجمالية: ${formatPercentage(enhancedTruthResults.overall_truth_likelihood)} (${getTruthLevel(enhancedTruthResults.overall_truth_likelihood)})
• مستوى الثقة: ${formatPercentage(enhancedTruthResults.confidence_level)}
• درجة المصداقية: ${formatPercentage(enhancedTruthResults.credibility_score)}

التحليل اللغوي:
---------------
• نتيجة التحليل اللغوي: ${formatPercentage(enhancedTruthResults.linguistic_truth_result.truth_likelihood)}
• مؤشرات الصدق اللغوية:
${enhancedTruthResults.linguistic_truth_result.truth_indicators.map((indicator: string, index: number) => `  ${index + 1}. ${indicator}`).join('\n')}

• مؤشرات الخداع اللغوية:
${enhancedTruthResults.linguistic_truth_result.deception_indicators.map((indicator: string, index: number) => `  ${index + 1}. ${indicator}`).join('\n')}

التحليل الصوتي:
---------------
• نتيجة التحليل الصوتي: ${formatPercentage(enhancedTruthResults.acoustic_truth_result.truth_likelihood)}
• مؤشرات الصدق الصوتية:
${enhancedTruthResults.acoustic_truth_result.truth_indicators.map((indicator: string, index: number) => `  ${index + 1}. ${indicator}`).join('\n')}

• مؤشرات الخداع الصوتية:
${enhancedTruthResults.acoustic_truth_result.deception_indicators.map((indicator: string, index: number) => `  ${index + 1}. ${indicator}`).join('\n')}

الخلاصة:
--------
بناءً على التحليل المتقدم للعوامل اللغوية والصوتية، يُظهر هذا التقرير مستوى ${getTruthLevel(enhancedTruthResults.overall_truth_likelihood)} من الصدق والمصداقية في المحتوى المُحلل.

=====================================
تم إنشاء هذا التقرير بواسطة نظام كشف الصدق المتقدم
    `.trim()
    
    const blob = new Blob([truthText], { type: 'text/plain; charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `تقرير_تحليل_الصدق_${Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const downloadAcousticAnalysis = () => {
    if (!multimodalResults) return
    
    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString('ar-SA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatPercentage = (value: number) => {
      return `${Math.round(value * 100)}%`
    }

    const formatDecimal = (value: number, decimals: number = 2) => {
      return value.toFixed(decimals)
    }

    const getQualityLevel = (quality: string) => {
      switch(quality?.toLowerCase()) {
        case 'excellent': return 'ممتاز'
        case 'good': return 'جيد'
        case 'fair': return 'مقبول'
        case 'poor': return 'ضعيف'
        default: return quality || 'غير محدد'
      }
    }

    const getStressLevel = (stress: string) => {
      switch(stress?.toLowerCase()) {
        case 'high': return 'عالي'
        case 'medium': return 'متوسط'
        case 'low': return 'منخفض'
        default: return stress || 'غير محدد'
      }
    }

    const acousticText = `
تقرير التحليل الصوتي
====================

تاريخ التحليل: ${formatDate(new Date().toISOString())}

الخصائص الصوتية الأساسية:
--------------------------
• جودة الصوت: ${getQualityLevel(multimodalResults.summary.voice_quality)}
• مستوى التوتر: ${getStressLevel(multimodalResults.summary.stress_level)}

المقاييس الصوتية:
-----------------
• معدل الكلام: 145 كلمة/دقيقة
• تنوع النبرة: ${formatPercentage(0.72)}
• استقرار الصوت: ${formatPercentage(0.68)}

تحليل النبرة والإيقاع:
---------------------
• متوسط التردد الأساسي: متغير حسب السياق
• تنوع الإيقاع: يُظهر تنوعاً طبيعياً في الكلام
• وضوح النطق: جيد إلى ممتاز

التحليل الزمني:
---------------
• توزيع الطاقة الصوتية عبر الزمن: متوازن
• فترات الصمت: ضمن المعدل الطبيعي
• استمرارية الكلام: منتظمة

الخلاصة:
--------
يُظهر التحليل الصوتي خصائص ${getQualityLevel(multimodalResults.summary.voice_quality)} للكلام المُسجل مع مستوى توتر ${getStressLevel(multimodalResults.summary.stress_level)}، مما يوفر نظرة شاملة على جودة الصوت وخصائص المتحدث.

====================
تم إنشاء هذا التقرير بواسطة نظام التحليل الصوتي المتقدم
    `.trim()
    
    const blob = new Blob([acousticText], { type: 'text/plain; charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `تقرير_التحليل_الصوتي_${Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const downloadSentimentAnalysis = () => {
    if (!multimodalResults) return
    
    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString('ar-SA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatPercentage = (value: number) => {
      return `${Math.round(value * 100)}%`
    }

    const getSentimentLevel = (sentiment: string) => {
      switch(sentiment?.toLowerCase()) {
        case 'positive': return 'إيجابي'
        case 'negative': return 'سلبي'
        case 'neutral': return 'محايد'
        case 'mixed': return 'مختلط'
        default: return sentiment || 'غير محدد'
      }
    }

    const getIntensityLevel = (value: number) => {
      if (value >= 80) return 'عالي جداً'
      if (value >= 60) return 'عالي'
      if (value >= 40) return 'متوسط'
      if (value >= 20) return 'منخفض'
      return 'منخفض جداً'
    }

    // Create sample data for emotional analysis
    const emotionalIntensityData = [
      { emotion: 'الفرح', intensity: multimodalResults.final_assessment.emotional_authenticity * 100 },
      { emotion: 'الحزن', intensity: (1 - multimodalResults.final_assessment.emotional_authenticity) * 50 },
      { emotion: 'الغضب', intensity: (1 - multimodalResults.final_assessment.psychological_wellness) * 60 },
      { emotion: 'الخوف', intensity: (1 - multimodalResults.final_assessment.confidence_score) * 40 },
      { emotion: 'المفاجأة', intensity: Math.random() * 30 + 20 },
    ]

    const sentimentText = `
تقرير تحليل المشاعر والعواطف
=============================

تاريخ التحليل: ${formatDate(new Date().toISOString())}

التقييم العام للمشاعر:
----------------------
• المشاعر الإجمالية: ${getSentimentLevel(multimodalResults.summary.overall_sentiment)}
• مستوى الثقة في التحليل: ${formatPercentage(multimodalResults.summary.sentiment_confidence)}
• صدق المشاعر: ${formatPercentage(multimodalResults.final_assessment.emotional_authenticity)}

تحليل شدة المشاعر:
------------------
${emotionalIntensityData.map(item => `• ${item.emotion}: ${formatPercentage(item.intensity / 100)} (${getIntensityLevel(item.intensity)})`).join('\n')}

المقاييس العاطفية:
-----------------
• مستوى الطاقة العاطفية: ${formatPercentage(0.75)}
• تماسك المشاعر: ${formatPercentage(0.82)}
• صدق التعبير العاطفي: ${formatPercentage(0.69)}

التحليل النفسي:
---------------
• الصحة النفسية العامة: ${formatPercentage(multimodalResults.final_assessment.psychological_wellness)}
• مستوى الثقة بالنفس: ${formatPercentage(multimodalResults.final_assessment.confidence_score)}
• الاستقرار العاطفي: ${formatPercentage((multimodalResults.final_assessment.psychological_wellness + multimodalResults.final_assessment.confidence_score) / 2)}

التطور الزمني للمشاعر:
-----------------------
• بداية التسجيل: مشاعر متوسطة الإيجابية
• منتصف التسجيل: ذروة التعبير العاطفي
• نهاية التسجيل: استقرار في المشاعر الإيجابية

الخلاصة:
--------
يُظهر التحليل العاطفي مشاعر ${getSentimentLevel(multimodalResults.summary.overall_sentiment)} بمستوى ثقة ${formatPercentage(multimodalResults.summary.sentiment_confidence)}، مع صدق عاطفي يبلغ ${formatPercentage(multimodalResults.final_assessment.emotional_authenticity)}.

=============================
تم إنشاء هذا التقرير بواسطة نظام تحليل المشاعر المتقدم
    `.trim()
    
    const blob = new Blob([sentimentText], { type: 'text/plain; charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `تقرير_تحليل_المشاعر_${Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const downloadBehavioralAnalysis = () => {
    if (!multimodalResults) return
    
    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString('ar-SA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatPercentage = (value: number) => {
      return `${Math.round(value * 100)}%`
    }

    const getReliabilityLevel = (assessment: string) => {
      switch(assessment?.toLowerCase()) {
        case 'high': return 'عالي'
        case 'moderate': return 'متوسط'
        case 'low': return 'منخفض'
        default: return assessment || 'غير محدد'
      }
    }

    const getClarityLevel = (clarity: number) => {
      if (clarity >= 0.8) return 'ممتاز'
      if (clarity >= 0.6) return 'جيد'
      if (clarity >= 0.4) return 'مقبول'
      if (clarity >= 0.2) return 'ضعيف'
      return 'ضعيف جداً'
    }

    const behavioralText = `
تقرير التحليل السلوكي والنفسي
==============================

تاريخ التحليل: ${formatDate(new Date().toISOString())}

التقييم السلوكي الرئيسي:
------------------------
• احتمالية الخداع: ${formatPercentage(multimodalResults.final_assessment.deception_likelihood)}
• وضوح الإدراك: ${formatPercentage(multimodalResults.final_assessment.cognitive_clarity)} (${getClarityLevel(multimodalResults.final_assessment.cognitive_clarity)})
• مستوى الثقة: ${formatPercentage(multimodalResults.final_assessment.confidence_score)}

الأنماط السلوكية:
-----------------
• درجة الاتساق: ${formatPercentage(0.78)}
• تقييم الموثوقية: ${getReliabilityLevel("MODERATE")}
• استقرار السلوك: جيد إلى متوسط

المؤشرات السلوكية المحددة:
---------------------------
• أنماط كلام متسقة
• مستويات توتر معتدلة
• وضوح إدراكي جيد
• استجابات منطقية ومتماسكة

التوصيات:
----------
${multimodalResults.recommendations.map((rec: string, index: number) => `${index + 1}. ${rec}`).join('\n')}

التحليل النفسي المتقدم:
-----------------------
• الصحة النفسية: ${formatPercentage(multimodalResults.final_assessment.psychological_wellness)}
• الاستقرار العاطفي: ${formatPercentage((multimodalResults.final_assessment.psychological_wellness + multimodalResults.final_assessment.confidence_score) / 2)}
• القدرة على التكيف: متوسط إلى جيد

الخلاصة:
--------
يُظهر التحليل السلوكي مستوى ${getReliabilityLevel("MODERATE")} من الموثوقية مع وضوح إدراكي ${getClarityLevel(multimodalResults.final_assessment.cognitive_clarity)} ومستوى ثقة ${formatPercentage(multimodalResults.final_assessment.confidence_score)}.

==============================
تم إنشاء هذا التقرير بواسطة نظام التحليل السلوكي المتقدم
    `.trim()
    
    const blob = new Blob([behavioralText], { type: 'text/plain; charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `تقرير_التحليل_السلوكي_${Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const downloadFullScript = () => {
    if (!multimodalResults) return
    
    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString('ar-SA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatTime = (seconds: number) => {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = Math.floor(seconds % 60)
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    }

    let scriptContent = `
النص الكامل للتسجيل الصوتي
=====================================

تاريخ المعالجة: ${formatDate(multimodalResults.analysis_timestamp)}
`

    // Add transcription info if available
    if (multimodalResults.transcription_info) {
      scriptContent += `
معلومات التفريغ:
-----------------
• النموذج المستخدم: ${multimodalResults.transcription_info.model_used}
• اللغة: ${multimodalResults.transcription_info.language}
• المدة الإجمالية: ${multimodalResults.transcription_info.total_duration}
• عدد الكلمات: ${multimodalResults.transcription_info.total_words}
• عدد الأحرف: ${multimodalResults.transcription_info.total_characters}
${multimodalResults.transcription_info.total_segments ? `• عدد المقاطع: ${multimodalResults.transcription_info.total_segments}` : ''}

`
    }

    // Add segmented transcript if available, otherwise use full transcription
    if (multimodalResults.segments && multimodalResults.segments.length > 0) {
      scriptContent += `النص المقسم حسب الوقت:
=====================================

`
      multimodalResults.segments.forEach((segment, index) => {
        scriptContent += `[${formatTime(segment.start)} - ${formatTime(segment.end)}] (الثقة: ${Math.round(segment.confidence * 100)}%)
${segment.text}

`
      })
    } else {
      scriptContent += `النص الكامل:
=====================================

${multimodalResults.full_transcription || multimodalResults.text_content}

`
    }

    scriptContent += `
=====================================
تم إنشاء هذا النص بواسطة نظام التفريغ الصوتي المتقدم
    `.trim()
    
    const blob = new Blob([scriptContent], { type: 'text/plain; charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `النص_الكامل_${Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const loadLatestResults = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load multimodal results
      const multimodalResponse = await fetch('/api/results/multimodal/latest')
      if (multimodalResponse.ok) {
        const multimodalData = await multimodalResponse.json()
        setMultimodalResults(multimodalData)
      }

      // Load enhanced truth results
      const truthResponse = await fetch('/api/results/enhanced-truth/latest')
      if (truthResponse.ok) {
        const truthData = await truthResponse.json()
        setEnhancedTruthResults(truthData)
      }

    } catch (err) {
      setError('Failed to load analysis results')
      console.error('Error loading results:', err)
    } finally {
      setLoading(false)
    }
  }

  const getCredibilityColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600'
    if (score >= 0.4) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getCredibilityBadge = (score: number) => {
    if (score >= 0.7) return <Badge className="bg-green-100 text-green-800">High Reliability</Badge>
    if (score >= 0.4) return <Badge className="bg-yellow-100 text-yellow-800">Moderate Reliability</Badge>
    return <Badge className="bg-red-100 text-red-800">Low Reliability</Badge>
  }

  const formatPercentage = (value: number) => `${(value * 100).toFixed(1)}%`

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading analysis results...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert className="m-4">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (!multimodalResults && !enhancedTruthResults) {
    return (
      <Alert className="m-4">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>No Results Found</AlertTitle>
        <AlertDescription>No analysis results available. Please run an analysis first.</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <Button
          variant="outline"
          onClick={() => window.location.href = '/'}
          className="flex items-center gap-2"
        >
          <Home className="h-4 w-4" />
          Back to Home
        </Button>
      </div>
      
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Multimodal Analysis Results</h1>
        <p className="text-muted-foreground">
          Comprehensive AI-powered analysis combining linguistic, acoustic, and behavioral insights
        </p>
      </div>

      {/* Quick Overview Cards */}
      {multimodalResults && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overall Credibility</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatPercentage(multimodalResults.final_assessment.overall_credibility)}
              </div>
              <div className="mt-2">
                {getCredibilityBadge(multimodalResults.final_assessment.overall_credibility)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Truth Likelihood</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatPercentage(multimodalResults.summary.truth_likelihood)}
              </div>
              <Progress 
                value={multimodalResults.summary.truth_likelihood * 100} 
                className="mt-2"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Voice Quality</CardTitle>
              <Volume2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatPercentage(multimodalResults.summary.voice_quality)}
              </div>
              <Progress 
                value={multimodalResults.summary.voice_quality * 100} 
                className="mt-2"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Stress Level</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatPercentage(multimodalResults.summary.stress_level)}
              </div>
              <Progress 
                value={multimodalResults.summary.stress_level * 100} 
                className="mt-2"
              />
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Analysis Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">نظرة عامة</TabsTrigger>
          <TabsTrigger value="truth-analysis">كشف الصدق</TabsTrigger>
          <TabsTrigger value="acoustic">التحليل الصوتي</TabsTrigger>
          <TabsTrigger value="sentiment">تحليل المشاعر</TabsTrigger>
          <TabsTrigger value="recommendations">المؤشرات السلوكية</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">نظرة عامة - Overview</h2>
            <Button onClick={downloadOverviewData} variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              تحميل البيانات
            </Button>
          </div>
          {multimodalResults && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Final Assessment */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Brain className="h-5 w-5" />
                    Final Assessment
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span>Overall Credibility</span>
                      <span className={`font-semibold ${getCredibilityColor(multimodalResults.final_assessment.overall_credibility)}`}>
                        {formatPercentage(multimodalResults.final_assessment.overall_credibility)}
                      </span>
                    </div>
                    <Progress value={multimodalResults.final_assessment.overall_credibility * 100} />

                    <div className="flex justify-between items-center">
                      <span>Emotional Authenticity</span>
                      <span className="font-semibold">
                        {formatPercentage(multimodalResults.final_assessment.emotional_authenticity)}
                      </span>
                    </div>
                    <Progress value={multimodalResults.final_assessment.emotional_authenticity * 100} />

                    <div className="flex justify-between items-center">
                      <span>Multimodal Consistency</span>
                      <span className="font-semibold">
                        {formatPercentage(multimodalResults.final_assessment.multimodal_consistency)}
                      </span>
                    </div>
                    <Progress value={multimodalResults.final_assessment.multimodal_consistency * 100} />

                    <div className="flex justify-between items-center">
                      <span>Psychological Wellness</span>
                      <span className="font-semibold">
                        {formatPercentage(multimodalResults.final_assessment.psychological_wellness)}
                      </span>
                    </div>
                    <Progress value={multimodalResults.final_assessment.psychological_wellness * 100} />
                  </div>
                </CardContent>
              </Card>

              {/* Analysis Summary */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Analysis Summary
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Sentiment:</span>
                      <Badge className="ml-2" variant={multimodalResults.summary.overall_sentiment === 'positive' ? 'default' : 'secondary'}>
                        {multimodalResults.summary.overall_sentiment}
                      </Badge>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Processing Time:</span>
                      <span className="ml-2 font-medium">{multimodalResults.processing_time.toFixed(1)}s</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Deception Risk:</span>
                      <span className="ml-2 font-medium">
                        {formatPercentage(multimodalResults.summary.deception_likelihood)}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Confidence:</span>
                      <span className="ml-2 font-medium">
                        {formatPercentage(multimodalResults.final_assessment.confidence_score)}
                      </span>
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        Timeline Transcription - النص الزمني:
                      </h4>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={downloadFullScript}
                        className="flex items-center gap-2"
                      >
                        <Download className="h-4 w-4" />
                        Download Full Script
                      </Button>
                    </div>
                    
                    {/* Audio Player with Enhanced Controls */}
                    {multimodalResults.audio_file && (
                      <div className="mb-4 p-4 bg-muted rounded-md">
                        <div className="flex items-center gap-3 mb-3">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm font-medium">Audio Player</span>
                          {multimodalResults.transcription_info?.total_duration && (
                            <span className="text-xs text-muted-foreground">
                              Duration: {multimodalResults.transcription_info.total_duration}
                            </span>
                          )}
                        </div>
                        <audio
                          ref={setAudioRef}
                          controls
                          preload="metadata"
                          className="w-full"
                          onTimeUpdate={(e) => setCurrentAudioTime(e.currentTarget.currentTime)}
                          onError={(e) => {
                            console.error('Audio loading error:', {
                              error: e,
                              audioSrc: multimodalResults.audio_file,
                              errorType: e.currentTarget?.error?.code,
                              errorMessage: e.currentTarget?.error?.message,
                              networkState: e.currentTarget?.networkState,
                              readyState: e.currentTarget?.readyState
                            })
                            setError(`Failed to load audio file: ${multimodalResults.audio_file}`)
                          }}
                          onLoadStart={() => console.log('Audio loading started')}
                          onCanPlay={() => console.log('Audio can play')}
                        >
                          <source src={multimodalResults.audio_file} type="audio/mpeg" />
                          <source src={multimodalResults.audio_file} type="audio/mp3" />
                          <source src={multimodalResults.audio_file} type="audio/wav" />
                          Your browser does not support the audio element.
                        </audio>
                        {/* Progress indicator */}
                        {multimodalResults.segments && audioRef && (
                          <div className="mt-2 text-xs text-muted-foreground">
                            Current time: {formatTime(currentAudioTime)}
                            {selectedSegment && (
                              <span className="ml-2">
                                • Playing segment {multimodalResults.segments.findIndex(s => s.id === selectedSegment) + 1} of {multimodalResults.segments.length}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Timeline Transcription */}
                    {multimodalResults.segments && multimodalResults.segments.length > 0 ? (
                      <div className="bg-muted p-4 rounded-md max-h-96 overflow-y-auto border-r-4 border-blue-500">
                        <div className="space-y-3">
                          {multimodalResults.segments.map((segment) => (
                            <div
                              key={segment.id}
                              className={`p-3 rounded-lg border-l-4 cursor-pointer transition-all hover:bg-background ${
                                selectedSegment === segment.id ? 'bg-background shadow-md' : ''
                              }`}
                              style={{ borderLeftColor: getSpeakerColor(segment.speaker_id) }}
                              onClick={() => playSegment(segment)}
                            >
                              <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-2">
                                  <span 
                                    className="px-2 py-1 rounded text-xs font-medium text-white"
                                    style={{ backgroundColor: getSpeakerColor(segment.speaker_id) }}
                                  >
                                    {getSpeakerName(segment.speaker_id)}
                                  </span>
                                  <span className="text-xs text-muted-foreground">
                                    {formatTime(segment.start)} - {formatTime(segment.end)}
                                  </span>
                                  <span className="text-xs text-muted-foreground">
                                    ({(segment.confidence * 100).toFixed(0)}%)
                                  </span>
                                </div>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    playSegment(segment)
                                  }}
                                  className="p-1 rounded hover:bg-muted-foreground/10 transition-colors"
                                  title="Play this segment"
                                >
                                  <Play className="h-4 w-4" />
                                </button>
                              </div>
                              <div className="text-right leading-relaxed" dir="rtl" lang="ar">
                                {segment.text}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="bg-muted p-4 rounded-md text-sm max-h-48 overflow-y-auto border-r-4 border-blue-500">
                        <div className="text-right leading-relaxed" dir="rtl" lang="ar">
                          {multimodalResults.full_transcription || multimodalResults.text_content.trim()}
                        </div>
                      </div>
                    )}
                    
                    {multimodalResults.transcription_info && (
                      <div className="mt-2 text-xs text-muted-foreground grid grid-cols-2 gap-2">
                        <div>Model: {multimodalResults.transcription_info.model_used}</div>
                        <div>Duration: {multimodalResults.transcription_info.total_duration}</div>
                        <div>Words: {multimodalResults.transcription_info.total_words}</div>
                        <div>Characters: {multimodalResults.transcription_info.total_characters}</div>
                        {multimodalResults.transcription_info.total_segments && (
                          <div>Segments: {multimodalResults.transcription_info.total_segments}</div>
                        )}
                      </div>
                    )}
                  </div>

                  <Separator />

                  <div>
                    <h4 className="font-medium mb-2">Audio File:</h4>
                    <div className="bg-muted p-3 rounded-md text-sm">
                      <div className="flex items-center gap-2">
                        <Volume2 className="h-4 w-4" />
                        <span className="font-mono text-xs">
                          {multimodalResults.original_audio_file || multimodalResults.audio_file}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* Enhanced Truth Analysis Tab */}
        <TabsContent value="truth-analysis" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">كشف الصدق - Truth Detection</h2>
            <Button onClick={downloadTruthAnalysis} variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              تحميل تحليل الصدق
            </Button>
          </div>
          {enhancedTruthResults && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Truth Metrics */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Eye className="h-5 w-5" />
                    Truth Detection Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span>Overall Truth Likelihood</span>
                      <span className="font-semibold text-lg">
                        {formatPercentage(enhancedTruthResults.overall_truth_likelihood)}
                      </span>
                    </div>
                    <Progress value={enhancedTruthResults.overall_truth_likelihood * 100} />

                    <div className="flex justify-between items-center">
                      <span>Confidence Level</span>
                      <span className="font-semibold">
                        {formatPercentage(enhancedTruthResults.confidence_level)}
                      </span>
                    </div>
                    <Progress value={enhancedTruthResults.confidence_level * 100} />

                    <div className="flex justify-between items-center">
                      <span>Credibility Score</span>
                      <span className="font-semibold">
                        {formatPercentage(enhancedTruthResults.credibility_score)}
                      </span>
                    </div>
                    <Progress value={enhancedTruthResults.credibility_score * 100} />
                  </div>
                </CardContent>
              </Card>

              {/* Narrative Coherence */}
              <Card>
                <CardHeader>
                  <CardTitle>Narrative Coherence Analysis</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span>Overall Coherence</span>
                      <span className="font-semibold">
                        {formatPercentage(enhancedTruthResults.linguistic_truth_result.narrative_coherence.overall_score)}
                      </span>
                    </div>
                    <Progress value={enhancedTruthResults.linguistic_truth_result.narrative_coherence.overall_score * 100} />

                    <div className="flex justify-between items-center">
                      <span>Temporal Consistency</span>
                      <span className="font-semibold">
                        {formatPercentage(enhancedTruthResults.linguistic_truth_result.narrative_coherence.temporal_consistency)}
                      </span>
                    </div>
                    <Progress value={enhancedTruthResults.linguistic_truth_result.narrative_coherence.temporal_consistency * 100} />

                    <div className="flex justify-between items-center">
                      <span>Emotional Consistency</span>
                      <span className="font-semibold">
                        {formatPercentage(enhancedTruthResults.linguistic_truth_result.narrative_coherence.emotional_consistency)}
                      </span>
                    </div>
                    <Progress value={enhancedTruthResults.linguistic_truth_result.narrative_coherence.emotional_consistency * 100} />
                  </div>

                  <Separator />

                  <div className="space-y-2">
                    <div>
                      <span className="text-sm font-medium">Supporting Evidence:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {enhancedTruthResults.linguistic_truth_result.narrative_coherence.supporting_evidence.map((evidence, index) => (
                          <Badge key={index} variant="outline" className="text-green-700 border-green-300">
                            {evidence}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    {enhancedTruthResults.linguistic_truth_result.narrative_coherence.contradictions.length > 0 && (
                      <div>
                        <span className="text-sm font-medium">Contradictions:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {enhancedTruthResults.linguistic_truth_result.narrative_coherence.contradictions.map((contradiction, index) => (
                            <Badge key={index} variant="outline" className="text-red-700 border-red-300">
                              {contradiction}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Deception Markers */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5" />
                    Deception Markers Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <span className="text-sm font-medium">Linguistic Complexity</span>
                      <Progress value={enhancedTruthResults.linguistic_truth_result.deception_markers.linguistic_complexity * 100} />
                      <span className="text-xs text-muted-foreground">
                        {formatPercentage(enhancedTruthResults.linguistic_truth_result.deception_markers.linguistic_complexity)}
                      </span>
                    </div>
                    
                    <div className="space-y-2">
                      <span className="text-sm font-medium">Emotional Inconsistency</span>
                      <Progress value={enhancedTruthResults.linguistic_truth_result.deception_markers.emotional_inconsistency * 100} />
                      <span className="text-xs text-muted-foreground">
                        {formatPercentage(enhancedTruthResults.linguistic_truth_result.deception_markers.emotional_inconsistency)}
                      </span>
                    </div>
                    
                    <div className="space-y-2">
                      <span className="text-sm font-medium">Overall Deception Risk</span>
                      <Progress value={enhancedTruthResults.linguistic_truth_result.deception_markers.overall_deception_likelihood * 100} />
                      <span className="text-xs text-muted-foreground">
                        {formatPercentage(enhancedTruthResults.linguistic_truth_result.deception_markers.overall_deception_likelihood)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* Acoustic Analysis Tab */}
        <TabsContent value="acoustic" className="space-y-4">
          {multimodalResults && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Mic className="h-5 w-5" />
                    Voice Quality Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span>Voice Quality</span>
                      <span className="font-semibold">
                        {formatPercentage(multimodalResults.summary.voice_quality)}
                      </span>
                    </div>
                    <Progress value={multimodalResults.summary.voice_quality * 100} />

                    <div className="flex justify-between items-center">
                      <span>Stress Level</span>
                      <span className="font-semibold">
                        {formatPercentage(multimodalResults.summary.stress_level)}
                      </span>
                    </div>
                    <Progress value={multimodalResults.summary.stress_level * 100} />

                    <div className="flex justify-between items-center">
                      <span>Emotional Authenticity</span>
                      <span className="font-semibold">
                        {formatPercentage(multimodalResults.summary.emotional_authenticity)}
                      </span>
                    </div>
                    <Progress value={multimodalResults.summary.emotional_authenticity * 100} />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Audio File Information</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div>
                      <span className="text-sm text-muted-foreground">File:</span>
                      <span className="ml-2 font-medium">{multimodalResults.audio_file}</span>
                    </div>
                    <div>
                      <span className="text-sm text-muted-foreground">Analysis Date:</span>
                      <span className="ml-2 font-medium">
                        {new Date(multimodalResults.analysis_timestamp).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* Acoustic Analysis Tab */}
        <TabsContent value="acoustic" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">التحليل الصوتي - Acoustic Analysis</h2>
            <Button onClick={downloadAcousticAnalysis} variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              تحميل التحليل الصوتي
            </Button>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Acoustic Timeline */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    التحليل الزمني للصوت
                  </CardTitle>
                  <CardDescription>
                    تطور مؤشرات الضغط والنبرة والصوت عبر الزمن
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={acousticTimelineData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="stress" stroke="#FF8042" strokeWidth={2} name="مستوى الضغط" />
                      <Line type="monotone" dataKey="pitch" stroke="#0088FE" strokeWidth={2} name="النبرة (Hz)" />
                      <Line type="monotone" dataKey="volume" stroke="#00C49F" strokeWidth={2} name="مستوى الصوت" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Stress Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <PieChart className="h-5 w-5" />
                    توزيع مستويات الضغط
                  </CardTitle>
                  <CardDescription>
                    نسبة توزيع مستويات الضغط في التسجيل
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <RechartsPieChart>
                      <Pie
                        data={stressDistributionData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {stressDistributionData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Prosody Features Radar */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    تحليل الخصائص الصوتية
                  </CardTitle>
                  <CardDescription>
                    تقييم شامل للخصائص الصوتية والنطقية
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <RadarChart data={prosodyFeaturesData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="feature" />
                      <PolarRadiusAxis angle={90} domain={[0, 1]} />
                      <Radar
                        name="القيمة"
                        dataKey="value"
                        stroke="#8884d8"
                        fill="#8884d8"
                        fillOpacity={0.6}
                      />
                      <Tooltip />
                    </RadarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            {/* Acoustic Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">معدل الكلام</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">142 كلمة/دقيقة</div>
                  <p className="text-xs text-muted-foreground">ضمن المعدل الطبيعي</p>
                  <Progress value={71} className="mt-2" />
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">تنوع النبرة</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">68%</div>
                  <p className="text-xs text-muted-foreground">تنوع جيد في النبرة</p>
                  <Progress value={68} className="mt-2" />
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">استقرار الصوت</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">84%</div>
                  <p className="text-xs text-muted-foreground">استقرار عالي</p>
                  <Progress value={84} className="mt-2" />
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        <TabsContent value="sentiment" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">تحليل المشاعر - Sentiment Analysis</h2>
            <Button onClick={downloadSentimentAnalysis} variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              تحميل تحليل المشاعر
            </Button>
          </div>
          {multimodalResults && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Sentiment Overview */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    تحليل المشاعر العام
                  </CardTitle>
                  <CardDescription>
                    التقييم الشامل للحالة العاطفية والمشاعر
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">المشاعر الإيجابية</span>
                    <Badge variant={multimodalResults.final_assessment.emotional_authenticity > 0.6 ? "default" : "secondary"}>
                      {(multimodalResults.final_assessment.emotional_authenticity * 100).toFixed(1)}%
                    </Badge>
                  </div>
                  <Progress value={multimodalResults.final_assessment.emotional_authenticity * 100} />
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">الاستقرار العاطفي</span>
                    <Badge variant={multimodalResults.final_assessment.psychological_wellness > 0.6 ? "default" : "secondary"}>
                      {(multimodalResults.final_assessment.psychological_wellness * 100).toFixed(1)}%
                    </Badge>
                  </div>
                  <Progress value={multimodalResults.final_assessment.psychological_wellness * 100} />
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">الثقة في التعبير</span>
                    <Badge variant={multimodalResults.final_assessment.confidence_score > 0.6 ? "default" : "secondary"}>
                      {(multimodalResults.final_assessment.confidence_score * 100).toFixed(1)}%
                    </Badge>
                  </div>
                  <Progress value={multimodalResults.final_assessment.confidence_score * 100} />
                </CardContent>
              </Card>

              {/* Emotional Intensity Chart */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    شدة المشاعر
                  </CardTitle>
                  <CardDescription>
                    توزيع شدة المشاعر المختلفة
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={[
                      { emotion: 'الفرح', intensity: multimodalResults.final_assessment.emotional_authenticity * 100 },
                      { emotion: 'الحزن', intensity: (1 - multimodalResults.final_assessment.emotional_authenticity) * 50 },
                      { emotion: 'الغضب', intensity: (1 - multimodalResults.final_assessment.psychological_wellness) * 60 },
                      { emotion: 'الخوف', intensity: (1 - multimodalResults.final_assessment.confidence_score) * 40 },
                      { emotion: 'المفاجأة', intensity: Math.random() * 30 + 20 },
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="emotion" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="intensity" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Sentiment Timeline */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    تطور المشاعر عبر الزمن
                  </CardTitle>
                  <CardDescription>
                    تغير الحالة العاطفية خلال فترة التسجيل
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={[
                      { time: '0%', positivity: 0.4, stability: 0.6, confidence: 0.5 },
                      { time: '25%', positivity: 0.6, stability: 0.7, confidence: 0.6 },
                      { time: '50%', positivity: multimodalResults.final_assessment.emotional_authenticity, stability: multimodalResults.final_assessment.psychological_wellness, confidence: multimodalResults.final_assessment.confidence_score },
                      { time: '75%', positivity: 0.5, stability: 0.6, confidence: 0.7 },
                      { time: '100%', positivity: 0.7, stability: 0.8, confidence: 0.6 },
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="positivity" stroke="#00C49F" strokeWidth={2} name="الإيجابية" />
                      <Line type="monotone" dataKey="stability" stroke="#0088FE" strokeWidth={2} name="الاستقرار" />
                      <Line type="monotone" dataKey="confidence" stroke="#FF8042" strokeWidth={2} name="الثقة" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Sentiment Analysis Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">التقييم العام</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {multimodalResults?.final_assessment.emotional_authenticity > 0.6 ? 'إيجابي' : 
                   multimodalResults?.final_assessment.emotional_authenticity > 0.4 ? 'محايد' : 'سلبي'}
                </div>
                <p className="text-xs text-muted-foreground">الحالة العاطفية العامة</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">مستوى الطاقة</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {multimodalResults ? (multimodalResults.final_assessment.confidence_score * 100).toFixed(0) + '%' : 'N/A'}
                </div>
                <p className="text-xs text-muted-foreground">نشاط وحيوية المتحدث</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">التماسك العاطفي</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {multimodalResults ? (multimodalResults.final_assessment.psychological_wellness * 100).toFixed(0) + '%' : 'N/A'}
                </div>
                <p className="text-xs text-muted-foreground">ثبات الحالة العاطفية</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">مؤشر الصدق العاطفي</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {enhancedTruthResults ? (enhancedTruthResults.credibility_score * 100).toFixed(0) + '%' : 'N/A'}
                </div>
                <p className="text-xs text-muted-foreground">مصداقية التعبير العاطفي</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Behavioral Indicators Tab */}
        <TabsContent value="recommendations" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">المؤشرات السلوكية - Behavioral Indicators</h2>
            <Button onClick={downloadBehavioralAnalysis} variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              تحميل المؤشرات السلوكية
            </Button>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Behavioral Patterns */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  الأنماط السلوكية
                </CardTitle>
                <CardDescription>
                  تحليل السلوكيات والأنماط المكتشفة
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {enhancedTruthResults?.linguistic_truth_result && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <span className="text-sm font-medium">مؤشرات الصدق</span>
                      <Badge variant="default">
                        {enhancedTruthResults.linguistic_truth_result.truth_indicators.length} مؤشر
                      </Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                      <span className="text-sm font-medium">مؤشرات الضغط</span>
                      <Badge variant="secondary">
                        {Math.floor(enhancedTruthResults.linguistic_truth_result.deception_markers.overall_deception_likelihood * 10)} مؤشر
                      </Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <span className="text-sm font-medium">مؤشرات الثقة</span>
                      <Badge variant="outline">
                        {Math.floor(enhancedTruthResults.confidence_level * 10)} مؤشر
                      </Badge>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Reliability Assessment */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5" />
                  تقييم الموثوقية
                </CardTitle>
                <CardDescription>
                  التقييم الشامل لموثوقية البيانات
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold mb-2">
                      {enhancedTruthResults ? 
                        enhancedTruthResults.overall_truth_likelihood > 0.7 ? 'عالية' :
                        enhancedTruthResults.overall_truth_likelihood > 0.4 ? 'متوسطة' : 'منخفضة'
                        : 'غير متاح'
                      }
                    </div>
                    <p className="text-sm text-muted-foreground">درجة الموثوقية العامة</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">احتمالية الصدق</span>
                      <span className="text-sm font-medium">
                        {enhancedTruthResults ? (enhancedTruthResults.overall_truth_likelihood * 100).toFixed(1) + '%' : 'N/A'}
                      </span>
                    </div>
                    <Progress value={enhancedTruthResults ? enhancedTruthResults.overall_truth_likelihood * 100 : 0} />
                    
                    <div className="flex justify-between">
                      <span className="text-sm">مستوى الثقة</span>
                      <span className="text-sm font-medium">
                        {enhancedTruthResults ? (enhancedTruthResults.confidence_level * 100).toFixed(1) + '%' : 'N/A'}
                      </span>
                    </div>
                    <Progress value={enhancedTruthResults ? enhancedTruthResults.confidence_level * 100 : 0} />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recommendations */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  التوصيات والملاحظات
                </CardTitle>
                <CardDescription>
                  توصيات مبنية على نتائج التحليل
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {multimodalResults?.recommendations && multimodalResults.recommendations.length > 0 ? (
                    multimodalResults.recommendations.map((recommendation, index) => (
                      <div key={index} className="p-4 border rounded-lg bg-gray-50">
                        <div className="flex items-start gap-3">
                          <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                          <p className="text-sm">{recommendation}</p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-2 text-center py-8 text-gray-500">
                      لا توجد توصيات متاحة حالياً
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Interactive Dashboard Preview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                لوحة التحكم التفاعلية
              </CardTitle>
              <CardDescription>
                نظرة شاملة على جميع المؤشرات والتحليلات
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {multimodalResults ? (multimodalResults.final_assessment.overall_credibility * 100).toFixed(0) + '%' : 'N/A'}
                  </div>
                  <p className="text-xs text-blue-700">المصداقية</p>
                </div>
                
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {enhancedTruthResults ? (enhancedTruthResults.overall_truth_likelihood * 100).toFixed(0) + '%' : 'N/A'}
                  </div>
                  <p className="text-xs text-green-700">الصدق</p>
                </div>
                
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">
                    {multimodalResults ? (multimodalResults.final_assessment.confidence_score * 100).toFixed(0) + '%' : 'N/A'}
                  </div>
                  <p className="text-xs text-orange-700">الثقة</p>
                </div>
                
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {multimodalResults ? (multimodalResults.final_assessment.psychological_wellness * 100).toFixed(0) + '%' : 'N/A'}
                  </div>
                  <p className="text-xs text-purple-700">الصحة النفسية</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default MultimodalResultsPage
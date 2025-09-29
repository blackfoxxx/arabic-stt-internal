"use client";

import { useParams } from 'next/navigation';
import MultimodalResultsPage from '@/components/MultimodalResultsPage';

export default function TranscriptPage() {
  const params = useParams();
  const transcriptId = params.transcriptId as string;

  return <MultimodalResultsPage transcriptId={transcriptId} />;
}
export interface ExamSession {
  id: string;
  candidateId: string;
  candidateName: string;
  sessionStartTime: number;
  currentRiskScore: number;
  status: 'active' | 'flagged' | 'paused';
  videoStreamUrl?: string;
  riskTrend: number[];
}

export interface Alert {
  id: string;
  sessionId: string;
  type: 'mobile_phone' | 'face_not_visible' | 'multiple_faces' | 'copied_text' | 'tab_switch' | 'inactivity' | 'audio_anomaly' | 'manual';
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  message: string;
  timestamp: number;
  isAcknowledged: boolean;
  snapshot?: string;
}

export interface TimelineEvent {
  id: string;
  sessionId: string;
  eventType: string;
  timestamp: number;
  confidence: number;
  riskContribution: number;
  snapshot?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface ExamInfo {
  id: string;
  name: string;
  startTime: number;
  duration: number;
  totalCandidates: number;
  activeCandidates: number;
}

export interface Evidence {
  id: string;
  sessionId: string;
  timestamp: number;
  eventType: string;
  riskScoreAtCapture: number;
  imageUrl: string;
  thumbnailUrl?: string;
}

export interface WebSocketMessage {
  type: 'alert' | 'score_update' | 'event' | 'connection' | 'session_update';
  data: unknown;
}

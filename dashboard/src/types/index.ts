export type AgentStatus = 'active' | 'draft' | 'archived';

export interface Agent {
  id: string;
  name: string;
  version: string;
  score: number;
  status: AgentStatus;
  lastEvaluation: string;
  dimensions: {
    reasoning: number;
    safety: number;
    performance: number;
    adaptability: number;
    communication: number;
  };
  strengths: string[];
  weaknesses: string[];
}

export interface TestRun {
  id: string;
  agentId: string;
  agentName: string;
  date: string;
  score: number;
  status: 'passed' | 'failed' | 'warning';
  duration: number;
}

export interface DashboardStats {
  totalAgents: number;
  averageScore: number;
  testsRun: number;
  passRate: number;
}

export interface ScoreHistory {
  date: string;
  score: number;
}

import { notFound } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { agents, testRuns } from '@/lib/mockData';
import { ArrowLeft, FileText, CheckCircle2, AlertCircle } from 'lucide-react';

export default function AgentDetailPage({ params }: { params: { id: string } }) {
  const agent = agents.find((a) => a.id === params.id);

  if (!agent) {
    notFound();
  }

  const agentTests = testRuns
    .filter((test) => test.agentId === agent.id)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  const maxScore = Math.max(...Object.values(agent.dimensions));

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <Link
            href="/agents"
            className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Agents
          </Link>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">{agent.name}</h1>
            <Badge variant={agent.status === 'active' ? 'default' : 'secondary'}>
              {agent.status}
            </Badge>
          </div>
          <p className="text-muted-foreground">
            Version {agent.version} • Last evaluated{' '}
            {new Date(agent.lastEvaluation).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>
        <div className="text-right">
          <div className="text-4xl font-bold">{agent.score.toFixed(1)}</div>
          <div className="text-sm text-muted-foreground">Overall Score</div>
        </div>
      </div>

      {/* Dimension Scores */}
      <Card>
        <CardHeader>
          <CardTitle>Performance by Dimension</CardTitle>
          <CardDescription>Breakdown of scores across all evaluation criteria</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {Object.entries(agent.dimensions).map(([dimension, score]) => {
            const percentage = (score / 10) * 100;
            const barWidth = (score / maxScore) * 100;
            return (
              <div key={dimension} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium capitalize">{dimension}</span>
                  <span className="text-sm font-bold">{score.toFixed(1)}</span>
                </div>
                <div className="h-3 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>

      <div className="grid gap-8 md:grid-cols-2">
        {/* Strengths */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              Strengths
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {agent.strengths.map((strength, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-green-600 mt-1">•</span>
                  <span className="text-sm">{strength}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Weaknesses */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-orange-600" />
              Areas for Improvement
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {agent.weaknesses.map((weakness, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-orange-600 mt-1">•</span>
                  <span className="text-sm">{weakness}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Test History */}
      <Card>
        <CardHeader>
          <CardTitle>Test History</CardTitle>
          <CardDescription>Timeline of all evaluations for this agent</CardDescription>
        </CardHeader>
        <CardContent>
          {agentTests.length === 0 ? (
            <p className="text-center py-8 text-muted-foreground">No test history available</p>
          ) : (
            <div className="space-y-4">
              {agentTests.map((test, index) => (
                <div key={test.id} className="flex items-center gap-4 p-4 rounded-lg border">
                  <div
                    className={`h-10 w-10 rounded-full flex items-center justify-center ${
                      test.status === 'passed'
                        ? 'bg-green-100 text-green-700'
                        : test.status === 'warning'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    <FileText className="h-5 w-5" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">Test Run #{agentTests.length - index}</span>
                      <Badge
                        variant={
                          test.status === 'passed'
                            ? 'default'
                            : test.status === 'warning'
                            ? 'secondary'
                            : 'destructive'
                        }
                      >
                        {test.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {new Date(test.date).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                      {' • '}
                      {test.duration}s duration
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold">{test.score.toFixed(1)}</div>
                    <div className="text-xs text-muted-foreground">Score</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Action Button */}
      <div className="flex justify-end">
        <Button size="lg">
          <FileText className="mr-2 h-4 w-4" />
          View Full HTML Report
        </Button>
      </div>
    </div>
  );
}

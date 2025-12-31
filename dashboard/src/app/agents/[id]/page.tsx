import { notFound } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { fetchAgentById, fetchTestResultsByAgent } from '@/lib/supabaseData';
import { ArrowLeft, FileText, CheckCircle2, AlertCircle } from 'lucide-react';

// Enable dynamic params to accept any agent ID
export const dynamicParams = true;
export const revalidate = 0;

export default async function AgentDetailPage({ params }: { params: { id: string } }) {
  let agent, testResults;

  try {
    agent = await fetchAgentById(params.id);
    testResults = await fetchTestResultsByAgent(params.id);
  } catch (error) {
    console.error('Error fetching agent:', error);
    notFound();
  }

  if (!agent) {
    notFound();
  }

  // Get the last test details for dimensions
  const lastTest = testResults[0];
  const dimensions = lastTest ? {
    completeness: lastTest.completeness || 0,
    tone: lastTest.tone || 0,
    engagement: lastTest.engagement || 0,
    compliance: lastTest.compliance || 0,
    conversion: lastTest.conversion || 0,
  } : {};

  const maxScore = Math.max(...Object.values(dimensions), 1);

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
            <h1 className="text-3xl font-bold tracking-tight">{agent.agent_name}</h1>
            <Badge variant={agent.status === 'active' ? 'default' : 'secondary'}>
              {agent.status}
            </Badge>
          </div>
          <p className="text-muted-foreground">
            Version {agent.version} • Last evaluated{' '}
            {agent.last_test_at ? new Date(agent.last_test_at).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            }) : 'Never'}
          </p>
        </div>
        <div className="text-right">
          <div className="text-4xl font-bold">{(agent.last_test_score || 0).toFixed(1)}</div>
          <div className="text-sm text-muted-foreground">Overall Score</div>
        </div>
      </div>

      {/* Dimension Scores */}
      {Object.keys(dimensions).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Performance by Dimension</CardTitle>
            <CardDescription>Breakdown of scores across all evaluation criteria</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {Object.entries(dimensions).map(([dimension, score]) => {
              const percentage = (score / 10) * 100;
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
      )}

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
              {lastTest?.strengths && lastTest.strengths.length > 0 ? (
                lastTest.strengths.map((strength, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-green-600 mt-1">•</span>
                    <span className="text-sm">{strength}</span>
                  </li>
                ))
              ) : (
                <li className="text-sm text-muted-foreground">No strengths data available</li>
              )}
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
              {lastTest?.weaknesses && lastTest.weaknesses.length > 0 ? (
                lastTest.weaknesses.map((weakness, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-orange-600 mt-1">•</span>
                    <span className="text-sm">{weakness}</span>
                  </li>
                ))
              ) : (
                <li className="text-sm text-muted-foreground">No weaknesses data available</li>
              )}
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
          {testResults.length === 0 ? (
            <p className="text-center py-8 text-muted-foreground">No test history available</p>
          ) : (
            <div className="space-y-4">
              {testResults.map((test, index) => {
                const isPassed = test.overall_score >= 8.0;
                const isWarning = test.overall_score >= 6.0 && test.overall_score < 8.0;
                const status = isPassed ? 'passed' : isWarning ? 'warning' : 'failed';

                return (
                  <div key={test.test_result_id} className="flex items-center gap-4 p-4 rounded-lg border">
                    <div
                      className={`h-10 w-10 rounded-full flex items-center justify-center ${
                        status === 'passed'
                          ? 'bg-green-100 text-green-700'
                          : status === 'warning'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      <FileText className="h-5 w-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">Test Run #{testResults.length - index}</span>
                        <Badge
                          variant={
                            status === 'passed'
                              ? 'default'
                              : status === 'warning'
                              ? 'secondary'
                              : 'destructive'
                          }
                        >
                          {status}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {new Date(test.tested_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                        {' • '}
                        {(test.test_duration_ms / 1000).toFixed(1)}s duration
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold">{test.overall_score.toFixed(1)}</div>
                      <div className="text-xs text-muted-foreground">Score</div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Action Button */}
      {agent.test_report_url && (
        <div className="flex justify-end">
          <Button size="lg" asChild>
            <a href={agent.test_report_url} target="_blank" rel="noopener noreferrer">
              <FileText className="mr-2 h-4 w-4" />
              View Full HTML Report
            </a>
          </Button>
        </div>
      )}
    </div>
  );
}

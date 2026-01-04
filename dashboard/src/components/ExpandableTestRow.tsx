'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { TableCell, TableRow } from '@/components/ui/table';
import type { TestExecution, E2ETestResult } from '@/types/database';
import { ChevronDown, ChevronRight, CheckCircle2, XCircle, Clock, MessageSquare, FileText } from 'lucide-react';

interface ExpandableTestRowProps {
  execution: TestExecution;
}

export function ExpandableTestRow({ execution }: ExpandableTestRowProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'passed':
        return 'default';
      case 'warning':
        return 'secondary';
      case 'failed':
      case 'error':
      case 'timeout':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  const getScoreBadgeVariant = (score: number) => {
    if (score >= 8) return 'default';
    if (score >= 7) return 'secondary';
    return 'destructive';
  };

  const overallStatus = execution.failed_scenarios === 0 ? 'passed' :
                        execution.passed_scenarios > execution.failed_scenarios ? 'warning' : 'failed';

  const hasScenarios = execution.scenarios && execution.scenarios.length > 0;

  return (
    <>
      {/* Main Row */}
      <TableRow
        className={`cursor-pointer hover:bg-muted/50 ${isExpanded ? 'bg-muted/30' : ''}`}
        onClick={() => hasScenarios && setIsExpanded(!isExpanded)}
      >
        <TableCell className="w-[40px]">
          {hasScenarios ? (
            <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </Button>
          ) : (
            <span className="w-6" />
          )}
        </TableCell>
        <TableCell>
          <Link
            href={`/agents/${execution.agent_version_id}`}
            className="font-medium hover:underline"
            onClick={(e) => e.stopPropagation()}
          >
            {execution.agent_name}
          </Link>
          <span className="text-xs text-muted-foreground ml-2">
            v{execution.version}
          </span>
        </TableCell>
        <TableCell className="text-muted-foreground">
          {new Date(execution.tested_at).toLocaleDateString('pt-BR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </TableCell>
        <TableCell>
          <div className="flex items-center gap-2">
            <span className="text-green-500 font-medium">{execution.passed_scenarios} Pass</span>
            <span className="text-muted-foreground">/</span>
            <span className="text-red-500 font-medium">{execution.failed_scenarios} Fail</span>
          </div>
          {execution.overall_score > 0 && (
            <div className="text-xs text-muted-foreground mt-1">
              Score: {execution.overall_score.toFixed(1)}/10
            </div>
          )}
        </TableCell>
        <TableCell>
          <Badge variant={getStatusBadgeVariant(overallStatus)}>
            {overallStatus}
          </Badge>
        </TableCell>
        <TableCell className="text-right">
          <Link
            href={`/agents/${execution.agent_version_id}`}
            className="text-xs text-blue-500 hover:underline"
            onClick={(e) => e.stopPropagation()}
          >
            <FileText className="h-4 w-4 inline mr-1" />
            Ver HTML
          </Link>
        </TableCell>
      </TableRow>

      {/* Expanded Scenarios */}
      {isExpanded && hasScenarios && (
        <>
          <TableRow className="bg-muted/20">
            <TableCell colSpan={6} className="p-0">
              <div className="border-l-2 border-primary/30 ml-6 pl-4 py-2">
                <div className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wider">
                  Cenários de Teste ({execution.scenarios.length})
                </div>
                <div className="space-y-1">
                  {execution.scenarios.map((scenario) => (
                    <ScenarioRow key={scenario.id} scenario={scenario} />
                  ))}
                </div>
              </div>
            </TableCell>
          </TableRow>
        </>
      )}
    </>
  );
}

interface ScenarioRowProps {
  scenario: E2ETestResult;
}

function ScenarioRow({ scenario }: ScenarioRowProps) {
  const [showConversation, setShowConversation] = useState(false);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'failed':
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'timeout':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <XCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getPersonaBadge = (persona: string | null) => {
    if (!persona) return null;
    const colors: Record<string, string> = {
      hot: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      warm: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      cold: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      objection: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    };
    return (
      <span className={`text-xs px-2 py-0.5 rounded-full ${colors[persona.toLowerCase()] || 'bg-gray-100 text-gray-800'}`}>
        {persona}
      </span>
    );
  };

  return (
    <div className="bg-background/50 rounded-md p-3 border border-border/50">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {getStatusIcon(scenario.status)}
          <div>
            <div className="font-medium text-sm">
              {scenario.scenario_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </div>
            {scenario.scenario_description && (
              <div className="text-xs text-muted-foreground line-clamp-1">
                {scenario.scenario_description}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs">
          {getPersonaBadge(scenario.lead_persona)}

          <div className="flex items-center gap-1 text-muted-foreground">
            <MessageSquare className="h-3 w-3" />
            {scenario.total_turns} turnos
          </div>

          {scenario.score !== null && (
            <Badge variant={scenario.score >= 8 ? 'default' : scenario.score >= 6 ? 'secondary' : 'destructive'}>
              {scenario.score.toFixed(1)}
            </Badge>
          )}

          {scenario.duration_seconds !== null && (
            <span className="text-muted-foreground">
              {scenario.duration_seconds.toFixed(1)}s
            </span>
          )}

          {scenario.conversation && scenario.conversation.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 text-xs"
              onClick={() => setShowConversation(!showConversation)}
            >
              {showConversation ? 'Ocultar' : 'Ver Conversa'}
            </Button>
          )}
        </div>
      </div>

      {/* Conversation Preview */}
      {showConversation && scenario.conversation && scenario.conversation.length > 0 && (
        <div className="mt-3 pt-3 border-t border-border/50">
          <div className="text-xs font-medium text-muted-foreground mb-2">Conversa:</div>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {scenario.conversation.slice(0, 10).map((msg: any, idx: number) => (
              <div
                key={idx}
                className={`text-xs p-2 rounded ${
                  msg.role === 'assistant'
                    ? 'bg-blue-50 dark:bg-blue-900/30 ml-4'
                    : 'bg-gray-50 dark:bg-gray-900/30 mr-4'
                }`}
              >
                <div className="font-medium text-muted-foreground mb-1">
                  {msg.role === 'assistant' ? '🤖 Bot' : '👤 Lead'}
                </div>
                <div className="whitespace-pre-wrap">{msg.content || msg.message}</div>
              </div>
            ))}
            {scenario.conversation.length > 10 && (
              <div className="text-xs text-center text-muted-foreground py-2">
                ... e mais {scenario.conversation.length - 10} mensagens
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error Message */}
      {scenario.error_message && (
        <div className="mt-2 text-xs text-red-500 bg-red-50 dark:bg-red-900/20 p-2 rounded">
          ⚠️ {scenario.error_message}
        </div>
      )}
    </div>
  );
}

export default ExpandableTestRow;

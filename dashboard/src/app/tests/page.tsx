'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { fetchTestExecutions } from '@/lib/supabaseData';
import type { TestExecution } from '@/types/database';
import { ExpandableTestRow } from '@/components/ExpandableTestRow';
import { Search, Calendar, Clock, RefreshCw, CheckCircle2, XCircle } from 'lucide-react';

type StatusFilter = 'all' | 'passed' | 'failed' | 'warning';

export default function TestsPage() {
  const [executions, setExecutions] = useState<TestExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [scoreFilter, setScoreFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  const loadData = async () => {
    try {
      const data = await fetchTestExecutions(100);
      setExecutions(data);
    } catch (error) {
      console.error('Error fetching test executions:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-2">
          <div className="text-lg font-medium">Carregando histórico de testes...</div>
          <div className="text-sm text-muted-foreground">Por favor aguarde</div>
        </div>
      </div>
    );
  }

  const getExecutionStatus = (exec: TestExecution): 'passed' | 'warning' | 'failed' => {
    if (exec.failed_scenarios === 0) return 'passed';
    if (exec.passed_scenarios > exec.failed_scenarios) return 'warning';
    return 'failed';
  };

  const filteredExecutions = executions
    .filter((exec) => {
      const status = getExecutionStatus(exec);
      const matchesSearch = exec.agent_name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesStatus = statusFilter === 'all' || status === statusFilter;
      const matchesScore =
        scoreFilter === 'all' ||
        (scoreFilter === 'high' && exec.overall_score >= 8) ||
        (scoreFilter === 'medium' && exec.overall_score >= 7 && exec.overall_score < 8) ||
        (scoreFilter === 'low' && exec.overall_score < 7);

      return matchesSearch && matchesStatus && matchesScore;
    })
    .sort((a, b) => new Date(b.tested_at).getTime() - new Date(a.tested_at).getTime());

  // Calculate stats
  const totalExecutions = executions.length;
  const totalScenarios = executions.reduce((acc, e) => acc + e.total_scenarios, 0);
  const totalPassed = executions.reduce((acc, e) => acc + e.passed_scenarios, 0);
  const totalFailed = executions.reduce((acc, e) => acc + e.failed_scenarios, 0);
  const passRate = totalScenarios > 0 ? (totalPassed / totalScenarios * 100) : 0;

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Histórico de Execuções</h1>
          <p className="text-muted-foreground">
            Resultados dos testes automatizados (Python LLM-as-a-Judge)
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={refreshing}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Execuções</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalExecutions}</div>
            <p className="text-xs text-muted-foreground">
              {totalScenarios} cenários testados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Taxa de Sucesso</CardTitle>
            <Badge className="h-6">
              {passRate.toFixed(1)}%
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span className="text-green-600 font-bold">{totalPassed}</span>
              </div>
              <div className="flex items-center gap-1">
                <XCircle className="h-4 w-4 text-red-500" />
                <span className="text-red-600 font-bold">{totalFailed}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cobertura</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {executions.length > 0 ? Math.round(totalScenarios / executions.length) : 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Média cenários/execução
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Último Teste</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm font-medium">
              {executions.length > 0
                ? new Date(executions[0].tested_at).toLocaleDateString('pt-BR', {
                    day: '2-digit',
                    month: 'short',
                    hour: '2-digit',
                    minute: '2-digit',
                  })
                : '-'}
            </div>
            <p className="text-xs text-muted-foreground">
              {executions.length > 0 ? executions[0].agent_name : '-'}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Todas as Execuções</CardTitle>
          <CardDescription>
            Clique em uma execução para ver os cenários detalhados
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Filters */}
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por nome do agente..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as StatusFilter)}>
              <SelectTrigger className="w-full md:w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos Status</SelectItem>
                <SelectItem value="passed">Passou</SelectItem>
                <SelectItem value="warning">Parcial</SelectItem>
                <SelectItem value="failed">Falhou</SelectItem>
              </SelectContent>
            </Select>
            <Select value={scoreFilter} onValueChange={(value) => setScoreFilter(value as 'all' | 'high' | 'medium' | 'low')}>
              <SelectTrigger className="w-full md:w-[180px]">
                <SelectValue placeholder="Score" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos Scores</SelectItem>
                <SelectItem value="high">8+ (Alto)</SelectItem>
                <SelectItem value="medium">7-8 (Médio)</SelectItem>
                <SelectItem value="low">&lt;7 (Baixo)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Results count */}
          <p className="text-sm text-muted-foreground">
            Mostrando {filteredExecutions.length} de {executions.length} execuções
          </p>

          {/* Table */}
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[40px]"></TableHead>
                  <TableHead>Agente / Cliente</TableHead>
                  <TableHead>Data/Hora</TableHead>
                  <TableHead>Resultados</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Relatório</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredExecutions.length === 0 ? (
                  <TableRow>
                    <td colSpan={6} className="text-center py-8 text-muted-foreground">
                      Nenhum teste encontrado com os filtros aplicados
                    </td>
                  </TableRow>
                ) : (
                  filteredExecutions.map((execution) => (
                    <ExpandableTestRow
                      key={execution.execution_id}
                      execution={execution}
                    />
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

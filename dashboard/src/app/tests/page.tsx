'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { fetchAllTestResults } from '@/lib/supabaseData';
import type { LatestTestResult } from '@/types/database';
import { Search, Calendar, Clock } from 'lucide-react';

type StatusFilter = 'all' | 'passed' | 'failed' | 'warning';

export default function TestsPage() {
  const [testResults, setTestResults] = useState<LatestTestResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [scoreFilter, setScoreFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  useEffect(() => {
    async function loadTests() {
      try {
        const data = await fetchAllTestResults(100);
        setTestResults(data);
      } catch (error) {
        console.error('Error fetching test results:', error);
      } finally {
        setLoading(false);
      }
    }
    loadTests();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-2">
          <div className="text-lg font-medium">Loading test history...</div>
          <div className="text-sm text-muted-foreground">Please wait</div>
        </div>
      </div>
    );
  }

  const getTestStatus = (score: number): 'passed' | 'warning' | 'failed' => {
    if (score >= 8.0) return 'passed';
    if (score >= 6.0) return 'warning';
    return 'failed';
  };

  const filteredTests = testResults
    .filter((test) => {
      const status = getTestStatus(test.overall_score);
      const matchesSearch = test.agent_name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesStatus = statusFilter === 'all' || status === statusFilter;
      const matchesScore =
        scoreFilter === 'all' ||
        (scoreFilter === 'high' && test.overall_score >= 8) ||
        (scoreFilter === 'medium' && test.overall_score >= 7 && test.overall_score < 8) ||
        (scoreFilter === 'low' && test.overall_score < 7);

      return matchesSearch && matchesStatus && matchesScore;
    })
    .sort((a, b) => new Date(b.tested_at).getTime() - new Date(a.tested_at).getTime());

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'passed':
        return 'default';
      case 'warning':
        return 'secondary';
      case 'failed':
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

  // Calculate stats
  const totalTests = testResults.length;
  const passedTests = testResults.filter((t) => getTestStatus(t.overall_score) === 'passed').length;
  const averageDuration = totalTests > 0
    ? Math.round(
        testResults.reduce((acc, test) => acc + test.test_duration_ms, 0) / totalTests / 1000
      )
    : 0;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Test History</h1>
        <p className="text-muted-foreground">
          Complete history of all agent evaluations
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tests</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalTests}</div>
            <p className="text-xs text-muted-foreground">
              All time
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pass Rate</CardTitle>
            <Badge className="h-6">
              {totalTests > 0 ? ((passedTests / totalTests) * 100).toFixed(1) : '0'}%
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{passedTests}</div>
            <p className="text-xs text-muted-foreground">
              Passed tests
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Duration</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{averageDuration}s</div>
            <p className="text-xs text-muted-foreground">
              Per test
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Test Runs</CardTitle>
          <CardDescription>Filter and search through test history</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Filters */}
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by agent name..."
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
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="passed">Passed</SelectItem>
                <SelectItem value="warning">Warning</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
            <Select value={scoreFilter} onValueChange={(value) => setScoreFilter(value as 'all' | 'high' | 'medium' | 'low')}>
              <SelectTrigger className="w-full md:w-[180px]">
                <SelectValue placeholder="Score Range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Scores</SelectItem>
                <SelectItem value="high">8+ (High)</SelectItem>
                <SelectItem value="medium">7-8 (Medium)</SelectItem>
                <SelectItem value="low">&lt;7 (Low)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Results count */}
          <p className="text-sm text-muted-foreground">
            Showing {filteredTests.length} of {testResults.length} test runs
          </p>

          {/* Table */}
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Agent</TableHead>
                  <TableHead>Date & Time</TableHead>
                  <TableHead>Score</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Duration</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTests.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                      No tests found matching your filters
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredTests.map((test) => {
                    const status = getTestStatus(test.overall_score);
                    return (
                      <TableRow key={test.test_result_id}>
                        <TableCell>
                          <Link
                            href={`/agents/${test.agent_version_id}`}
                            className="font-medium hover:underline"
                          >
                            {test.agent_name}
                          </Link>
                          <span className="text-xs text-muted-foreground ml-2">
                            v{test.version}
                          </span>
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {new Date(test.tested_at).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </TableCell>
                        <TableCell>
                          <Badge variant={getScoreBadgeVariant(test.overall_score)}>
                            {test.overall_score.toFixed(1)}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant={getStatusBadgeVariant(status)}>
                            {status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {(test.test_duration_ms / 1000).toFixed(1)}s
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

# AI Factory V4 Testing Dashboard

Modern Next.js 14 dashboard for monitoring and evaluating AI agents performance.

## Features

- **Overview Page** - Dashboard with key metrics, score trends chart, and recent agents
- **Agents Page** - Searchable/filterable table of all agents with status and scores
- **Agent Detail Page** - Deep dive into individual agent performance with dimension breakdowns
- **Tests Page** - Complete history of all test runs with advanced filtering

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **Icons**: lucide-react

## Project Structure

```
dashboard/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Overview dashboard
│   │   ├── agents/
│   │   │   ├── page.tsx          # Agents list
│   │   │   └── [id]/page.tsx     # Agent detail
│   │   ├── tests/
│   │   │   └── page.tsx          # Tests history
│   │   └── layout.tsx            # Root layout with navigation
│   ├── components/
│   │   ├── navigation.tsx        # Top navigation bar
│   │   └── ui/                   # shadcn/ui components
│   ├── lib/
│   │   ├── mockData.ts           # Mock data for testing
│   │   └── utils.ts              # Utility functions
│   └── types/
│       └── index.ts              # TypeScript type definitions
```

## Pages Overview

### 1. Overview Page (`/`)
- **Stats Cards**: Total Agents, Average Score, Tests Run, Pass Rate
- **Score Trends Chart**: Visual timeline of average scores
- **Recent Agents**: Last 5 agents tested with quick links

### 2. Agents Page (`/agents`)
- **Filterable Table**: Search by name, filter by status/score range
- **Columns**: Name, Version, Score, Status, Last Evaluation
- **Click**: Navigate to agent detail page

### 3. Agent Detail Page (`/agents/[id]`)
- **Header**: Agent name, version, status, overall score
- **Dimension Scores**: 5 performance bars (reasoning, safety, performance, adaptability, communication)
- **Strengths/Weaknesses**: Categorized insights
- **Test History**: Timeline of all evaluations
- **Action**: View Full HTML Report button

### 4. Tests Page (`/tests`)
- **Stats**: Total tests, pass rate, average duration
- **Filterable Table**: Search by agent, filter by status/score
- **Columns**: Agent, Date & Time, Score, Status, Duration

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Data Structure

Currently using mock data from `/src/lib/mockData.ts`. Replace with real API calls:

```typescript
// Example: Fetch agents from API
const response = await fetch('/api/agents');
const agents = await response.json();
```

### Key Types

```typescript
type AgentStatus = 'active' | 'draft' | 'archived';

interface Agent {
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

interface TestRun {
  id: string;
  agentId: string;
  agentName: string;
  date: string;
  score: number;
  status: 'passed' | 'failed' | 'warning';
  duration: number;
}
```

## Customization

### Adding New Components

```bash
npx shadcn@latest add [component-name]
```

### Color Scheme

Edit `/src/app/globals.css` to customize theme colors:

```css
@layer base {
  :root {
    --primary: 222.2 47.4% 11.2%;
    --secondary: 210 40% 96.1%;
    /* ... */
  }
}
```

## Next Steps

1. **API Integration**: Replace mock data with real backend
2. **Authentication**: Add user login/permissions
3. **Real-time Updates**: Implement WebSocket for live test results
4. **Export Features**: PDF/CSV export for reports
5. **Advanced Analytics**: More charts and insights

## Contributing

Built with Next.js 14 best practices:
- Server Components by default
- Client Components only when needed (filters, interactive elements)
- Type-safe with TypeScript
- Responsive design (mobile-first)
- Accessible UI components (shadcn/ui)

## License

MIT

---

**Built for**: AI Factory V4 Testing Framework
**Stack**: Next.js 14 + TypeScript + Tailwind + shadcn/ui
**Created**: 2025-12-31

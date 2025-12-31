# Quick Start Guide

## Immediate Access

**The dashboard is already running!**

Visit: **http://localhost:3000**

## Pages Available

1. **http://localhost:3000** - Overview Dashboard
2. **http://localhost:3000/agents** - Agents List
3. **http://localhost:3000/agents/agent-1** - Agent Detail (example)
4. **http://localhost:3000/tests** - Tests History

## What You Can Do Right Now

### Navigate
- Click on any agent name to see details
- Use the top navigation to switch between pages
- Filter agents by status and score
- Search for specific agents or tests

### Test the Filters
On the Agents page:
- Try searching for "Support"
- Filter by "Active" status
- Select "8+ (High)" score range

On the Tests page:
- Search by agent name
- Filter by test status (passed/failed/warning)
- See pass rate statistics

### Explore Agent Details
Click on "Customer Support Agent" to see:
- Overall score: 8.7
- 5 dimension breakdowns
- Strengths and weaknesses
- Complete test history

## File Locations

All important files are in:
```
/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/src/
```

### To Edit Mock Data
```
/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/src/lib/mockData.ts
```

### To Edit Pages
```
/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/src/app/page.tsx           (Overview)
/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/src/app/agents/page.tsx   (Agents List)
/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/src/app/tests/page.tsx    (Tests)
```

### To Edit Styles
```
/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/src/app/globals.css
```

## Commands

### Stop Server
```bash
# Press Ctrl+C in the terminal where npm run dev is running
```

### Restart Server
```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard
npm run dev
```

### Build for Production
```bash
npm run build
npm start
```

## Next: Connect Real Data

Replace the mock data in any component:

```typescript
// OLD (current):
import { agents } from '@/lib/mockData';

// NEW (with API):
const agents = await fetch('/api/agents').then(r => r.json());
```

Create API routes in:
```
/Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard/src/app/api/
```

Example API route:
```typescript
// src/app/api/agents/route.ts
export async function GET() {
  const agents = await fetchFromDatabase();
  return Response.json(agents);
}
```

## Troubleshooting

### Port Already in Use
If port 3000 is busy:
```bash
# Kill existing process
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm run dev
```

### TypeScript Errors
```bash
# Rebuild types
npm run build
```

### Missing Dependencies
```bash
npm install
```

## Features to Add

1. **Authentication**: Add login/logout
2. **Real API**: Connect to backend
3. **Real-time**: WebSocket updates
4. **Export**: Download reports as PDF
5. **Charts**: Add more visualization libraries

## Documentation

- Full details: `README.md`
- Build summary: `SUMMARY.md`
- This guide: `QUICKSTART.md`

---

**You're all set! The dashboard is working with mock data.**

Try clicking around and exploring the interface.

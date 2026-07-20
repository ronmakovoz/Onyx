# Second Nature CX Intelligence OS

An Onyx-inspired Customer Success intelligence dashboard tailored to Second
Nature's enterprise AI role-play and coaching platform. All account, portfolio,
learner, performance, and cost data is synthetic demonstration data.

## Prerequisites

- Node.js `>=22.13.0`

## Quick Start

```bash
npm install
npm run dev
npm run build
```

This project does not use `wrangler.jsonc`.

## Product Areas

- Executive portfolio health and renewal risk
- Customer 360 with learner, role-play, certification, and readiness telemetry
- Rollout command center and CSM performance
- Platform whitespace and expansion recommendations
- Enablement briefings and AI agent workflows
- Second Nature integration model, audit, and cost visibility
- Owner-only activity analytics for opens, navigation, clicks, and engagement time

## Anthropic

Copy `.env.example` to `.env.local` and set `ANTHROPIC_API_KEY` to enable live
Claude-generated briefings and agent reports. Without a key, the application
uses clearly labeled deterministic demo outputs.

## Commands

- `npm run dev`: start local development
- `npm run build`: create the production vinext worker bundle
- `npm test`: build and verify the rendered dashboard routes

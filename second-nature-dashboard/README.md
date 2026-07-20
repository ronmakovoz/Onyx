# Second Nature Resident Experience Intelligence OS

An Onyx-inspired Customer Success intelligence dashboard tailored to Second
Nature's property-management Resident Experience Platform. It models Resident
Onboarding, Resident Benefits Packages, Maestro orchestration, portfolio
activation, renewals, and expansion. All account, resident, portfolio,
performance, and cost data is synthetic demonstration data.

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
- Customer 360 with doors, residents, onboarding, RBP activation, and lease telemetry
- Launch command center and CSM performance
- Resident-experience whitespace and expansion recommendations
- Executive briefings and Anthropic-powered agent workflows
- Maestro and property-accounting integration model, audit, and cost visibility
- Owner-only activity analytics for opens, navigation, clicks, and engagement time

## Anthropic

Copy `.env.example` to `.env.local` and set `ANTHROPIC_API_KEY` to enable live
Claude-generated briefings and agent reports. Without a key, the application
uses clearly labeled deterministic demo outputs.

## Commands

- `npm run dev`: start local development
- `npm run build`: create the production vinext worker bundle
- `npm test`: build and verify the rendered dashboard routes

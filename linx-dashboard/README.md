# Linx CX Intelligence OS

An Onyx-inspired Customer Success intelligence dashboard tailored to Linx
Security's identity-security platform. All account, portfolio, usage, and cost
data in this project is synthetic demonstration data.

## Prerequisites

- Node.js `>=22.13.0`

## Quick Start

```bash
npm install
npm run dev
npm run build
```

This starter does not use `wrangler.jsonc`.

## Product Areas

- Executive portfolio health and renewal risk
- Customer 360 and identity-program telemetry
- Implementation command center and CSM performance
- Product whitespace and expansion recommendations
- Account briefings and AI agent workflows
- Linx architecture, model routing, audit, and cost visibility
- Owner-only activity analytics for opens, navigation, clicks, and engagement time

## Anthropic

Copy `.env.example` to `.env.local` and set `ANTHROPIC_API_KEY` to enable live
Claude-generated briefings and agent reports. Without a key, the application
uses clearly labeled deterministic demo outputs.

## Commands

- `npm run dev`: start local development
- `npm run build`: create the production vinext worker bundle
- `npm test`: build and verify the rendered dashboard routes

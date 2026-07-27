# Blinkit Growth Team Graduation Project

## Problem Statement

### AI-Powered Product Discovery Engine for Blinkit

You are building an AI-powered customer discovery engine for Blinkit's Growth Team.

## Background

Quick commerce has become part of users' weekly routines.

- Customers repeatedly purchase the same grocery items every week.
- Although Blinkit offers products across dozens of categories, users rarely discover new categories organically.

**Examples:**

| From | To |
|------|-----|
| Grocery | Pet Care |
| Snacks | Personal Care |
| Dairy | Baby Care |
| Household Essentials | Electronics |
| Fruits | Health Supplements |

**Blinkit's strategic growth objective is:**

Increase the percentage of Monthly Active Customers that purchase from at least one new category every month.

Instead of directly proposing features, the objective is to first understand **why customers fail to discover new categories**.

## Project Objective

Build an AI-powered customer research platform that continuously gathers, analyzes, and synthesizes customer feedback from multiple sources to identify opportunities for increasing cross-category discovery.

The platform should answer questions like:

- Why do users repeatedly purchase the same categories?
- Why don't users explore?
- What blocks category expansion?
- Which customer segments naturally explore?
- Which segments never explore?
- What information is missing before trying a new category?
- Which trust barriers exist?
- Which shopping habits prevent discovery?
- Which recurring complaints emerge across platforms?
- Which unmet needs appear consistently?

**After identifying insights:**

1. Validate them through user interviews.
2. Design an AI-native MVP.
3. Deploy the MVP.

## Data Sources

The discovery engine should support multiple customer feedback sources.

**Examples:**

| Category | Sources |
|----------|---------|
| Reviews | Google Play Reviews, Apple App Store Reviews |
| Communities | Reddit, Quora, Local discussion forums |
| Social Media | X, LinkedIn, Instagram comments, YouTube comments |
| Product Discussions | Consumer forums, Grocery discussions, Quick commerce communities |
| Internal Research | User interviews, Survey responses |

## AI Stack

You may use any AI-native architecture.

**Examples:**

- **Tools:** Cursor, Claude, GPT, Gemini, Groq, LangChain, LangGraph, CrewAI, AutoGen, n8n, Zapier, RAG
- **Vector stores:** Pinecone, Chroma, Qdrant, FAISS, Supabase Vector
- **Data & backend:** PostgreSQL, FastAPI
- **Frontend:** Streamlit, React, NextJS

**Preferred LLM:** Groq

## Required Output

The system should automatically:

### 1. Collect data

Gather reviews from multiple sources.

### 2. Clean data

- Remove duplicates
- Remove spam
- Normalize text
- Detect language
- Translate when necessary

### 3. Analyze

Use LLMs to identify:

- Themes
- Complaints
- Motivations
- Unmet needs
- Opportunities
- Emotions
- Jobs-to-be-done
- Shopping behaviors

### 4. Cluster

Automatically cluster reviews into themes.

**Examples:** Category Discovery, Shopping Habit, Price, Search, Recommendations, Trust, Delivery, Availability, Subscription, Coupons, etc.

### Generate insights

Every insight should include:

- Problem
- Evidence
- Frequency
- Example reviews
- Customer segment
- Business impact
- Potential opportunity
- Confidence score

### Validate

The system should compare findings across Play Store, App Store, Reddit, Forums, Interviews, and Surveys, and identify:

- Consistent insights
- Contradicting insights
- Weak insights
- High-confidence insights

## User Research

The project should include a research module.

**Store:**

- Interview notes
- Survey responses
- Affinity mapping
- JTBD
- Pain points
- User segments
- Behavior patterns

**Research synthesis:** Compare AI insights against actual interviews. Highlight validated assumptions, rejected assumptions, and new discoveries.

## AI-Native MVP

After identifying opportunities, design an AI-powered solution.

**Possible MVPs:**

- AI Shopping Assistant
- AI Discovery Feed
- AI Category Explorer
- AI Recommendation Agent
- AI Meal Planner
- AI Smart Basket Expansion
- AI Personalized Home Feed
- AI Discovery Coach
- AI Weekly Shopping Planner

The MVP should be deployable.

## Deliverables

The repository should generate:

- Review Analysis Workflow
- Architecture Diagram
- Workflow Diagram
- Research Repository
- Interview Repository
- Survey Repository
- Problem Statement
- Opportunity Assessment
- Final MVP
- Deployment Guide
- Presentation Assets

## Project Structure

Create a `docs/` folder:

```
docs/
  problemStatement.md
  context.md
  architecture.md
  implementation-plan.md
  workflow.md
  review-analysis.md
  research-plan.md
  interview-guide.md
  survey-plan.md
  problem-definition.md
  mvp-design.md
  deployment-plan.md
  edge-cases.md
  future-roadmap.md
```

## Context

Generate `context.md` including:

- Background
- Business goal
- Success metrics
- Assignment scope
- Customer behavior
- Business constraints
- North Star Metric
- Primary KPIs
- Secondary KPIs
- Assumptions
- Non-goals
- Glossary

## Architecture

Generate `architecture.md` describing:

- System Overview
- Data Pipeline
- Review Ingestion Layer
- Preprocessing Layer
- Embedding Pipeline
- Vector Database
- LLM Analysis Engine
- Theme Extraction Engine
- Sentiment Analysis
- Insight Generator
- Research Repository
- Recommendation Engine
- Frontend
- Backend
- Deployment
- Scalability
- Failure Recovery
- Monitoring
- Security
- Prompt Management

## Implementation Plan

Generate `implementation-plan.md` split into phases:

| Phase | Focus |
|-------|--------|
| **Phase 1** | Project Setup — folder structure, environment, dependencies, backend, frontend, configuration |
| **Phase 2** | Review Collection — Play Store, App Store, CSV, JSON, manual upload |
| **Phase 3** | Preprocessing — cleaning, normalization, deduplication, language detection, translation, tokenization, embeddings |
| **Phase 4** | LLM Analysis — theme detection, pain points, sentiment, emotion, segmentation, JTBD, opportunity detection, insight ranking, confidence score (**use Groq instead of OpenAI**) |
| **Phase 5** | Research Repository — interview upload, survey upload, research comparison, AI validation, problem definition |
| **Phase 6** | AI-native MVP — backend, frontend, deployment, testing |

## Edge Cases

Generate `edge-cases.md` to handle:

- Empty reviews
- Duplicate reviews
- Unsupported language
- Hallucinations
- LLM failures
- Missing fields
- Corrupted CSV
- Low confidence insights
- Conflicting themes
- Timeouts
- API failures

## Implementation Prompts

Generate sequential prompts:

- Implement Phase 1
- Implement Phase 2
- Implement Phase 3
- Implement Phase 4
- Implement Phase 5
- Implement Phase 6

## Frontend

Build a modern AI-native product.

**Preferred:** React, NextJS, Tailwind, ShadCN, Framer Motion — responsive, accessibility compliant, portfolio quality.

**Dashboard should include:**

- Review Upload
- Review Sources
- Review Statistics
- Theme Distribution
- Sentiment Charts
- Opportunity Dashboard
- Customer Segments
- Insight Cards
- Interview Repository
- Survey Repository
- Problem Statement
- AI Recommendations
- MVP Demo

## Deployment

**Case 1:** Frontend basic — deploy everything on Streamlit.

**Case 2:**

- Frontend: Vercel
- Backend: Railway / Render
- Database: Supabase

Generate `deployment-plan.md` including environment variables, secrets, production config, logging, monitoring, CI/CD (GitHub), deployment steps, and rollback strategy.

## Testing

Generate:

- Manual Testing Checklist
- Unit Tests
- Integration Tests
- Prompt Evaluation
- LLM Evaluation
- Performance Testing
- Edge Case Testing
- Research Validation

## Final Output

The repository should produce:

- ✓ AI Discovery Engine
- ✓ Review Analysis Workflow
- ✓ Research Repository
- ✓ User Interview Repository
- ✓ Survey Repository
- ✓ Problem Definition
- ✓ Opportunity Assessment
- ✓ AI-native MVP
- ✓ Production Deployment
- ✓ Presentation-ready Assets
- ✓ Documentation
- ✓ Architecture
- ✓ Workflow Diagrams
- ✓ GitHub-ready Repository

## Additional Instruction for Cursor

Always follow a **documentation-first** development workflow:

1. Create or update the relevant document in `docs/` before implementing code.
2. Keep architecture, implementation plan, and deployment plan synchronized with code changes.
3. Build incrementally, phase by phase.
4. Prefer **Groq** as the LLM provider.
5. Design for modularity so additional review sources and AI workflows can be added later without major refactoring.
6. Produce clean, production-ready code with proper logging, error handling, testing, and deployment support.

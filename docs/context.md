# Context

**Project:** AI-Powered Product Discovery Engine for Blinkit

## Background

Quick commerce is part of weekly routines for many urban Indian shoppers. Blinkit users often reorder the same grocery and essentials categories. Cross-category discovery is a strategic growth lever: increasing the share of monthly active customers who buy from at least one new category per month.

## Business goal

Understand why customers fail to discover new categories, then validate and ship an AI-native intervention grounded in multi-source feedback (app reviews, surveys, interviews).

## North Star Metric

Percentage of Monthly Active Customers who purchase from at least one **new** category each month.

## Primary KPIs

- Cross-category purchase rate (new category per MAU per month)
- Recommendation acceptance rate (when MVP ships)
- Insight confidence score distribution from the research platform

## Secondary KPIs

- Review corpus size and source coverage
- Survey/interview triangulation agreement rate
- Time from ingest to ranked opportunity list

## Assignment scope

- Ingest and analyze public Blinkit app reviews (Play Store, App Store India)
- Integrate primary survey and interview research
- Produce ranked, evidence-backed insights
- Design and deploy a deployable AI-native MVP (default candidate: Smart Basket Expansion)

## Customer behavior (hypotheses)

- Search-first, closed-list shopping dominates
- Trust in recommendations is moderate; transparency builds trust
- Price and fees surface more often than discovery in open feedback

See [`research-findings.md`](../research-findings.md) for Wave 1 survey evidence.

## Business constraints

- Prefer **Groq** as LLM provider
- Documentation-first development
- Modular collectors and analysis pipelines
- Portfolio-quality frontend; production-capable backend

## Assumptions

- App store reviews contain signal on discovery, trust, search, and delivery
- Survey sample is directional until Wave 2 quotas are met
- MVP value is framed as alternatives/reminders, not “explore more categories”

## Non-goals

- Replacing Blinkit’s production recommendation system
- Real-time personalization at Blinkit scale in the graduation project timeline
- Scraping sources that violate terms of service beyond documented public APIs

## Glossary

| Term | Definition |
|------|------------|
| Cross-category discovery | User buys from a category they had not bought from before on Blinkit |
| Insight | Structured finding with evidence, frequency, segment, and confidence |
| Triangulation | Comparing AI-derived insights with surveys and interviews |
| JTBD | Jobs-to-be-done framing from review or interview text |

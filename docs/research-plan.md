# Research Plan

**Project:** AI-Powered Product Discovery Engine for Blinkit  
**Companion docs:** [`problemStatement.md`](./problemStatement.md) · [`survey-plan.md`](./survey-plan.md) · [`review-analysis.md`](./review-analysis.md)

---

## 1. Purpose

Phase 5 closes the loop between **scaled AI signals** (app store reviews) and **primary human research** (interviews, surveys). The platform must store human evidence, code it into the same theme taxonomy as Phase 4, triangulate every AI insight, and rank opportunities for MVP selection.

---

## 2. Research Tracks

| Track | Method | Repository table | Coding |
|-------|--------|------------------|--------|
| Depth interviews | 30–45 min semi-structured calls / async transcripts | `interviews` | LLM-assisted coding with transcript span citations |
| Quantitative survey | Self-administered questionnaire (Wave 1 fielded) | `surveys` | Per-question aggregation + segment breakdowns |
| Secondary | Play Store / App Store reviews | `reviews` | Phase 3–4 pipeline |

Wave 1 survey details: [`survey-plan.md`](./survey-plan.md). Raw CSV: [`../data/primary-survey-responses.csv`](../data/primary-survey-responses.csv).

---

## 3. Interview Program

### Target sample (Wave 1)

| Segment | n | Rationale |
|---------|---|-----------|
| Metro salaried 25–34 | 2 | Matches dominant survey cohort; habit + search barriers |
| Parent (child under 5) | 1 | Baby Care expansion category |
| Pet owner | 1 | Pet Care latent demand |
| Price-sensitive / student | 1 | Discount-led discovery |
| Heavy user / skeptic | 1 | Tests AI recommendation appetite vs survey |

Minimum **5 coded interviews** before triangulation runs.

### Procedure

1. Recruit via personal network (same constraints as survey Wave 1).
2. Use [`interview-guide.md`](./interview-guide.md) — ~12 questions, 35 minutes core.
3. Record notes or transcript; upload via `POST /api/research/interviews/upload` or JSON body.
4. Run `POST /api/research/interviews/code-all` to extract pain points, JTBD, discovery barriers, and cited quotes.
5. Affinity-map coded output to Phase 4 theme categories.

---

## 4. Survey Program

Wave 1 is **directional only** (n=12, convenience sample). Ingestion expands each CSV row into normalized `surveys` rows (one row per closed question + open-text fields).

Analysis outputs:

- Univariate counts per question key
- Segment breakdown (`respondent_segment` derived from age_group + occupation)
- Cross-tabs: discovery frequency × shopping mode × order frequency

PII rule: respondent names are replaced with pseudonyms (`R01`…`R12`) at ingest; real names never persist in the database.

---

## 5. Affinity Mapping

Human findings (interview quotes, survey open text, coded pain points) are grouped under the shared taxonomy:

`Category Discovery`, `Shopping Habit`, `Price`, `Search`, `Recommendations`, `Trust`, `Delivery`, `Availability`, `Subscription`, `Coupons`

Mapping uses keyword + barrier alignment first; optional LLM refinement when `GROQ_API_KEY` is set.

---

## 6. Triangulation Engine

For each AI `insights` row, compare:

1. **Theme overlap** — insight theme category vs affinity groups from interviews/surveys  
2. **Barrier alignment** — discovery barriers in insight evidence vs coded barriers  
3. **Survey prevalence** — supporting counts for matching survey question keys  

| Status | Meaning |
|--------|---------|
| `validated` | Human evidence supports the insight problem statement |
| `partially_supported` | Mixed or weak human signal |
| `rejected` | Human evidence contradicts the AI claim |
| `new_discovery` | Human-only theme with no matching AI insight (feeds opportunity list) |

Each insight receives `Validation` rows with `source_type` `interview` / `survey` and cited human evidence in `notes`.

---

## 7. Opportunity Assessment

Validated problems (and selected `new_discovery` items) are scored on:

| Dimension | Weight | Source |
|-----------|--------|--------|
| Reach | 25% | Survey counts + interview segment spread |
| Severity | 25% | Pain intensity in coding + open text |
| North-star impact | 35% | Category expansion / basket adjacency relevance |
| Implementation effort | 15% | Inverse effort (lower effort scores higher) |

Top opportunities are persisted in `opportunities` with a JSON `scoring_rationale` for dashboard display.

---

## 8. Problem Definition Output

`POST /api/research/problem-definition/generate` writes [`problem-definition.md`](./problem-definition.md): a sharpened problem statement citing review IDs, interview quotes, and survey counts.

---

## 9. Acceptance Criteria (Phase 5)

- ≥5 interviews and ≥1 survey wave stored and coded  
- Every AI insight has an explicit validation status with human evidence citations  
- ≥1 insight marked `rejected` by interview/survey data  
- Top 3 opportunities ranked with visible scoring rationale  

# Survey Plan

**Project:** AI-Powered Product Discovery Engine for Blinkit
**Companion docs:** [`problemstatement.md`](./problemstatement.md) · [`research-findings.md`](./research-findings.md) · [`implementation-plan.md`](./implementation-plan.md)
**Raw data:** [`data/primary-survey-responses.csv`](./data/primary-survey-responses.csv)

---

## 1. Purpose

The survey is the primary quantitative input to the discovery problem. Its job is to establish *what* shoppers say about category discovery in a structured, countable form, so that app store review mining can test prevalence at scale and depth interviews can explain causes.

It is deliberately not the instrument that answers "why." Section 8 sets out what this survey can and cannot conclude.

---

## 2. Research Objectives

Each objective maps to a question the problem statement requires the platform to answer.

| Objective | Problem statement question | Instrument coverage |
|-----------|---------------------------|---------------------|
| Measure basket repetition | Why do users repeatedly purchase the same categories? | Q1, Q2, Q4 |
| Identify discovery barriers | What blocks category expansion? | Q6 |
| Locate the discovery surface | Which shopping habits prevent discovery? | Q3 |
| Segment explorers vs. non-explorers | Which segments explore and which never do? | Q5 cross-tabbed with Q1, Q2, age |
| Test intervention appetite | What information is missing before trying a new category? | Q7, Q10 |
| Measure trust barriers | Which trust barriers exist? | Q8, Q9, Q11, Q12 |
| Surface unprompted pain | Which recurring complaints and unmet needs emerge? | Q13, Q14, Q15 |

---

## 3. Sampling Approach

### Wave 1 — as fielded

| Parameter | Value |
|-----------|-------|
| Method | Self-administered online questionnaire |
| Recruitment | Convenience and snowball sampling through personal network |
| Fielding window | 24–26 July 2026 |
| Responses | 12 submissions from 11 unique respondents |
| Screening | None — no filter on Blinkit usage or order recency |
| Incentive | None |

Wave 1 was an unscreened convenience sample, which is why its output is treated as directional signal rather than measurement.

### Wave 2 — planned

Wave 1's composition, not its size, is its main weakness. Ten of 12 respondents were 25–34 and none were over 34. Three of the five target expansion categories in the brief — Pet Care, Baby Care, Health Supplements — are bought disproportionately by pet owners, parents, and older shoppers, so Wave 1 systematically missed the people the project most needs to hear from.

Wave 2 therefore uses quota sampling rather than open recruitment:

| Quota | Target | Rationale |
|-------|--------|-----------|
| Age 35+ | ≥ 30% of responses | Wave 1 had zero |
| Parents of children under 5 | ≥ 20% | Carries Baby Care |
| Pet owners | ≥ 20% | Carries Pet Care |
| Tier 2/3 city residents | ≥ 25% | Wave 1 was metro-heavy; two respondents raised small-town coverage unprompted |
| Non-explorers (Q5 = Rarely or Never) | ≥ 40% | The segment the project exists to move |
| Target n | 80–120 | Minimum for credible sub-group comparison |

Screening question to add at the top: *Have you ordered from Blinkit in the last 30 days?* Respondents answering no route to a short lapsed-user branch instead of the main instrument.

---

## 4. Instrument — Wave 1 as Fielded

**A note on fidelity:** the answer options below are reconstructed from the response data. Options that no respondent selected are invisible in the exported results, so this list is a lower bound on what was shown. Where the full option set is uncertain it is marked.

### Screening and demographics

| # | Question | Type | Options |
|---|----------|------|---------|
| D1 | Name | Open text | Optional — left blank by 1 respondent |
| D2 | Age | Single choice | `18-24` · `25-34` (higher brackets presumed offered, none selected) |
| D3 | What is your occupation? | Single choice | `Salaried Professional` · `Student` · `Freelancer` (further options presumed, none selected) |
| D4 | City | Open text | — |

### Behaviour

**Q1. How often do you order from Blinkit?** *(single choice)*
`Daily` · `2–3 times a week` · `Once a week` · `2–3 times a month` (lower-frequency options presumed offered)

**Q2. What do you usually buy on Blinkit?** *(select all that apply)*
`Fruits & Vegetables` · `Dairy` · `Snacks` · `Beverages` · `Personal Care` · `Household Essentials` · `Electronics` · free-text other

**Q3. How do you usually shop on Blinkit?** *(single choice)*
`I search for exactly what I need` · `I browse categories` · `A mix of the above`

**Q4. Approximately what percentage of your order consists of products you've purchased before?** *(single choice)*
`Less than 25%` · `25–50%` · `50–75%` · `More than 75%`

**Q5. How often do you discover and buy completely new products on Blinkit?** *(single choice)*
`Very often` · `Sometimes` · `Rarely` · `Never` (Never presumed offered, none selected)

### Barriers

**Q6. If you rarely buy new products, why?** *(select all that apply — conditional on Q5)*
`I already know what I need` · `Recommendations don't feel relevant` · `I don't trust recommendations` · `I forget to check new categories` · `Too many products to browse` · `I don't have time to explore` · `New products seem expensive`

**Q7. Which of these would encourage you to try a new product?** *(select all that apply)*
`Discounts` · `Personalized recommendations` · `Similar to products I already buy` · `Trending among people like me` · `Recommended by AI` · `Reviews & ratings` · `Bundles` · `Free samples`

### AI appetite and trust

**Q8. Have you ever purchased something because Blinkit recommended it?** *(single choice)*
`Never` · `Once or twice` · `Sometimes` (a higher-frequency option presumed offered)

**Q9. Imagine Blinkit had an AI Shopping Assistant that understood your shopping habits. How interested would you be?** *(single choice)*
`Not Interested` · `Somewhat Interested` · `Interested` · `Extremely Interested`

**Q10. Which AI recommendations would be most useful?** *(select up to 3 — cap not enforced)*
`"People with similar shopping habits also bought…"` · `Healthier alternatives` · `Cheaper alternatives` · `Premium alternatives` · `New products matching my preferences` · `Recipes based on my cart` · `Weekly shopping suggestions` · `Seasonal recommendations` · `Reminders before I run out of items`

**Q11. How much would you trust AI recommendations?** *(1–5 scale, 1 lowest, 5 highest)*

**Q12. What would make you trust AI recommendations more?** *(select all that apply)*
`Explain why it is recommended` · `Show customer reviews` · `Tell me how many people bought it` · `Show similar past purchases` · `Allow me to dismiss recommendations` · `Personalization improves over time`

### Open text

**Q13.** What's the biggest frustration while shopping on Blinkit?
**Q14.** If you could improve one thing about Blinkit's shopping experience, what would it be?
**Q15.** Any additional suggestions?

---

## 5. Known Defects in the Wave 1 Instrument

These are documented rather than quietly fixed, because several of them change how the Wave 1 results may be read.

| # | Defect | Consequence |
|---|--------|-------------|
| 1 | Q2 omitted Pet Care, Baby Care, and Health Supplements | The most damaging flaw. Three of the five target expansion categories were never offered, so their absence from results is an artefact and **cannot** be cited as evidence users don't buy them |
| 2 | Q10's "select up to 3" cap was not enforced | One respondent selected 9 options. Q10 counts are inflated and not comparable between respondents |
| 3 | Q6 conditional logic leaked | A respondent who answered "Very often" to Q5 still answered Q6; another left it blank. The denominator for Q6 is ambiguous |
| 4 | No screening question | Usage recency and eligibility are unverified |
| 5 | Q5 and Q4 use vague frequency labels | "Sometimes" and "Rarely" are interpreted differently across respondents; one participant answering twice gave different answers three days apart |
| 6 | No repeat-submission control | One respondent submitted twice, so 12 responses represent 11 people |
| 7 | Q8 and Q9 are adjacent and leading | Asking about AI interest straight after a recommendation question invites acquiescence bias, which the trust score in Q11 partly exposes |
| 8 | No question on the discovery moment itself | Nothing asks when or where a user last considered a new category, so the instrument captures attitudes but not the decision context |
| 9 | Demographics collected names | Personally identifying data in a repository intended to be public — see section 7 |

---

## 6. Instrument — Wave 2 Revisions

### Fixes to existing questions

- **Q2:** add `Pet Care`, `Baby Care`, `Health Supplements`, `Home & Kitchen`, `Stationery`, `Frozen Food`. Without these the survey cannot speak to the brief.
- **Q5 and Q1:** replace vague adverbs with anchored counts — *"In your last 5 Blinkit orders, how many included a product you had never bought before?"* with options `0` · `1` · `2` · `3+`. Recall over a bounded window is far more reliable than "sometimes."
- **Q6:** make the branch unconditional and reword to *"What makes you less likely to try a product you haven't bought before?"* so every respondent answers and the denominator is clean.
- **Q10:** enforce the 3-option cap in the form logic, or drop the cap and switch to a ranking question.
- **Q12:** keep as is. It produced the survey's most actionable output and needs no change.

### Questions to add

| # | Question | Type | Why |
|---|----------|------|-----|
| N1 | Have you ordered from Blinkit in the last 30 days? | Screen | Eligibility |
| N2 | Do you have children under 5? / Do you own a pet? | Single choice | Enables the Baby Care and Pet Care quotas and the cross-tabs the brief needs |
| N3 | Think of the last time you considered buying from a category you'd never tried on Blinkit. What happened? | Open text | Captures the decision moment — the biggest gap in Wave 1 |
| N4 | Which of these have you bought *outside* Blinkit in the last month? *(same category list as Q2)* | Multi-select | Reveals latent demand Blinkit is losing, which is the actual size of the discovery opportunity |
| N5 | Where in the app would you most want a suggestion to appear? | Single choice | Tests the section 4 finding in `research-findings.md` that only in-flow surfaces will be seen: `Search results` · `Cart` · `Checkout` · `Home feed` · `Order confirmation` · `Nowhere` |
| N6 | If a suggestion turned out to be a poor fit, what would you do? | Single choice | Measures tolerance for recommendation error before trust is lost |

N4 is the highest-value addition. Wave 1 measured what people buy on Blinkit but never asked what they buy elsewhere, which is precisely where the cross-category opportunity is quantifiable.

### Question order

Move the AI questions (Q8–Q12) *after* the unprompted open-text questions. Wave 1 asked about AI enthusiasm before asking what frustrates people, which primes respondents toward the solution the project already has in mind. Reversing the order gives a cleaner read on whether discovery surfaces as a problem on its own.

---

## 7. Data Handling

| Concern | Approach |
|---------|----------|
| Storage | Exported to `data/primary-survey-responses.csv`, one row per submission, header matching the schema in `implementation-plan.md` |
| Pipeline ingestion | Loaded through the CSV collector into the `surveys` table in Phase 5 |
| Deduplication | Repeat submissions flagged in `data_quality_note` rather than deleted, so the analysis can choose whether to include them |
| Data quality flags | Column-shift recovery, blank fields, and instrument violations recorded per row |
| **PII** | Wave 1 collected respondent names and cities. Before the repository is made public, names must be replaced with pseudonymous IDs (`R01`…`R12`) and the mapping kept out of version control. City can stay; it is analytically useful and not identifying on its own |
| Consent | Wave 1 had no explicit consent statement. Wave 2 must open with one covering purpose, storage, and the fact that responses appear in a public portfolio project |

The PII point is a release blocker, not a nice-to-have: the current CSV carries eleven real names.

---

## 8. Analysis Plan

1. **Univariate counts** for every closed question, reported as counts out of n rather than percentages while n stays below 30.
2. **Cross-tabs** that matter for the brief: Q5 discovery frequency against Q1 order frequency, Q3 shopping mode, age, and household composition. The explorer / non-explorer split is the segmentation the problem statement asks for.
3. **Gap analysis** on N4 versus Q2 — categories bought elsewhere but not on Blinkit, sized per respondent.
4. **Open-text coding** of Q13–Q15 into the shared theme taxonomy (Category Discovery, Shopping Habit, Price, Search, Recommendations, Trust, Delivery, Availability, Subscription, Coupons) so survey text and app store reviews are directly comparable.
5. **Triangulation** in Phase 5: each survey finding enters as an explicit hypothesis and receives a validation status of validated, rejected, partially supported, or contradicted against review and interview evidence.

### What this survey can and cannot conclude

It can identify which barriers exist and are worth testing at scale, and it can rank stated intervention preferences within the sample. With Wave 1's n it cannot establish prevalence, and it cannot support any claim about Blinkit's user base as a whole. Stated interest in AI features is also a weak predictor of behaviour, so Q9 should never be quoted as demand — the trust score in Q11 is the more honest number.

---

## 9. Success Criteria for Wave 2

- All quotas in section 3 met.
- Every defect in section 5 closed.
- Q6 answered by 100% of respondents with an unambiguous denominator.
- At least 30 responses from self-identified non-explorers, enough to compare that segment against explorers.
- N4 gap analysis produces a ranked list of categories with latent demand, sized by respondent count.
- Consent statement present and all PII pseudonymised before commit.

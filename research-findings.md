# Research Findings

**Project:** AI-Powered Product Discovery Engine for Blinkit
**Companion docs:** [`problemstatement.md`](./problemstatement.md) · [`implementation-plan.md`](./implementation-plan.md)
**Raw data:** [`data/primary-survey-responses.csv`](./data/primary-survey-responses.csv)

---

## 1. Research Design

| Track | Method | Status |
|-------|--------|--------|
| Primary | Self-administered online questionnaire, 15 questions, convenience sample | 12 responses collected 24–26 Jul 2026 |
| Secondary | Public app store review mining (Play Store, App Store India) | Sources registered, ingestion pending Phase 2 |

### Secondary source registry

These are the ingestion targets for the Phase 2 collectors. The identifiers below are what the collector configuration needs.

| Source | App | Identifier | Collector config |
|--------|-----|-----------|-----------------|
| Google Play Store | Blinkit: Grocery in 10 minutes | `com.grofers.customerapp` | `lang=en`, `country=in` |
| Apple App Store (India) | Blinkit: Groceries & More | `960335206` | `country=in` |

Source URLs:
- https://play.google.com/store/apps/details?id=com.grofers.customerapp&hl=en_IN
- https://apps.apple.com/in/app/blinkit-groceries-more/id960335206

A deliberate note on sequencing: the survey findings below should be treated as **hypotheses to test against review data**, not as conclusions. With 12 responses the survey cannot establish prevalence; the app store corpus can. The triangulation step in Phase 5 exists precisely to resolve the two against each other.

---

## 2. Sample Profile

12 responses from **11 unique respondents** — one participant (Kham) submitted twice, on 24 Jul and 26 Jul.

| Attribute | Distribution |
|-----------|-------------|
| Age | 25–34: 10 · 18–24: 1 · not stated: 1 |
| Occupation | Salaried professional: 6 · Student: 1 · Freelancer: 1 · not stated: 4 |
| City | Guwahati: 4 · Mumbai: 3 · Bengaluru: 2 · Kolkata: 1 · Meerut: 1 · not stated: 1 |
| Order frequency | Once a week: 5 · 2–3 times a week: 4 · Daily: 2 · 2–3 times a month: 1 |

The sample is almost entirely 25–34 metro professionals. That matters for interpretation, and section 6 covers why.

---

## 3. Question-by-Question Results

Counts are out of 12 responses. Multi-select questions sum to more than 12.

### What people buy (Q2)

| Category | Count |
|----------|-------|
| Snacks | 11 |
| Household Essentials | 9 |
| Dairy | 7 |
| Beverages | 7 |
| Fruits & Vegetables | 6 |
| Personal Care | 6 |
| Electronics | 1 |

Baskets cluster tightly in food and daily essentials. Electronics appears once, from the single daily-ordering heaviest user.

### How people shop (Q3) and how much repeats (Q4)

| Shopping mode | Count |
|---------------|-------|
| I search for exactly what I need | 7 |
| A mix of the above | 4 |
| I browse categories | 1 |

| Share of basket previously purchased | Count |
|--------------------------------------|-------|
| 25–50% | 8 |
| More than 75% | 2 |
| 50–75% | 1 |
| Less than 25% | 1 |

### Why new products don't get bought (Q6)

| Reason | Count |
|--------|-------|
| I already know what I need | 9 |
| Recommendations don't feel relevant | 4 |
| I forget to check new categories | 2 |
| Too many products to browse | 2 |
| I don't trust recommendations | 1 |
| I don't have time to explore | 1 |
| New products seem expensive | 1 |

### What would encourage trying something new (Q7)

| Encourager | Count |
|-----------|-------|
| Discounts | 8 |
| Reviews & ratings | 7 |
| Personalized recommendations | 6 |
| Similar to products I already buy | 5 |
| Free samples | 4 |
| Trending among people like me | 3 |
| Bundles | 1 |
| Recommended by AI | 1 |

### Appetite for an AI assistant (Q8, Q9, Q11)

| Bought because Blinkit recommended it | Count |
|---------------------------------------|-------|
| Sometimes | 7 |
| Once or twice | 3 |
| Never | 2 |

| Interest in an AI shopping assistant | Count |
|--------------------------------------|-------|
| Somewhat interested | 7 |
| Interested | 2 |
| Extremely interested | 2 |
| Not interested | 1 |

**Trust in AI recommendations (1–5):** mean **3.17**, median 3, mode 3. Nine of 12 scored 3 or below; a single respondent scored 5.

### Which AI recommendations would help (Q10)

| Recommendation type | Count |
|--------------------|-------|
| New products matching my preferences | 11 |
| Cheaper alternatives | 9 |
| Healthier alternatives | 8 |
| Seasonal recommendations | 5 |
| Reminders before I run out of items | 5 |
| "People with similar shopping habits also bought…" | 4 |
| Premium alternatives | 3 |
| Weekly shopping suggestions | 3 |
| Recipes based on my cart | 2 |

These counts are inflated and not comparable across respondents — see the instrument flaw noted in section 6.

### What would build trust (Q12)

| Trust builder | Count |
|--------------|-------|
| Show customer reviews | 9 |
| Explain why it is recommended | 7 |
| Tell me how many people bought it | 7 |
| Personalization improves over time | 6 |
| Allow me to dismiss recommendations | 4 |
| Show similar past purchases | 2 |

### Open-text frustrations and requests (Q13–Q15)

| Theme | Mentions | Verbatim examples |
|-------|----------|-------------------|
| Fees and surcharges | 4 | "surge fee" · "the rush hour charge; low discount" · "Unnecessary surcharge" · "Adding random items to avoid delivery charges" |
| Returns and refunds | 2 | "No return policy" · "Refund policy" |
| Price vs. offline | 1 | "Sometime item overpriced compared to buying physical in market" |
| Product availability | 1 | "Non availability of some essential products" |
| App UI | 1 | "They can work on their UI" |
| No frustration stated | 3 | "Not as such" · "NA" |
| Shared family accounts | 1 respondent, twice | "Blinkit shared account with family" |
| Tier 2/3 city expansion | 2 | "Having Blinkit services in Tier 2 and Tier 3 cities" · "Services in small town" |

---

## 4. What the Data Actually Says

### Discovery failure is structural, not motivational

Two findings interlock: 9 of 12 named **"I already know what I need"** as the reason they don't buy new products, and 7 of 12 shop by **searching for exactly what they need** while only one browses categories. Users arrive with a closed list and treat search as a vending machine.

The implication is sharp and it constrains the MVP: any discovery surface placed *outside* the search-and-checkout path — a home feed, a category tab, a browse carousel — will be structurally bypassed by the majority of this sample. Intervention has to sit inside the flow users already run.

### Discovery is not a pain users feel

Across Q13 and Q14, **not one respondent** named poor discovery, weak recommendations, or difficulty finding new products as their biggest frustration. What they named was fees, refunds, pricing, and availability. Only Kunal asked for anything discovery-adjacent, wanting "suggestive nature and reminders."

This is the most strategically important finding in the survey, and it reframes the brief. Cross-category discovery is a **business** problem, not a user-perceived one. An MVP marketed to users as "discover more categories" is selling a solution to a problem they have not reported having. The workable path is to solve something they *do* want — cheaper options (9), health alternatives (8), running-out reminders (5) — and let cross-category discovery be the mechanism rather than the pitch.

### Enthusiasm for AI is broad but shallow

Eleven of 12 expressed at least some interest in an AI shopping assistant, which reads like a strong signal until you set it beside the trust score: mean 3.17, with 9 of 12 at or below the midpoint. The modal respondent is "somewhat interested" and neutral on trust. That combination describes willingness to try, not willingness to rely.

Q12 says exactly how to close the gap, and the asks are concrete and cheap: show customer reviews (9), explain why this was recommended (7), show how many people bought it (7). Transparency and social proof, not better model accuracy, are what this sample is asking for.

### Users want alternatives to known items more than new categories

The top-ranked AI recommendation type was "new products matching my preferences" (11), followed by cheaper (9) and healthier (8) alternatives. Read against Q7, where "similar to products I already buy" drew 5 mentions, the pattern is a preference for **substitution and adjacency inside familiar territory** over genuine category jumps. A pet-care suggestion to someone who has never bought pet care is a harder sell than a cheaper or healthier version of the snack already in their cart.

### Price is the loudest signal, but it blocks ordering more than exploring

Discounts topped Q7 (8), cheaper alternatives ranked second in Q10 (9), and fee complaints dominated the open text (4 mentions, 5 including offline price comparison). Yet "new products seem expensive" drew only a single mention in Q6. Price sensitivity in this sample is mostly about the cost of the order, not the risk of trying something unfamiliar — worth separating rather than collapsing into one "price barrier."

### A hypothesis worth testing, not asserting

The two daily users scored trust at 3 and 2, while the least frequent user scored 5. If entrenched habit correlates with resistance to algorithmic suggestion, the users with the most room to expand would also be the hardest to influence. With n=2 on one side this is noise, not a finding, but it is a cheap thing to check against the review corpus and interviews.

---

## 5. Implications for the Build

| Finding | Consequence for the MVP |
|---------|------------------------|
| Search-dominant, closed-list shopping | Place suggestions in search results, cart, and checkout — not a browse feed |
| Discovery is not a felt pain | Frame the value as cheaper, healthier, or timely, never as "explore more" |
| Trust neutral at 3.17 | Ship reviews, ratings, purchase counts, and a plain-language reason with every suggestion |
| "Explain why it is recommended" (7) | The reason string is a core feature, not polish — this validates the barrier-aware messaging design in the implementation plan |
| Dismissibility wanted (4) | Every suggestion needs a visible dismiss control that demonstrably affects later suggestions |
| Adjacency beats novelty | Rank suggestions by proximity to existing basket items before reaching for distant categories |
| Reminders wanted (5) | Replenishment prediction is a credible trust-building wedge that earns the right to suggest adjacent items later |

---

## 6. Limitations

These are stated plainly because the survey's weaknesses determine how much weight its findings can carry.

**Sample.** Twelve responses from 11 unique respondents is directional only and cannot support any percentage claim about Blinkit's user base. One respondent answered twice and changed their Q5 answer from "Rarely" to "Sometimes" between submissions, which is itself a caution about the stability of self-reported discovery behaviour.

**Skew.** Ten of 12 respondents are 25–34, and none are over 34. The sample is metro-heavy. This is a serious gap for this specific brief: Baby Care, Pet Care, and Health Supplements — three of the five target expansion categories — are bought disproportionately by parents, pet owners, and older shoppers, none of whom this sample reaches. It is a convenience sample drawn from a personal network, so friendly-response bias should be assumed.

**Instrument flaws.**

- Q10 asked respondents to select up to 3 options but did not enforce the cap; one respondent selected 9. Q10 counts are therefore inflated and not comparable across respondents.
- Q2's category options did not include Pet Care, Baby Care, or Health Supplements. Their absence from the results is an artefact of the instrument and **cannot** be read as evidence that respondents don't buy them. This needs fixing before the next survey wave, since those categories are the entire point of the brief.
- Q6 was conditional on rarely buying new products, but a respondent who answered "Very often" still filled it in, and another left it blank entirely.
- One row arrived with demographics missing and columns shifted; order frequency was recovered by inference and flagged in the CSV.
- All behavioural data is self-reported. Basket-share percentages are recall estimates, and stated interest in AI is a notoriously poor predictor of actual usage.

**What this survey cannot answer.** Whether the barriers named here generalise, how often discovery failures occur in practice, and what users actually do rather than what they say they do. Those require the app store corpus and the depth interviews.

---

## 7. Next Steps

1. Ingest the Play Store and App Store corpora using the identifiers in section 2, then test whether "I already know what I need" behaviour and the absence of discovery complaints replicate at scale.
2. Run depth interviews weighted deliberately toward the demographics this survey missed — parents, pet owners, and shoppers over 34 — since they carry the target expansion categories.
3. Revise the instrument: enforce the Q10 cap, add the missing categories to Q2, and fix the Q6 conditional logic before any second wave.
4. Feed each finding above into the Phase 5 triangulation engine as an explicit hypothesis with a validation status, so agreement and contradiction between survey, reviews, and interviews stays visible.

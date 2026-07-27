# Problem Definition

**Project:** AI-Powered Product Discovery Engine for Blinkit
**Status:** Generated from triangulated review, interview, and survey evidence

---

## North star

Increase the share of Blinkit baskets that include at least one **adjacent-category** item
the shopper has not purchased in the prior 90 days, without increasing time-to-checkout.

## Sharpened problem

Blinkit shoppers treat the app as a **mission-driven restock tool**: they search for known SKUs,
repeat prior baskets, and rarely explore non-grocery categories—even when latent demand exists
(pet care, baby care, personal care expansions). Discovery fails at the **moment of purchase**
because in-flow surfaces do not reduce trust and habit barriers with contextual, cited suggestions.

## Evidence summary

- **Interviews coded:** 27
- **Survey aggregates:** 6 question/response buckets loaded
- **AI insights triangulated:** 18

### Top affinity themes (human + AI)

- **Recommendations** — 85 findings (survey)
- **Trust** — 73 findings (interview:1, interview:10, interview:12)
- **Category Discovery** — 56 findings (interview:10, interview:12, interview:14)
- **Shopping Habit** — 25 findings (interview:11, interview:13, interview:15)
- **Search** — 12 findings (interview:1, interview:10, interview:12)

### Validated / contested AI insights

- **[validated]** Pet Care category discovery from grocery-only baskets
  - Reviews cited: `[1, 2]`
  - Interview evidence: Interview 1: "I literally search 'Amul milk' and checkout in under two minutes."; Interview 2: "Participant: Groceries on Blinkit every week, but baby wipes and diapers I still order from another app because I don't "; Interview 3: "For pet
- **[validated]** Pet Care category discovery from grocery-only baskets
  - Reviews cited: `[1, 2]`
  - Interview evidence: Interview 1: "I literally search 'Amul milk' and checkout in under two minutes."; Interview 2: "Participant: Groceries on Blinkit every week, but baby wipes and diapers I still order from another app because I don't "; Interview 3: "For pet
- **[partially_supported]** Users rarely discover pet care from grocery baskets
  - Reviews cited: `[1, 2]`
  - Interview evidence: Interview 1: "I literally search 'Amul milk' and checkout in under two minutes."; Interview 2: "Trust is the issue — if I'm trying a new category for my kid, I need ratings and easy returns spelled out."; Interview 3: "For pet food I never 
- **[partially_supported]** Users rarely discover pet care from grocery baskets
  - Reviews cited: `[1, 2]`
  - Interview evidence: Interview 1: "I literally search 'Amul milk' and checkout in under two minutes."; Interview 2: "Trust is the issue — if I'm trying a new category for my kid, I need ratings and easy returns spelled out."; Interview 3: "For pet food I never 
- **[rejected]** Delivery delays are the primary reason users fail at category discovery on Blinkit
  - Reviews cited: `[1]`
  - Interview evidence: Interview 1: "I literally search 'Amul milk' and checkout in under two minutes."; Interview 2: "Participant: Groceries on Blinkit every week, but baby wipes and diapers I still order from another app because I don't "; Interview 3: "For pet
- **[rejected]** Delivery delays are the primary reason users fail at category discovery on Blinkit
  - Reviews cited: `[1]`
  - Interview evidence: Interview 1: "I literally search 'Amul milk' and checkout in under two minutes."; Interview 2: "Participant: Groceries on Blinkit every week, but baby wipes and diapers I still order from another app because I don't "; Interview 3: "For pet
- **[rejected]** Delivery delays are the primary reason users fail at category discovery on Blinkit
  - Reviews cited: `[1]`
  - Interview evidence: Interview 1: "I literally search 'Amul milk' and checkout in under two minutes."; Interview 2: "Participant: Groceries on Blinkit every week, but baby wipes and diapers I still order from another app because I don't "; Interview 3: "For pet
- **[rejected]** Delivery delays are the primary reason users fail at category discovery on Blinkit
  - Reviews cited: `[1]`
  - Interview evidence: Interview 1: "I literally search 'Amul milk' and checkout in under two minutes."; Interview 2: "Participant: Groceries on Blinkit every week, but baby wipes and diapers I still order from another app because I don't "; Interview 3: "For pet

### Ranked opportunities

1. **Human research theme: Category Discovery** (score 3.9)
   - Reach 4.0, Severity 3.5, North-star 4.5, Effort 3.0
2. **Pet Care category discovery from grocery-only baskets** (score 3.815)
   - Reach 2.96, Severity 3.5, North-star 5.0, Effort 3.0
   - Weights: {'reach': 0.25, 'severity': 0.25, 'north_star': 0.35, 'effort': 0.15}
3. **Pet Care category discovery from grocery-only baskets** (score 3.815)
   - Reach 2.96, Severity 3.5, North-star 5.0, Effort 3.0
   - Weights: {'reach': 0.25, 'severity': 0.25, 'north_star': 0.35, 'effort': 0.15}

## Implications for MVP

Ship a **barrier-aware, in-cart suggestion** with one adjacent item per order,
grounded in insight IDs and human quotes—not generic promotions.

## Rejected assumptions

Any insight marked `rejected` above should not drive MVP copy; interviews outrank
stated survey enthusiasm for AI when behaviors describe dismissal and trust barriers.

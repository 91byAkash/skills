# Competitor Data: [Competitor name]

```yaml
name: "[Competitor]"
website: "https://competitor.example"
last_verified: "2026-10-08"          # re-verify before republishing anything that uses this file
verified_by: "[name]"
sources:                              # every fact below should trace to one of these
  - "pricing page, checked 2026-10-08"
  - "docs: /docs/sso, checked 2026-10-08"
  - "trial account, 2026-10-01"
positioning:
  tagline: "[their words]"
  target_customer: "[segment, size, industry]"
  category_claim: "[how they describe their category]"
pricing:                              # as of last_verified
  free_tier: "[limits]"
  tiers:
    - {name: "Starter", price: "$X/user/mo annual", key_limits: "[ ]"}
    - {name: "Business", price: "$X/user/mo annual", key_limits: "[ ]"}
    - {name: "Enterprise", price: "custom", key_limits: "[ ]"}
  hidden_costs: ["onboarding fee $X", "SSO only on Enterprise", "API overage $X per 1k calls"]
  sample_total_cost: "10 users annual on Business = $X"
features:                             # rating 1-5 or short description; mark unknowns as "not listed (date)"
  core_workflow: 4
  reporting: 3
  integrations: "40+ listed; no native [tool] (docs, 2026-10-08)"
  mobile_app: "iOS + Android"
  sso: "Enterprise tier only (pricing page, 2026-10-08)"
strengths: ["[honest strength]", "[ ]"]
weaknesses: ["[fair weakness with source]", "[ ]"]
best_for: ["[use case/team]"]
not_ideal_for: ["[use case/team]"]
review_themes:                        # from review mining; counts out of N reviews read
  praise: [{theme: "easy setup", count: 34}]
  complaints: [{theme: "slow support", count: 21}]
migration:
  import_tools: "[CSV import / API / migration service]"
  what_transfers: "[ ]"
  what_needs_rebuild: "[ ]"
  typical_time: "[ ]"
switcher_quotes: ["\"[quote]\" - [name, role, company] (permission: yes)"]
```

## Our product (same fields, kept in a sibling file)

# Tracking Plan: [Product / Site]

Owner: [name]  ·  Last updated: [YYYY-MM-DD]  ·  Tools: [analytics, tag manager, product analytics, CDP]  ·  Ads: [platforms]

## 1. Decisions this data serves
| # | Decision | Metric | Events needed |
|---|---|---|---|
| D1 | Which channels bring paying customers? | Paid conversions by first/last touch source | `signup_completed`, `subscription_started` + campaign props |
| D2 | | | |

## 2. Events
| Event | Description | Trigger (exact) | Properties | Client/Server | Destinations | Decision | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| `signup_completed` | Account created | Server, after user row insert | `method`, `plan`, `referral_code` | Server | analytics, CRM | D1 | eng | live |

## 3. Identity
- Anonymous id: [tool default cookie]
- `user_id` set at: [signup/login], value: [internal id]
- `account_id` (B2B): [where set]
- Logout behavior: [reset id]

## 4. Conversions / key events
| Name | Event | Counting | Value | Imported to ads? |
|---|---|---|---|---|
| Lead | `demo_requested` | once per session | [$ estimate] | yes |
| Purchase | `subscription_started` | every event | `value` | yes |

## 5. Custom definitions
| Name | Scope (event/user/item) | Parameter |
|---|---|---|

## 6. Campaign tagging
UTM convention: [link to sheet]. `utm_medium` allowed values: cpc, paid-social, display, email, social, referral, affiliate, sms, podcast.

## 7. Server-side reporting (if ads run)
| Platform | Events sent | Click id captured | Dedupe key | Hashed fields | Verified on |
|---|---|---|---|---|---|

## 8. Consent and privacy
Regions: [ ]. Consent tool: [ ]. Default state: [denied in EU/UK]. PII policy: no PII in properties/URLs. Retention: [14 months].

## 9. QA checklist
- [ ] Each event fires once per action in debug view, desktop and mobile
- [ ] Properties populated with expected types and values
- [ ] No duplicate containers or double tags
- [ ] Conversions recorded with correct counting
- [ ] Consent: tags blocked before opt-in where required
- [ ] No PII in payloads or URLs
- [ ] Cross-domain / payment provider sessions preserved
- [ ] 1-week reconciliation vs source of truth: analytics [n] vs orders [n] = [gap %]
- [ ] Click-id coverage on paid orders: [%]

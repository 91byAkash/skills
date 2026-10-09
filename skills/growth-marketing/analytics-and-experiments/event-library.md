# Event Library

Starter events by context. Copy what serves a decision; delete the rest. Names are `object_action`, snake_case. Where an analytics tool has a recommended name (in brackets), prefer it.

## Standard context (attach to every event)
| Group | Properties |
|---|---|
| Page | `page_location`, `page_title`, `page_referrer`, `content_group` |
| Identity | `user_id` (internal id, never email), `account_id` (B2B), `user_type` (anonymous/free/trial/paid), `plan_type` |
| Campaign | `source`, `medium`, `campaign`, `content`, `term` (persisted first-touch and last-touch) |
| Device | handled automatically by most tools; do not duplicate |

## Marketing site
| Event | Trigger | Properties |
|---|---|---|
| `cta_clicked` | Any primary/secondary CTA | `cta_text`, `cta_location` (hero, nav, pricing_card, footer), `destination` |
| `form_started` | First field focus | `form_name`, `form_location` |
| `form_submitted` | Server-confirmed success | `form_name`, `form_location` |
| `form_error` | Validation failure | `form_name`, `field_name`, `error_type` |
| `resource_downloaded` | Gated asset delivered | `resource_name`, `resource_type` |
| `newsletter_subscribed` | Confirmed (double opt-in if used) | `list_name`, `source` |
| `demo_requested` [`generate_lead`] | Demo form success | `company_size`, `industry`, `lead_source` |
| `contact_submitted` | Contact form success | `inquiry_type` |
| `video_played` / `video_completed` | Player events | `video_id`, `video_title`, `percent` |
| `scroll_depth` | 25/50/75/100% (only if you will use it) | `depth` |
| `pricing_viewed` | Pricing page view | `source`, `billing_period_default` |

## Signup and onboarding (SaaS)
| Event | Trigger | Properties |
|---|---|---|
| `signup_started` | Signup form/view opened | `entry_point`, `method_options` |
| `signup_completed` [`sign_up`] | Account created (server) | `method` (email/google/sso), `plan`, `referral_code` |
| `onboarding_step_completed` | Each step | `step_number`, `step_name` |
| `onboarding_skipped` | Skip clicked | `step_name` |
| `activation_reached` | Your aha action (define it!) | `action_type`, `minutes_since_signup` |
| `feature_used` | Core features only | `feature_name`, `feature_area` |
| `invite_sent` / `teammate_joined` | Collaboration | `role`, `invite_method` |
| `integration_connected` | Integration success | `integration_name` |
| `error_shown` | User-visible error | `error_type`, `surface` |
| `help_opened` / `support_contacted` | Help usage | `surface`, `topic` |

## Monetization (subscription)
| Event | Trigger | Properties |
|---|---|---|
| `plan_selected` | Plan card chosen | `plan_name`, `billing_period` |
| `checkout_started` [`begin_checkout`] | Checkout opened | `plan`, `value`, `currency` |
| `trial_started` | Trial begins (server) | `plan`, `trial_days`, `card_required` |
| `trial_converted` / `trial_expired` | Trial end (server) | `plan`, `value` |
| `subscription_started` [`purchase`] | First successful charge (server) | `transaction_id`, `plan`, `value`, `currency`, `billing_period` |
| `subscription_renewed` | Renewal charge (server) | `plan`, `value` |
| `subscription_upgraded` / `_downgraded` | Plan change (server) | `from_plan`, `to_plan`, `mrr_delta` |
| `payment_failed` / `payment_recovered` | Billing provider webhooks | `attempt`, `decline_code` |
| `cancel_flow_started` / `save_offer_accepted` / `subscription_cancelled` | Cancellation flow | `reason`, `offer_type`, `tenure_months`, `mrr_lost` |
| `refund_issued` [`refund`] | Server | `transaction_id`, `value`, `reason` |
| `paywall_viewed` / `upgrade_prompt_clicked` | In-app upgrade surfaces | `trigger` (limit, feature, trial_end), `surface` |

## Ecommerce
| Event | Properties |
|---|---|
| `product_list_viewed` [`view_item_list`] | `list_name`, `items[]` |
| `product_viewed` [`view_item`] | `item_id`, `item_name`, `item_category`, `price` |
| `product_searched` [`search`] | `search_term`, `results_count` |
| `product_added_to_cart` [`add_to_cart`] | `items[]`, `value` |
| `cart_viewed` | `value`, `items_count` |
| `checkout_started` [`begin_checkout`] | `value`, `items[]`, `coupon` |
| `shipping_info_entered` [`add_shipping_info`] | `shipping_tier` |
| `payment_info_entered` [`add_payment_info`] | `payment_type` |
| `order_completed` [`purchase`] | `transaction_id`, `value`, `tax`, `shipping`, `currency`, `coupon`, `items[]` |
| `upsell_viewed` / `upsell_accepted` | `offer_id`, `value`, `position` (order bump, post-purchase 1, downsell) |
| `refund_completed` [`refund`] | `transaction_id`, `value` |

## B2B account and pipeline (send from CRM/backend)
| Event | Properties |
|---|---|
| `account_created` | `source`, `plan`, `employee_band` |
| `lead_qualified` (MQL/SQL) | `lead_score`, `qualification_reason` |
| `meeting_booked` | `meeting_type`, `source` |
| `opportunity_created` / `opportunity_won` / `opportunity_lost` | `amount`, `stage`, `loss_reason` |
| `account_churned` / `account_reactivated` | `reason`, `tenure_months`, `mrr` |

## Standard funnels to build
- **Signup**: `cta_clicked` → `signup_started` → `signup_completed` → `onboarding_step_completed` (1..n) → `activation_reached`.
- **Self-serve purchase**: `pricing_viewed` → `plan_selected` → `checkout_started` → `subscription_started`.
- **Trial**: `trial_started` → `activation_reached` → `paywall_viewed` → `trial_converted`.
- **Ecommerce**: `product_viewed` → `product_added_to_cart` → `checkout_started` → `shipping_info_entered` → `payment_info_entered` → `order_completed`.
- **Demo-led**: `pricing_viewed`/`cta_clicked` → `demo_requested` → `meeting_booked` → `opportunity_created` → `opportunity_won`.

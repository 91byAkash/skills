# Site launch QA

Use this whenever a launch depends on a page or site going live: a new site, a redesign, a platform or domain move, a new section, or the single landing page the announcement links to. The launch spike is wasted if it lands on a dead form, a page search engines were told to ignore, or a price that changed last week. Deeper technical SEO lives in seo-optimization; event and conversion setup lives in analytics-and-experiments.

## How to use it

The checks are grouped by **what can go wrong**, not by date. Each one carries a timing tag:

- **T-** run on staging before the switch (allow at least two working days to fix what you find);
- **T0** run in the hour the new site goes live;
- **T+** repeat daily for the first week after launch, then weekly until day 14.

Give every group one owner. A check counts as done only when someone has looked at the result, not when a tool reported success.

## 1. Visitors cannot convert

| Check | When |
|---|---|
| Fill in each form yourself with a marked test entry, then find that entry in the place it is meant to reach (CRM, inbox, support tool) with every field in the right column. | T- |
| After submitting, the visitor sees the thank-you state or lands on the right page; the anti-spam step lets a normal person through on a phone. | T- |
| Buy or sign up end to end with a real card, then refund it. | T- |
| One genuine signup or purchase and one genuine form entry, traced all the way through. | T0 |
| Anything that blocks paying or signing up is fixed before any other bug report. | T+ |

## 2. Search engines drop or ignore the site

The most frequent launch-day disaster is a "don't index me" setting carried from staging onto the live site. Check it twice.

| Check | When |
|---|---|
| Staging sits behind a password or noindex; the production build has neither (look at the page source and the response headers). | T- and T0 |
| Canonical URLs use the live domain. No staging hostnames anywhere in the HTML or the sitemap. | T- |
| Each page has its own title and description and exactly one H1. | T- |
| robots.txt does not block pages you want found; the XML sitemap contains live URLs only and is submitted in the Google and Bing webmaster consoles. | T- / T0 |
| Structured data passes a schema validator and the search engine's rich-result test. | T- |
| Moving domains or URLs: every old URL that has traffic or backlinks maps to its nearest new page with one permanent redirect. Test a sample. The redirects ship in the same deploy as the new site. | T- / T0 |
| Coverage and 404 reports reviewed; any old URL still being requested gets a redirect. | T+ |

## 3. The content is wrong

| Check | When |
|---|---|
| Search the build for leftovers: "TBD", lorem ipsum, test prices, invented testimonials, pages in the plan that never got built. | T- |
| Prices, plan names, limits and contact details agree with the billing system and with what sales and support are telling people. | T- |
| Every claim in the launch copy is true for every visitor today; nothing depends on a feature flag that is still off for some users. | T- |
| Privacy, terms and cookie pages exist, are current, and show the correct company details. | T- |
| A crawl of staging finds no broken internal links, missing images or pages nothing links to. | T- |
| The ten highest-traffic pages load with status 200 and the right content, title and canonical. | T0 |
| Internal links that now go through a redirect are pointed straight at the new URL. | T+ |

## 4. You cannot measure the launch

| Check | When |
|---|---|
| The analytics tag loads once per page on every template; your own team's traffic is excluded; UTM parameters are still present after any redirect. | T- |
| Conversion events fire on the confirmed submission or thank-you state, never on the button press. | T- |
| The consent banner works, and tags that need consent wait for it. | T- |
| The real-time report shows visits on the new pages. | T0 |
| Each ad platform receives conversions at roughly the rate it did before; a silent drop starves paid campaigns of signal. | T+ |
| Traffic and conversions compared page by page with the same period before launch; dig into any page down by more than 30%. | T+ |

## 5. The site breaks for part of the audience

| Check | When |
|---|---|
| Key templates load quickly on a mid-range phone over a mobile connection, with compressed hero images and no content jumping around. | T- |
| Tested in mobile Safari, mobile Chrome, desktop browsers, and the in-app browsers of the social networks you will post on (many launch clicks open there). | T- |
| Meaningful images have alt text, form fields have labels, and the whole page works with a keyboard and a visible focus ring. | T- |
| Link previews (title, description, image) look right on each network you plan to post to. | T- |
| HTTPS works on both the apex domain and www, and one permanently redirects to the other. | T0 |

## 6. You cannot undo it

| Check | When |
|---|---|
| The rollback steps for this host are written down and someone has actually performed them once (redeploy the previous build, restore a backup, or point DNS back). | T- |
| If DNS is changing, the record's TTL was lowered at least a day ahead; restore the normal TTL once things are stable. | T- / T+ |
| One named person can roll back and is reachable during the switch and the following days. | T0 |

## When the numbers look wrong in launch week

- **Organic visits collapse.** Almost always a noindex or robots rule that came over from staging. Remove it, resubmit the sitemap and request reindexing for the most important pages.
- **Old pages lose rankings.** Redirects are missing or chained. Point each old URL directly at one new URL.
- **Analytics records signups the CRM never receives.** The form integration still uses staging credentials. Switch to production keys and backfill from the form tool's export.
- **An ad platform reports zero conversions.** The tag was dropped or an event name changed. Restore the names and confirm with the platform's tag debugger.
- **Social traffic bounces immediately.** A script or pop-up fails inside in-app browsers. Reproduce in the app and suppress the pop-up for those user agents.

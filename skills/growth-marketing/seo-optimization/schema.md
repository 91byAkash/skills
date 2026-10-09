# Structured Data (JSON-LD)

Principles: mark up only what is visible on the page and true; use JSON-LD in the head or body; use the most specific type; keep `@id` and URLs absolute and stable; validate the rendered output (rich results are never guaranteed). Since 2023 Google shows FAQ rich results only for well-known government and health sites and has retired HowTo rich results, and in 2025 it dropped more (including Course Info, Claim Review, Estimated Salary, Vehicle Listing); check the current Search Gallery before promising a type; the markup can still help other consumers understand the page, but don't promise SERP features from it.

## Which type per page
| Page | Types | Required (minimum) | Recommended |
|---|---|---|---|
| Homepage / About | Organization (or LocalBusiness), WebSite | name, url | logo, sameAs, contactPoint, description, foundingDate |
| Blog post / news | Article / BlogPosting / NewsArticle | headline, image, datePublished, author | dateModified, publisher, description, mainEntityOfPage |
| Product (ecommerce) | Product + Offer | name, image, offers (price, priceCurrency, availability) | sku, brand, gtin, aggregateRating, review, shippingDetails, hasMerchantReturnPolicy |
| SaaS / app | SoftwareApplication (or WebApplication) | name, offers or aggregateRating | applicationCategory, operatingSystem |
| FAQ section | FAQPage | mainEntity (Question + acceptedAnswer) | |
| Tutorial | HowTo | name, step | totalTime, tool, supply |
| Any page with breadcrumbs | BreadcrumbList | itemListElement (position, name, item) | |
| Local business | LocalBusiness subtype | name, address | geo, openingHoursSpecification, telephone, priceRange, areaServed |
| Event / webinar | Event | name, startDate, location (Place or VirtualLocation) | endDate, eventAttendanceMode, offers, organizer |
| Video page | VideoObject | name, thumbnailUrl, uploadDate | description, duration, contentUrl, hasPart (clips) |
| Reviews | Review / AggregateRating (nested in the item reviewed) | itemReviewed, reviewRating / ratingValue + reviewCount | Self-serving reviews of your own business are not eligible for stars |
| Course, JobPosting, Recipe | Specific types | see type docs | |

## Copy-ready examples

Organization + WebSite on the homepage using `@graph`:
```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#org",
      "name": "Acme",
      "url": "https://example.com/",
      "logo": "https://example.com/logo.png",
      "description": "Expense management for agencies and studios.",
      "sameAs": ["https://www.linkedin.com/company/acme", "https://x.com/acme"],
      "contactPoint": {"@type": "ContactPoint", "contactType": "sales", "email": "sales@example.com"}
    },
    {
      "@type": "WebSite",
      "@id": "https://example.com/#website",
      "url": "https://example.com/",
      "name": "Acme",
      "publisher": {"@id": "https://example.com/#org"}
    }
  ]
}
```

Article:
```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "How to Close the Books in 3 Days",
  "image": ["https://example.com/img/close-books.png"],
  "datePublished": "2026-09-02T08:00:00+05:30",
  "dateModified": "2026-10-01T10:00:00+05:30",
  "author": {"@type": "Person", "name": "Priya Shah", "url": "https://example.com/authors/priya-shah"},
  "publisher": {"@id": "https://example.com/#org"},
  "mainEntityOfPage": "https://example.com/blog/close-books-3-days"
}
```

Product with Offer:
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Trail Runner 2 - Men's",
  "image": ["https://example.com/p/trail-runner-2.jpg"],
  "sku": "TR2-M-42",
  "brand": {"@type": "Brand", "name": "Acme"},
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/products/trail-runner-2",
    "price": "129.00",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition"
  },
  "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.6", "reviewCount": "214"}
}
```

SoftwareApplication:
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Acme",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web, iOS, Android",
  "offers": {"@type": "Offer", "price": "29", "priceCurrency": "USD"}
}
```

FAQPage:
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {"@type": "Question", "name": "Does Acme have a mobile app?",
     "acceptedAnswer": {"@type": "Answer", "text": "Yes. iOS and Android apps are included on every plan."}}
  ]
}
```

BreadcrumbList:
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/"},
    {"@type": "ListItem", "position": 2, "name": "Features", "item": "https://example.com/features"},
    {"@type": "ListItem", "position": 3, "name": "Analytics"}
  ]
}
```

LocalBusiness:
```json
{
  "@context": "https://schema.org",
  "@type": "Dentist",
  "name": "Smile Studio Austin",
  "url": "https://example.com/locations/austin",
  "telephone": "+1-512-555-0100",
  "address": {"@type": "PostalAddress", "streetAddress": "100 Congress Ave", "addressLocality": "Austin",
              "addressRegion": "TX", "postalCode": "78701", "addressCountry": "US"},
  "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "08:00", "closes": "17:00"}]
}
```

Event (webinar):
```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "Month-End Close Workshop",
  "startDate": "2026-11-12T17:00:00+00:00",
  "endDate": "2026-11-12T18:00:00+00:00",
  "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",
  "location": {"@type": "VirtualLocation", "url": "https://example.com/webinars/close"},
  "organizer": {"@id": "https://example.com/#org"},
  "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "url": "https://example.com/webinars/close"}
}
```

## Implementation
- Static sites: in the template or a partial per page type.
- Frameworks: a component that serializes data to JSON-LD, rendered server-side.
- CMS: SEO plugin or custom fields mapped to markup; check that plugins don't output duplicate or conflicting graphs.
- Programmatic pages: generate from the same data that renders the page so values never diverge.

## Validation
- Rich Results Test (renders JavaScript) and the schema.org validator; Search Console enhancement reports after launch.
- Common errors: missing required properties; dates not ISO 8601; relative URLs; enum values not full schema.org URLs (`https://schema.org/InStock`); prices with currency symbols; markup describing content not on the page; duplicate Organization nodes from multiple plugins.

Checklist:
- [ ] Validates without errors
- [ ] Matches visible content
- [ ] All required properties present
- [ ] One coherent graph per page (no duplicate/conflicting nodes)

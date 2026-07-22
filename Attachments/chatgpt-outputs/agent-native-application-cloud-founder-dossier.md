# From Intent to Production Software

## Founder strategy, business model, go-to-market, and seed fundraising playbook for an agent-native application cloud

**Status:** Working founder dossier  
**Prepared for:** The founding team  
**Date:** July 20, 2026  
**Companion technical document:** *Building a Secure JavaScript Hosting Platform with Goja*


## How to use this document

This document is not a prediction that one exact plan will work. It is a structured set of decisions, hypotheses, experiments, and pitch materials for turning a strong technical system into a venture-scale company. It is written for four readers:

1. The existing technical and design founders, who need a shared commercial model.
2. A prospective business or go-to-market co-founder, who needs enough detail to decide whether to join.
3. Seed investors, who need to understand why the company is technically differentiated and commercially focused.
4. Early design partners, who need to understand what the platform lets them do now.

The most important distinction in the document is between **the long-term product surface** and **the initial go-to-market wedge**. The platform can eventually support personal applications, shared applications among friends, professional business systems, commerce, logistics, booking, and enterprise workflows. The company cannot initially sell all of those things through one message. A broad technical platform needs a narrow commercial entry point.

The recommended entry point is a design-partner and studio-led business that produces professional operational applications for small businesses, service companies, communities, and internal teams. The platform is the product. Paid application delivery is the learning and distribution mechanism. Self-service creation, a module marketplace, and enterprise hosting follow after the team has evidence about which application patterns repeat.

Current market facts in this document are dated July 20, 2026. Refresh them before circulating the memo externally.


## Contents

| Section | Scope |
|---|---|
| Executive decision memo | Recommended company, wedge, business model, financing posture, team decision, and next ninety days |
| Part I. The Company Thesis | Chapters 1–5: company thesis, central insight, product promise, timing, and category boundaries |
| Part II. The Product as a Business | Chapters 6–10: application ladder, product experience, semantic modules, release semantics, and design advantage |
| Part III. Market, Competition, and Positioning | Chapters 11–17: category, competitive map, defensibility, beachheads, and bottom-up market model |
| Part IV. Business Models and Pricing | Chapters 18–26: revenue architecture, packaging, modules, marketplace, services, enterprise, and financial scenarios |
| Part V. Go-to-Market | Chapters 27–33: design partners, studios, vertical packs, self-service, sales, partnerships, and metrics |
| Part VI. Seed Fundraising | Chapters 34–42: financing stage, round scenarios, investor narrative, deck, demo, diligence, and process |
| Part VII. The Founding Team | Chapters 43–49: team story, commercial co-founder decision, role, search, trial, equity, and governance |
| Part VIII. Execution Plan | Chapters 50–55: first ninety days, roadmap, hiring, experiments, risk register, and pivot criteria |
| Part IX. Pitch Assets | Chapters 56–62: concise pitches, ten-minute narrative, one-pager, outreach, and founder FAQ |
| Appendices | Sources, model assumptions, and one hundred co-founder discussion questions |

The Word edition uses heading styles throughout, so readers can use the Navigation Pane for chapter-level navigation.

# Executive decision memo

## The recommended company

Build an **agent-native application cloud** in which coding agents generate compact JavaScript or TypeScript applications against a catalog of secure, versioned, high-level modules. The platform owns the operational semantics: identity, authorization, data, payments, search, booking, messaging, UI rendering, deployment, rollback, audit, isolation, quotas, and billing.

The investor-facing version is simpler:

> **Coding agents are becoming capable of generating applications, but production software still requires a large amount of fragile operational code. We replace that code with high-level, versioned application modules, so agents can turn intent into professional software that is secure, maintainable, and deployable by construction.**

The product should not be pitched as another general-purpose code generator. Replit, Lovable, v0, Base44, and several other platforms already occupy that category with enormous distribution and capital. The company should be pitched as the layer that makes generated applications **durable, governable, and economically composable**.

## The recommended initial wedge

Start with **designers, AI-native studios, automation consultants, and technically ambitious agencies** that need to deliver custom operational software to clients. The applications should concentrate on a repeating set of jobs:

- Booking, scheduling, and availability.
- Lightweight CRM and customer portals.
- Product or service catalogs and search.
- Quotes, orders, payments, and subscriptions.
- Inventory, logistics, status tracking, and notifications.
- Community coordination, forms, voting, and event planning.
- Internal operations dashboards and approval workflows.

This wedge fits the existing team. The technical founder can provide the secure runtime and modules. The design founder can demonstrate a level of product quality that pure infrastructure teams usually lack. Studios and agencies provide concentrated demand, repeated app creation, and a path to revenue before self-service acquisition is solved.

Personal and friend-shared applications remain important. They are excellent demos, viral artifacts, and long-term product surfaces. They should not be the first revenue model because consumer acquisition, support, and retention would distract from proving that the platform can support business-critical applications.

## The recommended business model

Use a four-layer revenue model:

1. **Builder subscription.** Charge creators, teams, and studios for generation, collaboration, environments, governance, and support.
2. **Application runtime.** Charge a base fee per production application plus metered compute, storage, bandwidth, users, and other infrastructure.
3. **Premium modules and resources.** Charge per application or by usage for high-value capabilities such as product search, booking, commerce, managed identity, messaging, and larger databases.
4. **Enterprise and marketplace revenue.** Charge for private deployments, SSO, audit retention, governance, support, and take a percentage of third-party module, template, and expert revenue.

Keep generation credits separate from runtime charges. A customer should understand the difference between paying to create software and paying to operate it.

## The recommended financing posture

The technology and demo quality can support a strong seed narrative. The financing stage depends on customer proof:

- With no paid external users, describe the round as a **pre-seed or formation seed**, even if the product is technically advanced.
- With ten or more paid design partners, active production applications, and evidence of repeated module use, a conventional **seed round** is credible.
- With repeatable studio acquisition, meaningful monthly recurring revenue, and expanding app counts per customer, the company can argue for an infrastructure-style seed premium.

Carta's July 2026 software benchmark reports a median seed round of $4.1 million at a $24.3 million valuation with 18% dilution.[^S8] That is useful context, not a pricing entitlement. The recommended planning range is:

| Financing plan | Raise | Intended runway | Appropriate when |
|---|---:|---:|---|
| Lean pre-seed | $1.5M–$2.5M | 15–18 months | Product is strong, but customer evidence is early |
| Institutional seed | $3M–$4.5M | 18–24 months | Paid design partners and initial repeatability exist |
| Infrastructure seed | $5M–$8M | 24 months | Strong usage, clear module economics, and unusually strong investor demand exist |

The default recommendation is to prepare for a $3.5 million seed but begin investor conversations only after a focused design-partner sprint creates external proof.

## The recommended team decision

Do not recruit a generic “business person.” Recruit either:

- A **CEO/GTM co-founder** who can own category narrative, customer discovery, sales, partnerships, fundraising, and company building; or
- A **founding commercial executive** who can do the same work but earns the co-founder title only after a working trial proves mutual fit.

Whether the new person should become CEO depends on what the technical founder wants to do for the next decade. If the technical founder wants to lead product, fundraising, recruiting, and company strategy, remain CEO and hire a founding GTM leader. If the technical founder wants to spend most of the time on architecture, runtime security, and technical product, recruit a CEO co-founder.

The search should run in parallel with customer development. A candidate should complete a six- to eight-week trial that includes customer interviews, pricing work, design-partner outreach, and at least one paid close. The role is too important to award on the basis of charisma or fundraising contacts alone.

## The first ninety days

The company should leave the next ninety days with five concrete assets:

1. A sharp company narrative and investor demo.
2. Twenty-five serious customer interviews in one beachhead.
3. Five paid design partners and at least three live applications.
4. A first commercial module catalog with explicit prices and margins.
5. A repeatable co-founder or founding-GTM search process.

The strongest near-term milestone is not another subsystem. It is proving that a customer will pay for a professional application created in days, keep it live, request changes, and accept a recurring platform bill.


# Part I. The Company Thesis

## 1. The company that should exist

Software creation is moving from manual implementation toward intent-driven generation. The change is visible in consumer-facing app builders, coding agents, internal enterprise tools, and production deployment platforms. Replit reported more than 50 million users, usage across 85% of the Fortune 500, and a $400 million financing at a $9 billion valuation in March 2026.[^S1] Lovable raised $330 million at a $6.6 billion valuation in December 2025.[^S3] Vercel reported more than four million v0 users when it repositioned the product around production applications in February 2026.[^S5]

Those facts establish demand. They do not establish that the problem is solved.

Most current systems generate conventional application code and then rely on conventional stacks. The agent creates routes, database schemas, frontend state, authentication glue, billing integration, API calls, deployment configuration, and error handling. The user gets a repository and a deployment, but also inherits the operational consequences of every generated decision.

The proposed company changes the unit of generation. The agent does not need to generate an entire operational stack. It writes a compact application program whose important dependencies are high-level platform capabilities.

```javascript
const app = require("app")
const booking = require("booking")
const customers = require("crm")
const payments = require("payments")

app.page("/book/:serviceId")
  .public()
  .load(async ctx => {
    const service = await booking.services.get(ctx.params.serviceId)
    const slots = await booking.availability.list({
      serviceId: service.id,
      from: ctx.query.from,
      days: 14,
    })
    return ctx.ui.bookingPage({ service, slots })
  })

app.action("reserve")
  .sessionUser()
  .csrf()
  .input("booking.reserve/v1")
  .effect("booking.create")
  .handle(async ctx => {
    const customer = await customers.current(ctx.actor)
    const reservation = await booking.reserve({
      customerId: customer.id,
      slotId: ctx.input.slotId,
    })
    return payments.checkout.forReservation(reservation.id)
  })
```

This program specifies the application's business behavior. It does not specify lock acquisition, retry policy, payment idempotency, webhook verification, database indexes, session cookies, authorization token parsing, deployment topology, or rollback mechanics. Those semantics live in versioned modules and the host.

The company therefore sells two things at once:

- A creation environment that is easier for coding agents to use.
- An application runtime that is safer and easier for people to operate.

![The product thesis](./_founder_assets/thesis_stack.png)

### 1.1 The category statement

A useful category name is **agent-native application platform** or **agent-native application cloud**.

“AI app builder” is understandable but crowded. “Serverless JavaScript platform” is technically accurate but commercially incomplete. “Low-code” suggests visual configuration tools designed around human drag-and-drop workflows. “Developer platform” excludes the operators, designers, and business users who should eventually create applications.

The category should communicate three ideas:

1. Coding agents are a first-class authoring client.
2. Applications are generated against semantic platform primitives rather than arbitrary stacks.
3. The output is professional production software, not only a prototype.

### 1.2 The core company claim

> **The most reliable way for an LLM to create professional software is not to ask it to reproduce every operational detail. It is to give it a small language of high-value application semantics and a host that guarantees the operational consequences.**

That claim is technical enough to be defensible and simple enough to organize a business.

## 2. The central technical and commercial insight

The system is based on a separation between **denotational semantics** and **operational semantics**.

Denotational semantics describe what an application operation means. `productSearch.search(query)` means “return relevant products under this application's catalog and policy.” `booking.reserve(slot)` means “create a valid reservation for this slot.” `payments.checkout(order)` means “create a checkout flow for this order.”

Operational semantics describe how the result is produced safely. Product search may require indexing, ranking, typo tolerance, tenant filters, cache invalidation, usage metering, and failover. Booking may require transactions, locking, time zones, idempotency, reminders, cancellation policy, and concurrency control. Payments may require secret storage, webhook verification, retries, reconciliation, and dispute handling.

A conventional coding agent must generate or configure both layers. Your platform lets the agent concentrate on the first.

### 2.1 Why this matters for LLMs

LLMs perform better when the solution space is constrained by a coherent grammar and when APIs express intent directly. The benefit is not merely fewer tokens. It includes:

- Fewer opportunities to invent insecure glue code.
- Fewer dependency and version choices.
- Smaller application programs that are easier to review.
- More deterministic static validation.
- More repeatable tests.
- Easier upgrades because operational fixes live in modules.
- Better portability across user interfaces and deployment targets.
- More reliable rollback because releases include exact module versions.

An agent that needs to implement product search from a database query, a frontend filter, and a ranking heuristic may produce plausible code. An agent that calls a typed product-search module can produce a complete application behavior with much less ambiguity.

Lovable described the same pressure from the opposite direction when it built its Supabase integration: making the backend usable by an LLM required a concise, structured, goal-oriented translation layer over the underlying API.[^S25] That observation is important. The product opportunity is not merely to connect an agent to more APIs. It is to design the semantic layer that lets the agent use those capabilities correctly.

### 2.2 Why this matters commercially

The semantic module is also the unit of monetization. A product-search module can be sold because it contains ongoing operational value. A booking module can be sold because it handles difficult concurrency and lifecycle rules. A managed identity module can be sold because it encapsulates security, persistence, and compliance work.

This creates a business with stronger economics than pure generation credits. The customer continues paying because the application continues using capabilities that remain valuable after the first prompt.

### 2.3 The improvement loop

The platform produces a compounding improvement loop:

```text
more applications
    -> more repeated operational patterns
    -> better high-level modules and templates
    -> less code required per application
    -> higher agent success rate
    -> faster creation and lower support cost
    -> more applications
```

General-purpose app builders can also add primitives. The defensible opportunity is to build a coherent module system, release contract, runtime, UI protocol, and commercial ecosystem in which those primitives are the primary programming model rather than optional integrations.

## 3. The product promise

The product promise should be stated in customer language:

> **Describe an application, review the important decisions, and deploy professional software in minutes. The platform keeps it secure, versioned, observable, and changeable.**

That promise contains six commitments.

### 3.1 Creation is fast

A user should be able to move from idea to an interactive application during one session. The coding agent can generate the app program, data model, UI intent, tests, and release manifest. The user should not need to create cloud accounts or wire credentials manually for every primitive.

### 3.2 The result is real software

The result has a stable URL, persistent data, authentication, permissions, logs, metrics, backups, custom domains, and an explicit release history. It can serve real users and business processes.

### 3.3 Changes are controlled

Every change creates a release candidate. The platform shows code and authority diffs, runs tests and smoke checks, activates the candidate, and supports rollback to an exact release.

### 3.4 Security is structural

Applications receive only selected modules, permissions, resources, and network access. HTTP authentication, authorization, CSRF, audit, rate limits, and resource binding run in the Go host before JavaScript business logic executes.

### 3.5 Design quality is not an afterthought

The platform combines agent generation with a typed UI system, reusable design recipes, and professional renderer targets. A customer should not have to choose between rapid generation and a coherent product experience.

### 3.6 Operations improve centrally

When the platform fixes a module implementation, improves observability, or patches runtime security, applications can receive the improvement through controlled module upgrades rather than bespoke rewrites.

## 4. Why this moment matters

The timing argument has four parts.

### 4.1 Application generation has become a mass-market behavior

Replit's 2026 financing announcement describes users ranging from children and teachers to employees creating legal assistants and sales leaderboards, with more than 50 million users overall.[^S1] Lovable describes its mission as enabling the 99% who cannot code to build production software, and its funding trajectory reflects investor conviction in that behavior.[^S3] Wix acquired Base44 for approximately $80 million in 2025 to expand into natural-language software creation.[^S7]

The market no longer needs to be convinced that people will ask AI to build applications. Vercel reported in April 2026 that more than 30% of deployments on its platform were initiated by coding agents, up roughly tenfold over six months.[^S17] Wix reported in March 2026 that Base44 had reached $100 million in annual recurring revenue approximately one year after founding.[^S18] These figures do not guarantee that a new entrant will win. They show that agent-driven creation and operation are becoming normal software behavior rather than a novelty.

### 4.2 The prototype-to-production gap is now visible

Vercel's February 2026 v0 announcement explicitly argued that AI-generated software had become a shadow-IT and security problem in enterprises, citing credentials in prompts, exposed data, deleted databases, and missing audit trails.[^S5] That is a direct statement from a major deployment platform that generation alone is not enough.

Your product thesis begins where that problem becomes expensive.

### 4.3 Agents need stable tools, not only better models

Model capability will continue improving. That helps every participant. It also reduces defensibility for products whose only advantage is prompt orchestration. Stable application semantics, module ecosystems, operational history, release data, user distribution, and trusted integrations remain differentiated even when the underlying model changes.

Lovable's MCP offering shows that app platforms increasingly expect external agents to call platform primitives directly.[^S4] Your system is naturally compatible with that direction because the runtime, module resolver, release APIs, and deployment controls can all be exposed as agent tools.

### 4.4 High-level primitives are becoming the competitive frontier

When Vercel acquired the new.website team into v0, it highlighted built-in forms, databases, SEO, and content management as primitives that reduce the amount of prompting required for baseline functionality.[^S6] This is strong evidence for the general principle. Your opportunity is to carry that approach much further into application operations: search, booking, CRM, commerce, logistics, identity, workflows, and professional release management.

## 5. What the company is not

A strong pitch becomes clearer when it excludes adjacent categories.

### 5.1 Not another model wrapper

The company should be able to change model providers without changing the product identity. Model quality matters, but the durable product is the application semantics and runtime.

### 5.2 Not a conventional platform-as-a-service with an AI chat box

A normal platform gives developers infrastructure primitives and asks them to assemble an application. This platform gives agents and builders business-level capabilities and compiles them into controlled infrastructure.

### 5.3 Not a visual low-code suite

Visual tools may be useful for editing schemas, pages, and workflows. They are not the conceptual center. The primary artifact is a versioned application program that agents can create and humans can inspect.

### 5.4 Not a services company disguised as software

Paid implementation work is useful during launch. It becomes a trap if every app requires unique platform engineering. The company must measure module reuse, template reuse, and declining delivery cost. Services exist to discover repeatable product patterns.

### 5.5 Not a promise that arbitrary hostile JavaScript is safe in one shared process

The production system must preserve operating-system isolation, strict module selection, hard resource limits, and worker disposal. The pitch should be ambitious without making security claims the architecture cannot support.

### 5.6 Not all markets at once

Personal applications, social coordination, small-business software, professional systems, and enterprise applications can share a platform. They do not share acquisition channels, support expectations, pricing, or compliance requirements. The company must sequence them.


# Part II. The Product as a Business

## 6. The application ladder

The product vision spans a useful application ladder.

![Application ladder](./_founder_assets/segment_ladder.png)

### 6.1 Personal applications

Examples include a private email triage client, a personal knowledge dashboard, a todo system, a household inventory, or a custom feed. These applications demonstrate the emotional power of software that fits one person's exact workflow.

The commercial challenges are low willingness to pay, high variety, consumer support, privacy expectations, and uncertain retention. Personal applications should initially serve as dogfood, demos, and a source of product insight.

### 6.2 Friend and community applications

Examples include a barbecue scheduling poll, a trip planner, a club membership page, a shared shopping list, or a local sports league. These applications are shareable and can create organic distribution. They are also temporary. A successful friend-shared app may be used intensely for one week and then never again.

The product should eventually support ephemeral application pricing and automatic archival. This segment can drive awareness without carrying the company’s early revenue target.

### 6.3 Small-business applications

Examples include booking, quoting, customer intake, service catalogs, invoices, customer portals, and lightweight CRM. These users have recurring problems and budgets. They also require reliability, payments, permissions, custom domains, support, and data ownership.

This segment is commercially attractive but fragmented. Distribution through studios, agencies, accountants, consultants, and vertical partners can be more efficient than direct acquisition one small business at a time.

### 6.4 Professional operational systems

Examples include logistics dashboards, inventory workflows, field-service applications, approval systems, supplier portals, and custom commerce operations. These applications have higher annual value and stronger retention. They also require integration, migration, audit, role models, and service-level expectations.

The platform's technical architecture is particularly valuable here because operational semantics and release safety matter more than visual novelty.

### 6.5 Enterprise applications

Enterprises want private applications, identity integration, governance, approved modules, network controls, data residency, audit, support, and procurement. The revenue can be large, but sales cycles and product requirements can overwhelm a young company.

Enterprise should be an expansion path after the single-node and multi-tenant operational model is proven with smaller customers.

## 7. The end-to-end product experience

The product should be designed around a complete lifecycle rather than a code editor.

### 7.1 Start from intent

A builder describes the application, imports a brief, or selects a vertical pack. The system asks questions only when a decision changes behavior, authority, or price.

Example:

```text
Build a booking site for a mobile bicycle repair service.
Customers choose a service, address, and time slot.
Require a card authorization but charge after the repair.
Let staff manage availability and mark jobs complete.
Send email and SMS reminders.
Use our existing logo and a calm, high-contrast design.
```

### 7.2 Generate a plan before code

The agent should produce a visible plan containing:

- Pages, routes, actions, and workflows.
- Actors and permission boundaries.
- Data entities and retention.
- Selected modules and resources.
- External integrations and secrets.
- Estimated recurring cost.
- Tests and success criteria.

The user approves the plan or edits it. This step prevents the agent from making invisible operational decisions while appearing to “just build.”

### 7.3 Generate the application program

The output is a compact JavaScript/TypeScript application plus a typed UI program and tests. The source remains visible and versioned. Advanced builders can edit it directly. Most users can continue through conversation or structured editors.

### 7.4 Resolve commercial and security policy

The platform checks:

- Whether the account is entitled to each module.
- Whether the environment policy permits each permission.
- Whether required resources and secret bindings exist.
- Whether quotas are sufficient.
- Whether the change requires additional approval.

This is where the business model and technical model meet. A premium search module is both a product feature and a release dependency.

### 7.5 Build and validate

The build service validates the source graph, compiles TypeScript, executes the program collector, validates route and workflow plans, runs tests, scans assets, calculates fingerprints, and produces a signed release artifact.

### 7.6 Preview with real semantics

The preview environment should use the same module versions and security pipeline as production, with preview-scoped data and secrets. A preview that swaps real modules for mocks can hide the failures that matter.

### 7.7 Deploy deliberately

The builder sees an authority and behavior diff:

```text
+ module booking@1.4.0
+ module messaging.sms@2.1.3
+ secret binding twilio-production
+ permission messaging.send
+ table reservations
~ public route /book/:serviceId
+ authenticated route /staff/jobs
```

The release is activated after smoke checks. High-risk changes can require approval or canary rollout.

### 7.8 Operate and evolve

The platform provides logs, usage, costs, module health, user activity, backups, release history, and rollback. The agent can investigate production through a read-only identity and propose changes. It cannot silently mutate production.

## 8. High-level modules are the leverage point

Modules should be designed as complete product capabilities, not thin API wrappers.

### 8.1 Core modules

Core modules establish the programming environment:

- HTTP routes and planned security.
- Typed UI and assets.
- Basic database and key-value storage.
- Time, jobs, and queues.
- Logs, metrics, and application configuration.
- File and object storage under scoped paths.

These modules may be included in baseline plans because every application needs them.

### 8.2 Premium business modules

Premium modules encode high-value operational domains:

| Module | Simple application API | Hidden operational semantics |
|---|---|---|
| Product search | `search.products.query(...)` | Indexing, ranking, typo tolerance, tenant filtering, reindexing, quotas |
| Booking | `booking.reserve(...)` | Availability, time zones, concurrency, cancellation, reminders, idempotency |
| Commerce | `commerce.orders.create(...)` | Tax, inventory, payment state, refunds, reconciliation, webhooks |
| CRM | `crm.contacts.upsert(...)` | Identity resolution, deduplication, lifecycle, privacy, audit |
| Messaging | `messages.send(...)` | Provider routing, templates, consent, retries, rate limits, cost controls |
| Identity | `identity.users.invite(...)` | OIDC, sessions, credentials, keys, recovery, replay protection |
| Logistics | `shipments.plan(...)` | State machines, carrier integration, labels, events, exceptions |
| Documents | `documents.generate(...)` | Templates, rendering, storage, signatures, retention |
| Workflow | `workflow.start(...)` | Durable state, retries, timers, compensation, approvals |

The first module catalog should remain small. Ten excellent modules are more valuable than one hundred inconsistent wrappers.

### 8.3 Module design rules

Every premium module should have:

- A stable semantic contract.
- Versioned TypeScript declarations.
- Explicit permissions and effects.
- Configuration and binding schemas.
- Deterministic test fakes.
- Bounded inputs and outputs.
- Idempotency rules.
- Usage dimensions and price metadata.
- Migration and deprecation policy.
- Audit and redaction behavior.
- A clear failure model.

### 8.4 A module is not necessarily implemented in-process

The JavaScript API may be backed by:

- A Go library in the worker.
- A managed platform service.
- A customer resource.
- A third-party API through a broker.
- An isolated workflow service.

The application should not need to know which operational implementation is used when the semantic contract is preserved.

## 9. Professional release semantics are part of the product

Many app builders treat deployment as the final button after generation. This platform should treat release management as a visible customer feature.

### 9.1 Immutable releases

A release includes source, program contract, module lock, renderer version, resource bindings, policy, tests, and provenance. Changing any of those produces a different release.

### 9.2 Rollback

Rollback selects an exact previous release and creates a new traffic generation. It does not mean “run whatever source used to be in the repository.” Database compatibility is evaluated separately.

### 9.3 Approval

Approval policy is based on authority change. A CSS adjustment may deploy automatically. Adding outbound network access, a payment effect, or a new secret may require a human approval.

### 9.4 Agent identities

Coding agents have keys, grants, expiration, nonces, and audit history. An agent can prepare and request a release without holding human administrator credentials.

### 9.5 Operational agents

A production agent can inspect logs, metrics, release history, and module status under a read-only identity. It can propose a patch and release candidate. The platform preserves a human or policy-controlled promotion boundary.

## 10. Design quality is a founding advantage

The technical system is difficult to build. The design system is equally important to the company outcome.

### 10.1 Why design matters more in generated software

When users can create many applications quickly, visual inconsistency becomes a platform-level problem. A mediocre generated interface makes the entire system feel unreliable, even when the backend is correct. A coherent renderer and semantic UI grammar produce three advantages:

- Applications look professional without requiring the agent to generate every layout detail.
- Accessibility and interaction behavior can improve centrally.
- Designers can create reusable recipes and vertical packs that agents apply consistently.

### 10.2 The designer founder's leverage

The designer founder should not be presented as someone who “makes the demos look good.” The role is to define the product language through which generated applications become understandable, editable, and trustworthy.

That includes:

- Intent-level UI primitives.
- Design-system presets.
- Review and approval interfaces.
- Visual authority diffs.
- Application templates and vertical packs.
- Builder workflows for non-technical users.
- Public demos that make the platform's ambition legible.

### 10.3 Design as distribution

Exceptional demos can create demand before the full self-service product exists. The company should publish complete applications, not only feature videos. A potential customer should be able to use a booking app, CRM, logistics portal, or community scheduler and understand that it was generated from compact application semantics.

# Part III. Market, Competition, and Positioning

## 11. The category is real and crowded

The first investor question will be: why is this not Replit, Lovable, v0, Base44, Retool, or a future feature of a cloud platform?

A weak answer lists technical implementation differences. A strong answer begins by conceding the market reality.

AI application creation has become one of the fastest-growing software categories. Replit announced that annualized revenue increased from $2.8 million to $150 million in less than a year before its September 2025 financing, then raised $400 million at a $9 billion valuation in March 2026.[^S1][^S2] Lovable raised $330 million at a $6.6 billion valuation after previously raising $200 million at $1.8 billion.[^S3] Vercel transformed v0 from a component generator into a full-stack production product and explicitly positioned enterprise security and production integration as central requirements.[^S5] Wix acquired Base44 to make natural-language application creation a major product pillar.[^S7]

This evidence has two implications.

First, investors do not need another abstract explanation of why natural-language software creation matters. The category has been validated.

Second, a new company cannot win by claiming that its agent writes code slightly better. The incumbent platforms have distribution, capital, model access, hosting, integrations, and large engineering teams. The opportunity must be based on a different product architecture and go-to-market.

## 12. Competitive map

### 12.1 Direct prompt-to-application platforms

| Platform | Current strength | What customers receive | Strategic opening for this company |
|---|---|---|---|
| Replit | Large user base, broad framework support, integrated agent, database, deployment, collaboration | General-purpose hosted projects and applications | Smaller semantic programs, stronger module contracts, explicit release governance, application marketplace economics |
| Lovable | Strong design experience, full-stack web generation, Supabase and integration workflow, external-agent access through MCP | Conventional web application code and hosted project | Operational modules as primary language, not connectors; broader business semantics; controlled runtime profiles |
| v0 / Vercel | Full-stack Next.js generation, Git workflows, enterprise deployment, strong frontend and cloud integration | Vercel-native full-stack applications | Runtime designed specifically for compact agent-authored apps; platform-neutral business modules; lower application complexity |
| Base44 / Wix | Code-free natural-language apps with built-in auth and database; large distribution parent | Integrated no-code applications and agents | Inspectable JS program, third-party module ecosystem, professional release contracts, open provider model |

The direct competitors are not identical. Replit is broad and increasingly enterprise-aware. Lovable is strong in rapid full-stack creation and design. v0 has a powerful deployment position and an explicit enterprise narrative. Base44 combines built-in application primitives with Wix distribution.

Your differentiation must survive all four improving.

### 12.2 Adjacent infrastructure platforms

| Category | Examples | Strength | Limitation relative to the thesis |
|---|---|---|---|
| Backend-as-a-service | Supabase, Firebase, Convex | Data, auth, functions, storage | The agent still assembles application behavior, UI, security policy, and operations |
| Serverless hosting | AWS Lambda, Cloudflare Workers, Vercel Functions, Deno Deploy | Scalable execution and deployment | Execution primitives are lower-level than business semantics |
| Internal tools | Retool, Power Apps, Appsmith | Connectors, enterprise data access, fast internal UI | Less suited to arbitrary customer-facing products, personal apps, and open module composition |
| Commerce platforms | Shopify, Wix, Squarespace | Deep vertical semantics, payments, themes, app ecosystems | Strong in a defined vertical rather than general application behavior |
| Search and specialist APIs | Algolia, Twilio, Stripe, SendGrid | Excellent domain infrastructure | Each integration still requires application-specific orchestration and operational glue |
| Coding agents and IDEs | Cursor, Claude Code, GitHub Copilot, Windsurf | Professional code generation and repository work | They operate on general codebases and do not define the production application substrate |

The long-term company can be understood as combining the best property of vertical platforms with the breadth of an application cloud: strong semantic primitives without being restricted to one vertical.

### 12.3 The competitive question to answer

The investor should leave with this distinction:

> **Current AI app builders generate stacks. This platform generates applications over a governed semantic runtime.**

The difference must be visible in a demo. Show the same application built with compact module calls, authority review, exact releases, and rollback. Do not rely on an architecture slide alone.

## 13. Where the durable differentiation can live

No single technical feature creates a moat. The defensibility comes from a system of reinforcing assets.

### 13.1 Module semantics and operational history

A booking module improves as the company learns from thousands of booking applications. It accumulates edge cases, migration knowledge, provider integrations, tests, observability, templates, and performance data. The JavaScript API remains small while the operational implementation becomes difficult to reproduce.

The same is true for product search, CRM, messaging, commerce, identity, logistics, and workflow.

### 13.2 Application corpus

A large corpus of successful application programs creates valuable training and evaluation data:

- Which plans lead to accepted releases.
- Which module combinations recur.
- Which generated patterns survive production.
- Which tests catch real failures.
- Which UI recipes produce engagement.
- Which operational changes require human approval.

The platform can improve its agent, validators, templates, and modules from real application outcomes rather than code-completion benchmarks.

### 13.3 Release and operational data

Production history creates another data asset:

- Deployment success and rollback behavior.
- Module-specific incident patterns.
- Cost distributions by application type.
- Safe default quotas.
- Common authority expansions.
- Upgrade compatibility.

This information makes future generated applications more reliable and makes the platform difficult to replace with a prompt wrapper.

### 13.4 Design system and renderer ecosystem

A mature intent-level UI system can become a durable distribution and quality advantage. Designers contribute recipes, component packs, vertical presets, and visual standards. Applications inherit improvements without regenerating every frontend.

### 13.5 Module marketplace and provider relationships

A module ecosystem creates two-sided value. Builders get capabilities. Module providers get distribution and a billing surface. Application users create usage. The platform becomes the trusted policy and metering layer.

Shopify's app ecosystem shows that platform-managed installation, billing, extensions, and distribution can support substantial developer economics; Shopify currently takes no revenue share on the first $1 million in lifetime app revenue and 15% above that for most developers.[^S11] The exact terms are not a template to copy, but the strategic pattern is relevant.

### 13.6 Trust and governance

If the platform becomes known for safe agent-generated applications, the trust model itself becomes a commercial asset. Enterprises, agencies, and module providers will prefer a platform where permissions, secrets, releases, and audit are explicit.

## 14. The danger of a horizontal launch

The platform is horizontal at the architecture level. A horizontal launch would produce an incoherent business.

A message such as “build any app, from personal email to enterprise logistics” creates several problems:

- No buyer knows whether the product is designed for them.
- Product requirements conflict across segments.
- The team cannot prioritize modules.
- Pricing becomes arbitrary.
- Sales cycles range from minutes to a year.
- Support expectations vary from community help to contractual response times.
- Investors cannot identify a repeatable acquisition motion.

Airtable eventually became a broad platform, but its founders described becoming more opinionated and targeted over time even after early horizontal adoption.[^S26] A young company with fewer resources should narrow sooner.

The correct framing is:

> **Broad product vision, narrow first customer, repeated expansion.**

## 15. Beachhead options

The team should evaluate five plausible entry points.

### 15.1 Personal app cloud

**Customer:** Technically curious individuals and professionals.  
**Examples:** Personal email client, knowledge dashboard, todo system, household tools.  
**Advantages:** Emotional product, strong demos, large theoretical audience, dogfooding.  
**Problems:** Low willingness to pay, privacy burden, varied integrations, high churn, consumer acquisition cost.  
**Recommendation:** Keep as product inspiration and a viral surface, not the first business.

### 15.2 Friend and community micro-apps

**Customer:** Event organizers, clubs, families, informal communities.  
**Examples:** Doodle-style scheduling, trip planning, shared lists, voting, event pages.  
**Advantages:** Simple sharing loop, clear delight, low sales friction.  
**Problems:** Short application lifetime, low revenue, seasonal use, support volume.  
**Recommendation:** Use as the free tier and public demonstration of just-in-time software.

### 15.3 Small service businesses

**Customer:** Clinics, salons, coaches, repair services, local operators, professional services.  
**Examples:** Booking, intake, CRM, quotes, reminders, payments, customer portals.  
**Advantages:** Clear recurring value, repeatable module set, existing spend, strong retention when embedded.  
**Problems:** Fragmented acquisition, onboarding, migration, local-market differences.  
**Recommendation:** Excellent end-customer target, preferably reached through channels.

### 15.4 Studios, agencies, and automation consultants

**Customer:** Designers, developers, no-code agencies, operations consultants, fractional technical teams.  
**Examples:** Client portals, booking systems, internal tools, lightweight commerce, custom workflows.  
**Advantages:** One customer creates many apps; customers already sell implementation; strong fit with designer founder; immediate willingness to pay; concentrated feedback.  
**Problems:** Risk of becoming a services tool, need multi-client management, customer support expectations.  
**Recommendation:** Best initial commercial wedge.

### 15.5 Enterprise internal application platform

**Customer:** IT, operations, product, and innovation teams.  
**Examples:** Internal agents, workflows, approval apps, data portals, department tools.  
**Advantages:** Large contracts, strong governance need, explicit shadow-IT pain.  
**Problems:** Long sales cycles, compliance, connectors, procurement, private networking, support.  
**Recommendation:** Build toward it, but do not make it the first sales motion.

### 15.6 Scoring the options

The following table uses a 1–5 score, where 5 is strongest. The numbers are hypotheses to test.

| Beachhead | Willingness to pay | Repeated module use | Distribution efficiency | Product fit today | Venture expansion | Total |
|---|---:|---:|---:|---:|---:|---:|
| Personal apps | 2 | 3 | 2 | 4 | 4 | 15 |
| Friend/community apps | 1 | 3 | 4 | 4 | 3 | 15 |
| Small service businesses direct | 4 | 5 | 2 | 4 | 4 | 19 |
| Studios/agencies | 5 | 5 | 4 | 4 | 5 | 23 |
| Enterprise internal platform | 5 | 4 | 2 | 2 | 5 | 18 |

## 16. Recommended beachhead

The recommended go-to-market is **studio-led professional application creation**, with small-business and operational applications as the primary outputs.

### 16.1 The customer

The initial buyer is a small team that already earns money creating or improving software for others:

- Digital product studios.
- Brand and design agencies expanding into applications.
- No-code and automation consultancies.
- Fractional CTO and operations consultants.
- Vertical SaaS implementers.
- Independent designers with strong client relationships.

### 16.2 The job

Their job is not “write JavaScript.” It is:

> **Turn a client requirement into a polished, reliable, maintainable application quickly enough to preserve margin and respond to change.**

### 16.3 The value proposition

The platform lets them:

- Produce higher-value applications without staffing a full engineering team.
- Use agents to generate logic while preserving design control.
- Reuse booking, CRM, search, payments, auth, messaging, and workflow modules.
- Give clients professional release, domain, data, and audit features.
- Manage multiple client applications from one workspace.
- Charge setup fees and recurring retainers.
- Avoid taking responsibility for every low-level operational failure.

### 16.4 Why this creates a venture path

The studio channel can expand into a platform economy:

1. Studios create many applications.
2. Repeated applications reveal vertical packs and modules.
3. The platform productizes those patterns.
4. Less technical builders use the product directly.
5. Module providers and specialists join the marketplace.
6. Enterprises adopt the governed runtime internally.

The studio is not the final customer definition. It is the first efficient distribution and learning mechanism.

## 17. Bottom-up market model

Do not lead the pitch with a generic “low-code market will be $X billion” slide. Bottom-up economics are more credible.

### 17.1 Studio platform opportunity

Illustrative assumptions:

- 10,000 serious studios, agencies, and automation consultancies in reachable markets.
- Average platform revenue of $500 per month.
- Average runtime and module revenue of $500 per month across their client apps.

```text
10,000 customers × $1,000 monthly total revenue
= $10M MRR
= $120M ARR
```

The exact customer count must be validated. The calculation shows that the initial channel can support a substantial company without assuming consumer scale.

### 17.2 Production application opportunity

Illustrative assumptions:

- 200,000 active business and community applications.
- Average platform runtime and module revenue of $40 per month.

```text
200,000 apps × $40 per month
= $8M MRR
= $96M ARR
```

A mature platform could support many more applications, but early planning should use numbers that can be explained through customer acquisition and application count.

### 17.3 Enterprise opportunity

Illustrative assumptions:

- 500 enterprise customers.
- Average annual contract value of $150,000.

```text
500 × $150,000
= $75M ARR
```

Enterprise is a separate motion and should not be counted as an automatic consequence of the self-service product.

### 17.4 Marketplace opportunity

Illustrative assumptions:

- $500 million in annual third-party module, template, and expert transactions.
- 15% platform take rate.

```text
$500M × 15%
= $75M annual marketplace revenue
```

Marketplace revenue appears only after the platform has meaningful distribution. It should be treated as an expansion model, not as the first financial plan.

### 17.5 The combined ambition

These models show several independent paths to a $100 million-plus revenue company. The pitch should not add every scenario into a fictional trillion-dollar TAM. It should show that the initial wedge is large enough and that the platform has credible expansion surfaces.


# Part IV. Business Models and Pricing

## 18. The business-model menu

The platform can generate revenue through several models. Each aligns with a different value event.

### 18.1 Builder subscription

The customer pays for the ability to create, collaborate, review, and manage applications. This model is predictable and easy to understand. It resembles current app-builder subscriptions, which range from entry-level plans around $20 per month to professional plans around $100 per month on Replit.[^S9]

### 18.2 Generation usage

The customer pays for model and agent usage. This protects margins when complex builds consume more inference. The risk is that credits make customers feel uncertain about the cost of completing an application.

Generation should be metered transparently and should not be the main value story.

### 18.3 Runtime usage

The customer pays for active applications, compute, storage, bandwidth, database size, scheduled jobs, messages, and end users. This aligns revenue with operational cost and customer value.

### 18.4 Premium module subscription

The customer pays for a capability that has recurring operational value. Examples include product search, booking, CRM, commerce, managed identity, and messaging.

### 18.5 Transaction fee

The platform takes a small percentage of bookings, commerce, payments, or marketplace activity. This can produce large revenue but creates pricing sensitivity and regulatory complexity. Use only when the platform materially participates in the transaction.

### 18.6 Marketplace take rate

The platform takes a percentage when customers buy third-party modules, templates, design systems, or expert services.

### 18.7 Services and implementation

The company charges for application delivery, migration, module creation, and enterprise integration. This creates early revenue and learning but does not receive software multiples unless delivery becomes repeatable and partner-led.

### 18.8 Enterprise license and support

The customer pays for SSO, governance, private networking, audit, data residency, dedicated capacity, private modules, and contractual support.

### 18.9 OEM and embedded platform

Another software company embeds the builder or runtime into its own product. This can become a high-value channel after the APIs and multi-tenant control plane are mature.

## 19. Recommended revenue architecture

![Business model stack](./_founder_assets/business_model_stack.png)

The recommended model separates four ledgers.

### 19.1 Creation ledger

Tracks:

- Agent/model usage.
- Parallel build tasks.
- Compilation and preview resources.
- Asset generation.
- Collaborative builder seats.

The builder subscription includes a predictable allowance. Overage can be purchased.

### 19.2 Runtime ledger

Tracks:

- Active production applications.
- Requests and compute time.
- Storage and database size.
- Bandwidth.
- Scheduled and background work.
- Active end users where appropriate.

Runtime bills should remain legible. A customer should be able to attribute cost to an application.

### 19.3 Module ledger

Tracks:

- Module subscription state.
- Usage dimensions specific to a module.
- Underlying vendor costs.
- Platform markup or revenue share.
- Entitlement snapshots used by releases.

Algolia, for example, prices search through search requests and stored records on its current Grow plan.[^S13] A product-search module could expose a simpler package while metering those underlying dimensions internally.

### 19.4 Contract ledger

Tracks:

- Enterprise commitments.
- Negotiated discounts.
- Support level.
- Marketplace transactions.
- Credits and promotional allowances.
- Channel partner economics.

Stripe's billing products explicitly support subscription, usage, credit, and hybrid pricing models, which makes them a suitable billing substrate once the platform's own usage ledger is authoritative.[^S12]

## 20. Packaging and pricing hypotheses

The following packaging is a starting hypothesis, not a launch announcement.

| Plan | Price hypothesis | Customer | Included value |
|---|---:|---|---|
| Free | $0 | Personal exploration and shared micro-apps | One public or private app, limited generation, platform domain, core modules, strict quotas |
| Creator | $25/month | Individual professional builder | Five apps, custom domains, more generation, core runtime allowance, basic support |
| Pro | $99/month | Serious builder or small team | Twenty apps, collaboration, private apps, environments, release approvals, longer history |
| Studio | $399/month | Agency, studio, consultant | Client workspaces, 100 apps, white-label controls, pooled credits, team roles, priority support |
| Business | $1,000–$3,000/month | Larger studio or operating company | Higher limits, audit retention, advanced modules, service guarantees, migration support |
| Enterprise | Custom | Large organization or platform | SSO, private networking, dedicated resources, data residency, private modules, premium support |

### 20.1 Application charges

A production app can include a base platform charge:

| App class | Base fee hypothesis | Intended use |
|---|---:|---|
| Ephemeral shared app | Free or $1–$5 active month | Polls, events, temporary coordination |
| Personal persistent app | Included or $5/month | Private productivity and household tools |
| Professional app | $15–$50/month | Custom domain, backups, auth, production support |
| Business-critical app | $100+/month | Higher availability, audit, advanced modules, support |

Usage applies above included allowances.

### 20.2 Why not charge per seat alone

An application platform creates value through applications and usage, not only through builders. Per-seat pricing would undercharge studios with a few builders and many client apps. It would also make personal and community apps unattractive if every end user required a paid seat.

Use builder seats for creation and app/runtime economics for operation.

### 20.3 Why not charge only for compute

Pure infrastructure pricing obscures the value of semantic modules and makes the business compete with commodity compute. The customer is paying to avoid building and operating complex capabilities, not only for CPU milliseconds.

### 20.4 Price presentation

The customer-facing bill should show:

```text
Studio plan                         $399.00
18 active production apps          $270.00
Booking module: 6 apps             $174.00
Product search: 2 apps + usage      $91.40
Messaging usage                     $38.20
Compute and storage overage         $24.80
                                  --------
Total                               $997.40
```

Clarity builds trust and lets studios pass costs to clients.

## 21. Premium module economics

### 21.1 Three module pricing forms

A module can use:

1. **Flat per-app subscription.** Best when value is recurring and usage is predictable.
2. **Usage-based pricing.** Best when vendor cost and customer value scale with operations.
3. **Hybrid base plus usage.** Best when every active integration creates fixed operational cost and heavy users create variable cost.

### 21.2 Example price hypotheses

| Module | Price hypothesis | Meter |
|---|---:|---|
| Booking | $29/app/month | Reservations above included allowance |
| Product search | $19/app/month | Records and search requests |
| CRM | $29/app/month | Contacts above allowance |
| Messaging email | $10/app/month | Messages sent |
| Messaging SMS | $10/app/month | Provider cost + platform margin |
| Commerce | $49/app/month | Orders or GMV overage |
| Managed identity | $20/app/month | Monthly active users above allowance |
| Workflow | $25/app/month | Executions and durable wait time |
| Documents | $15/app/month | Documents generated and stored |
| Premium database | $25/app/month | Storage, backups, connections |

The platform should test willingness to pay before implementing elaborate pricing. A module with strong adoption but weak willingness to pay may belong in a higher plan rather than as a separate SKU.

### 21.3 Margin formula

For each module:

```text
module revenue
- underlying provider cost
- platform compute and storage
- support allocation
- expected incident and refund cost
= module gross profit
```

Set price to preserve a target gross margin after realistic usage, not only at median usage.

### 21.4 Build versus partner

Use this decision framework:

| Condition | Prefer platform implementation | Prefer external provider |
|---|---|---|
| Semantics are central to differentiation | Yes | Maybe as internal dependency |
| Commodity infrastructure already excellent | No | Yes |
| Provider margin leaves room for markup | Maybe | Yes |
| Data residency or security requires control | Yes | No |
| Operational complexity is larger than current team | No | Yes |
| Customer needs portability across providers | Build stable abstraction | Use multiple adapters |

The platform can own the semantic contract while outsourcing infrastructure.

## 22. Marketplace economics

A module marketplace should come after first-party modules establish quality standards.

### 22.1 Marketplace participants

- Infrastructure vendors exposing managed capabilities.
- Domain specialists building booking, logistics, compliance, or commerce modules.
- Designers selling component systems and vertical UI packs.
- Studios selling templates and implementation packages.
- Open-source maintainers offering supported module editions.

### 22.2 Platform responsibilities

The marketplace must provide more than listing and billing. It should own:

- Module identity and versioning.
- Security review and permission declarations.
- Configuration and binding schemas.
- Type declarations and documentation.
- Test fixtures.
- Installation through release resolution.
- Metering and payout.
- Deprecation and incident policy.
- Compatibility with runtime profiles.
- Customer support boundaries.

### 22.3 Take-rate hypothesis

A simple launch model:

- 0% on the first $25,000 in lifetime module revenue to encourage experimentation.
- 15% on software module and template revenue after the threshold.
- 10% on referred expert services where the platform handles discovery and payment.
- Negotiated economics for strategic infrastructure providers.

The take rate should be justified by distribution, billing, security review, and operational tooling.

## 23. Services as a launch mechanism

Services can accelerate the company if they are structured as product discovery.

### 23.1 Recommended offers

| Offer | Price hypothesis | Duration | Output |
|---|---:|---:|---|
| Application discovery sprint | $2,500–$5,000 | 1 week | Scope, workflow model, prototype plan, fixed build quote |
| Professional app launch | $7,500–$25,000 | 2–6 weeks | Production application, data setup, domain, training |
| Vertical pack implementation | $5,000–$15,000 | 1–3 weeks | Configured reusable solution with minor extensions |
| Enterprise pilot | $25,000–$100,000 | 6–12 weeks | Governed environment, integrations, security review, pilot apps |

### 23.2 Productization discipline

Every delivery should record:

- New platform code required.
- Existing modules used.
- New module candidates.
- Template reuse.
- Time by function.
- Support incidents.
- Recurring revenue attached.
- Whether the next similar app becomes cheaper.

The target is declining marginal delivery effort.

### 23.3 Partner-led delivery

The company should avoid scaling an internal agency. Train studios and certified experts to deliver applications. The platform team handles difficult module, runtime, and security work.

## 24. Enterprise and private deployments

Enterprise packaging can include:

- SAML/OIDC SSO and SCIM.
- Approved module catalog.
- Private modules.
- Dedicated worker pools.
- Private network connectivity.
- Customer-managed keys.
- Data residency.
- Extended audit retention.
- Policy-as-code and approvals.
- Staging and production separation.
- Support response commitments.
- Software bill of materials and provenance.
- Private cloud or customer-controlled deployment.

The enterprise product should not promise arbitrary Kubernetes deployment on day one. Start with dedicated managed environments and a controlled single-node or cluster profile.

## 25. Unit economics and gross margin

The platform has four major cost categories.

### 25.1 Generation cost

Model inference, build sandboxes, previews, image generation, and agent retries. This cost can be controlled with included credits, model routing, caching, and semantic modules that reduce generated work.

The semantic architecture creates a direct economic advantage: fewer tokens and fewer retries per accepted application.

### 25.2 Runtime cost

Compute, memory, storage, bandwidth, databases, backups, queues, logs, and sandbox overhead. Goja can be efficient for orchestration-heavy applications, but isolation and warm capacity create real cost.

### 25.3 Module provider cost

Search requests, messages, payment services, identity MAUs, maps, AI calls, and other third-party usage.

### 25.4 Support cost

Generated applications can create support volume when user expectations exceed platform guarantees. Strong validation, observability, templates, and module semantics reduce this cost.

### 25.5 Gross margin targets

Illustrative target ranges:

| Revenue stream | Mature gross margin target |
|---|---:|
| Builder subscription | 75%–90% |
| Runtime | 55%–75% |
| First-party modules | 65%–85% |
| Third-party marketplace | 85%–95% on take-rate revenue |
| Services | 25%–50% |
| Enterprise support | 50%–75% |

Blended margin can be lower early while infrastructure is underutilized and services are significant.

### 25.6 Cost metrics to instrument immediately

- Generation cost per accepted release.
- Generation cost per active application.
- Runtime cost per active application and per request.
- Support minutes per active application.
- Gross margin by module.
- Idle warm capacity cost.
- Cost of failed builds and releases.
- Cost of preview environments.

## 26. Illustrative financial scenarios

These are operating models, not forecasts.

### 26.1 Year-one design-partner scenario

| Metric | Assumption |
|---|---:|
| Paid design partners | 25 |
| Average initial project revenue | $12,000 |
| Services revenue | $300,000 |
| Active production apps at year end | 100 |
| Average platform/runtime/module revenue per app | $75/month |
| Exit app MRR | $7,500 |
| Studio subscriptions at year end | 20 × $399 |
| Exit studio MRR | $7,980 |
| Total exit MRR | ~$15,500 |

The primary outcome is not revenue scale. It is evidence of repeated application patterns and recurring platform value.

### 26.2 Early product-market-fit scenario

| Metric | Assumption | Annualized revenue |
|---|---:|---:|
| 250 Studio accounts | $399/month | $1.20M |
| 2,500 professional apps | $30/month base | $0.90M |
| Premium modules | $35/app average on 60% attach | $0.63M |
| 20 Business accounts | $2,000/month | $0.48M |
| Marketplace take-rate revenue | — | $0.30M |
| Total | — | **$3.51M ARR** |

### 26.3 Scale scenario

| Metric | Assumption | Annualized revenue |
|---|---:|---:|
| 2,000 Studio/Pro accounts | $250 blended/month | $6.0M |
| 25,000 production apps | $25/month base | $7.5M |
| Premium modules | $40/app average on 70% attach | $8.4M |
| 100 enterprise customers | $150,000 ACV | $15.0M |
| Marketplace take-rate revenue | — | $5.0M |
| Total | — | **$41.9M ARR** |

The company can become large before consumer scale. Consumer and personal applications become strategic upside rather than a dependency.

# Part V. Go-to-Market

## 27. Design partner program

The design partner program is the bridge between a technically mature prototype and a repeatable business.

A design partner is not a friendly user who agrees to provide feedback. A design partner has a real application need, a deadline, a named decision-maker, and some form of economic commitment.

### 27.1 Program objective

The first cohort should answer four questions:

1. Which application patterns recur across customers?
2. Which platform capabilities create willingness to pay?
3. Which parts of delivery still require founder intervention?
4. Does the customer treat the result as disposable output or as durable software?

### 27.2 Partner profile

Prioritize partners that have:

- An application need that can go live within six weeks.
- Real users or a real internal team.
- A workflow involving at least three reusable modules.
- A decision-maker available weekly.
- Budget for implementation and recurring hosting.
- Permission to publish an anonymized case study.
- A problem that is important but not safety-critical in the first cohort.

Avoid the first cohort being dominated by:

- Highly regulated medical or financial workflows.
- Massive legacy migrations.
- Applications that require many custom hardware integrations.
- Customers who want unlimited bespoke development for a small fixed fee.
- “Innovation” teams with no path to production use.

### 27.3 Offer structure

A practical first offer:

> **We will design and launch one production application in four weeks for a fixed fee. The application includes a custom domain, authentication, data, release history, and thirty days of iteration. After launch, the client pays a recurring platform and support fee.**

Example commercial terms:

- $10,000 fixed launch fee.
- $250–$1,000 monthly platform and support fee depending on usage and modules.
- Explicit scope and named success metric.
- Permission to use anonymized product and operational metrics.
- No transfer of platform IP.
- Customer owns application data and receives source export under defined terms.

### 27.4 Cohort composition

A useful first cohort of five:

1. A design agency client portal.
2. A service-business booking and CRM application.
3. A community coordination application with payments.
4. An internal inventory or logistics workflow.
5. A lightweight commerce catalog with search and customer accounts.

This range tests the shared platform without scattering into unrelated edge cases.

### 27.5 Weekly operating rhythm

| Day | Activity |
|---|---|
| Monday | Review user behavior, support issues, and release history |
| Tuesday | Customer workflow and design session |
| Wednesday | Build module or template improvements shared across partners |
| Thursday | Ship candidate release and run acceptance checks |
| Friday | Commercial review: cost, scope, recurring value, next application opportunity |

### 27.6 Exit criteria

A design partner is successful when:

- The application is used by real users for four consecutive weeks.
- The customer requests an additional workflow or second application.
- At least 70% of the implementation uses reusable modules and templates.
- Recurring revenue exceeds direct runtime and support cost by a healthy margin.
- The customer can explain the value without referring to the novelty of AI.

## 28. Studio and agency channel

![Commercialization sequence](./_founder_assets/gtm_sequence.png)

Studios and agencies can become the platform's first scalable distribution channel.

### 28.1 Why the channel works

A studio already has:

- Customer trust.
- Problem discovery skills.
- Design and domain expertise.
- A sales pipeline.
- A business model based on delivery.

The platform supplies:

- Agent-efficient implementation.
- Secure runtime and modules.
- Release and operational controls.
- Multi-client workspace management.
- Recurring infrastructure and module billing.

The combined offer lets studios sell more ambitious work with fewer specialized engineers.

### 28.2 Studio product requirements

The Studio plan needs features that a single-builder product does not:

- Separate client organizations and environments.
- Role-based access for studio staff and clients.
- White-label preview and handoff.
- Client-specific billing and cost attribution.
- Template and module catalogs controlled by the studio.
- Approval workflows.
- Export and offboarding.
- Reusable design systems.
- Support escalation from studio to platform.
- A portfolio dashboard showing app health and costs.

### 28.3 Partner economics

A partner can earn revenue through:

- Discovery and design fees.
- Application launch fees.
- Monthly support retainers.
- Resale margin on platform plans or modules.
- Marketplace template and module revenue.
- Referrals.

The platform should avoid complicated revenue sharing until the basic product works. A first partner model can offer:

- 20% recurring referral share for twelve months.
- Wholesale Studio pricing above a minimum app volume.
- Marketplace payout for templates and modules.
- Certification and lead distribution after quality review.

### 28.4 Certification

Certification should measure actual capability:

- Can the partner scope an application into supported semantics?
- Can they design safe actor and permission models?
- Can they build and test a release?
- Can they interpret usage and incidents?
- Can they manage data import and customer handoff?
- Can they identify when custom platform engineering is required?

A certification badge without delivery quality will damage trust.

## 29. Vertical solution packs

Vertical packs convert repeated service work into product.

### 29.1 Pack definition

A vertical pack contains:

- A reference application program.
- Data schemas and migration rules.
- UI recipes and brand variables.
- Module selections and configuration defaults.
- Role and permission model.
- Tests and sample data.
- Onboarding questions.
- Reporting and operational dashboards.
- Pricing guidance for partners.

### 29.2 Candidate packs

| Pack | Core modules | Initial buyer |
|---|---|---|
| Service booking | Booking, CRM, payments, messaging, identity | Local service businesses and agencies |
| Client portal | Identity, documents, messaging, workflow, billing | Agencies and professional services |
| Lightweight commerce | Catalog, product search, orders, payments, messaging | Independent brands and studios |
| Field operations | Scheduling, forms, inventory, maps, messaging | Repair, inspection, and service teams |
| Community organizer | Events, polls, payments, messaging, identity | Clubs, associations, informal communities |
| Inventory and supplier portal | Database, workflow, documents, notifications, search | Small distributors and operations teams |

### 29.3 Pack selection rule

Build a pack only after three independent customers request substantially similar behavior. One customer proves a project. Three customers suggest a product.

### 29.4 Pack economics

A pack may be:

- Included in a Studio plan.
- Sold as a one-time template.
- Sold as a monthly vertical product.
- Used as the basis for a partner certification.
- Bundled with premium modules.

## 30. Self-service and product-led growth

Self-service should be built after the team knows which decisions can be safely automated.

### 30.1 Self-service activation event

The activation event is not “user sent a prompt.” It is:

> **The user deployed an application that another person successfully used.**

Track the funnel:

```text
account created
  -> intent submitted
  -> plan approved
  -> preview generated
  -> release deployed
  -> first external user
  -> second session or transaction
  -> application retained after 30 days
```

### 30.2 Free product

The free tier should demonstrate the core experience while controlling cost:

- One active application.
- Platform subdomain.
- Strict generation and runtime quotas.
- Core modules only.
- Community support.
- Automatic sleep or archival.
- Public templates and forkable examples.

Friend-shared and community apps fit naturally here.

### 30.3 Viral surfaces

Potential loops:

- “Made with” link on free applications.
- Fork this application.
- Reuse this poll, event, or form.
- Invite a collaborator to edit.
- Publish a template.
- Install a module.
- Share a design-system recipe.

The viral loop must lead back to application creation, not only to end-user traffic.

### 30.4 Agent API and MCP

Expose the platform as tools for external coding agents:

- Create project.
- Inspect module catalog.
- Generate or update application source.
- Validate plan.
- Create preview.
- Read build errors.
- Request release.
- Read production logs under policy.
- Propose rollback.

Lovable's MCP integration demonstrates demand for app platforms that external agents can operate.[^S4] Lovable has also begun exposing published applications themselves to ChatGPT, Claude, and other assistants through hosted MCP servers, showing that application distribution is moving toward agent-mediated use as well as agent-mediated creation.[^S19] The platform should treat both directions as first-class APIs, with explicit identities, grants, versions, and audit.

### 30.5 Source export and trust

Customers will ask whether they are locked in. Provide:

- Application source export.
- Data export.
- Release manifest and module lock.
- Static asset export.
- Clear explanation of which premium modules require the platform runtime.

The company does not need to promise that every managed capability can run independently. It should make the boundary explicit.

## 31. Founder-led sales

The founders should sell the first applications. This is not a temporary embarrassment. It is how the company learns the language of the market.

### 31.1 Discovery conversation

A useful sequence:

1. What recurring workflow currently requires spreadsheets, email, forms, and manual coordination?
2. Who performs it and how often?
3. What breaks or gets delayed?
4. What software has been tried?
5. What would a successful application change?
6. Which users and permissions exist?
7. Which systems must be integrated?
8. What is the economic value of solving it?
9. Who can approve a paid pilot?
10. What deadline creates urgency?

Do not begin with a platform tour.

### 31.2 Qualification

Use a simple qualification score:

| Dimension | Weak | Strong |
|---|---|---|
| Pain | Interesting inconvenience | Frequent costly workflow failure |
| Urgency | Someday | Deadline within 60 days |
| Authority | Enthusiast | Budget owner involved |
| Repeatability | Unique research project | Common workflow with reusable modules |
| Integration | Many inaccessible systems | Few clear systems or fresh workflow |
| Economic value | Hard to quantify | Revenue, labor, or customer experience impact |

### 31.3 Sales artifact

The best sales artifact is a working application produced from the customer's own workflow. A generic slide deck is less persuasive than a branded preview with real sample data and an authority plan.

### 31.4 Paid pilots

Free pilots create weak signals. Use a smaller paid discovery sprint when the customer is not ready for a full application. Payment proves priority and establishes a professional relationship.

### 31.5 Expansion

The platform's natural expansion metric is **applications per customer**. After the first app succeeds, ask:

- Which adjacent workflow uses the same users or data?
- Which manual process should become an action or dashboard?
- Which external customer experience is still handled through email?
- Which internal report should become interactive?

## 32. Partnerships and ecosystem

### 32.1 Infrastructure partnerships

Potential partners include:

- Search providers.
- Payment and billing platforms.
- Messaging providers.
- Identity providers.
- Database and object-storage vendors.
- Mapping and logistics providers.
- AI model and inference platforms.

A partner module gives the provider agent-native distribution. The platform gets operational capability without building every service.

### 32.2 Design and agency partnerships

The design founder can establish partnerships with:

- Product design communities.
- Web and brand studios.
- No-code consultants.
- Figma and design-system educators.
- Freelance networks.

The message is not “replace your developers.” It is “expand the class of software your team can deliver profitably.”

### 32.3 Open-source strategy

Open source can improve trust and developer adoption. Candidate open components:

- Goja runtime SDK.
- Module provider interface.
- Application program types.
- Widget IR and renderer contracts.
- Local development tools.
- Example modules.

Potential closed or hosted value:

- Control plane.
- Managed worker isolation.
- Premium first-party modules.
- Billing and entitlements.
- Enterprise governance.
- Hosted build and release service.
- Marketplace distribution.

Open-source strategy should be based on distribution and trust, not ideology.

### 32.4 Strategic platform integrations

Longer term, the application runtime can be offered inside:

- Website builders.
- Collaboration products.
- CRM and ERP systems.
- Vertical SaaS products.
- AI assistant platforms.
- Cloud marketplaces.

The integration pitch is: give your users a safe way to generate custom application behavior without exposing your internal systems directly.

## 33. Metrics that matter

### 33.1 Creation metrics

- Median time from intent to first preview.
- Median time from intent to first live external user.
- Prompt-to-valid-plan rate.
- Plan-to-accepted-release rate.
- Number of agent retries per accepted release.
- Generation cost per accepted release.
- Human edits per generated application.

### 33.2 Application quality metrics

- 7-, 30-, and 90-day active application retention.
- Percentage of releases rolled back.
- Incidents per 1,000 application-days.
- Support minutes per active application.
- Test coverage of declared routes and actions.
- Percentage of changes deployed without founder intervention.

### 33.3 Commercial metrics

- Paid design partners.
- Monthly recurring revenue.
- Applications per paying account.
- Premium module attach rate.
- Expansion revenue.
- Gross margin by customer and module.
- Partner-sourced pipeline.
- Sales cycle length.
- Pilot-to-recurring conversion.

### 33.4 Semantic leverage metrics

These metrics are specific to the thesis:

- Percentage of application behavior expressed through platform modules.
- Median application source size.
- Module reuse across applications.
- Number of new platform capabilities required per customer project.
- Reduction in generation tokens versus a conventional stack baseline.
- Frequency of operational fixes delivered through module upgrades rather than app rewrites.

### 33.5 North-star candidates

Potential north-star metrics:

1. **Weekly active production applications.** Measures durable output, but treats tiny and important apps equally.
2. **Successful end-user actions per week.** Measures application value, but requires consistent action semantics.
3. **Gross profit from active applications.** Measures economic health, but is less inspiring for product teams.
4. **Applications retained after ninety days per active builder.** Measures creation quality and repeatability.

The recommended early north star is:

> **Number of applications created on the platform that remain active and used by external users ninety days later.**

This prevents the company from optimizing for disposable demos.


# Part VI. Seed Fundraising

## 34. Is this pre-seed or seed?

Funding stage is not determined by years of engineering effort. It is determined by the evidence available to investors.

![Proof ladder](./_founder_assets/proof_ladder.png)

### 34.1 Technical proof already present

The existing system addresses difficult problems that most prompt-to-app prototypes avoid:

- Owned Goja runtime and module composition.
- Secure HTTP route planning and host enforcement.
- Identity, sessions, agents, and capabilities.
- Versioned releases, audit, and rollback concepts.
- Widget UI semantics.
- Paid-module and entitlement architecture.
- A credible path to isolated execution.

This supports a strong claim that the team can build the platform.

### 34.2 Product proof present or near-term

The designer founder's demos can show that the platform produces compelling applications rather than only infrastructure. Investors should see several complete, distinct applications built on the same semantics.

### 34.3 Customer proof required

Seed investors will still ask:

- Who pays?
- Why now rather than later?
- Which app types repeat?
- How much implementation is manual?
- Do users keep the apps?
- Why does a customer choose this over Replit or Lovable?

Paid design partners answer these questions better than another technical roadmap.

### 34.4 Economic proof

The most valuable seed evidence is:

- Customers create a second application.
- Premium modules attach to a large percentage of apps.
- Recurring revenue grows faster than support cost.
- Applications remain active after ninety days.
- The platform becomes cheaper and faster to use with each repeated pattern.

### 34.5 Stage recommendation

Use this decision table:

| Evidence at launch of process | Recommended description |
|---|---|
| Excellent prototype and demos, no paid users | Pre-seed / formation round |
| 3–10 paid pilots, early live apps | Seed, with honest early-traction framing |
| 10–30 paying customers, recurring revenue, repeated modules | Strong seed |
| Repeatable channel, $50k+ MRR, expansion evidence | Large seed or early Series A discussion |

## 35. Financing scenarios

### 35.1 Lean pre-seed

**Raise:** $1.5M–$2.5M  
**Runway:** 15–18 months  
**Team:** Founders plus two to three hires  
**Purpose:** Find the wedge, ship design partners, harden the runtime, establish pricing.

Advantages:

- Less dilution.
- Faster close.
- Strong pressure to focus.

Risks:

- Insufficient capital for security, infrastructure, modules, and GTM simultaneously.
- Fundraising returns quickly if enterprise pilots take longer.

### 35.2 Institutional seed

**Raise:** $3M–$4.5M  
**Runway:** 18–24 months  
**Team:** Founders plus five to seven hires  
**Purpose:** Build the studio product, deliver core module catalog, operate production apps, prove recurring revenue.

This is the recommended default if the team enters the process with paid design partners.

### 35.3 Infrastructure seed

**Raise:** $5M–$8M  
**Runway:** 24 months  
**Team:** Founders plus eight to twelve hires  
**Purpose:** Build isolated multi-tenant execution, broader modules, enterprise governance, and aggressive distribution.

Carta reported that AI infrastructure seed rounds had a median of $13 million at a $66 million post-money valuation in its May 2026 analysis.[^S10] That data reflects a concentrated and exceptional category. Do not anchor to it unless investors independently classify the company that way and the customer proof supports it.

### 35.4 Recommended use of $3.5 million

Illustrative budget over twenty months:

| Category | Amount | Purpose |
|---|---:|---|
| Founder salaries and benefits | $480,000 | Sustainable full-time commitment |
| Engineering hires | $1,150,000 | Runtime/security, modules, frontend/product |
| GTM and customer success | $420,000 | Founding commercial hire, design-partner delivery |
| Cloud and model cost | $350,000 | Build, preview, worker, logging, inference |
| Security, legal, insurance | $250,000 | Company, IP, privacy, contracts, reviews |
| Design, research, events | $150,000 | User research, partner program, launch |
| Contingency | $700,000 | Hiring variance and runway protection |
| Total | **$3,500,000** | — |

The contingency is intentionally large because infrastructure cost and hiring timelines are uncertain.

### 35.5 Round structure

Carta reports that SAFEs remain common at pre-seed and smaller seed rounds, while priced rounds predominate in larger seed financings.[^S14] YC publishes standard post-money SAFE documents, but the company should use experienced counsel for the actual financing.

A practical approach:

- Use a post-money SAFE for a fast pre-seed with a small number of investors.
- Use a priced seed when raising institutional capital, establishing a board, and hiring materially.
- Avoid accumulating many different SAFE caps and side letters.
- Model dilution across all outstanding instruments before signing.

## 36. The investor narrative

A seed pitch needs one coherent sequence.

### 36.1 Opening

> **AI can now generate an application, but it still generates too much fragile operational code. We built an application runtime where agents write small JavaScript programs against high-level modules for search, booking, identity, payments, UI, and workflow. The platform handles security, releases, rollback, and operations. This makes real custom software fast enough to create just in time.**

### 36.2 Problem

- Businesses and individuals have countless workflows that do not justify a conventional software project.
- Coding agents lower implementation cost, but generated general-purpose stacks are difficult to secure, operate, and maintain.
- Current app builders produce impressive first versions, while production semantics remain distributed across generated code and third-party integrations.

### 36.3 Insight

- LLMs perform better when APIs express business intent directly.
- Operational complexity can be centralized in versioned modules.
- The same abstraction improves security, maintainability, unit economics, and monetization.

### 36.4 Product

- Agent generates compact application program.
- Platform resolves modules, permissions, resources, and price.
- Go host enforces HTTP security before JavaScript.
- Typed UI renderer produces polished interfaces.
- Release system validates, deploys, audits, and rolls back.

### 36.5 Wedge

- Studios and agencies use the platform to deliver professional operational apps.
- Each account creates many apps.
- Repeated applications become vertical packs and modules.

### 36.6 Business model

- Builder subscriptions.
- Runtime and application fees.
- Premium modules.
- Marketplace and enterprise.

### 36.7 Defensibility

- Module semantics and operational history.
- Application and release corpus.
- Design system.
- Marketplace and provider relationships.
- Trusted production runtime.

### 36.8 Team

- Technical founder built the difficult runtime and release foundation.
- Designer founder built impressive product and UI demonstrations.
- Commercial leadership is being recruited around a clear design-partner program.

### 36.9 Ask

- Raise enough to prove the studio channel, ship core modules, and operate hundreds of durable production applications.

## 37. Twelve-slide pitch deck

### Slide 1. Company and claim

**Headline:** Professional software, generated at the level of intent.  
**Subhead:** An agent-native application cloud built on secure, versioned business modules.

Show one high-quality application and one compact source excerpt.

### Slide 2. The problem

**Headline:** AI can generate code faster than teams can safely operate it.

Show the operational surface a generated app normally requires:

```text
auth + permissions + database + migrations + payments + webhooks
+ search + UI + deployment + secrets + logs + rollback + support
```

### Slide 3. The insight

**Headline:** Agents should specify application meaning; the platform should own operational behavior.

Show:

```javascript
booking.reserve(...)
payments.checkout(...)
search.products.query(...)
```

beside the hidden operational responsibilities.

### Slide 4. Product

Show the flow:

```text
intent -> plan -> compact JS app -> validated release -> live application
```

Include screenshots of plan review, preview, and release diff.

### Slide 5. Why the architecture wins

- Smaller programs.
- Fewer insecure choices.
- Central upgrades.
- Exact releases and rollback.
- Better agent success and lower generation cost.
- Paid modules with recurring value.

### Slide 6. Demonstrations

Show three applications using the same platform:

- Community scheduling app.
- Booking and CRM app.
- Logistics or commerce operations app.

Avoid a grid of ten shallow examples.

### Slide 7. Market timing

Use sourced facts:

- Replit: 50M+ users and $9B valuation.[^S1]
- Lovable: $6.6B valuation after $330M Series B.[^S3]
- Vercel: production/security shift in v0.[^S5]
- Base44 acquisition by Wix.[^S7]

**Conclusion:** App generation is validated; durable production semantics are the next control point.

### Slide 8. Beachhead and go-to-market

**Headline:** Start with studios that create many professional apps.

Show:

```text
paid design partners -> vertical packs -> studio channel -> self-service -> marketplace
```

### Slide 9. Business model

Show builder subscription, app runtime, premium modules, and enterprise/marketplace.

### Slide 10. Traction and proof

Use actual metrics only:

- Live apps.
- Paid partners.
- Time to production.
- Module reuse.
- App retention.
- Revenue.
- Generation-cost reduction.

If the process starts before traction, label the slide “Proof already built” and distinguish technical, product, and customer proof.

### Slide 11. Team

Show why the combination of systems engineering and product design is unusual and necessary. Include the commercial role being recruited only if the search is concrete.

### Slide 12. Financing and milestones

Example:

> Raising $3.5 million to reach 250 studio accounts, 2,500 durable production apps, ten premium modules, and repeatable partner-led acquisition.

Use milestones you can defend. Do not commit to arbitrary customer counts because they make the slide look ambitious.

## 38. The live demo

The live demo is the most important fundraising asset.

### 38.1 Demo goal

Prove four claims in under eight minutes:

1. An agent can create a real application quickly.
2. The application uses high-level modules rather than generated operational glue.
3. Production deployment is controlled and reviewable.
4. The same system supports materially different applications.

### 38.2 Recommended demo script

**Minute 0–1: Start from a real brief**

```text
Create a booking application for a mobile bicycle repair business.
Customers select a service, location, and available slot.
Staff can manage jobs. Require login for staff and card authorization for customers.
```

**Minute 1–2: Show generated plan**

Highlight actors, routes, data, modules, permissions, and estimated price.

**Minute 2–4: Show application program**

Open the booking route and payment action. Emphasize the small semantic API.

**Minute 4–5: Show preview**

Use the application as a customer and as staff. The designer founder should control this part.

**Minute 5–6: Show release diff**

Add SMS reminders. The release diff shows a new messaging module, permission, and recurring cost.

**Minute 6–7: Deploy and inspect**

Show release ID, smoke test, audit, and production logs.

**Minute 7–8: Break and rollback**

Deploy an intentionally bad change to preview or canary, show failure, and return to the previous release.

### 38.3 Backup demo

Never rely on network calls or a single live environment. Prepare:

- Recorded full demo.
- Local or staged environment.
- Static screenshots.
- Prebuilt release candidates.
- A two-minute compressed path.

### 38.4 Demo discipline

Do not spend most of the demo watching the agent type. Investors have seen that. Spend time on the plan, semantic program, professional application, authority diff, and rollback.

## 39. Investor objections and answers

### Objection 1: “Replit or Vercel will build this.”

**Answer:** They will add more primitives, which validates the direction. Our architecture makes semantic modules, controlled runtime profiles, and release governance the primary programming model. We are starting with repeated operational applications and a module economy rather than general repositories. The question is whether we can build distribution and a module corpus before general platforms close the gap.

Do not claim incumbents cannot compete. Explain why focused execution can establish a valuable control point.

### Objection 2: “Why JavaScript and Goja?”

**Answer:** JavaScript is familiar to models, developers, and tooling. Goja gives us a pure-Go runtime with explicit ownership and a narrow host surface. The value is not JavaScript compatibility with every npm package. It is a compact, controlled application language that links to Go-backed modules and can run efficiently inside a professional host.

### Objection 3: “Is this low-code?”

**Answer:** The platform can expose visual editors, but the primary artifact is a versioned application program and release plan. The authoring client can be an LLM, a human developer, or a designer. Security and operations are host-owned.

### Objection 4: “Why will apps not become unmaintainable?”

**Answer:** Application programs are small; operational semantics live in versioned modules; source graphs are closed; releases pin exact dependencies; route and effect plans are validated; upgrades and rollbacks are explicit. Maintainability is a product feature, not an assumption about model quality.

### Objection 5: “How do you compete with vertical SaaS?”

**Answer:** Initially, the platform does not replace every mature vertical product. It wins workflows that are too custom for off-the-shelf SaaS and too small for conventional development. Repeated patterns become vertical packs. Deep vertical modules may eventually compete with or complement vertical SaaS.

### Objection 6: “Who is the buyer?”

**Answer:** The first buyer is a studio or consultant delivering operational applications. The end users are small businesses, communities, and teams. One studio creates multiple apps, which creates concentrated distribution and repeated module demand.

### Objection 7: “Is services revenue hiding weak software demand?”

**Answer:** We track reusable module percentage, delivery hours per app, recurring revenue, application retention, and apps per studio. The service layer is a deliberate discovery channel. The plan includes clear productization thresholds.

### Objection 8: “What is the moat if models improve?”

**Answer:** Better models reduce creation cost for everyone. Our moat is the semantic module catalog, operational data, application corpus, release and governance system, design system, and ecosystem distribution. Better models make these assets more valuable because more people can use them.

### Objection 9: “Can Goja safely run untrusted code?”

**Answer:** The interpreter is not the isolation boundary. Production workers use explicit module permissions, resource budgets, interruption, worker disposal, and operating-system sandboxing. We do not claim that one in-process VM contains hostile tenants.

### Objection 10: “Why now if you still need a business co-founder?”

**Answer:** The existing team already covers two hard founding functions: systems technology and product/design. The company has a defined design-partner motion and a structured search for commercial leadership. We are not outsourcing the business problem; the founders are running customer discovery and sales now.

## 40. Data room and diligence

### 40.1 Company documents

- Certificate of incorporation.
- Bylaws.
- Board and stockholder consents.
- Capitalization table.
- Founder stock purchase and vesting documents.
- 83(b) election evidence where applicable.
- Option plan.
- Material contracts.

### 40.2 Intellectual property

- Founder and employee IP assignment.
- Open-source inventory and license policy.
- Third-party model and API terms.
- Module provider agreements.
- Trademark and domain inventory.
- Security architecture and threat model.

### 40.3 Product and technical

- Architecture overview.
- Technical companion textbook.
- Product roadmap.
- Demo environments.
- Release and module contracts.
- Security review and known risks.
- Reliability metrics.
- Infrastructure cost model.
- Dependency and SBOM process.

### 40.4 Commercial

- Customer interview notes.
- Design-partner agreements.
- Pipeline.
- Revenue and usage data.
- Pricing tests.
- Case studies.
- Cohort retention.
- Unit economics.
- Competitive analysis.

### 40.5 Team

- Founder bios.
- Hiring plan.
- Cofounder role specification.
- Advisor relationships.
- References.

### 40.6 Financial

- Historical expenses.
- Eighteen- to twenty-four-month plan.
- Model and cloud cost assumptions.
- Financing scenarios.
- Cap table dilution model.
- Tax and accounting status.

## 41. Investor targeting

Build the target list by thesis, not fame.

### 41.1 Investor archetypes

| Archetype | What they should understand | Why they may care |
|---|---|---|
| AI application infrastructure | Agent tooling, model commoditization, runtime economics | Semantic modules and governed execution create durable infrastructure |
| Developer tools and platforms | Open source, APIs, ecosystems, bottom-up adoption | xgoja, module providers, studio channel, marketplace |
| Design and creation tools | Designer workflows, collaborative creation, visual quality | Strong design founder and intent-level UI system |
| Vertical SaaS and SMB software | Distribution, willingness to pay, channel economics | Generated custom apps expand beyond fixed SaaS products |
| Enterprise application platforms | Governance, shadow IT, identity, audit | Safe employee-created applications and private modules |
| Marketplace investors | Two-sided ecosystems and take-rate models | Module, template, and expert marketplace potential |

### 41.2 Example programs and communities

Potential founder and investor ecosystems to research include Y Combinator, South Park Commons, Entrepreneurs First, Antler, Heavybit, and specialist seed funds in developer tools and AI infrastructure. South Park Commons currently describes a founder community and funding range from $1 million to $10 million for venture-scale companies.[^S20] Entrepreneurs First explicitly supports individuals testing cofounders and building from early ideas.[^S21]

This is not a recommendation to join an accelerator by default. The right program can provide cofounder density, narrative help, customer introductions, and a concentrated fundraising process. The wrong program consumes time and introduces financing constraints.

### 41.3 Target-list construction

Create a spreadsheet with:

- Firm and fund.
- Relevant partner.
- Stage and check size.
- Relevant portfolio companies.
- Conflict risk.
- Thesis fit.
- Warm introduction path.
- Likely objection.
- Meeting status.
- Reference calls available.

Prioritize forty firms:

- Ten high-conviction targets.
- Fifteen strong fits.
- Fifteen useful market-learning conversations.

### 41.4 Strategic investors

Strategic capital can help with modules and distribution but creates risks:

- Competitors learn product details.
- Exclusivity requests limit the marketplace.
- Future investors perceive dependency.
- Product priorities shift toward one provider.

Accept strategic investment only when the commercial benefit is concrete and the terms preserve platform neutrality.

## 42. Running the process

Fundraising works best as a concentrated process with prepared proof.

### 42.1 Before launch

Have ready:

- Final deck.
- Live and recorded demo.
- One-page memo.
- Data room.
- Financial plan.
- Customer references.
- Clear round size and use of funds.
- Founder role story.
- Investor target list and warm paths.

### 42.2 Meeting sequence

1. Begin with friendly investors who will give direct feedback.
2. Refine the pitch after five to eight meetings.
3. Start high-priority firms in a compressed window.
4. Create momentum through customer and product updates, not artificial deadlines.
5. Run partner meetings close together.
6. Reference-check investors before accepting a term sheet.

### 42.3 Meeting goals

The first meeting should produce one of four outcomes:

- Clear pass with useful reason.
- Follow-up request.
- Partner introduction.
- Customer or cofounder introduction.

A vague “keep us updated” is not progress unless the update criteria are explicit.

### 42.4 Weekly fundraising review

Track:

- Meetings completed.
- Follow-ups scheduled.
- Repeated objections.
- Product or commercial proof requested.
- Investor conviction signals.
- Reference introductions.
- Round allocation and ownership.

### 42.5 Choosing investors

Evaluate:

- Belief in the long-term platform, not only current AI excitement.
- Understanding of developer tools and application economics.
- Ability to help recruit commercial leadership.
- Customer and partner network.
- Behavior in difficult portfolio situations.
- Follow-on strategy.
- Conflict with direct competitors.
- Speed and clarity of decision-making.

The highest valuation is not automatically the best financing.


# Part VII. The Founding Team

## 43. The current team story

The company already has the two capabilities that are hardest to manufacture after incorporation: a founder who has built the difficult technical substrate and a founder who can make the result feel like a product rather than an infrastructure demonstration.

That combination is unusually relevant to this market. Agent-generated software fails in two different ways. It can be operationally unsound, and it can be visually or behaviorally incoherent. The technical founder addresses the first class of failure through a controlled runtime, explicit modules, secure HTTP semantics, identity boundaries, versioned releases, rollback, and isolation. The design founder addresses the second through product direction, interface systems, application demonstrations, interaction quality, and a coherent visual language.

The missing capability is not “business” in the abstract. The missing capability is ownership of the market-facing company system:

- Choosing an initial customer and refusing distracting segments.
- Converting technical differentiation into a category narrative.
- Running customer discovery without turning every request into a feature commitment.
- Closing paid design partners and turning them into repeatable products.
- Designing pricing, packaging, and channel economics.
- Building the investor process and recruiting the first commercial team.
- Establishing a company cadence in which product, customer, and capital decisions reinforce one another.

![Founding team operating system](./_founder_assets/founding_team_system.png)

### 43.1 The technical founder's durable contribution

The technical founder should be described as more than the person who wrote the runtime. The founder has developed a point of view about how agents should create software:

1. Application code should express business intent through compact JavaScript or TypeScript.
2. Difficult operational semantics should live behind versioned native modules.
3. The host should enforce authentication, authorization, release policy, resource access, and runtime ownership.
4. Generated software should be inspectable, reproducible, rollbackable, and supportable.
5. The module system should be commercially meaningful, not merely a package registry.

This is the intellectual foundation of the company. Investors need to see that the technical work is not a collection of clever components. It is one architecture built around a specific market insight.

The technical founder's near-term job is therefore not to finish every subsystem. It is to make the architecture legible through a small number of undeniable applications, to close the remaining production gaps that block external use, and to create a module boundary that other engineers can extend.

### 43.2 The design founder's durable contribution

The design founder is not a downstream service provider who makes technical demos presentable. Design is part of the product architecture.

A platform that lets agents create professional applications needs a theory of interface generation. Without one, every application becomes a pile of generated components, inconsistent interaction patterns, and one-off responsive behavior. A typed widget protocol, semantic recipes, renderer targets, and application-level design constraints let the system create products that feel intentional while remaining easy for an agent to author.

The design founder should own or co-own:

- Product experience and interaction principles.
- The visual and semantic design system.
- The demo portfolio and customer-facing application quality.
- Design-partner discovery around end-user workflows.
- Template, recipe, and vertical-pack quality.
- The editor and review experience for generated applications.
- Brand and category expression.

The investor narrative should make this founder advantage concrete. Show several applications that share the same platform but do not look like the same template. Show how a design rule becomes a reusable system capability. Show the difference between generated code and generated product quality.

### 43.3 The commercial founder's required contribution

The third founder, if one joins, must complete the system rather than duplicate it. The person should be able to turn a broad technical platform into a sequence of narrow commercial proofs.

The required behavior is closer to an early-stage CEO and company builder than to a later-stage sales executive. A strong candidate can spend the morning interviewing an operations manager, the afternoon restructuring the product narrative with the other founders, and the evening building a seed investor map. The candidate must be comfortable selling something that still changes every week while protecting the long-term architecture from bespoke customer demands.

The person should not need to implement the runtime, but must be able to understand and explain why the runtime matters. A commercial founder who treats the product as a generic AI app builder will erase the differentiation. A commercial founder who can explain semantic modules, production guarantees, and the studio wedge in customer language can make the differentiation valuable.

### 43.4 The founding-team narrative

The external story should be concise:

> **We are a technical founder who built the agent-native runtime, a design founder who built an unusually strong application experience and demo system, and a commercial founder or founding executive who turns that technology into a repeatable market. Together we cover infrastructure, product quality, and company creation.**

Do not exaggerate team completeness before the commercial role is filled. Investors will discover the gap quickly. State it as an active and disciplined search, and demonstrate that the existing founders are already doing customer work rather than waiting for someone else to begin it.

### 43.5 Internal ownership before the third founder arrives

Until the role is filled, the existing founders need explicit temporary ownership:

| Company function | Temporary owner | Weekly output |
|---|---|---|
| Product and technical roadmap | Technical founder | One prioritized roadmap and release review |
| Design system and application quality | Design founder | Demo/application review and design-system decisions |
| Customer discovery | Shared, with one meeting owner | Interview notes, problem ranking, follow-ups |
| Sales pipeline | One named founder | Updated pipeline, next actions, pricing evidence |
| Company narrative and fundraising prep | One named founder | Deck revisions, investor map, proof gaps |
| Finance and administration | Technical founder or fractional operator | Cash report, contracts, legal checklist |

Shared responsibility without a named owner usually means no responsibility. Temporary ownership can change, but it must remain explicit.

## 44. Do you need a business co-founder?

A co-founder is not a job opening with a larger equity grant. A co-founder is a person who accepts company-level risk, takes durable authority over a major part of the system, and remains responsible when the original plan fails.

The correct question is therefore not “Would a business person help?” The answer to that question is always yes. The correct question is:

> **Does the company need another person with founder-level authority and commitment to own the market, capital, and organization for the next decade?**

### 44.1 Reasons to add a commercial co-founder

The case is strong when several conditions are true:

- The technical founder wants to remain deeply involved in architecture and product rather than spend most weeks selling, fundraising, recruiting, and managing.
- The design founder wants to own product and design rather than the entire commercial organization.
- The market requires category creation and founder-led enterprise or channel sales.
- A candidate brings exceptional founder-market fit, not merely general management experience.
- The candidate is willing to join before certainty, compensation, and organizational support exist.
- The candidate changes the rate at which the company learns, closes customers, and recruits.

Technical founders frequently seek complementary commercial skills. YC's co-founder matching data found that 74% of engineering founders preferred a co-founder with sales and marketing skills, while 53% preferred operations skills.[^S15] That preference does not prove a specific candidate is right. It confirms that the gap is common and strategically meaningful.

### 44.2 Reasons not to add one yet

Do not add a co-founder because fundraising feels uncomfortable, because investors ask who sells, or because the founders want someone to “handle business.” Those motivations create a vague role with impossible expectations.

Delay or reject the co-founder decision when:

- The candidate wants a mature product, salary, and team before committing.
- The candidate's primary value is investor introductions.
- The person cannot personally sell the first ten customers.
- The person does not develop a credible understanding of the product's architecture.
- The person proposes broad partnerships instead of direct customer work.
- The candidate treats design as marketing polish or technical work as an implementation detail.
- The existing founders have not decided who wants to be CEO.
- The company has not defined the decisions the new founder would own.

A strong founding commercial executive can be better than a weak co-founder. Titles should follow demonstrated company-level ownership.

### 44.3 Four viable leadership structures

| Structure | When it works | Main risk |
|---|---|---|
| Technical founder remains CEO; commercial co-founder becomes President or Chief Business Officer | Technical founder wants company leadership and can fundraise, while the commercial founder owns GTM and operations | Ambiguous final authority if decision rights are not explicit |
| Commercial co-founder becomes CEO; technical founder becomes CTO or Chief Product/Technology Officer | Technical founder wants to build product and the candidate has exceptional company-building capacity | Technical thesis may be diluted if CEO lacks product depth |
| Existing founders remain the founding team; hire a founding GTM executive | Founders can lead fundraising and strategy but need commercial execution | Executive may lack founder-level commitment or authority |
| Run without a dedicated commercial leader through design-partner phase | Existing founders can sell the first ten customers and want more evidence before recruiting | Market learning and fundraising preparation may move too slowly |

The company does not need to decide based on convention. It needs to decide based on the work each founder wants to perform repeatedly.

### 44.4 The CEO question

The CEO's core job at this stage is to maintain company coherence. That means choosing the market, allocating scarce attention, recruiting, financing the company, resolving founder disagreements, and ensuring that customers receive value.

The technical founder should remain or become CEO if that work is energizing and if the founder is willing to become excellent at it. Technical depth does not disqualify someone from CEO leadership. Refusing market and organizational work does.

A commercial co-founder should become CEO when the person has the strongest combined ability to:

- Hold the product and market thesis.
- Recruit exceptional people.
- Sell before the sales process exists.
- Raise capital without distorting the company.
- Make hard priority decisions.
- Represent the company with credibility to technical and nontechnical audiences.
- Preserve trust among the founders under pressure.

Do not decide the CEO role as an equity prize or status concession. Decide it as an operating responsibility.

### 44.5 Recommended decision

The recommended path is:

1. The existing founders begin customer discovery and paid design-partner work immediately.
2. They publish a precise co-founder brief rather than a generic search.
3. Promising candidates complete a six-week working trial.
4. The team makes the co-founder and CEO decisions after observing real customer, product, and conflict behavior.
5. A candidate who is strong but not yet founder-level can join as a founding executive with milestone-based equity.

This sequence preserves speed while protecting the cap table and founding relationship.

## 45. Role definition for a commercial co-founder

A useful role description begins with outcomes, not traits.

### 45.1 Mission

> **Turn an agent-native application platform with strong technology and design into a focused company with paid customers, repeatable distribution, a credible seed narrative, and an operating system capable of scaling.**

### 45.2 Twelve-month outcomes

The commercial co-founder should be accountable for producing, with the other founders:

1. A clearly defined beachhead and category narrative.
2. Ten to twenty paid design partners or equivalent recurring customers.
3. A repeatable studio, agency, or vertical-pack acquisition motion.
4. Pricing evidence across builder, runtime, and premium-module revenue.
5. Customer case studies showing time-to-value and production durability.
6. A qualified pipeline that does not depend entirely on personal friends.
7. A completed seed financing on terms appropriate to the evidence.
8. The first commercial and customer-engineering hires.
9. A company operating cadence, budget, and board reporting system.
10. A founder relationship that becomes stronger after disagreements and missed targets.

### 45.3 Weekly responsibilities

The role initially includes direct work that later becomes separate functions:

- Conduct customer discovery and sales calls.
- Build and advance the design-partner pipeline.
- Write proposals and negotiate pilot agreements.
- Review application delivery and customer outcomes.
- Translate customer patterns into product priorities with the technical and design founders.
- Test packaging, pricing, and module economics.
- Build channel relationships with studios and agencies.
- Maintain the investor narrative and fundraising data room.
- Recruit early employees and advisors.
- Own budget, runway, and basic business operations.
- Lead the weekly company review.

A candidate who only wants strategy, partnerships, or fundraising is not suited to the stage.

### 45.4 Ideal experience profile

No candidate will match every line. The strongest profiles include some combination of:

- Founder or first ten employee at a developer-tools, infrastructure, vertical SaaS, automation, or application-platform company.
- Successful founder-led sales to small businesses, agencies, studios, or enterprise teams.
- Experience packaging technical infrastructure into a simple commercial product.
- Evidence of building a category narrative rather than merely executing an established playbook.
- Ability to negotiate partnerships without substituting partnerships for customer acquisition.
- Product judgment sufficient to distinguish a repeated pattern from a bespoke request.
- Fundraising experience or the ability to learn it rapidly.
- Comfort with open source, developer communities, and technical buyers.
- Respect for design as a product capability.
- Experience operating with very little staff and incomplete data.

The candidate does not need to be a former venture-backed CEO. A high-agency product, GTM, or operations leader who has repeatedly created new motions can be stronger than a polished executive from a mature company.

### 45.5 Required product understanding

By the end of a trial, the candidate should be able to explain, without scripts:

- Why high-level modules make agents more reliable.
- Why this is not simply Replit, Lovable, or v0 on Goja.
- How the runtime and release model reduce operational risk.
- Why the first customer segment is narrower than the product vision.
- How builder, runtime, module, and marketplace revenue differ.
- Why design is part of the platform architecture.
- Which security claims the system can and cannot make today.
- What proof is still missing.

Commercial clarity requires technical honesty.

### 45.6 Authority and decision rights

The role should come with actual authority. A possible initial division is:

| Decision area | Primary owner | Required consultation |
|---|---|---|
| Company strategy and financing | CEO | All founders |
| Runtime architecture and security | Technical founder | CEO and design founder for product impact |
| Product experience and design system | Design founder | Technical founder and CEO |
| Beachhead, pricing, and GTM | Commercial founder | All founders |
| Customer commitments | Commercial founder | Technical and design founders before roadmap commitments |
| Hiring | Functional owner | CEO and at least one other founder |
| Budget | CEO | Board and functional owners |
| Major module roadmap | Product trio | Customer evidence and technical feasibility |

The point is not rigid bureaucracy. It is to prevent every disagreement from becoming a referendum on the founding relationship.

## 46. Candidate scorecard

Founders often choose co-founders through chemistry and narrative. Chemistry matters, but it is difficult to distinguish early rapport from durable compatibility. A scorecard forces the team to collect evidence.

### 46.1 Weighted scorecard

| Dimension | Weight | Evidence to collect |
|---|---:|---|
| Founder motivation and risk tolerance | 15% | Full-time commitment, financial expectations, persistence under ambiguity |
| Customer discovery | 15% | Quality of interviews, synthesis, ability to find non-obvious pain |
| Founder-led sales | 15% | Ability to create urgency, ask for money, negotiate, and close |
| Strategic judgment | 12% | Beachhead selection, prioritization, rejection of distractions |
| Product and technical fluency | 10% | Accurate explanation of architecture and customer consequences |
| Narrative and communication | 10% | Customer pitch, investor pitch, writing, listening, precision |
| Operating ability | 8% | Cadence, follow-through, financial discipline, recruiting |
| Fundraising and network creation | 5% | Investor understanding, warm path creation, reference quality |
| Working style and conflict behavior | 10% | Candor, accountability, speed, ability to disagree productively |

A candidate does not pass because the weighted score exceeds a number. The score identifies where enthusiasm lacks evidence.

### 46.2 Work samples

Use real work rather than hypothetical interviews:

1. **Customer interview.** The candidate leads a discovery call with a potential design partner, then writes a synthesis separating facts, interpretations, and product implications.
2. **Paid pilot proposal.** The candidate produces a one-page proposal with scope, price, timeline, success criteria, and exclusions.
3. **Positioning exercise.** The candidate explains the product to a studio owner, a seed investor, and a small-business operator without using the same pitch.
4. **Pricing review.** The candidate critiques the proposed pricing model and designs two tests.
5. **Founder disagreement.** The team debates a real request that would create short-term revenue but distort the platform.
6. **Investor meeting.** The candidate participates in or simulates a partner meeting and handles objections.
7. **Operating review.** The candidate runs a weekly meeting using actual pipeline, product, and cash data.

### 46.3 Reference questions

References should answer behavioral questions:

- What did the candidate personally create from nothing?
- Did the candidate sell, or manage people who sold?
- How did the person behave when a major plan failed?
- Did colleagues trust the candidate with bad news?
- Which kinds of people performed poorly under the candidate?
- Did the candidate make product promises that engineering could not keep?
- How did the person handle credit and blame?
- Would the reference found another company with this person?
- What should the existing founders know before sharing control?

Seek references supplied by the candidate and back-channel references where appropriate and ethical.

### 46.4 Red flags

Treat these as evidence, not personality quirks:

- Uses “we” for achievements but cannot describe personal contribution.
- Talks primarily about brand, partnerships, or investors rather than customers.
- Wants to delegate outbound sales before closing it personally.
- Cannot state what should not be built.
- Treats technical complexity as something engineering should hide from leadership.
- Confuses confidence with certainty.
- Produces many introductions but few advanced commitments.
- Avoids written commitments and measurable outcomes.
- Changes the company story to match every audience.
- Negotiates founder economics before doing meaningful work together.
- Is dismissive of support, implementation, or operational details.
- Blames prior teams without describing personal mistakes.

## 47. Search channels

A co-founder search should be run like a high-priority company process. Waiting for a perfect introduction creates no learning and gives the search no deadline.

### 47.1 Start with the co-founder brief

Publish or privately circulate a concise brief containing:

- The company thesis.
- What has already been built.
- The design proof and demonstrations.
- The commercial hypothesis and initial wedge.
- The exact role and twelve-month outcomes.
- The current founder roles.
- What remains uncertain.
- Expected commitment, location, and timing.
- The working-trial process.
- The founder's honest reason for seeking a partner.

The brief should attract people who want the actual work, not merely the category.

### 47.2 Warm network

Ask for introductions from:

- Founders of developer-tool, infrastructure, no-code, vertical SaaS, and agency-platform companies.
- Seed investors and angel investors who know zero-to-one operators.
- Customers and potential design partners.
- Senior product, partnerships, and GTM leaders from adjacent platforms.
- Designers and engineering leaders who have worked with unusually commercial operators.
- Former colleagues, open-source collaborators, and founder communities.

The request should describe the person, not ask whether someone knows “a business co-founder.”

### 47.3 Structured founder communities

Use founder communities as talent-density tools rather than endorsements. YC operates a dedicated co-founder matching platform, and its published examples include teams that worked on trial projects before committing.[^S22] South Park Commons supports founders from exploration through funded company creation, with current funding described as ranging from $1 million to $10 million.[^S20] Entrepreneurs First explicitly accepts individuals with an early idea or a co-founder under test and runs a matching process.[^S21]

Other relevant sources include:

- Founder residencies and accelerators.
- Developer-tools and AI-infrastructure communities.
- Design-technology communities.
- Industry-specific operator networks in booking, commerce, logistics, and SMB software.
- Local founder groups where repeated in-person work is possible.

Do not join a program solely to outsource the search. Join when the community, location, capital, and schedule improve the company's odds.

### 47.4 Targeted outbound

Build a list of fifty to one hundred people with evidence of relevant behavior. Good target profiles include:

- Former founders whose companies did not work but who demonstrated strong sales and company judgment.
- Early GTM or product leaders at Retool, Airtable, Replit, Lovable, Vercel, Supabase, Shopify, Wix, automation platforms, or vertical SaaS companies.
- Agency or studio founders who productized custom software delivery.
- Operators who launched a new business line inside a platform company.
- Investors or community leaders who want to return to operating.

A short outbound message should state why this particular person fits the problem. Generic mass outreach is weak evidence of how the candidate search will be run.

### 47.5 Candidate funnel

Track the search:

| Stage | Target |
|---|---:|
| Identified profiles | 100 |
| Warm or tailored outreach | 50 |
| First conversations | 20 |
| Deep founder conversations | 8 |
| Working sessions | 4 |
| Six-week trials | 1–2 |
| Founder decision | 0 or 1 |

“No hire” is a valid outcome. A forced co-founder is more expensive than a longer search.

## 48. The working-trial process

The trial should expose the real work of founding the company. Social dinners and pitch conversations reveal compatibility, but they do not reveal execution under pressure.

### 48.1 Trial structure

A six-week trial can be run while legal founder status remains undecided.

#### Week 0: explicit expectations

Agree in writing on:

- Time commitment.
- Confidentiality and intellectual-property assignment for trial work.
- Whether the trial is paid consulting work.
- Which decisions remain with the existing founders.
- Expected artifacts and customer access.
- Evaluation criteria.
- What happens if either side stops early.

#### Week 1: understand and restate the thesis

The candidate reviews the product, technical companion document, demos, market analysis, and current pipeline. The output is a written company thesis in the candidate's own words, including the strongest objection to the business.

#### Week 2: customer discovery

The candidate sources or joins at least five interviews. The output is a problem map, buyer map, repeated-language analysis, and recommendation about the initial wedge.

#### Week 3: commercial offer

The candidate creates the design-partner offer, pricing, scope, agreement outline, and outreach sequence. The team sends it to real prospects.

#### Week 4: sell and negotiate

The candidate leads sales conversations and asks for a paid commitment. The output is not necessarily a closed contract; it is evidence of how the person creates urgency, handles objections, and updates strategy.

#### Week 5: investor and partner narrative

The candidate revises the one-pager and pitch, runs several practice meetings, and builds a targeted investor or partner map.

#### Week 6: operating review and founder decision

The candidate runs a company review covering product, customers, pipeline, cash, risks, and next-month priorities. The founders then discuss role, authority, economics, and unresolved concerns.

### 48.2 Trial scorecard

At the end, answer:

- Did the candidate increase the rate of customer learning?
- Did the candidate ask for money directly?
- Did prospects understand the product more clearly?
- Did the candidate protect the long-term architecture from one-off demands?
- Did written work become more precise?
- Did the candidate reliably complete commitments?
- Did disagreement improve decisions?
- Did the existing founders want to share difficult information with this person?
- Did everyone become more ambitious and more realistic?
- Would the team still choose this person after a failed fundraise or lost customer?

### 48.3 Trial compensation

There are three reasonable structures:

1. **Unpaid mutual exploration** for a limited number of hours, before the candidate performs material company work.
2. **Paid consulting agreement** for a part-time trial, with all work assigned to the company.
3. **Short employment arrangement** when the candidate works full-time and local law requires employment treatment.

Use counsel. Do not rely on informal promises about future equity in exchange for substantial work.

### 48.4 Why the trial matters

Carta reports that two-founder teams remain the most common among venture-funded startups, and YC matching data shows that technical and nontechnical pairings are common.[^S16][^S15] Those population patterns do not reduce the importance of individual compatibility. Founder failure is often a governance and trust failure. A trial is a low-cost way to observe the future company before making it irreversible.

## 49. Equity, vesting, and governance

Founder equity should reflect future company-building risk and commitment, while acknowledging the substantial technology and design value already created. It should not be calculated as an hourly invoice for past work or divided automatically by title.

### 49.1 Principles

1. **Equity pays for the future.** Past contributions matter because they de-risk the company, but most founder equity compensates years of future work and opportunity cost.
2. **Vesting protects every founder.** A founder who leaves early should not retain the same ownership as founders who continue building.
3. **Authority and equity are related but not identical.** The CEO can have final operating authority without owning a majority.
4. **Near-equal splits can be rational.** Carta reported that 44.6% of two-founder teams formed in 2025 divided equity equally, and the median two-founder split was 51–49.[^S23] That is evidence of a trend, not a rule for this company.
5. **The process matters.** A transparent model and explicit assumptions are more important than pretending there is one objectively correct percentage.

### 49.2 Contribution model

Evaluate each founder across:

- Pre-existing intellectual property and product proof.
- Full-time start date.
- Cash invested or salary deferred.
- Future role breadth and company-level risk.
- Replacement difficulty.
- Customer, distribution, or fundraising leverage.
- Expected duration of contribution.
- Personal guarantees or unusual liabilities.

Do not assign precise percentage points to each category as if the result were scientific. Use the model to reveal disagreement.

### 49.3 Illustrative structures

These are discussion examples, not recommendations:

| Situation | Illustrative founder allocation before employee pool and financing |
|---|---|
| Technical and design founders have both worked full-time for a substantial period; commercial founder joins before revenue and takes CEO-level risk | 38% technical / 32% design / 30% commercial |
| Technical founder created most existing IP; design founder recently joined; commercial founder joins after first customers | 48% technical / 27% design / 25% commercial |
| All three have worked together through a meaningful trial and commit at the same early stage | Approximately one-third each, adjusted for prior IP and cash |
| Candidate joins after seed financing with market salary and narrower GTM role | Founding-executive option grant rather than co-founder common stock |

The correct number depends on facts not provided here. The important distinction is whether the new person is accepting founder-level uncertainty before the commercial proof exists.

### 49.4 Vesting

A common founder structure is four-year vesting with a one-year cliff, usually implemented through company repurchase rights over unvested founder stock. For founders who have already spent material time building the company, the board can recognize a portion of elapsed service while preserving meaningful future vesting.

Questions to decide with counsel:

- Vesting commencement date for each founder.
- Credit for prior full-time service.
- Treatment of existing intellectual property.
- Single-trigger or double-trigger acceleration, if any.
- Repurchase price for unvested shares.
- Treatment of voluntary departure, termination, disability, and death.
- Whether founders receive restricted stock or options based on tax and company timing.
- Timely 83(b) elections where applicable.

Do not promise acceleration casually. Broad single-trigger acceleration can make an acquisition harder and create divergent incentives.

### 49.5 Governance

The founders should sign a written founder agreement or equivalent set of corporate documents covering:

- Roles and decision rights.
- CEO authority.
- Board composition.
- Reserved decisions requiring board or founder approval.
- Equity and vesting.
- Intellectual-property assignment.
- Confidentiality.
- Founder departure.
- Outside activities.
- Expense and salary policy.
- Conflict resolution.
- Sale of the company.
- Deadlock process.

A simple initial board might contain the CEO and one other founder, expanding when an institutional financing occurs. Another structure gives all three founders board seats before financing. The choice should account for local law, investor expectations, and the need to avoid operational deadlock.

### 49.6 Reserved decisions

Examples that should not be made unilaterally by one functional founder:

- Issuing equity or debt.
- Selling the company or material intellectual property.
- Changing founder compensation materially.
- Hiring or firing a founder-level executive.
- Entering an exclusive strategic partnership.
- Changing the primary business or abandoning the platform thesis.
- Taking on material debt or long-term obligations.
- Committing to a customer requirement that changes the security model.

### 49.7 Founder conflict protocol

Write the protocol before conflict:

1. The decision owner writes the decision, alternatives, evidence, and deadline.
2. Each founder states objections and the evidence that would change their view.
3. The team distinguishes reversible from irreversible decisions.
4. Reversible decisions go to the functional owner after consultation.
5. Irreversible company decisions go to the CEO or board under agreed authority.
6. Relationship conflicts are discussed separately from the product decision.
7. Persistent deadlock can use a mutually selected advisor or board member, but not as a substitute for founder responsibility.

The founders do not need to agree on every decision. They need to trust the decision system.


# Part VIII. Execution Plan

## 50. The first ninety days

The first ninety days should convert private conviction into external proof. The company already has substantial technical proof. The operating risk is continuing to improve the substrate without learning which customers will pay, which modules create leverage, and which product promise survives contact with real use.

The quarter should have one governing objective:

> **Prove that the team can repeatedly create and operate professional applications for a defined customer type, with a delivery model that becomes more productized each time.**

![The first ninety days](./_founder_assets/ninety_day_proof_loop.png)

### 50.1 Day 0 scorecard

Before starting, record the baseline:

- Number of external customer interviews completed.
- Number of paid customers.
- Number of externally used production applications.
- Median time from application request to live preview.
- Median time from approved preview to production release.
- Percentage of application code using existing modules rather than custom host work.
- Number of reusable modules and vertical recipes.
- Current monthly infrastructure cost.
- Current cash and runway.
- Current co-founder candidates and investor relationships.

The quarter is an experiment only if the starting point and success conditions are explicit.

### 50.2 Days 1–30: focus and recruitment of evidence

The first month is for choosing the commercial problem and recruiting people who have it.

#### Customer work

- Conduct twenty-five to thirty interviews across no more than two adjacent customer profiles.
- Prioritize studios, agencies, automation consultants, and small-business operators with recurring software needs.
- Ask for current workflow artifacts: spreadsheets, forms, screenshots, email templates, reports, and existing software bills.
- Identify who owns the problem, who uses the system, who approves spending, and what event creates urgency.
- Select one primary beachhead and one secondary learning segment.

#### Product work

- Stabilize the minimum production path required for external design partners.
- Define the first commercial module catalog and exact support status.
- Create three canonical application demonstrations that use the same runtime but express different customer value.
- Build the authority-diff and release-review experience required for founder and customer trust.
- Instrument generation cost, runtime cost, module usage, errors, rollback, and support time.

#### Commercial work

- Publish the design-partner offer.
- Build a list of one hundred prospects and fifty studio or agency partners.
- Begin the commercial co-founder search using the brief and scorecard.
- Draft pilot agreements, terms, data-processing boundaries, and a security FAQ.
- Test three price anchors in customer conversations.

#### Month-one exit criteria

- One beachhead chosen.
- Five prospects have agreed to a scoped design-partner discussion.
- At least two prospects have accepted a paid proposal or entered procurement.
- The team can demonstrate creation, review, deployment, change, and rollback in one coherent session.
- The first module price and cost model exists.

### 50.3 Days 31–60: paid application delivery

The second month turns interviews into live systems.

#### Deliver three paid pilots

Choose pilots that share modules but differ enough to test breadth. A useful cohort might include:

1. A service booking and customer portal application.
2. A lightweight CRM, quoting, and follow-up application.
3. A product catalog, search, ordering, or inventory application.

Each pilot needs:

- A named business owner.
- A real workflow with current pain.
- A production user group.
- A payment, even if discounted.
- A measurable before-and-after outcome.
- A defined support and change process.
- Permission to use anonymized results in fundraising or sales, where possible.

#### Measure semantic leverage

For every application, record:

- Total application source lines and generated artifacts.
- Number of module calls and module versions.
- Amount of custom Go or infrastructure work required.
- Time spent by technical, design, and commercial founders.
- Number of generated iterations before acceptance.
- Bugs by layer: application logic, module, runtime, renderer, deployment, integration.
- Time to fix and whether the fix benefited other applications.

The key question is not whether the team can deliver. It is whether the second application is materially easier than the first.

#### Productize repeated work

At the end of each week, classify work into:

- Customer-specific application behavior.
- Reusable module capability.
- Reusable UI recipe.
- Reusable vertical configuration.
- Platform defect.
- Service process that should become product.

Anything repeated twice should be reviewed for productization. Anything repeated three times without productization is an operating warning.

#### Month-two exit criteria

- Three paid pilots in production or an accepted production trial.
- At least two applications share a meaningful module combination.
- The team has a documented deployment, support, and rollback process.
- A customer has requested and received a post-launch change.
- At least one module improvement has benefited multiple applications.
- A candidate commercial co-founder has begun a working trial, or the team has concluded that a founding executive search is more appropriate.

### 50.4 Days 61–90: repeatability and financing readiness

The third month tests whether the company has a repeatable story rather than three consulting projects.

#### Expand the cohort

- Add five to seven design partners or studio projects.
- Require new work to fit the chosen module and vertical roadmap unless the strategic learning is exceptional.
- Convert at least some pilots from project fees to recurring platform contracts.
- Test expansion: a second application, additional users, a premium module, or another environment.

#### Produce commercial evidence

Create:

- Two detailed case studies.
- A before-and-after time and cost analysis.
- A module attach-rate report.
- A customer retention and usage dashboard.
- A pricing summary showing accepted, rejected, and negotiated offers.
- A product roadmap justified by repeated customer evidence.
- A recorded five-minute demo and a live investor demo.

#### Decide financing timing

Begin a formal seed process only if the evidence meets a defined threshold. A reasonable threshold is:

- Five or more paid external customers.
- Three or more production applications used weekly.
- At least one repeated vertical or channel pattern.
- Clear gross-margin path for the first modules.
- Customer references willing to speak.
- A credible eighteen- to twenty-four-month plan.

If the evidence is weaker, raise a smaller formation round or continue design-partner revenue rather than manufacturing a seed narrative.

#### Day-ninety target dashboard

| Metric | Target range |
|---|---:|
| Serious customer interviews | 40–60 |
| Paid design partners | 5–10 |
| Live production applications | 5–10 |
| Applications per repeat customer or studio | 1.2–2.0 |
| Time to first useful preview | Under one business day for scoped patterns |
| Time to production | Under one week for standard packs |
| Existing-module coverage | More than 70% of operational capability |
| Recurring monthly revenue | Evidence-dependent; target $10K–$30K MRR or contracted equivalent |
| Gross-margin model | Positive contribution margin on standard application profiles |
| Customer references | At least three |
| Commercial co-founder decision | Made, or a defined alternative plan exists |

The revenue target is not a universal seed requirement. Its purpose is to force the team to charge and learn.

### 50.5 Weekly company cadence

A disciplined week can follow this rhythm:

| Day | Primary work |
|---|---|
| Monday | Company metrics, customer pipeline, product priorities, cash, and risk review |
| Tuesday | Customer discovery and sales; application delivery |
| Wednesday | Product and module development; design review |
| Thursday | Customer deployment, onboarding, and partner work |
| Friday | Retrospective, productization review, documentation, demo and narrative update |

Protect customer time. A platform company can spend every hour discussing architecture and still learn nothing about its business.

## 51. Twenty-four-month roadmap

A useful roadmap describes proof and capability, not a list of features with artificial dates. Each phase should make the next phase possible.

### 51.1 Phase 1: design-partner platform, months 0–3

**Company proof:** Customers pay for applications produced on the platform.

**Product:**

- Secure hosted JavaScript runtime with explicit module profiles.
- Professional HTTP application framework.
- Versioned releases, preview, activation, rollback, logs, and audit.
- Initial Widget DSL renderer and static frontend asset path.
- Core modules: database, identity/session integration, forms, notifications, files, and basic payments.
- First premium modules: booking or product search, selected by customer demand.
- Manual or founder-assisted application creation workflow.

**Commercial:**

- Paid design-partner program.
- Studio and agency interviews.
- First pricing and support contracts.
- Seed narrative based on external applications.

### 51.2 Phase 2: repeatable solution packs, months 4–6

**Company proof:** Multiple customers use the same module and recipe combinations.

**Product:**

- Project and environment management.
- Structured application manifest and module lock.
- Reusable vertical packs for two selected workflows.
- Resource provisioning and binding.
- Usage ledger and billing integration.
- Safer secrets and outbound-network policy.
- Customer-visible release history and change review.
- First application export and data export.

**Commercial:**

- Ten to twenty paid customers or equivalent studio volume.
- Standard pilot and recurring contracts.
- First channel partner program.
- Seed financing if evidence supports it.

### 51.3 Phase 3: studio product, months 7–12

**Company proof:** A studio or internal builder can create applications without continuous founder intervention.

**Product:**

- Multi-project studio workspace.
- Agent APIs and MCP tools for create, inspect, validate, preview, release, and rollback.
- Brand and design-system controls.
- Client handoff, permissions, and billing ownership.
- Reusable data migration and import tools.
- Module documentation generated for humans and agents.
- Better test generation and application evaluation.
- Production worker isolation, quotas, and cost controls.
- Module-level operational dashboards.

**Commercial:**

- Certified or selected studio partners.
- Application and module attach-rate expansion.
- Initial self-service waitlist and guided onboarding.
- Customer success playbooks and partner economics.

### 51.4 Phase 4: self-service application cloud, months 13–18

**Company proof:** New customers reach production value without founder-led implementation.

**Product:**

- Self-service account, project, and application creation.
- Guided application planning and authority review.
- Template and recipe discovery.
- Usage budgets and spend controls.
- Managed custom domains, backups, and recovery.
- Broader premium module catalog.
- In-app user management and external OIDC options.
- Application analytics and product telemetry.
- Public fork/share flows for personal and community applications.

**Commercial:**

- Product-led acquisition experiments.
- Builder subscriptions and standardized runtime plans.
- Free personal/shared app tier with controlled cost.
- Expansion from studios into direct business teams.

### 51.5 Phase 5: marketplace and enterprise controls, months 19–24

**Company proof:** Third parties create economic value on the platform, or enterprise customers operate meaningful application portfolios.

**Product:**

- Third-party module SDK, review, signing, billing, and lifecycle.
- Template and design-recipe marketplace.
- Enterprise SSO, SCIM, policy, approvals, audit retention, and private networking.
- Private modules and customer-specific providers.
- Dedicated worker pools or private deployment profiles.
- Regional placement and data-residency controls.
- Organization-wide application inventory and risk view.
- Compatibility and automated module-upgrade tooling.

**Commercial:**

- Marketplace take rate.
- Enterprise contracts.
- Private-cloud or dedicated deployment offerings.
- Partner-led vertical expansion.

### 51.6 Roadmap gates

Do not advance because time passed. Advance when the previous proof exists.

| Gate | Evidence required |
|---|---|
| Design partners → solution packs | Repeated module combinations and paid recurring use |
| Solution packs → studio product | At least one partner delivers without founder-only knowledge |
| Studio product → self-service | Onboarding and support are sufficiently standardized |
| Self-service → marketplace | Module boundary, billing, review, and support are stable |
| Single-node → distributed execution | Measured capacity, reliability requirements, and customer demand justify it |
| General platform → enterprise | Security, identity, audit, and support contracts can be met truthfully |

## 52. Hiring plan

The company should hire against bottlenecks revealed by proof. Hiring to resemble a complete startup before the market is understood increases burn without increasing learning.

### 52.1 Founder stage: three to five people

Before or immediately after a seed round, the core team may be:

- Technical founder.
- Design founder.
- Commercial co-founder or founding GTM leader.
- One senior product/platform engineer.
- One customer or product engineer, potentially contract-to-hire.

The first engineer should increase the rate at which modules and production reliability improve. The second technical hire should reduce the founders' direct involvement in every application delivery.

### 52.2 First eight hires

A plausible sequence is:

| Priority | Role | Why now |
|---:|---|---|
| 1 | Senior platform/runtime engineer | Close isolation, reliability, module SDK, and operational gaps |
| 2 | Product engineer | Build builder workspace, review experience, and customer-facing application surfaces |
| 3 | Customer engineer / solutions architect | Deliver pilots, translate patterns into reusable modules, support studios |
| 4 | Developer experience engineer | Agent APIs, module docs, SDKs, examples, source graph, diagnostics |
| 5 | Product designer or design engineer | Extend the design founder's system into scalable tooling and recipes |
| 6 | Infrastructure/security engineer | Worker plane, observability, egress, secrets, incident response |
| 7 | Founding account executive or partnerships lead | Scale a sales motion already closed by founders |
| 8 | Customer success / partner operations | Support growing app portfolios and studio partners |

The order changes with evidence. A flood of studio interest may move customer engineering earlier. Heavy enterprise demand may move security and infrastructure earlier.

### 52.3 Roles not to hire first

Avoid early hiring of:

- A large general sales team before founders can repeatably close.
- A chief marketing officer before positioning and audience are proven.
- A large support team before the productization problem is addressed.
- A machine-learning research team unless proprietary model work is essential.
- Multiple infrastructure specialists before measured load requires them.
- A marketplace team before the first-party module contract is stable.
- A full executive layer around three founders.

### 52.4 Hiring profile

Early employees should be comfortable crossing boundaries. Useful signals include:

- Has shipped products with a small team.
- Can read customer evidence and change technical priorities.
- Writes clearly.
- Understands security boundaries without becoming paralyzed by them.
- Builds abstractions after observing repetition, not before.
- Likes agents as users and can design APIs for them.
- Can operate both the platform and applications built on it.
- Respects design quality and operational reliability equally.

### 52.5 Seed headcount and burn

An institutional seed plan of $3.5 million should not assume immediate hiring to twenty people. A disciplined plan might reach eight to twelve full-time employees over eighteen months, depending on revenue and geography.

Illustrative fully loaded annual costs:

| Role group | Approximate annual cash cost per person |
|---|---:|
| Senior engineering in high-cost U.S. market | $220K–$320K |
| Senior engineering in distributed European market | $140K–$230K |
| Design/product | $150K–$250K |
| Customer engineering | $140K–$230K |
| Early GTM | $160K–$280K including variable compensation |
| Operations/finance support | $80K–$160K or fractional |

These are planning ranges, not compensation recommendations. Benefits, payroll taxes, recruiting, equipment, travel, legal, and contractor costs must be included.

### 52.6 Fractional and contract support

Use specialists for non-core work:

- Startup counsel.
- Finance and bookkeeping.
- Security assessment and penetration testing.
- Compliance preparation.
- Recruiting support for a small number of critical roles.
- Brand production under the design founder's direction.
- Customer-specific data migration where the work does not define the platform.

Do not outsource the product thesis, module architecture, customer discovery, or core application experience.

## 53. Experiment backlog

A startup advances by invalidating uncertainty. The experiment backlog should rank questions by how much company value depends on the answer.

### 53.1 Market and buyer experiments

| Hypothesis | Test | Success evidence | Decision enabled |
|---|---|---|---|
| Studios have repeated demand for custom operational apps | Interview 20 studios and offer a paid pilot | Five serious pilots and repeated workflow categories | Commit to studio wedge |
| Small service businesses will pay recurring platform fees | Sell booking/CRM pack directly to 15 operators | Three paid recurring contracts at target price | Direct vertical motion |
| Internal teams value governance over code ownership | Demo release/authority controls to enterprise innovation teams | Two design-partner commitments with security stakeholders | Enterprise internal-app path |
| Personal apps can drive viral acquisition | Launch five forkable personal/community apps | Meaningful fork-to-builder conversion and retained use | Invest in free viral surface |
| Buyers value custom software over configurable SaaS | Compare proposal language and close rates | Higher willingness to pay for custom workflow ownership | Positioning choice |

### 53.2 Product and agent experiments

| Hypothesis | Test | Success evidence |
|---|---|---|
| High-level modules materially improve agent reliability | Build the same app using modules and conventional stack primitives | Higher test pass rate, fewer iterations, smaller source, lower support time |
| A module catalog can guide planning | Give an agent a constrained catalog and ambiguous app request | Agent selects compatible modules and produces valid plan without manual repair |
| Authority diffs increase trust | Show users a release with and without permission diff | Users identify risky changes faster and approve with greater confidence |
| Widget recipes improve quality without reducing variety | Generate ten apps from shared recipes | Consistent usability with differentiated brand and layout |
| External agents can operate the platform effectively | Expose project and release MCP tools to two coding agents | Complete create-to-deploy flow with bounded errors and audit |
| Source export reduces lock-in concern | Offer export during sales | Fewer procurement objections without meaningful churn increase |

### 53.3 Pricing experiments

| Question | Test |
|---|---|
| Builder subscription or per-app fee first? | Present three packages with identical total expected spend but different framing |
| How much value belongs to premium modules? | Quote search, booking, and payments separately versus bundled |
| Are studios sensitive to seats or app portfolios? | Compare per-builder and per-active-client-app packaging |
| Can design-partner services fund learning? | Offer fixed-price implementation plus recurring platform fee |
| Do customers accept usage overages? | Provide included quota, alerts, and transparent overage price in pilots |
| Is a transaction fee acceptable? | Test only where the platform creates transaction value, such as booking or commerce |

### 53.4 Channel experiments

- Give three studios the same vertical pack and compare delivery time.
- Offer white-label client handoff and observe whether it affects close rate.
- Pay a referral fee versus revenue share and compare partner motivation.
- Let a partner keep implementation revenue while the platform retains runtime revenue.
- Run a certification workshop and measure whether trained partners ship independently.
- Compare partner-sourced customers with direct customers on support burden and retention.

### 53.5 Module experiments

For each candidate module, test four questions:

1. Does it recur across applications?
2. Does it hide difficult operational semantics?
3. Will customers pay for it separately or retain because of it?
4. Can the platform support it with acceptable margins and risk?

A module that is easy to implement, rarely reused, and hard to price is a library feature, not a premium business line.

### 53.6 Experiment review

Every experiment should have:

- A named owner.
- A decision deadline.
- A maximum time or cash budget.
- A prewritten success and failure condition.
- Collected raw evidence.
- A decision recorded after completion.

Do not let experiments become permanent pilots with no decision.

## 54. Risk register

The company is ambitious because it combines an application platform, runtime, module ecosystem, agent experience, design system, and marketplace. The risks should be stated directly.

### 54.1 Strategic risks

| Risk | Probability | Impact | Leading indicator | Mitigation |
|---|---|---|---|---|
| General app builders add similar high-level modules | High | High | Competitors ship deeper built-in business primitives | Win on coherent module contract, operational depth, ecosystem, and focused GTM |
| The category is too broad to explain | High | High | Prospects understand demos but cannot describe the company | Narrow wedge, repeated language testing, one category claim |
| Studios are a service-heavy dead end | Medium | High | Every project requires unique platform engineering | Productization metrics, fixed packs, partner self-sufficiency gates |
| Customers prefer existing SaaS to custom apps | Medium | High | Low urgency or unwillingness to maintain a custom workflow | Focus on workflows with painful mismatch and high change frequency |
| Platform value is captured by model or cloud providers | Medium | High | Underlying providers bundle creation and modules at low cost | Own application semantics, multi-provider module layer, data, and distribution |
| Personal apps distract from revenue | High | Medium | High usage with low retention and support-heavy free tier | Treat personal apps as bounded acquisition surface until economics prove otherwise |

### 54.2 Technical and security risks

| Risk | Probability | Impact | Leading indicator | Mitigation |
|---|---|---|---|---|
| Tenant code escapes or abuses the host | Low–medium | Catastrophic | Unexpected host access, sandbox anomalies | OS isolation, no ambient authority, egress control, worker disposal, external review |
| JavaScript timeout does not stop native work | Medium | High | Requests return while workers remain busy | Interrupt plus process kill, capability cancellation, poisoned-worker disposal |
| Module capability policy differs from runtime reality | Medium | Catastrophic | Validation says denied while module remains available | Signed release lock, deny-by-default runtime construction, conformance tests |
| Premium module creates systemic incident | Medium | High | Correlated failures across many applications | Version pinning, canaries, rollback, circuit breakers, module-specific SLOs |
| Generated migration destroys customer data | Medium | Catastrophic | Destructive schema changes without backup or compatibility | Native migration planner, backups, approvals, expand/contract policy |
| Secrets or personal data appear in prompts/logs | Medium | High | Raw tokens or customer records in traces | Opaque handles, redaction, scoped evidence, logging limits, customer controls |
| Runtime cost becomes unpredictable | Medium | High | A few apps dominate CPU, model, or integration spend | Per-app budgets, metering, alerts, quotas, isolation, pricing alignment |
| Goja performance limits application scope | Medium | Medium | CPU-bound scripts or queue saturation | Keep heavy work in native modules, isolate workers, profile, define supported workloads |

### 54.3 Commercial risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Customers like demos but do not pay | High until disproven | Catastrophic | Charge for pilots immediately and measure decision process |
| Pricing is too complex | Medium | High | Separate creation, runtime, and modules internally but present simple packages |
| Premium modules create pass-through margin pressure | Medium | Medium | Negotiate provider economics, aggregate usage, build high-margin modules selectively |
| Enterprise sales cycles consume the team | Medium | High | Require paid scoped design partnership and avoid roadmap promises without sponsor |
| Agency partners own the customer relationship | Medium | Medium | Direct platform contract, client-visible value, export and support boundaries |
| Services revenue hides weak software economics | High | High | Track product versus service margin, reuse, delivery hours, recurring conversion |
| Marketplace launches before supply or demand | Medium | Medium | Keep first-party catalog until repeated external provider demand exists |

### 54.4 Founder and organization risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Commercial co-founder is selected too quickly | Medium | Catastrophic | Scorecard, trial, references, vesting, governance |
| Technical founder remains the only person who understands the system | High | High | Architecture documentation, module SDK, pairing, ownership transfer |
| Design quality depends entirely on one founder | High | High | Encode recipes, renderer rules, review tools, and hire design engineering |
| Founders avoid sales while seeking a salesperson | Medium | High | Existing founders close first customers and define motion |
| Team burns capital before narrowing | Medium | High | Stage-gated hiring and monthly proof review |
| Founder roles remain ambiguous | Medium | High | Written decision rights and weekly owner review |

### 54.5 Legal and platform risks

The company will eventually touch payments, identity, personal data, communications, commerce, and third-party content. Risks include:

- Data-protection and residency obligations.
- Payment facilitation and marketplace regulation.
- Consumer-protection claims about generated applications.
- Third-party API and model terms.
- Open-source license obligations.
- Customer ownership of generated source and data.
- Accessibility requirements.
- Security representations in contracts.
- Sector-specific requirements in health, finance, employment, or education.

Use counsel to define the initial supported sectors and prohibited uses. A platform can be general-purpose while its commercial terms remain specific about unsupported regulated activity.

### 54.6 The narrative risk

The product can sound either too technical or too magical.

If the pitch emphasizes Goja, runtime ownership, and module linking, investors may see a niche JavaScript host. If it emphasizes instant professional applications without showing the mechanism, investors may hear an undifferentiated vibe-coding claim.

The remedy is a three-step explanation:

1. Agents are good at specifying business logic but unreliable at reproducing operational infrastructure.
2. The platform gives them high-level modules whose operational semantics are implemented and governed centrally.
3. The result is smaller, safer, more maintainable software with recurring module economics.

Then show it.

## 55. Kill criteria and strategic pivots

A kill criterion is not a declaration that the vision was foolish. It is a promise to stop funding a specific hypothesis when evidence contradicts it.

### 55.1 Company-level continuation criteria

After twelve months of concentrated work, the company should demonstrate most of the following:

- A defined customer segment with repeated pain.
- At least twenty paying customers, or a smaller number with meaningful recurring contracts.
- Multiple customers operating more than one application.
- Repeated use of the same premium modules.
- Declining delivery and support cost per standard application.
- Evidence that customers retain because of the platform, not only founder service.
- A credible path to software gross margins.
- A distribution motion with signs of repeatability.
- A team capable of operating the platform without one founder handling every incident.

If none of these exist, the company should not continue presenting the same plan with more features.

### 55.2 Wedge kill criteria

#### Studio and agency wedge

Change or abandon the wedge if, after ten serious partner engagements:

- Studios refuse recurring platform economics.
- Partners require full source and infrastructure ownership with no retained platform value.
- Each app requires bespoke native module work.
- Partner support costs exceed platform revenue with no improvement trend.
- Studios do not produce repeat client volume.

Possible pivot: sell the runtime and module platform directly to larger AI-native software factories or internal engineering teams.

#### Small-business vertical packs

Change or abandon a vertical if:

- Customer acquisition is fragmented and expensive.
- Existing vertical SaaS meets the need adequately.
- Migration and onboarding dominate value.
- Regulatory requirements exceed the company's stage.
- The same modules do not generalize to adjacent customers.

Possible pivot: sell the pack through vertical consultants or choose a workflow with higher change frequency.

#### Personal and community apps

Constrain the free surface if:

- Applications are created once and never reused.
- Sharing creates end-user traffic but not builders.
- Support and infrastructure cost exceed acquisition value.
- Privacy integrations such as email create disproportionate risk.

Possible pivot: use personal apps as curated demonstrations rather than an open free tier.

### 55.3 Product hypothesis kill criteria

Reconsider semantic modules as the primary programming model if agents do not show measurable improvement over conventional generation on:

- Successful production deployment.
- Number of repair iterations.
- Security defects.
- Application code size.
- Upgrade and rollback reliability.
- Support time.
- Cross-application reuse.

The likely response is not to abandon modules entirely. It may be to make the module system a layer used by conventional TypeScript applications rather than a compact Goja application runtime.

### 55.4 Strategic pivots that preserve the core insight

Several companies can be built from the same technical insight.

#### Pivot A: agent application runtime for other builders

Sell the runtime, module SDK, release system, and worker plane to AI coding platforms, studios, and enterprises. The company becomes infrastructure rather than the end-user builder.

This pivot is appropriate when other creation tools have distribution but lack safe operational semantics.

#### Pivot B: vertical software factory

Choose one high-value vertical—booking, logistics, field service, membership organizations, or commerce operations—and use the platform internally to create highly customized applications.

This pivot is appropriate when horizontal distribution is weak but one vertical shows strong repeated willingness to pay.

#### Pivot C: enterprise internal application governance

Focus on employee- and agent-created internal applications, with identity, data connectors, audit, approvals, and application inventory.

This pivot is appropriate when security and governance create stronger urgency than external app creation.

#### Pivot D: premium module network

Make high-level modules available to Replit, Lovable, v0, conventional TypeScript, and other agent environments. The company becomes an agent-friendly business capability layer.

This pivot is appropriate when module demand is strong across runtimes but customers resist a new application host.

#### Pivot E: AI-native studio operating system

Provide studios with planning, generation, design systems, client review, deployment, billing, and maintenance across multiple underlying runtimes.

This pivot is appropriate when studios love the workflow but require runtime flexibility.

### 55.5 What should not be abandoned casually

Preserve the core learning unless evidence directly disproves it:

> **Agents create better professional software when complex operational semantics are represented by small, typed, high-level capabilities.**

The runtime, customer, or distribution model can change while that insight remains valuable.


# Part IX. Pitch Assets

## 56. One-sentence pitches

One sentence cannot explain the entire company. Its job is to create the correct next question.

### 56.1 Primary investor pitch

> **We are building an agent-native application cloud where coding agents create compact JavaScript applications over secure, high-level modules, so custom software can be generated quickly and still be production-ready, governable, and maintainable.**

### 56.2 Outcome-oriented investor pitch

> **We let AI agents turn business intent into professional software by replacing thousands of lines of fragile operational glue with versioned modules for identity, payments, search, booking, data, UI, and deployment.**

### 56.3 Studio and agency pitch

> **Deliver custom client applications in days instead of months, using an agent-native platform that handles the hard production work and lets your team focus on workflow and design.**

### 56.4 Small-business customer pitch

> **We create software around the way your business actually works, then keep it hosted, secure, backed up, and easy to change as the business evolves.**

### 56.5 Enterprise pitch

> **Give employees and coding agents a governed way to create internal applications, with approved modules, identity, permissions, audit, release review, and a complete application inventory.**

### 56.6 Developer pitch

> **Write the business logic in JavaScript; import high-level modules; let the host own authentication, concurrency, secrets, infrastructure, deployment, and rollback.**

### 56.7 Module-provider pitch

> **Package your service as an agent-friendly application primitive, and we provide runtime integration, policy, metering, billing, documentation, and distribution into generated apps.**

### 56.8 General-audience pitch

> **You describe the software you need, an AI builds it from reliable building blocks, and the platform keeps it working like a professionally engineered product.**

### 56.9 Pitches to avoid

Avoid leading with:

- “AWS Lambda for Goja.” This describes an implementation layer and understates the product.
- “A better Replit.” It invites a feature comparison with a much larger company.
- “No-code for LLMs.” It is clever but unclear to buyers.
- “An app store for modules.” The marketplace is a later business model, not the initial value.
- “Build anything instantly.” The claim is broad, unprovable, and associated with prototype tools.
- “Secure by default” without specifying the structural controls and current scope.

## 57. Thirty-second pitch

### 57.1 Investor version

> Coding agents can generate a lot of code, but real applications still depend on difficult operational details: authentication, permissions, database semantics, payments, search, booking, deployment, rollback, and security. Today agents reproduce that glue differently in every project, which makes generated apps fragile. We built an application cloud where the agent writes a small JavaScript program against high-level, versioned modules, while the platform guarantees the operational behavior. We already have the secure runtime, HTTP framework, release system, identity work, and strong design demos. We are now using it with studios and design partners to build professional custom apps in days and turn the repeated capabilities into a module business.

### 57.2 Customer version

> Most businesses end up adapting their work to generic software or paying a large amount for custom development. Our platform lets us create an application around your real workflow in days. The application is not a throwaway prototype: it has users, permissions, persistent data, backups, release history, and support. When you need to change it, we create a reviewed release and can roll back safely.

### 57.3 Cofounder-candidate version

> We have a technically deep, working agent-native application platform and a design founder producing excellent product demos. The missing founder role is to choose the first market, close paid design partners, build the channel and pricing model, and lead the company and seed process with us. This is not a finished product looking for a salesperson. It is a company formation problem with unusually strong technical and design proof.

## 58. Two-minute pitch

> Software creation is moving from writing every implementation detail to describing what should exist. The current generation of coding agents proves that millions of people want to build applications, but the way those tools work creates a new problem: the agent generates a conventional stack and the user inherits every operational decision. Authentication, authorization, database migrations, payments, webhooks, search, deployment, and rollback are regenerated in slightly different ways for every app.
>
> Our core insight is that an agent should not have to reproduce those semantics. It should write a compact application program against high-level modules. A booking API should mean reserve a valid slot, not generate locks, retries, time-zone rules, reminders, and cancellation logic. A product-search API should mean search the authorized catalog, not configure indexing, ranking, typo tolerance, tenant filters, and metering. The platform owns that complexity in versioned modules.
>
> We built the technical foundation for this model: a Go-hosted JavaScript runtime with explicit module composition, a secure HTTP framework where authentication and authorization run before JavaScript, professional release and rollback semantics, identity integration, application workers, and a typed UI system. Our design co-founder has built applications that demonstrate the product quality this architecture can produce.
>
> We are entering through AI-native studios, agencies, and operational small-business applications such as booking, lightweight CRM, catalogs, quotes, and logistics. They need to deliver custom software repeatedly, which gives us revenue and shows us which modules recur. We charge for the builder, each production application, premium modules, and eventually enterprise governance and a marketplace.
>
> The long-term opportunity is a cloud where people and agents create software just in time—from a personal tool or a barbecue scheduling app to a professional CRM or commerce operation—without requiring the agent to reinvent production engineering every time.

## 59. Ten-minute investor narrative

The ten-minute pitch should be treated as one argument with a live product proof, not twelve disconnected slide descriptions.

### 59.1 Minute 0–1: the change in software creation

Open with the behavior, not the technology.

> More people can now create software by describing it. That is already a mass-market behavior. The limiting problem has moved. The question is no longer only whether an agent can generate an interface and some code. The question is whether the resulting application can safely run a business, evolve over time, and be operated by someone who did not hand-engineer the stack.

Show one strong generated application immediately. Do not spend the first minute on a market chart.

### 59.2 Minute 1–2: the production gap

Show a conventional generated application architecture:

```text
prompt
  -> generated frontend
  -> generated API routes
  -> generated schema
  -> auth integration
  -> payment integration
  -> deployment config
  -> monitoring and recovery
```

Explain that the agent is asked to reproduce operational decisions that have failure modes far outside the visible interface.

Use a concrete example:

> “Reserve this booking slot” appears simple. In production it means concurrency control, idempotency, time zones, cancellation rules, reminders, authorization, and payment state. If every app regenerates those rules, every app becomes a new reliability problem.

### 59.3 Minute 2–3: the insight

Introduce the semantic split.

> We move the operational semantics into versioned modules. The agent specifies what the application means. The platform implements how that meaning is safely produced.

Show two code samples side by side: one conventional integration and one compact module call. The module sample should be real and executable.

### 59.4 Minute 3–5: live demo

The live demo should follow a fixed sequence:

1. Start from a plain-language application request.
2. Show the agent selecting or being constrained to approved modules.
3. Show the generated compact application source.
4. Open a working preview with high design quality.
5. Show the data and user workflow.
6. Request a meaningful change.
7. Show the source and authority diff.
8. Create a release candidate and run validation.
9. Activate the release.
10. Demonstrate rollback or a denied unsafe change.

A good demo request might be:

> “Create a barbecue planning app for twenty friends. Let people propose dates, vote, claim food items, and pay their share. The organizer can see attendance and send reminders.”

Then connect it to a professional version:

> “The same module semantics support a catering booking system, a membership event platform, or a field-service scheduling workflow. The surface changes; the production capabilities remain governed and reusable.”

### 59.5 Minute 5–6: what is built

Show the system as a set of completed foundations and explicit gaps:

**Built or technically proven:**

- Goja runtime ownership and asynchronous execution.
- xgoja provider and native-module composition.
- Secure planned HTTP routes.
- Authentication, sessions, programmatic agents, CSRF, resources, authorization, audit, rate limits, and guarded fetch.
- Deployment validation, immutable releases, activation, rollback, and agent identities.
- Tiny-IDP production and scriptable identity foundations.
- Widget DSL and high-quality application demos.

**Being productized:**

- Isolated multi-tenant worker plane.
- Commercial module catalog and entitlement enforcement.
- Builder workspace and application planning.
- Design-partner delivery and studio workflow.
- Billing, usage, support, and customer operations.

This honesty improves credibility. The company has solved hard problems, but has not yet solved every business problem.

### 59.6 Minute 6–7: beachhead

State one first market:

> We are starting with AI-native studios, agencies, and automation consultants that repeatedly deliver operational software. They already have customers, they understand custom workflows, and they feel the cost of rebuilding authentication, data, payments, search, deployment, and maintenance for every project.

Show the first solution packs:

- Booking and customer portal.
- Lightweight CRM and quoting.
- Catalog, product search, and ordering.
- Internal logistics and status workflows.

Explain that direct small-business customers are a secondary channel and personal/shared apps are a product-led surface, not the initial revenue model.

### 59.7 Minute 7–8: business model

Show the four revenue layers:

1. Builder subscription.
2. Production application runtime.
3. Premium modules and resources.
4. Enterprise, marketplace, and partner revenue.

Use one invoice example:

```text
Studio plan                         $499 / month
8 active client applications       $392 / month
Booking module on 3 apps            $147 / month
Product search usage                 $86 / month
Storage and runtime overage           $41 / month
-------------------------------------------------
Monthly platform revenue           $1,165
```

State that the numbers are hypotheses being tested, not published pricing.

### 59.8 Minute 8–9: defensibility

Defensibility is not “we use Goja.” It is the combination of:

- High-level module semantics and operational edge cases.
- Application and release outcome data.
- A growing corpus of successful compact programs.
- Design recipes and renderer systems.
- Studio and module-provider distribution.
- Trust, governance, and application inventory.
- Module economics that persist after generation.

Explain that better models improve the platform because they become better clients of the same semantic APIs.

### 59.9 Minute 9–10: team, proof, and ask

> The technical founder built the core runtime and security architecture. The design founder built an unusually strong application and interface system. We are adding the commercial founder or founding GTM leader who will own the first market and company-building motion. Over the next eighteen to twenty-four months, the capital turns the technical proof into paid design partners, a repeatable studio product, the first premium module catalog, and a self-service application cloud.

State the exact round, milestones, and current customer proof. End on the application, not the financing slide.

## 60. Investor one-pager

### From intent to production software

**Company:** Working name to be determined  
**Category:** Agent-native application cloud  
**Stage:** Technical product built; design-partner commercialization  
**Round:** Targeting a $3.5 million seed, adjusted to customer proof

#### Problem

Coding agents can generate application code, but professional software depends on operational semantics that agents currently reproduce in every project: authentication, permissions, data consistency, payments, search, booking, secrets, integrations, deployment, observability, migration, and rollback. The generated application may look complete while carrying hidden security and maintenance risk.

#### Insight

LLMs perform better when they operate against small, typed, goal-oriented APIs. The application should state what a business operation means; the platform should own how it runs safely. A search module should expose product search, not search-cluster administration. A booking module should expose reservation semantics, not locks and reminder queues.

#### Product

The platform lets coding agents generate compact JavaScript or TypeScript applications over a catalog of secure, versioned modules. It provides:

- Agent planning and generation.
- High-level modules for data, identity, payments, search, booking, messaging, UI, and workflows.
- A Go-owned secure HTTP pipeline.
- Isolated execution with explicit permissions and resources.
- Preview, validation, immutable releases, deployment, audit, and rollback.
- A typed UI protocol and professional design system.
- APIs and MCP tools for external coding agents.

#### Why now

Prompt-to-app platforms have validated mass demand and attracted major usage and capital. At the same time, leading platforms now describe production security, governance, built-in primitives, and agent-driven deployment as central product problems. The competitive frontier is moving from code generation toward reliable application semantics.

#### Beachhead

Start with AI-native studios, agencies, automation consultants, and operational small-business applications. These customers create repeated custom software and expose recurring module patterns. Initial packs include booking, lightweight CRM, catalog/search, quoting/orders, and internal logistics.

#### Business model

- Builder and studio subscriptions.
- Base fee and metered usage per production application.
- Premium modules and managed resources.
- Enterprise governance and private deployment.
- Marketplace take rate on modules, templates, and experts.

#### Defensibility

The moat compounds through module operational history, application and release outcome data, a corpus of successful agent-authored programs, design recipes, provider economics, partner distribution, and a trusted governance layer. Model improvements increase the value of the platform rather than eliminating it.

#### Team

- Technical founder with a substantial first version of the runtime, module system, HTTP security framework, release control plane, and identity architecture.
- Design founder with strong product craft, renderer and DSL work, and impressive working demonstrations.
- Active search for a commercial co-founder or founding GTM leader to own market selection, customers, partnerships, fundraising, and company operations.

#### Eighteen- to twenty-four-month milestones

- Ten to twenty paid design partners and repeated production use.
- Two to three proven vertical solution packs.
- Studio workspace and external-agent API.
- First premium module catalog with measured margins.
- Self-service application creation and runtime billing.
- Production worker isolation, governance, support, and reliability evidence.

#### Ask

Capital, design partners, studio relationships, module-provider partners, and introductions to an exceptional commercial co-founder.

## 61. Outreach messages

Outreach should be brief enough to answer and specific enough to demonstrate fit.

### 61.1 Warm investor introduction request

**Subject:** Introduction to [Partner] — agent-native application platform

> I am building a platform that lets coding agents create compact JavaScript applications over secure, high-level modules for identity, data, payments, search, booking, UI, and deployment. The technical runtime and several strong product demos are working; we are now starting a focused design-partner motion with studios and operational software use cases.
>
> [Partner] appears relevant because of their work in [developer tools / application infrastructure / design software / vertical SaaS]. Would you be comfortable introducing us? I can send a one-page summary and a short demo first.

### 61.2 Direct investor message

**Subject:** Agents can generate code; we are building the production semantics

> [Name] — I am the technical founder of an agent-native application cloud. Instead of asking an LLM to regenerate authentication, database behavior, payments, search, deployment, and rollback for every app, the agent writes a small JavaScript program against versioned high-level modules and the host guarantees the operational behavior.
>
> We have built a substantial secure runtime and release foundation, and my design co-founder has working demos that show the product quality. We are entering through studios and repeated operational applications. Your investment in / writing about [specific company or thesis] suggests this may fit. May I send a five-minute demo and one-page memo?

### 61.3 Design-partner message

**Subject:** Build one of your recurring workflows as a professional custom app

> We are working with a small group of teams that currently coordinate important work through spreadsheets, forms, email, and several disconnected tools. We can turn one of those workflows into a custom application in days, including users, permissions, data, notifications, and a controlled release process.
>
> We are looking for workflows that are repeated, painful, and likely to change over time. The design partnership is paid but discounted, and you receive a working production application plus direct influence over the platform. Would a 30-minute workflow review be useful?

### 61.4 Studio or agency partner message

**Subject:** A production platform for AI-native custom app delivery

> Your team already knows how to discover workflows and design client experiences. We are building the runtime that removes the repeated production work: auth, permissions, data, payments, search, booking, deployment, rollback, and managed modules behind a compact JavaScript API.
>
> We are selecting a few studios to test whether the platform can reduce delivery time and create recurring runtime revenue without taking away the client relationship. I would like to show you the current demos and compare them with the kinds of projects you repeatedly build.

### 61.5 Commercial co-founder message

**Subject:** Cofounder role: turn a working agent-native app cloud into a company

> I have built a technically substantial first version of an application platform designed for coding agents: compact JavaScript programs, native high-level modules, secure HTTP semantics, release/version/rollback, identity, and isolated hosting. A design founder has built an unusually strong product and demo layer.
>
> We are looking for the person who wants founder-level ownership of market selection, design partners, pricing, studio channels, company operations, recruiting, and seed fundraising. The role starts with a working trial on real customer and pitch work; it is not a generic “business co-founder” search. Your experience with [specific evidence] looks unusually relevant. Are you open to a direct conversation?

### 61.6 Advisor request

> We are not looking for a ceremonial advisor list. We need help with [specific issue: studio channel economics, developer-platform pricing, enterprise app governance, module marketplace, or seed positioning]. Could we schedule one focused session? I will send a short memo with the decision, evidence, and alternatives in advance.

### 61.7 Customer reference request

> We are preparing a financing and broader design-partner launch. Would you be comfortable speaking with a small number of investors or prospects about the problem you had, the application we delivered, the time to value, and what still needs improvement? We will coordinate each request and never share confidential information without approval.

### 61.8 Follow-up after a first investor meeting

> Thank you for the discussion. The two questions I heard were [question one] and [question two]. We are addressing them through [specific customer test or product proof]. I have attached the short technical note we discussed and a link to the demo. I will send an update when [explicit milestone] is complete.

## 62. Founder FAQ

This section provides direct answers to questions that investors, candidates, partners, and the founders themselves are likely to ask.

### 62.1 Why JavaScript and Goja?

JavaScript is widely understood by models, developers, and frontend ecosystems. Goja embeds JavaScript inside a Go-owned runtime without requiring a separate V8 service or Node process for every application. More importantly, go-go-goja already provides explicit runtime ownership, native modules, generated xgoja profiles, asynchronous boundaries, and a secure HTTP framework. The company is not betting that Goja is the fastest general JavaScript engine. It is using Goja as a controllable language layer over high-value native capabilities.

CPU-heavy work should not run as arbitrary JavaScript. It should run in bounded native modules, external services, queues, or specialized infrastructure.

### 62.2 Why not just build on Node.js?

Node has a vast ecosystem but also a vast ambient dependency and authority surface. The product thesis requires a closed, reviewable module set, runtime-owned context, and application profiles constructed from selected native capabilities. Node can be used elsewhere in the system, but a general npm environment is not the safest default for untrusted agent-generated applications.

The semantic module architecture could eventually support other runtime targets. Goja is the first controlled execution substrate, not necessarily the only one forever.

### 62.3 Why will agents be better at this than ordinary app generation?

The platform reduces the number of operational choices and represents business operations directly. The claim should be tested quantitatively. Expected improvements include fewer generation iterations, smaller programs, fewer security defects, better static validation, easier tests, and more reliable upgrades. If those improvements do not appear, the product needs to change.

### 62.4 Is this simply an AI app builder?

It includes an app-building experience, but the differentiated product is the application substrate. Current builders generally generate conventional stacks and integrate lower-level services. This platform makes versioned semantic modules, permissions, resources, and professional release behavior the primary programming model.

### 62.5 Why cannot Replit, Lovable, v0, Wix, or a cloud provider copy this?

They can and will add high-level primitives. The company must build more than a feature. The durable system includes deep module semantics, operational edge cases, module economics, a compact program model, application and release outcome data, design recipes, studio distribution, provider relationships, and trust.

The company should assume competitors improve rapidly. It wins by focusing earlier, learning faster in selected workflows, and building a coherent ecosystem around the semantic runtime.

### 62.6 What is the initial customer?

The recommended first customer is an AI-native studio, agency, automation consultant, or technically ambitious operator that repeatedly needs custom operational applications. The first end-user workflows are booking, lightweight CRM, catalogs/search, quotes/orders, internal logistics, customer portals, and coordination.

### 62.7 Why not start with personal applications?

Personal apps are strategically important because they demonstrate just-in-time software and create sharing loops. They are a difficult first business due to low willingness to pay, privacy integrations, broad support needs, and consumer acquisition. They should be a bounded free or viral surface until their economics are proven.

### 62.8 Can the platform really support both a barbecue poll and a CRM?

The runtime and module principles can support both. The products have different support, compliance, pricing, and distribution requirements. The architecture can remain broad while the commercial message and launch segment remain narrow.

### 62.9 What is a premium module?

A premium module exposes a small application API over difficult, ongoing operational behavior. Examples include product search, booking, commerce, managed identity, messaging, document workflows, maps/routing, or logistics. Premium status is justified by recurring customer value, provider cost, operational responsibility, or specialized domain depth.

### 62.10 Why is product search a good example?

A simple `products.search()` API can hide indexing, ranking, typo tolerance, facets, tenant isolation, merchandising, analytics, cache invalidation, provider selection, quotas, and cost control. It is easy for an agent to use, valuable to many applications, and operationally substantial enough to support recurring revenue.

### 62.11 Are modules just API wrappers?

No. A useful module owns lifecycle and policy as well as transport. It may provision resources, maintain state, validate schemas, enforce permissions, manage retries and idempotency, emit usage, expose observability, and support version upgrades. A thin wrapper can be included, but it is not the primary moat.

### 62.12 Who builds the modules?

The company builds the first-party core and first premium catalog. Later, infrastructure providers, vertical experts, and third-party developers can build reviewed modules through a provider SDK. The marketplace should not launch until module lifecycle, billing, support, and security review are stable.

### 62.13 What happens when a module has a security bug?

Releases pin exact module versions. The platform can block new releases, notify affected customers, test a patched version, canary it, and promote controlled upgrades. Emergency policy can suspend a vulnerable module or application. Centralizing operational behavior makes a patch more scalable, but also increases correlated risk, which requires module-specific incident processes.

### 62.14 How does rollback work when data changes?

Code rollback and data rollback are separate. Releases should declare schema compatibility. Migrations should use expand/contract patterns, backups, and explicit approvals for destructive changes. The platform can route traffic back to an earlier compatible release, but it should not pretend that every database migration is automatically reversible.

### 62.15 Is customer JavaScript trusted?

No. The production model should treat tenant-authored code as untrusted and isolate it at the operating-system or sandbox boundary. Goja's controlled module surface reduces authority but is not a complete security boundary. Timeouts require interrupt and process termination, and workers that encounter unsafe states should be discarded.

### 62.16 Does the system expose arbitrary network access?

Not by default. Outbound HTTP is a capability with explicit origin policy, timeout, response limits, credential-source controls, metering, and audit. High-value integrations should use typed modules rather than arbitrary fetch whenever practical.

### 62.17 How are secrets handled?

Secrets remain in host-managed stores or provider bindings. JavaScript receives opaque handles or narrow operations, not raw long-lived credentials. Logs, prompts, request contexts, and audit records should be redacted and bounded.

### 62.18 How does application authentication work?

Platform users and hosted-application users are separate populations. The control plane authenticates customers and collaborators. Hosted apps can use managed identity realms, dedicated identity deployments, or external OIDC. The application receives verified, non-secret identity claims and declares route policy; Go owns credential validation, sessions, CSRF, and protocol operations.

### 62.19 Why is the HTTP framework differentiated?

The Express-style JavaScript API compiles route intent into a Go-owned plan. Before JavaScript executes, the host can apply authentication, principal requirements, CSRF, resource resolution, grant checks, authorization, rate limits, and audit. The same plan can protect Go handlers. This turns security policy into a reviewable application artifact rather than scattered handler code.

### 62.20 What is the UI strategy?

The platform supports static frontend assets and a versioned Widget DSL. In the Widget model, application code returns semantic, serializable UI intent. A renderer owns components, styling, state wiring, accessibility, and target behavior. This gives agents a smaller grammar and lets design improvements propagate across applications.

Unsafe arbitrary HTML can exist as a privileged capability, not the default safe UI contract.

### 62.21 Will customers be locked in?

Managed high-level modules create platform dependence, as every cloud platform does. Reduce harmful lock-in through source export, data export, release manifests, module locks, documented APIs, and clear ownership terms. Some managed semantics will require the platform runtime. That boundary should be explicit during sales.

### 62.22 Can customers self-host?

Not necessarily at launch. Self-hosting expands support, security, upgrade, and module-provider complexity. Enterprise dedicated deployments or a controlled runtime package can be offered when demand and economics justify them. The first product should optimize for a reliable managed service.

### 62.23 What is open source?

A possible strategy is to keep the runtime, module SDK, local development tools, and selected core modules open, while the managed control plane, premium modules, governance, billing, and marketplace are commercial. The exact boundary should maximize adoption and trust without giving away the entire managed economic layer.

Open source should have a product reason: developer trust, provider ecosystem, local development, or distribution. It should not be used as a substitute for go-to-market.

### 62.24 How does pricing work?

Internally, maintain separate ledgers for creation, runtime, modules, and contract entitlements. Externally, present simple packages. A studio might pay a builder subscription, a fee per active client application, and module usage. An enterprise might pay an annual platform contract with included application and usage capacity.

### 62.25 Why will gross margins be attractive?

Application programs are small, and Goja is efficient for orchestration workloads. Expensive behavior can be centralized, metered, and priced through modules. Margins depend on model generation cost, worker utilization, provider pass-through cost, support, and application traffic. The company must instrument them from the first pilots rather than assume infrastructure margins.

### 62.26 Is this a services business?

The launch uses paid services to discover repeated product patterns. The company remains a software business only if module reuse rises, delivery hours decline, recurring platform revenue grows, and partners can ship without founder intervention. Those metrics should be reviewed explicitly.

### 62.27 What is the marketplace opportunity?

Once there is application demand and a stable module contract, third parties can sell modules, templates, design systems, vertical packs, and expert services. The platform can provide installation, permissions, metering, billing, compatibility, review, and distribution. The marketplace is an expansion mechanism, not the day-one wedge.

### 62.28 What is the largest possible company?

The largest vision is a new application cloud in which software is created when needed rather than purchased from a fixed catalog. Individuals create personal tools; communities create temporary shared applications; businesses create systems around their exact operations; enterprises govern portfolios of employee- and agent-created software; providers distribute capabilities as modules.

The company captures value from creation, operation, modules, transactions, enterprise governance, and the ecosystem.

### 62.29 Why raise venture capital?

The platform requires simultaneous investment in runtime security, product experience, modules, application delivery, and distribution. A credible winner can become a large ecosystem company, but the market is moving quickly and competitors are well financed. Venture capital is appropriate if the founders want to pursue the broad platform outcome and can demonstrate a path to venture-scale distribution.

A narrower profitable studio or vertical software factory could be built with less capital. The financing choice should match the intended company.

### 62.30 What should the seed round prove?

The seed should prove that the architecture becomes a repeatable business:

- Paid customers use production applications.
- Agents create them faster and more reliably through semantic modules.
- Repeated workflows become modules and packs.
- Studios or direct customers provide a repeatable acquisition path.
- Application count and module revenue expand per customer.
- The worker and control plane meet a truthful production standard.
- The company can move toward self-service without services cost growing linearly.

### 62.31 Why this team?

The technical founder has already tackled runtime ownership, module composition, HTTP security, release control, identity, and isolation problems that most app-builder teams encounter later. The design founder has an effective product system and impressive demos. The team is adding commercial founder-level ownership deliberately rather than pretending technology alone creates a company.

### 62.32 What is the biggest unresolved question?

The largest unresolved question is distribution: which customer repeatedly pays for custom applications on this substrate, and which channel can acquire them efficiently? The design-partner and studio program exists to answer that question before the company scales the team.


# Appendix A. Source notes

## A.1 Source method

Market and financing facts in this document were checked against company announcements, official product and pricing documentation, primary developer documentation, or established private-market data providers. They are evidence about current behavior, not guarantees about this company.

The category moves quickly. Refresh financing, pricing, usage, and product claims before sending an investor document. Preserve the retrieval date in the external version so a reader can distinguish a historical claim from a current one.

## A.2 Source register

| Source | Organization | Subject | Why it is used |
|---|---|---|---|
| S1 | Replit | March 2026 Series D, valuation, users, enterprise penetration | Category demand and scale |
| S2 | Replit | September 2025 Series C and annualized revenue growth | Category growth evidence |
| S3 | Lovable | December 2025 Series B | Investor conviction and nontechnical-builder demand |
| S4 | Lovable | MCP interface for external agents | Agent-operated platform evidence |
| S5 | Vercel | February 2026 v0 relaunch | Production, enterprise security, and shadow-IT framing |
| S6 | Vercel | new.website acquisition | Built-in primitives reduce prompting and configuration |
| S7 | Wix | Base44 acquisition | Strategic value of natural-language application creation |
| S8 | Carta | July 2026 software financing benchmarks | Seed planning context |
| S9 | Replit | Core and Pro pricing | Current app-builder price anchors |
| S10 | Carta | AI infrastructure seed benchmark | Exceptional infrastructure-financing context |
| S11 | Shopify | App developer revenue share | Marketplace economics precedent |
| S12 | Stripe | Usage and hybrid billing | Billing substrate and pricing-model support |
| S13 | Algolia | Grow plan pricing | Specialist-module usage economics |
| S14 | Carta | SAFE and priced-round prevalence | Financing instrument context |
| S15 | Y Combinator | Co-founder matching preferences | Complementary founder-skill evidence |
| S16 | Carta | Founder Ownership Report 2026 | Founder-team and ownership context |
| S17 | Vercel | Agentic Infrastructure | Agent-driven deployment behavior |
| S18 | Wix | 2025 full-year results and Base44 ARR | Commercial scale of generated applications |
| S19 | Lovable | Apps available inside ChatGPT and Claude | Agent-mediated application distribution |
| S20 | South Park Commons | Residency and funding | Cofounder/founder community option |
| S21 | Entrepreneurs First | Individual founder and cofounder matching program | Cofounder search option |
| S22 | Y Combinator | Cofounder matching success examples | Trial-project precedent |
| S23 | Carta | Two-founder equity data | Equity discussion context |
| S25 | Lovable | Supabase integration and LLM-friendly translation layer | Evidence for semantic API design |
| S26 | First Round Review / Airtable | Horizontal product go-to-market | Evidence for narrowing a broad platform wedge |

Source S24 is intentionally unused in this edition so source numbers remain stable across working drafts.

## A.3 Interpretation cautions

### Financing benchmarks

Median financing data describes completed rounds among companies that raised. It does not describe the probability that an arbitrary company will raise, nor does it establish an appropriate valuation. Round size should be derived from milestones, runway, dilution, and investor demand.

### Competitor usage and revenue

Company announcements are useful evidence of category momentum but may use non-comparable definitions. “Users,” “annualized revenue,” “ARR,” “deployments,” and “Fortune 500 usage” can be measured differently. Use them to show direction, not to calculate a precise total addressable market.

### Pricing pages

Published self-service prices change frequently and omit negotiated enterprise contracts, discounts, credits, and pass-through infrastructure. They are anchors for packaging discussion rather than direct comparables.

### Marketplace terms

Shopify's revenue-share structure is a precedent for ecosystem design, not a recommended take rate. A new marketplace must account for payment processing, support, refunds, taxes, provider costs, and the amount of demand the platform actually creates.

# Appendix B. Assumptions and model notes

## B.1 Purpose of the models

Every financial table in this document is an operating hypothesis. The numbers are designed to expose relationships and decisions, not to produce a forecast that appears precise.

Maintain a separate spreadsheet with editable assumptions, monthly cash flow, customer cohorts, infrastructure cost, headcount, and financing. The narrative document should show only the outputs needed to explain the business.

## B.2 Revenue model

A general monthly revenue formula is:

```text
monthly revenue
  = builder subscriptions
  + active application base fees
  + metered runtime revenue
  + premium module subscriptions
  + premium module usage
  + services and implementation
  + enterprise contract allocation
  + marketplace take rate
  + transaction revenue
  - credits, discounts, refunds, and bad debt
```

Keep the ledgers separate even when the invoice is bundled. Separate ledgers let the company understand whether a customer values creation, application operation, a specific module, or professional service.

## B.3 Customer types

Model at least four cohorts separately:

| Cohort | Primary unit | Expected pattern |
|---|---|---|
| Individual builder | One builder and one to three apps | Low acquisition cost, high churn risk, limited support |
| Studio or agency | Builders and active client apps | Higher app count, channel leverage, partner support requirements |
| Direct SMB | One business and one to several operational apps | Strong workflow retention, onboarding and migration cost |
| Enterprise | Annual contract, app portfolio, users and governance | Long sales cycle, high ACV, compliance and support commitments |

Do not calculate one average customer across all four.

## B.4 Illustrative pricing assumptions

The pricing hypotheses in the document assume ranges such as:

- Individual builder: $20–$50 per month plus runtime.
- Professional builder or small team: $100–$300 per month.
- Studio: $399–$1,499 per month plus active applications and modules.
- Production application base fee: $29–$149 per month depending on profile.
- Premium module: $20–$500 per application per month, or usage-based.
- Enterprise: $25,000–$250,000 annual contract value before large private deployments.
- Design-partner implementation: $5,000–$50,000 depending on scope.

These are test ranges. Publish prices only after the company understands included support, infrastructure, and module provider cost.

## B.5 Module contribution margin

Calculate module contribution margin as:

```text
module contribution margin
  = module revenue
  - third-party provider charges
  - dedicated infrastructure
  - incremental support
  - refunds and credits
  - payment processing attributable to the module
```

Shared engineering and company overhead are excluded from contribution margin but included in gross margin and operating margin as appropriate.

A module with low direct margin may still be valuable if it causes high retention or application expansion. Track both direct module margin and influenced revenue.

## B.6 Application contribution margin

```text
application contribution margin
  = application base and usage revenue
  - worker compute
  - storage and bandwidth
  - database and backup cost
  - observability cost
  - model inference attributed to application operation
  - customer support attributable to the application
```

Generation cost belongs to the builder or creation ledger unless it is bundled into application onboarding.

## B.7 Services accounting

Separate:

- Discovery and workflow design.
- Application-specific implementation.
- Reusable module development.
- Data migration.
- Training and onboarding.
- Ongoing support.

Reusable module development is product investment even when discovered during a paid project. Application-specific implementation is service cost. Failing to separate them can make product margins appear better or worse than reality.

## B.8 Acquisition and retention

Track customer acquisition cost by channel:

```text
CAC
  = channel-specific sales and marketing spend
  + allocated founder or sales time
  + partner commission
  + unrecovered pilot cost
  divided by new paying customers
```

For studios, also track cost per activated client application. A studio with a higher customer acquisition cost can be attractive if it creates many retained applications.

Retention should be measured at multiple levels:

- Builder retention.
- Organization retention.
- Application retention.
- End-user activity.
- Module retention.
- Net revenue retention.
- App count expansion.

An organization may remain while replacing one application. That is different from full platform churn.

## B.9 Market model

The bottom-up market model should avoid a claim such as “all software spending.” Use observable units:

```text
number of target studios
  × average active client applications
  × annual platform revenue per application

plus

number of target direct businesses
  × average applications per business
  × annual platform and module revenue

plus

enterprise application portfolios
  × annual governance and runtime contract
```

Run conservative, base, and aggressive cases. The seed pitch does not require a precise global total if the beachhead and expansion logic are credible.

## B.10 Example studio cohort

Illustrative only:

| Variable | Value |
|---|---:|
| Studio subscription | $499/month |
| Active client applications | 10 |
| Average app base revenue | $49/month |
| Average module revenue per app | $65/month |
| Runtime overage average | $15/month/app |
| Monthly revenue per studio | $1,789 |
| Annualized revenue per studio | $21,468 |

At one hundred similar studios, annualized revenue would be approximately $2.15 million before implementation, enterprise, or marketplace revenue. The critical assumptions are active app count, module attach rate, churn, and support cost.

## B.11 Example direct-business cohort

| Variable | Value |
|---|---:|
| Business platform plan | $149/month |
| Active applications | 2 |
| Included one app; second app | $49/month |
| Premium modules | $150/month |
| Usage overage | $30/month |
| Monthly recurring revenue | $378 |
| Annualized revenue | $4,536 |

A thousand customers at this profile represent roughly $4.5 million in annual recurring revenue. Customer acquisition and onboarding determine whether the model is attractive.

## B.12 Financing model

For a financing plan, model:

- Starting cash.
- Round gross proceeds.
- Legal and transaction cost.
- Hiring dates rather than annualized headcount only.
- Salary, payroll tax, benefits, recruiting, equipment, travel, and contractor cost.
- Cloud and model cost by customer cohort.
- Revenue collection timing and payment terms.
- Bad debt and refunds.
- Contingency reserve.
- Minimum cash threshold for beginning the next financing.

A $3.5 million raise does not create twenty-four months of runway automatically. Hiring sequence and revenue matter.

## B.13 Dilution examples

Simple post-money dilution approximation:

```text
new investor ownership
  = new capital / post-money valuation
```

A $3.5 million round at a $20 million post-money valuation implies 17.5% new investor ownership before considering option-pool changes or other securities. SAFE conversion, pre-money versus post-money option pool treatment, and multiple instruments can materially change founder ownership. Use a cap-table model and counsel.

## B.14 Metrics definitions

Define metrics before reporting them.

- **Application created:** A project with a valid compiled program, not merely a prompt.
- **Application activated:** A release receiving production traffic.
- **Active application:** An activated app with defined end-user or scheduled activity during the period.
- **Successful generation:** A requested change that passes validation and is accepted without manual source repair.
- **Module attach rate:** Percentage of active applications using a module.
- **Semantic coverage:** Percentage of operational behavior implemented through catalog modules rather than app-specific infrastructure.
- **Time to first value:** Time from accepted request to an end user completing the target workflow.
- **Rollback rate:** Percentage of activations reverted within a defined interval.
- **Support minutes per app:** Human support time attributable to an active application.
- **Studio independence:** Percentage of partner applications shipped without founder intervention.

Consistent definitions are more valuable than impressive but unstable metrics.

# Appendix C. Cofounder discussion questions

A founder relationship should be examined before it is romanticized. These questions are not a compatibility quiz. They surface assumptions that otherwise become conflicts under pressure.

## C.1 Mission and ambition

1. What company do you want to exist in ten years?
2. Which part of the current thesis would you defend even after a difficult year?
3. Which part are you least convinced by?
4. Do you want a venture-scale platform company, a profitable software company, or either depending on evidence?
5. What outcome would make the next decade feel worthwhile even if the company is not a unicorn?
6. Which customer problems do you personally care about?
7. What kinds of applications should the company refuse to support?
8. How important are open source, ecosystem, and developer adoption relative to managed revenue?
9. What would cause you to change the initial market?
10. What would cause you to stop the company?

## C.2 Role and authority

11. Which work do you want to perform every week for five years?
12. Which work do you tolerate but do not want to own?
13. Who should be CEO, and why?
14. What decisions should the CEO make without unanimous founder approval?
15. Which decisions belong to the technical founder?
16. Which decisions belong to the design founder?
17. Which decisions belong to the commercial founder?
18. How should customer promises be approved?
19. How should the team resolve a product decision when customer evidence and technical judgment conflict?
20. What is the smallest area in which each founder has final authority?

## C.3 Commitment and life constraints

21. When can each founder work full-time?
22. What personal runway does each founder have?
23. What minimum salary is required, and when?
24. Are there family, health, visa, location, or caregiving constraints that affect the company?
25. How much travel is acceptable?
26. Is relocation possible or desirable?
27. How many years is each person prepared to work before liquidity?
28. What outside work, advisory roles, or investments will continue?
29. How should the company respond if a founder needs extended leave?
30. What level of personal financial risk is acceptable?

## C.4 Equity and compensation

31. What existing work and intellectual property is being contributed?
32. How should prior full-time work be recognized?
33. What future commitment does each founder make?
34. Should the equity split be equal, near-equal, or weighted? Why?
35. When should vesting begin for each founder?
36. What happens if a founder leaves before the cliff?
37. What happens if a founder becomes part-time?
38. When should founder salaries begin and how should they be set?
39. How should cash contributions or founder loans be treated?
40. What acceleration, if any, is appropriate on acquisition or termination?

## C.5 Fundraising and ownership

41. How much capital should the company raise before product-market fit?
42. What dilution is acceptable to reach the next proof point?
43. Are there investors or strategic companies the founders would not accept?
44. How much control should the founders give a board?
45. How should the team choose between a higher valuation and a stronger investor?
46. What happens if the company cannot raise the planned seed?
47. Would the founders bootstrap or operate a services-led version?
48. What information should be shared with investors and when?
49. Who leads fundraising and investor relations?
50. How should secondary liquidity be considered later?

## C.6 Customer and product judgment

51. Is the studio and agency wedge the best first market?
52. Which customer request would each founder refuse even if it produced substantial revenue?
53. How much service work is acceptable during the first year?
54. When does a customer-specific feature become a module?
55. Who decides whether a module is safe and supportable?
56. How should the company handle a security issue that requires disabling customer functionality?
57. What level of product quality is required before charging?
58. How should design quality and delivery speed be traded off?
59. How much source and data portability should customers receive?
60. When should the company support self-hosting?

## C.7 Working style

61. What does a good weekly founder meeting look like?
62. How quickly does each founder make reversible decisions?
63. How does each founder prefer to receive criticism?
64. What behavior causes each person to lose trust?
65. How does each founder behave when tired or afraid?
66. Does each person surface bad news early?
67. How should commitments be recorded and reviewed?
68. What communication requires synchronous discussion?
69. How much written decision-making is appropriate?
70. How should the founders protect focused work while remaining available to customers?

## C.8 Conflict

71. Describe a prior conflict in which you were wrong.
72. Describe a prior conflict in which you were right but handled it poorly.
73. When should a decision be revisited?
74. Who can mediate founder conflict?
75. What happens if two founders consistently agree against the third?
76. What behavior would justify removing a founder from an operating role?
77. What happens if a founder wants to sell and the others do not?
78. How should personal relationship repair be separated from the business decision?
79. What information should never be withheld from the other founders?
80. How will the founders know the relationship is failing?

## C.9 Ethics and trust

81. Which customer data uses are unacceptable even if legal?
82. What claims about AI, security, and production readiness will the company refuse to make?
83. How should the company handle applications that cause harm?
84. Which regulated sectors should be excluded initially?
85. How transparent should the company be about incidents?
86. How should usage data improve agents without violating customer trust?
87. What advertising or data-selling models are unacceptable?
88. How should the company balance law-enforcement requests, customer privacy, and safety?
89. How should conflicts of interest be disclosed?
90. What kind of company culture would each founder refuse to build?

## C.10 Success, failure, and exit

91. What does success mean at two, five, and ten years?
92. Would each founder accept an early acquisition? Under what conditions?
93. Is remaining independent a goal or an option?
94. How should a life-changing acquisition offer be evaluated?
95. What if the company becomes a strong $20 million revenue business but not a venture-scale outcome?
96. What if the platform thesis works but the initial product does not?
97. What if one founder wants to continue and another wants to stop?
98. How should founder performance be evaluated?
99. What would each founder regret not attempting?
100. After answering these questions, what remains difficult to say directly?


[^S1]: Replit, “The Future is Actually Very Human: Replit raises $400 million at a $9 billion valuation,” March 11, 2026, https://replit.com/blog/replit-raises-400-million-dollars. The announcement states more than 50 million users and use by people at 85% of the Fortune 500.

[^S2]: Replit, “Replit Closes $250 Million in Funding to Build on Customer Momentum,” September 10, 2025, https://replit.com/news/funding-announcement-series-c. The announcement reports annualized revenue growth from $2.8 million to $150 million in less than a year.

[^S3]: Lovable, “Lovable raises $330M to power the age of the builder,” December 18, 2025, https://lovable.dev/blog/series-b. The announcement reports a $6.6 billion valuation.

[^S4]: Lovable, “Lovable MCP: Build apps from any AI agent,” accessed July 20, 2026, https://lovable.dev/mcp. The page describes project creation, code inspection, database work, and deployment through agent-callable tools.

[^S5]: Vercel, “Introducing the new v0,” February 3, 2026, https://vercel.com/blog/introducing-the-new-v0. The announcement reports more than four million users and frames production security, enterprise integration, and shadow IT as central problems.

[^S6]: Vercel, “new.website joins forces with v0,” March 23, 2026, https://vercel.com/blog/new-website-joins-forces-with-v0. The announcement emphasizes built-in forms, databases, SEO, and content primitives that reduce prompting.

[^S7]: Wix, “Wix Further Expands into Vibe Coding with Acquisition of Base44,” June 18, 2025, https://www.wix.com/press-room/home/post/wix-further-expands-into-vibe-coding-with-acquisition-of-base44-a-hyper-growth-startup-that-simplif. Wix disclosed approximately $80 million of initial consideration plus performance-based earn-outs.

[^S8]: Carta, Peter Walker, “VC Startup Fundraising Benchmarks From 1000 Rounds,” July 10, 2026, https://carta.com/data/linkedin-vc-fundraising-benchmarks-2026/. The software-only six-month sample reports a $4.1 million median seed raise, $24.3 million median valuation, and 18% median dilution.

[^S9]: Replit, “Replit Pro Is Here — and Core Now Offers Even Better Value,” February 24, 2026, https://replit.com/blog/pro-plan. The announcement lists Core at $20 per month and Pro starting at $100 per month.

[^S10]: Carta, Peter Walker, “The AI Infra trade,” May 22, 2026, https://carta.com/data/newsletter-the-ai-infra-trade/. Carta reports a $13 million median seed round and $66 million median post-money valuation for AI infrastructure startups in its analysis.

[^S11]: Shopify, “Update to Shopify’s app developer revenue share,” April 24, 2025, https://shopify.dev/changelog/update-to-shopifys-app-developer-revenue-share. The current structure exempts the first $1 million of lifetime gross app revenue and applies 15% above that for most eligible developers.

[^S12]: Stripe, “Advanced usage-based billing,” accessed July 20, 2026, https://docs.stripe.com/billing/subscriptions/usage-based/advanced/compare, and “Usage-based billing,” https://docs.stripe.com/billing/subscriptions/usage-based. Stripe documents recurring fees, usage meters, credits, flat-fee-plus-overage, and hybrid pricing structures.

[^S13]: Algolia, “Grow Plan,” accessed July 20, 2026, https://www.algolia.com/pricing/grow-plan. The page prices the plan through included and additional search requests and stored records.

[^S14]: Carta, Kevin Dowd, “At pre-seed and seed, the dominance of SAFEs continues to grow,” January 7, 2025, https://carta.com/data/pre-seed-and-seed-safes-q3-2024/. The analysis reports SAFE prevalence at pre-seed and smaller seed rounds, with priced equity more common in larger seed financings.

[^S15]: Y Combinator, Catheryn Li and Katherine Bernstein, “What do people want in a co-founder?” October 21, 2021, https://www.ycombinator.com/blog/what-do-people-want-in-a-co-founder. YC reports matching preferences and the prevalence of technical/nontechnical pairings on its platform.

[^S16]: Carta, “Founder Ownership Report 2026,” March 2026, https://carta.com/data/founder-ownership-2026/. The report discusses founder counts, venture fundraising, equity ownership, and employee pools.

[^S17]: Vercel, Tom Occhino, “Agentic Infrastructure,” April 9, 2026, https://vercel.com/blog/agentic-infrastructure. Vercel reports that more than 30% of deployments were initiated by coding agents and that the share had risen approximately 1,000% over six months.

[^S18]: Wix, “Wix Reports Fourth Quarter and Full Year 2025 Results,” March 4, 2026, https://www.wix.com/press-room/home/post/wix-reports-fourth-quarter-and-full-year-2025-results. Wix reports Base44 reaching $100 million of ARR approximately one year after founding.

[^S19]: Lovable, “Your Lovable app now works inside ChatGPT and Claude,” July 15, 2026, https://lovable.dev/blog/agent-integrations. The announcement describes hosted MCP servers for published Lovable applications with OAuth and access controls.

[^S20]: South Park Commons, homepage and program description, accessed July 20, 2026, https://www.southparkcommons.com/. SPC describes a residency and funding from $1 million to $10 million for venture-scale companies.

[^S21]: Entrepreneurs First, “Found, don't follow,” accessed July 20, 2026, https://www.joinef.com/. EF describes backing individuals, helping them test and find cofounders, and supporting company creation before a fixed team exists.

[^S22]: Y Combinator, Catheryn Li, “Does co-founder matching work? It did for these YC companies,” November 24, 2021, https://www.ycombinator.com/blog/does-co-founder-matching-work. The examples include matched founders who worked on trial projects before committing and entering YC.

[^S23]: Carta, “Dynamic Duos: Equity Math for Two-Founder Teams,” June 2026, https://carta.com/data/two-founder-teams/. Carta reports that 44.6% of two-founder teams formed in 2025 split equity equally and that the median split was 51–49.

[^S25]: Lovable, “How Lovable’s Supabase Integration Changed the Game,” March 11, 2025, https://lovable.dev/blog/lovable-supabase-integration-mcp. The article describes creating a concise, structured, goal-oriented translation layer to make Supabase effective for LLM-driven application creation.

[^S26]: First Round Review, “Airtable's Path to Product-Market Fit — Lessons for Building Horizontal Products,” accessed July 20, 2026, https://review.firstround.com/airtables-path-to-product-market-fit-lessons-for-building-horizontal-products/. Airtable co-founder Andrew Ofstad describes beginning horizontally and becoming more targeted and opinionated in go-to-market over time.

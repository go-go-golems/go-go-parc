---
title: "Textbook: Using the CSS Visual Diff JavaScript API to Validate Website Implementations"
aliases:
  - Using the CSS Visual Diff JavaScript API
  - CSS Visual Diff JS API for Designers
  - Website implementation validation with css-visual-diff scripts
  - Pixel-accurate website validation with JavaScript verbs
tags:
  - textbook
  - article
  - css-visual-diff
  - javascript-api
  - visual-regression
  - frontend
  - design-systems
  - browser-automation
  - pixel-accuracy
status: active
type: article
created: 2026-04-25
repo: /home/manuel/workspaces/2026-04-21/hair-v2/css-visual-diff
ticket: CSSVD-JSAPI-PIXEL-WORKFLOWS
---

# Using the CSS Visual Diff JavaScript API to Validate Website Implementations

This chapter teaches how to use the new `css-visual-diff` JavaScript API as a practical validation loop for website implementation work. The reader I have in mind is a designer, design engineer, frontend engineer, or coding agent operator who needs to answer a concrete question: did the website we built match the visual intent closely enough, and if it did not, what changed?

The API is not a screenshot toy. A screenshot can tell you that something looks different, but it rarely tells you why. The JavaScript API is built around evidence: rendered pixels, DOM selectors, computed styles, element bounds, text, attributes, reports, and catalogs. The trick is learning when to use the quick path and when to drop down into the primitives.

> [!summary]
> This workflow has three useful modes:
> 1. **Quick visual comparison** with `cvd.compare.region(...)` when you want screenshots, pixel diff PNGs, JSON, and Markdown with minimal ceremony.
> 2. **Collect-and-analyze comparison** with `locator.collect(...)` and `cvd.compare.selections(...)` when you want JavaScript policy logic over browser facts.
> 3. **Catalog workflows** with `cvd.catalog.create(...)` and `catalog.record(...)` when you compare many regions and need one durable manifest/index for review.

## 1. What website validation actually means

When a designer says “this page is off,” they often mean several different things at once. The text may be correct but the font weight is wrong. The spacing may be off by eight pixels. The button may have the right color but the wrong border radius. The layout may be vertically shifted because the hero image loaded at a different height. A pixel diff can detect all of those as visual changes, but it cannot classify them on its own.

A good validation loop therefore needs multiple kinds of evidence:

| Evidence | Question it answers | Example |
|---|---|---|
| Existence | Did the intended element render? | `#cta` exists. |
| Visibility | Can the user see it? | The button has non-zero bounds and visible styles. |
| Bounds | Did layout and spacing match? | Width changed from `120` to `136`. |
| Text | Did the content match? | “Book now” became “Reserve now”. |
| Computed styles | Did CSS produce the right result? | `font-size` is `18px`, not `16px`. |
| Attributes | Did state/classes/data hooks match? | `class="secondary"` instead of `primary`. |
| Pixels | What did the browser actually paint? | `7.1%` of pixels changed. |
| Artifacts | Can a reviewer inspect evidence? | `diff_comparison.png`, `compare.md`, `manifest.json`. |

The new JavaScript API is designed around this table. It does not force you to choose between pixels and facts. It lets you collect both, then decide what matters for the page you are validating.

The most important concept is that a validation script should answer a precise visual question. Not “is the page okay?” but “does the archive content region match the reference implementation at desktop width?” or “did the primary CTA keep its typography, bounds, and visible state after the CSS refactor?” Precise questions lead to precise selectors, evidence, and reports.

## 2. The mental model: pages, locators, collected selections, comparisons

The API has a small vocabulary. Learn these nouns first.

| Object | What it represents | Typical method |
|---|---|---|
| `Browser` | A Chromium browser service. | `await cvd.browser()` |
| `Page` | One loaded browser page. | `await browser.page(url, options)` |
| `Locator` | A selector on one loaded page. | `page.locator("#cta")` |
| `CollectedSelection` | Browser facts for one selector at one moment. | `await locator.collect()` |
| `SelectionComparison` | Analysis of two collected selections. | `await cvd.compare.selections(left, right)` |
| `Catalog` | Durable collection of results/comparisons. | `cvd.catalog.create(...)` |

A locator is live. It is a handle to a selector on a page. A collected selection is not live. It is a snapshot of evidence. That distinction is the key to reliable validation.

Think of it like this:

```text
Page:                 the browser is here
Locator:              look at this selector on this page
CollectedSelection:   here is what the browser said at 14:03:12
SelectionComparison:  here is how the left evidence differs from the right evidence
Catalog:              here is the durable review packet
```

This model avoids a common mistake in visual tooling: repeatedly querying a changing browser page while trying to compare it. The API encourages you to collect once, compare stable data, and then write reports/artifacts from that data.

## 3. The quick path: compare one region

The quickest useful validation is `cvd.compare.region(...)`. Use it when you have two pages and one selector to compare.

```js
async function compareCTA(leftUrl, rightUrl, outDir) {
  const cvd = require("css-visual-diff")
  const browser = await cvd.browser()
  let leftPage, rightPage

  try {
    leftPage = await browser.page(leftUrl, {
      viewport: { width: 1280, height: 720 },
      waitMs: 250,
      name: "reference",
    })

    rightPage = await browser.page(rightUrl, {
      viewport: { width: 1280, height: 720 },
      waitMs: 250,
      name: "implementation",
    })

    const comparison = await cvd.compare.region({
      name: "primary-cta",
      left: leftPage.locator("[data-testid='primary-cta']"),
      right: rightPage.locator("[data-testid='primary-cta']"),
      outDir,
      threshold: 30,
      styleProps: [
        "font-family",
        "font-size",
        "font-weight",
        "line-height",
        "color",
        "background-color",
        "border-radius",
        "padding",
      ],
      attributes: ["class", "aria-label", "data-state"],
    })

    await comparison.artifacts.write(outDir, ["json", "markdown"])
    return comparison.summary()
  } finally {
    if (leftPage) await leftPage.close()
    if (rightPage) await rightPage.close()
    await browser.close()
  }
}
```

The important line is not complicated:

```js
const comparison = await cvd.compare.region({ left, right, outDir })
```

That call does a lot of work:

```text
1. Validate that left and right are real locator handles.
2. Collect rich browser facts for the left selector.
3. Capture the left region screenshot.
4. Collect rich browser facts for the right selector.
5. Capture the right region screenshot.
6. Normalize screenshots to the same size.
7. Compute pixel differences.
8. Write diff PNG artifacts.
9. Return a queryable SelectionComparison handle.
```

The default `inspect` mode is `rich`. That means the API collects useful browser facts up front, not just pixels. The result can answer questions like:

```js
comparison.pixel.summary()
comparison.bounds.diff()
comparison.styles.diff(["font-size", "line-height"])
comparison.attributes.diff(["class"])
```

For a designer or frontend engineer, this is the difference between “there is a 4% visual diff” and “the diff is mostly explained by font size, padding, and border radius.”

## 4. What artifacts mean

A visual comparison should leave evidence behind. When `cvd.compare.region(...)` receives an `outDir`, it writes image artifacts:

```text
left_region.png
right_region.png
diff_only.png
diff_comparison.png
```

When you call:

```js
await comparison.artifacts.write(outDir, ["json", "markdown"])
```

it writes:

```text
compare.json
compare.md
```

Each file has a different purpose.

| File | Purpose |
|---|---|
| `left_region.png` | Shows the reference/baseline region. |
| `right_region.png` | Shows the implementation/current region. |
| `diff_only.png` | Highlights changed pixels. |
| `diff_comparison.png` | Places left, right, and diff side by side. |
| `compare.json` | Stores full machine-readable comparison data. |
| `compare.md` | Gives a compact human-readable report. |

The side-by-side image is usually the first artifact to show a designer. The JSON file is usually the first artifact to inspect in automation. The Markdown report is the bridge between the two.

## 5. Reading the comparison object

A `SelectionComparison` handle is behavior-rich. It is not just JSON. You query it through methods and properties:

```js
const summary = comparison.summary()
const full = comparison.toJSON()
const pixel = comparison.pixel.summary()
const bounds = comparison.bounds.diff()
const typography = comparison.styles.diff(["font-size", "font-weight", "line-height"])
const classes = comparison.attributes.diff(["class"])
const report = comparison.report.markdown()
```

The `summary()` method is for command output. It is intentionally compact:

```js
{
  schemaVersion: "cssvd.selectionComparison.v1",
  name: "primary-cta",
  boundsChanged: true,
  textChanged: false,
  styleChanges: 3,
  attributeChanges: 1,
  artifactCount: 2,
  pixel: {
    changedPercent: 7.13,
    changedPixels: 713,
    totalPixels: 10000
  }
}
```

The `toJSON()` method is for durable storage and deeper analysis. It contains left/right summaries, full style diffs, attribute diffs, text diff, bounds diff, pixel stats, and artifact descriptors.

The rule is simple:

- Return `summary()` from a CLI verb when humans or CI need a concise row.
- Write `toJSON()` when you want a complete record.
- Use filtered methods like `styles.diff([...])` when you are writing custom policy.

## 6. The primitive path: collect first, then analyze

The quick path is excellent when you want standard evidence. The primitive path is better when the validation policy belongs to your project.

Imagine a designer says: “I do not care if the button moved a little in responsive layout, but I care deeply that the typography and semantic state match.” You can encode that directly.

```js
async function validateButtonPolicy(leftPage, rightPage) {
  const cvd = require("css-visual-diff")

  const collectOptions = {
    inspect: "rich",
    styles: [
      "font-family",
      "font-size",
      "font-weight",
      "line-height",
      "letter-spacing",
      "color",
      "background-color",
    ],
    attributes: ["class", "aria-disabled", "data-state"],
  }

  const left = await leftPage.locator("[data-testid='primary-cta']").collect(collectOptions)
  const right = await cvd.collect.selection(
    rightPage.locator("[data-testid='primary-cta']"),
    collectOptions,
  )

  const comparison = await cvd.compare.selections(left, right, {
    name: "primary-cta-policy",
    styleProps: collectOptions.styles,
    attributes: collectOptions.attributes,
  })

  const typography = comparison.styles.diff([
    "font-family",
    "font-size",
    "font-weight",
    "line-height",
    "letter-spacing",
  ])

  const semanticState = comparison.attributes.diff(["aria-disabled", "data-state"])

  return {
    ok: typography.length === 0 && semanticState.length === 0,
    typography,
    semanticState,
    allStyleChanges: comparison.styles.diff(),
    bounds: comparison.bounds.diff(),
  }
}
```

This script is not merely comparing two pages. It is expressing a design policy. It says typography and semantic state are blocking issues; layout shifts are recorded but not necessarily failing.

That is the power of exposing primitives. The tool does not have to know your policy. It has to give you reliable evidence and convenient query methods.

## 7. Choosing selectors like a designer

A visual diff tool is only as good as its selectors. A brittle selector turns every validation run into a debugging session. A good selector names the design intent.

Prefer selectors like:

```css
[data-testid='primary-cta']
[data-component='booking-card']
main [data-page='archive']
```

Be careful with selectors like:

```css
body > div:nth-child(2) > div > button
.MuiButton-root.css-17abcde
#root > *
```

Sometimes a broad selector is useful. For example, `#root > *` may be the right selector when comparing a whole rendered app shell. But broad selectors should be a deliberate choice, not a fallback because the component lacks test hooks.

A good practice is to define a small target map in your script:

```js
const sections = [
  { name: "hero", selector: "[data-section='hero']" },
  { name: "search", selector: "[data-section='search']" },
  { name: "results", selector: "[data-section='results']" },
  { name: "footer", selector: "footer" },
]
```

This map becomes shared language between design and engineering. “The results section changed by 3%” is much easier to discuss than “some part of the page changed.”

## 8. Validating multiple sections

A real page is rarely one region. You may want to validate a hero, navigation bar, card grid, CTA, and footer. JavaScript is the workflow language; you do not need a separate workflow builder.

```js
async function compareSections(leftUrl, rightUrl, outDir) {
  const cvd = require("css-visual-diff")
  const browser = await cvd.browser()
  let leftPage, rightPage

  const sections = [
    { name: "hero", selector: "[data-section='hero']" },
    { name: "cards", selector: "[data-section='cards']" },
    { name: "cta", selector: "[data-testid='primary-cta']" },
  ]

  try {
    leftPage = await browser.page(leftUrl, { viewport: cvd.viewport.desktop(), waitMs: 250 })
    rightPage = await browser.page(rightUrl, { viewport: cvd.viewport.desktop(), waitMs: 250 })

    const results = []
    for (const section of sections) {
      const sectionDir = `${outDir}/${section.name}`
      const comparison = await cvd.compare.region({
        name: section.name,
        left: leftPage.locator(section.selector),
        right: rightPage.locator(section.selector),
        outDir: sectionDir,
      })
      await comparison.artifacts.write(sectionDir, ["json", "markdown"])
      results.push(comparison.summary())
    }

    return {
      sectionCount: results.length,
      changed: results.filter(r => r.pixel && r.pixel.changedPercent > 0),
      results,
    }
  } finally {
    if (leftPage) await leftPage.close()
    if (rightPage) await rightPage.close()
    await browser.close()
  }
}
```

This is intentionally ordinary JavaScript: an array, a loop, a result list. The API supplies strong primitives; the script supplies orchestration.

## 9. Recording comparisons in a catalog

When there are many sections, individual artifact folders are not enough. You need one index. That is what catalogs are for.

```js
async function comparePageIntoCatalog(leftUrl, rightUrl, outDir) {
  const cvd = require("css-visual-diff")
  const browser = await cvd.browser()
  let leftPage, rightPage

  const catalog = cvd.catalog.create({
    title: "Homepage visual validation",
    outDir,
    artifactRoot: "artifacts",
  })

  const sections = [
    { name: "hero", selector: "[data-section='hero']" },
    { name: "cta", selector: "[data-testid='primary-cta']" },
  ]

  try {
    leftPage = await browser.page(leftUrl, { viewport: cvd.viewport.desktop(), waitMs: 250 })
    rightPage = await browser.page(rightUrl, { viewport: cvd.viewport.desktop(), waitMs: 250 })

    for (const section of sections) {
      const artifactDir = catalog.artifactDir(section.name)
      const comparison = await cvd.compare.region({
        name: section.name,
        left: leftPage.locator(section.selector),
        right: rightPage.locator(section.selector),
        outDir: artifactDir,
      })
      await comparison.artifacts.write(artifactDir, ["json", "markdown"])
      catalog.record(comparison, {
        slug: section.name,
        name: section.name,
        url: leftUrl,
        selector: section.selector,
      })
    }

    const manifestPath = await catalog.writeManifest()
    const indexPath = await catalog.writeIndex()
    return { manifestPath, indexPath, summary: catalog.summary() }
  } finally {
    if (leftPage) await leftPage.close()
    if (rightPage) await rightPage.close()
    await browser.close()
  }
}
```

The catalog writes:

```text
manifest.json
index.md
artifacts/<section>/left_region.png
artifacts/<section>/right_region.png
artifacts/<section>/diff_only.png
artifacts/<section>/diff_comparison.png
artifacts/<section>/compare.json
artifacts/<section>/compare.md
```

The manifest is for tools. The index is for people. The artifact folders are for evidence. This is the shape you want for design review, CI attachments, and long-running quality tracking.

## 10. Designer-friendly interpretation

A designer does not necessarily want to read JSON. A designer wants answers in design language:

- Did the element exist?
- Did it occupy the same space?
- Did the text change?
- Did the typography change?
- Did the visual rendering change?
- Where can I see the before/after/diff?

The `SelectionComparison` object maps cleanly to that language.

```js
function designerSummary(comparison) {
  const pixel = comparison.pixel.summary()
  const bounds = comparison.bounds.diff()
  const typography = comparison.styles.diff(["font-size", "font-weight", "line-height", "font-family"])
  const color = comparison.styles.diff(["color", "background-color"])

  return {
    changedPercent: pixel ? pixel.changedPercent : 0,
    layoutChanged: bounds.changed,
    typographyChanged: typography.length > 0,
    colorChanged: color.length > 0,
    report: comparison.report.markdown(),
  }
}
```

This is not a replacement for looking at the screenshot. It is a guide for looking at the screenshot. If the diff image shows changes around the button, and the structured data says `font-size`, `padding`, and `border-radius` changed, the review conversation starts from evidence instead of guesswork.

## 11. CI-friendly interpretation

A CI check needs different output. It should produce a clear pass/fail summary and leave artifacts for humans.

```js
function classify(comparison) {
  const pixel = comparison.pixel.summary()
  const criticalStyles = comparison.styles.diff([
    "font-family",
    "font-size",
    "font-weight",
    "line-height",
  ])
  const bounds = comparison.bounds.diff()

  const changedPercent = pixel ? pixel.changedPercent : 0
  const fail = changedPercent > 2.0 || criticalStyles.length > 0

  return {
    ok: !fail,
    changedPercent,
    criticalStyleChanges: criticalStyles,
    boundsChanged: bounds.changed,
  }
}
```

The threshold here is a policy choice. A design-system component may require a strict threshold. A marketing page may allow small pixel changes if typography and content are stable. The API does not decide this for you; it gives you the data to decide.

## 12. Authoring workflow: how to use this during implementation

A productive authoring loop looks like this:

1. Start with one region, not the whole page.
2. Use `cvd.compare.region(...)` to get screenshots and a pixel diff.
3. Inspect `comparison.styles.diff()` and `comparison.bounds.diff()` to classify the cause.
4. Fix CSS/layout/content.
5. Re-run the same command.
6. When the region is stable, add it to a catalog workflow.
7. Repeat for the next region.

The loop is intentionally small. Do not start by comparing the entire application if you are trying to tune one card. Compare the card. Do not start with ten selectors if the first selector is unstable. Validate one selector, then expand.

A useful command while authoring is the public example:

```bash
css-visual-diff verbs --repository examples/verbs examples compare region \
  http://localhost:3000/reference \
  http://localhost:3000/current \
  '[data-testid="primary-cta"]' \
  /tmp/cssvd-cta \
  --output json
```

Open:

```text
/tmp/cssvd-cta/diff_comparison.png
/tmp/cssvd-cta/compare.md
```

Then change the implementation and run it again.

## 13. What to do when validation fails

Failures should be debugged from the outside in.

### Step 1: Did the page load?

If the command fails before selector evaluation, check URL, local dev server, wait time, and viewport. Increase `waitMs` if the app hydrates slowly.

### Step 2: Did the selector match?

Use a locator directly:

```js
const status = await page.locator("#cta").status()
return status
```

If `exists` is false, the problem is not visual diffing. It is selector choice, route state, app rendering, or preparation.

### Step 3: Was the element visible?

A selector can exist but be invisible. Look at bounds and styles:

```js
const locator = page.locator("#cta")
return {
  visible: await locator.visible(),
  bounds: await locator.bounds(),
  styles: await locator.computedStyle(["display", "visibility", "opacity"]),
}
```

### Step 4: Did pixels change because content changed?

Text changes are often the simplest explanation:

```js
comparison.toJSON().text
```

If text changed, the pixel diff may be correct and the issue is content, not CSS.

### Step 5: Did pixels change because layout changed?

Look at:

```js
comparison.bounds.diff()
```

A width/height delta often explains large areas of changed pixels.

### Step 6: Did pixels change because styles changed?

Look at filtered style diffs:

```js
comparison.styles.diff(["font-size", "line-height", "padding", "border-radius", "background-color"])
```

This usually points directly at the CSS rule or token that needs attention.

## 14. Common anti-patterns

### Anti-pattern: comparing the whole page too early

Whole-page screenshots are useful for final review but noisy during authoring. Start with the region you are implementing. Expand later.

### Anti-pattern: using brittle generated class names

Generated CSS class names often change for reasons unrelated to design. Prefer stable `data-testid`, `data-section`, semantic IDs, or project-specific hooks.

### Anti-pattern: returning behavior-rich handles from verbs

Do not return `comparison` directly from a CLI verb. Return `comparison.summary()` or `comparison.toJSON()`. Handles are for script logic; lowered values are for output.

### Anti-pattern: treating pixel percent as the whole truth

A `0.5%` diff can be serious if it changes a critical icon. A `10%` diff can be acceptable if it is expected content length. Always pair pixel diffs with text, bounds, and style evidence.

### Anti-pattern: skipping artifacts

If a validation result matters, write artifacts. A JSON row in CI is useful, but a reviewer needs `diff_comparison.png` and `compare.md`.

## 15. A complete project-local verb

A practical project can keep a file like `verbs/visual-checks.js`:

```js
async function validateHomepage(leftUrl, rightUrl, outDir) {
  const cvd = require("css-visual-diff")
  const browser = await cvd.browser()
  const catalog = cvd.catalog.create({
    title: "Homepage Validation",
    outDir,
    artifactRoot: "artifacts",
  })

  const sections = [
    { name: "hero", selector: "[data-section='hero']" },
    { name: "primary-cta", selector: "[data-testid='primary-cta']" },
    { name: "footer", selector: "footer" },
  ]

  let leftPage, rightPage
  try {
    leftPage = await browser.page(leftUrl, { viewport: cvd.viewport.desktop(), waitMs: 500 })
    rightPage = await browser.page(rightUrl, { viewport: cvd.viewport.desktop(), waitMs: 500 })

    const summaries = []
    for (const section of sections) {
      const artifactDir = catalog.artifactDir(section.name)
      const comparison = await cvd.compare.region({
        name: section.name,
        left: leftPage.locator(section.selector),
        right: rightPage.locator(section.selector),
        outDir: artifactDir,
        styleProps: ["font-size", "line-height", "color", "background-color", "padding"],
        attributes: ["class", "aria-label"],
      })
      await comparison.artifacts.write(artifactDir, ["json", "markdown"])
      catalog.record(comparison, {
        slug: section.name,
        name: section.name,
        url: leftUrl,
        selector: section.selector,
      })
      summaries.push(comparison.summary())
    }

    const manifestPath = await catalog.writeManifest()
    const indexPath = await catalog.writeIndex()

    return {
      ok: summaries.every(s => !s.pixel || s.pixel.changedPercent < 2.0),
      manifestPath,
      indexPath,
      summaries,
    }
  } finally {
    if (leftPage) await leftPage.close()
    if (rightPage) await rightPage.close()
    await browser.close()
  }
}

__verb__("validateHomepage", {
  parents: ["site"],
  short: "Validate homepage visual implementation against a reference",
  fields: {
    leftUrl: { argument: true, required: true },
    rightUrl: { argument: true, required: true },
    outDir: { argument: true, required: true },
  },
})
```

Run it:

```bash
css-visual-diff verbs --repository ./verbs site validate-homepage \
  http://localhost:3000/reference \
  http://localhost:3000/current \
  /tmp/homepage-validation \
  --output json
```

The resulting directory is a review packet. It has a catalog index, a manifest, per-section screenshots, pixel diffs, JSON comparisons, and Markdown reports.

## 16. How designers and engineers should collaborate around the artifacts

The artifacts support a shared review process.

1. The engineer runs the validation script.
2. The designer opens `index.md` and the relevant `diff_comparison.png` files.
3. The engineer checks `compare.json` or `compare.md` for computed style and bounds diffs.
4. The team classifies each difference as expected, acceptable, or a defect.
5. The engineer updates CSS/layout/content and reruns the same script.

This workflow is better than screenshot ping-pong because it preserves evidence. The question is no longer “does this look off to you?” The question becomes “the CTA differs by 3.2%, with font size and padding changes; is that intentional?”

## 17. Working rules

- Start with one selector and one viewport.
- Prefer stable semantic selectors over generated class names.
- Use `cvd.compare.region(...)` first; drop to `collect` and `compare.selections` when you need policy logic.
- Always close browsers in `finally` blocks.
- Return `summary()` for compact CLI output and write `toJSON()` / artifacts for durable evidence.
- Use catalogs when validating more than one section.
- Treat pixel percent as a signal, not a verdict.
- Keep validation scripts in the project repository so the visual contract evolves with the UI.

## 18. What this API gives you now

The new JavaScript API lets a project create a pixel-accuracy loop without inventing its own browser harness. It gives you live pages, strict locators, rich collection, deterministic comparisons, PNG artifacts, Markdown reports, JSON data, and catalogs. It also gives you enough JavaScript flexibility to encode project-specific policy.

That combination is the point. A designer can get visual evidence. A frontend engineer can get computed CSS and bounds. A CI system can get structured JSON. A project can keep its own registry of pages and selectors in userland. The Go side handles the hard browser and image work; JavaScript handles orchestration and judgment.

## 19. Packaging validation scripts into a reusable project CLI

A one-off validation script is useful during experimentation. A reusable project CLI is useful every day. The difference is not only polish; it is where the validation workflow lives in the development loop. If a script is hidden in a scratch directory, only the person who wrote it will run it. If it is packaged as a project command with stable arguments, documented outputs, and predictable artifact locations, it becomes part of how the team builds the website.

The goal is to turn this:

```bash
node ./scratch/compare-cta.js
```

into this:

```bash
npm run visual:homepage -- --left http://localhost:4100 --right http://localhost:4200
```

or this:

```bash
css-visual-diff verbs --repository ./visual-verbs site validate-homepage \
  http://localhost:4100 \
  http://localhost:4200 \
  ./artifacts/visual/homepage \
  --output json
```

The second form is more than a command. It is a contract. It tells every developer, designer, CI job, and coding agent how visual validation is supposed to be run.

### 19.1 The three layers of a reusable visual CLI

A good reusable setup has three layers:

```text
project command       npm script, Makefile target, CI step, or devctl command
        ↓
css-visual-diff verb  stable CLI arguments and structured output
        ↓
JS validation module  selectors, viewports, comparisons, catalog writing
```

Each layer has a different job.

| Layer | Responsibility | Example |
|---|---|---|
| Project command | Make the workflow discoverable and easy to run. | `npm run visual:homepage` |
| `css-visual-diff` verb | Provide a typed command interface and machine-readable output. | `site validate-homepage <leftUrl> <rightUrl> <outDir>` |
| JS validation module | Encode project-specific visual policy. | Compare hero, CTA, cards, footer. |

This separation matters because the JavaScript API is intentionally flexible. Flexibility is good inside the validation module, where the project encodes selectors and policy. It is less good at the command boundary. The command boundary should be boring: arguments in, artifacts out, JSON summary returned.

### 19.2 Put visual verbs in the repository

The first packaging decision is where the scripts live. A good default is:

```text
visual-verbs/
  homepage.js
  components.js
  shared.js
```

or, if the project already has a tooling directory:

```text
tools/visual/
  verbs/
    homepage.js
    checkout.js
    shared.js
```

The important property is that the scripts are versioned with the website. Visual validation is not external QA glue. It is part of the implementation contract. When a component is renamed, the selector changes in the same pull request. When a new breakpoint is added, the validation command can gain a new viewport. When a design decision intentionally changes spacing, the artifact threshold or style policy can change with the code.

A repository-local verb can start very small:

```js
// visual-verbs/homepage.js

async function validateHomepage(leftUrl, rightUrl, outDir) {
  const cvd = require("css-visual-diff")
  const browser = await cvd.browser()
  const catalog = cvd.catalog.create({
    title: "Homepage visual validation",
    outDir,
    artifactRoot: "artifacts",
  })

  const sections = [
    { name: "hero", selector: "[data-section='hero']" },
    { name: "primary-cta", selector: "[data-testid='primary-cta']" },
    { name: "footer", selector: "footer" },
  ]

  const summaries = []
  let leftPage, rightPage

  try {
    leftPage = await browser.page(leftUrl, { viewport: cvd.viewport.desktop(), waitMs: 500 })
    rightPage = await browser.page(rightUrl, { viewport: cvd.viewport.desktop(), waitMs: 500 })

    for (const section of sections) {
      const artifactDir = catalog.artifactDir(section.name)
      const comparison = await cvd.compare.region({
        name: section.name,
        left: leftPage.locator(section.selector),
        right: rightPage.locator(section.selector),
        outDir: artifactDir,
        styleProps: ["font-size", "line-height", "color", "background-color", "padding"],
        attributes: ["class", "aria-label"],
      })

      await comparison.artifacts.write(artifactDir, ["json", "markdown"])
      catalog.record(comparison, {
        slug: section.name,
        name: section.name,
        url: leftUrl,
        selector: section.selector,
      })
      summaries.push(classify(section, comparison))
    }

    const manifestPath = await catalog.writeManifest()
    const indexPath = await catalog.writeIndex()

    return {
      ok: summaries.every(s => s.ok),
      manifestPath,
      indexPath,
      summaries,
    }
  } finally {
    if (leftPage) await leftPage.close()
    if (rightPage) await rightPage.close()
    await browser.close()
  }
}

function classify(section, comparison) {
  const pixel = comparison.pixel.summary()
  const changedPercent = pixel ? pixel.changedPercent : 0
  const criticalStyles = comparison.styles.diff(["font-size", "line-height"])

  return {
    name: section.name,
    ok: changedPercent < 2.0 && criticalStyles.length === 0,
    changedPercent,
    criticalStyles,
    bounds: comparison.bounds.diff(),
  }
}

__verb__("validateHomepage", {
  parents: ["site"],
  short: "Validate homepage visual implementation against a reference URL",
  fields: {
    leftUrl: { argument: true, required: true },
    rightUrl: { argument: true, required: true },
    outDir: { argument: true, required: true },
  },
})
```

The verb definition is the packaging boundary. It turns an ordinary JavaScript function into a reusable command. The function can still use normal JavaScript internally: arrays, loops, helper functions, classification logic, shared modules. But callers do not need to know the internals. They only need the command name and arguments.

### 19.3 Wrap the verb with project-native commands

The `css-visual-diff verbs` command is the universal execution mechanism. But most teams do not want to type the full command every time. They want project-native shortcuts.

In a Node frontend project, add `package.json` scripts:

```json
{
  "scripts": {
    "visual:homepage": "css-visual-diff verbs --repository ./visual-verbs site validate-homepage",
    "visual:homepage:local": "npm run visual:homepage -- http://localhost:4100 http://localhost:4200 ./artifacts/visual/homepage --output json"
  }
}
```

Now the daily command becomes:

```bash
npm run visual:homepage:local
```

In a Go or polyglot repository, a `Makefile` target may be better:

```makefile
visual-homepage:
	css-visual-diff verbs --repository ./visual-verbs site validate-homepage \
		$(LEFT_URL) $(RIGHT_URL) $(OUT_DIR) --output json
```

Run it with:

```bash
make visual-homepage \
  LEFT_URL=http://localhost:4100 \
  RIGHT_URL=http://localhost:4200 \
  OUT_DIR=./artifacts/visual/homepage
```

The wrapper command should not hide all options. It should provide good defaults while still allowing explicit URLs and output paths. Local development, CI, and design-review runs often use the same verb with different endpoints.

### 19.4 Make artifacts predictable

A reusable CLI must write to predictable locations. If every run writes to a random temp directory, nobody will know where to look. If every run overwrites the same directory without warning, useful evidence disappears.

A good default layout is:

```text
artifacts/
  visual/
    homepage/
      latest/
        manifest.json
        index.md
        artifacts/
          hero/
          primary-cta/
          footer/
      2026-04-25T14-30-00Z/
        manifest.json
        index.md
        artifacts/
          ...
```

For local authoring, `latest` is convenient. For CI, a timestamped or build-numbered directory is better. A wrapper can choose the output path:

```bash
OUT_DIR="./artifacts/visual/homepage/latest"
npm run visual:homepage -- "$LEFT_URL" "$RIGHT_URL" "$OUT_DIR" --output json
```

A CI job can use:

```bash
OUT_DIR="./artifacts/visual/homepage/${GITHUB_RUN_ID}"
```

The validation script itself should not need to know whether it is running locally or in CI. It receives `outDir`, writes catalog files and comparison artifacts there, and returns a summary.

### 19.5 Use JSON output as the automation contract

Human reviewers want images and Markdown. Automation wants JSON. A reusable CLI should always return a compact structured result.

A good result shape is:

```json
{
  "ok": false,
  "manifestPath": "./artifacts/visual/homepage/latest/manifest.json",
  "indexPath": "./artifacts/visual/homepage/latest/index.md",
  "summaries": [
    {
      "name": "hero",
      "ok": true,
      "changedPercent": 0.2,
      "criticalStyles": []
    },
    {
      "name": "primary-cta",
      "ok": false,
      "changedPercent": 4.7,
      "criticalStyles": [
        { "property": "font-size", "left": "16px", "right": "14px" }
      ]
    }
  ]
}
```

This output is small enough for CI logs and precise enough for other tools to consume. The detailed evidence remains in the artifact directory.

The command boundary therefore has two products:

```text
stdout JSON:   decision and pointers
artifact dir:  evidence and review material
```

This is the right split. Do not try to put every pixel and every style diff into CI logs. Do not force humans to parse JSON to see what changed.

### 19.6 Build it into the core development loop

Once the command is stable, it can become part of the normal implementation cycle.

A frontend engineer working on a page might run:

```bash
npm run dev:reference -- --port 4100
npm run dev:current -- --port 4200
npm run visual:homepage -- http://localhost:4100 http://localhost:4200 ./artifacts/visual/homepage/latest --output json
```

The loop is:

```text
edit CSS/component
refresh dev server
run visual command
open index.md and diff_comparison.png
inspect JSON summary for causes
fix implementation
run again
```

This is very different from saving screenshots manually. The command makes the comparison repeatable. The artifact directory makes the evidence inspectable. The JSON summary makes the result scriptable. The catalog makes multi-section review navigable.

For coding-agent workflows, the command becomes even more important. An agent can be instructed:

```text
After changing the homepage CSS, run npm run visual:homepage:local.
If it fails, inspect the JSON summary and the Markdown reports before editing again.
Do not claim the implementation matches until the visual command passes or the remaining differences are documented.
```

The reusable CLI gives the agent a concrete feedback loop. Instead of asking the model to judge a screenshot vaguely, the project gives it structured evidence: changed pixel percent, style diffs, bounds diffs, and artifact paths.

### 19.7 Add fast and full commands

Not every run needs the same coverage. A mature project usually needs at least two commands:

```json
{
  "scripts": {
    "visual:quick": "css-visual-diff verbs --repository ./visual-verbs site validate-homepage",
    "visual:full": "css-visual-diff verbs --repository ./visual-verbs site validate-all-pages"
  }
}
```

The quick command should be optimized for local authoring. It may validate one page, one viewport, and a small set of high-value selectors. It should finish quickly enough that developers actually run it.

The full command should be optimized for confidence. It may validate several pages, multiple viewports, and more sections. It belongs in CI or pre-release checks.

The distinction is important. If the only visual command takes five minutes, developers will avoid it while editing. If the only visual command takes ten seconds but covers only the hero, CI will miss regressions. The core development loop needs both fast feedback and deeper validation.

### 19.8 CI integration

A CI job should run the same reusable command that developers run locally. The only difference is endpoint setup and artifact upload.

A typical CI shape is:

```yaml
- name: Start reference app
  run: npm run start:reference -- --port 4100 &

- name: Start PR app
  run: npm run start:current -- --port 4200 &

- name: Run visual validation
  run: |
    css-visual-diff verbs --repository ./visual-verbs site validate-homepage \
      http://localhost:4100 \
      http://localhost:4200 \
      ./artifacts/visual/homepage/${{ github.run_id }} \
      --output json | tee visual-result.json

- name: Upload visual artifacts
  uses: actions/upload-artifact@v4
  with:
    name: visual-homepage
    path: ./artifacts/visual/homepage/${{ github.run_id }}
```

The policy decision is whether the command itself exits non-zero when `ok` is false, or whether CI parses `visual-result.json` and decides. Both patterns can work. For early adoption, it is often better to upload artifacts and warn before making visual validation a hard gate. Once the signal is trusted, the project can fail CI on blocker differences.

The important rule is this:

> CI should not invent a separate visual workflow. It should run the project-local visual CLI.

That keeps local and remote behavior aligned.

### 19.9 Packaging shared helpers

As soon as there are several visual verbs, shared code should move into helper modules. For example:

```text
visual-verbs/
  shared.js
  homepage.js
  product-page.js
  checkout.js
```

`shared.js` might define:

```js
function classifyComparison(comparison, policy) {
  const pixel = comparison.pixel.summary()
  const changedPercent = pixel ? pixel.changedPercent : 0
  const criticalStyles = comparison.styles.diff(policy.criticalStyles || [])
  const criticalAttributes = comparison.attributes.diff(policy.criticalAttributes || [])

  return {
    ok:
      changedPercent <= (policy.maxPixelChange ?? 2.0) &&
      criticalStyles.length === 0 &&
      criticalAttributes.length === 0,
    changedPercent,
    criticalStyles,
    criticalAttributes,
    bounds: comparison.bounds.diff(),
  }
}

function section(name, selector, policy = {}) {
  return { name, selector, policy }
}

module.exports = { classifyComparison, section }
```

Then page-specific verbs stay declarative:

```js
const { classifyComparison, section } = require("./shared")

const sections = [
  section("hero", "[data-section='hero']", { maxPixelChange: 1.0 }),
  section("primary-cta", "[data-testid='primary-cta']", {
    maxPixelChange: 0.5,
    criticalStyles: ["font-size", "line-height", "background-color"],
  }),
]
```

This is the point where the validation setup starts to feel like a real project tool rather than a script. Shared classification logic gives consistent results across pages. Page files remain readable. Designers can review the section lists and policy values without wading through browser setup code.

### 19.10 A CLI is also documentation

A packaged command documents the project’s visual contract. If a new engineer asks “how do I know whether this page still matches the design?”, the answer should be a command, not tribal knowledge.

Good command names matter:

```text
site validate-homepage
site validate-checkout
components validate-buttons
components validate-cards
```

Good output paths matter:

```text
./artifacts/visual/homepage/latest/index.md
```

Good help text matters:

```js
__verb__("validateHomepage", {
  parents: ["site"],
  short: "Validate homepage visual implementation against a reference URL",
  long: `Compare key homepage sections between a reference URL and an implementation URL.
Writes a catalog with per-section screenshots, pixel diffs, JSON comparison data,
and Markdown reports. Intended for local CSS authoring and CI artifact generation.`,
  fields: {
    leftUrl: { argument: true, required: true, help: "Reference/baseline URL" },
    rightUrl: { argument: true, required: true, help: "Implementation/current URL" },
    outDir: { argument: true, required: true, help: "Artifact output directory" },
  },
})
```

A command with clear help text becomes discoverable through the CLI. It also gives coding agents better context. The command description tells the agent what the tool does, what inputs it expects, and what artifacts it writes.

### 19.11 The development loop as an architecture

The final architecture is not just JavaScript files. It is a loop:

```text
Developer changes UI code
        ↓
Project command runs css-visual-diff verb
        ↓
Verb loads reference/current pages
        ↓
JS API compares meaningful regions
        ↓
Catalog writes review packet
        ↓
JSON summary classifies differences
        ↓
Developer/designer/agent fixes or approves
```

This loop should be cheap enough for local development and reliable enough for CI. That is why packaging matters. The JS API provides the primitives, but the reusable CLI turns them into a habit.

A good project-local visual CLI has these properties:

- one obvious command for each important page or component family,
- stable arguments for reference URL, implementation URL, and artifact directory,
- predictable output paths,
- JSON summaries for automation,
- Markdown and PNG artifacts for review,
- shared classification helpers,
- local and CI usage of the same command,
- enough help text that a new engineer or coding agent can run it correctly.

When those properties are in place, visual validation stops being an occasional QA event. It becomes part of the core development loop: edit, run, inspect, fix, repeat.

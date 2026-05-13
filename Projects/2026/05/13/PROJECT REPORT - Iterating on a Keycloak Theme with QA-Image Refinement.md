---
title: "Iterating on a Keycloak Theme with QA-Image Refinement"
aliases:
  - Keycloak theme QA-image workflow
  - OS1 consent page iteration
  - go-go-host theme visual iteration loop
tags: [project-report, keycloak, theme, os1, css, freemarker, device-flow, qa-image, visual-iteration]
status: active
type: project-report
created: 2026-05-13
repo: /home/manuel/workspaces/2026-05-11/go-go-host-v1/go-go-host
related_reports:
  - "[[PROJECT REPORT - Keycloak OS1 Login Theme - A Technical Deep Dive]]"
  - "[[PROJECT REPORT - go-go-host OAuth Device Flow CLI - A Technical Deep Dive]]"
source_files:
  - deployments/dev/keycloak/themes/go-go-host/login/login-oauth-grant.ftl
  - deployments/dev/keycloak/themes/go-go-host/login/resources/css/os1-overrides.css
---

# Iterating on a Keycloak Theme with QA-Image Refinement

This report documents the workflow of iteratively refining a Keycloak login theme's visual appearance using the `ask_questions_about_images` (qa-image) tool as a visual feedback loop. The concrete task was adding an OS1-styled OAuth consent page for the device flow, but the broader pattern — screenshot → VLM analysis → targeted CSS edit → reload → repeat — is the real deliverable.

The starting point was the existing OS1 login theme documented in [[PROJECT REPORT - Keycloak OS1 Login Theme - A Technical Deep Dive]]. The consent page (where a user grants scopes to a CLI client during device flow) was rendering with the default Keycloak styling inside the OS1 window chrome. It needed to match.

> [!summary]
> The iteration loop was: take a screenshot → ask a VLM to describe what it sees → identify specific spacing/typography/color issues → make targeted CSS edits → reload and repeat. The VLM acted as a second pair of eyes that could describe rendered CSS in plain language, catching things like "the header title is hidden" or "the scope list is cramped." The key technical discovery was that Keycloak's required-action OAuth flow doesn't set the template's `bodyClass` on the `<body>` element, which broke the `body.oauth` selectors and required switching to CSS `:has()` selectors instead.

## The problem

The OAuth consent page for device flow (the page that asks "Do you grant these access privileges?") was rendering inside the OS1 window chrome but the internals — scope list, heading, buttons — were using default Keycloak styling. The scope items had too much spacing. Both buttons (Yes/No) were identically styled black blocks. The page title "Grant Access to go-go-host-cli" was hidden because the CSS that hides the login page title was also hiding it here.

The user's assessment was precise: "scope rows are fine, just a bit of padding above the title" and "maybe make scopes a list and slightly smaller font and slight color muted accent."

## The Keycloak template gap

The existing theme only overrode `login.ftl`. Keycloak renders the consent page from a different FreeMarker template — `login-oauth-grant.ftl` — which the theme didn't override. Without a custom template, Keycloak falls back to the parent theme's version, which produces the default PatternFly DOM.

The base Keycloak 26 `login-oauth-grant.ftl` (from the `base` theme) looks like this:

```ftl
<@layout.registrationLayout bodyClass="oauth"; section>
    <#if section = "header">
        <p>${msg("oauthGrantTitle",advancedMsg(client.name))}</p>
    <#elseif section = "form">
        <div id="kc-oauth" class="content-area">
            <h3>${msg("oauthGrantRequest")}</h3>
            <ul>
                <#list oauth.clientScopesRequested as clientScope>
                    <li><span>${advancedMsg(clientScope.consentScreenText)}</span></li>
                </#list>
            </ul>
            <form class="form-actions" action="${url.oauthAction}" method="POST">
                <input type="hidden" name="code" value="${oauth.code}">
                <div id="kc-form-buttons">
                    <input class="..." name="accept" id="kc-login" type="submit" value="${msg('doYes')}"/>
                    <input class="..." name="cancel" id="kc-cancel" type="submit" value="${msg('doNo')}"/>
                </div>
            </form>
        </div>
    </#if>
</@layout.registrationLayout>
```

The important structural elements are `#kc-oauth`, `#kc-form-buttons`, `#kc-login` (Yes), and `#kc-cancel` (No). The custom template added `id="kc-oauth-scopes"` to the `<ul>` for CSS targeting and `class="kc-oauth-buttons"` to the button container.

## The `:has()` selector discovery

The base template passes `bodyClass="oauth"` to `registrationLayout`. The initial CSS used `body.oauth` selectors to differentiate the consent page from the login page:

```css
body.oauth .login-pf-header { /* show header */ }
body:not(.oauth) .login-pf-header { /* hide header */ }
```

This didn't work. When I navigated to the actual consent page and inspected the DOM, the `<body>` had no class at all:

```javascript
document.body.className  // ""
```

Keycloak's required-action OAuth flow (the `/login-actions/required-action?execution=OAUTH_GRANT` path) doesn't apply the template's `bodyClass` parameter to the `<body>` element. The `bodyClass` is set in the FreeMarker template, but the required-action rendering path in Keycloak apparently ignores it.

The fix was to switch from `body.oauth` to `.card-pf:has(#kc-oauth)`:

```css
/* Login page: no #kc-oauth inside the card → hide title, strip header */
.card-pf:not(:has(#kc-oauth)) .login-pf-header { ... }
.card-pf:not(:has(#kc-oauth)) #kc-page-title { display: none; }

/* Consent page: #kc-oauth exists inside the card → show title, add header border */
.card-pf:has(#kc-oauth) .login-pf-header { ... }
.card-pf:has(#kc-oauth) #kc-page-title { display: block; }
```

The `:has()` selector works because `#kc-oauth` only exists in the consent page DOM. This is a structural selector — it depends on template content, not on Keycloak's body-class plumbing, which is fragile across rendering paths.

> [!warning] Browser support
> `:has()` is supported in all modern browsers (Chrome 105+, Firefox 121+, Safari 15.4+). Since Keycloak login pages are only accessed through modern browsers, this is acceptable. But if IE11 support were needed, this approach would not work.

## The iteration loop

The workflow followed a tight loop:

### Loop 1: Initial state assessment

1. **Screenshot** the production consent page (from the user's clipboard).
2. **Ask VLM**: "Describe the visual appearance of this page in detail."
3. **VLM response**: Identified the OS1 window chrome, scope list with default styling, both buttons as identical black blocks, footer links.
4. **Assessment**: Need custom template, CSS for scopes, button differentiation.

### Loop 2: First implementation

1. Created `login-oauth-grant.ftl` template.
2. Added consent-specific CSS: bordered scope table, button gap, secondary "No" button, `body.oauth` selectors.
3. **Screenshot** the local dev consent page.
4. **Ask VLM**: "How does this look? Is the scope list compact? Are buttons spaced? Is No styled as secondary?"
5. **VLM response**: Header title is still hidden (the `body.oauth` selectors aren't matching). Scope rows cramped. Button gap too small. "No" outline too heavy. Overall top-heavy layout.
6. **User feedback**: "scope rows are fine, just a bit of padding above the title."

### Loop 3: Fix selectors and spacing

1. Switched from `body.oauth` to `:has()` selectors.
2. Increased top padding, scope row padding, button gap.
3. Lightened "No" button to 1px border, `#666` text, `#999` shadow.
4. **Screenshot** the updated page.
5. **Ask VLM**: "How does this look?"
6. **VLM response**: Looks clean. Title now visible. Scope list bordered table reads well. "No" is secondary. Padding adequate.
7. **User feedback**: "scope rows are fine, just a bit of padding above the title" and "button gap is fine too. it's just the padding" then "maybe make scopes a list and slightly smaller font and slight color muted accent."

### Loop 4: Final polish

1. Added `1rem` top padding to the content area.
2. Changed scope list from bordered table to `list-style: disc` with `10px` `#666` text.
3. Lightened font weight to `600`.
4. **Screenshot** the result.
5. **Ask VLM**: Confirmed bullet list rendering, muted color, adequate padding.
6. **User feedback**: "perfect."

### The loop pattern

```
Screenshot → VLM Description → Identify Issues → CSS Edit → Cache Clear → Reload → Screenshot → ...
```

The VLM served three roles:

1. **Verifier**: "Is the title visible now?" / "Is the scope list showing as a bullet list?"
2. **Describer**: "The gap between YES and NO is small; the group margins above/below are also tight."
3. **Catch-all**: Caught the hidden `#kc-page-title` which I hadn't noticed because the OS1 title bar is the visual focus.

The VLM is not a designer. It describes what it sees in CSS-rendered pixels, not what good design looks like. The design decisions — "make scopes a list", "slightly smaller font", "muted accent" — came from the user. The VLM confirmed execution.

## What the VLM is good at vs. what it misses

### Good at

- Confirming whether a CSS rule is actually taking effect (e.g., "is the title visible?")
- Describing spacing relationships in plain language ("the gap between buttons is small")
- Catching global side effects ("the header title is hidden on this page too")
- Verifying color values and contrast ("scope items appear as #666 gray")

### Bad at

- Proposing design direction (it will describe current state, not suggest improvements)
- Distinguishing subtle font size differences (10px vs 11px is hard to call from a screenshot)
- Knowing project-specific context (it doesn't know what "OS1 style" means without context)
- Pixel-perfect measurements (it estimates padding/margins but doesn't measure)

### The human's role

The human provides:

- **Design intent**: "make scopes a list and slightly smaller font and slight color muted accent"
- **Priority calls**: "scope rows are fine" (overriding VLM's suggestion to increase padding)
- **Acceptance**: "perfect." (the final call that the loop is done)

The VLM is a visual regression checker and describer. The human is the designer and the decider.

## The local development setup for theme iteration

The local Keycloak runs in Docker Compose at `http://127.0.0.1:18080` with the theme directory mounted read-only:

```yaml
volumes:
  - ./keycloak/themes/go-go-host:/opt/keycloak/themes/go-go-host:ro
```

This means CSS and template changes are reflected immediately on container restart, but Keycloak caches theme resources aggressively. After each CSS edit:

```bash
docker exec go-go-host-keycloak rm -rf /opt/keycloak/data/tmp/kc-gzip-cache
```

Then reload the browser. This is fast enough for a tight iteration loop (a few seconds per cycle).

For the consent page specifically, reaching the page required completing a device flow:

1. Create a test client with `oauth2.device.authorization.grant.enabled` attribute and `consentRequired=true`.
2. `curl -X POST .../auth/device` to get a device code and verification URI.
3. Navigate to the verification URI.
4. Log in as a test user.
5. The consent page appears.

This is more steps than just loading the login page, but the device code is valid for 10 minutes, so a single flow gives enough time for multiple screenshot-edit-reload cycles.

## Production deployment

The theme is deployed as a JAR file stored in a Kubernetes ConfigMap. The deployment path:

1. Rebuild the JAR from the local theme directory:
   ```bash
   jar cf go-go-host-keycloak-theme.jar META-INF theme
   ```

2. Base64-encode the JAR and update the ConfigMap in the GitOps repo:
   ```
   /home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/keycloak/keycloak-theme-configmap.yaml
   ```

3. Commit and push. Argo CD syncs the ConfigMap.

4. Restart the Keycloak pod to mount the updated ConfigMap:
   ```bash
   kubectl rollout restart deployment keycloak -n keycloak
   ```

5. Verify the new pod is running and the theme loads.

The separation of concerns is the same as documented in [[PROJECT REPORT - Keycloak OS1 Login Theme - A Technical Deep Dive]]: theme source in the app repo, GitOps for the runtime artifact, Terraform for realm state.

## The final CSS for the consent page

The consent-page-specific CSS in `os1-overrides.css`:

```css
/* Content area: more breathing room */
.card-pf:has(#kc-oauth) #kc-content {
  padding: 1rem 1rem 0.75rem !important;
}

/* Heading */
#kc-oauth h3 {
  font-size: 11px !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.03em !important;
  color: #111 !important;
  margin: 0 0 0.65rem 0 !important;
}

/* Scope list: simple bullet list with muted accent */
#kc-oauth ul,
#kc-oauth-scopes {
  list-style: disc !important;
  padding-left: 1.25rem !important;
  margin: 0 0 1rem 0 !important;
  border: none !important;
}

#kc-oauth li {
  padding: 0.15rem 0 !important;
  font-size: 10px !important;
  color: #666 !important;
  line-height: 1.35 !important;
}

#kc-oauth li span {
  font-size: 10px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.02em !important;
  color: #666 !important;
}

/* Button container */
#kc-oauth .kc-oauth-buttons,
#kc-oauth #kc-form-buttons {
  display: flex !important;
  flex-direction: column !important;
  gap: 0.65rem !important;
}

/* "No" button: lighter secondary */
input#kc-cancel {
  background: #fff !important;
  color: #666 !important;
  border: 1px solid #999 !important;
  box-shadow: 1px 1px 0 #999 !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
}

input#kc-cancel:hover {
  color: #111 !important;
  border-color: #111 !important;
  box-shadow: 1px 1px 0 #111 !important;
}
```

## What changed in the login page CSS

The login page was also affected by this work, because the old `body:not(.oauth)` selectors were removed. The new selectors use `.card-pf:not(:has(#kc-oauth))` instead, which produces the same result for the login page (no `#kc-oauth` in the card → hide title, strip header).

The `input[type="submit"]` selector was also removed from the primary button rule. Previously all submit buttons got the black primary style. Now only `input#kc-login` (the Yes button and Sign In button) gets it, and `input#kc-cancel` gets the secondary style explicitly.

## What to remember for next time

1. **Keycloak's body class is unreliable.** The template can declare `bodyClass="oauth"`, but not all rendering paths actually apply it. Use structural selectors based on template content (`:has()`) instead.

2. **The VLM is a describer, not a designer.** It tells you what it sees. You tell it what to look for. The design direction comes from the human.

3. **Scope the VLM question tightly.** "Describe the visual appearance" is too broad. "Is the title visible?" and "How much padding is above the header?" are better. Broad questions give broad answers that are harder to act on.

4. **Cache clearing is part of the loop.** Every CSS edit → `rm -rf kc-gzip-cache` → reload. If you forget the cache clear, you'll see the old CSS and think your edit didn't work.

5. **The `:has()` selector is the right tool for Keycloak theme differentiation.** It's structural, it doesn't depend on Keycloak's rendering pipeline setting body classes correctly, and it's supported in all modern browsers.

6. **Test both pages after shared CSS changes.** The login page and consent page share `os1-overrides.css`. A change that fixes the consent page can break the login page. Screenshot both after each edit round.

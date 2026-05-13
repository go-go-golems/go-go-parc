---
title: "Keycloak OS1 Login Theme — A Technical Deep Dive"
aliases:
  - go-go-host Keycloak OS1 login theme
  - Keycloak OS1 theme deep dive
  - go-go-host custom authentication landing page
  - Keycloak theme GitOps Terraform report
tags: [project-report, keycloak, go-go-host, auth, oidc, github, terraform, gitops, k3s, argocd, css, freemarker, ui]
status: active
type: project-report
created: 2026-05-12
repo: /home/manuel/workspaces/2026-05-11/go-go-host-v1/go-go-host
related_repos:
  - /home/manuel/code/wesen/2026-03-27--hetzner-k3s
  - /home/manuel/code/wesen/terraform
public_auth_url: https://auth.yolo.scapegoat.dev/realms/go-go-host
public_app_url: https://hosting.yolo.scapegoat.dev
source_ticket: HOST-010-KEYCLOAK-CUSTOM-LOGIN
---

# Keycloak OS1 Login Theme — A Technical Deep Dive

This report explains how the `go-go-host` Keycloak login page was changed from the default PatternFly-styled login page into a monochrome, classic Mac OS 1-inspired authentication surface. The implementation covered local development, the Keycloak theme system, FreeMarker template overrides, CSS constraints, GitHub identity-provider placement, GitOps deployment of a theme artifact, and Terraform ownership of realm state.

The goal was not only to make the login page visually consistent with the `go-go-host` dashboard. The deeper engineering goal was to separate three different kinds of configuration that are often confused during authentication work: the files Keycloak loads at startup, the realm settings stored in Keycloak's database, and the OAuth credentials that must remain outside Git.

> [!summary]
> The finished setup has three durable layers:
> 1. **The theme files live with the application** under `deployments/dev/keycloak/themes/go-go-host/login/`.
> 2. **The production theme artifact is deployed by GitOps** as a Keycloak provider JAR mounted into `/opt/keycloak/providers/`.
> 3. **The production realm selects the theme and owns GitHub SSO through Terraform** in `terraform/keycloak/apps/go-go-host/envs/k3s-beta/`.

## The result in one paragraph

The production login page for `go-go-host` now uses a custom Keycloak login theme named `go-go-host`. The page is monochrome: white background, black borders, compact type, square controls, an active-window title bar made from horizontal stripes, and a black primary button. GitHub is rendered as the first login option above the local username/password form. The local form remains available, but it is secondary. The theme is deployed to production Keycloak as a JAR through the K3s GitOps repo, and the realm setting `loginTheme = "go-go-host"` plus the GitHub IdP configuration are now managed in Terraform.

The production login URL is:

```text
https://auth.yolo.scapegoat.dev/realms/go-go-host/protocol/openid-connect/auth?client_id=go-go-host-dashboard&redirect_uri=https%3A%2F%2Fhosting.yolo.scapegoat.dev%2Fapp%2Fauth%2Fcallback&response_type=code&scope=openid&code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&code_challenge_method=S256
```

## Why a Keycloak theme is a multi-layer change

A Keycloak login theme is not just a CSS file. Keycloak renders login pages from a combination of realm state, provider resources, FreeMarker templates, message bundles, JavaScript, and CSS. A visible change on the login screen therefore requires several conditions to be true at the same time.

First, Keycloak must be able to find the theme files. In local development this means mounting a directory into `/opt/keycloak/themes/go-go-host`. In production it means installing a theme artifact into the running Keycloak server. For this project the production artifact is a JAR mounted into `/opt/keycloak/providers/go-go-host-keycloak-theme.jar`.

Second, the realm must select the theme. Installing the theme into Keycloak does not make any realm use it. The `go-go-host` realm must have `loginTheme` set to `go-go-host`. That setting is realm state and belongs in Terraform, not in the Kubernetes Deployment.

Third, the desired social login button only appears when the realm has an enabled identity provider. Template and CSS work can prepare the layout, but Keycloak will not render a GitHub button unless a GitHub identity-provider instance exists in the realm.

Those three conditions form the minimum complete system:

```mermaid
flowchart TD
    ThemeFiles[Theme files in app repo] --> ThemeJar[Theme JAR]
    ThemeJar --> GitOps[GitOps ConfigMap / Keycloak Deployment]
    GitOps --> ProvidersDir[/opt/keycloak/providers/go-go-host-keycloak-theme.jar]
    ProvidersDir --> KeycloakRuntime[Keycloak runtime can load theme]

    Terraform[Terraform realm config] --> LoginTheme[realm.loginTheme = go-go-host]
    Terraform --> GithubIdP[GitHub IdP alias github]

    KeycloakRuntime --> Render[Rendered login page]
    LoginTheme --> Render
    GithubIdP --> Render
```

If any one of these is missing, the page fails in a different way. If the artifact is missing, Keycloak cannot load the theme. If the realm does not select the theme, Keycloak falls back to its default login theme. If the GitHub IdP is missing, the custom social-provider area is absent even though the template is correct.

## The source files

The local theme source lives in the application repository:

```text
/home/manuel/workspaces/2026-05-11/go-go-host-v1/go-go-host/deployments/dev/keycloak/themes/go-go-host/login/
├── footer.ftl
├── login.ftl
├── resources/
│   └── css/
│       └── os1-overrides.css
└── theme.properties
```

The theme configuration is deliberately small:

```properties
parent=keycloak
import=common/keycloak
styles=css/login.css css/os1-overrides.css
locales=en
```

The choice of `parent=keycloak` means the theme inherits Keycloak's normal login behavior and PatternFly baseline styling. The custom CSS then overrides that baseline. This was faster and safer than extending `base` because `base` requires recreating much more of the login surface. The cost is that the custom CSS is coupled to the DOM and class names generated by Keycloak 26.

The important files have different responsibilities:

| File | Responsibility |
|---|---|
| `theme.properties` | Tells Keycloak that this is a login theme, extends the built-in `keycloak` theme, and loads the OS1 CSS after the parent CSS. |
| `login.ftl` | Reorders the login page so identity providers render above the local username/password form. |
| `footer.ftl` | Adds a small footer area with project links. |
| `resources/css/os1-overrides.css` | Implements the monochrome window, controls, title bar, spacing, and social-provider button styles. |

## Reading Keycloak's login rendering path

Keycloak's login page is rendered through a FreeMarker layout macro. The base `login.ftl` imports `template.ftl` and passes content into named sections. The most important sections for this work were `header`, `form`, `socialProviders`, and `info`.

A simplified version of the default structure looks like this:

```ftl
<#import "template.ftl" as layout>
<@layout.registrationLayout ...; section>
  <#if section = "header">
    ${msg("loginAccountTitle")}
  <#elseif section = "form">
    ... username/password form ...
  <#elseif section = "socialProviders">
    ... GitHub, Google, or other IdP buttons ...
  <#elseif section = "info">
    ... registration or help text ...
  </#if>
</@layout.registrationLayout>
```

In the default Keycloak theme, social providers are rendered after the local login form. For `go-go-host`, that order was wrong. GitHub login is the preferred path for normal users. The local form remains useful for bootstrap and admin cases, but it should not be the first thing the page asks the user to do.

The custom `login.ftl` therefore moves the social-provider loop into the `form` section before the local form:

```ftl
<#if realm.password && social?? && social.providers?has_content>
  <div id="kc-social-providers">
    <ul class="kc-social-providers-list">
      <#list social.providers as p>
        <li>
          <a id="social-${p.alias}" class="kc-social-provider-btn" href="${p.loginUrl}">
            <#if p.iconClasses?has_content>
              <i class="${p.iconClasses!}" aria-hidden="true"></i>
            </#if>
            <span class="kc-social-provider-displayname">${p.displayName!}</span>
          </a>
        </li>
      </#list>
    </ul>
  </div>
  <div class="kc-login-divider">
    <span class="kc-login-divider-text">or</span>
  </div>
</#if>
```

The local form follows this block. This makes the first actionable control on the page the GitHub login button when GitHub is configured.

The design rule is simple: the template decides order and semantic structure; CSS decides presentation. Trying to solve the provider order with CSS alone would leave the DOM order incorrect and would create keyboard-navigation and accessibility problems.

## The DOM Keycloak actually renders

One of the first implementation lessons was that the FreeMarker files do not show the final class names directly. The templates use properties such as `${properties.kcInputClass!}` and `${properties.kcButtonPrimaryClass!}`. Those resolve through the parent theme's `theme.properties`.

The rendered Keycloak 26 login page uses PatternFly v4 classes. The main structure is:

```html
<div class="login-pf-page">
  <div id="kc-header" class="login-pf-page-header">
    <div id="kc-header-wrapper">go-go-host beta</div>
  </div>

  <div class="card-pf">
    <header class="login-pf-header">
      <h1 id="kc-page-title">Sign in to your account</h1>
    </header>

    <div id="kc-content">
      <div id="kc-content-wrapper">
        <div id="kc-form">
          <div id="kc-form-wrapper">
            ... social providers ...
            ... username/password form ...
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

The relevant input and button classes include:

```text
.pf-c-form-control
.pf-c-input-group
.pf-c-button.pf-m-primary
.pf-c-button.pf-m-control
.card-pf
.login-pf-page
.login-pf-header
```

This is why the first CSS pass only partially worked. It targeted some intuitive IDs, such as `input#kc-login`, but many visible styles were still controlled by PatternFly classes. The final CSS uses explicit selectors for both Keycloak IDs and PatternFly classes, with `!important` because the parent CSS has stronger or later rules in several places.

## The OS1 styling rules

The visual target was deliberately constrained. The theme should be monochrome and compact. It should not use green, teal, blue, gradients, rounded corners, or modern card shadows.

The final rules were:

- The page background is white.
- The login surface is a rectangular window.
- The title bar uses horizontal black stripes.
- The centered title reads `go-go-host`, not the realm display name.
- Controls use square corners and black borders.
- The primary button is black with white text.
- Links are black and underlined.
- Link hover does not become a large inverted rectangle.
- GitHub login appears above the username/password form.
- The `OR` divider separates social login from local login.

The core CSS begins by taking control of the page background and font:

```css
.login-pf body,
body#kc-login {
  background: #fff !important;
  background-image: none !important;
  font-family: "Chicago", "Geneva", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
  font-size: 12px !important;
  color: #111 !important;
}

.login-pf-page {
  background: #fff !important;
  background-image: none !important;
}
```

The title bar is the most specific part of the theme. Keycloak renders the realm display name as a raw text node inside `#kc-header-wrapper`. Since it is not wrapped in an element, it cannot be hidden with a child selector. The solution is to set the wrapper's font size to zero, then render the desired title through a pseudo-element:

```css
#kc-header-wrapper {
  background: #fff !important;
  background-image: repeating-linear-gradient(
    to bottom,
    #111 0px, #111 1px,
    #fff 1px, #fff 2px
  ) !important;
  border: 2px solid #111 !important;
  border-bottom: none !important;
  font-size: 0 !important;
  text-align: center !important;
  overflow: hidden !important;
}

#kc-header-wrapper::after {
  content: 'go-go-host' !important;
  display: inline-block !important;
  padding: 0 0.5rem !important;
  background: #fff !important;
  position: relative !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  letter-spacing: 0.02em !important;
  color: #111 !important;
}
```

The header and card are siblings, so they must be aligned separately:

```css
#kc-header,
.login-pf-page-header {
  max-width: 500px !important;
  margin: 0 auto !important;
  width: 500px !important;
}

.card-pf {
  border: 2px solid #111 !important;
  border-top: none !important;
  border-radius: 0 !important;
  box-shadow: 4px 4px 0 #111 !important;
  background: #fff !important;
  padding: 0 !important;
  margin-top: 0 !important;
}
```

The controls follow the same rule set:

```css
.pf-c-form-control,
input#username,
input#password,
input[type="text"],
input[type="password"],
input[type="email"] {
  border: 2px solid #111 !important;
  border-radius: 0 !important;
  box-shadow: 1px 1px 0 #999 !important;
  background: #fff !important;
  color: #111 !important;
  font-family: inherit !important;
  font-size: 11px !important;
  padding: 0.35rem 0.5rem !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

.pf-c-button.pf-m-primary,
input#kc-login,
input[type="submit"] {
  background: #111 !important;
  color: #fff !important;
  border: 2px solid #111 !important;
  border-radius: 0 !important;
  box-shadow: 2px 2px 0 #111 !important;
  text-transform: uppercase !important;
}
```

The page now has a single coherent language: every important edge is a black rule, every control is square, and every accent is expressed through weight, border, or placement rather than color.

## The social login layout

Social login is not an optional afterthought in this deployment. The normal path is GitHub. The local form remains because bootstrap and recovery paths still need it.

The layout is therefore:

```text
OS1 title bar
GitHub button
OR divider
username/password fields
Sign In button
footer links
```

The social provider CSS makes the GitHub button a full-width, high-weight control:

```css
#kc-social-providers li a,
.kc-social-provider-btn {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 0.5rem !important;
  border: 2px solid #111 !important;
  border-radius: 0 !important;
  box-shadow: 2px 2px 0 #111 !important;
  padding: 0.65rem 1rem !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  text-align: center !important;
  text-decoration: none !important;
  color: #111 !important;
  background: #fff !important;
  text-transform: uppercase !important;
}
```

The divider is a small structural cue, not a visual focus:

```css
.kc-login-divider {
  display: flex !important;
  align-items: center !important;
  margin: 0.75rem 0 !important;
  gap: 0.5rem !important;
}

.kc-login-divider::before,
.kc-login-divider::after {
  content: '' !important;
  flex: 1 !important;
  border-top: 1px solid #111 !important;
}

.kc-login-divider-text {
  font-size: 10px !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  color: #666 !important;
}
```

This ordering matters for keyboard users as well as visual users. The first major action in the form is GitHub. The DOM order and the visual order match.

## The spacing bug above GitHub

After the GitHub button appeared, the top of the card had too much internal whitespace. The visible gap was about 30 pixels. That was not caused by the title bar itself. The title bar and card were touching. The space came from padding inside the card body.

The relevant computed values were:

```json
{
  "content": {
    "padding": "12px 16px",
    "paddingTop": "12px"
  },
  "social": {
    "padding": "12px 0px 0px",
    "paddingTop": "12px"
  }
}
```

The fix was to remove top padding from both layers:

```css
#kc-content {
  padding: 0 1rem 0.75rem !important;
  margin: 0 !important;
}

#kc-social-providers {
  padding-top: 0 !important;
  margin-top: 0 !important;
}
```

This reduced the top whitespace to a small readable gap while keeping the form from touching the border too tightly. The final spacing is intentional: GitHub is visually first, but the body still has enough internal structure to read as a form.

## Local development flow

The local Keycloak service is defined in:

```text
/home/manuel/workspaces/2026-05-11/go-go-host-v1/go-go-host/deployments/dev/docker-compose.yaml
```

The Keycloak service mounts both the realm import and the theme directory:

```yaml
volumes:
  - ./keycloak/realm-go-go-host.json:/opt/keycloak/data/import/realm-go-go-host.json:ro
  - ./keycloak/themes/go-go-host:/opt/keycloak/themes/go-go-host:ro
```

The local stack is usually started through `devctl`:

```bash
cd /home/manuel/workspaces/2026-05-11/go-go-host-v1/go-go-host
devctl up --force
```

Useful local endpoints:

```text
Keycloak admin: http://127.0.0.1:18080/admin/master/console/
Admin user:     admin
Admin password: admin
Realm:          go-go-host
```

The local callback URL for GitHub OAuth is:

```text
http://127.0.0.1:18080/realms/go-go-host/broker/github/endpoint
```

During theme development, clear Keycloak's theme cache after CSS or template changes:

```bash
docker exec go-go-host-keycloak rm -rf /opt/keycloak/data/tmp/kc-gzip-cache
```

The ticket includes helper scripts:

```text
ttmp/2026/05/12/HOST-010-KEYCLOAK-CUSTOM-LOGIN--custom-keycloak-login-theme-for-go-go-host/scripts/
├── 01-restart-keycloak-with-theme.sh
├── 02-set-realm-login-theme.sh
└── 03-add-github-idp.sh
```

Those scripts are useful for reproducing the dev setup and for documenting the exact Admin API calls, but the production long-term path is Terraform.

## Production deployment path

The production Keycloak server runs in K3s and is managed by Argo CD from the GitOps repository:

```text
/home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/keycloak/
```

The theme was packaged into a JAR with this shape:

```text
META-INF/keycloak-themes.json
theme/go-go-host/login/theme.properties
theme/go-go-host/login/login.ftl
theme/go-go-host/login/footer.ftl
theme/go-go-host/login/resources/css/os1-overrides.css
```

The `keycloak-themes.json` file declares that the JAR contains a login theme:

```json
{
  "themes": [
    {
      "name": "go-go-host",
      "types": ["login"]
    }
  ]
}
```

The JAR is stored in GitOps as a ConfigMap:

```text
/home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/keycloak/keycloak-theme-configmap.yaml
```

The Keycloak Deployment mounts the JAR into the providers directory:

```yaml
volumeMounts:
  - name: theme-jar
    mountPath: /opt/keycloak/providers/go-go-host-keycloak-theme.jar
    subPath: go-go-host-keycloak-theme.jar
    readOnly: true
volumes:
  - name: theme-jar
    configMap:
      name: keycloak-theme-go-go-host
```

Argo CD then rolls Keycloak. The validation commands are:

```bash
kubectl get application keycloak -n argocd \
  -o jsonpath='{.status.sync.status} {.status.health.status}'

kubectl get pods -n keycloak -l app.kubernetes.io/name=keycloak
```

At this point Keycloak can load the theme, but the realm still has to select it. That selection is Terraform state.

## Terraform ownership of realm state

The `go-go-host` beta realm is managed here:

```text
/home/manuel/code/wesen/terraform/keycloak/apps/go-go-host/envs/k3s-beta/
```

This Terraform environment now owns the durable auth configuration:

- realm `go-go-host`,
- selected login theme `go-go-host`,
- dashboard OIDC client `go-go-host-dashboard`,
- GitHub identity provider,
- redirect URIs and web origins,
- platform admin role,
- bootstrap `wesen` user.

The realm module was extended with an optional `login_theme` variable:

```hcl
variable "login_theme" {
  type        = string
  default     = null
  nullable    = true
  description = "Optional login theme name selected for this realm. The theme artifact must already be installed in Keycloak."
}
```

The module passes that into `keycloak_realm`:

```hcl
resource "keycloak_realm" "this" {
  realm        = var.realm_name
  display_name = var.display_name
  login_theme  = var.login_theme
  # ...
}
```

The `go-go-host` environment sets the value:

```hcl
module "realm" {
  source      = "../../../../modules/realm-base"
  realm_name  = var.realm_name
  login_theme = var.login_theme
  # ...
}
```

The default is:

```hcl
variable "login_theme" {
  type        = string
  default     = "go-go-host"
  description = "Keycloak login theme selected for the go-go-host realm. The theme artifact is deployed by K3s GitOps."
}
```

The GitHub IdP is now declared in Terraform:

```hcl
resource "keycloak_oidc_github_identity_provider" "github" {
  count = var.enable_github_sso ? 1 : 0

  realm                         = module.realm.realm
  client_id                     = var.github_client_id
  client_secret                 = var.github_client_secret
  enabled                       = true
  display_name                  = var.github_display_name
  default_scopes                = "user:email"
  trust_email                   = true
  sync_mode                     = "IMPORT"
  github_json_format            = true
  gui_order                     = "10"
  hide_on_login_page            = false
  store_token                   = false
  add_read_token_role_on_create = false
}
```

The existing manually-created GitHub IdP was imported into Terraform state:

```bash
terraform import 'keycloak_oidc_github_identity_provider.github[0]' go-go-host/github
```

A plan then showed that Terraform would remove the existing `wesen` user's GitHub federated identity link. That link is runtime account state created by Keycloak's broker flow. Terraform should not remove it. The managed user therefore ignores that field:

```hcl
resource "keycloak_user" "wesen" {
  # ...

  lifecycle {
    ignore_changes = [
      federated_identity,
    ]
  }
}
```

After that, Terraform applied cleanly:

```text
Apply complete! Resources: 0 added, 1 changed, 0 destroyed.
```

A final plan reported:

```text
No changes. Your infrastructure matches the configuration.
```

## The ownership rule

This project now has a clear operating rule.

| Layer | Owned by | Examples |
|---|---|---|
| Theme source | App repo | `login.ftl`, `footer.ftl`, `os1-overrides.css` |
| Keycloak server runtime | K3s GitOps | Deployment, ConfigMap, mounted theme JAR, pod rollout |
| Keycloak realm state | Terraform | `loginTheme`, GitHub IdP, clients, roles, redirect URIs |
| Secret material | Operator environment / Vault-backed source | GitHub client secret, Keycloak admin credentials |

This separation matters because each layer changes at a different rate and has a different rollback model. A CSS bug should be fixed by changing the theme artifact. A bad realm redirect URI should be fixed in Terraform. A broken Keycloak pod should be fixed in GitOps. A leaked OAuth secret should be rotated in the secret system and then applied through the mechanism that consumes it.

## What can break

The current implementation is intentionally small, but there are several failure modes worth preserving.

### The theme can be installed but not selected

If the JAR is mounted correctly but `loginTheme` is unset, Keycloak renders its default login page. The fix is Terraform, not GitOps:

```bash
cd /home/manuel/code/wesen/terraform/keycloak/apps/go-go-host/envs/k3s-beta
terraform plan
terraform apply
```

### The social section can disappear

If the GitHub IdP is disabled or missing, the template does not render the social-provider block. This is not a CSS failure. The condition in `login.ftl` requires `social.providers?has_content`.

Check Terraform and Keycloak state:

```bash
terraform state list | grep github
kubectl exec -n keycloak deploy/keycloak -- \
  /opt/keycloak/bin/kcadm.sh get realms/go-go-host/identity-provider/instances
```

### Keycloak can serve stale CSS

In development, Keycloak may continue serving old theme assets from:

```text
/opt/keycloak/data/tmp/kc-gzip-cache
```

Clear it after changes:

```bash
docker exec go-go-host-keycloak rm -rf /opt/keycloak/data/tmp/kc-gzip-cache
```

In production, a pod rollout should load the mounted provider JAR. If a change does not appear, check the pod start time, mounted file, and Argo CD sync status.

### Keycloak upgrades can break the template

The custom `login.ftl` is copied from Keycloak's base template and then modified. If Keycloak changes its login template in a future release, this custom copy will not inherit those changes automatically.

The safe upgrade process is:

1. Extract the new `theme/base/login/login.ftl` from the new Keycloak theme JAR.
2. Diff it against the current custom `login.ftl`.
3. Reapply the social-provider ordering changes deliberately.
4. Screenshot local and production login pages.

### Terraform can attempt to remove runtime user links

The Keycloak provider sees `federated_identity` on users. These links are created when users login through GitHub. They are runtime state. The bootstrap `wesen` user ignores changes to `federated_identity` so Terraform does not unlink the GitHub account.

## Recommended future direction

The current ConfigMap-mounted JAR is acceptable for this small beta theme. The long-term production path should be reconsidered if the theme grows.

A custom Keycloak image is cleaner for larger theme or provider artifacts:

```Dockerfile
FROM quay.io/keycloak/keycloak:26.1.0
COPY go-go-host-keycloak-theme.jar /opt/keycloak/providers/go-go-host-keycloak-theme.jar
```

Then GitOps owns only the image tag:

```yaml
image: ghcr.io/go-go-golems/keycloak-go-go-host:<tag>
```

The remaining important improvement is secret handling. Terraform now owns the GitHub IdP resource, which means the GitHub client secret is a Terraform input. Terraform state must be treated as secret-bearing infrastructure. A more mature setup would source that secret from Vault-backed automation or ensure the remote state backend has the correct security posture.

## Validation checklist

Use this checklist after changing the theme, Keycloak deployment, or Terraform realm state.

### Local validation

```bash
cd /home/manuel/workspaces/2026-05-11/go-go-host-v1/go-go-host
devctl up --force
docker exec go-go-host-keycloak rm -rf /opt/keycloak/data/tmp/kc-gzip-cache
```

Open the local auth URL:

```text
http://127.0.0.1:18080/realms/go-go-host/protocol/openid-connect/auth?client_id=go-go-host-dashboard&redirect_uri=http://127.0.0.1:5173/app/auth/callback&response_type=code&scope=openid&code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&code_challenge_method=S256
```

Check:

- The title bar is striped and constrained to the window.
- The page is monochrome.
- GitHub is above the local form.
- The `OR` divider is present.
- Footer links remain black and underlined.

### Production GitOps validation

```bash
kubectl get application keycloak -n argocd \
  -o jsonpath='{.status.sync.status} {.status.health.status}'

kubectl exec -n keycloak deploy/keycloak -- \
  ls -l /opt/keycloak/providers/go-go-host-keycloak-theme.jar
```

### Production Terraform validation

```bash
cd /home/manuel/code/wesen/terraform/keycloak/apps/go-go-host/envs/k3s-beta
export AWS_PROFILE=manuel
terraform plan -detailed-exitcode
```

Expected result after a clean apply:

```text
No changes. Your infrastructure matches the configuration.
```

### Production page validation

Open the production auth URL and verify the page:

```text
https://auth.yolo.scapegoat.dev/realms/go-go-host/protocol/openid-connect/auth?client_id=go-go-host-dashboard&redirect_uri=https%3A%2F%2Fhosting.yolo.scapegoat.dev%2Fapp%2Fauth%2Fcallback&response_type=code&scope=openid&code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&code_challenge_method=S256
```

## Closing notes

The final result is a small change on the surface and a useful operational pattern underneath. The visible login page is one screen. The durable implementation is a coordinated set of source files, theme packaging, GitOps runtime deployment, Terraform realm ownership, and secret handling.

The most important rule is to keep those layers separate. Theme files define what Keycloak can render. GitOps defines what the Keycloak server can load. Terraform defines what the realm selects and which identity providers exist. Secrets provide the credentials that make those providers work. When each layer has a clear owner, the system can be changed, reviewed, and recovered without guessing where a setting lives.

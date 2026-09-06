# ZITADEL Branding Setup

- URL: https://chatgpt.com/c/6a67fa40-eab0-83ea-af90-9efb6825bd51
- Created: 2026-07-28T00:39:31.065Z

---

> i use zitadel but i'm a bit confused by how I can use my branding for say, the user settings page and login page and all that. How do people usually do it?

I’ll separate the built-in branding options from the cases where teams replace ZITADEL’s UI entirely, then map that to login and user-settings pages.

```json
{"system1_search_query":[{"q":"site:zitadel.com/docs branding login page user settings ZITADEL custom branding"},{"q":"site:zitadel.com/docs ZITADEL custom login UI branding console user settings"},{"q":"site:zitadel.com/docs ZITADEL login v2 branding themes organization"},{"q":"site:github.com/zitadel zitadel login UI branding user settings"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 5 websites**

**Choosing a settings approach**

I’d recommend hosting login with your branding, then keeping general profile settings in your app. Link security-sensitive actions to ZITADEL’s self-service pages, or build a fully custom settings UI through its APIs if seamless styling is essential.

**Chose a settings approach**

**Designing the account flow**

I’d build your own settings page for profile fields and ordinary preferences, using your backend to call the relevant APIs with least-privilege user authorization. Keep password, MFA, passkeys, and recovery actions delegated to ZITADEL’s security flows.

**Designed the account flow**

</details>

The usual approach is **not to make every ZITADEL page look exactly like your application**. Teams generally split settings into two categories:

- **Application settings**—display name, preferences, notifications, billing, etc.—stay inside the application.
- **Identity/security settings**—password, MFA, passkeys, verified email—are handled by ZITADEL’s hosted UI or by a custom interface built over ZITADEL’s APIs.

## Recommended low-maintenance setup

```text
your-app.example.com
  ├── /settings                 Your application settings
  └── Sign in → auth.example.com

auth.example.com
  ├── Hosted ZITADEL login
  └── ZITADEL account security/self-service
```

### 1. Give ZITADEL its own branded domain

Use something like:

```text
auth.example.com
login.example.com
identity.example.com
```

That removes the visibly third-party ZITADEL hostname and makes redirects feel intentional. ZITADEL explicitly supports custom authentication domains for this purpose. citeturn383596view6

### 2. Configure the built-in branding

In **Default Settings → Branding**, configure:

- Light and dark logos
- Icons
- Primary, background, warning and text colors
- Custom font
- Login-name suffix visibility
- “Powered by ZITADEL” watermark visibility

You must click **Apply settings** after configuring it. Instance branding becomes the fallback for organizations that do not override it. citeturn486851view0turn486851view5

You can also configure message text, login text, email templates, support links, privacy policy and terms. citeturn486851view3turn486851view5

One current wrinkle: with **Hosted Login V2**, interface-text overrides are configured through the Settings V2 API rather than directly through the Management Console. citeturn383596view3

### 3. Make sure the correct branding is selected

This is a frequent source of confusion. Creating branding does not necessarily mean every authorization request will use it.

For a single-brand product, set the project branding behavior to **Enforce project’s policy**. That forces the organization owning the project to supply the branding throughout login.

For a multi-tenant B2B product, use **Allow login user policy**. Login starts with your product branding, then can switch to the customer organization’s branding once ZITADEL identifies the user. citeturn383596view4

You can also explicitly select an organization by adding an organization scope to the OIDC authorization request:

```text
urn:zitadel:iam:org:id:123456789
```

or:

```text
urn:zitadel:iam:org:domain:primary:customer.example
```

That triggers the selected organization’s login settings and branding. citeturn383596view2turn383596view5

## What to do about the user-settings page

ZITADEL provides an existing profile and security page at:

```text
https://auth.example.com/ui/console/users/me
```

It supports profile changes, password management, MFA and passkeys. citeturn383596view2

However, that page is part of the ZITADEL console experience. It can use some of your branding assets, but it will not look like a completely native page in your application.

A practical setup is:

1. Build `/settings` inside your application.
2. Put normal product preferences there.
3. Add an **Account security** section with links such as:
   - Change password
   - Manage passkeys
   - Configure MFA
4. Send those links to ZITADEL’s self-service UI.

This keeps sensitive credential operations out of your application while retaining most of the branded experience.

## When to build custom pages

Build your own account-security UI when users must never leave your application’s visual shell. ZITADEL supports implementing profile and self-service functionality through its APIs. citeturn383596view2

A fully custom login is also possible using ZITADEL’s Session and OIDC APIs, or by self-hosting and modifying its newer Login App. The Login App already supports login, registration, password changes, passkeys, MFA and account self-service. citeturn383596view1turn383596view7

The tradeoff is substantial: once you own the login UI, you must correctly handle password resets, account selection, external identity providers, MFA, passkeys, session cookies and OIDC continuation flows. For most products, the hosted login plus custom domain and branding is the better boundary.

## My default recommendation

Use:

- `auth.yourdomain.com`
- Hosted Login V2
- Instance-level branding
- **Enforce project’s policy** for a single-brand application
- Your own `/settings` page for product/profile preferences
- ZITADEL-hosted pages for password, MFA and passkey operations

Only replace the ZITADEL self-service and login interfaces when matching your application pixel-for-pixel is a firm product requirement.


---

> i use zitadel but i'm a bit confused by how I can use my branding for say, the user settings page and login page and all that. How do people usually do it?

I’ll verify the current ZITADEL options and then give you the standard setup most teams use.

```json
{"system1_search_query":[{"q":"site:zitadel.com/docs branding login hosted login user settings self service ZITADEL"},{"q":"site:zitadel.com/docs custom domain branding ZITADEL"},{"q":"site:zitadel.com/docs self service user profile password MFA ZITADEL"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 7 websites**

</details>

Most teams use **ZITADEL for authentication**, but keep the main user-settings experience inside their own application.

```text
app.example.com/settings
├── Profile and application preferences
├── Notifications
├── Billing
└── Security
    ├── Change password
    ├── Configure MFA
    └── Manage passkeys

auth.example.com
└── ZITADEL login and authentication flows
```

## The common setup

### 1. Brand the hosted login

Use ZITADEL’s hosted login with:

- Your logo
- Brand colors and font
- Customized login wording
- Privacy, terms and support links
- A custom domain such as `auth.example.com`

Branding can be set at the instance level as a default, or overridden for individual organizations. ZITADEL’s hosted login supports organization-specific branding, which is useful for multi-tenant B2B products. citeturn219369view0turn219369view1turn219369view4

For Hosted Login V2, logos, colors and branding settings are supported, but custom interface translations currently have to be configured through the Settings V2 API rather than directly through the Console. citeturn219369view1

### 2. Build the settings page in your application

Usually, `/settings` is a normal page in the application. Your application owns things such as:

- Display preferences
- Application profile information
- Notifications
- Team membership
- Subscription and billing
- Product-specific settings

For identity-related operations, you can either implement them using ZITADEL’s APIs or direct users to ZITADEL’s self-service interface.

ZITADEL’s built-in self-service profile is available at:

```text
https://auth.example.com/ui/console/users/me
```

It supports profile updates, password changes, MFA, passkeys, email and phone verification, and related account operations. citeturn219369view2

## The important limitation

The built-in `/ui/console/users/me` page is part of ZITADEL’s **Management Console**. It is not intended to become a completely white-labeled, application-native settings page.

ZITADEL removed dynamic color theming from the Management Console and explicitly recommends implementing your own user-facing UI when fully branded background, button, link and text colors are required. This limitation does **not** apply to the hosted login UI. citeturn219369view5

That means you should expect:

| Page | Typical approach |
|---|---|
| Login, registration and password reset | Branded ZITADEL hosted login |
| Application preferences | Your own UI |
| Basic profile information | Usually your own UI |
| Password, MFA and passkeys | ZITADEL self-service or your own API-based UI |
| Administrative console | ZITADEL Console, not heavily white-labeled |

## Three practical options

### Option A: Hosted login plus ZITADEL self-service

Use the hosted login and send users to `/ui/console/users/me` for security settings.

This is the least work, but users will see the ZITADEL Console-style settings interface.

### Option B: Hosted login plus your own settings UI

Use hosted login for authentication, but build a branded `/settings/security` page that calls ZITADEL’s APIs.

This is usually the best balance. ZITADEL handles the authentication protocol and login security, while your application controls the settings experience. ZITADEL documents that the built-in self-service interface can be replaced with your own API-based implementation. citeturn219369view2

### Option C: Self-host or replace the complete login UI

ZITADEL provides a Next.js Login App that can be self-hosted and customized. It includes login, registration and account self-service functionality such as profile changes, password changes, passkeys and MFA. Its feature set is still evolving, so you should verify that every authentication flow you require is implemented before adopting it. citeturn219369view1turn219369view3

A completely custom login can also be built using ZITADEL’s Session and OIDC APIs, but then your team owns considerably more authentication-flow logic. citeturn219369view7

## My recommendation

For most SaaS applications:

1. Configure branding under ZITADEL’s default or organization settings.
2. Use `auth.yourdomain.com` as the custom authentication domain.
3. Continue using ZITADEL’s hosted login.
4. Build `app.yourdomain.com/settings` yourself.
5. Initially link password, MFA and passkey management to ZITADEL self-service.
6. Gradually replace those links with API-based screens only when the Console-style experience becomes a product problem.

The key distinction is: **ZITADEL’s login page is designed to be branded; the Management Console user-settings page is not designed to be fully white-labeled.**


---

> come on, answer

```json
{"system1_search_query":[{"q":"site:zitadel.com/docs branding login page user settings page ZITADEL self service UI branding"},{"q":"site:zitadel.com/docs ZITADEL user settings page branding hosted login custom UI"},{"q":"site:zitadel.com/docs ZITADEL account console users me branding limitations"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 8 websites**

</details>

You’re right. The usual setup is:

**Login page:** use ZITADEL’s hosted login on a custom domain such as `auth.example.com`. Configure your logo, colors and font under **Default Settings → Branding**. For a single-brand product, set the project’s branding behavior to **Enforce project’s policy**, so your branding remains throughout the login flow. citeturn795864view0turn795864view3turn795864view4

**User settings:** build this page inside your own application:

```text
app.example.com/settings
```

Put profile details, preferences, billing and other product settings there.

For password, MFA and passkeys, you have two choices:

1. **Easy:** link users to ZITADEL’s built-in account page:

```text
https://auth.example.com/ui/console/users/me
```

It works, but it looks like ZITADEL’s management interface rather than a fully native part of your app. citeturn795864view2turn795864view5

2. **Fully branded:** build those security screens inside your app using ZITADEL’s APIs. ZITADEL explicitly supports replacing the built-in profile UI this way. citeturn795864view2turn505090search6

So the common architecture is:

```text
Hosted ZITADEL login     → branded with your logo/colors
Your own /settings page  → matches your app completely
ZITADEL APIs             → password, MFA, passkeys when needed
```

Start with the hosted login plus the built-in account page. Replace the account page with your own UI only when its appearance becomes a real problem.


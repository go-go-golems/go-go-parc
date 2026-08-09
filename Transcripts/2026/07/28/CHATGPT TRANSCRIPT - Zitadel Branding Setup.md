# Zitadel Branding Setup

- URL: https://chatgpt.com/c/6a67fd1e-32dc-83ea-8230-c120091c37d6
- Created: 2026-07-28T00:51:44.747Z

---

> i use zitadel but i'm a bit confused by how I can use my branding for say, the user settings page and login page and all that. How do people usually do it?

I’ll separate ZITADEL’s built-in branding from the cases where teams replace parts of the UI entirely, then map that to a practical setup.

```json
{"system1_search_query":[{"q":"site:zitadel.com/docs branding login user settings page custom UI ZITADEL"},{"q":"site:zitadel.com/docs guides manage console settings branding ZITADEL"},{"q":"site:zitadel.com/docs custom login UI ZITADEL user settings"},{"q":"site:github.com/zitadel/zitadel branding login custom UI user settings"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 11 websites**

</details>

The key distinction is that “branding” changes ZITADEL-owned screens; it does not turn the management console into a fully custom product UI. Teams choose between a branded hosted surface and an API-driven in-app account area.

```json
{"system1_search_query":[{"q":"site:zitadel.com/docs Login V2 self service URL account settings ZITADEL"},{"q":"site:github.com/zitadel/zitadel \"self service\" \"login\" Next.js ZITADEL route"},{"q":"site:zitadel.com/docs custom domain ZITADEL Cloud login domain branding"},{"q":"site:zitadel.com/docs user self service custom UI API profile password passkey ZITADEL"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 9 websites**

**Clarifying customization scope**

I’m distinguishing branding from full UI replacement. ZITADEL can brand hosted login and emails, while account settings remain within its Console-style interface. I’ll explain which parts can be customized and where a separate product-native settings page may be needed.

**Clarified customization scope**

**Planning the authentication foundation**

I’m treating the stable auth domain as the first decision. I’ll cover domain setup, branding, tenant-specific experiences, hosted self-service, custom settings pages, email branding, and the practical boundary between customer and admin interfaces.

**Planned the authentication foundation**

</details>

ZITADEL currently has **two different concepts mixed together**, which is probably the source of the confusion:

1. **Brand ZITADEL’s hosted screens**
2. **Build your own product-facing account screens using ZITADEL APIs**

## The usual setup

For most SaaS products, the practical default is:

- Use ZITADEL’s **hosted login**
- Put it on `auth.yourcompany.com`
- Apply your logo, colors, font, light/dark themes and email branding
- Build the normal profile/account page inside your own application
- Send users to ZITADEL only for sensitive authentication workflows you have not implemented yourself

This gives you a product-native settings experience without taking responsibility for maintaining the entire login, MFA, passkey and recovery system.

## 1. Brand the hosted login

At the **instance level**, configure your default branding. ZITADEL supports separate light and dark themes, logos, background/primary/warning/text colors, a custom font, login-name display options and hiding the ZITADEL watermark. Applying the branding also affects authentication emails. citeturn188978view0

A typical configuration would be:

```text
Application: app.example.com
ZITADEL/Auth: auth.example.com
Branding: Example logo, colors and font
Email sender: security@example.com
```

Using a custom authentication domain is worthwhile beyond aesthetics: passkeys are domain-bound, so changing your login domain later can invalidate or complicate existing passkey registrations. ZITADEL explicitly recommends configuring the production custom domain early. citeturn188978view2turn188978view4

For the newer hosted Login V2, ZITADEL Cloud serves it at:

```text
https://auth.example.com/ui/v2/login
```

You can enable it per application or for the entire instance. citeturn188978view2

One current limitation: Login V2 text overrides are configured through the **Settings V2 API**, rather than directly in the Management Console. citeturn188978view2

## 2. Decide what “user settings” means in your product

ZITADEL provides an existing profile self-service page at:

```text
https://auth.example.com/ui/console/users/me
```

It lets users change profile information, passwords, email and phone numbers, and manage MFA and passkeys. citeturn796230view3

The simplest implementation is therefore:

```text
Your app
  └── Account settings
        └── Redirect to ZITADEL self-service
```

This is reasonable for an internal product, an MVP or a developer-oriented application. The drawback is that the user enters something resembling the ZITADEL management interface rather than remaining inside your product.

For a polished customer-facing SaaS, the more common structure is:

```text
/settings/profile
/settings/security
/settings/sessions
/settings/team
```

You build those pages inside your application and call ZITADEL APIs for the underlying operations. ZITADEL explicitly supports implementing your own profile self-service through its APIs. citeturn796230view3

A useful division is:

| Area | Recommended owner |
|---|---|
| Name, avatar, language | Your application |
| Product preferences | Your application/database |
| Email or phone changes | Your application UI + ZITADEL API |
| Password change | ZITADEL hosted flow initially |
| MFA and passkeys | ZITADEL hosted flow initially |
| Password recovery | ZITADEL hosted login |
| Team members and roles | Your application UI + ZITADEL APIs |
| Internal IAM administration | ZITADEL Console |

Avoid treating the ZITADEL Console as your entire customer portal. It is primarily an identity-management interface, not a customizable application shell.

## 3. Full white-labeling

When matching the product design exactly is mandatory, you can self-host or fork ZITADEL’s Next.js Login V2 application, or build a login UI using the Session and OIDC APIs. The official login app uses the instance or organization branding and policies and includes profile, password, passkey and MFA self-service capabilities. citeturn796230view7

That architecture looks like:

```text
app.example.com
    Your product

auth.example.com
    Your fork of ZITADEL Login V2
    ├── login
    ├── registration
    ├── MFA
    ├── passkeys
    ├── recovery
    └── authentication self-service

ZITADEL backend
    Identity, policies, sessions and tokens
```

This gives maximum control, but you now own deployment, updates, security headers, accessibility, feature parity and testing of every authentication method. I would only choose this when the built-in branding is genuinely insufficient.

## Multi-tenant branding

For B2B applications, ZITADEL can apply branding at two levels:

- **Instance branding:** your default product brand
- **Organization branding:** a customer-specific override

To activate a particular organization’s branding during login, you can configure private labeling on the project or include the organization domain scope in the OIDC authorization request. Be aware that explicitly requesting the organization also restricts the login to users from that organization. citeturn188978view0turn796230view5

A common model is:

```text
Instance default:
  Your product branding

Organization: Acme
  Acme logo and colors

Organization: Globex
  Globex logo and colors
```

## My recommendation

Start with:

1. `auth.yourdomain.com` as the stable custom domain.
2. Hosted Login V2 with instance-level branding.
3. Your own SMTP sender and branded email templates.
4. A temporary “Security settings” link to ZITADEL self-service.
5. Your own in-app profile and organization-management pages.
6. Move password/MFA/passkey management in-app only when the UX benefit justifies the added implementation and security work.

That is usually the best balance: **ZITADEL owns authentication complexity; your application owns the customer experience.**


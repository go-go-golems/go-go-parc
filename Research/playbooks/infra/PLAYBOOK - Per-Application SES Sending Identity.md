---
title: "Playbook: Per-Application SES Sending Identity"
aliases:
  - SES per-app sending identity playbook
  - application SMTP credential playbook
  - SES domain identity and Vault SMTP delivery
tags:
  - playbook
  - infrastructure
  - aws-ses
  - smtp
  - terraform
  - vault
  - kubernetes
  - dns
  - security
status: active
type: playbook
created: 2026-07-31
repo: /home/manuel/code/wesen/terraform
related_repos:
  - /home/manuel/code/wesen/2026-03-27--hetzner-k3s
related:
  - "[[Projects/2026/07/26/PROJECT REPORT - ZITADEL SES SMTP - Vault Backed Verification and Recovery]]"
  - "[[Projects/2026/07/31/PROJECT REPORT - Hyperslop Mailing List - Double Opt-In Service from Zero to Production]]"
  - "[[Research/KB/Projects/infrastructure-and-release]]"
---

# Playbook: Per-Application SES Sending Identity

This playbook defines the procedure for giving one application its own AWS SES sending
identity and SMTP credential. It spans three repositories — `wesen/terraform` owns the
sending boundary, Vault owns the credential value, and `wesen/2026-03-27--hetzner-k3s`
delivers it into the Pod — which is why it lives here rather than in any one of them.

Use it when an application must send mail as its own domain or address. Do not use it to
add a second consumer to an existing credential; that is the arrangement this playbook
exists to replace.

> [!warning] The rule this playbook enforces
> Terraform owns the **boundary**: the domain identity, DKIM, the MAIL FROM domain, the IAM
> principal, and the policy that restricts what that principal may send as. Vault owns the
> **credential value**. An `aws_iam_access_key` resource writes both `secret` and
> `ses_smtp_password_v4` into Terraform state, extending their lifetime into every state
> snapshot, plan, log, and state-reader's permissions. Create the access key out-of-band and
> write it straight to Vault.
>
> This was violated once and reverted; see
> [[Projects/2026/07/31/PROJECT REPORT - Hyperslop Mailing List - Double Opt-In Service from Zero to Production]]
> §6.1.1 for the state evidence and the rotation that undoes it.

## 1. Decide the identity

An SES **identity** is a verified domain and determines what a message may claim in `From:`.
An SES **credential** is an IAM user whose access key is converted into an SMTP password.
They are separate objects: creating the identity produces no credential, and a credential is
account-scoped rather than identity-scoped.

Verify the **apex** when the application sends as `something@example.com`. Verifying
`mail.example.com` only permits sending as `@mail.example.com`. The MAIL FROM subdomain is a
separate setting and does not change what `From:` may claim.

## 2. Terraform — identity, DKIM, MAIL FROM

Add a module instance under `ses/domains/<domain>/envs/<env>`. It should output the DNS
records the zone needs — DKIM CNAMEs, the MAIL FROM MX and SPF TXT — rather than writing
them itself, because the zone usually lives in a different provider and state.

## 3. Terraform — the IAM principal

One IAM user per application. Scope `ses:SendRawEmail` by `Resource` to this identity's ARN
and its configuration set, so the credential cannot send as any other verified domain in the
account:

```hcl
resource "aws_iam_user_policy" "smtp" {
  name = "ses-send-raw-${replace(var.domain_name, ".", "-")}"
  user = aws_iam_user.smtp.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "ses:SendRawEmail"
      Resource = [
        module.ses_domain.identity_arn,
        "arn:aws:ses:${var.aws_region}:${data.aws_caller_identity.current.account_id}:configuration-set/${var.configuration_set_name}",
      ]
    }]
  })
}
```

Do **not** add an `aws_iam_access_key` resource. If a hand-created user already exists,
`import` it rather than recreating it; a clean plan afterwards confirms the hand-written
policy matched the declared one.

## 4. DNS — and the apply order

The zone module reads the SES outputs through `terraform_remote_state`, so **SES must be
applied before the zone**. Applying the zone first fails with an error naming neither
package. Record that order in a comment in the zone's `main.tf`; it is not otherwise
discoverable.

Record shapes are not portable between providers:

| | DigitalOcean | Cloudflare |
|---|---|---|
| Value field | `value` | `content` |
| MX priority | part of the record | separate `priority` argument |
| `tags` | supported | quota 0 on the current plan — omit entirely |
| Trailing dot | expected | must not be present |

`scapegoat.dev` and `workshops.tokenmaxxing-rehab.com` are DigitalOcean;
`hyperslop.systems` is Cloudflare. A record map copied between them does not apply.

## 5. Create the credential out-of-band and write it to Vault

The SMTP password is a SigV4 derivation over the IAM secret: HMAC chain from
`AWS4`+secret through the fixed date `11111111`, the region, `ses`, `aws4_request`, then the
message `SendRawEmail`, prefixed with a `0x04` version byte and base64-encoded. The AWS
console shows it at creation time; deriving it by hand is possible but unnecessary.

Write it to `kv/apps/<app>/<env>/ses` with these keys, which the application reads as
`SMTP_*` environment variables:

```text
host  port  username  password  from_address  from_name
```

`from_address` must be on a domain SES has verified.

## 6. Vault policy and role

Grant the application's own path and nothing else. Name explicitly what it must **not** read
when a neighbouring application has a similar path — this is where the shared-credential
arrangement creeps back in:

```hcl
path "kv/data/apps/<app>/<env>/ses" {
  capabilities = ["read"]
}

path "kv/metadata/apps/<app>/<env>/ses" {
  capabilities = ["read"]
}
```

Commit the policy to `vault/policies/kubernetes/<app>.hcl` and the role to
`vault/roles/kubernetes/<app>.json`, then apply with
`bash scripts/bootstrap-vault-kubernetes-auth.sh`.

## 7. Kubernetes

Three things beyond the usual VSO wiring:

- **A `VaultStaticSecret`** at `path: apps/<app>/<env>/ses`, with
  `argocd.argoproj.io/sync-wave: "-1"` so the Secret exists before the Deployment.
- **A NetworkPolicy egress rule for TCP 587.** No other policy on this cluster opens it.
  Without it every send hangs until the SMTP deadline instead of failing fast, which reads
  as an application hang rather than a network policy.
- **A rollout restart on every credential rotation.** Environment variables sourced from a
  Secret are injected when the container starts. VSO refreshing the Secret does not change
  the environment of a running process, so the Pod keeps presenting the old credential until
  it is replaced. This is the most commonly missed step.

## 8. Verify

```bash
# Identity, DKIM and MAIL FROM all verified
aws sesv2 get-email-identity --email-identity <domain> \
  --query '{Verified:VerifiedForSendingStatus,Dkim:DkimAttributes.Status,MailFrom:MailFromAttributes.MailFromDomainStatus}'

# Production access — a sandboxed account can only send to verified addresses,
# which makes a public signup form useless
aws sesv2 get-account --query ProductionAccessEnabled
```

Then send one real message and confirm delivery with the CloudWatch `AWS/SES` `Send` metric.

> [!important] Do not use `GetSendQuota` as your evidence
> `SendQuota.SentLast24Hours` has been observed stale at `0.0` while CloudWatch showed real
> sends. It will support a wrong conclusion. Use the CloudWatch metric.

Application logs are not evidence either unless you have confirmed the service actually
writes them — see the silent-service failure in the maillist report.

## 9. Rotation

Rotation is the same sequence, and a revert from a Terraform-managed key is a rotation, not
a detach: the secret is already in state history, so removing the resource does not unpublish
it.

1. Create a replacement access key out-of-band; write it to `kv/apps/<app>/<env>/ses`.
2. If a Terraform-managed key exists: `terraform state rm aws_iam_access_key.<name>`, then
   delete that key in AWS so the copy in state history authenticates nothing.
3. Remove the resource and any outputs from the configuration.
4. `kubectl rollout restart deployment/<app> -n <ns>` — see §7.
5. Confirm the CloudWatch `Send` metric increments on a live send.

## Related

- [[Projects/2026/07/26/PROJECT REPORT - ZITADEL SES SMTP - Vault Backed Verification and Recovery]]
  — sets the credential-in-state rule and asked for exactly this per-application principal.
  ZITADEL itself still uses the older shared credential.
- [[Projects/2026/07/31/PROJECT REPORT - Hyperslop Mailing List - Double Opt-In Service from Zero to Production]]
  — the first application built this way, including what violating §5 looks like.
- [[Projects/2026/03/25/PROJ - wesen terraform - Infra Session Report]] — the first SES domain
  in this account, `mail.scapegoat.dev`, on the shared-credential arrangement this replaces.

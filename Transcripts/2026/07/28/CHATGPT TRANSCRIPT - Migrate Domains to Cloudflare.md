# Migrate Domains to Cloudflare

- URL: https://chatgpt.com/c/6a6802e8-4564-83ea-a2aa-1c38838f09c5
- Created: 2026-07-28T01:16:24.903Z

---

> migrate my domains from godaddy to cloudflare, how?

I’ll separate the DNS cutover from the registrar transfer, because they are different operations and have different risks.

```json
{"system1_search_query":[{"q":"site:developers.cloudflare.com registrar transfer domain to Cloudflare Registrar official"},{"q":"site:developers.cloudflare.com dns zone add site change nameservers official Cloudflare"},{"q":"site:godaddy.com help transfer domain away from GoDaddy official auth code unlock domain"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 14 websites**

</details>

The safest sequence is:

## 1. Move DNS to Cloudflare first

This changes who hosts your DNS, but **GoDaddy remains the registrar**.

1. In Cloudflare, open **Domains → Onboard a domain**.
2. Enter the root domain, such as `example.com`.
3. Select a Cloudflare plan.
4. Let Cloudflare scan your existing DNS records.
5. Compare Cloudflare’s imported records against GoDaddy’s DNS zone.

Cloudflare’s scan may miss records, so manually verify all:

- `A`, `AAAA`, and `CNAME` website records
- `MX` email records
- Email-related `TXT` records: SPF, DKIM and DMARC
- Verification records for Google Workspace, Microsoft 365, Stripe, Shopify, etc.
- Subdomains and service records such as `SRV`
- CAA records

A missing mail record can interrupt email even when the website still works. citeturn744212search1turn892814search0

## 2. Disable DNSSEC at GoDaddy

Before changing nameservers, turn off DNSSEC in GoDaddy if it is currently enabled. Leaving the old DNSSEC configuration active during the nameserver change can make the domain unreachable. You can enable DNSSEC again in Cloudflare afterward. citeturn744212search21turn744212search42

## 3. Change the GoDaddy nameservers

Cloudflare will display two assigned nameservers resembling:

```text
alice.ns.cloudflare.com
bob.ns.cloudflare.com
```

In GoDaddy:

1. Open **Domain Portfolio**.
2. Select the domain.
3. Find **Nameservers**.
4. Choose **Change Nameservers** or **Use my own nameservers**.
5. Replace the GoDaddy nameservers with the two Cloudflare nameservers.
6. Save.

Cloudflare assigns the nameservers when the domain is onboarded; they must be copied exactly. citeturn744212search26turn744212search39

Wait until Cloudflare shows the domain as **Active**, then test:

```text
https://example.com
https://www.example.com
```

Also test sending and receiving email and any important subdomains.

## 4. Configure Cloudflare carefully

Once active:

- Use **Proxied**—orange cloud—for normal website records.
- Use **DNS only**—gray cloud—for mail records, FTP, SSH, verification records, and services Cloudflare should not proxy.
- Under **SSL/TLS**, use **Full (strict)** when your web server has a valid certificate.
- Re-enable **DNSSEC** in Cloudflare.
- Avoid deleting the old GoDaddy DNS zone until everything has been tested.

## 5. Transfer the registration to Cloudflare

After DNS is stable, move the actual registration.

In GoDaddy:

1. Open **Domain Portfolio**.
2. Select the domain.
3. Choose **Transfer to Another Registrar**.
4. Unlock the domain.
5. Obtain the authorization code, also called the EPP or auth code. citeturn744212search2turn744212search22

In Cloudflare:

1. Open **Domain Registration → Transfer Domains**.
2. Select the eligible domain.
3. Enter the GoDaddy authorization code.
4. Confirm the registrant details and payment.
5. Submit the transfer.

You can usually accelerate the process by approving the outgoing transfer in GoDaddy. Otherwise, GoDaddy says it can take approximately five to seven days. citeturn744212search28turn892814search0

## Common transfer blockers

The domain may not be transferable when:

- It was registered within the last 60 days.
- It was transferred within the last 60 days.
- Certain registrant contact details were recently changed.
- The domain is locked.
- The domain is expired, in redemption, or involved in a dispute.
- Cloudflare does not support that domain extension.

Most successful transfers add one year to the registration term, subject to registry-specific exceptions. Cloudflare Registrar also requires the domain to keep using Cloudflare nameservers. citeturn892814search1turn892814search3turn744212search20

**Recommended order:** copy DNS → disable DNSSEC → switch nameservers → test website and email → re-enable DNSSEC → transfer the registration. This separates the high-risk DNS cutover from the administrative registrar transfer.


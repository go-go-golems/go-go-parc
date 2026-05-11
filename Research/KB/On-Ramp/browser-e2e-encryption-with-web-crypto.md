---
title: "Browser E2E Encryption with Web Crypto"
aliases:
  - web crypto e2e
  - browser e2ee
  - envelope encryption in browser
  - web crypto sharing
tags: [knowledge-base, on-ramp, web-crypto, e2ee, encryption, browser, sharing]
status: active
type: knowledge-base
created: 2026-05-11
---

# Browser E2E Encryption with Web Crypto

> [!summary]
> The Web Crypto API is enough to build a real browser-based end-to-end encrypted storage system. The practical pattern is envelope encryption: each document gets its own symmetric key, and that key is wrapped for each authorized user with their public key. Public docs explain the cryptographic primitives; this entry explains the application shape.

## The idea in one paragraph

A browser E2E system does not encrypt “everything with one key.” Instead, it uses **envelope encryption**:
- generate one symmetric content key per document,
- encrypt the document content with that symmetric key,
- wrap that symmetric key separately for each authorized user using their public key,
- store only ciphertext on the server.

This is what makes selective sharing practical.

## Why we care

[[PROJ - E2E Encrypted Storage Prototype]] proves this pattern works in a minimal Go + SQLite + browser app. The server stores only ciphertext. All key generation, encryption, decryption, wrapping, and unwrapping happen in the browser via Web Crypto.

## The minimum architecture

At a high level:

1. user generates an asymmetric keypair in the browser,
2. each document gets a fresh symmetric key,
3. content is encrypted with the symmetric key,
4. the symmetric key is wrapped for each recipient,
5. server stores ciphertext + wrapped keys,
6. browser unwraps the right key before decrypting content.

The big conceptual payoff is that sharing a document means sharing the **document key**, not re-encrypting the whole document separately for every recipient.

## Why this is better than one-key-for-everything

A single long-lived symmetric key makes every document equally exposed. If it leaks, everything leaks. Per-document keys shrink the blast radius and make selective sharing possible. User A can share document 17 with user B without giving user B access to documents 1–16.

## The gotchas we've hit

**Metadata is often forgotten.** If you encrypt only the content body but not filenames, titles, or recipient lists, you may still leak a lot.

**Session/auth security is separate from crypto correctness.** A prototype can have correct encryption and weak session tokens at the same time. Don't confuse “the server stores only ciphertext” with “the whole system is production secure.”

**Key recovery is a product problem, not just a crypto problem.** If the user loses the browser key material and there is no backup or recovery flow, their data is gone.

**Revocation is harder than sharing.** Giving access is easy: wrap the document key for another user. Revoking access usually requires key rotation and rewrapping.

## What Web Crypto gives you

The important point is not that Web Crypto exposes algorithms. The important point is that it is sufficient for a complete browser-side flow:
- key generation,
- key import/export,
- symmetric encryption,
- asymmetric wrapping/unwrapping,
- no third-party JS crypto library required.

That lowers the barrier to building serious browser-side prototypes.

## Where to go deeper

- [[PROJ - E2E Encrypted Storage Prototype]] — full working prototype
- [[Tribal/application-native-authorization]] — if you need to separate authentication from document authorization
- Web Crypto API docs: <https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API>

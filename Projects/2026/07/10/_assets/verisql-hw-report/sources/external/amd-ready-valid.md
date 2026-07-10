# READY/VALID transfer rule

- Source: AMD documentation, “READY/VALID Handshake”.
- URL: https://docs.amd.com/r/en-US/pg286-v-demosaic/READY/VALID-Handshake
- Accessed: 2026-07-10.

The cited protocol documentation defines a transfer at a rising clock edge when READY and VALID are both asserted, subject to reset. VeriSQL-HW uses the same event rule. Its one-entry elastic register accepts a replacement input on the same edge that the previous output is consumed, and it must hold the registered output stable while VALID is high and READY is low.

---
title: "Captured source: Local Usb Network Common H"
source_file: "local-usb-network-common-h.md"
type: source
---

# Captured source: Local Usb Network Common H

Original ticket source file: `local-usb-network-common-h.md`.

#pragma once

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef union {
    uint32_t val;
    uint8_t bytes[4];
} UsbNetworkIpAddress;

typedef struct {
    UsbNetworkIpAddress address;
    UsbNetworkIpAddress netmask;
    UsbNetworkIpAddress gateway;
} UsbNetworkIpConfig;

#ifdef __cplusplus
}
#endif

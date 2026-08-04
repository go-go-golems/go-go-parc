---
title: "Captured source: External Mqtt Org"
source_file: "external-mqtt-org.md"
type: source
---

# Captured source: External Mqtt Org

Original ticket source file: `external-mqtt-org.md`.

## Why MQTT?

### Lightweight and Efficient

MQTT clients are very small, require minimal resources so can be used on small microcontrollers. MQTT message headers
are small to optimize network bandwidth.

### Bi-directional Communications

MQTT allows for messaging between device to cloud and cloud to device. This makes for easy broadcasting messages to
groups of things.

### Scale to Millions of Things

MQTT can scale to connect with millions of IoT devices.

### Reliable Message Delivery

Reliability of message delivery is important for many IoT use cases. This is why MQTT has 3 defined quality of service
levels: 0 - at most once, 1- at least once, 2 - exactly once

### Support for Unreliable Networks

Many IoT devices connect over unreliable cellular networks. MQTT’s support for persistent sessions reduces the time
to reconnect the client with the broker.

### Security Enabled

MQTT makes it easy to encrypt messages using TLS and authenticate clients using modern authentication protocols, such
as OAuth.

## MQTT Publish / Subscribe Architecture

![MQTT: publish / subscribe architecture](https://mqtt.org/assets/img/mqtt-publish-subscribe.png "MQTT: publish /
subscribe architecture")

## MQTT in Action

MQTT is used in a wide variety of industries[Automotive](https://mqtt.org/use-cases#automotive)

[

Logistics

](https://mqtt.org/use-cases#logistics)[

Manufacturing

](https://mqtt.org/use-cases#manufacturing)[

Smart Home

](https://mqtt.org/use-cases#smarthome)[

Consumer Products

](https://mqtt.org/use-cases#consumer-products)[

Transportation

](https://mqtt.org/use-cases#transportation)

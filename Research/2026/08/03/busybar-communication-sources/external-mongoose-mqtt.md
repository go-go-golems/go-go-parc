---
title: "Captured source: External Mongoose Mqtt"
source_file: "external-mongoose-mqtt.md"
type: source
---

# Captured source: External Mongoose Mqtt

Original ticket source file: `external-mongoose-mqtt.md`.

## User Guide

## Introduction

Mongoose is a lightweight networking library for C and C++ that provides event-driven, non-blocking APIs for TCP, UDP,
HTTP, WebSocket, and MQTT. It is widely used to add embedded web servers, secure device dashboards, cloud connectivity,
and OTA firmware updates to microcontrollers and embedded devices. Since 2004, Mongoose has powered thousands of
commercial and open-source products - it even runs on the International Space Station.

Mongoose runs on Windows, Linux, and macOS, as well as on embedded platforms such as STM32, NXP, TI, ESP32, and other
Cortex-M and RISC-V microcontrollers. It can integrate with existing operating systems and TCP/IP stacks like FreeRTOS
and lwIP, or run on bare metal using Mongoose's built-in TCP/IP stack and network drivers.

To get started quickly, try [Mongoose Wizard](https://mongoose.ws/wizard/) - a visual Web UI builder that helps you
create professional device dashboards and connectivity without frontend expertise.

## 2-minute integration guide

**Step 1.** Follow [Build Tools](https://mongoose.ws/documentation/tutorials/tools/) to setup your development
environment
**Step 2.** Copy [mongoose.c](https://raw.githubusercontent.com/cesanta/mongoose/master/mongoose.c) and
[mongoose.h](https://raw.githubusercontent.com/cesanta/mongoose/master/mongoose.h) to your source tree
**Step 3.** Add the following snippets to your `main.c` file:

```c
#include "mongoose.h"

// Connection event handler function
static void ev_handler(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_HTTP_MSG) {  // New HTTP request received
    struct mg_http_message *hm = (struct mg_http_message *) ev_data;  // Parsed HTTP request
    if (mg_match(hm->uri, mg_str("/api/hello"), NULL)) {              // REST API call?
      mg_http_reply(c, 200, "", "{%m:%d}\n", MG_ESC("status"), 1);    // Yes. Respond JSON
    } else {
      struct mg_http_serve_opts opts = {.root_dir = ".", .fs = &mg_fs_posix};
      mg_http_serve_dir(c, hm, &opts);  // For all other URLs, Serve static files
    }
  }
}

int main() {
  struct mg_mgr mgr;  // Mongoose event manager. Holds all connections
  mg_mgr_init(&mgr);  // Initialise event manager
  mg_http_listen(&mgr, "http://0.0.0.0:8000", ev_handler, NULL);
  for (;;) {
    mg_mgr_poll(&mgr, 1000);  // Infinite event loop
  }
  return 0;
}
```

**Step 4.** Rebuild and run. Point your browser at [http://localhost:8000](http://localhost:8000/).

> NOTE: If you're building for some embedded system, create `mongoose_config.h` and add extra build flags in that file.
See [Build options](#build-options) for details.

## Connections and event manager

Mongoose has two basic data structures:

- `struct mg_mgr` - An event manager that holds all active connections
- `struct mg_connection` - A single connection descriptor

Connections could be listening, outbound, or inbound. Outbound connections are created by the `mg_connect()` call.
Listening connections are created by the `mg_listen()` call. Inbound connections are those accepted by a listening
connection. Each connection is described by a `struct mg_connection` structure, which has a number of fields. All
fields are exposed to the application by design, to give an application full visibility into Mongoose's internals.

Consider the snippet that starts an HTTP server:

```c
struct mg_mgr mgr;   // Event manager
mg_mgr_init(&mgr);   // Init manager
mg_http_listen(&mgr, "http://0.0.0.0:8000", fn, NULL);   // Setup HTTP listener
mg_http_listen(&mgr, "https://0.0.0.0:8443", fn, NULL);  // Setup HTTPS listener
for (;;) {                  // Infinite event loop
  mg_mgr_poll(&mgr, 1000);  // Process all connections
}
```

`mg_mgr_poll()` iterates over all connections, accepts new connections, sends and receives data, closes connections,
and calls event handler functions for the respective events.

Each connection has two event handler functions: `c->fn` and `c->pfn`. The `c->fn` is a user-specified event handler
function. The `c->pfn` is a protocol-specific handler function that is set implicitly. For example, a
`mg_http_listen()` sets `c->pfn` to a Mongoose's HTTP event handler. A protocol-specific handler is called before a
user-specific handler. It parses incoming data and may invoke protocol-specific events like `MG_EV_HTTP_MSG`. In the
snippet above, a user-specified `fn()` function will be called on every event, like incoming HTTP request.

> NOTE: Since Mongoose's core is not protected against concurrent accesses, make sure that all `mg_*` API functions are
called from the same thread or RTOS task.

## Send and receive buffers

Each connection has a send and receive buffer:

- `struct mg_connection::send` - Data to be sent to a peer
- `struct mg_connection::recv` - Data received from a peer

When data arrives, Mongoose appends received data to the `recv` and triggers a `MG_EV_READ` event. The user may send
data back by calling one of the output functions, like `mg_send()`, `mg_printf()` or a protocol-specific function like
`mg_ws_send`. Output functions append data to the `send` buffer. When Mongoose successfully writes data to the socket,
it discards data from struct `mg_connection::send` and sends an `MG_EV_WRITE` event.

## Event handler function

Each connection has an event handler function associated with it, which must be implemented by the user. Event handler
is the key element of Mongoose, since it defines the connection's behavior. See below for an example of an event
handler function:

```c
// Event handler function defines connection behavior
static void fn(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_READ) {
    mg_send(c, c->recv.buf, c->recv.len);   // Implement echo server
    c->recv.len = 0;                        // Delete received data
  }
}
```
- `struct mg_connection *c` - The connection receiving this event
- `int ev` - An event number, defined in mongoose.h. For example, when data arrives on an inbound connection, `ev`
would be `MG_EV_READ`
- `void *ev_data` - Points to the event-specific data, and it has a different meaning for different events. For
example, for an `MG_EV_READ` event, `ev_data` is a `long *` pointing to the number of bytes received from a remote peer
and saved into the `c->recv` IO buffer. The exact meaning of `ev_data` is described for each event. Protocol-specific
events usually have `ev_data` pointing to structures that hold protocol-specific information
- `c->fn_data`, `void *` - A user-defined pointer for the connection, which is a placeholder for application-specific
data. This `fn_data` pointer is set during the `*_listen()` or `*_connect()` call. Listening connections copy the value
of `c->fn_data` to the newly accepted connection, so all accepted connections initially share the same `fn_data`
pointer. It is fine to update/replace that pointer for any connection at any time by setting `c->fn_data = new_value;`

## Events

Below is the list of events triggered by Mongoose, taken as-is from `mongoose.h`. For each event, a comment describes
the meaning of the `ev_data` pointer passed to an event handler:

```c
enum {
  MG_EV_ERROR,      // Error                        char *error_message
  MG_EV_OPEN,       // Connection created           NULL
  MG_EV_POLL,       // mg_mgr_poll iteration        uint64_t *uptime_millis
  MG_EV_RESOLVE,    // Host name is resolved        NULL
  MG_EV_CONNECT,    // Connection established       NULL
  MG_EV_ACCEPT,     // Connection accepted          NULL
  MG_EV_TLS_HS,     // TLS handshake succeeded      NULL
  MG_EV_READ,       // Data received from socket    long *bytes_read
  MG_EV_WRITE,      // Data written to socket       long *bytes_written
  MG_EV_CLOSE,      // Connection closed            NULL
  MG_EV_HTTP_HDRS,  // HTTP headers                 struct mg_http_message *
  MG_EV_HTTP_MSG,   // Full HTTP request/response   struct mg_http_message *
  MG_EV_WS_OPEN,    // Websocket handshake done     struct mg_http_message *
  MG_EV_WS_MSG,     // Websocket msg, text or bin   struct mg_ws_message *
  MG_EV_WS_CTL,     // Websocket control msg        struct mg_ws_message *
  MG_EV_MQTT_CMD,   // MQTT low-level command       struct mg_mqtt_message *
  MG_EV_MQTT_MSG,   // MQTT PUBLISH received        struct mg_mqtt_message *
  MG_EV_MQTT_OPEN,  // MQTT CONNACK received        int *connack_status_code
  MG_EV_SNTP_TIME,  // SNTP time received           uint64_t *epoch_millis
  MG_EV_WAKEUP,     // mg_wakeup() data received    struct mg_str *data
  MG_EV_MDNS_REQ,   // mDNS request                 struct mg_mdns_req *
  MG_EV_MDNS_RESP,  // mDNS response                struct mg_mdns_resp *
  MG_EV_MODBUS_REQ, // Modbus TCP request           struct mg_modbus_req *
  MG_EV_USER        // Starting ID for user events
};
```

## Connection flags

`struct mg_connection` has a bitfield with connection flags. Flags are binary: they can be either 0 or 1. Some flags
are set by Mongoose and must be not changed by an application code. For example, the `is_udp` flag tells the
application if that connection is UDP or not. Some flags can be changed by application, for example, the `is_draining`
flag, if set by an application, tells Mongoose to send the remaining data to a peer, and when everything is sent, close
the connection.

> NOTE: User-changeable flags are: `is_hexdumping`, `is_draining`, `is_closing`.

This is taken from `mongoose.h` as-is:

```c
struct mg_connection {
  ...
  unsigned is_listening : 1;   // Listening connection
  unsigned is_client : 1;      // Outbound (client) connection
  unsigned is_accepted : 1;    // Accepted (server) connection
  unsigned is_resolving : 1;   // Non-blocking DNS resolv is in progress
  unsigned is_connecting : 1;  // Non-blocking connect is in progress
  unsigned is_tls : 1;         // TLS-enabled connection
  unsigned is_tls_hs : 1;      // TLS handshake is in progress
  unsigned is_udp : 1;         // UDP connection
  unsigned is_websocket : 1;   // WebSocket connection
  unsigned is_hexdumping : 1;  // Hexdump in/out traffic
  unsigned is_draining : 1;    // Send remaining data, then close and free
  unsigned is_closing : 1;     // Close and free the connection immediately
  unsigned is_full : 1;        // Stop reads, until cleared
  unsigned is_resp : 1;        // Response is still being generated
  unsigned is_readable : 1;    // Connection is ready to read
  unsigned is_writable : 1;    // Connection is ready to write
};
```

## Opening and closing connections

In order to open a listening (server) connection, call a corresponding function for the respective protocol. For
example, to open HTTP and MQTT servers,

```c
mg_http_listen(&mgr, "http://0.0.0.0:80", http_event_handler_fn, NULL);
mg_mqtt_listen(&mgr, "mqtt://0.0.0.0:1883", mqtt_event_handler_fn, NULL);
```

In order to open a listening connection for a custom protocol, use a plain TCP (or UDP if you wish) listener:

```c
mg_listen(&mgr, "tcp://0.0.0.0:1234", tcp_event_handler_fn, NULL);
```

In order to open a client connection, use the `mg_*connect()` function for the respective protocol:

- `mg_connect()` for plain TCP/UDP or custom protocol
- `mg_http_connect()` for HTTP
- `mg_ws_connect()` for Websocket
- `mg_mqtt_connect()` for MQTT
- `mg_sntp_connect()` for SNTP

Check out client examples for SMTP, SSDP, etc.

You pass the connect function an URL, Mongoose will asynchronously resolve the host name to an IP address via DNS, and
it can also resolve '.local' domain addresses using mDNS, if you open an mDNS listener yourself.

In order to close a connection, there is no dedicated function. You should tell Mongoose to close the connection using
connection flags. Inside your event handler function, use one of these two flags:

- `c->is_draining = 1;` - send all remaining data in the send buffer ("drain" the connection), then properly close the
connection.
- `c->is_closing = 1;` - close straight away, remove the connection on the next poll cycle regardless of any buffered
data or a clean TCP closure.

For example, this simple TCP echo server closes the connection right after echoing the first message back:

```c
static void fn(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_READ) {
    mg_send(c, c->recv.buf, c->recv.len); // Send received data back
    c->recv.len = 0;     // Clean receive buffer
    c->is_draining = 1;  // Close this connection when the response is sent
  }
}
```

## Architecture diagram

![Mongoose Architecture](https://mongoose.ws/documentation/images/mongoose.svg)

Mongoose Library can work on top of an existing TCP/IP stack - like on Windows, Mac, Linux, Zephyr RTOS, Azure RTOS,
lwIP, etc. Also it implements its own TCP/IP stack with drivers - so in embedded environments, especially bare metal
ones, it can be used stand-alone and does not need any exta software to implement networking.

Same goes with TLS. Mongoose can use 3rd party libraries like OpenSSL or mbedTLS, but it also implements its own TLS
1.3 stack. Hence, Mongoose Library can be a one-stop solution to provide the whole network functionality, including
secure communication over TLS.

## Build options

Mongoose source code ships in two files: [mongoose.h](https://github.com/cesanta/mongoose/blob/master/mongoose.h) (API
definitions) and [mongoose.c](https://github.com/cesanta/mongoose/blob/master/mongoose.c) (Implementation). In order to
specify build options, create a third file called `mongoose_config.h` and specify the options there, for example:

```c
#define MG_ARCH MG_ARCH_ARMGCC
#define MG_IO_SIZE 1024
```

| Name | Default | Description |
| --- | --- | --- |
| MG\_ARCH | Autodetected | See [arch.h](https://github.com/cesanta/mongoose/blob/master/src/arch.h) |
| MG\_TLS | MG\_TLS\_NONE | TLS implementation to use. Valid options:   MG\_TLS\_NONE   MG\_TLS\_BUILTIN
MG\_TLS\_MBED   MG\_TLS\_OPENSSL   MG\_TLS\_WOLFSSL |
| MG\_ENABLE\_IPV6 | 0 | Enable IPv6 |
| MG\_ENABLE\_MD5 | 1 | Enable MD5 implementation |
| MG\_ENABLE\_SSI | 1 | Enable serving SSI files by \`mg\_http\_serve\_dir() |
| MG\_ENABLE\_CUSTOM\_CALLOC | 0 | Provide custom `mg_calloc()` and `mg_free()` |
| MG\_ENABLE\_CUSTOM\_RANDOM | 0 | Provide custom RNG function mg\_random() |
| MG\_ENABLE\_CUSTOM\_MILLIS | 0 | Enable custom `mg_millis()` function |
| MG\_ENABLE\_POSIX\_FS | Autodetected | Enable POSIX fopen/fread/.. functions. Valid options: 0 or 1 |
| MG\_ENABLE\_FATFS | 0 | Enable embedded FAT FS support |
| MG\_ENABLE\_LINES | undefined | If defined, show source file names in logs |
| MG\_IO\_SIZE | 2048 | Granularity of the send/recv IO buffer growth. Set to 256 on the smallest system with tiny RAM,
and 32768 on the big systems like OSes - Linux, Mac, Windows |
| MG\_MAX\_RECV\_SIZE | 3145728 | Maximum recv buffer size. If a connection's receive buffer grows more, the connection
gets closed automatically |
| MG\_MAX\_HTTP\_HEADERS | 40 | Maximum number of HTTP headers |
| MG\_HTTP\_INDEX | "index.html" | Index file for HTML directory |
| MG\_FATFS\_ROOT | "/" | FAT FS root directory |
| MG\_ENABLE\_SOCKET | 1 | Use BSD socket low-level API |
| MG\_ENABLE\_LWIP | 0 | lwIP network stack |
| MG\_ENABLE\_FREERTOS\_TCP | 0 | Amazon FreeRTOS-Plus-TCP network stack |
| MG\_ENABLE\_RL | 0 | Keil MDK network stack |
| MG\_ENABLE\_TCPIP | 0 | Built-in Mongoose TCP/IP stack |
| MG\_ENABLE\_TCPIP\_PRINT\_DEBUG\_STATS | 0 | Print built-in Mongoose TCP/IP stack stats every second |
| MG\_ENABLE\_DRIVER\_\* | undefined | Enable specific Mongoose TCP/IP stack driver. Available options:
MG\_ENABLE\_DRIVER\_STM32F   MG\_ENABLE\_DRIVER\_STM32H   MG\_ENABLE\_DRIVER\_STM32N   MG\_ENABLE\_DRIVER\_IMXRT10
MG\_ENABLE\_DRIVER\_IMXRT11   MG\_ENABLE\_DRIVER\_MCXE   MG\_ENABLE\_DRIVER\_MCXN   MG\_ENABLE\_DRIVER\_RW612
MG\_ENABLE\_DRIVER\_CMSIS   MG\_ENABLE\_DRIVER\_RA6   MG\_ENABLE\_DRIVER\_RA8   MG\_ENABLE\_DRIVER\_SAME54
MG\_ENABLE\_DRIVER\_TM4C   MG\_ENABLE\_DRIVER\_TMS570   MG\_ENABLE\_DRIVER\_XMC7   MG\_ENABLE\_DRIVER\_XMC
MG\_ENABLE\_DRIVER\_W5100   MG\_ENABLE\_DRIVER\_W5500   MG\_ENABLE\_DRIVER\_PICO\_W   MG\_ENABLE\_DRIVER\_CYW
MG\_ENABLE\_DRIVER\_CYW\_SDIO   MG\_ENABLE\_DRIVER\_NXP\_WIFI   MG\_ENABLE\_DRIVER\_PPP |
| MG\_TCPIP\_PHY\_ADDR | 0 | PHY address (for built-in stack only) |
| MG\_DRIVER\_MDC\_CR | 4 | MDC CR divider for Ethernet MAC (for built-in stack only) |
| MG\_SET\_MAC\_ADDRESS(mac) |  | Set MAC address (for built-in stack only) |

> NOTE: most build constants are defined in [src/config.h](https://github.com/cesanta/mongoose/blob/master/src/config.h)

> NOTE: the `MG_IO_SIZE` constant also sets the maximum UDP message size, see
[issues/907](https://github.com/cesanta/mongoose/issues/907) for details. If your application uses large UDP messages,
increase the `MG_IO_SIZE` limit accordingly.

> If your architecture is not listed in the See [arch.h](https://github.com/cesanta/mongoose/blob/master/src/arch.h),
then set your architecture as `MG_ARCH_CUSTOM` and specify all necessary includes for your build environment:

```c
#include <stdint.h>
#include <stdbool.h>
#include <stdarg.h>
// ... other includes ...

#define MG_ARCH MG_ARCH_CUSTOM
//  ... other options ...
```

## Using JSON

Mongoose Library is often used to implement RESTful services, which use JSON format for data exchange. Therefore
Mongoose provides functions to [parse JSON strings](#json) and [create JSON strings](#mg_snprintf-mg_vsnprintf) easily.

For example, the following event handler function handles a POST request to the `/api/sum` URI. The POST body is
expected to be a JSON array of two numbers, like `[123.38, -2.72]`. Here is an example `curl` command that generates
such request:

```sh
curl localhost:8000/api/sum -d '[123.38, -2.72]'
```

The handler returns the sum of those two numbers. The `mg_json_get_num()` function is used to extract values from the
JSON string, and `mg_http_reply()` prints a JSON string back:

```c
static void fn(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_HTTP_MSG) {
    struct mg_http_message *hm = (struct mg_http_message *) ev_data;
    if (mg_match(hm->uri, mg_str("/api/sum"), NULL)) {
      double num1 = 0.0, num2 = 0.0;
      mg_json_get_num(hm->body, "$[0]", &num1);  // Extract first number
      mg_json_get_num(hm->body, "$[1]", &num2);  // Extract second number
      mg_http_reply(c, 200, "Content-Type: application/json\r\n",
                    "{%m:%g}\n", MG_ESC("result"), num1 + num2);
    } else {
      ...
    }
  }
```

There is also a set of functions to ease server-side processing by means of [RPC](#rpc) methods.

The following tutorials have working usage examples:

- [REST basics](https://mongoose.ws/documentation/tutorials/webui/webui-rest/)
- [Websocket server](https://mongoose.ws/documentation/tutorials/websocket/websocket-server/)
- [Websocket client](https://mongoose.ws/documentation/tutorials/websocket/websocket-client/)
- [JSON-RPC over WS](https://mongoose.ws/documentation/tutorials/websocket/json-rpc-over-websocket/)
- [Pure JavaScript UI](https://mongoose.ws/documentation/tutorials/webui/webui-plain/)
- [Data push](https://mongoose.ws/documentation/tutorials/webui/webui-push/)

## Built-in TCP/IP stack

Mongoose works on any system that provides BSD socket API. In other words, it works on top of any BSD-compatible TCP/IP
stack. That includes UNIX, Mac, Windows systems, as well as some embedded TCP/IP stacks like lwIP. However, Mongoose
provides its own TCP/IP stack that can be activated by the build option `MG_ENABLE_TCPIP` set to `1`. It can be done
either by setting compiler flags or via `mongoose_config.h`:

- Via the compiler flags (e.g.: gcc): add `-D MG_ENABLE_TCPIP=1` to the build flags
- Via `mongoose_config.h`: add the following line:
	```c
	#define MG_ENABLE_TCPIP 1           // Enable built-in TCP/IP stack
	```

Mongoose's TCP/IP stack provides a [driver
API](https://github.com/cesanta/mongoose/blob/90a23fe/src/net_builtin.h#L10-L15) that makes it easy to create a driver.
There is a bunch of built-in drivers available, for example STM32 F2/F4/F7, STM32 H5/H7, SAME54, TM4C, W5500. You can
take a look at their implementation in the [src/drivers/](https://github.com/cesanta/mongoose/tree/master/src/drivers)
directory. Every driver gets activated by its respective build option, for example the STM32H5 driver needs
`MG_ENABLE_DRIVER_STM32H` set to `1`:

- Via the compiler flags: add `-DMG_ENABLE_DRIVER_STM32H=1` to the build flags
- Via `mongoose_config.h`: add the following line:
	```c
	#define MG_ENABLE_DRIVER_STM32H 1   // Enable STM32H network driver
	```
- For more information on how to develop your own driver, follow the [CMSIS-Driver
tutorial](https://mongoose.ws/documentation/tutorials/cmsis_driver)

In addition to this, [Mongoose Wizard](#mongoose-wizard) generates code for several standard boards.

- For more information on how to configure Mongoose for your own board, follow the [Hardware
tutorial](https://mongoose.ws/documentation/tutorials/hardware/)

### Configuration and state

```c
struct mg_tcpip_if {
  uint8_t mac[sizeof(struct mg_l2addr)];  // MAC address; must be set to a valid address
  uint32_t ip, mask, gw;                  // Static IPv4 address, netmask, gateway; 0 = use DHCP
  struct mg_str tx;                       // TX frame buffer (managed by the stack)
  bool enable_dhcp_client;                // Enable DHCP client; auto-set if ip==0
  bool enable_dhcp_server;                // Enable DHCP server
  bool enable_get_gateway;                // DHCP server offers itself as the default gateway
  bool enable_req_dns;                    // DHCP client requests a DNS server address
  bool enable_req_sntp;                   // DHCP client requests an SNTP server address
  bool enable_fcs_check;                  // Verify and strip FCS from received frames
  bool enable_mac_check;                  // Drop frames not addressed to this MAC
  bool update_mac_hash_table;             // Signal driver to refresh MAC multicast hash table
  struct mg_tcpip_driver *driver;         // Hardware driver; must be set before mg_tcpip_init()
  void *driver_data;                      // Passed to all driver functions as ifp->driver_data
  mg_tcpip_event_handler_t fn;            // User event handler for MG_TCPIP_EV_* events
  struct mg_mgr *mgr;                     // Mongoose event manager; set by mg_tcpip_init()
  char dhcp_name[MG_TCPIP_DHCPNAME_SIZE]; // Hostname sent in DHCP requests; defaults to "mip"
  uint16_t mtu;                           // IP MTU (max payload size at the IP layer)
  uint16_t framesize;                     // Maximum L2 frame size in bytes

#if MG_ENABLE_IPV6
  uint64_t ip6ll[2], ip6[2];  // IPv6 link-local and global addresses
  uint8_t prefix[8];          // Global prefix bytes
  uint8_t prefix_len;         // Global prefix length in bits
  uint64_t gw6[2];            // IPv6 default gateway
  bool enable_slaac;          // Enable SLAAC (stateless address autoconfiguration)
  bool enable_dhcp6_client;   // Enable DHCPv6 client (not yet fully implemented)
  bool is_ip6_changed;        // Set by stack when IPv6 address changes
#endif

  enum mg_l2type l2type;                  // Layer-2 type: Ethernet, PPP, etc. (see l2.h)
  union mg_l2data l2data;                 // Layer-2 config and state (see l2.h)

  // Internal state, user can use it but should not change it
  uint8_t state;                  // Current link and IPv4 state
#define MG_TCPIP_STATE_DOWN 0       // Physical link is down
#define MG_TCPIP_STATE_LINK_UP 1    // Driver reports physical link is up
#define MG_TCPIP_STATE_UP 2         // L2 is ready (e.g. PPP negotiated)
#define MG_TCPIP_STATE_REQ 3        // DHCP REQUESTING: waiting for DHCP offer
#define MG_TCPIP_STATE_IP 4         // IP address assigned; resolving gateway MAC
#define MG_TCPIP_STATE_READY 5      // Fully operational; gateway MAC resolved
#if MG_ENABLE_IPV6
  uint8_t state6;                 // Current IPv6 link/IP state (MG_TCPIP_STATE_*)
#endif
};
```

This is best understood by following an example, please check one of our working [tutorials](#tutorials) for your chip.
In addition, [Mongoose Wizard](#mongoose-wizard) generates code for several standard boards and takes advantage of a
series of macros that allow a seamless configuration

Configure `fn` if you need to enable an interface event handler triggered on [Interface events](#interface-events)

`l2-type` defaults to Ethernet `MG_TCPIP_L2_ETH`, you can set it to:

- `MG_TCPIP_L2_PPP` for PPP, see [this
example](https://github.com/cesanta/mongoose/tree/master/tutorials/mqtt/mqtt-client/arduino/sim800-mqtt)
- `MG_TCPIP_L2_PPPoE` for PPPoE, see [this
example](https://github.com/cesanta/mongoose/tree/master/tutorials/stm32/nucleo-f746zg/minimal-pppoe)

`l2data` is usually handled by the stack, but either for plain Ethernet or even PPPoE, you can set a VLAN id to use:

```c
struct mg_tcpip_if mif = {
  ...
  .l2data.eth = {.vlan_id = 3} // enable 802.1Q tagging, use VLAN id 3 for all traffic
};
```

Otherwise, it defaults to 0, no 802.1Q tagging, and this feature is not used.

### Interface events

Mongoose's TCP/IP stack allows users to define an interface event handler, that will be called when certain events
occur:

```c
enum {
  MG_TCPIP_EV_STATE_CHANGE,  // state change                   uint8_t *(&ifp->state)
  MG_TCPIP_EV_DHCP_DNS,      // DHCP DNS assignment            uint32_t *ipaddr
  MG_TCPIP_EV_DHCP_SNTP,     // DHCP SNTP assignment           uint32_t *ipaddr
  MG_TCPIP_EV_ARP,           // Got ARP packet                 struct mg_str *
  MG_TCPIP_EV_TIMER_1S,      // 1 second timer                 NULL
  MG_TCPIP_EV_DRIVER,         // Driver event                  driver specific
  MG_TCPIP_EV_STATE6_CHANGE,  // state6 change                 uint8_t *(&ifp->state6)
  MG_TCPIP_EV_USER            // Starting ID for user events
};
```

Usage example:

- see [tap-driver](https://github.com/cesanta/mongoose/tree/master/tutorials/tcpip/tap-driver)

## Built-in TLS stack

Mongoose implements a built-in TLS 1.3 stack. It can be enabled by one of the following ways:

- Via the compiler flags: add `-DMG_TLS=MG_TLS_BUILTIN` to the build flags
- Via `mongoose_config.h`: add the following line:
	```c
	#define MG_TLS MG_TLS_BUILTIN  // Enable built-in TLS 1.3 stack
	```

## Built-in OTA updates

Supported architectures:

| **MG\_OTA value** | **Description** |
| --- | --- |
| MG\_OTA\_NONE | No OTA support |
| MG\_OTA\_STM32H5 | STM32 H5 series |
| MG\_OTA\_STM32H7 | STM32 H7 series |
| MG\_OTA\_STM32H7\_DUAL\_CORE 3 | STM32 H7 dual core series |
| MG\_OTA\_STM32F | STM32 F7/F4/F2 series |
| MG\_OTA\_CH32V307 | WCH CH32V307 |
| MG\_OTA\_U2A | Renesas U2A16, U2A8, U2A6 |
| MG\_OTA\_RT1020 | NXP IMXRT1020 |
| MG\_OTA\_RT1050 | NXP IMXRT1050 |
| MG\_OTA\_RT1060 | NXP IMXRT1060 |
| MG\_OTA\_RT1064 | NXP IMXRT1064 |
| MG\_OTA\_RT1170 | NXP IMXRT1170 |
| MG\_OTA\_MCXN | NXP MCXN947 |
| MG\_OTA\_RW612 | NXP RW612 |
| MG\_OTA\_FLASH | OTA via an internal flash |
| MG\_OTA\_ESP32 | ESP32, ESP32Sx, ESP32Cx |
| MG\_OTA\_PICOSDK | RP2040/2350 using Pico-SDK |
| MG\_OTA\_CUSTOM | Custom implementation |

See [src/ota.h](https://github.com/cesanta/mongoose/blob/master/src/ota.h) for more information and API.

If `MG_OTA_CUSTOM` is set to `1` in `mongoose_config.h`, then the user must provide implementation for the following
functions: `ota_begin()`, `ota_write()`, and `ota_end()`.

See [Firmware Update tutorial](https://mongoose.ws/documentation/tutorials/firmware-update/) for more details.

## Reference projects

Mongoose Library provides several reference projects - "complete" projects that can be used as a base for a production
firmware.

## Web UI dashboard

See the [Web UI dashboard guide](https://mongoose.ws/documentation/tutorials/device-dashboard/)

## IoT fleet management

See the [IoT fleet management guide](https://mongoose.ws/documentation/tutorials/mqtt-dashboard/)

## Best practices

- Debug log. To increase debug verbosity, call `mg_log_set()`:
	```c
	mg_log_set(MG_LL_DEBUG);
	mg_mgr_init(&mgr);
	```
	The `MG_INFO()`, `MG_DEBUG()` logging macros use `putchar()` by default, i.e. they use standard C `stdout`
stream. That works fine on the traditional OS. In the embedded environment, in order to see debug output, two ways are
possible: IO retargeting or Mongoose log redirection. IO retargeting can already be implemented by an embedded SDK -
for example ESP32 SDK redirects `printf()` to the UART0. Otherwise, IO retargeting can be implemented manually, see
[guide](https://github.com/cpq/bare-metal-programming-guide#redirect-printf-to-uart) for more details. The alternative
way is to redirect Mongoose logs:
	```c
	void log_fn(char ch, void *param) {
	  output_a_single_character_to_UART(ch);
	}
	...
	mg_log_set_fn(log_fn, param);  // Use our custom log function
	```
- If you need to perform any sort of initialisation of your connection, do it by catching `MG_EV_OPEN` event. That
event is sent immediately after a connection has been allocated and added to the event manager, but before anything
else:
	```c
	static void fn(struct mg_connection *c, int ev, void *ev_data) {
	  if (ev == MG_EV_OPEN) {
	    ... // Do your initialisation
	  }
	```
- If you need to keep some connection-specific data, you have two options:
	- Use the `c->fn_data` pointer. That pointer is passed to the event handler as its last parameter:
		```c
		static void fn(struct mg_connection *c, int ev, void *ev_data) {
		  if (ev == MG_EV_OPEN) {
		    c->fn_data = malloc(123);       // Change our fn_data
		  } else if (ev == MG_EV_CLOSE) {
		    free(fn_data);  // Don't forget to free!
		  }
		  ...
		}
		// Every accepted connection inherits a NULL pointer as c->fn_data,
		// but then we change it in its connection event handler to something else
		mg_http_listen(&mgr, "http://localhost:1234", fn, NULL);
		```
		- Use the `c->data` buffer, which can hold some amount of connection-specific data without extra memory
allocation:
		```c
		static void fn(struct mg_connection *c, int ev, void *ev_data) {
		  if (ev == MG_EV_WS_OPEN) {
		    c->data[0] = 'W'; // Established websocket connection, store something
		    ...
		```
- Use the `mg_http_reply()` function to create HTTP responses. That function properly sets the `Content-Length` header,
which is important. Of course you can create responses manually, e.g. with `mg_printf()` function, but be sure to set
the `Content-Length` header:
	```c
	mg_printf(c, "HTTP/1.1 200 OK\r\Content-Length: %d\r\n\r\n%s", 2, "hi");
	```
	Alternatively, use chunked transfer encoding:
	```c
	mg_printf(c, "HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n");
	mg_http_printf_chunk(c, "%s", "foo");
	mg_http_printf_chunk(c, "%s", "bar");
	mg_http_printf_chunk(c, "");  // Don't forget the last empty chunk
	```
	> NOTE: if you are not using `mg_http_reply()` or `mg_http_*_chunk()`, make sure to set `c->is_resp = 0;` when
your event handler finished writing its response.
- Send and receive buffers, and the number of accepted connections, can grow indefinitely. If you need to keep a bound
on them, you can do that in your respective event handlers:
	```c
	static inline numconns(struct mg_mgr *mgr) {
	  int n = 0;
	  for (struct mg_connection *t = mgr->conns; t != NULL; t = t->next) n++;
	  return n;
	}
	static void fn(struct mg_connection *c, int ev, void *ev_data) {
	  if (ev == MG_EV_ACCEPT) {
	    if (numconns(c->mgr) > LIMIT) {
	      MG_ERROR(("Too many connections"));
	      c->is_closing = 1;
	    }
	  } else if (ev == MG_EV_READ) {
	    if (c->recv.len > LIMIT) {
	      MG_ERROR(("Msg too large"));
	      c->is_draining = 1;
	    }
	  }
	  ...
	}
	```
	```c
	if (c->send.len > LIMIT) {
	  MG_ERROR(("Stalled"));
	} else {
	  // send
	}
	```
	- Mongoose uses this technique internally to shape traffic when serving large files; you don't need to do this
unless you are dynamically sending data.
		- In more complex scenarios, you can also [limit memory allocation to a fixed memory
pool](https://www.youtube.com/watch?v=8rA8-uSzGWA)
- On embedded environments, make sure the serving task has enough stack: give it 2k for simple RESTful serving, or 4-8k
for complex dynamic/static serving. In certain environments, it is necessary to adjust heap size, too. By default, IO
buffer allocation size `MG_IO_SIZE` is 2048: change it to 512 to trim run-time per-connection memory consumption.
	- If using TLS, the `MG_MAX_RECV_SIZE` limit must accomodate the largest record (16424 bytes), and the value of
`MG_IO_SIZE` will affect decryption performance when receiving large content.
- On the other hand, in scenarios where data accumulates faster than it can be consumed, as for example, in TLS large
file transfers, you might want to make `MG_IO_SIZE` larger to speed it up.
- In order to benchmark mongoose, create a server that is able to respond with content of different sizes. You can use
the following code:
	```c
	#include "mongoose.h"
	static void mg_hfn_push_data(struct mg_connection *c) {
	  size_t left = *(size_t *) c->data;  // Bytes left to send
	  if (left > 0 && c->send.len < MG_IO_SIZE) {
	    const char chunk[] = "abcdefghijklmnopqrstubwxyz0123456789\n";
	    size_t cs = sizeof(chunk) - 1;
	    while (left >= cs && c->send.len < MG_IO_SIZE * 2) {
	      mg_send(c, chunk, cs);
	      left -= cs;
	    }
	    if (left < cs) {
	      if (left > 0) mg_send(c, chunk, left - 1);
	      if (left > 0) mg_send(c, "\n", 1);
	      left = 0;
	    }
	    *(size_t *) c->data = left;
	    if (left == 0) c->is_resp = 0;
	  }
	}
	// Implement a simple server with the following endpoints:
	//    URI       POST data        Description
	//    /debug    {"level": 0}     Set server debug level, from 0 to 4
	//    /?SIZE    n/a              Send a text response, default size is 256
	void ev_handler(struct mg_connection *c, int ev, void *ev_data) {
	  if (ev == MG_EV_HTTP_MSG) {
	    struct mg_http_message *hm = (struct mg_http_message *) ev_data;
	    if (mg_match(hm->uri, mg_str("/debug"), NULL)) {
	      int level = (int) mg_json_get_long(hm->body, "$.level", MG_LL_DEBUG);
	      mg_log_set(level);
	      mg_http_reply(c, 200, "", "Debug level set to %d\n", level);
	    } else {
	      size_t size = (size_t) mg_json_get_long(hm->query, "$", 256);
	      if (size == 0) size = 256;
	      *(size_t *) c->data = size;
	      c->is_resp = 1;
	      mg_printf(c, "HTTP/1.1 200 OK\nContent-Length: %lu\n\n", size);
	      mg_hfn_push_data(c);
	    }
	  } else if (ev == MG_EV_POLL) {
	    mg_hfn_push_data(c);
	  }
	}
	int main() {
	  struct mg_mgr mgr;  // Mongoose event manager. Holds all connections
	  mg_mgr_init(&mgr);  // Initialise event manager
	  mg_http_listen(&mgr, "http://0.0.0.0:8000", ev_handler, NULL);
	  for (;;) {
	    mg_mgr_poll(&mgr, 1000);  // Infinite event loop
	  }
	  return 0;
	}
	```

## Mongoose Wizard

Mongoose Wizard is a no-code visual tool for creating connected applications on embedded devices. Mongoose Wizard
generates ready-to-go projects for a variety of microcontrollers, as well as for Windows/Mac/Linux, which makes it very
easy to develop/iterate/test. You can start using Mongoose Wizard immediately at
[https://mongoose.ws/wizard/](https://mongoose.ws/wizard/).

We recommend to watch video tutorials from this YouTube playlist: [Mongoose Wizard
Tutorials](https://www.youtube.com/watch?v=vJF5repAxXY&list=PL_hLobTQiQqD_uLh6H55KfZbtJkiuWvkF)

## Concept

The core concept of Mongoose Wizard is the JSON configuration file, which describes your application options, target
hardware / software, Web UI, and RESTful API.

Mongoose Wizard's frontend is a visual way of editing configuration file. Alternatively, it can be edited manually
using your favorite editor.

Mongoose Wizard's backend takes a configuration file as an input, and generates a ready-to-go project as an output. You
can download that project to your workstation and build/flash/run it. Alternatively, if you're using Chrome browser
(which provides Web USB support), you can build and flash generated project directly from a browswer.

The network functionality is generated using Mongoose Library, and interfaces with the rest of the firmware via a set
of "glue" functions and structures. The glue API is consolidated in the `mongoose_glue.{c,h}` files, and is meant to be
modified by the user to "glue" the generated functionality to the hardware.

For example, a Web UI can show a panel with a toggle button, and the generated glue code is:

- a structure with a boolean value
- a getter and setter functions for that structure

Generated in `mongoose_glue.h`:

```c
struct leds {
  bool led1;
};
```

Generated in `mongoose_glue.c`:

```c
// Generated default code maps Web UI toggle button to the structure
struct leds s_leds = {false};

void glue_get_leds(struct leds *leds) {
  // Insert your code here to sync s_leds to your hardware
  *leds = s_leds;
}
void glue_set_leds(struct leds *leds) {
  s_leds = *leds;
  // Insert your code here to sync s_leds to your hardware
}
```

## Overriding default glue callbacks

In order to glue that implementation to the hardware, a getter and setter function should be modified to "synchronise"
the hardware to the structure. This is done by following steps:

1. Create getter and setter functions with the same signature as the default ones but with the different name - for
example, change `glue_` prefix to `my_`:
```c
void my_get_leds(struct leds *leds) {
  leds->led1 = gpio_read(LED1);  // Read hardware, populate structure
}
void my_set_leds(struct leds *leds) {
  gpio_write(LED1, leds->led1); // Read structure, sync to hardware
}
```
2. Substitute the default glue callbacks with your custom ones by calling `mongoose_set_http_handlers()` after
`mongoose_init()`:
```c
mongoose_init();
mongoose_set_http_handlers("leds", my_get_leds, my_set_leds);  // <-- Add this
for (;;) {
  mongoose_poll();
}
```

Different REST API endpoint types generate use different callbacks. The list below contains the summary:

```c
mongoose_set_http_handlers("data", my_get_XXX, my_set_XXX);
mongoose_set_http_handlers("array", my_get_XXX, my_set_XXX);
mongoose_set_http_handlers("action", my_check_XXX, my_start_XXX);
mongoose_set_http_handlers("file", my_read_XXX, my_write_XXX);
mongoose_set_http_handlers("ota", my_open_XXX, my_close_XXX, my_write_XXX);
```

Similarly, callback for other protocols can be overridden too. Here is the relevant API:

```c
struct mongoose_mqtt_handlers {
  struct mg_connection *(*connect_fn)(mg_event_handler_t);
  void (*tls_init_fn)(struct mg_connection *);
  void (*on_connect_fn)(struct mg_connection *, int);
  void (*on_message_fn)(struct mg_connection *, struct mg_str, struct mg_str);
  void (*on_cmd_fn)(struct mg_connection *, struct mg_mqtt_message *);
};
void mongoose_set_mqtt_handlers(struct mongoose_mqtt_handlers *);

struct mongoose_modbus_handlers {
  bool (*read_reg_fn)(uint16_t address, uint16_t *value);
  bool (*write_reg_fn)(uint16_t address, uint16_t value);
};
void mongoose_set_modbus_handlers(struct mongoose_modbus_handlers *);

void mongoose_set_sntp_handler(void (*fn)(uint64_t epoch_ms));

void mongoose_set_auth_handler(int (*fn)(const char *user, const char *pass));
```

## Configuration file format

Configuration file has several sections, annotated below:

```js
{
  "version": "1.0.1",   // format version
  "api":     { ... },   // RESTful API definitions
  "ui":      { ... },   // Web UI controls
  "http":    { ... },   // HTTP protocol support
  "mqtt":    { ... },   // MQTT protocol support
  "dns":     { ... },   // DNS/MDNS protocol support
  "sntp":    { ... },   // SNTP (network time sync) protocol support
  "modbus":  { ... },   // Modbus-TCP protocol support
  "build":   { ... }    // Target hardware, IDE, OS
}
```

## REST API

Below is the annotated REST API snippet from the configuration file:

```js
"api": {                 // RESTful API endpoints. 4 types: data, array, action, upload, ota
  "reboot": {
    "type": "action",    // An action endpoint maps to a button. A button click triggers an action
    "read_level": 3,     // Read access level
    "write_level": 7,    // Write access level
    "value": false       // Default action value - false (not triggered)
  },
  "firmware_update": {
    "type": "ota",       // A firmware update endpoint - maps to a button that trigger file upload
    "read_level": 3,     // Read access level
    "write_level": 7     // Write access level
  },
  "file": {
    "type": "file",      // A file upload endpoint - maps to a button that trigger file upload
    "read_level": 3,     // Read access level
    "write_level": 7     // Write access level
  },
  "state": {             // struct state will be generated in the glue code
    "type": "data",      // Data endpoint maps to a Web UI panel, and a C structure
    "readonly": true,    // Optional attribute that prevents generation of the setter function
    "read_level": 3,     // Read access level
    "attributes": {      // Structure attributes
      "speed": { "type": "int", "value": 42},  // Integer and its default value
      "humidity": { "type": "double", "format": "%.4f", "value": 12.34}, // Double, its format and its default value
      "version": { "type": "string", "size": 20, "value": "1.0.0"},     // String, its size and its default value
      "online": { "type": "bool", "value": true}    // A Boolean and its default value
    }
  },
  "levels": {
    "type": "array",     // Generates array of objects
    "read_level": 3,     // Read access level
    "write_level": 7     // Write access level
    "attributes": {
      "name": { "type": "string", "value": "info", "size": 20},
      "level": { "type": "int", "value": 2}
    }
  },
  "local": {
    "type": "local",     // Local to Web UI, does not create any REST endpoint
    "read_level": 3,     // Read access level
    "write_level": 7     // Write access level
    "attributes": {...}  // Just like for the data endpoint
  }
},
```

See this video for the detailed explanation of the REST API endpoints:
[https://www.youtube.com/watch?v=gM-bzh\_H-tM](https://www.youtube.com/watch?v=gM-bzh_H-tM)

Below is a brief explanation of the REST API configuration and the corresponding usage using the `curl` command.

### REST API of type 'data'

Configuration:

```json
"settings": {
  "type": "data",
  "attributes": {
    "level": { "type": "int", "value": 42},
    "name": { "type": "string", "value": "unit1", "size": 20}
  }
}
```

Usage:

```sh
$ curl IP/api/settings
{"level": 42, "name": "unit1"}
$ curl IP/API/settings -d '{"level": 10}'
{"level": 10, "name": "unit1"}
```

### REST API of type 'array'

Configuration:

```json
"wifi": {
  "type": "sensors",
  "attributes": {
    "type": { "type": "int", "value": 10},
    "name": { "type": "string", "value": "temp1", "size": 20}
  }
}
```

Usage:

```sh
$ curl IP/api/sensors
[{"type": 0, "name": "temp1"}, {"type": 1, "name": "humidity1"}]
$ curl IP/API/sensors/1 -d '{"type": 2}'
[{"type": 0, "name": "temp1"}, {"type": 2, "name": "humidity1"}]
```

## Web UI

If Web UI is enabled in the http settings (`http.ui` set to `true`), then the `ui` section of the configuration
describes the UI dashboard that will be rendered.

```js
"ui": {
  "pages": [             // Describes UI pages. Each page is mapped on a sidebar
    {
      "title": "Dashboard",  // Page title
      "icon": "desktop",     // Page icon
      "level": 0,            // Access level
      "classes": "page",     // CSS classes (optional)
      "css": "",             // Inline CSS styles (optional)
      "layout": [ ... ]      // Child elements (optional)
    }
  ]
},
```

The "layout" attribute for pages describe UI elements, which could be nested. Here's the format for the UI element:

```js
{
  "type": "",             // Optional. Can be "toggle", "action", "dropdown", "input", "upload", "ota". If absent,
generates "div" element
  "format": "hi!",        // Optional. Static text / HTML code. Can contain references to API data: "Current
temperature: ${state.temperature}"
  "classes": "flex",      // Optional. CSS classes
  "css": "color: red;",   // Optional. Inline CSS styles
  "layout": [ ... ]       // Optional. Nested elements
}
```

## Element types

Note: all elements can have `classes` and `css` attributes.

Container. Use `flex` class for horizonal, `flex flex-col` for vertical flex. The most common issue is to set the width
of the child elements - for example, panels, or titles. Here is the quick guide:

- To set a fixed width, use `"css": "flex: 0 0 10em;"` or `"css": "flex: 0 0 20%;"`
- To set an equal width, use `"classes": "flex-1"`
- Otherwise, an item will be sized to accomodate its content
```js
{ "classes": "flex", "layout": []}
```

Text / label

```js
{ "format": "hi!", "classes": "text-sm font-bold", "css": "color: red;" }
```

> Text can include HTML markup, and also special notation `${OBJECT.ATTRIBUTE}`, which substitutes by the respective
API value. For example: `Current temperature: <b>${state.temperature}</b>`

Input

```js
{ "type": "input",  "ref": "OBJECT_API.ATTRIBUTE" }
```

Toggle

```js
{ "type": "toggle",  "ref": "OBJECT_API.ATTRIBUTE" }
```

Dropdown

```js
{ "type": "dropdwon",  "ref": "OBJECT_API.ATTRIBUTE", "options": "aa,bb,cc" }
```

File Upload

```js
{ "type": "updload",  "ref": "UPLOAD_API_NAME" }
```

OTA (firmware update)

```js
{ "type": "ota",  "ref": "OTA_API_NAME" }
```

Action (rendered as a pushbutton, triggers an action on click)

```js
{ "type": "action",  "ref": "ACTION_API_NAME" }
```

Graph

```js
{
  "type": "graph",
  "ref": "graph_data",  // Custom endpoint returing array of [time,val] pairs
                        // Or, a websocket reference websocket.NAME
  "options": {          // options are optional !
    "xrange": 15,       // X axis span in seconds
    "updateMs": 25,     // For websocket, update interval in milliseconds
    "uplot": {...}      // uplot settings, e.g. {"scales": {"y": {"auto": false, "min":0, "max": 100}}}
  }
}
```

## Expressions

Element's attributes can have embedded Javascript expressions inside. For example, element's `css` attribute, which
translates to the HTML `style`, can be a simple text like `color: red;`, but can also contain expressions.

Javascript expressions are specified inside the curly brackets prepended by the dollar sign: `${...}`. Expressions can
be conditional, which allows to alter any element depending on the value of the REST API. For example, this alters the
background of element:

```
"css": "color: cyan; background: ${state.online ? 'green': 'red'};"
```

## Attributes

Below is the list of valid attributes that any element can have:

- `classes` - (any element) a string, space separated list of CSS classes, e.g.
- `css` - (any element) a string, semicolon-separated list of CSS rules
- `disabled` - (input, toggle, dropdown) a boolean, either `true` or `false`
- `min,max` - (gauge, progress) a number
- `min,max,step` - (number input) a number
- `readonly` - (input) a boolean, either `true` or `false`

In the Wizard UI, those can be set in the "Extra" field, which should be a valid JSON object that one or more of the
above keys.

## API access levels

Each entry in the `ui.api` generates a RESTful endpoint `/api/ENTRY_NAME`. An entry can be given a read and write
access level. When a user logs in to the UI, a user is given an access level, so the API's read and write level can
restrict who's able to read and write to the given API.

For example, a default dashboard project defines two users, "user" with access level 3 and "admin" with access level 7.
A "leds" API endpoint allows "user" to read `/api/leds`, but not modify it. "admin" can both read and write to it:

```sh
$ curl -u admin:admin DEVICE_IP/api/leds
{"led1": false, "led2": false}
$ curl -u admin:admin DEVICE_IP/api/leds -d '{"led2": true}'
{"led1": false, "led2": true}
$ curl -u user:user DEVICE_IP/api/leds -d '{"led2": true}'
Forbidden
```

## Web UI login

If Web UI login is activated on a settings page, then Wizard enables granular access control to pages, panels, and
variables in the following way:

1. Every user has an associated access level, visible to both UI and the device. A User - defined `glue_authenticate()`
function assigns group ID to the users. An access level is an integer from 1 to 9
2. Access levels are hierarchical: the higher the level, the more privileged it is User group 9 is the most privileged.
Level 1 is the least privileged
3. Access level 0 means that a privilege access check is disabled, and anyone can access that API

## HTTP protocol support

```js
"http": {
  "http": true,      // Enable/disable HTTP server
  "https": false,    // Enable/disable HTTPS (secure) server
  "ui": true,        // Generate Web UI
  "login": true      // Enable/disable user login for the Web UI
},
```

## Execute functions after a delay

Sometimes a certain function needs to be executed after a delay. For example, device must be rebooted after a
configuration change. In order to execute such function after some delay, Mongoose API function `mg_timer_add()` can be
used:

```c
mg_timer_add(&g_mgr, 500, 0,  my_func, NULL);  // Run my_func after 500 ms delay
```

## Autoupdate interval

The `ui.heartbeat` setting is an integer value, which is an interval in seconds for the Web UI to auto-refresh. If that
value is `0`, then auto-refresh is disabled. Otherwise, Web UI makes an `/api/heartbeat` API call every `ui.heartbeat`
seconds.

The `/api/heartbeat` API call returns a number, which in an internal version count. If that version count changes
(increments), then Web UI re-fetches all API values, and refreshes the UI. That is, in order to automatically update UI
elements, that internal counter should change. That internal counter is incremented by the `glue_update_state()`
function.

The internal version counter is automatically incremented every time a `glue_set_*` function is called - in other
words, if someone clicks on the save button.

If API value is changed somewhere else in the firmware code, the UI must be notified about this change by calling
`glue_update_state()` function.

> Call `glue_update_state()` in your firmware to force UI refresh. Note that refreshing UI is expensive, so call
`glue_update_state()` only if any of the API variable values really changes.

Also, that periodic poll updates a toolbar indicator, that shows device connection status. Normally it is green:
![Successful heartbeat indicator](https://mongoose.ws/documentation/images/heartbeat-ok.png)

If a device misses hearbeats, it becomes red:

In other words, auto-refresh ensures that you're looking at the Web UI that is not stale.

## Websockets updates

If Websocket support is enabled in the HTTP settings, then device can send frequent periodic updates to all connected
Web UI clients. The API function that enabled websocket updates is this:

```c
void mongoose_add_ws_reporter(unsigned timeout_ms, const char *name);
```

Where `timeout_ms` specifies how frequently the websocket updates should be sent by the device, and `name` is the name
of the "data" API endpoint that will be reported.

Therefore, if you'd like to send a real-time data from a device, first configure the "data" API endpoint, override its
handlers, and then call the `mongoose_add_ws_reporter()`. The getter function will be called with the specified
frequency, sending data to the UI:

```c
#include "mongoose_glue.h"

static void my_getter(struct real_time_data *data) {
  data->value1 = read_adc();
}

int main(void) {

  mongoose_init();

  mongoose_set_http_handlers("real_time_data", my_getter, NULL);
  mongoose_add_ws_reporter(200, "real_time_data");

  for (;;) {
    mongoose_poll();
  }
}
```

Then the UI can use `${real_time_data.value1}` expression to display values.

## Custom REST API handlers

Mongoose Wizard makes it easy to create REST API handlers that are represented by JSON objects or array of objects.
Those objects are mapped to C structures which are easy to handle.

However sometimes it is required to create an API handler that returns arbitrary data. For such cases, Mongoose Wizard
provides an API function to register a custom API handler:

```c
void mongoose_add_custom_handler(const char *url_pattern, mg_event_handler_t fn);
```

The `url_pattern` is a glob expression that should match an URI, and `fn` is an event handler function to call. Here is
an example:

```c
#include "mongoose/mongoose_glue.h"

// curl -qs IP/my/api
// curl -qs IP/my/api/1/2/3?foo=bar -d '{"a":42}'
static void my_ev_handler(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_HTTP_MSG) {
    struct mg_http_message *hm = (struct mg_http_message *) ev_data;
    MG_INFO(("POST data: [%.*s], URI: [%.*s], QUERY: [%.*s]",  //
             hm->body.len, hm->body.buf,                       //
             hm->uri.len, hm->uri.buf,                         //
             hm->query.len, hm->query.buf));
    mg_http_reply(c, 200, "", "ok\n");
  }
}

int main(void) {
  mongoose_init();
  mongoose_add_custom_handler("/my/api#", my_ev_handler);

  for (;;) {
    mongoose_poll();
  }

  return 0;
}
```

## Supported boards

Below is the list of development boards Mongoose Wizard supports.

| Architecture | Board | Connectivity |
| --- | --- | --- |
| STM32 | Nucleo-F207ZG | Built-in Ethernet |
| STM32 | Nucleo-F207ZG | Built-in Ethernet |
| STM32 | Nucleo-F429ZI | Built-in Ethernet |
| STM32 | Nucleo-F439ZI | Built-in Ethernet |
| STM32 | Nucleo-F746ZG | Built-in Ethernet |
| STM32 | Nucleo-F756ZG | Built-in Ethernet |
| STM32 | Nucleo-F767ZI | Built-in Ethernet |
| STM32 | Nucleo-H563ZI | Built-in Ethernet |
| STM32 | Nucleo-H723ZG | Built-in Ethernet |
| STM32 | Nucleo-H743ZI | Built-in Ethernet |
| STM32 | Nucleo-H753ZI | Built-in Ethernet |
| STM32 | Nucleo-H755ZI-Q | Built-in Ethernet |
| STM32 | Nucleo-H7S3L8 | Built-in Ethernet |
| STM32 | Nucleo-N657X0-Q | Built-in Ethernet |
| STM32 | STM32H735G-DK | Built-in Ethernet |
| STM32 | STM32H745I-DISCO | Built-in Ethernet |
| STM32 | STM32H747I-DISCO | Built-in Ethernet |
| STM32 | STM32H573I-DK | Built-in Ethernet |
| STM32 | Portenta H7 | Built-in Ethernet, CYW43439 WiFi |
| NXP | Teensy4.1 | Built-in Ethernet |
| NXP | RT1170-EVKB | Built-in Ethernet |
| NXP | RT1020-EVK | Built-in Ethernet |
| NXP | RT1024-EVK | Built-in Ethernet |
| NXP | RT1040-EVK | Built-in Ethernet |
| NXP | RT1050-EVKB | Built-in Ethernet |
| NXP | RT1060-EVKB | Built-in Ethernet |
| NXP | RT1064-EVK | Built-in Ethernet |
| NXP | FRDM-MCXN947 | Built-in Ethernet |
| NXP | FRDM-RW612 | Built-in Ethernet & WiFi |
| Texas Instruments | EK-TM4C1294XL | Built-in Ethernet |
| Texas Instruments | TMS570 | Built-in Ethernet |
| Espressif | ESP32, ESP32xx | Built-in WiFi |
| Infineon | XMC4400 2Go | Built-in Ethernet |
| Infineon | XMC4700 2Go | Built-in Ethernet |
| Infineon | KIT\_XMC72\_EVK | Built-in Ethernet |
| Infineon | CY8CPROTO-062S2-43439 | Built-in WiFi |
| Raspberry PI | RP2040, RP2350 | W5500, W5100 Ethernet |
| Raspberry PI | Pico-W, Pico2-W | CYW43439 WiFi |
| Nordic | nRF9160 Thingy:91 | Built-in Cellular |
| Renesas | RA6M4 | Built-in Ethernet |
| Renesas | RA8M1 | Built-in Ethernet |
| Zephyr | any | Built-in Ethernet |
| Zephyr | any | W5500 Ethernet |
| Arduino | any | W5500 Ethernet |
| Arduino | any | any WiFI (e.g. ESP32) |
| Windows | \- | \- |
| Linux,MacOS | \- | \- |

## FAQ

**Can I manually edit the wizard-generated UI?**

The generated UI cannot be manually edited. The Wizard does not generate HTML. Instead, the Wizard UI engine renders
the configuration `ui` section dynamically. If you want full manual control over your UI, do not use the Wizard and
create your own UI manually, see the [device dashboard
tutorial](https://mongoose.ws/documentation/tutorials/device-dashboard/#frontend-implementation)

## Tutorials

## Development Environment

- [Build tools](https://mongoose.ws/documentation/tutorials/tools/) - A guide on setting up a development environment
for building and running Mongoose Library examples, as well as developing new applications.

## Common Tasks

### Redirect printf to UART

Different C libraries provide different hooks. In all examples below, the STM32 Cube function `HAL_UART_Transmit()` is
used - change if required.

```c
int _write(int fd, unsigned char *buf, int len) {
  HAL_UART_Transmit(&huart3, buf, len, HAL_MAX_DELAY);
  return len;
}
```
```c
int __io_putchar(int ch) {
  HAL_UART_Transmit(&huart3, (uint8_t*) &ch, 1, HAL_MAX_DELAY);
  return ch;
}
```
```c
int fputc(int ch, FILE *f){
  HAL_UART_Transmit(&huart3, (uint8_t*) &ch, 1, HAL_MAX_DELAY);
  return ch;
}
```

### Report free RAM

```c
// Works in ARM GCC (newlib C library)
extern unsigned char _end[];                   // Heap start
static unsigned char *s_break_address = _end;  // Heap end (dynamic)

size_t ramUsed(void) {
  return (size_t) (s_break_address - _end);
}

size_t ramFree(void) {
  unsigned char endofstack;
  return (size_t) (&endofstack - s_break_address);
}

void *_sbrk(int incr) {
  unsigned char *prev_heap;
  unsigned char *heap_end = (unsigned char *) ((size_t) &heap_end - 256);
  prev_heap = s_break_address;
  if (s_break_address + incr > heap_end) {
    errno = ENOMEM;
    return (void *) -1;
  }
  s_break_address += incr;
  return prev_heap;
}
```

In order to report free RAM number in the bare metal superloop, see this example for Cube:

```c
uint32_t timer = 0, period = 1000;  // milliseconds
while (1) {
  uint32_t now = HAL_GetTick();

  if ((int32_t)(now - timer) >= 0) {
    printf("RAM: %u\n", ramFree());
    while ((int32_t)(now - timer) >= 0) timer += period;
  }
```

### Integrate Mongoose into existing embedded project

First, setup low level. For MCUs with built-in Ethernet controller, enable that controller and setup pins. Then, add
Mongoose:

**Step 1.** Copy `mongoose.h`. Open [https://github.com/cesanta/mongoose](https://github.com/cesanta/mongoose) in your
browser, click on "mongoose.h". Click on "Raw" button, and copy file contents into the clipboard. Create `mongoose.h`
file in your project, and paste the copied content there.
**Step 2.** Copy mongoose.c - repeat the same for `mongoose.c`
**Step 3.** Create `mongoose_config.h` file in your project, and paste the following contents. Uncomment the driver
appropriate for your device, and save:

```c
#pragma once

// See https://mongoose.ws/documentation/#build-options
#define MG_ENABLE_TCPIP 1          // Enable build-in TCP/IP stack
#define MG_ARCH MG_ARCH_CUBE       // Change this if not Cube
#define MG_ENABLE_DRIVER_STM32F 1  // Change this if not STM32Fxx
```

You can see the full list of all available options at
[https://mongoose.ws/documentation/#build-options](https://mongoose.ws/documentation/#build-options)

**Step 4.** Add `#include "mongoose.h"` to the top of you main C file
**Step 5.** Add `run_mongoose()` function:

```c
// In RTOS environment, run this function in a separate task. Give it 8k stack
static void run_mongoose(void) {
  struct mg_mgr mgr;        // Mongoose event manager
  mg_log_set(MG_LL_DEBUG);  // Set log level to debug
  mg_mgr_init(&mgr);        // Initialise event manager
  for (;;) {                // Infinite event loop
    mg_mgr_poll(&mgr, 0);   // Process network events
  }
}
```

**Step 6.** Update `main()` function to call `run_mongoose()` instead of running at infinite loop.
**Step 7.** Rebuild the firmware, and flash it. Notice the log messages. You should see something like this:

```
7f5    1 mongoose.c:5089:onstatechange  Link up
7f9    3 mongoose.c:5189:tx_dhcp_discov DHCP discover sent. Our MAC: 02:2d:cf:46:29:04
915    3 mongoose.c:5168:tx_dhcp_reques DHCP req sent
a30    2 mongoose.c:5296:rx_dhcp_client Lease: 86400 sec (86402)
a36    2 mongoose.c:5084:onstatechange  READY, IP: 192.168.0.60
a3c    2 mongoose.c:5085:onstatechange         GW: 192.168.0.1
a42    2 mongoose.c:5086:onstatechange        MAC: 02:2d:cf:46:29:04
bcf    2 mongoose.c:5755:mg_tcpip_poll  Status: ready, IP: 192.168.0.60, rx:6, tx:3, dr:0, er:0
fb7    2 mongoose.c:5755:mg_tcpip_poll  Status: ready, IP: 192.168.0.60, rx:6, tx:3, dr:0, er:0
```

If instead you see DHCP requests message like this:

```
130b0  3 mongoose.c:4776:tx_dhcp_discov DHCP discover sent. Our MAC: 02:03:04:05:06:07
13498  3 mongoose.c:4776:tx_dhcp_discov DHCP discover sent. Our MAC: 02:03:04:05:06:07
```

Then the most common cause for this is you have your Ethernet pins wrong. Click on the `.ioc` file, go to the Ethernet
configuration, and double-check the Ethernet pins against the table above.

> NOTE: if you want to to use RTOS for your firmware, for example FreeRTOS, then simply start `run_mongoose()` in a
sepatate task.

In a separate terminal, ping the board and make sure it is alive:

```
$ ping 192.168.0.60
PING 192.168.0.60 (192.168.0.60): 56 data bytes
64 bytes from 192.168.0.60: icmp_seq=0 ttl=64 time=15.197 ms
64 bytes from 192.168.0.60: icmp_seq=1 ttl=64 time=2.201 ms
```

Done! We have a functional TCP/IP stack running on our board. Notice that we did not use any extra middleware - no
RTOS, no lwIP.

## Web User Interface

- [Device dashboard](https://mongoose.ws/documentation/tutorials/device-dashboard/) - This tutorial shows an example of
how to build a device dashboard, what can be very useful for headless devices.
- [REST basics](https://mongoose.ws/documentation/tutorials/webui/webui-rest/) - This tutorial will show you the basics
of how to implement and use a REST-based user interface (UI).
- [Pure JavaScript UI](https://mongoose.ws/documentation/tutorials/webui/webui-plain/) - This tutorial will show you
how to implement a plain JavaScript-based user interface (UI) over a REST-based backend.
- [Preact UI](https://mongoose.ws/documentation/tutorials/webui/webui-preact/) - This tutorial will show you how to
implement a Preact-based frontend for a user interface (UI) over a REST-based backend. We'll concentrate here on the
basics of the Preact UI frontend.
- [User authentication](https://mongoose.ws/documentation/tutorials/webui/webui-login/) - This tutorial will show you
how to implement a session login with a Preact-based user interface (UI) over a REST-based backend. We'll concentrate
here on the basics of the login process.
- [Data push](https://mongoose.ws/documentation/tutorials/webui/webui-push/) - This tutorial will show you how to push
data from the device to a JavaScript-based user interface (UI) running on the browser; either using WebSocket or a
REST-based API.
- [MQTT dashboard](https://mongoose.ws/documentation/tutorials/mqtt-dashboard/) - This tutorial shows an example of how
to build a remote device dashboard, what can be very useful to handle remote devices.

## HTTP

- [HTTP server](https://mongoose.ws/documentation/tutorials/http/http-server/) - A basic HTTP server tutorials will
show you how to configure a HTTP server, while you get familiar with the event manager and the server API.
- [HTTP client](https://mongoose.ws/documentation/tutorials/http/http-client/) - This tutorial will show you how to
implement an HTTP client using Mongoose Library.
- [HTTP proxy client](https://mongoose.ws/documentation/tutorials/http/http-proxy-client/) - This tutorial will show
you how to use Mongoose as an HTTP client in places where connections must be done through a proxy.
- [HTTP reverse proxy](https://mongoose.ws/documentation/tutorials/http/http-reverse-proxy/) - This tutorial will show
you how to use Mongoose to implement a reverse proxy.
- [File uploads](https://mongoose.ws/documentation/tutorials/http/file-uploads/) - This tutorial will show you how to
upload a file to a Mongoose web server.
- [Huge response](https://mongoose.ws/documentation/tutorials/http/huge-response/) - This tutorial will show you how to
send large amounts of data, larger than available buffer memory.
- [Video stream](https://mongoose.ws/documentation/tutorials/http/video-stream/) - This tutorial will show you how to
send a video stream as a series of MJPEG frames.

## Websocket

- [Websocket server](https://mongoose.ws/documentation/tutorials/websocket/websocket-server/) - This tutorial
demonstrates how Mongoose Library can be used to implement a Websocket server.
- [Websocket client](https://mongoose.ws/documentation/tutorials/websocket/websocket-client/) - This tutorial
demonstrates how Mongoose Library can be used to implement a Websocket client.
- [JSON-RPC over WS](https://mongoose.ws/documentation/tutorials/websocket/json-rpc-over-websocket/) - This tutorial
demonstrates how Mongoose Library can be used to implement JSON-RPC functionality over WebSocket.

## MQTT

- [MQTT client](https://mongoose.ws/documentation/tutorials/mqtt/mqtt-client/) - This tutorial demonstrates how
Mongoose Library can be used to implement an MQTT client.
- [MQTT server](https://mongoose.ws/documentation/tutorials/mqtt/mqtt-server/) - This tutorial demonstrates how
Mongoose Library can be used to implement a simple MQTT 3.1.1 server.
- [MQTT over WS client](https://mongoose.ws/documentation/tutorials/mqtt/mqtt-over-ws-client/) - This tutorial
demonstrates how Mongoose Library can be used to implement an MQTT client that connects to the broker over WebSocket.
- [AWS IoT](https://mongoose.ws/documentation/tutorials/mqtt/mqtt-client-aws-iot/) - This tutorial demonstrates how
Mongoose Library can be used to communicate with the AWS IoT service.
- [MQTT dashboard](https://mongoose.ws/documentation/tutorials/mqtt-dashboard/) - This tutorial shows an example of how
to build an MQTT-controlled headless device.

## SSL/TLS

- [SSL/TLS](https://mongoose.ws/documentation/tutorials/tls/) - In this tutorial we describe how to enable SSL/TLS for
servers and clients.

## Firmware Update

- [Firmware Update](https://mongoose.ws/documentation/tutorials/firmware-update/) - This tutorial will show you how to
use Mongoose Library functions to implement firmware updates.

## Core

- [Timers](https://mongoose.ws/documentation/tutorials/core/timers/) - This tutorial will guide you to configure a
timer callback, a mechanism to perform some periodic actions.
- [Multithreading](https://mongoose.ws/documentation/tutorials/core/multi-threaded/) - This tutorial will show you how
to work with Mongoose on a multithreaded environment.
- [Embedded filesystem](https://mongoose.ws/documentation/tutorials/core/embedded-filesystem/) - This tutorial shows an
example of how to embed files in a packed filesystem that is linked into the server binary; forming a read-only file
system that can be used to hold credentials and/or web files to be served.

## Misc

- [Error handling](https://mongoose.ws/documentation/tutorials/error-handling/) - If a connection fails for some
reason, you can find answers what to do in this section.
- [UART bridge](https://mongoose.ws/documentation/tutorials/uart-bridge/) - This tutorial shows an example of how to
send UART data over the network.
- [CMSIS driver](https://mongoose.ws/documentation/tutorials/cmsis_driver/) - Write your own driver, port our generic
CMSIS-Driver to your ARM device

## SMTP

- [SMTP client](https://mongoose.ws/documentation/tutorials/smtp/smtp-client/) - This simple tutorial demonstrates how
Mongoose Library can be used to implement an SMTP client over TLS.

## TCP

- [TCP client and server](https://mongoose.ws/documentation/tutorials/tcp/tcp/) - This simple tutorial demonstrates how
Mongoose Library can be used to implement TCP clients and servers, even over TLS.
- [SOCKS5 server](https://mongoose.ws/documentation/tutorials/tcp/socks5-server/) - This tutorial will show you how to
use Mongoose Library functions to implement a TCP-based server, in this case a SOCKS5 proxy server.

## UDP

- [Captive DNS server](https://mongoose.ws/documentation/tutorials/udp/captive-dns-server/) - This tutorial
demonstrates how Mongoose Library can be used to implement a captive DNS portal. It is usually required for device
configuration.
- [SNTP time sync](https://mongoose.ws/documentation/tutorials/udp/sntp-time-sync/) - This tutorial will show you how
to synchronize time with a remote SNTP server.
- [SSDP search](https://mongoose.ws/documentation/tutorials/udp/ssdp-search/) - This tutorial demonstrates how to use
Mongoose Library for UDP communication, by performing an SSDP search.

## TCP/IP stack drivers

- [CMSIS Driver](https://mongoose.ws/documentation/tutorials/cmsis_driver/) - Write your own driver, port our generic
CMSIS-Driver to your ARM device
- [Driver for RNDIS](https://mongoose.ws/documentation/tutorials/rp2040/pico-rndis-dashboard/) - Write your own driver,
use TinyUSB and use your computer to control your device via USB
- [RMII driver with the RP2040 PIOs](https://mongoose.ws/documentation/tutorials/rp2040/pico-rmii/) - Write your own
driver, low-level drive of a PHY chip with a software minimalistic MAC controller
- [Ethernet Hardware](https://mongoose.ws/documentation/tutorials/hardware/) - Configure Mongoose for your own board,
in case it is not a standard board supported by [Mongoose Wizard](#mongoose-wizard)

## STM32

- [GCC+make/baremetal](https://mongoose.ws/documentation/tutorials/stm32/all-make-baremetal-builtin/) - Use Mongoose
baremetal on STM32 devices with GCC and make
- [GCC+make/FreeRTOS](https://mongoose.ws/documentation/tutorials/stm32/all-make-freertos-builtin/) - Use Mongoose over
FreeRTOS on STM32 devices with GCC and make
- [CubeIDE/baremetal](https://mongoose.ws/documentation/tutorials/stm32/all-cube-baremetal-builtin/) - Use Mongoose
baremetal on STM32 devices with STM32CubeIDE
- [CubeIDE/FreeRTOS](https://mongoose.ws/documentation/tutorials/stm32/all-cube-freertos-builtin/) - Use Mongoose over
FreeRTOS on STM32 devices with STM32CubeIDE
- [CubeIDE step-by-step](https://mongoose.ws/docs/guides/stm32-cubeide-mongoose/)
- [Keil/baremetal](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-baremetal/) - Use Mongoose
baremetal on STM32 devices with Keil
- [Keil/more options](https://mongoose.ws/documentation/#nucleo-f746zg) - Check the F746 to see several tutorials on
how to use Mongoose over an OS on STM32 devices with Keil
- [Keil step-by-step](https://mongoose.ws/documentation/tutorials/stm32/keil/)

### Nucleo-F207ZG

ram: 128k flash: 1m freq: 120MHz net: Ethernet

![Nucleo-F207ZG board](https://mongoose.ws/documentation/images/nucleo-f746zg.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f207&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f207&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f207&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f207&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f207&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f207&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=f207&ide=Zephyr&rtos=baremetal&file=README.md) |

### Nucleo-F429ZI

ram: 256k flash: 2m freq: 180MHz net: Ethernet

![Nucleo-F429ZI board](https://mongoose.ws/documentation/images/nucleo-f746zg.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f429&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f429&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f429&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f429&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f429&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f429&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Cube | FreeRTOS | lwIP | [tutorial](https://mongoose.ws/documentation/tutorials/stm32/all-cube-freertos-lwip/) |
| Keil | baremetal | built-in |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-baremetal/) |
| Keil | FreeRTOS | built-in |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-freertos/) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=f429&ide=Zephyr&rtos=baremetal&file=README.md) |
| GCC+make | baremetal | built-in USB |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/all-make-baremetal-builtin-rndis/) |

### Nucleo-F429ZI + RM2 breakout

net: WiFi

![RM2 breakout](https://mongoose.ws/documentation/images/rm2-breakout.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[example](https://github.com/cesanta/mongoose/tree/master/tutorials/stm32/rm2-nucleo-f429zi-make-baremetal-builtin/) |

### Nucleo-F439ZI

ram: 256k flash: 2m freq: 180MHz net: Ethernet

![Nucleo-F439ZI board](https://mongoose.ws/documentation/images/nucleo-f746zg.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f439&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f439&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f439&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f439&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f439&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f439&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Cube | FreeRTOS | lwIP | [tutorial](https://mongoose.ws/documentation/tutorials/stm32/all-cube-freertos-lwip/) |
| Keil | baremetal | built-in |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-baremetal/) |
| Keil | FreeRTOS | built-in |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-freertos/) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=f439&ide=Zephyr&rtos=baremetal&file=README.md) |
| GCC+make | baremetal | built-in USB |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/all-make-baremetal-builtin-rndis/) |

### Nucleo-F746ZG

ram: 320k flash: 1m freq: 216MHz net: Ethernet

![Nucleo-F746ZG board](https://mongoose.ws/documentation/images/nucleo-f746zg.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f746&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f746&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f746&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f746&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f746&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f746&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Cube | FreeRTOS | lwIP | [tutorial](https://mongoose.ws/documentation/tutorials/stm32/all-cube-freertos-lwip/) |
| Keil | baremetal | built-in |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-baremetal/) |
| Keil | FreeRTOS | built-in |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-freertos/) |
| Keil | CMSIS-RTOS v1 (RTX) | built-in |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-cmsis1/) |
| Keil | CMSIS-RTOS v2 | built-in |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-cmsis2/) |
| Keil | CMSIS-RTOS v2 | lwIP |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-cmsis2-lwip/) |
| Keil | FreeRTOS | lwIP |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-freertos-lwip/) |
| Keil | FreeRTOS | FreeRTOS+TCP |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-freertos-tcp/) |
| Keil | RTX | MDK | [tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-rtx-mdk/) |
| Keil | RTX5 | MDK | [tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-rtx5-mdk/) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=f746&ide=Zephyr&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | FreeRTOS+TCP |
[example](https://github.com/cesanta/mongoose/tree/master/tutorials/stm32/nucleo-f746zg-make-freertos-tcp) |
| GCC+make | baremetal | built-in USB |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/all-make-baremetal-builtin-rndis/) |

### Nucleo-F746ZG + RM2 breakout

net: WiFi

![RM2 breakout](https://mongoose.ws/documentation/images/rm2-breakout.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[example](https://github.com/cesanta/mongoose/tree/master/tutorials/stm32/rm2-nucleo-f746zg-make-baremetal-builtin/) |

### Nucleo-F756ZG

ram: 320k flash: 1m freq: 216MHz net: Ethernet

![Nucleo-F756ZG board](https://mongoose.ws/documentation/images/nucleo-f746zg.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f756&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f756&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f756&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f756&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f756&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f756&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Cube | FreeRTOS | lwIP | [tutorial](https://mongoose.ws/documentation/tutorials/stm32/all-cube-freertos-lwip/) |
| Keil | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f756&ide=Keil&rtos=baremetal&file=README.md) |
| Keil | FreeRTOS | built-in |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-freertos/) |
| Keil | CMSIS-RTOS v1 (RTX) | built-in |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-cmsis1/) |
| Keil | CMSIS-RTOS v2 | built-in |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-cmsis2/) |
| Keil | CMSIS-RTOS v2 | lwIP |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-cmsis2-lwip/) |
| Keil | FreeRTOS | lwIP |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-freertos-lwip/) |
| Keil | FreeRTOS | FreeRTOS+TCP |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-freertos-tcp/) |
| Keil | RTX | MDK | [tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-rtx-mdk/) |
| Keil | RTX5 | MDK | [tutorial](https://mongoose.ws/documentation/tutorials/stm32/nucleo-f746zg-keil-rtx5-mdk/) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=f756&ide=Zephyr&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | FreeRTOS+TCP |
[example](https://github.com/cesanta/mongoose/tree/master/tutorials/stm32/nucleo-f746zg-make-freertos-tcp) |
| GCC+make | baremetal | built-in USB |
[tutorial](https://mongoose.ws/documentation/tutorials/stm32/all-make-baremetal-builtin-rndis/) |

### Nucleo-F767ZI

ram: 512k flash: 2m freq: 216MHz net: Ethernet

![Nucleo-F767ZI board](https://mongoose.ws/documentation/images/nucleo-f746zg.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f767&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f767&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f767&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f767&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f767&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=f767&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=f767&ide=Zephyr&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | lwIP | [tutorial](https://mongoose.ws/documentation/tutorials/stm32/all-cube-freertos-lwip/) |

### Nucleo-H563ZI

ram: 640k flash: 2m freq: 250MHz net: Ethernet

![Nucleo-H563ZI board](https://mongoose.ws/documentation/images/nucleo-h563zi.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h563&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h563&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h563&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h563&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h563&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h563&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=h563&ide=Zephyr&rtos=baremetal&file=README.md) |

### STM32H573I-DK

ram: 640k flash: 2m freq: 250MHz net: Ethernet

![STM32H573I-DK board](https://mongoose.ws/documentation/images/stm32h573i-dk.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h573&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h573&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h573&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h573&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h573&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h573&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=h573&ide=Zephyr&rtos=baremetal&file=README.md) |

### Nucleo-H723ZG

ram: 564k flash: 1m freq: 550MHz net: Ethernet

![Nucleo-H723ZG board](https://mongoose.ws/documentation/images/nucleo-h743z.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h723&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h723&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h723&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h723&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h723&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h723&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=h723&ide=Zephyr&rtos=baremetal&file=README.md) |
| GCC+make | baremetal | built-in | [device
dashboard](https://mongoose.ws/documentation/tutorials/stm32/all-make-baremetal-builtin/) |
| GCC+make | baremetal | built-in | [MQTT dashboard
device](https://mongoose.ws/documentation/tutorials/mqtt-dashboard/#device-implementation) |

### STM32H735G-DK

ram: 564k flash: 1m freq: 550MHz net: Ethernet

![STM32H735G-DK board](https://mongoose.ws/documentation/images/stm32h735g-dk.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h735&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h735&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h735&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h735&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h735&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h735&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=h735&ide=Zephyr&rtos=baremetal&file=README.md) |

### Nucleo-H743ZI2

ram: 1m flash: 2m freq: 480MHz net: Ethernet

![Nucleo-H743ZI2 board](https://mongoose.ws/documentation/images/nucleo-h743z.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h743&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h743&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h743&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h743&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h743&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h743&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=h743&ide=Zephyr&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | lwIP | [tutorial](https://mongoose.ws/documentation/tutorials/stm32/all-cube-freertos-lwip/) |

### STM32H745I-Disco

ram: 1m flash: 2m freq: 480MHz net: Ethernet

![H745I-DISCO board](https://mongoose.ws/documentation/images/stm32h745i-disco.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h745&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h745&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h745&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h745&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h745&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h745&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=h745&ide=Zephyr&rtos=baremetal&file=README.md) |

### STM32H747I-Disco

ram: 1m flash: 2m freq: 480MHz net: Ethernet

![H747I-DISCO board](https://mongoose.ws/documentation/images/h747i-disco.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h747&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h747&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h747&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h747&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h747&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h747&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=h747&ide=Zephyr&rtos=baremetal&file=README.md) |

### Arduino Portenta H7

ram: 1m flash: 2m freq: 400MHz net: WiFi

![Arduino Portenta H7](https://mongoose.ws/documentation/images/portenta-h7.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[example](https://github.com/cesanta/mongoose/tree/master/tutorials/stm32/portenta-h7-make-baremetal-builtin/) |
| Cube | baremetal | built-in |
[example](https://github.com/cesanta/mongoose/tree/master/tutorials/stm32/portenta-h7-cube-baremetal-builtin/) |

### Nucleo-H753ZI

ram: 1m flash: 2m freq: 480MHz net: Ethernet

![Nucleo-H753ZI board](https://mongoose.ws/documentation/images/nucleo-h743z.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h753&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h753&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h753&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h753&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h753&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h753&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=h753&ide=Zephyr&rtos=baremetal&file=README.md) |

### Nucleo-H755ZI-Q

ram: 1m flash: 2m freq: 480MHz net: Ethernet

![Nucleo-H755ZI-Q board](https://mongoose.ws/documentation/images/nucleo-h755zi-q.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h755&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h755&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h755&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h755&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h755&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h755&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=h755&ide=Zephyr&rtos=baremetal&file=README.md) |

### Nucleo-H7S3L8

ram: 620k flash: 64k freq: 600MHz net: Ethernet

![Nucleo-H7S3L8 board](https://mongoose.ws/documentation/images/nucleo-h7s3l8.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h7s3l8&ide=CubeIDE&rtos=baremetal&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h7s3l8&ide=VSCode&rtos=baremetal&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=h7s3l8&ide=GCC+make&rtos=baremetal&file=README.md) |

### Nucleo-N657X0-Q

ram: 4.2m flash: 64m freq: 800MHz net: Ethernet

![Nucleo-N657X0-Q board](https://mongoose.ws/documentation/images/nucleo-n657x0-q.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=n657&ide=CubeIDE&rtos=baremetal&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=n657&ide=VSCode&rtos=baremetal&file=README.md) |

### Nucleo-U5A5ZJ-Q + X-NUCLEO-67W61M1

ram: 2.5m flash: 4m freq: 160MHz net: WiFi

![Nucleo-U5A5ZJ-Q board with X-NUCLEO-67W61M1
add-on](https://mongoose.ws/documentation/images/nucleo-u5a5zj-q+x-nucleo-67w61m1.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Cube | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=u5a5&ide=CubeIDE&rtos=baremetal&file=README.md) |
| Cube | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=u5a5&ide=CubeIDE&rtos=FreeRTOS&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=u5a5&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=u5a5&ide=GCC+make&rtos=FreeRTOS&file=README.md) |

### Nucleo-G031K8 + W5500 module

ram: 8k flash: 64k freq: 64MHz net: Ethernet

![Nucleo-G031K8 board + W5500 mini](https://mongoose.ws/documentation/images/nucleo-g031k8+w5500.webp)

| Framework | OS | IP stack | Example |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[example](https://github.com/cesanta/mongoose/tree/master/tutorials/stm32/nucleo-g031-make-baremetal-builtin/) |

## NXP

### FRDM-MCXN947

ram: 512k flash: 2m freq: 150MHz net: Ethernet

![NXP FRDM-MCXN947 board](https://mongoose.ws/documentation/images/FRDM-MCXN947.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=mcxn947&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=mcxn947&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| MCUXpresso | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=mcxn947&ide=MCUXpresso&rtos=baremetal&file=README.md) |
| MCUXpresso | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=mcxn947&ide=MCUXpresso&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=mcxn947&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=mcxn947&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=mcxn947&ide=Zephyr&rtos=baremetal&file=README.md) |

### FRDM-RW612

ram: 1.2m flash: 64m freq: 260MHz net: Ethernet net: WiFi

![NXP FRDM-RW612 board](https://mongoose.ws/documentation/images/frdm-rw612.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rw612&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rw612&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| MCUXpresso | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rw612&ide=MCUXpresso&rtos=baremetal&file=README.md) |
| MCUXpresso | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rw612&ide=MCUXpresso&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rw612&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rw612&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| MCUXpresso | FreeRTOS | built-in (Wi-Fi) |
[example](https://github.com/cesanta/mongoose/tree/master/tutorials/nxp/frdm-rw612-xpresso-freertos-lwip-wifi/) |
| MCUXpresso | FreeRTOS | built-in (Wi-Fi) |
[Wizard](https://mongoose.ws/wizard/#/output?board=rw612-w&ide=MCUXpresso&rtos=FreeRTOS&file=README.md) |
| MCUXpresso | FreeRTOS | lwIP (Ethernet) |
[example](https://github.com/cesanta/mongoose/tree/master/tutorials/nxp/frdm-rw612-xpresso-freertos-lwip/) |
| MCUXpresso | FreeRTOS | lwIP (Wi-Fi) |
[example](https://github.com/cesanta/mongoose/tree/master/tutorials/nxp/frdm-rw612-xpresso-freertos-lwip-wifi/) |

### FRDM-MCXE247

ram: 256k flash: 2m freq: 112MHz net: Ethernet

![NXP FRDM-MCXE247 board](https://mongoose.ws/documentation/images/FRDM-MCXE247.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=mcxe247&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=mcxe247&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| MCUXpresso | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=mcxe247&ide=MCUXpresso&rtos=baremetal&file=README.md) |
| MCUXpresso | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=mcxe247&ide=MCUXpresso&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=mcxe247&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=mcxe247&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=mcxe247&ide=Zephyr&rtos=baremetal&file=README.md) |

### MIMXRT1020-EVK

ram: 256k flash: 8m freq: 500MHz net: Ethernet

![NXP MIMXRT1020-EVK board](https://mongoose.ws/documentation/images/mimxrt1020-evk.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1020&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1020&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| MCUXpresso | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1020&ide=MCUXpresso&rtos=baremetal&file=README.md) |
| MCUXpresso | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1020&ide=MCUXpresso&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1020&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1020&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| MCUXpresso | FreeRTOS | lwIP | [tutorial](https://mongoose.ws/documentation/tutorials/nxp/nxp-mimxrt1020-freertos/) |
| MCUXpresso | AzureRTOS | Azure |
[tutorial](https://mongoose.ws/documentation/tutorials/nxp/nxp-mimxrt1020-azurertos/) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1020&ide=Zephyr&rtos=baremetal&file=README.md) |

### MIMXRT1024-EVK

ram: 256k flash: 4m freq: 500MHz net: Ethernet

![NXP MIMXRT1024-EVK board](https://mongoose.ws/documentation/images/mimxrt1024-evk.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1024&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1024&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| MCUXpresso | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1024&ide=MCUXpresso&rtos=baremetal&file=README.md) |
| MCUXpresso | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1024&ide=MCUXpresso&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1024&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1024&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1024&ide=Zephyr&rtos=baremetal&file=README.md) |

### MIMXRT1040-EVK

ram: 512k flash: 8m freq: 600MHz net: Ethernet

![NXP MIMXRT1040-EVK board](https://mongoose.ws/documentation/images/mimxrt1040-evk.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1040&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1040&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| MCUXpresso | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1040&ide=MCUXpresso&rtos=baremetal&file=README.md) |
| MCUXpresso | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1040&ide=MCUXpresso&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1040&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1040&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1040&ide=Zephyr&rtos=baremetal&file=README.md) |

### MIMXRT1050-EVKB

ram: 1m flash: 64m freq: 600MHz net: Ethernet

![NXP MIMXRT1050-EVKB board](https://mongoose.ws/documentation/images/mimxrt1050-evkb.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1050&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1050&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| MCUXpresso | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1050&ide=MCUXpresso&rtos=baremetal&file=README.md) |
| MCUXpresso | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1050&ide=MCUXpresso&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1050&ide=MCUXpresso&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1050&ide=MCUXpresso&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1050&ide=Zephyr&rtos=baremetal&file=README.md) |

### MIMXRT1060-EVKB

ram: 512k flash: 8m freq: 600MHz net: Ethernet

![NXP MIMXRT1060-EVKB board](https://mongoose.ws/documentation/images/mimxrt1060-evkb.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1060&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1060&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| MCUXpresso | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1060&ide=MCUXpresso&rtos=baremetal&file=README.md) |
| MCUXpresso | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1060&ide=MCUXpresso&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1060&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1060&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| MCUXpresso | baremetal | built-in |
[example](https://github.com/cesanta/mongoose/tree/master/tutorials/nxp/rt1060-evk-xpresso-baremetal-builtin/) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1060&ide=Zephyr&rtos=baremetal&file=README.md) |

### MIMXRT1064-EVK

ram: 512k flash: 4m freq: 600MHz net: Ethernet

![NXP MIMXRT1064-EVK board](https://mongoose.ws/documentation/images/mimxrt1064-evk.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1064&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1064&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| MCUXpresso | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1064&ide=MCUXpresso&rtos=baremetal&file=README.md) |
| MCUXpresso | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1064&ide=MCUXpresso&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1064&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1064&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1064&ide=Zephyr&rtos=baremetal&file=README.md) |

### MIMXRT1170-EVKB

ram: 64m flash: tons freq: 1GHz net: Ethernet

![NXP MIMXRT1170-EVKB board](https://mongoose.ws/documentation/images/mimxrt1170-evkb.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1170&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1170&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| VSCode | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1170&ide=VSCode&rtos=baremetal&file=README.md) |
| VSCode | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1170&ide=VSCode&rtos=FreeRTOS&file=README.md) |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=rt1170&ide=Zephyr&rtos=baremetal&file=README.md) |

### Teensy 4.1 + expansion board

ram: 1m flash: 8m freq: 600MHz net: Ethernet

![Teensy 4.1 board](https://mongoose.ws/documentation/images/teensy41exp.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Arduino |  | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=teensy41&ide=Arduino&rtos=baremetal&file=README.md) |

### FRDM-K64F

ram: 256k flash: 1m freq: 120MHz net: Ethernet

![NXP FRDM-K64F board](https://mongoose.ws/documentation/images/frdm-k64f.webp)

| Framework | OS | IP stack | Example |
| --- | --- | --- | --- |
| MCUXpresso | FreeRTOS | lwIP |
[example](https://github.com/cesanta/mongoose/tree/master/tutorials/nxp/nxp-frdmk64f-lwip-freertos) |

### FRDM-K66F

ram: 256k flash: 2m freq: 180MHz net: Ethernet

![NXP FRDM-K66F board](https://mongoose.ws/documentation/images/frdm-k66f.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| MCUXpresso | FreeRTOS | lwIP | [tutorial](https://mongoose.ws/documentation/tutorials/nxp/nxp-frdmk66f-freertos/) |

### NXP LPC54S018M-EVK

ram: 128m flash: 128m freq: 180MHz net: Ethernet

![NXP LPC54S018M-EVK board](https://mongoose.ws/documentation/images/lpc54018.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| MCUXpresso | FreeRTOS | lwIP |
[tutorial](https://mongoose.ws/documentation/tutorials/nxp/nxp-lpcxpresso54s018m-freertos/) |

## ESP

### ESP32 DevkitC

ram: 220k flash: 2/4m@40MHz freq: 160/240MHz net: WiFi

![ESP32 DevkitC board](https://mongoose.ws/documentation/images/esp32.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| ESP-IDF | FreeRTOS | lwIP | [device dashboard](https://mongoose.ws/documentation/tutorials/esp32/device-dashboard/) |
| ESP-IDF | FreeRTOS | lwIP | [UART bridge](https://mongoose.ws/documentation/tutorials/esp32/uart-bridge/) |
| ESP-IDF | FreeRTOS | lwIP |
[Wizard](https://mongoose.ws/wizard/#/output?board=esp32&ide=ESP-IDF&rtos=baremetal&file=README.md) |
| Arduino |  |  | [HTTP
server](https://github.com/cesanta/mongoose/tree/master/tutorials/http/http-server/arduino/esp32-http/) |
| Arduino |  |  |
[MQTT](https://github.com/cesanta/mongoose/tree/master/tutorials/mqtt/mqtt-client/arduino/esp32-mqtt/) |
| Arduino |  |  |
[Wizard](https://mongoose.ws/wizard/#/output?board=arduino-esp32&ide=Arduino&rtos=baremetal&file=README.md) |
| MicroPython | FreeRTOS | built-in |
[module](https://github.com/cesanta/mongoose/tree/master/tutorials/micropython/esp32/) |

### M5 STAMP PICO

ram: 220k flash: 4m@80MHz freq: 240MHz net: WiFi

![M5 STAMP PICO board](https://mongoose.ws/documentation/images/m5_stamp_pico.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| ESP-IDF | FreeRTOS | lwIP | [tutorial](https://mongoose.ws/documentation/tutorials/esp32/device-dashboard/) |
| ESP-IDF | FreeRTOS | lwIP |
[Wizard](https://mongoose.ws/wizard/#/output?board=esp32&ide=ESP-IDF&rtos=baremetal&file=README.md) |
| Arduino |  |  | [HTTP
server](https://github.com/cesanta/mongoose/tree/master/tutorials/http/http-server/arduino/esp32-http/) |
| Arduino |  |  |
[MQTT](https://github.com/cesanta/mongoose/tree/master/tutorials/mqtt/mqtt-client/arduino/esp32-mqtt/) |
| Arduino |  |  |
[Wizard](https://mongoose.ws/wizard/#/output?board=arduino-esp32&ide=Arduino&rtos=baremetal&file=README.md) |
| MicroPython | FreeRTOS | built-in |
[module](https://github.com/cesanta/mongoose/tree/master/tutorials/micropython/esp32/) |

### XIAO-ESP32-C3

ram: 400k flash: 4m@80MHz freq: 160MHz net: WiFi

![XIAO-ESP32-C3 board](https://mongoose.ws/documentation/images/xiao_esp32-c3.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| ESP-IDF | FreeRTOS | lwIP | [tutorial](https://mongoose.ws/documentation/tutorials/esp32/device-dashboard/) |
| ESP-IDF | FreeRTOS | lwIP |
[Wizard](https://mongoose.ws/wizard/#/output?board=esp32&ide=ESP-IDF&rtos=baremetal&file=README.md) |
| Arduino |  |  | [HTTP
server](https://github.com/cesanta/mongoose/tree/master/tutorials/http/http-server/arduino/esp32-http/) |
| Arduino |  |  |
[MQTT](https://github.com/cesanta/mongoose/tree/master/tutorials/mqtt/mqtt-client/arduino/esp32-mqtt/) |
| Arduino |  |  |
[Wizard](https://mongoose.ws/wizard/#/output?board=arduino-esp32&ide=Arduino&rtos=baremetal&file=README.md) |
| MicroPython | FreeRTOS | built-in |
[module](https://github.com/cesanta/mongoose/tree/master/tutorials/micropython/esp32/) |

### ESP8266 DevkitC

ram: 50k flash: 2m freq: 80MHz net: WiFi

![ESP8266 DevkitC board](https://mongoose.ws/documentation/images/esp8266-devkitc.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| RTOS SDK | SDK (FreeRTOS) | SDK (lwIP) |
[tutorial](https://mongoose.ws/documentation/tutorials/esp8266/http-client-server/) |

## Texas Instruments

- [GCC+make/baremetal](https://mongoose.ws/documentation/tutorials/ti/ek-tm4c1294xl-make-baremetal-builtin/) - Use
Mongoose baremetal on Tiva devices with GCC and make
- [GCC+make/FreeRTOS](https://mongoose.ws/documentation/tutorials/ti/ek-tm4c1294xl-make-freertos-builtin/) - Use
Mongoose over FreeRTOS on Tiva devices with GCC and make

### EK-TM4C1294xxx

ram: 256k flash: 1m freq: 120MHz net: Ethernet

![TI EK-TM4C1294XL board](https://mongoose.ws/documentation/images/tm4c129.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=tm4c129&ide=GCC+make&rtos=baremetal&file=README.md) |
| GCC+make | FreeRTOS | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=tm4c129&ide=GCC+make&rtos=FreeRTOS&file=README.md) |
| CCS | TI-RTOS | TI-RTOS | [tutorial](https://mongoose.ws/documentation/tutorials/ti/ti-ek-tm4c1294xl-http-server/) |
| GCC+make | baremetal | built-in USB |
[example](https://github.com/cesanta/mongoose/tree/master/tutorials/ti/ek-tm4c1294xl-make-baremetal-builtin-rndis) |

### TMDX570LC43HDK (TMS570)

ram: 512k flash: 4m freq: 300MHz net: Ethernet

![TMDX570LC43HDK board](https://mongoose.ws/documentation/images/tmdx570lc43hdk.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| CGT+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=tms570&ide=CGT+make&rtos=baremetal&file=README.md) |

## Infineon

### KIT\_XMC\_PLT2GO\_XMC4400

ram: 80k flash: 512k freq: 120MHz net: Ethernet

![Infineon XMC-4400 Platform2GO board](https://mongoose.ws/documentation/images/xmc4400_2go.webp)

| Framework | OS | IP stack | Example |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=xmc4400&ide=GCC+make&rtos=baremetal&file=README.md) |
| Modus IDE | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=xmc4400&ide=ModusIDE&rtos=baremetal&file=README.md) |

### KIT\_XMC47\_RELAX\_V1

ram: 352k flash: 2m freq: 144MHz net: Ethernet

![Infineon KIT_XMC47_RELAX_V1 board](https://mongoose.ws/documentation/images/xmc47_relax.webp)

| Framework | OS | IP stack | Example |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=xmc4700&ide=GCC+make&rtos=baremetal&file=README.md) |
| Modus IDE | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=xmc4700&ide=ModusIDE&rtos=baremetal&file=README.md) |

### KIT\_XMC72\_EVK

ram: 1m flash: 8m freq: 350MHz net: Ethernet

![Infineon XMC-7200 EVK board](https://mongoose.ws/documentation/images/kit_xmc72_evk.webp)

| Framework | OS | IP stack | Example |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=xmc7200&ide=GCC+make&rtos=baremetal&file=README.md) |
| Modus IDE | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=xmc7200&ide=ModusIDE&rtos=baremetal&file=README.md) |

### CY8CPROTO-062-4343W

ram: 1m flash: 2m freq: 150MHz net: WiFi

![Infineon CY8CPROTO-062-4343W board](https://mongoose.ws/documentation/images/CY8CPROTO-062-4343W.webp)

SOON...

### CY8CPROTO-062S2-43439

ram: 1m flash: 2m freq: 150MHz net: WiFi

![Infineon CY8CPROTO-062S2-43439 board](https://mongoose.ws/documentation/images/CY8CPROTO-062S2-43439.webp)

SOON...

## Nordic Semiconductor

### Nordic Thingy:91

ram: 256k flash: 1m freq: 64MHz net: Cellular

![Nordic Thingy:91 board](https://mongoose.ws/documentation/images/Thingy91_board.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Zephyr | Zephyr | Zephyr |
[Wizard](https://mongoose.ws/wizard/#/output?board=nrf91&ide=Zephyr&rtos=baremetal&file=README.md) |

### XIAO RP2040

ram: 264k flash: 2m freq: 133MHz net: USB (RNDIS/CDC-ECM)

![Seeed Xiao RP2040 board](https://mongoose.ws/documentation/images/xiao_rp2040.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| RPI PICO C SDK | baremetal | built-in USB RNDIS |
[tutorial](https://mongoose.ws/documentation/tutorials/rp2040/pico-rndis-dashboard/) |

## Renesas RA

### EK-RA6M4

ram: 1024k flash: 2m freq: 200MHz net: Ethernet

![Renesas EK-RA6M4 board](https://mongoose.ws/documentation/images/ek-ra6m4.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=ra6&ide=GCC+make&rtos=baremetal&file=README.md) |
| E2studio | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=ra6&ide=e2studio&rtos=baremetal&file=README.md) |

### EK-RA8M1

ram: 1024k flash: 2m freq: 480MHz net: Ethernet

![Renesas EK-RA8M1 board](https://mongoose.ws/documentation/images/ek-ra8m1.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=ra8m1&ide=GCC+make&rtos=baremetal&file=README.md) |
| E2studio | baremetal | built-in |
[Wizard](https://mongoose.ws/wizard/#/output?board=ra8m1&ide=e2studio&rtos=baremetal&file=README.md) |

## Microchip SAMxx

### SAM E54 Xplained Pro

ram: 256k flash: 1m freq: 120MHz net: Ethernet

![SAM E54 Xplained Pro](https://mongoose.ws/documentation/images/same54-xpro.webp)

| Framework | OS | IP stack | Example |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in | [device
dashboard](https://github.com/cesanta/mongoose/tree/master/tutorials/http/device-dashboard/microchip/same54-xpro) |
| GCC+make | baremetal | built-in | [MQTT
client](https://github.com/cesanta/mongoose/tree/master/tutorials/mqtt/mqtt-client/microchip/same54-xpro) |

### XIAO M0 + W5500 module

ram: 32k flash: 256k freq: 48MHz net: Ethernet

![XIAO M0 + W5500 module board](https://mongoose.ws/documentation/images/xiao-w5500.webp)

| Framework | OS | IP stack | Tutorial |
| --- | --- | --- | --- |
| Arduino |  | built-in | [tutorial](https://mongoose.ws/documentation/tutorials/arduino/w5500-http/) |

## WCH

### CH32V307

ram: 64k flash: 256k freq: 144MHz net: Ethernet

![WCH CH32V307 board](https://mongoose.ws/documentation/images/wch-ch32v307.webp)

| Framework | OS | IP stack | Example |
| --- | --- | --- | --- |
| GCC+make | baremetal | built-in |
[example](https://github.com/cesanta/mongoose/tree/master/tutorials/wch/ch32v307-make-baremetal-builtin/) |

## Zephyr

- [Tutorial](https://mongoose.ws/documentation/tutorials/zephyr/device-dashboard/)
- [Wizard (boards with
Ethernet)](https://mongoose.ws/wizard/#/output?board=zephyr&ide=Zephyr&rtos=baremetal&file=README.md)
- [Wizard (any supported board +
W5500)](https://mongoose.ws/wizard/#/output?board=zephyr-w5500&ide=Zephyr&rtos=baremetal&file=README.md)

## Windows

- [Wizard](https://mongoose.ws/wizard/#/output?board=windows&ide=GCC+make&rtos=baremetal&file=README.md)

## Mac and Linux

- [Wizard](https://mongoose.ws/wizard/#/output?board=unix&ide=GCC+make&rtos=baremetal&file=README.md)

## Embedded Linux

### Raspberry Pi

ram: 1G flash: SD freq: 1.2+ GHz net: Ethernet net: WiFi

![Raspberry Pi 4B board](https://mongoose.ws/documentation/images/raspberry_pi_4b.webp)

| Framework | Code | Tutorial |
| --- | --- | --- |
| Raspberry Pi OS | [Wizard](https://mongoose.ws/wizard/#/output?board=unix&ide=GCC+make&rtos=baremetal&file=README.md)
| [tutorial](https://mongoose.ws/documentation/tutorials/raspberry-pi/rp/) |

## Video Tutorials

[![Mongoose WebServer for Microcontrollers - setting up tools on Windows and building a basic
example.](https://mongoose.ws/documentation/images/0.webp)](https://www.youtube.com/watch?v=rjNwF8iWp7Q)

Introduction - setting up tools on Windows and building a basic example

[![A detailed HTTP server example
walk-through.](https://mongoose.ws/documentation/images/1.webp)](https://www.youtube.com/watch?v=2Hq1wc1AzCY)

A detailed HTTP server example walk-through

[![Implementing Web UI device dashboard on STM32F7 board using Keil
RTX.](https://mongoose.ws/documentation/images/2.webp)](https://www.youtube.com/watch?v=_NequYNg3Vw)

Implementing Web UI device dashboard on STM32F7 board using Keil RTX

[![Implementing Web UI device dashboard on STM32F7 board using Cube
IDE.](https://mongoose.ws/documentation/images/3.webp)](https://www.youtube.com/watch?v=8htC_TSBeO0)

Implementing Web UI device dashboard on STM32F7 board using Cube IDE

[![How does TCP/CP stack work on embedded
device.](https://mongoose.ws/documentation/images/4.webp)](https://www.youtube.com/watch?v=Yz8kg8-mi-Q)

How does TCP/CP stack work on embedded device - an animated tutorial

## API Reference

## Core

### struct mg\_addr

```c
struct mg_addr {
  uint8_t ip[16];    // Holds IPv4 or IPv6 address, in network byte order
  uint16_t port;     // TCP or UDP port in network byte order
  uint8_t scope_id;  // IPv6 scope ID
  bool is_ip6;       // True when address is IPv6 address
};
```

This structure contains a network address; it can be considered as the Mongoose equivalent for the sockets `sockaddr`
structure.

### struct mg\_mgr

```c
struct mg_mgr {
  struct mg_connection *conns;  // List of active connections
  struct mg_dns dns4;           // DNS for IPv4
  struct mg_dns dns6;           // DNS for IPv6
  struct mg_connection *mdns;   // mDNS connection
  int dnstimeout;               // DNS resolve timeout in milliseconds
  bool use_dns6;                // Use DNS6 server by default
  unsigned long nextid;         // Next connection ID
  void *userdata;               // Arbitrary user data pointer
  ...
  struct mg_tcpip_if *ifp;      // Builtin TCP/IP stack only. Interface pointer
};
```

Event management structure that holds a list of active connections, together with some housekeeping information.

### struct mg\_connection

```c
struct mg_connection {
  struct mg_connection *next;  // Linkage in struct mg_mgr :: connections
  struct mg_mgr *mgr;          // Our container
  struct mg_addr loc;          // Local address
  struct mg_addr rem;          // Remote address
  void *fd;                    // Connected socket, or LWIP data
  unsigned long id;            // Auto-incrementing unique connection ID
  struct mg_iobuf recv;        // Incoming data
  struct mg_iobuf send;        // Outgoing data
  mg_event_handler_t fn;       // User-specified event handler function
  void *fn_data;               // User-specified function parameter
  mg_event_handler_t pfn;      // Protocol-specific handler function
  void *pfn_data;              // Protocol-specific function parameter
  char data[MG_DATA_SIZE];     // Arbitrary connection data, MG_DATA_SIZE defaults to 32 bytes
  void *tls;                   // TLS specific data
  unsigned is_listening : 1;   // Listening connection
  unsigned is_client : 1;      // Outbound (client) connection
  unsigned is_accepted : 1;    // Accepted (server) connection
  unsigned is_resolving : 1;   // Non-blocking DNS resolve is in progress
  unsigned is_connecting : 1;  // Non-blocking connect is in progress
  unsigned is_tls : 1;         // TLS-enabled connection
  unsigned is_tls_hs : 1;      // TLS handshake is in progress
  unsigned is_udp : 1;         // UDP connection
  unsigned is_websocket : 1;   // WebSocket connection
  unsigned is_hexdumping : 1;  // Hexdump in/out traffic
  unsigned is_draining : 1;    // Send remaining data, then close and free
  unsigned is_closing : 1;     // Close and free the connection immediately
  unsigned is_full : 1;        // Stop reads, until cleared
  unsigned is_resp : 1;        // Response is still being generated
  unsigned is_readable : 1;    // Connection is ready to read
  unsigned is_writable : 1;    // Connection is ready to write
};
```

A connection - either a listening connection, or an accepted connection, or an outbound connection.

### mg\_mgr\_init()

```c
void mg_mgr_init(struct mg_mgr *mgr);
```

Initialize event manager structure:

- Set a list of active connections to NULL
- Set default DNS servers for IPv4 and IPv6
- Set default DNS lookup timeout

Parameters:

- `mgr` - a pointer to `mg_mgr` structure that needs to be initialized

Return value: none

Usage example:

```c
struct mg_mgr mgr;
mg_mgr_init(&mgr);
```

### mg\_mgr\_poll()

```c
void mg_mgr_poll(struct mg_mgr *mgr, int ms);
```

Perform a single poll iteration. For each connection in the `mgr->conns` list:

- See if there is incoming data. If there is, read it into the `c->recv` buffer, send `MG_EV_READ` event
- See if there is data in the `c->send` buffer, and write it, send `MG_EV_WRITE` event
- If a connection is listening, accept an incoming connection if any, and send `MG_EV_ACCEPT` event to it
- Send `MG_EV_POLL` event

Parameters:

- `mgr` - an event manager to use
- `ms` - a timeout in milliseconds

Return value: none

Usage example:

```c
while (running == true) mg_mgr_poll(&mgr, 1000 /* 1 sec */);
```

### mg\_mgr\_free()

```c
void mg_mgr_free(struct mg_mgr *mgr);
```

Close all connections, and free all resources.

Parameters:

- `mgr` - an event manager to cleanup

Return value: none

Usage example:

```c
struct mg_mgr mgr;
mg_mgr_init(&mgr);
while (running == true) mg_mgr_poll(&mgr, 1000);   // Event loop
mg_mgr_free(&mgr);
```

### mg\_listen()

```c
struct mg_connection *mg_listen(struct mg_mgr *mgr, const char *url,
                                mg_event_handler_t fn, void *fn_data);
```

Create a listening connection, append this connection to `mgr->conns`.

Parameters:

- `mgr` - an event manager to use
- `url` - a URL. Specifies local IP address and port to listen on, e.g. `tcp://127.0.0.1:1234` or `udp://0.0.0.0:9000`.
If this URL is a known TLS URL, the `is_tls` flag will be set
- `fn` - an event handler function
- `fn_data` - an arbitrary pointer, which will be stored in the connection structure as `c->fn_data`, so the event
handler can use it when called.

Return value: created connection, or `NULL` on error.

Usage example:

```c
struct mg_connection *c = mg_listen(&mgr, "tcp://127.0.0.1:8080", fn, NULL);
```

### mg\_connect()

```c
struct mg_connection *mg_connect(struct mg_mgr *mgr, const char *url,
                                 mg_event_handler_t fn, void *fn_data);
```

Create an outbound connection, append this connection to `mgr->conns`.

Parameters:

- `mgr` - An event manager to use
- `url` - A URL, specifies the remote IP address/port to connect to, e.g. `http://a.com`. If this URL is a known TLS
URL, the `is_tls` flag will be set. If it requires name resolution, an asynchronous address resolution process will
start, either mDNS ('.local' domain) or DNS.
- `fn` - An event handler function
- `fn_data` - an arbitrary pointer, which will be stored in the connection structure as `c->fn_data`, so the event
handler can use it when called.

Return value: created connection, or `NULL` on error. Possible errors are: not enough memory, a NULL URL, or, in the
case of our built-in TCP/IP stack, the network not being ready.

Note: This function does not connect to the requested peer, it allocates required resources and starts the connection
process. Once our peer is really connected, an `MG_EV_CONNECT` event is sent to the connection event handler.

Note: mDNS resolution of '.local' domain addresses requires an mDNS listener. It is the user's responsibility to start
one, otherwise resolution will fail. You just need to call [mg\_mdns\_listen()](#mg_mdns_listen) with a NULL handler
pointer.

Usage example:

```c
struct mg_connection *c = mg_connect(&mgr, "http://example.org", fn, NULL);
```

### mg\_send()

```c
bool mg_send(struct mg_connection *c, const void *data, size_t size);
```

Append `data` of size `size` to the `c->send` buffer. Return success / failure.

Note: Except when using UDP on the Mongoose TCP/IP stack, this function does not push data to the network. It only
appends data to the output buffer. Data is sent when `mg_mgr_poll()` is called. If `mg_send()` is called multiple
times, the output buffer grows. When calling this function to send UDP on the Mongoose TCP/IP stack, an Ethernet frame
gets sent immediately, the `c->send` buffer is bypassed.

Parameters:

- `c` - A connection pointer
- `data` - A pointer to data to append to the send buffer
- `size` - A data size

Return value: `true` if data appended successfully and `false` otherwise

Usage example:

```c
mg_send(c, "hi", 2);  // Append string "hi" to the output buffer
```

### mg\_wakeup()

```c
void mg_wakeup(struct mg_mgr *mgr, unsigned long id, const void *data, size_t size);
```

Any thread/task can send `data`, `size` to Mongoose manager executing in another thread. This is the only Mongoose
function that can be called from a different task/thread. Calling this function wakes up the event manager and
generates an `MG_EV_WAKEUP` event in the respective event handler. Call [mg\_wakeup\_init()](#mg_wakeup_init) in the
event manager thread before first using it.

The data could be anything. It could be a structure. Or it could be a pointer. The receiving connection gets
`MG_EV_WAKEUP`, and gets that data as a chunk of memory: `struct mg_str *data = ev_data`. Note that the sent data
should be small, ideally less than 512 bytes. If you need to send a large piece of data, allocate it and send a pointer
instead - see examples below.

Parameters:

- `mgr` - An event manager
- `id` - A destination connection ID
- `data` - A pointer to data to append to the send buffer
- `size` - A data size

Usage example:

Sending small data

```c
// Sender side:
struct foo foo = {0};                   // Small structure, size < 512 bytes
mg_wakeup(mgr, id, &foo, sizeof(foo));  // Send a structure

// Receiver side:
if (ev == MG_EV_WAKEUP) {
  struct mg_str *data = (struct mg_str *) ev_data;
  struct foo *foo = (struct foo *) data->buf;
}
```

Sending large data. Sender allocates it, receiver deallocates

```c
// Sender side:
struct foo *foo = malloc(sizeof(*foo));  // Big structure, allocate it
mg_wakeup(mgr, id, &foo, sizeof(foo));   // Send a pointer to structure

// Receiver side:
if (ev == MG_EV_WAKEUP) {
  struct mg_str *data = (struct mg_str *) ev_data;
  struct foo *foo = * (struct foo **) data->buf;
  // Do something with foo ...
  free(foo);   // Deallocate foo
}
```

### mg\_wakeup\_init()

```c
void mg_wakeup_init(struct mg_mgr *mgr);
```

Initialize the wakeup scheme used by [mg\_wakeup()](#mg_wakeup)

Parameters:

- `mgr` - An event manager

Usage example:

```c
mg_wakeup_init(&mgr);  // Initialise wakeup socket pai
```

### mg\_printf(), mg\_vprintf()

```c
int mg_printf(struct mg_connection *, const char *fmt, ...);
int mg_vprintf(struct mg_connection *, const char *fmt, va_list *ap);
```

Same as `mg_send()`, but formats data using `printf()` semantics. Return number of bytes appended to the output buffer.

> NOTE: See [mg\_snprintf](#mg_snprintf-mg_vsnprintf) for the list of supported format specifiers

Parameters:

- `c` - a connection pointer
- `fmt` - a format string in `printf` semantics

Return value: number of bytes appended to the output buffer.

Usage example:

```c
mg_printf(c, "Hello, %s!", "world"); // Add "Hello, world!" to output buffer
```

### mg\_wrapfd()

```c
struct mg_connection *mg_wrapfd(struct mg_mgr *mgr, int fd,
                                mg_event_handler_t fn, void *fn_data);
```

Wrap a given file descriptor `fd` into a connection, and add that connection to the event manager. An `fd` descriptor
must support `send()`, `recv()`, `select()` syscalls, and be non-blocking. Mongoose will treat it as a TCP socket. The
`c->rem` and `c->loc` addresses will be empty.

Parameters:

- `fd` - A file descriptor to wrap
- `mgr` - An event manager
- `fn` - A pointer to event handler function
- `fn_data` - an arbitrary pointer, which will be stored in the connection structure as `c->fn_data`, so the event
handler can use it when called.

Return value: Pointer to the created connection or `NULL` in case of error

## HTTP

### struct mg\_http\_header

```c
struct mg_http_header {
  struct mg_str name;   // Header name
  struct mg_str value;  // Header value
};
```

Structure represents HTTP header, like `Content-Type: text/html`. `Content-Type` is a header name and `text/html` is a
header value.

### struct mg\_http\_message

```c
struct mg_http_message {
  struct mg_str method, uri, query, proto;             // Request/response line
  struct mg_http_header headers[MG_MAX_HTTP_HEADERS];  // Headers
  struct mg_str body;                                  // Body
  struct mg_str message;                               // Request line + headers + body
};
```

Structure represents the HTTP message.

![HTTP message](https://mongoose.ws/documentation/images/mg_http_message.svg)

### mg\_http\_listen()

```c
struct mg_connection *mg_http_listen(struct mg_mgr *mgr, const char *url,
                                     mg_event_handler_t fn, void *fn_data);
```

Create HTTP listener.

Parameters:

- `mgr` - An event manager
- `url` - A URL, specifies local IP address and port to listen on, e.g. `http://0.0.0.0:8000`. If this URL is 'https',
the `is_tls` flag will be set
- `fn` - An event handler function
- `fn_data` - an arbitrary pointer, which will be stored in the connection structure as `c->fn_data`, so the event
handler can use it when called.

Return value: Pointer to created connection or `NULL` in case of error

Usage example:

```c
struct mg_connection *c = mg_http_listen(&mgr, "0.0.0.0:8000", fn, arg);
if (c == NULL) fatal_error("Cannot create listener");
```

### mg\_http\_connect()

```c
struct mg_connection *mg_http_connect(struct mg_mgr *, const char *url,
                                      mg_event_handler_t fn, void *fn_data);
```

Create HTTP client connection.

Parameters:

- `mgr` - An event manager
- `url` - A URL, specifies the remote URL, e.g. `http://google.com`. If this URL is 'https', the `is_tls` flag will be
set. See [mg\_connect()](#mg_connect)
- `fn` - An event handler function
- `fn_data` - an arbitrary pointer, which will be stored in the connection structure as `c->fn_data`, so the event
handler can use it when called.

Return value: created connection, or `NULL` on error. Possible errors are: not enough memory, a NULL URL, or, in the
case of our built-in TCP/IP stack, the network not being ready.

Note: This function does not connect to the requested peer, it allocates required resources and starts the connection
process. Once our peer is really connected, an `MG_EV_CONNECT` event is sent to the connection event handler.

Usage example:

```c
struct mg_connection *c = mg_http_connect(&mgr, "http://google.com", fn, NULL);
if (c == NULL) fatal_error("Cannot create connection");
```

### mg\_http\_status()

```c
int mg_http_status(const struct mg_http_message *hm);
```

Get status code of the HTTP response. Parameters:

- `hm` - Parsed HTTP response

Return value: status code, e.g. `200` for success.

### mg\_http\_get\_request\_len()

```c
int mg_http_get_request_len(const unsigned char *buf, size_t buf_len);
```

Get length of request.

The length of request is a number of bytes till the end of HTTP headers. It does not include length of HTTP body.

Parameters:

- `buf` - A pointer to a buffer with request
- `buf_len` - Buffer length

Return value: -1 on error, 0 if a message is incomplete, or the length of request

Usage example:

```c
const char *buf = "GET /test \n\nGET /foo\n\n";
int req_len = mg_http_get_request_len(buf, strlen(buf));  // req_len == 12
```
![Function mg_http_get_request_len()](https://mongoose.ws/documentation/images/mg_http_get_request_len.svg)

### mg\_http\_parse()

```c
int mg_http_parse(const char *s, size_t len, struct mg_http_message *hm);
```

Parse string request into `mg_http_message` structure

Parameters:

- `s` - A request string
- `len` - A request string length
- `hm` - A pointer to a structure to store parsed request

Return value: request length (see `mg_http_get_request_len()`)

Usage example:

```c
struct mg_http_message hm;
const char *buf = "GET / HTTP/1.0\n\n";
if (mg_http_parse(buf, strlen(buf), &hm) > 0) { /* success */ }
```

### mg\_http\_printf\_chunk()

```c
void mg_http_printf_chunk(struct mg_connection *c, const char *fmt, ...);
```

Write a chunk of data in chunked encoding format, using `printf()` semantic.

Parameters:

- `c` - A connection pointer
- `fmt` - A string, format specified in `printf` semantics

Return value: None

Usage example:

```c
mg_http_printf_chunk(c, "Hello, %s!", "world");
```

### mg\_http\_write\_chunk()

```c
void mg_http_write_chunk(struct mg_connection *c, const char *buf, size_t len);
```

Write a chunk of data in chunked encoding format.

Parameters:

- `c` - A connection pointer
- `buf` - Data to write
- `len` - Data length

Return value: None

Usage example:

```c
mg_http_write_chunk(c, "hi", 2);
```

### struct mg\_http\_serve\_opts

```c
struct mg_http_serve_opts {
  const char *root_dir;       // Web root directory, must be non-NULL
  const char *ssi_pattern;    // SSI file name pattern, e.g. #.shtml
  const char *extra_headers;  // Extra HTTP headers to add in responses
  const char *mime_types;     // Extra mime types, ext1=type1,ext2=type2,..
  const char *page404;        // Path to the 404 page, or NULL by default
  struct mg_fs *fs;           // Filesystem implementation. Use NULL for POSIX
};
```

A structure passed to `mg_http_serve_dir()` and `mg_http_serve_file()`, which drives the behavior of those two
functions.

In addition to overwriting autodetection based on an extension, you can also use `*` as an extension in `mime_types` to
force a particular MIME type for unknown extensions:

```c
sopts.mime_types = "*=preferred/default,txt=override/text"
```

### mg\_http\_serve\_dir()

```c
void mg_http_serve_dir(struct mg_connection *c, struct mg_http_message *hm,
                       const struct mg_http_serve_opts *opts);
```

Serve static files according to the given options. Files can also be gzip compressed, including the directory index.
All compressed files must end in `.gz` and there must not exist a file with the same name without the extension,
otherwise it will take precedence; see [mg\_http\_serve\_file()](#mg_http_serve_file)

> NOTE: In order to enable SSI, you need to set the `-DMG_ENABLE_SSI=1` build flag.

> NOTE: Avoid double dots `..` in the `root_dir`. If you need to reference an upper-level directory, use an absolute
path.

Parameters:

- `c` - Connection to use
- `hm` - HTTP message, that should be served
- `opts` - Serve options. Note that `opts.root_dir` can optionally accept extra comma-separated `uri=path` pairs, see
example below

Return value: None

Usage example:

```c
// Mongoose events handler
void fn(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_HTTP_MSG) {
    struct mg_http_message *hm = (struct mg_http_message *) ev_data;
    struct mg_http_serve_opts opts;
    memset(&opts, 0, sizeof(opts));
    opts.root_dir = "/var/www,/conf=/etc";  // Serve /var/www. URIs starting with /conf are served from /etc
    mg_http_serve_dir(c, hm, &opts);
  }
}
```

### mg\_http\_serve\_file()

```c
void mg_http_serve_file(struct mg_connection *c, struct mg_http_message *hm,
                        const char *path, struct mg_http_serve_opts *opts);
```

Serve a static file. If a file with the filename specified in `path` does not exist, Mongoose tries appending `.gz`;
and if such a file exists, it will serve it with a `Content-Encoding: gzip` header

> NOTE: `opts->root_dir` settings is ignored by this function.

> NOTE: `opts->extra_headers`, if not NULL, must end with `\r\n`.

Parameters:

- `c` - Connection to use
- `hm` - HTTP message to serve
- `path` - Path to file to serve
- `opts` - Serve options

Return value: None

Usage example:

```c
// Mongoose events handler
void fn(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_HTTP_MSG) {
    struct mg_http_message *hm = (struct mg_http_message *) ev_data;
    struct mg_http_serve_opts opts = {
      .mime_types = "png=image/png",
      .extra_headers = "AA: bb\r\nCC: dd\r\n"
    };
    mg_http_serve_file(c, hm, "a.png", &opts);
  }
}
```

### mg\_http\_reply()

```c
void mg_http_reply(struct mg_connection *c, int status_code,
                   const char *headers, const char *body_fmt, ...);
```

Send simple HTTP response using `printf()` semantic. This function formats response body according to a `body_fmt`, and
automatically appends a correct `Content-Length` header. Extra headers could be passed via `headers` parameter.

Parameters:

- `c` - Connection to use
- `status_code` - An HTTP response code
- `headers` - Extra headers, default NULL. If not NULL, must end with `\r\n`
- `fmt` - A format string for the HTTP body, in a printf semantics

Return value: None

![Function mg_http_reply()](https://mongoose.ws/documentation/images/mg_http_reply.svg)

Usage examples:

Send a simple JSON response:

```c
mg_http_reply(c, 200, "Content-Type: application/json\r\n", "{\"result\": %d}", 123);
```

Send JSON response:

```c
char *json = mg_mprintf("{%m:%d}", MG_ESC("name"), 123);
mg_http_reply(c, 200, "Content-Type: application/json\r\n", "%s\n", json);
mg_free(json);
```

Send a 302 redirect:

```c
mg_http_reply(c, 302, "Location: /\r\n", "");
```

Send error:

```c
mg_http_reply(c, 403, "", "%s", "Not Authorized\n");
```

### mg\_http\_get\_header()

```c
struct mg_str *mg_http_get_header(struct mg_http_message *hm, const char *name);
```

Get HTTP header value

Parameters:

- `hm` - HTTP message to look for header
- `name` - Header name

Return value: HTTP header value or `NULL` if not found

Usage example:

```c
// Mongoose event handler
void fn(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_HTTP_MSG) {
    struct mg_http_message *hm = (struct mg_http_message *) ev_data;
    struct mg_str *s = mg_http_get_header(hm, "X-Extra-Header");
    if (s != NULL) {
      mg_http_reply(c, 200, "", "Holly molly! Header value: %.*s", (int) s->len, s->buf);
    } else {
      mg_http_reply(c, 200, "", "Oh no, header is not set...");
    }
  }
}
```

### mg\_http\_get\_header\_var()

```c
struct mg_str mg_http_get_header_var(struct mg_str s, struct mg_str v);
```

Parse HTTP header (e.g. Cookie header) which has form `name1=value1; name2=value2; ...` and fetch a given variable.

Parameters:

- `s` - HTTP header
- `name` - variable name name

Return value: a requested variable, or an empty string.

Usage example:

```c
struct mg_str *cookie = mg_http_get_header(hm, "Cookie");
struct mg_str token = mg_str("");

if (cookie != NULL) {
  token = mg_http_get_header_var(*cookie, mg_str("access_token"));
}
```

### mg\_http\_var()

```c
struct mg_str mg_http_var(struct mg_str buf, struct mg_str name);
```

Fetch an undecoded HTTP variable. Parameters:

- `buf` - a url-encoded string: HTTP request body or query string
- `name` - a variable name to fetch

Return value: variable's value. If not found, it is a NULL string.

```c
// We have received a request to /my/uri?a=b&c=d%20
// The hm->query points to "a=b&c=d%20"
struct mg_str v = mg_http_var(hm->query, mg_str("c"));  // v = "d%20"
```

### mg\_http\_get\_var()

```c
int mg_http_get_var(const struct mg_str *var, const char *name, char *buf, int len);
```

Fetch and decode an HTTP variable

Parameters:

- `var` - HTTP request body
- `name` - Variable name
- `buf` - Buffer to write decoded variable
- `len` - Buffer size

Return value: Length of decoded variable. A zero or negative value means error

Usage example:

```c
char buf[100] = "";
mg_http_get_var(&hm->body, "key1", buf, sizeof(buf)) {
  ...
}
```

### mg\_http\_creds()

```c
void mg_http_creds(struct mg_http_message *hm, char *user, size_t userlen,
                   char *pass, size_t passlen);
```

Fetch authentication credential from the request, and store into the `user`, `userlen` and `pass`, `passlen` buffers.
The credentials are looked up in the following order:

- from the `Authorization` HTTP header,
	- Basic auth fills both user and pass
		- Bearer auth fills only pass
- from the `access_token` cookie, fills pass
- from the `?access_token=...` query string parameter, fills pass

If none is found, then both user and pass are set to empty nul-terminated strings.

For JWT Bearer authorization, see the [JWT Bearer Authorization
guide](https://mongoose.ws/docs/guides/jwt-bearer-authorization/).

Parameters:

- `hm` - HTTP message to look for credentials
- `user` - buffer to receive user name
- `userlen` - size of `user` buffer
- `pass` - buffer to receive password
- `passlen` - size of `pass` buffer

Return value: None

Usage example:

```c
// Mongoose events handler
void fn(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_HTTP_MSG) {
    struct mg_http_message *hm = (struct mg_http_message *) ev_data;
    char user[100], pass[100];
    mg_http_creds(hm, user, sizeof(user), pass, sizeof(pass)); // "user" is now user name and "pass" is now password
from request
  }
}
```

### mg\_http\_bauth()

```c
void mg_http_bauth(struct mg_connection *c, const char *user, const char *pass);
```

Write a Basic `Authorization` header to the output buffer.

Parameters:

- `c` - Connection to use
- `user` - User name
- `pass` - Password

Return value: None

Usage example which uses Basic auth to create Stripe subscription:

```c
mg_printf(c, "POST /v1/subscriptions HTTP/1.1\r\n"
             "Host: api.stripe.com\r\n"
             "Transfer-Encoding: chunked\r\n");
mg_http_bauth(c, stripe_private_key, NULL);     // Add Basic auth header
mg_printf(c, "%s", "\r\n");                     // End HTTP headers

mg_http_printf_chunk(c, "&customer=%s", customer_id);   // Set customer
mg_http_printf_chunk(c, "&items[0][price]=%s", price);  // And price
mg_http_printf_chunk(c, "");                            // End request
```

### struct mg\_http\_part

```c
// Parameter for mg_http_next_multipart
struct mg_http_part {
  struct mg_str name;      // Form field name
  struct mg_str filename;  // Filename for file uploads
  struct mg_str body;      // Part contents
};
```

Structure that describes a single part of a HTTP multipart message.

![HTTP part](https://mongoose.ws/documentation/images/mg_http_part.svg)

### mg\_http\_next\_multipart()

```c
size_t mg_http_next_multipart(struct mg_str body, size_t offset, struct mg_http_part *part);
```

Parse the multipart chunk in the `body` at a given `offset`. An initial `offset` should be 0. Fill up parameters in the
provided `part`, which could be NULL. Return offset to the next chunk, or 0 if there are no more chunks.

Parameters:

- `body` - Message body
- `offset` - Start offset
- `part` - Pointer to `struct mg_http_part` to fill

Return value: offset to the next chunk, or 0 if there are no more chunks.

Usage example (or see [form upload tutorial](https://mongoose.ws/documentation/tutorials/http/file-uploads/) ):

```c
struct mg_http_part part;
size_t pos = 0;

while ((pos = mg_http_next_multipart(body, pos, &part)) != 0) {
  MG_INFO(("Chunk name: [%.*s] filename: [%.*s] length: %lu bytes",
           part.name.len, part.name.buf,
           part.filename.len, part.filename.buf, part.body.len));
  // Use this chunk ....
}
```

A diagram below shows how `mg_http_next_multipart()` in action:

![Function mg_http_next_multipart()](https://mongoose.ws/documentation/images/mg_http_next_multipart.svg)

### mg\_http\_upload()

```c
long mg_http_upload(struct mg_connection *c, struct mg_http_message *hm,
                    struct mg_fs *fs, const char *dir, size_t max_size);
```

This is a helper utility function that is used to upload large files by small chunks.

Append HTTP POST data to a file in a specified directory. A file name and file offset are specified by the query string
parameters: `POST /upload?file=firmware.bin&offset=2048 HTTP/1.1`. If the offset is 0, then the file is truncated. It
is the client's responsibility to divide files into smaller chunks and send a sequence of POST requests that will be
handled by this function. The full path will be checked for sanity

Parameters:

- `c` - a connection
- `hm` - a parsed HTTP message
- `fs` - a filesystem where to write the files, e.g. `&mg_fs_posix`
- `dir` - a directory path where to write the files
- `max_size` - maximum allowed file size

Return value: file size after write, or negative number on error

Usage example:

```c
static void fn(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_HTTP_MSG) {
    struct mg_http_message *hm = (struct mg_http_message *) ev_data;
    if (mg_match(hm->uri, mg_str("/upload"), NULL)) {
      mg_http_upload(c, hm, &mg_fs_posix, "/tmp", 99999);
    } else {
      struct mg_http_serve_opts opts = {.root_dir = "."};   // Serve
      mg_http_serve_dir(c, ev_data, &opts);                 // static content
    }
  }
}
```

## WebSocket

### struct mg\_ws\_message

```c
struct mg_ws_message {
  struct mg_str data; // WebSocket message data
  uint8_t flags;      // WebSocket message flags
};
```

This structure represents the WebSocket message, the `flags` element corresponds to the first byte as described in [RFC
6455 section 5.2](https://www.rfc-editor.org/rfc/rfc6455#section-5.2).

To extract the message type from an incoming message, check the four LSBs in the `flags` element of the `struct
mg_ws_message`.

Possible WebSocket message types:

```c
#define WEBSOCKET_OP_CONTINUE 0
#define WEBSOCKET_OP_TEXT 1
#define WEBSOCKET_OP_BINARY 2
#define WEBSOCKET_OP_CLOSE 8
#define WEBSOCKET_OP_PING 9
#define WEBSOCKET_OP_PONG 10
```
```c
// Mongoose events handler
void fn(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_WS_MSG) {
    struct mg_ws_message *wm = (struct mg_ws_message *) ev_data;
    msgtype = wm->flags & 0x0F;
    if (msgtype == WEBSOCKET_OP_BINARY) {
      // This is a binary data message
    } else if (msgtype == WEBSOCKET_OP_TEXT) {
      // This is a text data message
    }
  }
}
```

To send a message, use the proper message type as described in [RFC 6455 section
5.6](https://www.rfc-editor.org/rfc/rfc6455#section-5.6) for data frames. when calling [mg\_ws\_send()](#mg_ws_send) or
[mg\_ws\_printf()](#mg_ws_printf-mg_ws_vprintf) below

### mg\_ws\_connect()

```c
struct mg_connection *mg_ws_connect(struct mg_mgr *mgr, const char *url,
                                    mg_event_handler_t fn, void *fn_data,
                                    const char *fmt, ...);
```

Create a client WebSocket connection.

Parameters:

- `mgr` - Event manager to use
- `url` - Specifies the remote URL, e.g. `ws://somewhere.com`. If this URL is 'wss', the `is_tls` flag will be set. See
[mg\_connect()](#mg_connect)
- `fn` - An event handler function
- `fn_data` - an arbitrary pointer, which will be stored in the connection structure as `c->fn_data`, so the event
handler can use it when called.
- `fmt` - format string in `printf` semantics for additional HTTP headers, or NULL. See
[mg\_snprintf](#mg_snprintf-mg_vsnprintf) for the list of supported format specifiers

Return value: created connection, or `NULL` on error. Possible errors are: not enough memory, a NULL URL, or, in the
case of our built-in TCP/IP stack, the network not being ready.

Note: This function does not connect to the requested peer, it allocates required resources and starts the connection
process. Once our peer is really connected, an `MG_EV_CONNECT` event is sent to the connection event handler.

Usage example:

```c
struct mg_connection *c = mg_ws_connect(&mgr, "ws://test_ws_server.com:1000",
                                        handler, NULL, "%s", "Sec-WebSocket-Protocol: echo\r\n");
if(c == NULL) fatal("Cannot create connection");
```

### mg\_ws\_upgrade()

```c
void mg_ws_upgrade(struct mg_connection *c, struct mg_http_message *,
                   const char *fmt, ...);
```

Upgrade given HTTP connection to WebSocket. Parameter `fmt` is a printf-like format string for the extra HTTP headers
returned to the client in a WebSocket handshake. Set it to `NULL` if no extra headers need to be passed.

Parameters:

- `c` - Connection to use
- `hm` - HTTP message
- `fmt` - format string in `printf` semantics for additional HTTP headers, or NULL. See
[mg\_snprintf](#mg_snprintf-mg_vsnprintf) for the list of supported format specifiers

Return value: None

Usage example:

```c
// Mongoose events handler
void fn(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_HTTP_MSG) {
    struct mg_http_message *hm = (struct mg_http_message *) ev_data;
    mg_ws_upgrade(c, hm, NULL);  // Upgrade HTTP to WS
  }
}
```

### mg\_ws\_send()

```c
size_t mg_ws_send(struct mg_connection *c, const void *buf, size_t len, int op);
```

Send data to WebSocket peer

Parameters:

- `c` - Connection to use
- `buf` - Data to send
- `len` - Data size
- `op` - WebSocket message type, see [WebSocket message type](#websocket-message-type) above

Return value: sent bytes count

Usage example:

```c
// Mongoose events handler
void fn(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_WS_OPEN) {
    struct mg_http_message *hm = (struct mg_http_message *) ev_data;
    mg_ws_send(c, "opened", 6, WEBSOCKET_OP_BINARY);  // Send "opened" to web socket connection
  }
}
```

### mg\_ws\_printf(), mg\_ws\_vprintf()

```c
size_t mg_ws_printf(struct mg_connection *, int op, const char *fmt, ...);
size_t mg_ws_vprintf(struct mg_connection *, int op, const char *fmt, va_list *);
```

Same as `mg_ws_send()`, but formats data using `printf()` semantics.

Parameters:

- `c` - Connection to use
- `op` - WebSocket message type, see [WebSocket message type](#websocket-message-type) above
- `fmt` - format string in `printf` semantics. See [mg\_snprintf](#mg_snprintf-mg_vsnprintf) for the list of supported
format specifiers

Return value: sent bytes count

Usage example:

```c
mg_ws_printf(c, WEBSOCKET_OP_TEXT, "Hello, %s!", "world");
```

### mg\_ws\_wrap()

```c
size_t mg_ws_wrap(struct mg_connection *c, size_t len, int op)
```

Convert data in output buffer to WebSocket format. Useful when implementing a protocol over WebSocket See
[tutorials/mqtt/mqtt-over-ws-client](https://github.com/cesanta/mongoose/tree/master/tutorials/mqtt/mqtt-over-ws-client)
 for a full example.

Parameters:

- `c` - Connection to use
- `len` - Bytes count to convert
- `op` - Websocket message type (see `mg_ws_send`)

Return value: New size of connection output buffer

Usage example:

```c
size_t len = c->send.len;         // Store output buffer len
mg_mqtt_login(c, s_url, &opts);   // Write MQTT login message
mg_ws_wrap(c, c->send.len - len, WEBSOCKET_OP_BINARY); // Wrap it into WS
```

## SNTP

### mg\_sntp\_connect()

```c
struct mg_connection *mg_sntp_connect(struct mg_mgr *mgr, const char *url,
                                      mg_event_handler_t fn, void *fn_data)
```

Connect to an SNTP server.

Parameters:

- `mgr` - Event manager to use
- `url` - Specifies the remote URL, `time.google.com` if NULL. See [mg\_connect()](#mg_connect)
- `fn` - A user event handler function, use NULL if you don't need one
- `fn_data` - an arbitrary pointer, which will be stored in the connection structure as `c->fn_data`, so the event
handler can use it when called.

Return value: created connection, or `NULL` on error. Possible errors are: not enough memory, a NULL URL, or, in the
case of our built-in TCP/IP stack, the network not being ready.

Simplest usage example: see [mg\_now()](#mg_now)

Full usage example:

```c
static void sntp_cb(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_SNTP_TIME) {
    // Time received, the internal protocol handler updates what mg_now() returns
    uint64_t curtime = mg_now();
    // otherwise, you can process the server returned data yourself
    uint64_t epoch_millis = *(uint64_t *) ev_data;
  }
}
...
mg_sntp_connect(mgr&, NULL /* connect to time.google.com */, sntp_cb, NULL);
```

### mg\_sntp\_request()

```c
void mg_sntp_request(struct mg_connection *c)
```

Send time request to SNTP server

Parameters:

- `c` - Connection to use

Return value: None

Usage example:

```c
mg_sntp_request(c);
```

## MQTT

### struct mg\_mqtt\_opts

```c
struct mg_mqtt_opts {
  struct mg_str user;               // Username, can be empty
  struct mg_str pass;               // Password, can be empty
  struct mg_str client_id;          // Client ID
  struct mg_str topic;              // message/subscription topic
  struct mg_str message;            // message content
  uint8_t qos;                      // message quality of service
  uint8_t version;                  // Can be 4 (3.1.1), or 5. If 0, assume 4
  uint16_t keepalive;               // Keep-alive timer in seconds
  uint16_t retransmit_id;           // For PUBLISH, init to 0
  bool retain;                      // Retain flag
  bool clean;                       // Clean session flag
  struct mg_mqtt_prop *props;       // MQTT5 props array
  size_t num_props;                 // number of props
  struct mg_mqtt_prop *will_props;  // Valid only for CONNECT packet (MQTT5)
  size_t num_will_props;            // Number of will props
};
```

Structure used when connecting to a broker and when sending messages, to specify connection options and last-will
message or to specify message and options

### struct mg\_mqtt\_message

```c
struct mg_mqtt_message {
  struct mg_str topic;  // Parsed topic for PUBLISH
  struct mg_str data;   // Parsed message for PUBLISH
  struct mg_str dgram;  // Whole MQTT packet, including headers
  uint16_t id;          // For PUBACK, PUBREC, PUBREL, PUBCOMP, SUBACK, PUBLISH
  uint8_t cmd;          // MQTT command, one of MQTT_CMD_*
  uint8_t qos;          // Quality of service
  uint8_t ack;          // CONNACK return code, 0 = success
  size_t props_start;   // Offset to the start of the properties (MQTT5)
  size_t props_size;    // Length of the properties
};
```

Structure representing an MQTT packet, either control or data

### mg\_mqtt\_connect()

```c
struct mg_connection *mg_mqtt_connect(struct mg_mgr *mgr, const char *url,
                                      const struct mg_mqtt_opts *opts,
                                      mg_event_handler_t fn, void *fn_data);
```

Create a client MQTT connection

Parameters:

- `mgr` - Event manager to use
- `url` - Specifies the broker URL, e.g. `mqtt://cloud.hivemq.com`. If this URL is 'mqtts', the `is_tls` flag will be
set. See [mg\_connect()](#mg_connect)
- `opts` - pointer to [MQTT options](#struct-mg_mqtt_opts) like client ID, clean session, last will, etc. Can be NULL
- `fn` - The event handler function
- `fn_data` - an arbitrary pointer, which will be stored in the connection structure as `c->fn_data`, so the event
handler can use it when called.

Return value: created connection, or `NULL` on error. Possible errors are: not enough memory, a NULL URL, or, in the
case of our built-in TCP/IP stack, the network not being ready.

Note: This function does not connect to a broker; it allocates the required resources and starts the TCP connection
process. Once that connection is established, an `MG_EV_CONNECT` event is sent to the connection event handler, then
the MQTT connection process is started (by means of [mg\_mqtt\_login()](#mg_mqtt_login)); and once the MQTT connection
request gets a response from the broker, an `MG_EV_MQTT_OPEN` event is sent to the connection event handler; connection
results are inside a [struct mg\_mqtt\_message](#struct-mg_mqtt_message)

Usage example:

```c
void fn(struct mg_connection *c, int ev, void *evd, void *fnd) {
  if (ev == MG_EV_CONNECT) {
    // TCP connection succeeded,
    // If target URL is TLS, set it up
  } else if (ev == MG_EV_MQTT_OPEN) {
    // MQTT connection process finished
    struct mg_mqtt_message *mm = (struct mg_mqtt_message *) ev_data;
    if(mm->ack)  // MQTT connection succeeded
  }
}
```
```c
mg_mqtt_connect(&mgr, "mqtt://test.org:1883", NULL, fn, NULL);
```

or

```c
struct mg_mqtt_opts opts = {.qos = 1,
                            .retain = true,
                            .topic = mg_str("mytopic"),
                            .message = mg_str("goodbye")};
mg_mqtt_connect(&mgr, "mqtt://test.org:1883", &opts, fn, NULL);
```

### mg\_mqtt\_listen()

```c
struct mg_connection *mg_mqtt_listen(struct mg_mgr *mgr, const char *url,
                                     mg_event_handler_t fn, void *fn_data);
```

Create an MQTT listener (act like a broker).

Parameters:

- `mgr` - Event manager to use
- `url` - Specifies the local IP address and port to listen on, e.g. `mqtt://0.0.0.0:1883`. If this URL is 'mqtts', the
`is_tls` flag will be set
- `fn` - The event handler function
- `fn_data` - an arbitrary pointer, which will be stored in the connection structure as `c->fn_data`, so the event
handler can use it when called.

Return value: Pointer to the created connection or `NULL` on error

Usage example:

```c
struct mg_connection *c = mg_mqtt_listen(&mgr, "mqtt://0.0.0.0:1883", fn, arg);
if (c == NULL) return -1; // Could not create connection
```

### mg\_mqtt\_login()

```c
void mg_mqtt_login(struct mg_connection *c, const struct mg_mqtt_opts *opts);
```

Send MQTT CONNECT request. Once the MQTT connection request gets a response from the broker, an `MG_EV_MQTT_OPEN` event
is sent to the connection event handler. This function is usually called by [mg\_mqtt\_connect()](#mg_mqtt_connect),
you will only need to call it when you manually start the MQTT connect process, e.g: when using MQTT over WebSocket.
Connection results are inside a [struct mg\_mqtt\_message](#struct-mg_mqtt_message)

Parameters:

- `c` - Connection to use
- `opts` - pointer to [MQTT connect options](#struct-mg_mqtt_opts), containing user name and password to use, if any,
and other options

Return value: None

Usage example:

```c
// Mongoose event handler
void fn(struct mg_connection *c, int ev, void *evd, void *fnd) {
  if (ev == MG_EV_WS_OPEN) {
    // WS connection established. Perform MQTT login
    struct mg_mqtt_opts opts = {.qos = 1,
                                .retain = true,
                                .topic = mg_str("mytopic"),
                                .message = mg_str("goodbye")};
    mg_mqtt_login(c, &opts);
  } else if (ev == MG_EV_MQTT_OPEN) {
    // MQTT connection process finished
    struct mg_mqtt_message *mm = (struct mg_mqtt_message *) ev_data;
    if(mm->ack)  // MQTT connection succeeded
  }
}
```

### mg\_mqtt\_pub()

```c
uint16_t mg_mqtt_pub(struct mg_connection *c, const struct mg_mqtt_opts *opts);
```

Publish a message to a specified topic, each contained in a `struct msg_str`

Note: This function does not actually send the message, it delivers to the underlying TCP/IP stack which will be
checked later when the manager runs.

Note that Mongoose does not handle retries for QoS 1 and 2. That has to be handled by the application in the event
handler, if needed. You can check if a publish request with QoS 1 or 2 succeeded by catching `MG_EV_MQTT_CMD` events
and checking for reception of PUBACK/PUBREC and PUBCOMP messsages; and their result codes inside a `struct
mg_mqtt_message`

Parameters:

- `c` - Connection to use
- `opts` - pointer to publish [MQTT options](#struct-mg_mqtt_opts), like QoS, and retain flag. The message body is
expected at `opts->message`, the topic at `opts->topic`; both as [mg\_str](#struct-mg_str)

Return value: When using QoS other than 0, this function returns the `id` field sent to the broker, suitable to be held
in `opts->retransmit_id` for a possible retransmission. See [this
tutorial](https://mongoose.ws/documentation/tutorials/mqtt/mqtt-client/#sending-qos-1-messages). Discard the returned
value if not interested in doing retransmissions, and initialize `opts->retransmit_id` as `0`.

Usage example:

```c
struct mg_mqtt_opts pub_opts = {.topic = mg_str("mytopic"),
                                .message = mg_str("hello"),
                                .qos = 1,
                                .retain = false};
mg_mqtt_pub(c, &pub_opts);
```

### mg\_mqtt\_sub()

```c
void mg_mqtt_sub(struct mg_connection *c, const struct mg_mqtt_opts *opts);
```

Subscribe to a topic specified as a `struct msg_str`. You can check if a subscription request succeeded by catching
`MG_EV_MQTT_CMD` events and checking for reception of a PUBACK messsage and its result code inside the `struct
mg_mqtt_message`

Reception of a message will trigger an `MG_EV_MQTT_MSG` event providing a [struct
mg\_mqtt\_message](#struct-mg_mqtt_message). Note that Mongoose does not handle broker retries for QoS 2 and duplicated
messages have to be handled by the application in the event handler, if required

Parameters:

- `c` - Connection to use
- `opts` - pointer to subscription [MQTT options](#struct-mg_mqtt_opts), like QoS. The topic is expected at
`opts->topic` as an [mg\_str](#struct-mg_str)

Return value: None

```c
// Mongoose event handler
void fn(struct mg_connection *c, int ev, void *evd, void *fnd) {
  if (ev == MG_EV_MQTT_MSG) {
    struct mg_mqtt_message *mm = (struct mg_mqtt_message *) ev_data;
    MG_INFO(("%.*s\t%.*s", (int) mm->topic.len, mm->topic.buf),
             (int) mm->data.len, mm->data.buf);
  }
}

struct mg_mqtt_opts sub_opts = {.topic = mg_str("mytopic"),
                                .qos = 1};
mg_mqtt_sub(c, &sub_opts);
```

### mg\_mqtt\_send\_header()

```c
void mg_mqtt_send_header(struct mg_connection *c, uint8_t cmd, uint8_t flags, uint32_t len);
```

Send an MQTT command header. Useful in handling QoS 2 and MQTT server implementations. The command can be one of the
following:

```c
#define MQTT_CMD_CONNECT 1
#define MQTT_CMD_CONNACK 2
#define MQTT_CMD_PUBLISH 3
#define MQTT_CMD_PUBACK 4
#define MQTT_CMD_PUBREC 5
#define MQTT_CMD_PUBREL 6
#define MQTT_CMD_PUBCOMP 7
#define MQTT_CMD_SUBSCRIBE 8
#define MQTT_CMD_SUBACK 9
#define MQTT_CMD_UNSUBSCRIBE 10
#define MQTT_CMD_UNSUBACK 11
#define MQTT_CMD_PINGREQ 12
#define MQTT_CMD_PINGRESP 13
#define MQTT_CMD_DISCONNECT 14
```

Parameters:

- `c` - Connection to use
- `cmd` - Command (see above)
- `flags` - Command flags (see MQTT specs)
- `len` - Size of what follows this header

Return value: None

Usage example:

```c
// Mongoose event handler
void fn(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_MQTT_CMD) {
    struct mg_mqtt_message *mm = (struct mg_mqtt_message *) ev_data;
    if (mm->cmd == MQTT_CMD_CONNECT) {
        uint8_t response[] = {0, 0};
        mg_mqtt_send_header(c, MQTT_CMD_CONNACK, 0, sizeof(response));  // Send acknowledgement
        mg_send(c, response, sizeof(response));
    }
  }
}
```

### mg\_mqtt\_ping()

```c
void mg_mqtt_ping(struct mg_connection *c);
```

Send an `MQTT_CMD_PINGREQ` command via [mg\_mqtt\_send\_header()](#mg_mqtt_send_header)

Parameters:

- `c` - Connection to use

Return value: None

Usage example:

```c
// Send periodic pings to all (MQTT over) WS connections
static void timer_fn(void *arg) {
  struct mg_mgr *mgr = (struct mg_mgr *) arg;
  for (struct mg_connection *c = mgr->conns; c != NULL; c = c->next) {
    if (c->is_websocket) mg_mqtt_ping(c);
  }
}
```

### mg\_mqtt\_parse()

```c
int mg_mqtt_parse(const uint8_t *buf, size_t len, struct mg_mqtt_message *m);
```

Parse a buffer and fill an `mg_mqtt_message` structure if it contains a valid MQTT packet.

Parameters:

- `buf` - buffer with MQTT packet to parse
- `len` - buffer length
- `m` - pointer to a [struct mg\_mqtt\_message](#struct-mg_mqtt_message) to be filled with the parsed message

Return value: `MQTT_OK` if message is successfully parsed, `MQTT_INCOMPLETE` if message isn't fully received and
`MQTT_MALFORMED` if message has a wrong format.

Usage example:

```c
// Iterate over all MQTT frames contained in buf, len
struct mg_mqtt_message mm;
while ((mg_mqtt_parse(buf, len, &mm)) == MQTT_OK) {
  switch (mm.cmd) {
    case MQTT_CMD_CONNACK:
      ...
  }
  buf += mm.dgram.len;
  len -= mm.dgram.len;
}
```

### mg\_mqtt\_unsub()

```c
void mg_mqtt_unsub(struct mg_connection *c, const struct mg_mqtt_opts *opts);
```

Remove subscription (unsubscribe) to a topic previously subscribed to using [mg\_mqtt\_sub()](#mg_mqtt_sub).

Parameters:

- `c` - Connection to use
- `opts` - pointer to [MQTT options](#struct-mg_mqtt_opts). The topic is expected at `opts->topic` as an
[mg\_str](#struct-mg_str)

Return value: None

```c
struct mg_mqtt_opts sub_opts = {.topic = mg_str("mytopic"),
                                .qos = 1};
mg_mqtt_sub(c, &sub_opts);
...
mg_mqtt_unsub(c, &sub_opts);
```

### mg\_mqtt\_disconnect()

```c
void mg_mqtt_disconnect(struct mg_connection *c, const struct mg_mqtt_opts *opts);
```

End an client MQTT connection

Note: This function does not destroy a connection; it just sends a disconnect request to the broker. Once the
connection is terminated, an `MG_EV_CLOSE` event will be sent to the connection event handler

Parameters:

- `c` - Connection to use
- `opts` - pointer to [MQTT options](#struct-mg_mqtt_opts), can be NULL for MQTT 3.1.1 connections

Return value: None

## mDNS

### struct mg\_mdns\_req

```c
struct mg_mdns_req {
  struct mg_dns_rr *rr;         // Parsed resource record from the incoming query
  struct mg_dnssd_record *r;    // User-supplied service record to include in the response
  struct mg_str reqname;        // Queried hostname, without the .local suffix
  struct mg_str respname;       // Hostname to use in response; defaults to fn_data if empty
  struct mg_addr *addr;         // IP address for A record; uses local interface if NULL
  bool is_listing;  // True if this is a service-discovery listing (_services._dns-sd._udp)
  bool is_resp;     // Set to true in the handler to trigger a response
  bool is_unicast;  // True if the client requested a unicast (QU) response
};
```

Structure pointed to by `ev_data` on an mDNS event handler function for an `MG_EV_MDNS_REQ` event.

[DNS-SD](#dns-sd) users will store a valid pointer to a [struct mg\_dnssd\_record](#struct-mg_dnssd_record) in the `r`
field, based on the requested name available in `reqname`.

### struct mg\_mdns\_resp

```c
struct mg_mdns_resp {
  struct mg_dns_rr *rr;  // Resource record from the response (1st in chain)
  struct mg_str name;    // Resolved hostname, without the .local suffix
  struct mg_addr addr;   // Resolved IP address
  struct mg_dnssd_record sd; // Service Discovery data
};
```

Structure pointed to by `ev_data` on an mDNS event handler function for an `MG_EV_MDNS_RESP` event.

### mg\_mdns\_listen()

```c
struct mg_connection *mg_mdns_listen(struct mg_mgr *mgr, mg_event_handler_t fn, void *fn_data);
```

Create an mDNS listener/responder \[for the given `hostname`\].

Parameters:

- `c` - Connection to use
- `fn` - The event handler function, if any; can be NULL
- `fn_data` - an arbitrary pointer, which will be stored in the connection structure as `c->fn_data`, so the event
handler can use it when called; can be NULL

Return value: mDNS connection.

Server usage example:

- see [mdns-server](https://github.com/cesanta/mongoose/tree/master/tutorials/udp/mdns-server)

If `fn_data` is passed, then it is a pointer to a buffer that holds a NUL-terminated `hostname` string. Must be valid
during the connection lifetime. Mongoose accepts only name queries for that host name, answering by itself; regardless
of an event handler function.

If an event handler function is passed, this function is called for mDNS requests with an `MG_EV_MDNS_REQ` event, as
follows:

- If `fn_data` is passed, only those requests (name or service queries) for that host name are processed, as described
above. This can be used to implement a [DNS-SD](#dns-sd) listener/responder for a typical host, using mDNS.
- Otherwise, all mDNS requests trigger the event handler. This can be used, for example, to support several host names
on a device.

Client usage example:

- see [mdns-client](https://github.com/cesanta/mongoose/tree/master/tutorials/udp/mdns-client)

An event handler function is not always required. If passed, this function will be called for mDNS responses, with an
`MG_EV_MDNS_RESP` event. Users will then compare the received information to what they're looking for. However, if you
just want to have a listener so Mongoose resolver can resolve '.local' address via mDNS, you will pass NULL as argument.

### mg\_mdns\_query()

```c
bool mg_mdns_query(struct mg_connection *c, const char *name, unsigned int rtype);
```

Issue an mDNS request of type `rtype` for the given `name`. Any responses will be handled by an event handler
registered at opening a listener, by calling [mg\_mdns\_listen](#mg_mdns_listen).

Parameters:

- `c` - Connection to use, returned when opening the listener
- `name` - The host or service name to query
- `rtype` - The type of record (MG\_DNS\_RTYPE\_A, PTR, SRV, TXT) to request

Return value: success/failure

Usage example:

- see [mdns-client](https://github.com/cesanta/mongoose/tree/master/tutorials/udp/mdns-client)

## DNS-SD

### struct mg\_dnssd\_record

```c
// DNS-SD response record
struct mg_dnssd_record {
  struct mg_str srvcproto;  // Service and protocol label, e.g. "_http._tcp"
  struct mg_str txt;        // TXT record contents, verbatim
  uint16_t port;            // Port number for the SRV record
};
```

Structure used to tell [mDNS](#mdns) how to answer to PTR, TXT and SRV record requests, so implementing a DNS-SD
service. It is also present on a response to a DNS-SD query

Server usage example:

- see [mdns-sd-server](https://github.com/cesanta/mongoose/tree/master/tutorials/udp/mdns-sd-server)

Client usage example:

- see [mdns-sd-client](https://github.com/cesanta/mongoose/tree/master/tutorials/udp/mdns-sd-client)

## TLS

### struct mg\_tls\_opts

```c
struct mg_tls_opts {
  struct mg_str ca;    // CA certificate; for both listeners and clients. PEM or DER
  struct mg_str cert;  // Certificate. PEM or DER
  struct mg_str key;   // Private key. PEM or DER
  struct mg_str name;  // If not empty, enable server name verification
};
```

TLS options structure:

- `ca` - Certificate Authority, an [mg\_str](#struct-mg_str). Used to verify the certificate that the other end sends
to us. If NULL, then server authentication for clients and client authentication for servers are disabled
- `cert` - Our own certificate; an [mg\_str](#struct-mg_str). If NULL, then we don't authenticate ourselves to the
other peer
- `key` - Our own private key; an [mg\_str](#struct-mg_str). Sometimes, a certificate and its key are bundled in a
single PEM file, in which case the values for `cert` and `key` could be the same
- `name` - Server name; an [mg\_str](#struct-mg_str). If not empty, enable server name verification

> NOTE: if both `ca` and `cert` are set, then two-way (mutual) TLS authentication is enabled, both sides authenticate
each other. Usually, for one-way (server) TLS authentication, server connections set both `key` and `cert`, whilst
clients only `ca` and/or possibly `name`.

For more information on developing TLS clients and servers, and how to load credentials, see the [TLS
tutorial](https://mongoose.ws/documentation/tutorials/tls/)

### mg\_tls\_init()

```c
void mg_tls_init(struct mg_connection *c, const struct mg_tls_opts *);
```

Initialise TLS on a given connection.

> NOTE: The mbedTLS implementation uses `mg_random` as RNG. The `mg_random` function can be overridden by setting
`MG_ENABLE_CUSTOM_RANDOM=1` and defining your own `mg_random()` implementation.

Parameters:

- `c` - Connection, for which TLS should be initialized
- `opts` - TLS initialization parameters

Return value: None

Usage example:

```c
// client event handler:
  if (ev == MG_EV_CONNECT) {
    struct mg_tls_opts opts = {.ca = mg_str(s_tls_ca)};
    mg_tls_init(c, &opts);

// server event handler:
  if (ev == MG_EV_ACCEPT) {
    struct mg_tls_opts opts = {.cert = mg_str(s_tls_cert),
                               .key = mg_str(s_tls_key)};
    mg_tls_init(c, &opts);
```

For more information on developing TLS clients and servers, see the [TLS
tutorial](https://mongoose.ws/documentation/tutorials/tls/)

## Timer

### mg\_timer\_add()

```c
struct mg_timer *mg_timer_add(struct mg_mgr *mgr,
                           uint64_t period_ms, unsigned flags,
                           void (*fn)(void *), void *fn_data);
```

Setup a timer. This is a high-level timer API that allows to add a software timer to the event manager. This function
`mg_calloc()` s a new timer and adds it to the `mgr->timers` list. All added timers are polled when `mg_mgr_poll()` is
called, and called if expired.

> NOTE: Make sure that the timer interval is equal or more to the `mg_mgr_poll()` timeout.

Parameters:

- `mgr` - Pointer to `mg_mgr` event manager structure
- `ms` - An interval in milliseconds
- `flags` - Timer flags bitmask, `MG_TIMER_REPEAT` and `MG_TIMER_RUN_NOW`
- `fn` - Function to invoke
- `fn_data` - Function argument to be passed on call

Return value: Pointer to created timer

Usage example:

```c
void timer_fn(void *data) {
  // ...
}

mg_timer_add(mgr, 1000, MG_TIMER_REPEAT, timer_fn, NULL);
```

### struct mg\_timer

```c
struct mg_timer {
  uint64_t period_ms;       // Timer period in milliseconds
  uint64_t expire;          // Expiration timestamp in milliseconds
  unsigned flags;           // Possible flags values below
#define MG_TIMER_ONCE 0     // Call function once
#define MG_TIMER_REPEAT 1   // Call function periodically
#define MG_TIMER_RUN_NOW 2  // Call immediately when timer is set
  void (*fn)(void *);       // Function to call
  void *arg;                // Function argument
  struct mg_timer *next;    // Linkage
};
```

Timer structure. Describes a software timer. Timer granularity is the same as the `mg_mgr_poll()` timeout argument in
the main event loop.

### mg\_timer\_init()

```c
void mg_timer_init(struct mg_timer **head,
                   struct mg_timer *t, uint64_t period_ms, unsigned flags,
                   void (*fn)(void *), void *fn_data);
```

Setup a timer.

Parameters:

- `head` - Pointer to `mg_timer` list head
- `t` - Pointer to `mg_timer` that should be initialized
- `ms` - An interval in milliseconds
- `flags` - Timer flags bitmask, `MG_TIMER_REPEAT` and `MG_TIMER_RUN_NOW`
- `fn` - Function to invoke
- `fn_data` - Function argument to be passed on call

Return value: None

Usage example:

```c
void timer_fn(void *data) {
  // ...
}

struct mg_timer timer, *head = NULL;
mg_timer_init(&head, &timer, 1000, MG_TIMER_REPEAT, timer_fn, NULL);
```

### mg\_timer\_free()

```c
void mg_timer_free(struct mg_timer **head, struct mg_timer *t);
```

Free timer, remove it from the internal timers list.

Parameters:

- `head` - Pointer to `mg_timer` list head
- `t` - Timer to free

Return value: None

Usage example:

```c
struct mg_timer timer;
// ...
mg_timer_free(&timer);
```

### mg\_timer\_poll()

```c
void mg_timer_poll(struct mg_timer **head, uint64_t uptime_ms);
```

Traverse list of timers and call them if current timestamp `uptime_ms` is past the timer's expiration time.

Note, that `mg_mgr_poll` function internally calls `mg_timer_poll`; therefore, in most cases it is unnecessary to call
it explicitly.

Parameters:

- `head` - Pointer to `mg_timer` list head
- `uptime_ms` - current timestamp

Return value: None

Usage example:

```c
mg_timer_poll(mg_millis());
```

## Time

### mg\_millis()

```c
uint64_t mg_millis(void);
```

Return current uptime in milliseconds.

Parameters: None

Return value: Current uptime

Usage example:

```c
uint64_t uptime = mg_millis();
```

### mg\_now()

```c
uint64_t mg_now(void);
```

Return current time in milliseconds, requires an SNTP server connection ([see mg\_sntp\_connect()](#mg_sntp_connect))

Parameters: None

Return value: If an SNTP server connection has been configured, returns current time. Otherwise, returns current uptime
just like `mg_millis()`

Usage example:

```c
mg_sntp_connect(mgr&, NULL /* connect to time.google.com */, NULL, NULL);
...
uint64_t curtime = mg_now();
```

### mg\_timer\_expired()

```c
bool mg_timer_expired(uint64_t *t, uint64_t period, uint64_t now);
```

Parameters:

- `t` - Pointer to a the timer value
- `period` - timer interval
- `now` - current time

Return true if a given timer `t` has expired: `now >= *t`, false otherwise. If the timer has expired, the `t` is
advanced by the `period`.

Usage example:

```c
uint64_t timer = 0, period = 500;  // Milliseconds
for (;;) {
  if (mg_timer_expired(&timer, period, mg_now())) {
    MG_INFO(("Hi!"));   // Print a message every 1/2 second
  }
  mg_mgr_poll(&mgr, 10);
}
```

## String

### struct mg\_str

```c
struct mg_str {
  const char *buf;  // Pointer to string data
  size_t len;       // String len
};
```

This structure represent an arbitrary chunk of memory, not necessarily zero-terminated. This is a "mongoose string",
and it gets used extensively in the codebase instead of C zero-terminated strings.

For example, when an HTTP request is received, Mongoose created a `struct mg_http_message` which has a collection of
`struct mg_str` pointing to request method, URI, headers, and so on. This way, Mongoose avoids any heap allocations and
does not modify the received buffer - instead, it uses `struct mg_str` to describe various parts of HTTP request.

Same goes with many other cases.

> NOTE: since `buf` is not necessarily zero-terminated, do not use libc string functions against it - like `strlen()`
or `sscanf()`.

### mg\_str()

```c
struct mg_str mg_str(const char *s)
```

Create Mongoose string from NULL-terminated C-string. This function doesn't duplicate provided string, and stores
pointer within created `mg_str` structure.

Note, that is you have problems in C++ (constructor shadowing), there is `mg_str_s` synonym for this function.

Parameters:

- `s` - Pointer to NULL-terminated string to store in created mg\_str

Return value: Created Mongoose string

Usage example:

```c
struct mg_str str = mg_str("Hello, world!);
```

### mg\_str\_n()

```c
struct mg_str mg_str_n(const char *s, size_t n);
```

Create Mongoose string from C-string `s` (can be non-NULL terminated, length is specified in `n`). Note: This function
doesn't duplicate provided string, but stores pointer within created `mg_str` structure.

Parameters:

- `s` - Pointer to string to store in created `mg_str`
- `n` - String length

Return value: Created Mongoose string

Usage example:

```c
struct mg_str str = mg_str_n("hi", 2);
```

### mg\_casecmp()

```c
int mg_casecmp(const char *s1, const char *s2);
```

Case insensitive compare two NULL-terminated strings.

Parameters:

- `s1`, `s2` - Pointers to strings to compare

Return value: Zero if strings are equal, more than zero if first argument is greater then second, and less than zero
otherwise

Usage example:

```c
if (mg_casecmp("hello", "HELLO") == 0) {
  // Strings are equal
}
```

### mg\_strcmp()

```c
int mg_strcmp(const struct mg_str str1, const struct mg_str str2);
```

Compare two mongoose strings.

Parameters:

- `str1`, `str2` - Pointers to Mongoose strings to compare

Return value: Zero if strings are equal, more than zero if first argument is greater than the second, and less than
zero otherwise

Usage example:

```c
struct mg_str str1 = mg_str("hello");
struct mg_str str2 = mg_str("hello");
if (mg_strcmp(str1, str2) == 0) {
  // Strings are equal
}
```

### mg\_strcasecmp()

```c
int mg_strcasecmp(const struct mg_str str1, const struct mg_str str2);
```

Compare two mongoose strings, ignoring the case of the characters.

Parameters:

- `str1`, `str2` - Pointers to Mongoose strings to compare

Return value: Zero if strings are equal, more than zero if first argument is greater than the second, and less than
zero otherwise

Usage example:

```c
struct mg_str str1 = mg_str("hello");
struct mg_str str2 = mg_str("HELLO");
if (mg_strcasecmp(str1, str2) == 0) {
  // Strings are equal
}
```

### mg\_strdup()

```c
struct mg_str mg_strdup(const struct mg_str s);
```

Duplicate provided string. Return new string or `MG_NULL_STR` on error. Note: This function allocates memory for the
returned string, you must free it using the `mg_free` function.

Parameters:

- `s` - Mongoose string to duplicate

Return value: Duplicated string

Usage example:

```c
struct mg_str str1 = mg_str("hello");
struct mg_str str2 = mg_strdup(str1);
//...
mg_free((void *)str2.buf);
```

### mg\_match()

```c
bool mg_match(struct mg_str str, struct mg_str pattern, struct mg_str *caps);
```

Check if string `str` matches glob pattern `pattern`, and optionally capture wildcards into the provided array `caps`.

> NOTE: If `caps` is not NULL, then the `caps` array size must be at least the number of wildcard symbols in `pattern`
plus 1. The last cap will be initialized to an empty string.

The glob pattern matching rules are as follows:

- `?` matches any single character
- `*` matches zero or more characters except `/`
- `#` matches zero or more characters
- any other character matches itself

Parameters:

- `str` - a string to match
- `pattern` - a pattern to match against
- `caps` - an optional array of captures for wildcard symbols `?`, `*`, '#'

Return value: `true` if matches, `false` otherwise

Usage example:

```c
// Assume that hm->uri holds /foo/bar. Then we can match the requested URI:
struct mg_str caps[3];  // Two wildcard symbols '*' plus 1
if (mg_match(hm->uri, mg_str("/*/*"), caps)) {
  // caps[0] holds \`foo\`, caps[1] holds \`bar\`.
}
```

### mg\_span()

```c
bool mg_span(struct mg_str s, struct mg_str *a, struct mg_str *b, char delim);
```

Span string `s` at the first occurence of character `delim`. Store the first part in `a`, and the rest of the string in
`b`. Both `a` and `b` can be NULL. If `delim` is not present in `s`, then `a` spans to the end of `s`.

Parameters:

- `s` - String being scanned
- `a` - Pointer to `mg_str` to store the prefix. Can be `NULL`
- `b` - Pointer to `mg_str` to store the rest. Can be `NULL`
- `delim` - A delimiter character

Return value: `true` if `s` is non-empty, `false` if it is empty

Usage example - scan comma-separated key=value pairs:

```c
struct mg_str entry, key, val;
struct mg_str s = mg_str("a=333,b=777,hello");

while (mg_span(s, &entry, &s, ',')) {
  mg_span(entry, &key, &val, '=');
  printf("key: %.*s, val: %.*s\n", (int) key.len, key.buf, (int) val.len, val.buf);
}

// This loop outputs the following:
// key: a, val: 333
// key: b, val: 777
// key: hello, val:
```
![Function mg_commalist()](https://mongoose.ws/documentation/images/mg_commalist.svg)

### mg\_str\_to\_num()

```c
bool mg_str_to_num(struct mg_str s, int base, void *val, size_t val_len);
```

Parse the string `s` for unsigned numbers in base `base`. The result is stored at the address pointed to by `val`. No
white space allowed.

Parameters:

- `s` - String to parse
- `base` - Number base: `2` for binary, `10` for decimal, `16` for hex; or `0` for auto, in which case binary numbers
must start with `0b` and hexadecimal numbers with `0x`. When the base is specified, *do not* prepend these.
- `val` - Where to store the number
- `val_len` - destination size; e.g.: `sizeof(uint8_t)` to `sizeof(uint64_t)`

Return value: Returns `true` if a number has been parsed successfully

Usage example:

```c
uint32_t val;
mg_str_to_num(mg_str_n("010203", 6), 16, &val, sizeof(val)); // returns true and val is now 0x10203
```

### mg\_path\_is\_sane()

```c
bool mg_path_is_sane(struct mg_str path);
```

Check `path` for starting with double dots in it.

Parameters:

- `path` - Mongoose string to check

Return value: true if OK, false otherwise

Usage example:

```c
char data[] = "../../a.txt";
bool res = mg_path_is_sane(mg_str(data));  // returns false
```

### mg\_snprintf(), mg\_vsnprintf()

```c
size_t mg_snprintf(char *buf, size_t len, const char *fmt, ...);
size_t mg_vsnprintf(char *buf, size_t len, const char *fmt, va_list ap);
```

Print formatted string into a string buffer, just like `snprintf()` standard function does, but in a predictable way
that does not depend on the C library or the build environment. The return value can be larger than the buffer length
`len`, in which case the overflow bytes are not printed. Mongoose library supports two non-standard specifiers: `%M`
and `%m`, for invoking custom print functions

Parameters:

- `buf` - Pointer to pointer to output buffer
- `len` - Buffer size
- `fmt` - format string in `printf` semantics.

Return value: Number of bytes printed

Supported format specifiers:

- `%c` - expect `char`
- `%f`, `%g` - expect `double`
- `%hhd`, `%hd`, `%d`, `%ld`, `%lld` - for `char`, `short`, `int`, `long`, `int64_t`
- `%hhu`, `%hu`, `%u`, `%lu`, `%llu` - same but for unsigned variants
- `%hhx`, `%hx`, `%x`, `%lx`, `%llx` - same, unsigned and hex output
- `%p` - expects any pointer, prints `0x.....` hex value
- `%s` - expects `char *`
- `%%` - prints the `%` character itself
- `%X.Y` - optional width and precision modifiers (e.g.: `%1.2d`)
- `%.*` - optional precision modifier, expected as `int` argument (e.g.: `%.*d`)
- `%M` - (EXTENSION) expects a pointer to a custom print function and its arguments
- `%m` - (EXTENSION) exactly like `%M` but double-quotes the output

List of built-in print functions for `%m` or `%M`:

- [mg\_print\_base64](#mg_print_base64) - prints a buffer as a base64-encoded string
- [mg\_print\_esc](#mg_print_esc) - prints a JSON-escaped string
- [mg\_print\_hex](#mg_print_hex) - prints a buffer as a hex string
- [mg\_print\_ip](#mg_print_ip) - prints an IP address in a `struct mg_str`
- [mg\_print\_ip\_port](#mg_print_ip_port) - prints IP address and port in a `struct mg_str`
- [mg\_print\_ip4](#mg_print_ip4) - prints an IPv4 address
- [mg\_print\_ip6](#mg_print_ip6) - prints an IPv6 address
- [mg\_print\_mac](#mg_print_mac) - prints a MAC address
- [mg\_print\_html\_esc](#mg_print_html_esc) - prints an HTML-escaped string

Usage example:

```c
mg_snprintf(buf, sizeof(buf), "%lld", (int64_t) 123);                  // 123                  (64-bit integer)
mg_snprintf(buf, sizeof(buf), "%.2s", "abcdef");                       // ab                   (part of a string)
mg_snprintf(buf, sizeof(buf), "%.*s", 2, "abcdef");                    // ab                   (part of a string)
mg_snprintf(buf, sizeof(buf), "%05x", 123);                            // 00123                (padded integer)
mg_snprintf(buf, sizeof(buf), "%%-%3s", "a");                          // %-  a                (padded string)
mg_snprintf(buf, sizeof(buf), "hi, %m", mg_print_base64, 1, "a");      // hi, "YWJj"           (base64-encode)
mg_snprintf(buf, sizeof(buf), "[%m]", mg_print_esc, 0, "two\nlines");  // ["two\nlines"]       (JSON-escaped string)
mg_snprintf(buf, sizeof(buf), "{%m:%g}", mg_print_esc, 0, "val", 1.2); // {"val": 1.2}         (JSON object)
mg_snprintf(buf, sizeof(buf), "hi, %M", mg_print_hex, 3, "abc");       // hi, 616263           (hex-encode)
mg_snprintf(buf, sizeof(buf), "IP: %M", mg_print_ip, &c->rem);         // IP: 1.2.3.4          (struct mg_addr)
mg_snprintf(buf, sizeof(buf), "Peer: %M", mg_print_ip_port, &c->rem);  // Peer: 1.2.3.4:21345  (struct mg_addr with
port)
mg_snprintf(buf, sizeof(buf), "%M", mg_print_ip4, "abcd");             // 97.98.99.100         (IPv4 address)
mg_snprintf(buf, sizeof(buf), "%M", mg_print_ip6, "abcdefghijklmnop"); // [4142:4344:4546:4748:494a:4b4c:4d4e:4f50]
mg_snprintf(buf, sizeof(buf), "%M", mg_print_mac, "abcdef");           // 61:62:63:64:65:66    (MAC address)
```

It is easy to implement a custom print function. For example, to format a structure as JSON string:

```c
struct a { int a, b; };

size_t print_a(void (*out)(char, void *), void *ptr, va_list *ap) {
  struct a *p = va_arg(*ap, struct a *);
  return mg_xprintf(out, ptr, "{%m:%d}", MG_ESC("a"), p->a); // MG_ESC invokes mg_print_esc
}

struct a temp = { 42, 43 };
mg_snprintf(buf, sizeof(buf), "%M", print_a, &temp);    // {"a":42}
```

### mg\_mprintf(), mg\_vmprintf()

```c
char *mg_mprintf(const char *fmt, ...);
char *mg_vmprintf(const char *fmt, va_list *ap);
```

Print message into an allocated memory buffer. Caller must `mg_free()` the result.

Parameters:

- `fmt` - format string in `printf` semantics. See [mg\_snprintf](#mg_snprintf-mg_vsnprintf) for the list of supported
format specifiers

Return value: allocated memory buffer

Usage example:

```c
char *msg = mg_mprintf("Build the message: %s", "hi!");
mg_free(msg);
```

### mg\_xprintf(), mg\_vxprintf()

```c
size_t mg_xprintf(void (*out)(char, void *), void *param, const char *fmt, ...);
size_t mg_vxprintf(void (*out)(char, void *), void *param, const char *fmt,
                   va_list *ap);
```

Print message using a specified character output function

Parameters:

- `out` - function to be used for printing chars
- `param` - argument to be passed to `out`
- `fmt` - format string in `printf` semantics. See [mg\_snprintf](#mg_snprintf-mg_vsnprintf) for the list of supported
format specifiers

Return value: Number of bytes printed

Usage example:

```c
void myfn(char c, void *p);

size_t len = mg_xprintf(myfn, myfn_p, "Print the string: %s!", "hi");
```

### mg\_pfn\_iobuf()

```c
void mg_pfn_iobuf(char ch, void *param);
```

Print a character to a [Generic IO buffer](#struct-mg_iobuf)

Parameters:

- `ch` - char to be printed
- `param` - must be `struct mg_iobuf *`

Usage example:

```c
mg_xprintf(mg_pfn_iobuf, &c->send, "hi!");  // Append to the output buffer
```

### mg\_aton()

```c
bool mg_aton(struct mg_str str, struct mg_addr *addr);
```

Parse IP address held by `str` and store it in `addr`.

Parameters:

- `str` - String to parse, for example `1.2.3.4`, `[::1]`, `01:02::03`
- `addr` - Pointer to `mg_addr` string to receive parsed value

Return value: `true` on success, `false` otherwise

Usage example:

```c
struct mg_addr addr;
if (mg_aton(mg_str("127.0.0.1"), &addr)) {
  // addr is now binary representation of 127.0.0.1 IP address
}
```

## JSON

Mongoose library is often used to exchange data in JSON format, therefore we have provided utility functions to format
JSON strings easily:

```c
mg_http_reply(c, 200, "Content-Type: application/json\r\n",
              "{%m: %u}", MG_ESC("value"), 123);  // {"value": 123}
```

Therefore, for full JSON support, a set of parsing functions is required - which is described below.

### mg\_json\_get()

```c
enum { MG_JSON_TOO_DEEP = -1, MG_JSON_INVALID = -2, MG_JSON_NOT_FOUND = -3 };
int mg_json_get(struct mg_str json, const char *path, int *toklen);
```

Parse JSON string `json` and return the offset of the element specified by the JSON `path`. The length of the element
is stored in the `toklen`.

Parameters:

- `json` - a string containing valid JSON
- `path` - a JSON path. Must start with `$`, e.g. `$.user`
- `toklen` - a pointer that receives element's length, can be NULL

Return value: offset of the element, or negative `MG_JSON_*` on error.

Usage example:

```c
// Create a json string: { "a": 1, "b": [2, 3] }
char *buf = mg_mprintf("{ %m: %d, %m: [%d, %d] }",
                       MG_ESC("a"), 1,
                       MG_ESC("b"), 2, 3);
struct mg_str json = mg_str(buf);
int offset, length;

// Lookup "$", which is the whole JSON. Can be used for validation
offset = mg_json_get(json, "$", &length);    // offset = 0, length = 23

// Lookup attribute "a". Point to value "1"
offset = mg_json_get(json, "$.a", &length);  // offset = 7, length = 1

// Lookup attribute "b". Point to array [2, 3]
offset = mg_json_get(json, "$.b", &length);  // offset = 15, length = 6

// Lookup attribute "b[1]". Point to value "3"
offset = mg_json_get(json, "$.b[1]", &length); // offset = 19, length = 1

mg_free(buf);
```

### mg\_json\_get\_tok()

```c
struct mg_str mg_json_get_tok(struct mg_str json, const char *path);
```

Parse JSON string `json` and return a `struct mg_str` pointing to the value of the element specified by the JSON
`path`. Useful to check if a token is present, or inspect when it can have different types.

Parameters:

- `json` - a string containing valid JSON
- `path` - a JSON path. Must start with `$`, e.g. `$.user`

Return value: a `struct mg_str` pointing to the value of the element, or with a NULL pointer on error.

Usage example:

```c
json = mg_str("{\"a\":\"b:c\"}");
val = mg_json_get_tok(json, "$.a"); // "b:c"
```

### mg\_json\_get\_num()

```c
bool mg_json_get_num(struct mg_str json, const char *path, double *v);
```

Fetch numeric (double) value from the json string `json` at JSON path `path` into a placeholder `v`. Return true if
successful.

Parameters:

- `json` - a string containing valid JSON
- `path` - a JSON path. Must start with `$`
- `v` - a placeholder for value

Return value: true on success, false on error

Usage example:

```c
double d = 0.0;
mg_json_get_num(mg_str("[1,2,3]", "$[1]", &d));     // d == 2
mg_json_get_num(mg_str("{\"a\":1.23}", "$.a", &d)); // d == 1.23
```

### mg\_json\_get\_bool()

```c
bool mg_json_get_bool(struct mg_str json, const char *path, bool *v);
```

Fetch boolean (bool) value from the json string `json` at JSON path `path` into a placeholder `v`. Return true if
successful.

Parameters:

- `json` - a string containing valid JSON
- `path` - a JSON path. Must start with `$`
- `v` - a placeholder for value

Return value: true on success, false on error

Usage example:

```c
bool b = false;
mg_json_get_bool(mg_str("[123]", "$[0]", &b));   // Error. b remains to be false
mg_json_get_bool(mg_str("[true]", "$[0]", &b));  // b is true
```

### mg\_json\_get\_long()

```c
long mg_json_get_long(struct mg_str json, const char *path, long default_val);
```

Fetch integer numeric (long) value from the json string `json` at JSON path `path`. Return it if found, or
`default_val` if not found.

Parameters:

- `json` - a string containing valid JSON
- `path` - a JSON path. Must start with `$`
- `default_val` - a default value for the failure case

Return value: found value, or `default_val` value

Usage example:

```c
long a = mg_json_get_long(mg_str("[123]", "$a", -1));   // a = -1
long b = mg_json_get_long(mg_str("[123]", "$[0]", -1)); // b = 123
```

### mg\_json\_get\_str()

```c
char *mg_json_get_str(struct mg_str json, const char *path);
```

Fetch string value from the json string `json` at JSON path `path`. If found, a string is allocated using
`mg_calloc()`, un-escaped, and returned to the caller. It is the caller's responsibility to `mg_free()` the returned
string.

Parameters:

- `json` - a string containing valid JSON
- `path` - a JSON path. Must start with `$`

Return value: non-NULL on success, NULL on error

Usage example:

```c
struct mg_str json = mg_str("{\"a\": \"hi\"}");  // json = {"a": "hi"}
char *str = mg_json_get_str(json, "$.a");        // str = "hi"
mg_free(str);
```

### mg\_json\_get\_hex()

```c
char *mg_json_get_hex(struct mg_str json, const char *path, int *len);
```

Fetch hex-encoded buffer from the json string `json` at JSON path `path`. If found, a buffer is allocated using
`mg_calloc()`, decoded, and returned to the caller. It is the caller's responsibility to `mg_free()` the returned
string. Returned buffer is nul-terminated.

Parameters:

- `json` - a string containing valid JSON
- `path` - a JSON path. Must start with `$`
- `len` - a pointer that receives decoded length. Can be NULL

Return value: non-NULL on success, NULL on error

Usage example:

```c
struct mg_str json = mg_str("{\"a\": \"6869\"}"); // json = {"a": "6869"}
char *str = mg_json_get_hex(json, "$.a", NULL);   // str = "hi"
mg_free(str);
```

### mg\_json\_get\_b64()

```c
char *mg_json_get_b4(struct mg_str json, const char *path, int *len);
```

Fetch base64-encoded buffer from the json string `json` at JSON path `path`. If found, a buffer is allocated using
`mg_calloc()`, decoded, and returned to the caller. It is the caller's responsibility to `mg_free()` the returned
string. Returned buffer is nul-terminated.

Parameters:

- `json` - a string containing valid JSON
- `path` - a JSON path. Must start with `$`
- `len` - a pointer that receives decoded length. Can be NULL

Return value: non-NULL on success, NULL on error

Usage example:

```c
struct mg_str json = mg_str("{\"a\": \"YWJj\"}"); // json = {"a": "YWJj"}
char *str = mg_json_get_b64(json, "$.a", NULL);   // str = "abc"
mg_free(str);
```

### mg\_json\_unescape()

```c
bool mg_json_unescape(struct mg_str str, char *buf, size_t len);
```

Unescape a JSON string

Parameters:

- `str` - a string containing valid JSON to be unescaped
- `buf` - buffer where to place the result
- `len` - buffer length

Return value: true on success, false on error

Usage example:

```c
struct mg_str str = mg_str("{\"a\": \"b\\u0063d\"}"); // escaped json = {"a": "b\u0063d"}
char json[20];
bool result = mg_json_unescape(str, result, 20);    // json = {"a": "bcd"}
```

### mg\_json\_next()

```c
size_t mg_json_next(struct mg_str obj, size_t ofs, struct mg_str *key, struct mg_str *val);
```

Iterate over elements of an object or array. An initial value for `ofs` must be 0, then on each iteration a previously
returned value should be passed.

Parameters:

- `json` - a string containing valid JSON
- `ofs` - an offset of the element
- `key` - a pointer that receives key. For arrays, set to empty. Can be NULL
- `val` - a pointer that receives value. Can be NULL

Return value: non-0 on success, 0 when there are no more elements

Usage example:

```c
struct mg_str key, val, obj = mg_str("{\"a\": [true], \"b\": 12345}");
size_t ofs = 0;
while ((ofs = mg_json_next(obj, ofs, &key, &val)) > 0) {
  printf("%.*s -> %.*s\n", (int) key.len, key.buf, (int) val.len, val.buf);
}
```

For an example on how to iterate over an arbitrary JSON string, see
[json\_scan()](https://github.com/cesanta/mongoose/blob/d18b2b390a7b6801349f1f62aa6d24ab67514fa6/test/unit_test.c#L2790-
L2804) function in the unit test.

## JSON Web Tokens (JWT)

Mongoose can sign and verify compact JSON Web Tokens (JWTs). HS256 is available in every build. ES256 is available when
`MG_TLS == MG_TLS_BUILTIN`.

Full example: [JWT Bearer authentication](https://github.com/cesanta/mongoose/tree/master/tutorials/http/jwt-auth)

### struct mg\_jwt\_opts

```c
struct mg_jwt_opts {
  struct mg_str claims;  // JSON payload
  struct mg_str header;  // Extra header members, no braces; alg/typ are set
  struct mg_str kid;     // Key ID protected header
  struct mg_str secret;  // HS256 secret
  const uint8_t *private_key;  // ES256 private key (MG_TLS_BUILTIN only)
  const uint8_t *public_key;   // ES256 public key (MG_TLS_BUILTIN only)
};
```

JWT options structure:

- `claims` - JSON claims to sign
- `header` - additional protected-header members, without surrounding braces
- `kid` - optional protected-header key ID
- `secret` - shared secret for HS256
- `private_key` - 32-byte ES256 private key for signing
- `public_key` - 64-byte ES256 public key for verification

Mongoose always writes the `alg` and `typ` protected-header members. `kid` and `header` are used when signing only;
verification selects its algorithm explicitly and does not select a key from `kid`.

### mg\_jwt\_sign\_hs256()

```c
size_t mg_jwt_sign_hs256(const struct mg_jwt_opts *opts, char *buf,
                         size_t len);
```

Sign JSON claims as a compact JWT using HMAC-SHA256.

Parameters:

- `opts` - JWT options. Set `claims` and `secret`
- `buf` - buffer to receive the JWT
- `len` - size of `buf`

Return value: JWT length, or 0 on error. The output is not NUL-terminated.

Usage example:

```c
char jwt[256];
struct mg_jwt_opts opts = {
    .claims = mg_str("{\"sub\":\"admin\"}"),
    .secret = mg_str("replace-with-a-secret"),
};
size_t n = mg_jwt_sign_hs256(&opts, jwt, sizeof(jwt));
if (n > 0 && n < sizeof(jwt)) jwt[n] = '\0';
```

### mg\_jwt\_verify\_hs256()

```c
size_t mg_jwt_verify_hs256(struct mg_str jwt, const struct mg_jwt_opts *opts,
                           char *buf, size_t len);
```

Verify a compact HS256 JWT and decode its JSON claims.

Parameters:

- `jwt` - compact JWT to verify
- `opts` - JWT options. Set `secret`
- `buf` - buffer to receive decoded claims
- `len` - size of `buf`

Return value: claims length, or 0 if the JWT is malformed, has a different algorithm, has an invalid signature, or does
not fit in `buf`. The claims are not NUL-terminated.

Usage example:

```c
char claims[256];
struct mg_jwt_opts opts = {.secret = mg_str("replace-with-a-secret")};
size_t n = mg_jwt_verify_hs256(mg_str(jwt), &opts, claims, sizeof(claims));
if (n > 0 && mg_json_get_long(mg_str_n(claims, n), "$.admin", 0) == 1) {
  // Valid administrator token
}
```

Notes: The function verifies the JWT format, algorithm, and signature. Validate expiry, issuer, audience, and
application authorization claims separately.

### mg\_jwt\_sign\_es256()

```c
size_t mg_jwt_sign_es256(const struct mg_jwt_opts *opts, char *buf,
                         size_t len);
```

Sign JSON claims as a compact JWT using ECDSA P-256 and SHA-256.

Parameters:

- `opts` - JWT options. Set `claims` and `private_key`
- `buf` - buffer to receive the JWT
- `len` - size of `buf`

Return value: JWT length, or 0 on error. The output is not NUL-terminated.

Usage example:

```c
extern uint8_t private_key[32];  // Application-provisioned P-256 private key
char jwt[256];
struct mg_jwt_opts opts = {
    .claims = mg_str("{\"sub\":\"admin\"}"),
    .private_key = private_key,
};
size_t n = mg_jwt_sign_es256(&opts, jwt, sizeof(jwt));
if (n > 0 && n < sizeof(jwt)) jwt[n] = '\0';
```

Notes: Available only when `MG_TLS == MG_TLS_BUILTIN`.

### mg\_jwt\_verify\_es256()

```c
size_t mg_jwt_verify_es256(struct mg_str jwt, const struct mg_jwt_opts *opts,
                           char *buf, size_t len);
```

Verify a compact ES256 JWT and decode its JSON claims.

Parameters:

- `jwt` - compact JWT to verify
- `opts` - JWT options. Set `public_key`
- `buf` - buffer to receive decoded claims
- `len` - size of `buf`

Return value: claims length, or 0 if the JWT is malformed, has a different algorithm, has an invalid signature, or does
not fit in `buf`. The claims are not NUL-terminated.

Usage example:

```c
extern uint8_t public_key[64];  // Application-provisioned P-256 public key
char claims[256];
struct mg_jwt_opts opts = {.public_key = public_key};
size_t n = mg_jwt_verify_es256(mg_str(jwt), &opts, claims, sizeof(claims));
if (n > 0 && mg_json_get_long(mg_str_n(claims, n), "$.admin", 0) == 1) {
  // Valid administrator token
}
```

Notes: Available only when `MG_TLS == MG_TLS_BUILTIN`. Validate expiry, issuer, audience, and application authorization
claims separately.

### JWT Bearer authorization

Use a compact JWT in an HTTP `Authorization: Bearer` header to protect an HTTP endpoint. Check the header scheme before
calling `mg_http_creds()`: that function also accepts Basic credentials, an `access_token` cookie, and an
`access_token` query parameter.

For a complete runnable example, see [JWT Bearer
authentication](https://github.com/cesanta/mongoose/tree/master/tutorials/http/jwt-auth).

```c
static bool authorized(struct mg_http_message *hm) {
  struct mg_str *auth = mg_http_get_header(hm, "Authorization");
  char user[1], token[512], claims[256];
  struct mg_jwt_opts opts = {.secret = mg_str("replace-with-a-secret")};
  size_t n;

  if (auth == NULL || !mg_match(*auth, mg_str("Bearer *"), NULL)) return false;
  mg_http_creds(hm, user, sizeof(user), token, sizeof(token));
  n = mg_jwt_verify_hs256(mg_str(token), &opts, claims, sizeof(claims));
  if (n == 0 || n >= sizeof(claims)) return false;
  return mg_json_get_long(mg_str_n(claims, n), "$.admin", 0) == 1;
}

static void fn(struct mg_connection *c, int ev, void *ev_data) {
  if (ev == MG_EV_HTTP_MSG) {
    struct mg_http_message *hm = (struct mg_http_message *) ev_data;
    if (!authorized(hm)) {
      mg_http_reply(c, 401, "WWW-Authenticate: Bearer\r\n", "Unauthorized\n");
    } else {
      mg_http_reply(c, 200, "", "OK\n");
    }
  }
}
```

After signature verification, validate every claim that your authorization policy requires. In particular, enforce
expiry and issuer/audience constraints when present, and use a trusted clock when evaluating time-based claims.

## RPC

Mongoose includes a set of functions to ease server-side processing by means of RPC methods.

### struct mg\_rpc

The RPC method handler structure. Each method has an entry in a linked list, each entry points to a string describing
the pattern that will invoke it and the function that will be called to satisfy the method invocation, with a proper
function argument.

```c
struct mg_rpc {
  struct mg_rpc *next;              // Next in list
  struct mg_str method;             // Method pattern
  void (*fn)(struct mg_rpc_req *);  // Handler function
  void *fn_data;                    // Handler function argument
};
```

### struct mg\_rpc\_req

The RPC request descriptor. An invoked method receives a descriptor containing the request, and a pointer to a function
to be called to print the output response, with a proper function argument; e.g.: [mg\_pfn\_realloc()](#mg_pfn_realloc)
or [mg\_pfn\_iobuf()](#mg_pfn_iobuf)

```c
struct mg_rpc_req {
  struct mg_rpc **head;  // RPC handlers list head
  struct mg_rpc *rpc;    // RPC handler being called
  mg_pfn_t pfn;          // Response printing function
  void *pfn_data;        // Response printing function data
  void *req_data;        // Arbitrary request data
  struct mg_str frame;   // Request, e.g. {"id":1,"method":"add","params":[1,2]}
};
```

### mg\_rpc\_add()

```c
void mg_rpc_add(struct mg_rpc **head, struct mg_str method_pattern,
                void (*handler)(struct mg_rpc_req *), void *handler_data);
```

Add the method `method_pattern` to the list `head` of RPC methods. Invoking this method will call `handler` and pass
`handler_data` to it with the request (as `r->fn_data` in the usage example below).

Parameters:

- `head` - the linked list pointer
- `method_pattern` - the name of the method
- `handler` - the RPC function performing the action for this method
- `handler_data` - Arbitrary function data

> NOTE: if `method_pattern` is an empty string, this handler will be called to process JSON-RPC responses. Handling
responses might be necessary if the JSON requests are initiated by both sides.

Usage example:

```c
struct mg_rpc *s_rpc_head = NULL;

static void rpc_sum(struct mg_rpc_req *r) {
  double a = 0.0, b = 0.0;
  mg_json_get_num(r->frame, "$.params[0]", &a);
  mg_json_get_num(r->frame, "$.params[1]", &b);
  mg_rpc_ok(r, "%g", a + b);
}

static void rpc_mul(struct mg_rpc_req *r) {//...}

  mg_rpc_add(&s_rpc_head, mg_str("sum"), rpc_sum, NULL);
  mg_rpc_add(&s_rpc_head, mg_str("mul"), rpc_mul, NULL);
```

### mg\_rpc\_del()

```c
void mg_rpc_del(struct mg_rpc **head, void (*handler)(struct mg_rpc_req *));
```

Remove the method with RPC function handler `handler` from the list `head` of RPC methods.

Parameters:

- `head` - the linked list pointer
- `handler` - the RPC function performing the action for this method, use NULL to deallocate all

Usage example:

```c
struct mg_rpc *s_rpc_head = NULL;
// add methods
// ...

// Time to cleanup
mg_rpc_del(&s_rpc_head, rpc_mul);    // Deallocate specific handler
mg_rpc_del(&s_rpc_head, NULL);       // Deallocate all RPC handlers
```

### mg\_rpc\_process()

```c
void mg_rpc_process(struct mg_rpc_req *req);
```

Invoke the proper method for this request. If the requested method does not exist, `mg_rpc_err()` will be invoked and
an error indication will be printed

Parameters:

- `req` - a request

Usage example:

```c
struct mg_rpc *s_rpcs = NULL;                               // Empty RPC list head
mg_rpc_add(&s_rpcs, mg_str("rpc.list"), mg_rpc_list, NULL); // Add rpc.list
// ... add more RPC methods

// On request, process the incoming frame
struct mg_str req = mg_str("{\"id\":1,\"method\":\"sum\",\"params\":[1,2]}");
struct mg_iobuf io = {0, 0, 0, 512};  // Empty IO buf, with 512 realloc granularity
struct mg_rpc_req r = {
  .head = &s_rpcs,        // RPC list head
  .rpc = NULL,            // This will be set by mg_rpc_process()
  .pfn = mg_pfn_iobuf,    // Printing function: print into the io buffer
  .pfn_data = &io,        // Pass our io buffer as a parameter
  .req_data = NULL,       // No specific request data
  .frame = req,           // Specify incoming frame
};

mg_rpc_process(&r);
if (io.buf != NULL) printf("Response: %s\n", (char *) io.buf);
mg_iobuf_free(&io);
```

### mg\_rpc\_ok(), mg\_rpc\_vok()

```c
void mg_rpc_ok(struct mg_rpc_req *, const char *fmt, ...);
void mg_rpc_vok(struct mg_rpc_req *, const char *fmt, va_list *ap);
```

Helper functions to print result frames

Parameters:

- `req` - a request
- `fmt` - format string in `printf` semantics. See [mg\_snprintf](#mg_snprintf-mg_vsnprintf) for the list of supported
format specifiers

Usage example:

```c
static void rpc_sum(struct mg_rpc_req *r) {
  double a = 0.0, b = 0.0;
  mg_json_get_num(r->frame, "$.params[0]", &a);
  mg_json_get_num(r->frame, "$.params[1]", &b);
  mg_rpc_ok(r, "%g", a + b);
}
```

### mg\_rpc\_err(), mg\_rpc\_verr()

```c
void mg_rpc_err(struct mg_rpc_req *, int code, const char *fmt, ...);
void mg_rpc_verr(struct mg_rpc_req *, int code, const char *fmt, va_list *);
```

Helper functions to print error frames

Parameters:

- `req` - a request
- `fmt` - format string in `printf` semantics. See [mg\_snprintf](#mg_snprintf-mg_vsnprintf) for the list of supported
format specifiers

Usage example:

```c
static void rpc_dosome(struct mg_rpc_req *r) {
  ...
  mg_rpc_err(r, -32109, "\"%.*s not found\"", len, &r->frame.buf[offset]);
}
```

### mg\_rpc\_list()

```c
void mg_rpc_list(struct mg_rpc_req *r);
```

Built-in RPC method to list all registered RPC methods. This function is not usually called directly, but registered as
a method.

Parameters:

- `req` - a request

Usage example:

```c
mg_rpc_add(&s_rpc_head, mg_str("rpc.list"), mg_rpc_list, &s_rpc_head);
```

(see also [mg\_rpc\_add()](#mg_rpc_add))

## Utility

### mg\_call()

```c
void mg_call(struct mg_connection *c, int ev, void *ev_data);
```

Send `ev` event to `c` event handler. This function is useful then implementing your own protocol.

Parameters:

- `c` - Connection to send event
- `ev` - Event to send
- `ev_data` - Additional event parameter

Return value: None

Usage example:

```c
// In a timer callback, send MG_EV_USER event to all connections
static void timer_fn(void *arg) {
  struct mg_mgr *mgr = (struct mg_mgr *) arg;
  for (struct mg_connection *c = mgr->conns; c != NULL; c = c->next) {
    mg_call(c, MG_EV_USER, "hi!");
  }
}
```

### mg\_error()

```c
void mg_error(struct mg_connection *c, const char *fmt, ...);
```

Send `MG_EV_ERROR` to connection event handler with error message formatted using printf semantics.

Parameters:

- `c` - Connection to send event
- `fmt` - Format string in `printf` semantics

Return value: None

Usage example:

```c
mg_error(c, "Operation failed, error code: %d", errno);
```

### mg\_md5\_init()

```c
void mg_md5_init(mg_md5_ctx *c);
```

Initialize context for MD5 hashing.

Parameters:

- `c` - Pointer to `mg_md5_ctx` structure to initialize

Return value: None

Usage example:

```c
mg_md5_ctx ctx;
mg_md5_init(&ctx);
```

### mg\_md5\_update()

```c
void mg_md5_update(mg_md5_ctx *c, const unsigned char *data, size_t len);
```

Hash `len` bytes of data pointed by `data` using MD5 algorithm.

Parameters:

- `c` - MD5 context
- `data` - Data to hash
- `len` - Data length

Return value: None

Usage example:

```c
mg_md5_ctx ctx;
// Context initialization
// ...

mg_md5_update(&ctx, "data", 4);       // hash "data" string
mg_md5_update(&ctx, "more data", 9);  // hash "more data" string
```

### mg\_md5\_final()

```c
void mg_md5_final(mg_md5_ctx *c, unsigned char buf[16]);
```

Get current MD5 hash for context.

Parameters:

- `c` - MD5 context
- `buf` - Pointer to buffer to write MD5 hash value

Return value: None

Usage example:

```c
mg_md5_ctx ctx;
// Context initialization
// ...

unsigned char buf[16];
mg_md5_final(&ctx, buf);  // \`buf\` is now MD5 hash
```

### mg\_sha1\_init()

```c
void mg_sha1_init(mg_sha1_ctx *c);
```

Initialize context for calculating SHA1 hash

Parameters:

- `c` - pointer to `mg_sha1_ctx` structure to initialize

Return value: none

Usage example:

```c
mg_sha1_ctx ctx;
mg_sha1_init(&ctx);
```

### mg\_sha1\_update()

```c
void mg_sha1_update(mg_sha1_ctx *c, const unsigned char *data, size_t len);
```

Hash `len` bytes of `data` using SHA1 algorithm.

Parameters:

- `c` - SHA1 context
- `data` - Data to hash
- `len` - Data length

Return value: None

Usage example:

```c
mg_sha1_ctx ctx;
// Context initialization
// ...

mg_sha1_update(&ctx, "data", 4);      // hash "data" string
mg_sha1_update(&ctx, "more data", 9); // hash "more data" string
```

### mg\_sha1\_final()

```c
void mg_sha1_final(unsigned char digest[20], mg_sha1_ctx *c);
```

Get current SHA1 hash for context.

Parameters:

- `c` - SHA1 context
- `digest` - Pointer to buffer to receive hash value

Return value: None

Usage example:

```c
mg_sha1_ctx ctx;
// Context initialization
// ...

unsigned char buf[20];
mg_sha1_final(buf, &ctx); // \`buf\` is now SHA1 hash
```

### mg\_base64\_update()

```c
size_t mg_base64_update(unsigned char p, char *buf, size_t len);
```

Encode `p` byte to base64 and write result into `buf` buffer

Parameters:

- `p` - Byte to encode
- `buf` - Pointer to buffer to write result
- `len` - Buffer length

Return value: Number of chars written into buffer

Usage example:

```c
char buf[10];
mg_base64_update((unsigned char)"a", buf, 10); // Encode "a" into base64 and write it to buf
```

### mg\_base64\_final()

```c
size_t mg_base64_final(char *buf, size_t len);
```

Add base64 finish mark and `\0` symbol to `buf`

Parameters:

- `buf` - Pointer to buffer to write finish mark
- `len` - Buffer length

Return value: Number of chars written into buffer

```c
char buf[10];
// ...

mg_base64_final(buf, 10);
```

### mg\_base64\_encode()

```c
size_t mg_base64_encode(const unsigned char *p, size_t n, char *buf, size_t len);
```

Encode `n` bytes data pointed to by `p` using base64 and write result into `buf`.

Parameters:

- `p` - Pointer to data to encode
- `n` - Data length
- `buf` - Pointer to buffer to write result
- `len` - Buffer length

Return value: Number of chars written into buffer

Usage example:

```c
char buf[128];
mg_base64_encode((uint8_t *) "abcde", 5, buf, 128); // buf is now YWJjZGU=
```

### mg\_base64\_decode()

```c
size_t mg_base64_decode(const char *src, size_t n, char *dst, size_t len);
```

Decode `n` bytes of base64-ed `src` and write it to `dst`.

Parameters:

- `src` - Data to decode
- `n` - Data length
- `dst` - Pointer to output buffer
- `len` - Buffer length

Return value: Number of chars written into buffer

Usage example:

```c
char buf[128];
mg_base64_decode("Q2VzYW50YQ==", 12, buf, 128); // buf is now "Cesanta"
```

### mg\_random()

```c
bool mg_random(void *buf, size_t len);
```

Fill in buffer `buf`, `len` with random data. Note: Mongoose uses this function for TLS and some other routines that
require RNG (random number generator). It is possible to override a built-in `mg_random()` by specifying a
`MG_ENABLE_CUSTOM_RANDOM=1` build preprocessor constant.

Parameters:

- `buf` - Pointer to buffer to receive random data
- `len` - Buffer size

Return value: This function returns `false` when the system `rand()` has to be used, because a stronger PRNG for the
configured MG\_ARCH could not be found.

Usage example:

```c
char buf[10];
mg_random(buf, sizeof(buf)); // \`buf\` is now random bytes
```

### mg\_random\_str()

```c
char *mg_random_str(char *buf, size_t len);
```

Fill in buffer `buf`, `len` with random alphanumeric characters: `a-zA-Z0-9`. A buffer is zero-terminated.

Parameters:

- `buf` - a pointer to a buffer
- `len` - a buffer size

Return value: `buf` value.

Usage example:

```c
char buf[10];
printf("Random: %s\n", mg_random_str(buf, sizeof(buf)));
```

### mg\_ntohs()

```c
uint16_t mg_ntohs(uint16_t net);
```

Convert `uint16_t` value to host order.

Parameters:

- `net` - 16-bit value in network order

Return value: 16-bit value in host order

Usage example:

```c
uint16_t val = mg_ntohs(0x1234);
```

### mg\_ntohl()

```c
uint32_t mg_ntohl(uint32_t net);
```

Convert `uint32_t` value to host order.

Parameters:

- `net` - 32-bit value in network order

Return value: 32-bit value in host order

Usage example:

```c
uint32_t val = mg_ntohl(0x12345678);
```

### mg\_htons()

```c
uint16_t mg_htons(uint16_t h);
```

Convert `uint16_t` value to network order.

Parameters:

- `h` - 16-bit value in host order

Return value: 16-bit value in network order

Usage example:

```c
uint16_t val = mg_htons(0x1234);
```

### mg\_htonl()

```c
uint32_t mg_ntohl(uint32_t h);
```

Convert `uint32_t` value to network order.

Parameters:

- `h` - 32-bit value in host order

Return value: 32-bit value in network order

Usage example:

```c
uint32_t val = mg_htonl(0x12345678);
```

### mg\_crc32()

```c
uint32_t mg_crc32(uint32_t crc, const char *buf, size_t len);
```

Calculate CRC-32/ISO-HDLC (Ethernet CRC-32) checksum for a given buffer. An initial `crc` value should be `0`.

Parameters:

- `crc` - Initial CRC value
- `buf` - Data to calculate CRC32
- `len` - Data size

Return value: Calculated CRC32 checksum

Usage example:

```c
char data[] = "hello";
uint32_t crc = mg_crc32(0, data, sizeof(data));
```

### mg\_crc16()

```c
uint16_t mg_crc16(uint16_t crc, const char *buf, size_t len);
```

Calculate CRC-16/IBM-SDLC (CRC-16/X-25, CRC-16/ISO-HDLC) checksum for a given buffer. An initial `crc` value should be
`0`.

Parameters:

- `crc` - Initial CRC value
- `buf` - Data to calculate CRC16
- `len` - Data size

Return value: Calculated CRC16 checksum

Usage example:

```c
char data[] = "hello";
uint16_t crc = mg_crc16(0, data, sizeof(data));
```

### mg\_check\_ip\_acl()

```c
int mg_check_ip_acl(struct mg_str acl, struct mg_addr *remote_ip);
```

Check IP address `remote_ip` against the IP ACL `acl`.

> Currently, only the IPv4 address format is supported for the ACL string.

Parameters:

- `acl` - an ACL string, e.g. `-0.0.0.0/0,+1.2.3.4`
- `remote_ip` - an IP address

Return value: 1 if `remote_ip` is allowed, 0 if not, and <0 if `acl` is invalid

Usage example:

```c
if (mg_check_ip_acl(mg_str("-0.0.0.0/0,+1.2.3.4"), c->rem) != 1) {
  LOG(LL_INFO, ("NOT ALLOWED!"));
}
```

### mg\_url\_decode()

```c
int mg_url_decode(const char *src, size_t src_len, char *dst, size_t dst_len, int form);
```

Decode URL-encoded string `s` and write it into `to` buffer.

Parameters:

- `src` - String to decode
- `src_len` - Length of the string to decode
- `dst` - Pointer to output buffer
- `dst_len` - Output buffer size
- `form` - If non-zero, then `+` is decoded as whitespace.

Return value: Decoded bytes count or negative value on error

Usage example:

```c
char url[] = "eexample.org%2Ftest";
char buf[1024];
mg_url_encode(url, sizeof(url) - 1, buf, sizeof(buf), 0); // buf is now "example.org/test"
```

### mg\_url\_encode

```c
size_t mg_url_encode(const char *s, size_t n, char *buf, size_t len);
```

Encode `s` string to URL-encoding and write encoded string into `buf`.

Parameters:

- `s` - String to encode
- `n` - String to encode length
- `buf` - Output buffer
- `len` - Output buffer size

Return value: Number of characters written to `buf`

Usage example:

```c
char url[] = "example.org/test";
char buf[1024];
mg_url_encode(url, sizeof(url) - 1, buf, sizeof(buf)); // buf is now "example.org%2Ftest"
```

### mg\_print\_base64

```c
size_t mg_print_base64(void (*out)(char, void *), void *param, va_list *ap);
```

Print a buffer as a base64-encoded string. Expects data length and a pointer to the data as next arguments in the
*va\_list* `ap`

Parameters:

- `out` - function to be used for printing chars
- `param` - argument to be passed to `out`

Return value: Number of bytes printed

Usage example:

```c
mg_snprintf(buf, sizeof(buf), "hi, %m", mg_print_base64, 1, "a");  // hi, "YWJj"
```

### mg\_print\_esc

```c
size_t mg_print_esc(void (*out)(char, void *), void *param, va_list *ap);
```

Print a JSON-escaped string. Expects string length and a pointer to the string in the *va\_list* `ap`. For
null-terminated strings use `0` for string length, or the macro `MG_ESC()`

Parameters:

- `out` - function to be used for printing chars
- `param` - argument to be passed to `out`

Return value: Number of bytes printed

Usage example:

```c
mg_snprintf(buf, sizeof(buf), "{%m: %u}", MG_ESC("value"), 123);           // {"value": 123}
mg_snprintf(buf, sizeof(buf), "{%m: %u}", mg_print_esc, 0, "value", 123);  // {"value": 123}
```

### mg\_print\_hex

```c
size_t mg_print_hex(void (*out)(char, void *), void *param, va_list *ap);
```

Print a buffer as a hex-encoded string. Expects data length and a pointer to the data as next arguments in the
*va\_list* `ap`

Parameters:

- `out` - function to be used for printing chars
- `param` - argument to be passed to `out`

Return value: Number of bytes printed

Usage example:

```c
mg_snprintf(buf, sizeof(buf), "hi, %M", mg_print_hex, 1, 255);  // hi, ff
```

### mg\_print\_ip

```c
size_t mg_print_ip(void (*out)(char, void *), void *param, va_list *ap);
```

Print an IP address using a specified character output function. Expects a pointer to a `struct mg_addr` as the next
argument in the *va\_list* `ap`

Parameters:

- `out` - function to be used for printing chars
- `param` - argument to be passed to `out`

Return value: Number of bytes printed

Usage example:

```c
struct mg_addr addr;
addr.ip = MG_U32('a', 'b', 'c', 'd');
mg_snprintf(buf, sizeof(buf), "%M", mg_print_ip, &addr);         // 97.98.99.100
```

### mg\_print\_ip\_port

```c
size_t mg_print_ip_port(void (*out)(char, void *), void *param, va_list *ap);
```

Print an IP address and port, using a specified character output function. Expects a pointer to a `struct mg_addr` as
the next argument in the *va\_list* `ap`

Parameters:

- `out` - function to be used for printing chars
- `param` - argument to be passed to `out`

Return value: Number of bytes printed

Usage example:

```c
struct mg_addr addr;
addr.ip = MG_U32('a', 'b', 'c', 'd');
addr.port = mg_htons(1234);
mg_snprintf(buf, sizeof(buf), "%M", mg_print_ip_port, &addr);         // 97.98.99.100:1234
```

### mg\_print\_ip4

```c
size_t mg_print_ip4(void (*out)(char, void *), void *param, va_list *ap);
```

Print an IP address using a specified character output function. Expects a pointer to a buffer containing the IPv4
address in network order as the next argument in the *va\_list* `ap`

Parameters:

- `out` - function to be used for printing chars
- `param` - argument to be passed to `out`

Return value: Number of bytes printed

Usage example:

```c
mg_snprintf(buf, sizeof(buf), "%M", mg_print_ip4, "abcd");         // 97.98.99.100
```

### mg\_print\_ip6

```c
size_t mg_print_ip6(void (*out)(char, void *), void *param, va_list *ap);
```

Print an IPv6 address using a specified character output function. Expects a pointer to a buffer containing the IPv6
address in network order as the next argument in the *va\_list* `ap`

Parameters:

- `out` - function to be used for printing chars
- `param` - argument to be passed to `out`

Return value: Number of bytes printed

Usage example:

```c
mg_snprintf(buf, sizeof(buf), "%M", mg_print_ip6, "abcdefghijklmnop");         //
[4142:4344:4546:4748:494a:4b4c:4d4e:4f50]
```

### mg\_print\_mac

```c
size_t mg_print_mac(void (*out)(char, void *), void *param, va_list *ap);
```

Print a MAC address using a specified character output function. Expects a pointer to a buffer containing the hardware
address as the next argument in the *va\_list* `ap`

Parameters:

- `out` - function to be used for printing chars
- `param` - argument to be passed to `out`

Return value: Number of bytes printed

Usage example:

```c
mg_snprintf(buf, sizeof(buf), "%M", mg_print_mac, "abcdef");          // 61:62:63:64:65:66
```

### mg\_print\_html\_esc

```c
size_t mg_print_html_esc(mg_pfn_t, void *arg, va_list *ap);
```

Print an HTML-escaped string. Expects string length and a pointer to the string in the *va\_list* `ap`. For
null-terminated strings use `0` for string length, or the macro `MG_ESC()`

Parameters:

- `out` - function to be used for printing chars
- `param` - argument to be passed to `out`

Return value: Number of bytes printed

Usage example:

```c
mg_printf(c, "<title>Index of %M</title>", mg_print_html_esc, (int) uri.len, uri.buf);
```

## IO Buffers

IO buffer, described by the `struct mg_iobuf`, is a simple data structure that inserts or deletes chunks of data at
arbitrary offsets and grows/shrinks automatically.

### struct mg\_iobuf

```c
struct mg_iobuf {
  unsigned char *buf;  // Pointer to stored data
  size_t size;         // Total size available
  size_t len;          // Current number of bytes
  size_t align;        // Alignment during allocation
};
```

Generic IO buffer. The `size` specifies an allocation size of the data pointed by `buf`, and `len` specifies number of
bytes currently stored.

![struct mg_iobuf diagram](https://mongoose.ws/documentation/images/mg_iobuf.svg)

### mg\_iobuf\_init()

```c
int mg_iobuf_init(struct mg_iobuf *io, size_t size, size_t align);
```

Initialize IO buffer, allocate `size` bytes.

Parameters:

- `io` - Pointer to `mg_iobuf` structure to initialize
- `size` - Amount of bytes to allocate
- `align` - Align `size` to the `align` mem boundary. `0` means no alignment

Return value: 1 on success, 0 on allocation failure

Usage example:

```c
struct mg_iobuf io;
if (mg_iobuf_init(&io, 0, 64)) {
  // io successfully initialized
}
```

### mg\_iobuf\_resize()

```c
int mg_iobuf_resize(struct mg_iobuf *io, size_t size);
```

Resize IO buffer, set the new size to `size`. The `io->buf` pointer could change after this, for example if the buffer
grows. If `size` is 0, then the `io->buf` is freed and set to NULL, and both `size` and `len` are set to 0. The
resulting `io->size` is always aligned to the `io->align` byte boundary; therefore, to avoid memory fragmentation and
frequent reallocations, set `io->align` to a higher value.

Parameters:

- `io` - iobuf to resize
- `size` - New size

Return value: 1 on success, 0 on allocation failure

Usage example:

```c
struct mg_iobuf io;
mg_iobuf_init(&io, 0, 10);  // An empty buffer with 10-byte alignment

if (mg_iobuf_resize(&io, 1)) {
  // New io size is 10
}
```

### mg\_iobuf\_free()

```c
void mg_iobuf_free(struct mg_iobuf *io);
```

Free memory pointed by `io->buf` and set to NULL. Both `size` and `len` are set to 0.

Parameters:

- `io` - iobuf to free

Return value: None

Usage example:

```c
struct mg_iobuf io;
// IO buffer initialization
// ...

// Time to cleanup
mg_iobuf_free(&io);
```

### mg\_iobuf\_add()

```c
size_t mg_iobuf_add(struct mg_iobuf *io, size_t offset, const void *buf, size_t len);
```

Insert data buffer `buf`, `len` at offset `offset`. The iobuf is expanded if required. The resulting `io->size` is
always aligned to the `io->align` byte boundary; therefore, to avoid memory fragmentation and frequent reallocations,
set `align` to a higher value.

Parameters:

- `io` - iobuf to add data
- `offset` - Offset to add data
- `buf` - Data to add
- `len` - Data length

Return value: new `io` length

Usage example:

```c
struct mg_iobuf io;         // Declare buffer
mg_iobuf_init(&io, 0, 16);  // Initialise empty buffer with 16 byte alignment
```
![Function mg_iobuf_init()](https://mongoose.ws/documentation/images/mg_iobuf_add1.svg)
```c
mg_iobuf_add(&io, io.len, "hello", 5);  // Append "hello"
```
![Function mg_iobuf_add()](https://mongoose.ws/documentation/images/mg_iobuf_add2.svg)

### mg\_iobuf\_del()

```c
size_t mg_iobuf_del(struct mg_iobuf *io, size_t offset, size_t len);
```

Delete up to `len` bytes starting from `offset`, shifting the remaining bytes, as detailed in the graph below. There is
no further action on the iobuf, `offset` and `len` are capped to operate within current iobuf size.

Parameters:

- `io` - iobuf to delete data
- `offset` - Start offset
- `len` - Number of bytes to delete

Return value: Number of bytes actually deleted

Usage example:

```c
struct mg_iobuf io;
mg_iobuf_init(&io, 0, 16);          // Empty buffer, 16-bytes aligned
mg_iobuf_add(&io, 0, "hello", 5);   // io->len is 5, io->size is 16
mg_iobuf_del(&io, 1, 3);            // io->len is 2, io->size is still 16
```
![Function mg_iobuf_del()](https://mongoose.ws/documentation/images/mg_iobuf_del.svg)

## Queue

Single-producer single-consumer non-blocking queue

### struct mg\_queue

```c
struct mg_queue {
  char *buf;
  size_t size;
  volatile size_t tail;
  volatile size_t head;
};
```

### mg\_queue\_init

```c
void mg_queue_init(struct mg_queue *q, char *buf, size_t size);
```

Initialize a queue

Parameters:

- `q` - pointer to an `mg_queue` structure
- `size` - queue size in bytes

Usage example:

```c
struct mg_queue q;
char buf[100];
mg_queue_init(&q, buf, sizeof(buf));
```

### mg\_queue\_book

```c
size_t mg_queue_book(struct mg_queue *q, char **ptr, size_t len);
```

Reserve space in a queue

Parameters:

- `q` - pointer to an `mg_queue` structure
- `ptr` - pointer to where to store the address of the reserved space in the queue
- `len` - number of bytes requested

Return value: number of bytes actually reserved

Usage example:

```c
struct mg_queue q;
char buf[100];
mg_queue_init(&q, buf, sizeof(buf));
char *ptr;
if (mg_queue_book(&q, &ptr, len) < len) {
  // Not enough space
} else {
  // Go ahead, memory area pointed to by ptr
}
```

### mg\_queue\_add

```c
void mg_queue_add(struct mg_queue *q, size_t len);
```

Add a new message to a queue

Parameters:

- `q` - pointer to an `mg_queue` structure
- `len` - Data length

Usage example:

```c
struct mg_queue q;
char buf[100];
mg_queue_init(&q, buf, sizeof(buf));
char *ptr;
if (mg_queue_book(&q, &ptr, len) < len) {
  // Not enough space
} else {
  memcpy(ptr, my_data, len);  // Copy data to the queue
  mg_queue_add(&q, len);      // Add a new message to the queue
}
```

### mg\_queue\_next

```c
size_t mg_queue_next(struct mg_queue *q, char **ptr);
```

Get the oldest message in a queue

Parameters:

- `q` - pointer to an `mg_queue` structure
- `ptr` - pointer to where to store the address of the message in the queue

Return value: number of bytes in message, 0 if no outstanding messages

Usage example:

```c
struct mg_queue q;
char buf[100];
mg_queue_init(&q, buf, sizeof(buf));
...
char *ptr;
size_t len;
if ((len = mg_queue_next(&q, &ptr)) > 0) {
  // message data pointed to by ptr
} else {
  // no messages
}
```

### mg\_queue\_del

```c
void mg_queue_del(struct mg_queue *q, size_t len);
```

Delete `len` bytes, oldest message in queue

Parameters:

- `q` - pointer to an `mg_queue` structure
- `len` - number of bytes to delete

Usage example:

```c
struct mg_queue q;
char buf[100];
mg_queue_init(&q, buf, sizeof(buf));
...
char *ptr;
if ((len = mg_queue_next(&q, &ptr)) > 0) {
  memcpy(somewhere, ptr, len);
  mg_queue_del(&q, len);
} else {
  // no messages
}
```

### mg\_queue\_printf()

```c
size_t mg_queue_printf(struct mg_queue *q, const char *fmt, ...);
```

Print message into a queue. Internally calls [mg\_queue\_book()](#mg_queue_book) and [mg\_queue\_add()](#mg_queue_add),
with the conveniency of printf. The format string is evaluated first to calculate needed room and then again to
actually print if there is available room in the queue; pay attention to side effects when calling.

Parameters:

- `q` - pointer to an `mg_queue` structure
- `fmt` - format string in `printf` semantics. See [mg\_snprintf](#mg_snprintf-mg_vsnprintf) for the list of supported
format specifiers

Return value: number of bytes printed

Usage example:

```c
struct mg_queue q;
char buf[100];
mg_queue_init(&q, buf, sizeof(buf));
mg_queue_printf(&q, "hi %s", "Peter");
```

## URL

### mg\_url\_port()

```c
unsigned short mg_url_port(const char *url);
```

Return port for given URL

Parameters:

- `url` - URL to extract port

Return value: Port for given URL or `0` if URL doesn't contain port and there isn't default port for URL protocol

Usage example:

```c
unsigned short port1 = mg_url_port("https://myhost.com") // port1 is now 443 (default https port)
unsigned short port2 = mg_url_port("127.0.0.1:567") // port2 is now 567
```

### mg\_url\_is\_ssl()

```c
int mg_url_is_ssl(const char *url);
```

Check if given URL uses an encrypted scheme

Parameters:

- `url` - URL to check

Return value: non-zero if given URL uses an encrypted scheme, zero otherwise

Usage example:

```c
if (mg_url_is_ssl("https://example.org")) {
  // scheme is encrypted
}
```

### mg\_url\_host()

```c
struct mg_str mg_url_host(const char *url);
```

Extract host name from given URL.

Parameters:

- `url` - a URL string

Return value: host name

Usage example:

```c
struct mg_str a = mg_url_host("https://my.example.org:1234"); // a == "my.example.org"
struct mg_str b = mg_url_host("tcp://[::1]"); // b == "[::1]"
```

### mg\_url\_user()

```c
struct mg_str mg_url_user(const char *url);
```

Extract user name from given URL.

Parameters:

- `url` - URL to extract user name

Return value: User name or empty string if not found

Usage example:

```c
struct mg_str user_name = mg_url_user("https://user@password@my.example.org"); // user_name is now "user"
```

### mg\_url\_pass()

```c
struct mg_str mg_url_pass(const char *url);
```

Extract password from given URL.

Parameters:

- `url` - URL to extract password

Return value: Password or empty string if not found

Usage example:

```c
struct mg_str pwd = mg_url_user("https://user@password@my.example.org"); // pwd is now "password"
```

### mg\_url\_uri()

```c
const char *mg_url_uri(const char *url);
```

Extract URI from given URL. Note, that function returns a pointer within `url`; there is no need to free it explicitly

Parameters:

- `url` - URL to extract URI

Return value: URI or `\` if not found

Usage example:

```c
const char *uri = mg_url_uri("https://example.org/subdir/subsubdir"); // \`uri\` is now pointer to "subdir/subsubdir"
```

## Logging

Mongoose provides a set of functions and macros for logging. The application can use these functions for its own
purposes as well as the rest of Mongoose API.

### LOG()

```c
#define LOG(level, args)
#define MG_ERROR(args) MG_LOG(MG_LL_ERROR, args)
#define MG_INFO(args) MG_LOG(MG_LL_INFO, args)
#define MG_DEBUG(args) MG_LOG(MG_LL_DEBUG, args)
#define MG_VERBOSE(args) MG_LOG(MG_LL_VERBOSE, args)
```

Logging macros. Usage example:

```c
MG_INFO(("Hello %s!", "world"));  // Output "Hello, world"
```

### mg\_log\_set()

```c
void mg_log_set(int level);
```

Set Mongoose logging level.

Parameters:

- `level` - log level, can be one of the following values:
	- `MG_LL_NONE` - Disable logging
		- `MG_LL_ERROR` - Log errors only
		- `MG_LL_INFO` - Log errors and info messages
		- `MG_LL_DEBUG` - Log errors, info and debug messages
		- `MG_LL_VERBOSE` - Log everything, and more

Return value: None

Usage example:

```c
mg_log_set(MG_LL_INFO);                  // Set log level to info
```

### mg\_hexdump()

```c
void mg_hexdump(const void *buf, int len);
```

Log a hex dump of binary data `buf`, `len`.

Parameters:

- `buf` - Data pointer
- `len` - Data length

Return value: none

Usage example:

```c
mg_hexdump(c->recv.buf, c->recv.len);  // Hex dump incoming data
```

### mg\_log\_set\_fn()

```c
void mg_log_set_fn(mg_pfn_t logfunc, void *param);
```

Redirect logs to a custom function. Parameters:

- `logfunc` - a pointer to a function that logs a single character
- `param` - a parameter for a logging function

Usage example: redirecting logs to syslog.

```c
static void mylog(char ch, void *param) {
  static char buf[256];
  static size_t len;
  buf[len++] = ch;
  if (ch == '\n' || len >= sizeof(buf)) {
    syslog(LOG_INFO, "%.*s", (int) len, buf); // Send logs
    len = 0;
  }
}
...
mg_log_set_fn(mylog, NULL);
```

## Filesystem

### struct mg\_fs

```c
struct mg_fs {
  int (*st)(const char *path, size_t *size, time_t *mtime);               // stat file
  void (*ls)(const char *path, void (*fn)(const char *, void *), void *); // List directory entries: call fn(file_name,
fn_data) for each directory entry
  void *(*op)(const char *path, int flags);                               // Open file
  void (*cl)(void *fd);                                                   // Close file
  size_t (*rd)(void *fd, void *buf, size_t len);                          // Read file
  size_t (*wr)(void *fd, const void *buf, size_t len);                    // Write file
  size_t (*sk)(void *fd, size_t offset);                                  // Set file position
  bool (*mv)(const char *from, const char *to);                           // Rename file
  bool (*rm)(const char *path);                                           // Delete file
  bool (*mkd)(const char *path);                                          // Create directory
};

enum { MG_FS_READ = 1, MG_FS_WRITE = 2, MG_FS_DIR = 4 };
```

Filesystem virtualisation layer.

Mongoose allows to override file IO operations in order to support different storages, like programmable flash,
no-filesystem devices etc. In order to accomplish this, Mongoose provides a `struct mg_fs` API to specify a custom
filesystem. In addition to this, Mongoose provides several built-in APIs - a standard POSIX, FatFS, and a "packed FS"
API:

```c
extern struct mg_fs mg_fs_posix;   // POSIX open/close/read/write/seek
extern struct mg_fs mg_fs_packed;  // Packed FS, see tutorials/core/embedded-filesystem
extern struct mg_fs mg_fs_fat;     // FAT FS
```

### struct mg\_fd

```c
struct mg_fd {
  void *fd;
  struct mg_fs *fs;
};
```

Opened file abstraction.

### mg\_fs\_open()

```c
struct mg_fd *mg_fs_open(struct mg_fs *fs, const char *path, int flags);
```

Open a file in a given filesystem.

Parameters:

- `fs` - a filesystem implementation
- `path` - a file path
- `flags` - desired flags, a combination of `MG_FS_READ` and `MG_FS_WRITE`

Return value: a non-NULL opened descriptor, or NULL on failure.

Usage example:

```c
struct mg_fd *fd = mg_fs_open(&mg_fs_posix, "/tmp/data.json", MG_FS_WRITE);
```

### mg\_fs\_close()

```c
void mg_fs_close(struct mg_fd *fd);
```

Close an opened file descriptor.

Parameters:

- `fd` - an opened file descriptor

Return value: none

### mg\_file\_read()

```c
struct mg_str mg_file_read(struct mg_fs *fs, const char *path);
```

Read the whole file in memory. This allocates memory that must be freed by calling `mg_free`

Parameters:

- `fs` - a filesystem implementation
- `path` - a file path

Return value: on success, the `struct mg_str` points to file data, which is guaranteed to be nul-terminated, and its
`len` field contains file length. On error, it contains a NULL pointer.

Usage example:

```c
struct mg_str data = mg_file_read(&mg_fs_packed, "/data.json"); // size = data.len
mg_free(data.buf);
```

### mg\_file\_write()

```c
bool mg_file_write(struct mg_fs *fs, const char *path, const void *buf, size_t len);
```

Write a piece of data `buf`, `len` to a file `path`. If the file does not exist, it gets created. The previous content,
if any, is deleted.

Parameters:

- `fs` - a filesystem implementation
- `path` - a file path
- `buf` - a pointer to data to be written
- `len` - data size

Return value: true on success, false on error

Usage example:

```c
mg_file_write(&mg_fs_fat, "/test.txt", "hi\n", 3);
```

### mg\_file\_printf()

```c
bool mg_file_printf(struct mg_fs *fs, const char *path, const char *fmt, ...);
```

Write a printf-formatted data to a file `path`. If the file does not exist, it gets created. The previous content, if
any, is deleted.

Parameters:

- `fs` - a filesystem implementation
- `path` - a file path
- `fmt` - format string in `printf` semantics. See [mg\_snprintf](#mg_snprintf-mg_vsnprintf) for the list of supported
format specifiers

Return value: true on success, false on error

Usage example:

```c
mg_file_printf(&mg_fs_fat, "/test.txt", "%s\n", "hi");
```

### mg\_fs\_ls()

```c
bool mg_fs_ls(struct mg_fs *fs, const char *path, char *buf, size_t len);
```

Helper function to scan a filesystem in a sequential way, without using a callback function. Each call will return one
entry until the list is exhausted

Parameters:

- `fs` - a filesystem implementation
- `path` - a file path
- `buf` - a pointer to where to store the results
- `len` - buffer size

Return value: true if there are more entries, need to call again; false when no more entries left.

Usage example:

```c
char buf[100] = "";
while (mg_fs_ls(&mg_fs_posix, "./", buf, sizeof(buf)))
  puts(buf);
```

## Wi-Fi

Currently, the following functions work only when using Mongoose built-in TCP/IP stack and drivers, for supported Wi-Fi
chipsets.

Usage example:

- see [Pico 2
W](https://github.com/cesanta/mongoose/tree/master/tutorials/pico-sdk/pico-2-w-picosdk-baremetal-builtin-ap)
- see [Pimoroni
RM2](https://github.com/cesanta/mongoose/tree/master/tutorials/stm32/rm2-nucleo-f746zg-make-baremetal-builtin)
- see [Portenta H7](https://github.com/cesanta/mongoose/tree/master/tutorials/stm32/portenta-h7-make-baremetal-builtin)

### Interface events

Wi-Fi adds these additional [Interface events](#interface-events)

```c
enum {
  ...
  MG_TCPIP_EV_WIFI_SCAN_RESULT,  // Wi-Fi scan results         struct mg_wifi_scan_bss_data *
  MG_TCPIP_EV_WIFI_SCAN_END,     // Wi-Fi scan has finished    NULL
  MG_TCPIP_EV_WIFI_CONNECT_ERR,  // Wi-Fi connect has failed   driver and chip specific
  ...
};
```

### struct mg\_wifi\_data

```c
struct mg_wifi_data {
  char *ssid, *pass;      // STA mode, SSID to connect to
  char *apssid, *appass;  // AP mode, our SSID
  uint32_t apip, apmask;  // AP mode, our IP address and mask
  uint8_t security;       // STA mode, TBD
  uint8_t apsecurity;     // AP mode, TBD
  uint8_t apchannel;      // AP mode, channel to use
  bool apmode;  // start in AP mode; 'false' -> connect to 'ssid' != NULL
};
```

Structure containing STA and AP credentials and configuration. When starting up, if `apmode` is true, AP mode will be
entered (the Access Point will start). Otherwise, if `ssid` is not NULL, STA mode will be entered and a connection to
that SSID will be attempted.

### struct mg\_wifi\_scan\_bss\_data

```c
struct mg_wifi_scan_bss_data {
  struct mg_str SSID;
  char *BSSID;
  int16_t RSSI;
  uint8_t security;
#define MG_WIFI_SECURITY_OPEN 0
#define MG_WIFI_SECURITY_WEP MG_BIT(0)
#define MG_WIFI_SECURITY_WPA MG_BIT(1)
#define MG_WIFI_SECURITY_WPA2 MG_BIT(2)
#define MG_WIFI_SECURITY_WPA3 MG_BIT(3)
  uint8_t channel;
  unsigned band : 2;
#define MG_WIFI_BAND_2G 0
#define MG_WIFI_BAND_5G 1
  unsigned has_n : 1;
};
```

Structure pointed to by `ev_data` when calling the interface event handler as a consequence of a call to
[mg\_wifi\_scan](#mg_wifi_scan). The `MG_TCPIP_EV_WIFI_SCAN_RESULT` event is triggered for each entry, and a final
`MG_TCPIP_EV_WIFI_SCAN_END` event is generated last.

### mg\_wifi\_scan()

```c
bool mg_wifi_scan(void);
```

Initiate a scan for available Wi-Fi networks, must be called in AP mode.

### mg\_wifi\_connect()

```c
bool mg_wifi_connect(struct mg_wifi_data *wifi);
```

Connect to the desired Wi-Fi network (STA mode), as defined by the argument

### mg\_wifi\_disconnect()

```c
bool mg_wifi_disconnect(void);
```

Disconnect from the current Wi-Fi network (STA mode)

### mg\_wifi\_ap\_start()

```c
bool mg_wifi_ap_start(struct mg_wifi_data *wifi);
```

Start being an Access Point (AP mode), as defined by the argument

### mg\_wifi\_ap\_stop()

```c
bool mg_wifi_ap_stop(void);
```

Stop being an Access Point

## Appendix

## Board pinouts: STM32

| Board | UART,TX,RX | Ethernet | LED | Doc |
| --- | --- | --- | --- | --- |
| STM32H747I-DISCO | USART1,A9,A10 | A1,A2,A7,C1,C4,C5,G11,G12,G13 | I12,I13,I14 |
[UM2411](https://www.st.com/resource/en/user_manual/um2411-discovery-kit-with-stm32h747xi-mcu-stmicroelectronics.pdf) |
| STM32H735G-DK | USART3,D8,D9 | A1,A2,A7,C1,C4,C5,B11,B12,B13 | C3,C2 |
[UM2679](https://www.st.com/resource/en/user_manual/um2679-discovery-kit-with-stm32h735ig-mcu-stmicroelectronics.pdf) |
| STM32H573I-DK | USART1,A9,A10 | A1,A2,A7,C1,C4,C5,G11,G12,G13 | I8,I9,F1 |
[UM3143](https://www.st.com/resource/en/user_manual/um3143-discovery-kit-with-stm32h573ii-mcu-stmicroelectronics.pdf) |
| Nucleo-N657X0-Q | USART1,E5,E6 | F4,F5,F7,F10,F11,F12,F13,F14,F15 | G0,G8,G10 |
[UM3417](https://www.st.com/resource/en/user_manual/um3417-stm32n6-nucleo144-board-mb1940-stmicroelectronics.pdf) |
| Nucleo-H563ZI | USART3,D8,D9 | A1,A2,A7,C1,C4,C5,B15,G11,G13 | B0,F4,G4 |
[UM3115](https://www.st.com/resource/en/user_manual/um3115-stm32h5-nucleo144-board-mb1404-stmicroelectronics.pdf) |
| Nucleo-H7S3L8 | USART3,D8,D9 | A2,A7,B6,G4,G5,G6,G11,G12,G13 | D10,D13,B7 |
[UM3276](https://www.st.com/resource/en/user_manual/um3276-stm32h7rx7sx-nucleo144-board-mb1737-stmicroelectronics.pdf) |
| Nucleo-H745ZI-Q | USART3,B10,B11 | A1,A2,A7,C1,C4,C5,B13,G11,G13 | I13,J2,D3 |
[UM2408](https://www.st.com/resource/en/user_manual/um2408-stm32h7-nucleo144-boards-mb1363-stmicroelectronics.pdf) |
| Nucleo-H755ZI-Q | USART3,D8,D9 | A1,A2,A7,C1,C4,C5,G11,G12,G13 | B0,E1,B14 |
[UM2408](https://www.st.com/resource/en/user_manual/um2408-stm32h7-nucleo144-boards-mb1363-stmicroelectronics.pdf) |
| Nucleo-H753ZI | USART3,D8,D9 | A1,A2,A7,C1,C4,C5,B11,B12,B13 | C3,C2,C2 |
[UM2407](https://www.st.com/resource/en/user_manual/um2407-stm32h7-nucleo144-boards-mb1364-stmicroelectronics.pdf) |
| Nucleo-H743ZI | USART3,D8,D9 | A1,A2,A7,C1,C4,C5,B13,G11,G13 | B0,E1,B14 |
[UM2407](https://www.st.com/resource/en/user_manual/um2407-stm32h7-nucleo144-boards-mb1364-stmicroelectronics.pdf) |
| Nucleo-H723ZG | USART3,D8,D9 | A1,A2,A7,C1,C4,C5,B13,G11,G13 | B0,E1,B14 |
[UM2407](https://www.st.com/resource/en/user_manual/um2407-stm32h7-nucleo144-boards-mb1364-stmicroelectronics.pdf) |
| Nucleo-Fxxxxx | USART3,D8,D9 | A1,A2,A7,C1,C4,C5,B13,G11,G13 | B0,B7,B14 |
[UM1974](https://www.st.com/resource/en/user_manual/um1974-stm32-nucleo144-boards-mb1137-stmicroelectronics.pdf) |

## Board pinouts: NXP

| Board | UART, TX, RX | Ethernet | LED |
| --- | --- | --- | --- |
| MIMXRT1020-EVK | LPUART2, B1\_08, B1\_09 | B0\_08, B0\_09, B0\_10, B0\_11, B0\_12, B0\_13, B0\_14, B0\_15, EMC\_40,
EMC\_41 | B0\_05 |
| MIMXRT1024-EVK | LPUART1, B0\_06, B0\_07 | B0\_08, B0\_09, B0\_10, B0\_11, B0\_12, B0\_13, B0\_14, B0\_15, EMC\_40,
EMC\_41 | B0\_24 |
| MIMXRT1040-EVK | LPUART1, B0\_12, B0\_13 | B1\_04, B1\_05, B1\_06, B1\_07, B1\_08, B1\_09, B1\_10, B1\_11, EMC\_40,
EMC\_41 | B0\_08 |
| MIMXRT1060-EVK | LPUART3, B0\_06, B0\_07 | B1\_04, B1\_05, B1\_06, B1\_07, B1\_08, B1\_09, B1\_10, B1\_11, EMC\_40,
EMC\_41 | B0\_08 |
| MIMXRT1064-EVK | LPUART1, B0\_12, B0\_13 | B1\_04, B1\_05, B1\_06, B1\_07, B1\_08, B1\_09, B1\_10, B1\_11, EMC\_40,
EMC\_41 | B0\_08 |

![arrow up](https://mongoose.ws/documentation/images/arrow-up-circle-fill.svg "scroll to top")

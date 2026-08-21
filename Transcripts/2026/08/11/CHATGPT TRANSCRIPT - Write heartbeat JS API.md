# Write heartbeat JS API

- URL: https://chatgpt.com/c/6a7b3116-cbb8-83ea-b1ae-eed4b98efe54
- Created: 2026-08-11T14:26:35.651Z

---

> make an elegent JS API for a heartbeat fold (websocket)

I’ll shape this as a small, ergonomic WebSocket heartbeat abstraction: declarative options, automatic timeout detection, and clean lifecycle hooks. I’ll also check whether “heartbeat fold” is a specific established term before naming the API around it.

```json
{"system2_search_query":[{"q":"\"heartbeat fold\" websocket javascript"},{"q":"\"heartbeat fold\" WebSocket"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Designing heartbeat API**

I’m shaping a compact WebSocket heartbeat API around application-level messages, since browser JavaScript can’t directly access protocol ping/pong frames. I’ll emphasize clear defaults, lifecycle control, timeout handling, and a foldable liveness state.

**Designed heartbeat API**

**Searched 21 websites**

</details>

I’d model the “fold” as: **heartbeat events are reduced into one current connection-health state**. I couldn’t find “heartbeat fold” as an established WebSocket term, so this treats it as a functional API design rather than matching an existing convention. In browsers, native WebSocket Ping/Pong control frames are not exposed to JavaScript, so a browser-side implementation should use application messages such as `{type:"ping"}` / `{type:"pong"}`. citeturn954157search0turn232931search0

### API

```js
const health = heartbeat(socket, {
  every: 10_000,
  timeout: 3_000,

  ping: ({ id, time }) => ({
    type: "ping",
    id,
    time
  }),

  pong: message =>
    message.type === "pong"
      ? message.id
      : null
})
.fold(
  {
    status: "connecting",
    rtt: null,
    misses: 0
  },

  (state, event) => {
    switch (event.type) {
      case "pong":
        return {
          status: "healthy",
          rtt: event.rtt,
          misses: 0
        };

      case "timeout":
        return {
          ...state,
          status: "stale",
          misses: state.misses + 1
        };

      case "close":
        return {
          ...state,
          status: "closed"
        };

      default:
        return state;
    }
  }
);

health.subscribe(state => {
  console.log(state);
});

// synchronous snapshot
health.value;

// cleanup
health.stop();
```

The nice part is that the heartbeat mechanism doesn't dictate what “healthy” means. It emits a tiny event algebra:

```ts
type HeartbeatEvent =
  | { type: "ping"; id: number; time: number }
  | { type: "pong"; id: number; rtt: number }
  | { type: "timeout"; id: number; elapsed: number }
  | { type: "open" }
  | { type: "close"; code: number; reason: string };
```

Then `.fold()` turns those events into whatever state your application wants.

### Minimal implementation

```js
export function heartbeat(ws, options = {}) {
  const {
    every = 10_000,
    timeout = 3_000,
    ping = ({ id, time }) => ({ type: "ping", id, time }),
    pong = msg => msg?.type === "pong" ? msg.id : null,
    encode = JSON.stringify,
    decode = JSON.parse
  } = options;

  let seq = 0;
  let interval;
  let stopped = false;

  const pending = new Map();
  const listeners = new Set();

  const emit = event => {
    for (const listener of listeners)
      listener(event);
  };

  const sendBeat = () => {
    if (ws.readyState !== WebSocket.OPEN)
      return;

    const id = ++seq;
    const time = performance.now();

    ws.send(encode(ping({ id, time })));

    emit({ type: "ping", id, time });

    const timer = setTimeout(() => {
      const beat = pending.get(id);

      if (!beat)
        return;

      pending.delete(id);

      emit({
        type: "timeout",
        id,
        elapsed: performance.now() - beat.time
      });
    }, timeout);

    pending.set(id, { time, timer });
  };

  const onOpen = () => {
    emit({ type: "open" });
    sendBeat();
    interval = setInterval(sendBeat, every);
  };

  const onMessage = event => {
    let message;

    try {
      message = decode(event.data);
    } catch {
      return;
    }

    const id = pong(message);

    if (id == null)
      return;

    const beat = pending.get(id);

    if (!beat)
      return;

    clearTimeout(beat.timer);
    pending.delete(id);

    emit({
      type: "pong",
      id,
      rtt: performance.now() - beat.time
    });
  };

  const onClose = event => {
    clearInterval(interval);

    for (const { timer } of pending.values())
      clearTimeout(timer);

    pending.clear();

    emit({
      type: "close",
      code: event.code,
      reason: event.reason
    });
  };

  ws.addEventListener("open", onOpen);
  ws.addEventListener("message", onMessage);
  ws.addEventListener("close", onClose);

  // Handle sockets already opened before heartbeat().
  if (ws.readyState === WebSocket.OPEN)
    onOpen();

  const source = {
    subscribe(fn) {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },

    fold(initial, reducer) {
      let value = initial;
      const subscribers = new Set();

      const unsubscribe = source.subscribe(event => {
        const next = reducer(value, event);

        if (Object.is(next, value))
          return;

        value = next;

        for (const fn of subscribers)
          fn(value, event);
      });

      return {
        get value() {
          return value;
        },

        subscribe(fn) {
          subscribers.add(fn);
          fn(value);

          return () => subscribers.delete(fn);
        },

        stop() {
          unsubscribe();
          source.stop();
        }
      };
    },

    stop() {
      if (stopped)
        return;

      stopped = true;

      clearInterval(interval);

      for (const { timer } of pending.values())
        clearTimeout(timer);

      pending.clear();

      ws.removeEventListener("open", onOpen);
      ws.removeEventListener("message", onMessage);
      ws.removeEventListener("close", onClose);

      listeners.clear();
    }
  };

  return source;
}
```

### Even cleaner default

I'd make the 90% case require almost no reducer:

```js
const health = heartbeat(ws, {
  every: 10_000,
  timeout: 3_000,
  ping: ({ id }) => ({ type: "ping", id }),
  pong: msg => msg.type === "pong" && msg.id
})
.health();

health.subscribe(({ alive, rtt, misses }) => {
  // ...
});
```

And expose `.fold()` only when custom semantics are needed:

```js
heartbeat(ws, config)
  .fold(initialState, reducer);
```

That gives the library a clean conceptual split:

```text
WebSocket
   │
heartbeat()
   │
   ├── ping
   ├── pong
   ├── timeout
   └── close
          │
        fold()
          │
          ▼
    application state
```

I prefer this over baking reconnection into the heartbeat API. **Heartbeat answers “is this connection alive?”; reconnection answers “what should I do about it?”** Keeping those separate makes the primitive much easier to compose. Protocol-level WebSocket Ping/Pong is explicitly intended for keepalive and responsiveness checks, while browser JavaScript has to implement this layer with ordinary messages because those control frames aren't exposed. citeturn232931search0turn954157search0


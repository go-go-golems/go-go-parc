# Explain coalgebras with examples

- URL: https://chatgpt.com/c/6a7a7585-cb88-83ea-8b40-1c472529ec71
- Created: 2026-08-11T01:06:35.915Z

---

> examples of coalgebras in real everyday down to earth honest web programming, for grunts in the trenches

In ordinary web programming, **coalgebra shows up whenever you have some state and a function that tells you “what can I observe now, and what state comes next?”** Most developers use coalgebraic patterns constantly without calling them coalgebras.

Mathematically, the cartoon version is:

```text
State -> SomeStructure<State>
```

Instead of consuming a structure and collapsing it into an answer, you **open a state up one step at a time**.

That sounds abstract. Here are the trench-level versions.

### 1. An iterator is basically a coalgebra

```ts
type Step<A, S> =
  | { done: true }
  | { done: false; value: A; next: S }

function nextNumber(n: number): Step<number, number> {
  return {
    done: false,
    value: n,
    next: n + 1
  }
}
```

You have a state:

```text
42
```

You inspect it once:

```text
value = 42
next state = 43
```

Then again:

```text
value = 43
next state = 44
```

The function does not build the infinite list `[42, 43, 44, ...]`.

It tells you **one observable step**.

That is quintessential coalgebra.

JavaScript's:

```js
iterator.next()
```

has essentially this flavor.

---

### 2. Pagination from a REST API

This is probably the most boringly practical example.

```ts
type Cursor = string | null

type Page<T> = {
  items: T[]
  nextCursor: Cursor
}

async function getPage(cursor: Cursor): Promise<Page<User>> {
  const url = cursor
    ? `/api/users?cursor=${cursor}`
    : `/api/users`

  return fetch(url).then(r => r.json())
}
```

Conceptually:

```text
Cursor -> Page + next Cursor
```

You don't necessarily know the entire collection.

You know:

> Given where I am now, give me what I can see now and enough information to continue.

That's coalgebra territory.

Your production code may look like:

```ts
let cursor: Cursor = null

do {
  const page = await getPage(cursor)

  for (const user of page.items) {
    await processUser(user)
  }

  cursor = page.nextCursor
} while (cursor !== null)
```

Nobody at standup says:

> "I implemented a coalgebra over our pagination state."

They say:

> "I loop over the cursor until there aren't any more pages."

Same pattern.

---

### 3. A UI state machine

Consider a login flow:

```ts
type LoginState =
  | { type: "loggedOut" }
  | { type: "submitting"; email: string }
  | { type: "loggedIn"; user: User }
  | { type: "failed"; message: string }
```

A function might tell the UI what this state looks like:

```ts
function view(state: LoginState) {
  switch (state.type) {
    case "loggedOut":
      return {
        screen: "login-form"
      }

    case "submitting":
      return {
        screen: "spinner"
      }

    case "loggedIn":
      return {
        screen: "dashboard",
        user: state.user
      }

    case "failed":
      return {
        screen: "error",
        message: state.message
      }
  }
}
```

A richer coalgebraic version says not only what you see, but how the system can continue.

Think:

```text
current app state
       |
       v
what is observable now
+
possible next behavior
```

This is why coalgebra is deeply connected with **state machines, reactive UIs, processes, servers, games, protocols, and long-running systems**.

Those things aren't really "final answers."

They're things you keep observing and interacting with.

---

### 4. WebSocket connections

A WebSocket is much more naturally thought about coalgebraically than as a fixed data structure.

You don't have:

```ts
const allMessages = socket.getEveryMessageThatWillEverExist()
```

Obviously.

You have something more like:

```text
Connection
   ↓
message now / wait / closed
   +
continuing Connection
```

Pseudo-code:

```ts
type SocketStep =
  | { type: "message"; message: Message; next: Connection }
  | { type: "closed" }
  | { type: "error"; error: Error }
```

Conceptually:

```ts
function observe(connection: Connection): Promise<SocketStep>
```

The connection is an ongoing thing.

You repeatedly observe its next piece of behavior.

That's exactly the world coalgebra was designed to describe.

---

### 5. Polling a job

You've probably written this:

```ts
async function waitForJob(id: string) {
  while (true) {
    const job = await fetch(`/jobs/${id}`).then(r => r.json())

    if (job.status === "done") {
      return job.result
    }

    if (job.status === "failed") {
      throw new Error(job.error)
    }

    await sleep(1000)
  }
}
```

Each request observes one step:

```text
job ID/state
    ↓
pending + continue
done + result
failed + error
```

Again: coalgebraic shape.

The important thing is that the program is describing an **evolving process**, not reducing a finished structure.

---

### 6. Infinite scrolling

The frontend equivalent:

```ts
type FeedState = {
  cursor: string | null
}

async function more(state: FeedState) {
  const page = await loadPosts(state.cursor)

  return {
    posts: page.posts,
    next: {
      cursor: page.nextCursor
    }
  }
}
```

Given the current feed state:

```text
State
```

you get:

```text
visible posts + future State
```

That's about as down-to-earth a coalgebra as you can get.

---

### 7. Retry logic

Here's another bit of production sludge:

```ts
type RetryState = {
  attempt: number
  delayMs: number
}

function nextRetry(state: RetryState): RetryState | null {
  if (state.attempt >= 5) {
    return null
  }

  return {
    attempt: state.attempt + 1,
    delayMs: state.delayMs * 2
  }
}
```

Starting with:

```ts
{ attempt: 0, delayMs: 250 }
```

you can **unfold**:

```text
250ms
500ms
1000ms
2000ms
4000ms
stop
```

The function describes how to expose the next stage from the current state.

Coalgebra.

---

### 8. Lazy tree traversal

Suppose you're loading comments from Reddit/Hacker News/your own horrifying enterprise CMS.

```ts
type NodeState = {
  id: string
}

async function expand(node: NodeState) {
  const data = await fetch(`/comments/${node.id}`).then(r => r.json())

  return {
    value: data.comment,
    children: data.childIds.map(id => ({ id }))
  }
}
```

Notice what's happening.

You didn't eagerly construct:

```text
EntireCommentTree
```

You have:

```text
NodeState -> value + child NodeStates
```

So the tree can be **generated on demand**.

That's a coalgebraic way to represent a tree.

---

### 9. React-ish component behavior

Ignore whether a particular framework implements this literally.

Conceptually a component is often:

```text
State
  ↓
what should be displayed
+
what events can produce the next State
```

For example:

```ts
type Counter = {
  count: number
}

function observeCounter(state: Counter) {
  return {
    text: `Count: ${state.count}`,

    increment: () => ({
      count: state.count + 1
    }),

    decrement: () => ({
      count: state.count - 1
    })
  }
}
```

Given one state, you expose its **observable behavior**.

That's a useful coalgebraic lens for UI programming.

---

## The easiest way to remember algebra vs. coalgebra

Here's the distinction that is actually useful at a keyboard.

**Algebra:**

```text
stuff containing smaller answers
        ↓
      answer
```

You **fold things down**.

Example:

```ts
[1, 2, 3, 4].reduce((total, x) => total + x, 0)
```

Conceptually:

```text
structure -> result
```

**Coalgebra:**

```text
state
  ↓
one piece of stuff + more state
```

You **unfold things outward**.

Example:

```ts
function step(n: number) {
  return {
    value: n,
    next: n + 1
  }
}
```

So the blue-collar mnemonic is:

> **Algebra consumes. Coalgebra reveals.**

Or more specifically:

> **A fold says, “How do I combine this thing?”**
>
> **An unfold says, “Given where I am, what's the next thing?”**

---

## Where you'll actually encounter the idea

In day-to-day web work, coalgebraic thinking is hiding behind:

- iterators and generators
- pagination/cursors
- streams
- WebSockets
- Server-Sent Events
- polling
- retries/backoff
- UI state machines
- workflow engines
- protocol handlers
- lazy trees
- infinite scroll
- event-driven systems
- reactive programming
- simulations
- long-running services

The common theme is **behavior over time**.

A JSON document sitting on disk is naturally treated as data.

A WebSocket connection, browser UI, job runner, video stream, cursor, or server process is different: its important characteristic is **what it can reveal/do next**.

That's where coalgebra stops being category-theory decoration and starts describing something working programmers deal with constantly.


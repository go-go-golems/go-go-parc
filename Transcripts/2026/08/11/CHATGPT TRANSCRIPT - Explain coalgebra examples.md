# Explain coalgebra examples

- URL: https://chatgpt.com/c/6a7a7623-25b0-83ea-93dc-81708034415f
- Created: 2026-08-11T01:09:09.183Z

---

> coalgebra: dog-grooming, cooking, react webapp

A useful way to think about **coalgebra** is: instead of asking “how do I build a value?”, ask **“given the current state, what can I observe, and what state comes next?”**

For a coalgebra of the form

$$
c : X \to O \times X
$$

`X` is the system state, `O` is what you can observe now, and the returned `X` is the next state.

| Domain | State $X$ | Observation | Next-state behavior |
|---|---|---|---|
| Dog grooming | dog + grooming progress | coat condition, nails, cleanliness | brush → bathe → dry → trim |
| Cooking | ingredients + cooking state | temperature, texture, doneness | chop → heat → stir → simmer |
| React webapp | application state | rendered UI | click/fetch/input → new state |

### Dog grooming

Imagine:

$$
groom : DogState \to GroomObservation \times DogState
$$

A state might contain:

```ts
type DogState = {
  dirty: boolean
  tangled: boolean
  nailsLong: boolean
  wet: boolean
}
```

The coalgebra tells you what is observable and how grooming continues:

```ts
function step(s: DogState) {
  if (s.tangled)
    return ["needs brushing", { ...s, tangled: false }]

  if (s.dirty)
    return ["needs bathing", { ...s, dirty: false, wet: true }]

  if (s.wet)
    return ["needs drying", { ...s, wet: false }]

  if (s.nailsLong)
    return ["needs nail trim", { ...s, nailsLong: false }]

  return ["finished", s]
}
```

The important part is that grooming is modeled as an **evolving process**, potentially observed step after step.

### Cooking

Cooking is naturally coalgebraic because a dish continually changes:

$$
cook : FoodState \to Observation \times FoodState
$$

For example:

```ts
type Soup = {
  temperature: number
  minutesCooked: number
  salt: number
}
```

A step could be:

```ts
function cookStep(soup: Soup) {
  return [
    {
      hot: soup.temperature >= 90,
      done: soup.minutesCooked >= 30
    },
    {
      ...soup,
      temperature: Math.min(100, soup.temperature + 5),
      minutesCooked: soup.minutesCooked + 1
    }
  ]
}
```

You can keep applying `cookStep`:

$$
s_0 \to s_1 \to s_2 \to s_3 \to \cdots
$$

That potentially infinite unfolding is one of the central intuitions behind coalgebra.

### React webapp

React is perhaps the clearest software analogy.

Take:

```ts
UI = render(state)
nextState = update(state, event)
```

A web application can be viewed roughly as:

$$
AppState \to UI \times (Event \to AppState)
$$

For example:

```ts
type State = {
  count: number
}

function app(state: State) {
  return {
    view: `<button>${state.count}</button>`,

    transition(event: "click") {
      return {
        count: state.count + 1
      }
    }
  }
}
```

At every moment the app exposes:

1. **what you can observe** — the UI;
2. **how it can continue** — its response to events.

So:

```text
state
  ↓
rendered page
  +
possible reactions
  ↓
new state
  ↓
new rendered page
  ↓
...
```

That is strongly coalgebraic.

The broad contrast is:

$$
\textbf{Algebra: } F(X) \to X
$$

**Combine/build things.**

```text
ingredients → meal
components → tree
numbers → result
```

versus

$$
\textbf{Coalgebra: } X \to F(X)
$$

**Observe/unfold behavior.**

```text
dog state → grooming step + remaining state
dish state → observation + next cooking state
app state → UI + possible next states
```

So, as a mnemonic: **algebra describes how things are constructed; coalgebra describes how systems behave.**


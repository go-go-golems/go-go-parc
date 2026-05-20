---
title: "DMETA Presentation UI: Building a CLIM-Style Street Deli Ordering Prototype"
aliases:
  - DMETA CLIM Street Deli Prototype
  - Hudson Street Deli Presentation UI
  - CLIM Presentation-Based Ordering UI
tags:
  - article
  - dmeta
  - design-system
  - presentation-based-ui
  - clim
  - opengenera
  - food-ordering
  - intelligent-replacement
status: active
type: article
created: 2026-05-20
repo: /home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta
related:
  - "[[ARTICLE - DMETA Meta Design System - Street Deli Core Model and Mobile Ordering App]]"
---

# DMETA Presentation UI: Building a CLIM-Style Street Deli Ordering Prototype

This article documents the second Hudson Street Deli prototype: a monochrome, Berkeley Mono, presentation-based interface inspired by CLIM and OpenGenera. The mobile prototype described in [[ARTICLE - DMETA Meta Design System - Street Deli Core Model and Mobile Ordering App]] proved that the street-deli core model could drive a polished touch interface. This prototype asks a narrower and more technical question: can the same core model drive an interface where every meaningful object is a typed presentation, every command declares the presentation types it accepts, and interaction is organized around action dispatch rather than visual controls?

The answer is yes, with important engineering constraints. The prototype works because the DMETA model already separates domain subjects, capabilities, presentations, and actions. The CLIM-style UI makes that separation visible. A menu item is not only text on the screen; it is a `<MenuItem>` presentation. An ingredient is not only a row; it is an `<Ingredient>` presentation. A replacement candidate is not only a suggestion; it is a `<Substitution>` presentation that can be supplied as an argument to the `APPLY` action.

> [!summary]
> - The CLIM prototype is the most literal implementation of DMETA's presentation-based UI idea: rendered text carries semantic type, identity, and action eligibility.
> - The same street-deli core model that produced role-colored mobile widgets also produces typed text presentations such as `<MenuItem>`, `<Ingredient>`, `<Substitution>`, and `<OrderItem>`.
> - The implementation converged on two interaction modes: normal mode (`click presentation → select → click action`) and select mode (`type action → compatible presentations turn red → click argument`).
> - The development process exposed concrete failure modes: direct-click actions were too eager, ES modules broke inline handlers, grey hint text hid command results, and a monolithic `app.js` made dispatch errors harder to reason about.

## Why this note exists

The first street-deli prototype deliberately emphasized mobile ordering: warm palette, ingredient-role colors, dietary badges, bottom sheets, cart controls, and touch affordances. That version is useful because it resembles a plausible customer-facing application.

The CLIM version is useful for a different reason. It removes most graphical design decisions and exposes the semantic machinery. There are no cards, no green substitution chips, no bottom sheets, no role-color palette, and no large touch controls. The interface is mostly text. Its hierarchy comes from type annotations, indentation, command output, and action dispatch.

That constraint makes it a good test of the DMETA model. If the model only works when wrapped in a polished mobile UI, then the model is not really presentation-based; it is tied to one rendering style. If the same model can drive a text-first command interface, then the model is doing real architectural work.

## The starting point: the street-deli core model

The street-deli system begins with the same DMETA extension described in the mobile article. The base DMETA vocabulary provides reusable archetypes such as `Actor`, `WorkItem`, `Event`, `Resource`, and `Relation`. The deli domain adds the concepts that are needed for intelligent ingredient replacement:

| Addition | Kind | Reason it exists |
|---|---|---|
| `Composition` | archetype | A menu item is assembled from parts that fill functional roles. |
| `Substitution` | archetype | A replacement rule is a first-class semantic subject with candidates, reasoning, pricing, and safety metadata. |
| `composable` | capability | A subject has parts, required roles, and optional roles. |
| `substitutable` | capability | A subject can be replaced by candidates that preserve roles and dietary constraints. |
| `configurable` | capability | A subject has options such as size, spice, or temperature. |
| `dietary` | capability | A subject carries dietary tags and allergen metadata. |

The important design decision is that ingredients are understood through functional roles. Cheese and avocado are not similar food categories, but both can fill a richness role. Bacon and smoked tofu are not the same product, but both can fill protein and umami roles. Bread and lettuce wrap are not the same ingredient category, but both can fill a structural role.

The model therefore defines `ingredient_role` as a logical type. Roles such as `structural`, `protein`, `richness`, `moisture`, `acidity`, `crunch`, `umami`, `heat`, `binding`, and `freshness` are not visual labels first. They are semantic facts used by the replacement system. A UI may render them as colored tags, as the mobile prototype does, or as plain text brackets, as the CLIM prototype does.

```yaml
composable:
  projections:
    parts:
      type: list
      required: true
    required_roles:
      type: list
      required: false
    optional_roles:
      type: list
      required: false

substitutable:
  projections:
    replaces:
      type: string
      required: true
    replacement_candidates:
      type: list
      required: true
    role_preservation:
      type: list
      required: false
    dietary_compatibility:
      type: list
      required: false
    allergen_flags:
      type: list
      required: false
    flavor_fit:
      type: string
      required: false
    price_delta_cents:
      type: integer
      required: false
    auto_suggest:
      type: boolean
      required: false
```

The CLIM prototype does not consume these YAML files directly. It uses hand-written JavaScript data that mirrors the same structure. This was a deliberate prototype choice: the objective was to prove the interaction model quickly, not to build a YAML compiler. The conceptual dependency remains clear. The fields in `js/data.js` correspond to model concepts:

| JavaScript field | Model concept |
|---|---|
| `ingredients[].roles` | `ingredient_role` logical type |
| `ingredients[].required` | composition integrity / required roles |
| `ingredients[].dietary` | `dietary` capability |
| `SUBS[ingredient].candidates[]` | `replacement_candidates` |
| `candidate.roles` | role preservation |
| `candidate.dietary` | dietary compatibility |
| `candidate.allergens` | allergen flags |
| `candidate.priceDelta` | price delta |
| `candidate.auto` | auto-suggest flag |
| `candidate.reasoning` | human-readable substitution explanation |

The code path begins with the model even though the prototype data is embedded in JavaScript.

## What presentation-based UI means here

A presentation-based UI is not just a UI that displays objects. It is a UI where rendered objects preserve enough semantic identity for actions to be discovered and executed against them. A line of text can be selected because it carries a type and an identity.

In the CLIM prototype, a rendered menu item looks like this:

```html
<span
  class="pres pres-block"
  data-type="MenuItem"
  data-id="classic-blta"
  onclick="handlePresentationClick('MenuItem','classic-blta',null,event)"
  oncontextmenu="handlePresentationContext('MenuItem','classic-blta',null,event)">
  <span class="pres-type">&lt;MenuItem&gt;</span>
  Classic BLTA
  <span class="pres-id">#classic-blta</span>
  <span class="role">$11.95</span>
</span>
```

The visible text is only one part of the presentation. The operative information is:

- `data-type="MenuItem"` declares the presentation type.
- `data-id="classic-blta"` declares the semantic identity.
- The click handler dispatches by type and id.
- The context-menu handler asks the action registry which commands accept this type.

The same pattern applies to ingredients and substitutions:

```html
<span data-type="Ingredient" data-id="cheddar">...</span>
<span data-type="RemovedIngredient" data-id="cheddar">...</span>
<span data-type="Substitution" data-id="cheddar" data-idx="0">...</span>
<span data-type="OrderItem" data-id="...">...</span>
```

The prototype treats each of these as a different argument type. A removed ingredient is not the same presentation type as an active ingredient, because different actions apply. An active `<Ingredient>` can be removed. A `<RemovedIngredient>` can be restored or used to show substitutions. A `<Substitution>` can be applied. An `<OrderItem>` can be removed from the cart, inspected, or edited.

That distinction matters because it prevents commands from becoming stringly typed. The command table can ask: does this action accept the selected presentation type? If yes, execute. If no, do not execute and tell the user what type is expected.

## The command table

The action registry is the center of the CLIM prototype. It is the prototype's command table: each action has an id, label, argument types, applicable views, description, and implementation function.

A representative subset looks like this:

```js
const ACTIONS = [
  {
    id: 'CUSTOMIZE',
    label: 'CUSTOMIZE',
    argTypes: ['MenuItem'],
    applicableTo: ['menu'],
    description: 'Open customizer for <MenuItem>. Modify ingredients, apply substitutions.',
    fn: (id) => openDetail(id),
  },
  {
    id: 'REMOVE-INGREDIENT',
    label: 'REMOVE-INGREDIENT',
    argTypes: ['Ingredient'],
    applicableTo: ['detail'],
    description: 'Remove <Ingredient> from composition. Triggers substitution search.',
    fn: (id) => removeIngredient(id),
  },
  {
    id: 'APPLY',
    label: 'APPLY',
    argTypes: ['Substitution'],
    applicableTo: ['detail'],
    description: 'Apply <Substitution> candidate to replace removed ingredient.',
    fn: (id, idx) => applySubstitution(id, idx),
  },
]
```

This table is small, but it encodes the main UI rule: actions are typed. `REMOVE-INGREDIENT` is not a general click handler. It accepts `<Ingredient>`. `APPLY` accepts `<Substitution>`. `CUSTOMIZE` accepts `<MenuItem>`. If the user types `APPLY` while looking at the menu, no menu item turns red because `APPLY` does not accept `MenuItem`.

The complete prototype action groups are:

| Group | Actions | Argument types |
|---|---|---|
| Navigation | `MENU`, `CART`, `BACK`, `HELP` | no args |
| Menu item | `CUSTOMIZE`, `ADD-TO-ORDER`, `DESCRIBE` | `<MenuItem>` |
| Ingredient | `REMOVE-INGREDIENT`, `SHOW-SUBSTITUTIONS` | `<Ingredient>` / `<RemovedIngredient>` |
| Removed/substituted ingredient | `RESTORE-INGREDIENT`, `UNDO-SUBSTITUTION`, `ALTERNATIVES` | `<RemovedIngredient>` / `<SubstitutedIngredient>` |
| Substitution | `APPLY`, `DESCRIBE` | `<Substitution>` |
| Cart | `PLACE-ORDER`, `REMOVE-FROM-CART`, `INSPECT`, `EDIT` | no args or `<OrderItem>` |
| Dietary | `FILTER-DIETARY` | no args |

The `HELP` command renders this table inside the interface. That is not only documentation; it is part of the interaction model. A user can inspect the live command vocabulary without reading source code.

## The two interaction modes

The implementation converged on two modes because a single click behavior could not satisfy both command-first and presentation-first use.

### Normal mode

Normal mode starts with a presentation. The user clicks a presented object, the system selects it, and the action bar lists commands that accept that object's type.

The flow is:

```text
click <MenuItem Classic BLTA>
  -> selected = { type: "MenuItem", id: "classic-blta" }
  -> action bar = MENU CART HELP CUSTOMIZE ADD-TO-ORDER DESCRIBE ...

click DESCRIBE
  -> dispatch DESCRIBE("classic-blta", null, "MenuItem")
  -> result line = "Classic BLTA — $11.95 — allergens: gluten, eggs — ..."
```

The code path is:

```js
function handlePresentationClick(type, id, idx, event) {
  if (state.mode === 'select') {
    executePendingActionIfCompatible(type, id, idx)
    return
  }

  selectPresentation(event.currentTarget, type, id, idx)
}

function selectPresentation(el, type, id, idx) {
  state.selected = { type, id, idx }
  el.classList.add('selected')
  showActionsFor(type, id, idx)
}

function showActionsFor(type, id, idx) {
  actions = getActionsForType(type, state.view)
  renderActionBar(actions)
}
```

This path is useful when the user sees an object and wants to know what can be done with it. It is the direct presentation-first path.

### Select mode

Select mode starts with a command. The user types an action name into the command line. If the action takes arguments, the system enters select mode. All compatible presentations turn red. The next click on a red presentation supplies the argument and executes the command.

The flow is:

```text
type DESCRIBE + Enter
  -> pendingAction = DESCRIBE
  -> action arg types = [MenuItem, Ingredient, Substitution, OrderItem]
  -> compatible presentations become red

click <MenuItem Grilled Cheese>
  -> dispatch DESCRIBE("grilled-cheese", null, "MenuItem")
  -> leave select mode
  -> result line = "Grilled Cheese — $8.95 — vegetarian — allergens: gluten, dairy — ..."
```

The core code is:

```js
function executeCommand(cmd) {
  const action = ACTIONS.find(a => a.id === normalize(cmd))

  if (!action) return unknownCommand(cmd)

  if (action.argTypes.length === 0) {
    action.fn()
    return
  }

  enterSelectMode(action)
}

function enterSelectMode(action) {
  state.mode = 'select'
  state.pendingAction = action

  for (const el of document.querySelectorAll('.pres')) {
    if (action.argTypes.includes(el.dataset.type)) {
      el.classList.add('selectable')
    } else {
      el.classList.add('select-disabled')
    }
  }
}

function executePendingAction(type, id, idx) {
  const action = state.pendingAction

  if (!action.argTypes.includes(type)) {
    setHint(`Need <${action.argTypes.join('> or <')}>`)
    return
  }

  action.fn(id, idx, type)
  exitSelectMode()
}
```

This path is useful when the user already knows the command and wants to supply an argument from visible presentations. It is the command-first path.

The two modes are not two separate applications. They share the same command table and the same action implementations. The only difference is the order in which the user supplies the command and the argument.

## How the CLIM prototype derives from the same model as the mobile prototype

The mobile prototype turns semantic facts into touch widgets. The CLIM prototype turns the same facts into typed text. The important point is that both are projections of the same source concepts.

| Core model concept | Mobile rendering | CLIM rendering |
|---|---|---|
| `MenuItem` / `Composition` | Card with price, description, role-colored ingredients | `<MenuItem>` line with id and price |
| `Ingredient` / `Resource` | Ingredient row with role tags and dietary badges | `<Ingredient>` line with bracketed roles |
| `Substitution` | Suggestion chip or candidate card | `<Substitution>` text block with reasoning |
| `dietary` capability | Colored dietary badges | Plain dietary text in result/description |
| `substitutable` capability | Bottom-sheet candidate list | Action-enabled substitution presentations |
| `Action` | Buttons, chips, swipe actions | Command table entries and context menu items |

The mobile UI hides some of the type machinery because touch interfaces need larger targets and immediate affordances. The CLIM UI exposes the type machinery because typed command dispatch is the main interaction. Neither is more faithful to the model in an absolute sense. They emphasize different parts of the model.

The mobile UI asks: can a customer order a sandwich quickly and safely?

The CLIM UI asks: can a typed presentation system make all action eligibility explicit?

Both rely on the same facts:

- A menu item has ingredients.
- Ingredients have roles.
- Removed ingredients have unfilled roles.
- Substitutions fill roles.
- Actions accept typed semantic subjects.

## The implementation shape

The CLIM prototype is served from:

```text
/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/examples/street-deli-ordering/prototype-clim/
```

The current source layout is:

```text
prototype-clim/
  index.html              # Shell: views, command line, action-result area
  styles.css              # Berkeley Mono, monochrome layout, select-mode red targets
  app.js                  # 3-line module entrypoint
  js/
    data.js               # MENU, SUBS, resolveSubKey()
    app-main.js           # Action registry, state machine, renderers, command dispatch
  fonts/
    BerkeleyMono-Regular.woff2
    BerkeleyMono-Bold.woff2
    BerkeleyMono-Oblique.woff2
```

The served copy is synchronized into:

```text
examples/street-deli-ordering/www/clim/
```

The server root is:

```text
examples/street-deli-ordering/www/
```

That root also contains the mobile prototype at `/mobile/`, so one static server can expose both versions:

```text
http://localhost:8770/mobile/
http://localhost:8770/clim/
```

### `index.html`: the application frame

The HTML shell is intentionally small. It defines view containers and a command-line footer. The most important late addition is the action-result area above the command prompt:

```html
<footer id="command-line">
  <div id="action-result" class="action-result">Ready.</div>
  <div class="cmd-input-area">
    <span class="prompt">Command:&nbsp;</span>
    <span class="cmd-buffer" id="cmd-buffer"></span>
    <span class="cmd-cursor">_</span>
  </div>
  <div class="cmd-hint" id="cmd-hint">...</div>
</footer>
```

This separation matters. `#action-result` is white and persistent. It is where command output goes. `#cmd-hint` is grey and advisory. It tells the user what to do next. Earlier versions put everything in the grey hint line, which made successful command output look like low-priority help text.

### `styles.css`: monochrome with one intentional exception

The requested visual rule was strict: monochrome black and white, single font size, Berkeley Mono. The implementation uses black background, grey body text, bright white for important text, and Berkeley Mono at a single root size. There is one intentional color exception: select mode uses red to mark compatible presentations.

```css
.pres.selectable {
  color: #ff4444;
  cursor: crosshair;
  border-bottom-color: transparent;
}

.pres.selectable:hover {
  background: transparent;
  border-bottom: 1px solid var(--fg);
}

.action-result {
  color: var(--fg-bright);
  border-bottom: 1px solid var(--border);
  padding: 0 0 4px;
  margin: 0 0 4px;
  min-height: 1.5em;
  white-space: pre-wrap;
}
```

The red select state is not a decorative theme color. It is a mode indicator. It tells the user which presentations can be supplied as arguments to the pending action. In normal mode the UI remains monochrome.

The hover behavior was adjusted during development. Selectable presentations should not be persistently underlined just because select mode is active. The persistent indication is red foreground. Hover can still use the normal underline behavior because hover means "the pointer is currently over this presentation," not "this is a valid argument."

### `js/data.js`: the prototype data source

The data module contains `MENU`, `SUBS`, and `resolveSubKey()`. It is deliberately separate from the CLIM state machine so that the data model is visible on its own.

`MENU` contains 11 items across bagels, sandwiches, and breakfast. Each item has ingredient roles and dietary metadata. `SUBS` maps ingredient ids to replacement candidate lists. Candidate objects carry the same fields that the core model expects: roles, dietary tags, allergens, flavor fit, price delta, auto flag, and reasoning.

The alias resolver is still important in the CLIM version:

```js
export function resolveSubKey(id) {
  if (SUBS[id] && SUBS[id] !== null) return id

  const base = id.replace(/-\d+$/, '')
  if (SUBS[base] && SUBS[base] !== null) return base

  // fall back to name matching across menu ingredients
}
```

Multiple menu items contain bacon, cheese, bread, or mayo under distinct ingredient ids. The resolver lets the prototype author substitution rules once and reuse them across item-specific ids.

### `js/app-main.js`: state, rendering, and dispatch

The main module currently contains the action registry, state machine, renderer functions, command line handling, context menu, and action implementations. It is still large, but it is no longer mixed with menu and substitution data.

The state is compact:

```js
const state = {
  view: 'menu',
  mode: 'normal',
  selected: null,
  pendingAction: null,
  customizing: null,
  cart: [],
  orderNum: 0,
  cmdBuffer: '',
  cmdHistory: [],
  contextMenu: null,
}
```

Each field exists for a specific part of the interaction model:

| Field | Responsibility |
|---|---|
| `view` | Which view is active: menu, detail, cart, tracker, help. |
| `mode` | Whether the UI is in normal mode or select mode. |
| `selected` | The presentation selected in normal mode. |
| `pendingAction` | The action waiting for an argument in select mode. |
| `customizing` | The current menu item composition being edited. |
| `cart` | The order items accumulated so far. |
| `cmdBuffer` | The typed command line buffer. |
| `contextMenu` | The active right-click menu element. |

The state model is small enough to audit manually. That is valuable for a prototype whose purpose is to teach interaction semantics.

## The replacement flow in the CLIM interface

The replacement flow uses the same ingredient roles and substitution candidates as the mobile prototype, but it renders them as command-addressable text.

A typical flow is:

```text
click <MenuItem Grilled Cheese>
click CUSTOMIZE
click <Ingredient Cheddar Cheese>
click REMOVE-INGREDIENT

Result:
  Cheddar Cheese is struck through.
  Unfilled roles: protein, richness, umami.
  Replacement candidates appear as <Substitution> presentations.

click <Substitution ★auto Avocado>
click APPLY

Result:
  Applied substitution: Cheddar Cheese → Avocado.
```

The same flow can be executed command-first:

```text
type CUSTOMIZE
click red <MenuItem Grilled Cheese>

type REMOVE-INGREDIENT
click red <Ingredient Cheddar Cheese>

type APPLY
click red <Substitution ★auto Avocado>
```

This command-first path is the most important feature of the CLIM version. It shows that the UI can invert the normal visual-control order. The user does not need to find a remove button near an ingredient. The user can name the command first, then choose a compatible object from the visible presentations.

The implementation does not perform a general search over hidden objects. Select mode only marks currently rendered presentations. That is the right constraint for this prototype. The point is not to implement a full object store; the point is to show that visible semantic presentations can serve as typed command arguments.

## Action output and guidance output

The late addition of `#action-result` fixed an important usability issue. The prototype now distinguishes command output from guidance.

```text
[action-result]
Grilled Cheese — $8.95 — vegetarian — allergens: gluten, dairy — Sourdough Bread, Cheddar Cheese, American Cheese, Butter

Command: _
Action result shown above.
```

This distinction should remain in future versions:

- `action-result` is for results of commands: descriptions, substitution applied messages, cart changes, order numbers.
- `cmd-hint` is for instructions: "click a red `<MenuItem>`", "ESC cancels select mode", "SHOW-SUBSTITUTIONS or RESTORE-INGREDIENT".

Without this separation, the interface loses clarity. A command-line interface must make it clear when the system has done work and when it is merely suggesting the next step.

## Development process and early errors

The CLIM prototype went through several corrections. These corrections are worth recording because they are common when building presentation-based interfaces.

### Error 1: direct-click actions were too eager

The first CLIM version clicked a presentation and immediately performed a default action. Clicking a `<MenuItem>` opened the customizer. Clicking an `<Ingredient>` removed it. Clicking a `<Substitution>` applied it.

That behavior is useful in a mobile prototype, but it is not the interaction model requested here. In a CLIM-style UI, normal clicking should select the presentation and expose available commands. Execution should happen when the user chooses a command.

The fix was to split interaction into normal mode and select mode. Normal mode selects; select mode supplies command arguments. This made command dispatch explicit.

### Error 2: action-first selection needed red compatible targets

The next iteration added command-first selection but did not make target compatibility clear enough. The clarified requirement was precise:

```text
select an ACTION (say type DESCRIBE in the console)
switch into select mode: all menu items turn red
click a menu item X: execute DESCRIBE X

click on X (in normal mode)
show actions that take a menu item
click DESCRIBE: execute DESCRIBE X
```

This requirement led to `enterSelectMode(action)`, which adds `.selectable` to compatible presentation nodes and `.select-disabled` to incompatible ones.

```js
function enterSelectMode(action) {
  state.mode = 'select'
  state.pendingAction = action

  for (const el of document.querySelectorAll('.pres')) {
    const pType = el.dataset.type
    if (action.argTypes.includes(pType)) {
      el.classList.add('selectable')
    } else {
      el.classList.add('select-disabled')
    }
  }
}
```

The resulting behavior is simple to inspect. If the user types `DESCRIBE`, every visible presentation type accepted by `DESCRIBE` becomes red. On the menu view, that means all 11 menu items. If the user types `REMOVE-INGREDIENT` in the customizer, active ingredient presentations become red. If the user types `APPLY` while substitutions are visible, substitution candidates become red.

### Error 3: module conversion broke inline handlers

After splitting the JavaScript into modules, the browser threw this error:

```text
Uncaught ReferenceError: handlePresentationClick is not defined
    onclick http://localhost:8770/clim/index.html:1
```

The cause was specific and important. The renderer still produced inline event attributes:

```html
onclick="handlePresentationClick('MenuItem','classic-blta',null,event)"
```

Before the module split, top-level functions were globals. After changing `app.js` to `type="module"`, top-level functions became module-scoped. Inline event attributes evaluate against `window`, so they could not see `handlePresentationClick`.

The short-term fix was explicit exposure:

```js
function exposeInlineHandlers() {
  Object.assign(window, {
    addToCart,
    closeContextMenu,
    executeActionFromBar,
    filterCategory,
    filterDietary,
    handlePresentationClick,
    handlePresentationContext,
    placeOrder,
    renderCart,
    renderHelp,
    renderMenu,
  })
}

export function init() {
  exposeInlineHandlers()
  renderMenu()
}
```

This is not the final architecture I would choose for a production implementation. A cleaner version would remove inline handlers and use delegated event listeners on the presentation container. The short-term fix was acceptable because it restored the prototype without undoing the module split.

The lesson is direct: syntax checks do not catch this class of browser error. `node --check` validates JavaScript syntax. It does not validate that inline HTML event attributes can resolve module-scoped functions.

### Error 4: command output was hidden in hint text

Earlier versions wrote command results into the grey hint line. That made successful execution hard to distinguish from guidance. The fix was a separate white action-result area above the command prompt.

This change is small in code and large in interaction clarity. It gives the interface three text layers:

| Layer | Color | Purpose |
|---|---|---|
| Presentation area | grey/white | Objects and data visible in the current view. |
| Action result | white | Output from the last command. |
| Command hint | grey | Instructions about the next possible operation. |

A presentation-based command UI needs this separation because selection and execution are separate steps. The user must be able to tell whether an action has happened.

### Error 5: the first `app.js` was too monolithic

The first CLIM implementation placed data, substitution rules, action registry, renderers, command line handling, context menu logic, and action implementations into one file. That worked for the first pass but made later changes risky.

The current split is minimal:

```text
app.js          # imports init and calls it
js/data.js      # MENU, SUBS, resolveSubKey
js/app-main.js  # behavior and rendering
```

This is not the final decomposition. `js/app-main.js` is still 852 lines. A future split should separate:

```text
js/actions.js       # ACTIONS registry and command dispatch
js/state.js         # state object and mode transitions
js/render-menu.js   # menu renderer
js/render-detail.js # customizer renderer
js/render-cart.js   # cart/tracker/help renderers
js/context-menu.js  # right-click menu
js/commands.js      # command-line input handling
```

The current split was enough to separate data from behavior and make the entrypoint explicit.

## The current tested behavior

After fixing the module-scope handler issue, I reran the CLIM prototype in the browser at:

```text
http://127.0.0.1:8770/clim/
```

I verified the following flows:

### Presentation-first flow

```text
click <MenuItem Classic BLTA>
  -> selected = true
  -> action bar includes CUSTOMIZE, ADD-TO-ORDER, DESCRIBE

click DESCRIBE
  -> action-result = "Classic BLTA — $11.95 — no dietary tags — allergens: gluten, eggs — ..."
  -> no console errors
```

### Command-first flow

```text
type DESCRIBE + Enter
  -> mode label = "MENU ▸ DESCRIBE"
  -> 11 menu items have .selectable
  -> hint asks user to click compatible presentation

click <MenuItem Grilled Cheese>
  -> leaves select mode
  -> red target count = 0
  -> action-result = "Grilled Cheese — $8.95 — vegetarian — allergens: gluten, dairy — ..."
  -> no console errors
```

These checks are not a full test suite, but they validate the two interaction paths that define the prototype.

## What the CLIM version teaches about DMETA

The CLIM prototype clarifies several properties of DMETA that are less visible in the mobile version.

### Presentations are not widgets

In the mobile prototype, it is easy to confuse a presentation with a widget. A SubstitutionChip looks like a presentation because it is visible and interactive. In the CLIM prototype, the distinction is clearer. A `<Substitution>` presentation can be rendered as a single line of text and still be a valid argument to `APPLY`. The presentation is the semantic contract; the widget is one possible renderer.

### Actions should declare accepted presentation types

The command table makes action eligibility explicit. `REMOVE-INGREDIENT` accepts `<Ingredient>`. `APPLY` accepts `<Substitution>`. `REMOVE-FROM-CART` accepts `<OrderItem>`. This is the same idea as the DMETA `actions` section in `presentations.yaml`, but implemented directly in JavaScript.

A production system could generate part of the action registry from YAML. The prototype does not do that yet, but the shape is aligned:

```yaml
actions:
  apply_substitution:
    accepts:
      - capability: substitutable
    arguments:
      substitution:
        mode: selected_presentation
        accepts:
          - capability: substitutable
```

The JavaScript equivalent is:

```js
{
  id: 'APPLY',
  argTypes: ['Substitution'],
  fn: (id, idx) => applySubstitution(id, idx),
}
```

The YAML version uses capabilities and presentations; the prototype uses direct presentation types. That is a reasonable simplification for a hand-written prototype.

### Argument selection is a first-class UI state

Select mode is not a popup and not a modal. It is a UI state in which visible presentations are filtered by type. Red targets are not merely highlighted; they are the valid argument set for the pending command.

This state is useful because it makes type constraints visible. If `APPLY` is pending, menu items do not turn red. If `DESCRIBE` is pending, menu items do turn red. If `REMOVE-INGREDIENT` is pending, only ingredients in the customizer turn red.

A generated DMETA UI could use the same rule:

```text
pending action accepts capability X
  -> find rendered presentations carrying capability X
  -> mark them as argument candidates
  -> click candidate supplies PresentationRef
```

The CLIM prototype implements the simpler presentation-type version of this rule.

### The action-result area is part of the command model

Command interfaces need an output channel. If actions are functions, then users need to see the function result. In the current prototype, the output channel is `#action-result`. It is intentionally placed above `Command:` so it reads as the result of the previous command, not as helper text for the next command.

This pattern should carry forward into any richer presentation-based UI. A detail drawer, toast, status line, or transcript can all serve as result channels, but the system needs an explicit result channel.

## Working rules for future CLIM-style DMETA prototypes

The following rules should guide the next iteration:

- A normal click selects a presentation. It should not execute a domain action by default.
- An action click executes against the selected presentation if the action accepts that presentation type.
- Typing an action name enters select mode when the action requires an argument.
- Select mode marks compatible presentations in red and leaves incompatible presentations unavailable.
- Command output must go to a visible result area, not to low-priority hint text.
- Inline handlers and ES modules should not be mixed unless handlers are explicitly exported to `window`.
- The action registry should be the single source of truth for action labels, accepted argument types, and descriptions.
- The context menu and action bar should both read from the same action registry.
- The HELP view should be generated from the action registry, not manually duplicated.
- Data should stay separate from dispatch logic, even in a prototype.

## Open questions

The current prototype is good enough to test the interaction model, but several questions remain.

**Should rendered presentations use delegated event handling instead of inline attributes?** The module-scope bug strongly suggests yes. Delegated handlers would reduce global exposure and make the renderer safer.

**Should the action registry be generated from `core-model/presentations.yaml`?** The hand-written registry is aligned with the YAML concepts, but generation would prove the DMETA toolchain more directly.

**Should select mode use capabilities rather than presentation types?** Today `DESCRIBE` accepts direct presentation types such as `MenuItem` and `Ingredient`. A more faithful DMETA implementation would accept capabilities such as `inspectable` or `substitutable` and derive eligible presentations from runtime metadata.

**Should action output become a transcript?** A single result line is enough for the prototype. A richer CLIM-style interface would likely keep a command transcript so users can inspect prior actions and results.

**Should the served `www/` tree be generated?** The repository currently contains both source prototypes and a copied served tree. This is convenient for manual testing but risks drift. A small script could rebuild `www/` from `prototype/` and `prototype-clim/`.

## Related files

The key implementation files are:

```text
/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/examples/street-deli-ordering/prototype-clim/index.html
/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/examples/street-deli-ordering/prototype-clim/styles.css
/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/examples/street-deli-ordering/prototype-clim/app.js
/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/examples/street-deli-ordering/prototype-clim/js/data.js
/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/examples/street-deli-ordering/prototype-clim/js/app-main.js
```

The core model files that explain why the prototype has these presentation types are:

```text
/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/examples/street-deli-ordering/core-model/archetypes.yaml
/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/examples/street-deli-ordering/core-model/capabilities.yaml
/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/examples/street-deli-ordering/core-model/presentations.yaml
/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/examples/street-deli-ordering/core-model/street-deli-ordering.yaml
```

The implementation diary is:

```text
/home/manuel/workspaces/2026-05-19/dmeta-dsl/dmeta/ttmp/2026/05/20/STREET-DELI-001--street-deli-mobile-ordering-meta-design-system/reference/01-diary.md
```

## Closing

The CLIM prototype is valuable because it removes most visual design and leaves the semantic system exposed. The result is not a replacement for the mobile prototype. It is a second projection of the same model. The mobile version proves the model can support a customer-facing ordering flow. The CLIM version proves the model can support typed presentation selection, action discovery, command-first argument collection, and context menus.

That combination is the stronger result. A model that can produce only one UI is a design for that UI. A model that can produce a mobile touch interface and a text-first presentation command interface is closer to a reusable design-system factory.

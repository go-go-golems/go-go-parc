# JS API Design Concepts

- URL: https://chatgpt.com/c/6a7f2cac-d748-83ea-b5a1-05b9937e9ee5
- Created: 2026-08-14T14:56:47.088Z

---

> If you were to design a JS API / DSL inspired by this paper, what would you design (it can even be multiple):

I’d translate the paper into three layers: a reactive **object-schema runtime**, an **affordance/planning DSL**, and a **grounded reference/language DSL**. The key is that “objects” stay live views over concurrent processes and expectations, not inert records.

The paper’s most interesting idea, translated into software terms, is **not “represent an object as a record.”** It is closer to:

> An object is a stable coordination handle around a changing bundle of processes, observations, histories, expectations, and possible actions.

That follows directly from the paper’s object schemas: concurrent interaction processes are grouped by the physical object they target, and those schemas become the bridge between continuous perception/action and discrete planning/language. fileciteturn0file0L79-L103 The paper goes even further and argues that, from the robot’s perspective, the “object” can be understood as the related processes and expected outcomes rather than as an independently fundamental representation. fileciteturn0file0L393-L431

I’d probably build **three related JS APIs**.

---

## 1. `schemas`: an object-centric reactive runtime

This would be the lowest-level and most faithful translation.

The central abstraction isn't an ECS entity or mutable JS object. It's a **live schema**:

```js
const apple = world.schema("apple-17");
```

A schema acquires meaning by attaching processes to it:

```js
apple.attach(
  process("vision.track", {
    run: trackVisualRegion,
  })
);

apple.attach(
  process("vision.toArmPose", {
    reads: ["vision.track"],
    run: projectCameraPoseToArmSpace,
  })
);

apple.attach(
  process("color.classify", {
    reads: ["vision.track"],
    run: classifyColor,
  })
);

apple.attach(
  process("grasp", {
    requires: ["arm", "hand"],
    run: graspObject,
  })
);
```

Each process writes an **interaction history**, rather than just overwriting some global state:

```js
apple.history("vision.track")
// [
//   { t: 1002, position: [120, 80], confidence: .93 },
//   { t: 1018, position: [123, 81], confidence: .91 },
//   ...
// ]

apple.latest("vision.track.position");
```

That closely mirrors the paper's interaction-process model: processes run concurrently, read histories, perform work, and write their own histories. The schema consists of the processes, history, and expectations associated with a target object. fileciteturn0file0L299-L318

### Processes would be first-class

I'd make the major process categories from the paper explicit:

```js
sensor(...)
action(...)
condition(...)
plan(...)
translate(...)
coordinate(...)
reference(...)
```

For example:

```js
apple.attach(
  sensor("pose2d", async function* ({ camera, signal }) {
    for await (const frame of camera.frames({ signal })) {
      yield findRegion(frame);
    }
  })
);

apple.attach(
  translate("pose3d", {
    from: "pose2d",
    compute: pose2d => cameraToRobot(pose2d),
  })
);
```

A process could simply be an `AsyncIterable` internally:

```ts
interface Process<T> {
  kind: string;
  target?: SchemaRef;
  start(ctx: ProcessContext): AsyncIterable<T>;
}
```

This maps unusually well to JavaScript.

---

## Schema state should be beliefs, not plain properties

Instead of:

```js
apple.color === "red"
```

I'd expose:

```js
apple.belief("color")
```

returning something like:

```js
{
  value: "red",
  confidence: 0.94,
  source: "color.classify",
  observedAt: 1755183492000
}
```

You could conveniently write:

```js
apple.value("color");      // "red"
apple.confidence("color"); // 0.94
```

but the uncertainty shouldn't disappear from the underlying model.

That's important because the paper explicitly describes schemas as bundles of beliefs that are *probably* about real physical objects, including cases where noise creates spurious object schemas. fileciteturn0file0L375-L392

---

## Object identity becomes reconciliation

This is where the DSL gets interesting.

Imagine vision says an object is here:

```js
visionSchema
```

while touch says the grasped object is somewhere else:

```js
touchSchema
```

Don't hide that conflict inside a giant perception subsystem.

Make coordination itself a process:

```js
apple.coordinate(
  reconcile({
    sources: ["vision.track", "grasp.track"],

    inconsistent(a, b) {
      return distance(a.position, b.position) > 0.15;
    },

    resolve({ weaker }) {
      return detach(weaker);
    }
  })
);
```

Or:

```js
world.identity({
  compatible(a, b) {
    return (
      colorDistance(a, b) < 0.1 &&
      shapeDistance(a, b) < 0.2
    );
  },

  onConflict: "split",
  onMatch: "merge",
});
```

That's directly inspired by the paper's coordination processes, which can detach a process when visual and touch tracking disagree, allowing it to attach to another schema or create a new one. fileciteturn0file0L347-L359

This could be a genuinely useful library outside robotics: distributed systems, UI agents, game AI, browser automation, multi-source entity resolution, etc.

---

# 2. `afford`: an affordance-oriented planning DSL

The second package would abstract away much of the process plumbing.

Rather than saying:

> Object X has method `lift()`.

You say:

> There is currently evidence that X affords lifting, with some expected outcome distribution.

For example:

```js
const lift = affordance("lift", {
  requires: object => [
    object.belief("pose3d"),
    object.belief("graspable"),
  ],

  resources: ["arm", "hand"],

  execute: async ({ object, arm, hand, signal }) => {
    await arm.moveTo(object.value("pose3d"), { signal });
    await hand.close({ signal });
    await arm.raise({ signal });
  }
});
```

Then:

```js
apple.affords(lift);
```

could return:

```js
{
  possible: true,
  expectedSuccess: 0.67
}
```

rather than a boolean.

---

## Outcome statistics should be built into the DSL

One of the nicest ideas in the paper is that object attributes aren't merely descriptive labels. They become predictors of action outcomes: e.g. repeated experience may teach the system that `heavy` predicts poor lifting success. fileciteturn0file0L443-L473

I'd make that first-class:

```js
const lift = affordance("lift", {
  learnOutcomeFrom: [
    "weight",
    "shape",
    "size",
    "material"
  ],

  // ...
});
```

After executions:

```js
await lift(apple);
```

the runtime automatically records:

```js
{
  action: "lift",
  features: {
    weight: "heavy",
    shape: "round"
  },
  outcome: "failure"
}
```

Then:

```js
world.predict(lift, apple)
// {
//   success: 0.31,
//   evidence: 14
// }
```

For an initial implementation I'd avoid ML entirely. A Beta-Bernoulli model or even simple success/failure counts by feature bucket would reproduce the paper's conceptual model surprisingly well.

Later you could swap in:

```js
world.outcomes.use(myClassifier);
```

without changing the planning DSL.

---

# 3. `goal`: a continuously replanning goal DSL

I would strongly resist a traditional:

```js
const plan = planner.makePlan(worldState);
await planner.execute(plan);
```

because that loses a central point of the paper.

Instead:

```js
await agent.achieve(
  grouped(greenBlock, redApple)
);
```

`grouped()` is a **continuously monitored condition**.

```js
const grouped = condition(
  "grouped",
  (a, b) => distance(a.pose, b.pose) < 0.1
);
```

And you declare ways of making it true:

```js
grouped.satisfyWith(
  plan("move-first", (a, b) =>
    sequence(
      goal(holding(a)),
      move(a, near(b)),
      release(a)
    )
  ),

  plan("move-second", (a, b) =>
    sequence(
      goal(holding(b)),
      move(b, near(a)),
      release(b)
    )
  )
);
```

Now:

```js
await agent.achieve(grouped(apple, block));
```

might initially choose:

```text
lift apple
move apple near block
```

because:

```text
P(success | apple) = .83
P(success | block) = .72
```

Then somebody says:

```js
apple.assert({ weight: "heavy" });
```

which changes the learned expectation:

```text
P(lift apple | heavy) = .34
```

and the running goal **automatically switches plans**:

```text
cancel lifting apple
lift block
move block near apple
```

That's almost exactly the interaction the paper uses to demonstrate its architecture: adding the `heavy` attribute immediately changes predicted manipulation success and causes the planner to revise the active plan. fileciteturn0file0L226-L264

---

## Dependency tracking makes replanning elegant

Internally, I'd make conditions reactive:

```js
const canLiftApple = computed(() =>
  probability(lift, apple)
);
```

A plan keeps track of which beliefs its score/preconditions depend on.

So if:

```js
apple.belief("weight")
```

changes, only affected plan branches become dirty.

Conceptually:

```js
goal(grouped(a, b))
  .option(move(a, near(b)))
  .option(move(b, near(a)))
  .choose(maxExpectedSuccess)
  .replanOnDependencyChange();
```

A compact DSL could look like:

```js
defineGoal("grouped", ({ a, b }) => ({
  satisfied: () => near(a, b),

  strategies: [
    () => move(a, near(b)),
    () => move(b, near(a)),
  ],

  choose: maxBy(expectedSuccess),
}));
```

---

# 4. Resource arbitration should be part of planning

The paper distinguishes processes that can happily run concurrently from **resource-bound processes** competing for things like the arm, and gives higher-priority collision avoidance precedence over verbal tasks. fileciteturn0file0L366-L374

I'd expose this explicitly:

```js
world.resource("arm", {
  mode: "exclusive",
  preemptible: true,
});
```

Actions declare:

```js
action("reach", {
  resources: ["arm"],
  priority: priority.social,
  run: ...
});

action("avoidCollision", {
  resources: ["arm"],
  priority: priority.safety,
  run: ...
});
```

So:

```text
reach(redBall)
```

can be running and then:

```text
collision!
```

causes:

```text
suspend/cancel reach
run avoidCollision
re-evaluate pose
replan reach
```

Using JS's `AbortController` would make this unusually natural:

```js
action("reach", async ({ arm, target, signal }) => {
  await arm.moveTo(target.pose(), { signal });
});
```

Preemption means aborting the lower-priority action's signal.

---

# 5. `ref`: live object references rather than queries

I'd make a separate little reference DSL.

A conventional query is:

```js
const ball = world.objects.find(
  x => x.color === "red" && x.shape === "ball"
);
```

But that's too static.

The paper's reference process actively searches schemas for an object matching linguistic attributes. fileciteturn0file0L537-L553

So:

```js
const ball = ref({
  color: "red",
  shape: "ball",
  cardinality: 1,
  definite: true,
});
```

or:

```js
const ball = ref.and(
  attr("color", "red"),
  attr("shape", "ball")
);
```

And importantly, `ball` is not necessarily an object:

```ts
type Ref<T> = LiveResolution<T>;
```

You can inspect it:

```js
ball.current()
ball.candidates()
ball.confidence()
ball.status
```

For ambiguity:

```js
ball.candidates()
// [
//   [schema17, .72],
//   [schema28, .24]
// ]
```

And it keeps resolving as the world changes.

That means you can do:

```js
await agent.achieve(
  holding(ref`the red ball`)
);
```

without collapsing the reference too early.

---

# 6. A tagged-template language DSL could be fun

I'd probably make this an optional package, not the core.

```js
const redBall = world.ref`the red ball`;

await agent.do`
  pick up ${redBall}
`;
```

But the more interesting direction would be declarative lexical grounding:

```js
language.adjective("red", {
  reference: x => x.belief("color").matches("red"),
});

language.adjective("heavy", {
  assertion: x => x.assert("weight", "heavy"),
});

language.verb("pick up", {
  directive: x => goal(holding(x)),
});
```

Then:

```js
agent.hear("Pick up the red ball.");
```

roughly lowers into:

```js
agent.achieve(
  holding(
    ref({
      color: "red",
      shape: "ball"
    })
  )
);
```

While:

```js
agent.hear("The red ball is heavy.");
```

lowers into:

```js
ref({ color: "red", shape: "ball" })
  .resolve()
  .then(ball => ball.assert("weight", "heavy"));
```

This corresponds closely to the paper's distinction between **descriptive**, **directive**, and **corrective** inputs. fileciteturn0file0L520-L568

---

# 7. Corrections could be modeled as plan patches

This might be my favorite API feature.

Suppose:

```js
const task = agent.achieve(
  move(block, leftOf(ball))
);
```

Then:

```js
task.correct({
  destination: rightOf(ball)
});
```

or even:

```js
agent.correctLast(
  replace(leftOf(ball), rightOf(ball))
);
```

The important thing is that correction doesn't create an unrelated new task. It **mutates the intention**, invalidates the relevant branch, and lets the planner reconcile its currently executing actions.

So:

```js
const task = agent.do(move(block, leftOf(ball)));

task.patch(intent =>
  intent.replace(leftOf(ball), rightOf(ball))
);
```

This directly captures the paper's examples like “Move the yellow block to the left … No, to the right,” where execution is interrupted and revised. fileciteturn0file0L611-L630

---

# 8. Put together, the top-level API might be surprisingly small

Something along these lines:

```js
import {
  createWorld,
  sensor,
  translate,
  action,
  condition,
  affordance,
  goal,
  ref,
} from "@schema/runtime";

const world = createWorld();

world.resource("arm", {
  exclusive: true,
  preemptible: true,
});

const apple = world.schema();

apple.attach(
  sensor("vision", trackApple)
);

apple.attach(
  translate("pose", {
    from: "vision",
    compute: toRobotCoordinates,
  })
);

apple.define("weight", {
  source: "language",
});

const lift = affordance("lift", {
  resources: ["arm"],
  learnFrom: ["weight", "shape", "size"],

  async execute({ target, resources, signal }) {
    await resources.arm.grasp(target.value("pose"), { signal });
    await resources.arm.raise({ signal });
  }
});

const holding = condition("holding",
  obj => obj.latest("grasp")?.success === true
);

holding.satisfyWith(
  goal(obj => lift(obj))
);

const grouped = condition("grouped",
  (a, b) => near(a.value("pose"), b.value("pose"))
);

grouped.satisfyWith(
  goal((a, b) => move(a, near(b))),
  goal((a, b) => move(b, near(a))),
);
```

And application code becomes almost trivial:

```js
const greenBlock = ref({
  color: "green",
  shape: "block",
});

const redApple = ref({
  color: "red",
  kind: "apple",
});

const task = agent.achieve(
  grouped(greenBlock, redApple)
);
```

Then later:

```js
redApple.resolve().assert({
  weight: "heavy"
});
```

No explicit:

```js
task.cancel();
planner.rebuild();
task.restart();
```

The change to the object schema itself should be enough to propagate through expectations → strategy score → plan tree → resource allocation.

**That propagation is the DSL's central promise.**

---

## The architecture I'd use underneath

I'd probably make the implementation look roughly like:

```text
                    ┌─────────────┐
                    │    Goals    │
                    │ / Planner   │
                    └──────┬──────┘
                           │
             depends on / scores
                           │
       ┌───────────────────▼──────────────────┐
       │             Object Schema             │
       │                                      │
       │ histories     beliefs   expectations │
       │     ▲            ▲           ▲       │
       │     │            │           │       │
       │ processes ───────┴───────────┘       │
       └─────┬───────────────────────┬────────┘
             │                       │
       observations                actions
             │                       │
       ┌─────▼─────┐          ┌──────▼──────┐
       │ Sensors / │          │ Resources / │
       │ external  │          │ effectors   │
       └───────────┘          └─────────────┘
```

The object schema therefore isn't really a database entity.

It's closer to a cross between:

- an **actor**,
- a **reactive signal graph**,
- an **event-sourced aggregate**,
- an **entity-resolution hypothesis**,
- and a bundle of **capabilities/affordances**.

That's a fairly unusual combination.

---

## One design choice I'd be strict about

I would **not** let this become:

```js
object = {
  color: "red",
  position: ...,
  graspable: true
};
```

because then almost everything distinctive about the paper disappears.

Instead:

```js
object.belief("color")
object.history("position")
object.expect(lift)
object.processes()
```

And preferably:

```js
object.affords(lift)
```

means:

> “Given the processes, current evidence, learned histories, and available resources, what is our present expectation of performing `lift` on this schema?”

not:

> “Read the `liftable` boolean.”

The authors explicitly connect affordance terms such as “liftable” and “graspable” to the processes and expected results associated with the schema. fileciteturn0file0L432-L442

---

## If I were actually turning this into npm packages

I'd split it:

```text
@objectschema/core
  Schema
  Process
  History
  Belief
  Signal
  identity/reconciliation

@objectschema/afford
  Affordance
  ExpectationModel
  OutcomeHistory

@objectschema/plan
  Goal
  Condition
  Strategy
  Scheduler
  Resource
  Priority
  preemption/replanning

@objectschema/ref
  Ref
  live matching
  ambiguity/confidence

@objectschema/language
  lexicon
  assertion/directive/correction lowering
```

Of those, **`@objectschema/core` + `@objectschema/plan` is the design I think has the most legs**. It wouldn't need to be a robotics library at all.

You could use exactly the same architecture for browser agents:

```js
const submitButton = ref({
  role: "button",
  label: "Submit"
});

submitButton.attach(
  sensor("dom", trackDOMNode)
);

submitButton.affords(click);
```

If React rerenders the page and destroys the DOM node, the **reference/schema persists while its grounding changes**. An action depending on it can immediately adapt.

That is essentially the paper's idea moved from the sensorimotor world into a dynamic software environment—and, in my view, is where this style of API becomes much more interesting than merely reproducing a 2008 robotics architecture.


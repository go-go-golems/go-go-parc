# 5.6 Is an Abstraction Step Function

## On research without collage, the identity provider it rebuilt around a language, and why the next important agent loop may happen above the level of code

*I use “5.6” throughout for GPT-5.6 Sol.*

I think 5.6 is a step function.

I do not mean that every answer is suddenly perfect, or that every benchmark moved by some magical amount, or that the old models have become useless. I mean something more practical: the unit of work I can hand to the model has changed again.

GPT-5 was the first model where I felt I could delegate a significant refactor without continuously babysitting it. Before that, I could ask for large changes, but I was usually also volunteering for several hours of following the model through the codebase, correcting local misunderstandings, repairing half-finished migrations, and repeatedly reminding it what the refactor was actually for. GPT-5 was the first time I regularly felt I could describe a fairly substantial structural change, let the model carry enough of the invariants through it, and come back to review the result rather than co-pilot every intermediate edit.

There have been incremental improvements since then that mattered a lot in practice. At some point enough tasks started working on the first pass that I could launch five jobs without effectively scheduling five future repair sessions for myself. That sounds less dramatic than a benchmark jump, but it changes the shape of a day. There is a huge difference between starting five things and spending the next five hours fixing them one after another, and starting five things with a reasonable expectation that most of them will converge.

With 5.6, I think the unit of delegation has moved from implementation into research-backed system design.

It is the first model I have used where research can feel almost unsupervised in the same way that refactoring started to feel almost unsupervised with GPT-5. I can point it at a difficult literature, a large codebase I do not know particularly well, and a broad engineering problem, and it can often keep the loop coherent for long enough to do several things in sequence:

- find the relevant research rather than merely a lot of adjacent research;
- synthesize it into a small set of governing ideas;
- decide which of those ideas actually matter for this codebase;
- change the internal representation of the application so those ideas become implementable;
- carry the new abstractions through a substantial implementation;
- and then step back out of the code and explain the machinery as a teachable conceptual system.

That is a very different object from a good patch, a long answer, or even a good literature review.

I have only been using it for a couple of weeks, and I am deliberately describing a personal workflow threshold rather than making a universal capability claim. I can already see cracks. It can still become too enchanted by a formalism. It can make a coherent argument faster than the evidence accumulates. It can write a beautiful self-consistent mythology around code that it also wrote. “Almost unsupervised” cannot mean “unaccountable.”

But I have spent enough time with new models to recognize the moment when a new stable unit of delegation appears. This feels like one of those moments.

The best example is an identity provider I have been building.

## The five stages of discovering a new model

Before getting into the identity provider, it helps to explain how these model jumps tend to reveal themselves to me. By now there is a fairly repetitive cycle.

Stage zero is the demo effect: *oh, that is not bad at all*. Something works conspicuously well. This is exciting, but it is also the least trustworthy stage. Any model can look revolutionary if the first prompt happens to land on exactly the right task.

Stage one is that I often cannot really tell the difference between the new model and the old one. I am still using my old workflow, old prompts, old tools, and old unit of delegation. The model may be more capable, but I have not yet found the task shape that exposes what the improvement is *for*. A better local answer is still a local answer.

Stage two is the useful one: *oh, fuck*.

This is when I stumble into something that changes the amount or kind of work I can hand over. It is not a nicer function or one extra bug caught. The workflow itself moves.

GPT-5 gave me that feeling around refactoring. Later models made parallel delegation much more practical because more tasks simply converged. With 5.6, the *oh, fuck* moment came when a research prompt did not end in a research document. It changed the ontology of the application, built a new language inside it, and then reconstructed the result into a textbook.

Stage three is when I begin to see the cracks. The vertical feeling wears off. I discover which prompts make the model drift, where its synthesis turns into collage, where it confuses formal-looking with formal, and which intermediate artifacts are necessary to keep it honest. That is when prompting techniques stop being vibes and become actual methods. I start building tools around the model.

Stage four is fluency. I can prompt it almost blind because I have internalized what context it needs, what shape of problem it can sustain, where to ask for competing designs, where to require gates, and what kind of evidence I need before I trust the result.

I am somewhere between stage two and stage three with 5.6. I can see the cracks, but I still have more of the vertical feeling than I have had in over a year.

The identity-provider project is the clearest reason why.

## The identity provider I mostly did not read

An identity provider, or IDP, is the part of a system that decides who you are and produces the assertions the rest of the system trusts. It sits behind logins and sessions and deals with things like credentials, account recovery, invitations, consent, authentication challenges, OAuth and OpenID Connect protocol state, token issuance, and the browser flows around all of that.

It is a bad domain in which to be casual. A bug in a normal application may lose a form submission. A bug in an identity system may let the wrong person become the right person.

I did not start this project because I had deep expertise in identity systems. Quite the opposite. Part of the experiment was to choose a domain complicated enough that I could not quietly rely on my own background to repair the model’s work. I let models build a great deal of the system, expanded it aggressively, pushed it toward production, and kept adding difficult requirements as I went.

I did not read most of the code line by line.

That remains an uncomfortable sentence. The point was not to prove that reading code no longer matters. It was to see how far I could push a different form of ownership: one based on explicit invariants, design documents, typed state transitions, traces, model-checking artifacts, conformance suites, package boundaries, and repeated architectural interrogation.

I wanted to know whether a model could build something too large for me to hold locally while still producing enough structure that I could develop a reliable global model of it.

The project moved through three broad asks:

1. Build an identity provider.
2. Research static analysis, model checking, formal methods, and relevant OAuth verification work, then improve the system.
3. Add a scripting layer so deployments can customize behavior without hard-coding every feature into the IDP.

These were not carefully engineered prompts. The second one in particular was broad and mediocre. That is part of why the result surprised me.

Previous models could research static analysis and formal methods in a recognizable way. They would find papers, summarize them, pull out several concepts, and draw plausible connections. But on difficult material you could often see the seams. The output behaved like a stack of research notes glued together. One paper would be represented accurately, the next would be simplified too aggressively, and the connection between them would become increasingly decorative.

If I then asked the model to apply the research to a real codebase, it often found the nearest surface to attach it to. It would add a checker at the edge, introduce some formal-looking types, or produce a model that described an idealized system while the actual application continued to operate through a different set of concepts.

5.6 did something else. It refactored the codebase so that the ideas the analysis needed were representable in the first place.

It introduced explicit objects and transitions around protocol state, evidence, assertions, and workflow behavior. It changed the internal ontology of the project. Instead of treating the existing implementation as fixed and finding somewhere to attach “static analysis” or “model checking,” it recognized that those techniques require a system with explicit states, transitions, and invariants. It rebuilt parts of the application around those objects and moved the existing behavior onto them.

This is one of the things that tells me the research capability has changed.

It is easy to retrieve a method. It is harder to recognize the preconditions under which the method says anything useful. It is harder again to notice that the application lacks those preconditions, redesign the application so they exist, and preserve behavior while doing so.

The model did not just add analysis. It made the system analyzable.

Then I asked it to make the IDP scriptable.

## I asked it to make the IDP scriptable. It more or less refused.

The feature request was reasonable. I wanted the identity provider to be a building block rather than one hard-coded product. I wanted deployments to express virtual users, invitation systems, project-specific signup flows, provider behavior, and other policy decisions without changing the Go implementation every time.

The obvious version of this request is to embed JavaScript and expose useful application objects on a context:

```javascript
ctx.store
ctx.sql
ctx.fetch
ctx.oauth
ctx.tokens
ctx.signingKey
```

This is also an excellent way to destroy nearly every useful invariant the previous work had introduced.

If arbitrary JavaScript can open a database transaction, inspect credentials, call network services, write HTTP responses, mint tokens, manipulate protocol objects, or access signing material, then the scripting layer becomes a second identity provider hidden inside the first one. The native implementation may be carefully typed, traced, checked, and modeled, while the deployment’s actual security behavior is determined by dynamic code with ambient authority.

5.6 rejected that premise.

It did not reject scripting. It rejected the interpretation that “scriptable” meant “give JavaScript access to the application.” Instead it designed a constrained computational language that happened to use JavaScript syntax and the Goja JavaScript interpreter.

The distinction is important. JavaScript could make policy decisions and compose host-defined operations. Go retained custody of credentials, protocol transitions, database transactions, browser responses, durable evidence, and final commits.

A script could receive a bounded input. It could invoke a small number of explicitly granted, versioned capabilities. It could choose a presentation from a host-controlled registry. It could return one member of a closed set of outcomes. It could construct an inert plan of effects for native code to validate and commit. It could identify a legal next handler when the workflow crossed a browser boundary.

It could not become the identity provider.

This created a fairly deep interpreter architecture, although none of the individual mechanisms is exotic on its own.

A **capability** is a narrow piece of authority represented by something the script must actually possess. Instead of a generic `ctx.store`, a handler might receive one versioned account-lookup capability that accepts one schema and returns another. The capability exists for one invocation, has a call budget, and becomes invalid when the invocation ends. Authority is passed explicitly rather than discovered through ambient global objects.

A **closed outcome** means a script cannot return an arbitrary object and hope the host interprets it sensibly. It must return something like `continue`, `present`, `challenge`, `commit`, `complete`, `deny`, `skip`, or `error`. The host can exhaustively interpret that finite set. A thrown exception is not silently converted into a policy denial. An absent result is not treated as permission to try a weaker provider.

A **native effect plan** means JavaScript does not perform the security-sensitive state change. It can propose something like “create this identity, bind this credential, consume this invitation, establish this session.” Go validates the exact sequence and applies it through a named atomic operation. The script describes the intended transaction; it does not own the transaction.

An **opaque secret handle** means a password can enter the JavaScript workflow without becoming a JavaScript string. The script may be able to pass the handle to a native password-policy capability or into an approved commit plan, but it cannot print, concatenate, retain, compare, or accidentally serialize the secret itself.

The most interesting construct is the **explicit continuation**.

An ordinary `await` may remain alive while one HTTP request is executing. A browser interaction cannot. The user may close the tab, return several hours later, hit another server instance, or resume after a deployment and process restart. The system cannot keep a JavaScript Promise alive across that interval. It should not serialize a Goja heap, closure, or interpreter stack and pretend that this is stable application state.

Instead it stores a small first-order record: which named handler should run next, which bounded public values it needs, which native references are attached, which program generation gave the handler its meaning, what revision the continuation is on, and when it expires.

At the simplest mechanical level, this is “put the next state in a database.” The rigorous part is specifying everything that must be true around that field:

- the next handler is registered in the same workflow;
- the event that resumes it matches the handler’s input schema;
- the carry is bounded, serializable, and permitted to cross a durable boundary;
- no password, credential, capability function, Promise, Goja object, or request-local resource leaks into it;
- any required native evidence was created before the resume;
- the continuation is tied to an exact semantic generation or an explicit migration;
- its revision advances atomically so replayed submissions cannot consume it twice;
- it expires and can be revoked.

The callback names in those continuation records create another problem. A persisted name such as `signup.email_verified` has to resolve to the same intended code in every runtime. The JavaScript closure itself exists only inside one Goja instance. The serializable program can store the name, but the system must prove that every independently created worker registers a matching callback set under the same program and schema identities.

So the model introduced **deterministic callback registration**: compile the same source into fresh runtimes, canonicalize the program, fingerprint the source, program, callbacks, and schemas, and reject activation if the materializations differ.

This is a subtle thing to invent as part of “add scripting.” It is really a dynamic-linking problem created by the relationship between durable semantic names and runtime-local closures.

It also designed the worker pool conservatively. Goja runtimes are not thread-safe. Each worker has one owner. Asynchronous native operations settle Promises by routing the completion back through that owner. A runtime is returned to the pool only when the invocation has produced a valid result and all asynchronous settlements are known to be complete. If a handler times out, throws, returns malformed output, or leaves the runtime in an uncertain state, the worker is discarded and replaced rather than optimistically cleaned up.

That is what I mean when I say the architecture was systematically woven together. The explicit continuation makes browser state first-order. The callback fingerprints bind that state to executable meaning. Invocation capabilities keep authority narrow. Closed outcomes keep host interpretation exhaustive. Native effect plans preserve transaction authority. Opaque handles constrain secret flow. Fail-stop worker reuse keeps one uncertain invocation from contaminating the next.

None of these ideas is individually unprecedented. The synthesis is the system.

> **Image placement: annotated continuation requirements and package plan.**  
> *Suggested caption: The page where I realized the scripting proposal was actually a small interpreter architecture: explicit continuation requirements, a pure program contract, a native workflow interpreter, constrained Goja runtimes, opaque secrets, and invocation capabilities.*

## Why this is evidence of research and synthesis, not merely better coding

The IDP is a useful example because it lets me be more precise about what I think has changed. “It did good research” is too vague. There are several distinct behaviors here.

### It kept the research question intact

Research outputs from earlier models often became source-driven. The answer inherited the shape of whatever papers or pages happened to be retrieved. If the literature contained five prominent techniques, the system got five sections, whether or not all five mattered.

Here the model kept returning to the engineering question: how can this identity provider become more analyzable and more configurable without losing protocol and security invariants?

Static analysis, model checking, capability systems, continuations, and effect plans were not presented as a museum of interesting ideas. They were selected and shaped according to that question.

### It selected representations, not just recommendations

A weak synthesis says, “Use a state machine.” A stronger one asks what the states and transitions actually are, where they live in the code, which events advance them, what evidence is attached, and how they are serialized.

The model repeatedly crossed from method to representation. It did not merely recommend model checking; it introduced the objects the model checker would observe. It did not merely recommend capabilities; it defined their lifetime, schemas, versions, budgets, and settlement behavior. It did not merely recommend durable workflows; it defined the continuation record and generation identity.

### It coordinated abstractions that constrain one another

The interesting work was not finding one clever pattern. It was recognizing that several patterns had to agree.

If callbacks are named but not deterministic across runtimes, continuations are unsafe. If continuations can carry arbitrary JavaScript values, secret handles and invocation lifetimes are meaningless. If scripts can perform effects directly, closed outcomes do not preserve protocol authority. If asynchronous calls can settle after a worker is reused, capability revocation is incomplete. If hot reload changes handler meaning without generation pinning, a valid continuation becomes a semantic time bomb.

The design is good because the pieces close one another’s gaps.

### It descended back into implementation

Models have always been able to propose abstractions. The hard part is the descent.

“Use capabilities” is a sentence. A working capability bridge must answer:

- how a capability is represented inside the VM;
- who grants it;
- whether a script can forge or retain it;
- how arguments and results are validated;
- how calls are metered;
- how cancellation works;
- how Promise settlement returns to the runtime owner;
- what happens after the invocation ends;
- how errors are classified.

Likewise, “use continuations” is a sentence. A production continuation needs schemas, revisions, expiry, replay behavior, code-generation identity, native references, migration rules, cleanup, and end-to-end restart tests.

The model stayed with the abstraction until these details had coherent answers.

### It changed the foundation rather than decorating it

This may be the biggest difference.

The model did not optimize for a small diff. It was willing to say, in effect: the application does not currently contain the right machinery, so we will build the machinery and rebase the existing application on it.

That happened during the analysis work and again during the scripting work. It is a form of architectural confidence that previous models often lacked. They were locally obedient. They tried to make the request fit inside the current code shape, even when the current code shape was the reason the request was difficult.

Here the model was willing to modify the ontology of the project.

### It could teach the result afterward

After the scripting layer existed, I asked the model to study the branch and write a textbook about the interpreter constructs: serialized continuations, invocation capabilities, deterministic callback registration, secret handles, closed outcomes, runtime leasing, generation-aware resumption, and the rest.

It produced a long monograph that did not merely walk the package tree. It reconstructed the dependency of ideas.

It began with why scripting an identity provider is dangerous. That motivated keeping protocol authority native. That motivated capabilities and closed outcomes. Browser interactions motivated explicit continuations. Durable handler names motivated deterministic registration and generation identity. Promise-returning capabilities motivated runtime ownership, settlement tracking, and fail-stop reuse.

In a sense, it reverse-compiled the codebase:

```text
implementation
    -> invariants
    -> computational patterns
    -> named concepts
    -> explanatory sequence
```

This is what I mean when I say 5.6 can teach. It can synthesize a complicated thinking workflow and arrange it so the reader encounters concepts in the order that makes them necessary.

I ended that morning with roughly two hundred pages of textbook-style material across several related investigations. Normally that much generated prose becomes exhausting almost immediately. The entropy rises. Sections repeat one another. The narrative stops advancing. The text becomes polished sludge.

This material remained interesting because the sections continued to have jobs. There was a lot of it because the project contained a lot of machinery, not because every point had been inflated into a chapter.

There is a major caveat: a model can write a beautiful explanation of a system it misunderstood. If it also wrote the code and tests, it can create a self-consistent mythology. The useful version needs exact source links, distinctions between implemented and proposed behavior, test references, unresolved concerns, and clear statements of inference.

But with those anchors, the ability to produce both a system and an inspectable theory of that system is qualitatively different from code generation.

> **Image placement: implementation phases and gates.**  
> *Suggested caption: What kept the work from feeling like architecture theater was the implementation plan: each abstract mechanism had a phase, a concrete purpose, and an end-to-end gate.*

## LLMs as abstraction machines

The phrase I keep coming back to is that LLMs are abstraction machines.

Saying they are pattern-matching machines is not wrong. It is just too low-resolution to describe the behavior I care about. The useful question is what kind of patterns they can recognize, at what level, how they coordinate several abstractions, and whether they can return from the abstraction to working concrete machinery without losing the constraints they started with.

The movement looks something like this:

```text
concrete artifacts
    -> recognize recurring structure
    -> move into an abstract representation
    -> coordinate it with other abstractions
    -> lower the result into new concrete artifacts
```

In the identity provider, the concrete artifacts were routes, forms, callbacks, database operations, credentials, protocol handlers, and tests. The model moved upward into evidence, authority, state transitions, effects, continuations, generations, and runtime ownership. It coordinated those with ideas from interpreter design and security. It then lowered the result back into packages, schemas, callback registries, stores, worker pools, validators, and end-to-end tests.

The important thing is not just climbing the abstraction ladder. Architecture astronauts climb easily. The interesting capability is moving up and down without dropping the problem.

A challenge in an identity system is simultaneously:

- a thing a human experiences;
- a protocol event;
- a piece of evidence;
- a security boundary;
- a browser interaction;
- a durable state transition;
- and an input to future policy.

A good language decides which of those views the script author sees and which the runtime owns. A good interpreter makes the division executable. A good compiler can make a convenient source form lower into a safer runtime form. A good textbook can explain why the division exists.

5.6 was able to move among these views without immediately flattening one into the others.

That is also why language design is such a strong test of model abstraction. A model can hide contradictions in prose. A language forces decisions.

The nouns need representations. The operations need signatures. State needs a lifetime. Effects need an interpreter. Invalid combinations need diagnostics. Authority needs a location. Durable values need a serialization rule. The abstract idea has to become something executable.

If a model can design a language, implement its interpreter, use the language to express real programs, and explain the result, it has walked both directions on the abstraction ladder.

## Ask for a language first

One of my most reliable prompting techniques over the last several years has been to ask for a language before asking for the application.

“Language” can mean many things. It may be a YAML DSL when the problem is mostly declarative. It may be a JavaScript API when I need lexical bindings, functions, branching, loops, or asynchronous composition. It may be a widget tree, a command language, a query notation, a set of typed Go interfaces, or a small family of builders.

The point is not to invent syntax for entertainment. The point is to find the boundary where domain concepts and computational concepts meet.

A logistics domain contains orders, shipments, refunds, routes, exceptions, appointments, and plans. An identity domain contains identities, credentials, invitations, challenges, consent, and sessions. A RAG experiment domain contains corpora, retrievers, rankers, prompts, evaluators, runs, and artifacts.

The computational side contains values, bindings, branches, loops, effects, state transitions, retries, transactions, serialization, concurrency, and failure.

A large amount of application complexity accumulates at the seam between these worlds. A domain expert says “add a refund workflow.” The implementation of that sentence may require permissions, a state transition, database updates, money calculations, a form, validation, an audit event, a queue, a notification, a page, and CSS.

A single prompt now asks the model to bridge from a high-level domain intention all the way down to dozens of unrelated implementation details. Every new feature prompt contains a hidden request to rediscover the architecture.

A small language makes the bridge part of the project.

If the application already has a language of workflows, forms, domain operations, and native effects, “add a refund flow” may become twenty lines. The model no longer needs to infer where validation lives, how a form is rendered, what an error looks like, or how the commit is made atomic. Those choices exist once in the interpreter.

This changes the effective intelligence of the model. It reshapes a messy application problem into a smaller surface with stronger regularities.

I have generated thousands of small languages and APIs over the last three or four years. That sounds more scientific than it has been. Most of the process has been vibed. I try a notation, watch where the model struggles, add a primitive, remove an escape hatch, move something from script into the runtime, generate more examples, and gradually accumulate patterns that I no longer consciously name.

Some of those patterns are ordinary API design. Some come from Common Lisp, macros, interpreter work, and old framework design. Some are specific to the way LLMs respond to concepts with strong representations in their training. Some are probably things I have rediscovered badly.

Until now, the optimization loop has mostly depended on my taste and on whether generated applications feel clean.

The research capability of 5.6 suggests that this loop can become more systematic.

## The language optimization loop

This is the part I am most interested in.

The old loop is roughly:

```text
describe the domain
    -> ask for a DSL or JavaScript API
    -> implement a few examples
    -> notice awkwardness
    -> patch the API
    -> repeat
```

It works surprisingly well, but the evaluation criteria live mostly in my head. One form feels too verbose. The model repeatedly misuses one primitive. An abstraction exposes implementation detail. A supposedly generic operator grants too much authority. A domain expert cannot read the result. I revise the language and try again.

A model that can sustain research and synthesis makes a more rigorous loop possible.

Start with a corpus of representative tasks rather than one feature request.

For an identity system, the corpus might include invitation signup, virtual users, account recovery, multi-factor challenge, policy denial, consent, provider selection, and migration of an in-progress browser flow. For a reproducible RAG laboratory, it might include freezing a corpus, comparing retrievers, varying prompts, running several evaluators, caching provider calls, and reproducing an experiment months later.

Ask the model to separate the domain ontology from the computational requirements.

Which concepts belong to the domain? Which operations are effects? Which values need stable identity? Which things are secret? Which steps are durable? Which parts require loops and branches? Which choices must remain native policy? Which values can safely cross time, process, or trust boundaries?

Then ask it to propose competing languages rather than one grand design.

One language may be highly declarative and easy to analyze but awkward for complex control flow. Another may use JavaScript callbacks and be pleasant to author but expose too much dynamism. A third may compile direct-style async functions into explicit state machines. A fourth may separate a pure policy language from a transactional effect language.

Implement the smallest interpreter for each serious candidate. Generate real programs. Make the model use the language, not merely praise it. Give it tasks it has not seen. Ask a second model to use it. Ask a human to read the programs. Collect the failures.

Now the language can be compared on concrete axes:

- How long are representative programs?
- How many concepts must an author learn?
- How often does the model request authority it does not need?
- How many invalid states are representable?
- Which errors are caught statically?
- Which survive until runtime?
- How local is a change?
- Can a deployment show a semantic diff rather than only a text diff?
- Can the interpreter enforce a hard guarantee once for every program?
- Does the language remain honest about the domain, or merely hide complexity?
- What implementation and verification burden does the language create?

Research becomes part of the loop instead of an initial survey. The model can examine workflow systems, capability languages, effect systems, durable execution frameworks, protocol state machines, theorem provers, compiler workbenches, and language usability research. It can compare those designs against the actual corpus, identify missing distinctions, and propose experiments instead of simply adding fashionable terminology.

Then revise the language, rerun the corpus, and compare.

This is not prompt optimization. It is not searching for magic wording that makes the model generate the right code. The artifact being optimized is the computational language between the model and the application.

Prompts are local and ephemeral. A language compounds.

Once an IDP has a good workflow language, future features become smaller. The interpreter centralizes security properties. The compiler can infer capability use. A static checker can reject a secret that would cross a durable suspension. The runtime can meter host calls. The documentation generator can produce a workflow graph. The deployment system can report that one release added a capability, widened an effect set, and changed one continuation schema.

There is a peculiar possibility here: the model can be the language designer, one of the language users, and part of the evaluation harness.

That is dangerous if taken literally. A language optimized only for one model may become alien to humans or brittle across model generations. The model may exploit accidental cues rather than understand the semantics. It may prefer verbose forms because they resemble its training data or compact forms that no human wants to maintain. We need human readers, independent interpreters, cross-model tests, static checks, and domain-expert review.

But models are also extremely cheap additional language users with interesting failure modes. We can generate hundreds of representative programs, mutate them, ask several models to repair them, compare error rates, measure unnecessary authority, and observe where notation helps or hurts generalization. Language design has traditionally been expensive to test because recruiting many skilled users is hard. Models do not replace those users, but they make a much larger experimental loop possible.

The loop can eventually operate above one project.

Imagine a malleable JavaScript compiler or interpreter where each project defines:

- value types;
- capabilities;
- effects;
- durable operations;
- secret and ownership rules;
- cost models;
- verification passes;
- native bindings;
- and the permitted subset of JavaScript.

Tiny-IDP would be one profile. A reproducible RAG system would be another. A deployment orchestrator, document approval engine, policy system, or agent tool runtime could reuse the compiler and runtime while exposing different computational worlds.

For Tiny-IDP, the flagship feature might be a `durable await` that looks like normal direct-style code:

```javascript
const form = await durable.present(SignupForm);
const proof = await durable.emailCode(form.email);
return commit.signup(form, proof);
```

The compiler would transform this into the explicit continuation handlers the runtime already understands. At each durable suspension it would calculate which values are live afterward and reject anything that cannot safely cross the boundary: secrets, capabilities, closures, Promises, request resources, Goja objects, unbounded data, or values without a stable schema.

The author gets pleasant direct style. The runtime still gets a small, explicit, inspectable state machine.

That is the broader language optimization loop I can now imagine: the model researches, proposes, implements, uses, analyzes, and refines the language in which future application work will be expressed.

> **Image placement: annotated reproducible RAG operator design.**  
> *Suggested caption: The same shape appearing in a second domain: trusted source packages, canonical artifacts, declared host capabilities, constrained runtimes, typed outputs, and reproducibility evidence. That recurrence is why I suspect this is a general language pattern rather than an IDP-specific trick.*

## What “better at research” means to me

I want to be careful with this claim because “research” covers too much.

I am not saying 5.6 can independently establish scientific truth. I am not saying it can replace a researcher who knows which experiment matters or a reviewer who can detect a hidden assumption. I am not saying the output of a long agent run becomes reliable merely because it is coherent.

I mean a more specific set of capabilities.

It can maintain a research objective across many sources and implementation steps without allowing the source material to entirely determine the shape of the answer.

It can compress a large literature into a small number of useful distinctions instead of preserving every retrieved concept at equal weight.

It can recognize when a method requires a different representation of the problem and modify the code so the method becomes applicable.

It can coordinate domain knowledge and computational structure. It understands that “evidence” in an identity system is at once a protocol fact, a security object, a workflow input, and a durable native reference.

It can keep several abstraction layers aligned over a long implementation: source API, interpreter contract, native authority, persistence, runtime scheduling, validation, and tests.

It can step back afterward and teach the reasoning in a sequence that is not isomorphic to the file tree or the search results.

And, perhaps most importantly, it can reject a naive prompt while still satisfying the underlying need.

That last point is part of what I mean by taste.

The model did not respond to “make it scriptable” with the largest possible scripting surface. It found a smaller problem: let scripts express policy and composition while the native kernel preserves authority. It did not respond to “add model checking” by wrapping the existing code in formal vocabulary. It changed the system so the transitions could be modeled.

Taste is an overloaded and subjective word, so I prefer to define it operationally:

- challenging the framing when the framing would undermine the goal;
- selecting a smaller abstraction rather than a larger API;
- introducing machinery only where it protects an invariant or enables a real use case;
- connecting each abstraction to a validator, implementation phase, and test gate;
- and being willing to rebuild the foundation instead of decorating a mismatch.

There are contexts where the IDP design would be absurdly overengineered. An identity provider is not one of them.

This combination—research, abstraction, implementation, and restraint—is why the jump feels different from “the new model codes better.”

## Research without collage

The phrase I have been using privately is research without collage.

Earlier models could gather an impressive amount of material. But when the topic became difficult, I was often the one performing the actual synthesis. I had to notice that two papers used similar terminology for different mechanisms, that one technique depended on a closed-world assumption that did not apply, that a proposed formalization had no relationship to the production data model, or that an elegant analogy quietly broke the security boundary.

5.6 is better at remaining inside that synthesis problem.

It can map the literature, identify a tractable core, choose methods, and return to the application with a proposal that changes concrete representations. It can stay in that loop long enough that I am no longer only using it to retrieve and summarize material. I can use it to create a small research program around a piece of software.

This is what I meant, somewhat recklessly, when I called the behavior “PhD-level” in conversation. I did not mean that it is producing a groundbreaking dissertation or deserves credentials. I meant the more ordinary but still difficult work that many PhDs consist of: map a body of work, identify the useful core, choose methods, apply them to a complicated artifact, document limitations, and maintain coherence over many steps.

I do not think it is postdoc-level yet, if we are going to continue abusing the metaphor. I can see it overgeneralize. I can see it become too enamored of a formal system. I can see places where the bibliography is stronger than the argument. It benefits greatly from a human who can reject an elegant but irrelevant theory.

But the floor has moved.

Ideas that were previously unreasonable for a small project—not because implementation was impossible, but because the research and synthesis overhead was too large—become plausible experiments:

- static analysis for a small identity provider;
- model checking selected protocol transitions;
- a compiler that derives explicit continuations from JavaScript;
- a project-specific capability and effect system;
- a textbook that reverse-engineers the architecture;
- a comparative language-design loop across unrelated domains.

Each would traditionally be a substantial side project before the application itself could continue. If the model can coordinate the research and implementation, they can be explored alongside production work.

That does not make them free. It changes which costs are scarce. Generating a large amount of coherent work becomes cheaper. Choosing what deserves to exist, defining acceptance evidence, and maintaining contact with reality become more important.

## The cracks: unsupervised cannot mean unaccountable

There is an obviously dangerous version of this story where the conclusion is that the model can research, architect, implement, verify, and document a system, so the human can stop paying attention.

That is not my conclusion.

I built a codebase I largely did not read, and the fact that this is uncomfortable is part of the experiment. A system can have beautiful design documents, passing tests, formal-looking models, and a coherent textbook while being wrong in ways none of those artifacts represent. Identity protocols have hostile environments, cryptographic assumptions, integration details, operational failure modes, and deployment realities that do not disappear because the internal architecture is elegant.

The model can also create a self-confirming world. It writes the code, writes the tests, writes the design document, and then writes the textbook explaining why the design is good. Coherence becomes dangerous because it is persuasive.

The answer is not to abandon the workflow. It is to make the evidence harder to fake.

That means conformance suites, adversarial tests, restart and replay tests, race detectors, browser integration, exact source links, canonical manifests, explicit generation identities, traceable native effects, semantic diffs, and independent review of the most sensitive boundaries. It means distinguishing “the model produced a plausible formal model” from “the production implementation refines that model under stated assumptions.”

It also means treating *unsupervised* as a description of interaction frequency, not responsibility.

I can let the model work for several hours without steering every step. I cannot let the resulting system enter production without a theory of what evidence makes it acceptable.

This is another reason language design matters. A smaller language makes independent evidence more tractable. If arbitrary JavaScript owns the IDP, the review surface is every possible program behavior. If JavaScript can only invoke typed capabilities and return closed outcomes, the trusted boundary is smaller. If durable workflows compile into explicit continuation graphs, they can be inspected. If effects are inert plans, native committers can enforce transaction shapes. If artifacts carry semantic manifests, deployment review can focus on authority and state changes rather than only source text.

Abstraction is not an escape from verification. A good abstraction creates a place where verification can be applied once.

## Where I am now

So I am somewhere in stage three.

Stage zero was immediate: 5.6 produced several outputs conspicuously better than what I had become used to.

Stage one was brief because ordinary coding was already good enough that a better patch did not explain the new model.

Stage two arrived when the identity-provider work kept going. The model did not merely collect research. It changed the fundamental representation of the application, built a scripting architecture that rejected my naive framing, and then extracted a coherent programming-languages textbook from the result.

That was the *oh, fuck* moment. The unit of delegation had moved from implementation to research-backed system design.

Now I can see the cracks. The model can write too much. It can produce a clean conceptual system faster than empirical validation. It needs explicit instructions to distinguish current implementation from future proposals. It benefits from competing designs and falsification criteria rather than one synthesis. It still needs independent tests, another model, or a domain expert to attack the result.

I am turning those cracks into techniques:

- ask for a language before an application;
- ask for competing languages before choosing one;
- force interpreter and compiler contracts to become explicit;
- make the model use the language it designed;
- maintain research diaries and source-linked artifacts;
- require implementation gates rather than architectural promises;
- evaluate against a corpus of real tasks;
- preserve native authority around things that cannot safely be delegated;
- and ask what evidence would falsify the design, not merely what would demonstrate it.

Stage four will be fluency: being able to run this kind of research and language evolution almost blind because the workflow has become internalized. I am not there yet.

But I can already see the next workflow taking shape:

```text
ask the model to discover the computational language of a domain
    -> implement and verify the interpreter
    -> express the application in that language
    -> observe where humans and models struggle
    -> research better abstractions
    -> evolve the language
    -> regenerate and recheck the application
```

That loop happens above ordinary code generation. The code becomes one compiled artifact of a more important design process.

## The abstraction step function

The most important thing about 5.6, from my perspective after these first weeks, is not that it writes more code or uses more terminology.

It can remain in a difficult research loop long enough to reorganize a system around the research. It can move from concrete code into abstract machinery, coordinate several abstractions, and descend back into working implementation. It can reject the surface form of a prompt while satisfying the underlying need. It can then turn the resulting code back into a conceptual narrative that teaches me what exists.

That is why I keep using the phrase abstraction machine.

Not because the model floats away from details. The useful behavior is the opposite: it can move up and down the ladder.

It can recognize that “make the IDP scriptable” is actually a question about authority, effects, runtime ownership, and durable control flow. It can recognize that “add model checking” is actually a question about whether the application has explicit states and transitions. It can recognize that “document the codebase” is actually a question about the dependency of ideas rather than the directory tree.

And it can turn each recognition into machinery.

I have spent several years asking models for languages because languages compress both the domain and the implementation into a surface the model can manipulate more reliably. Until now, that was mainly a prompting and framework technique I practiced by feel.

5.6 makes me think the model can become a serious participant in optimizing those languages themselves.

Maybe this will devolve. Maybe I am still seeing one unusually successful project through the glow of a new release. Maybe the model is better at producing the appearance of a research program than sustaining one. I have learned not to turn the first unlock into a universal law.

But this is the closest I have come in more than a year to the vertical feeling that the workflow has changed underneath me.

GPT-5 made large refactors feel delegable. Later models made reliable parallel work routine. 5.6, at least in this project, made research, synthesis, and abstraction feel delegable as one connected activity.

That is a much larger change than writing code faster.

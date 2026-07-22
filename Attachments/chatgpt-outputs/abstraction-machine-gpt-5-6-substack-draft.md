# 5.6 and the Abstraction Machine

## On unsupervised research, architectural taste, asking for a language first, and the possibility that the next important agent loop happens above the level of code

*Editor’s note: I use “5.6” throughout for GPT-5.6 Sol.*

I asked 5.6 to make my identity provider scriptable. It more or less refused.

Not literally. It implemented the feature. But it rejected the obvious interpretation of the feature: embed JavaScript, hand it the useful internal objects, and let deployments customize the system by calling into them. Instead it designed a small constrained language in which JavaScript could make policy decisions and compose host-defined operations while Go retained custody of credentials, transactions, protocol state, browser behavior, and durable evidence.

It then implemented the interpreter machinery required to make that boundary real: explicit continuations instead of persisted Promises, invocation-scoped capabilities instead of ambient services, deterministic callback registration, canonical fingerprints, opaque secret handles, closed outcomes, native effect plans, generation-aware resumption, and fail-stop worker reuse.

This article is partly about that design. More importantly, it is about what the design made me realize about the new model: the unit of work I can delegate has moved again.

New models arrive in a fairly predictable sequence for me by now.

The zeroth stage is the demo effect: *oh, that is not bad at all*. Something works that did not work before, or it works with an ease that is conspicuous enough to make me stop for a minute. This part is exciting, but it is also the least reliable. Every model can look like a revolution if you happen to ask it exactly the right question on the first day.

The first stage is stranger: I often cannot really tell the difference between the new model and the old one. I am still using my old workflow, my old prompts, my old expectations, and my old unit of delegation. The model may be better, but I have not yet found the task shape that exposes what the improvement is *for*.

Then comes the second stage, which is the useful one: *oh, fuck*.

This is when I stumble into a task that changes the amount or kind of work I can hand over. The relevant thing is not that the model writes a nicer function or catches an extra bug. The unit of delegation changes.

GPT-5 was the first model where I felt comfortable delegating significant refactors without continuously babysitting them. Before that, I could ask for large changes, but I was usually committing myself to spending the next several hours following the model through the codebase, catching local misunderstandings, repairing half-finished migrations, and steering it back toward the original goal. GPT-5 was the first time I regularly felt I could describe a substantial structural change and let the model carry enough of the invariants through the refactor that I could review the result rather than co-pilot every intermediate edit.

There were more incremental unlocks after that. One of the meaningful ones was simply that enough things started working on the first pass that I could launch several jobs in parallel without effectively scheduling several future repair sessions for myself. That sounds like a modest improvement, but it changes the shape of a day. There is a huge difference between starting five tasks and then spending five hours fixing them one by one, and starting five tasks with a reasonable expectation that most will converge.

With 5.6, I think I have encountered another one of these changes in the unit of delegation. It is the first model I have used where research can feel almost unsupervised in the same way that refactoring started to feel almost unsupervised with GPT-5.

I do not mean that I can ask it any research question and receive truth. I do not mean that it is a replacement for subject-matter expertise, peer review, experiments, or proofs. I mean something more practical and, for my work, more consequential: I can point it at a difficult body of literature, a large unfamiliar codebase, and a broad engineering objective, and it can often keep the research loop coherent long enough to synthesize the literature into a small set of ideas, apply those ideas to the code, restructure the implementation around them, and then explain what it did in a way that teaches me the resulting system.

That entire loop is new enough that I am still trying to find words for it.

I am somewhere between stage two and stage three with 5.6 now. Stage three is when the initial vertical feeling wears off and I start seeing the cracks: which tasks make it drift, which prompts produce architecture astronautics, where the research becomes a collage, where it confuses a plausible formalism with a valid one, where it needs a tool or a constraint or an explicit intermediate artifact. That is when prompting techniques become concrete and when I start building machinery around the model. Usually, by the time I become fluent at filling those cracks, I can already imagine the next model filling several of them by itself.

But I am not there yet. I can see some cracks. I also still have a bit of the vertical feeling, which I have not had this strongly in over a year.

The best example is an identity provider I have been building.

## The identity provider I mostly did not read

An identity provider is the part of a system that decides who you are and produces the assertions the rest of the system trusts. It deals with logins, sessions, credentials, challenges, invitations, consent, tokens, protocol state, and all of the unpleasant security boundaries around those things.

I did not begin this project because I had deep expertise in identity systems. Quite the opposite. Part of the experiment was to choose a domain complicated enough that I could not quietly rely on my own background to repair the model’s work. I let the model build a great deal of the system. I pushed it toward production. I added requirements as I went. I did not read most of the code line by line.

This is obviously not a sentence I would have written approvingly about software development a few years ago.

The point was not to prove that reading code no longer matters. It was to see how far I could push a different form of ownership: one based on design documents, explicit invariants, tests, traces, model-checking artifacts, package boundaries, and repeated architectural interrogation. I wanted to know whether a model could build something too large for me to hold locally while still producing enough structure that I could develop a reliable global understanding of it.

At some point I asked it to research static analysis, model checking, formal methods, and work on OAuth protocol verification, and then to improve the system accordingly. This was deliberately broad and, in retrospect, not even an especially good prompt.

Previous models could do the research part in a recognizable way. They would find papers, summarize them, extract a few concepts, and draw plausible connections. But on difficult material you could often see the seams. The answer behaved like a stack of research notes that had been glued together. One source would be represented accurately, the next would be simplified too aggressively, and the connection between them would become increasingly decorative. If I asked it to apply the result to a real codebase, the implementation often settled for adding a layer of assertions or a few formal-looking types around the existing structure.

What surprised me here was that the model did not merely add analysis tools around the code. It refactored the codebase so that the important protocol ideas became representable in the first place.

It introduced objects and transitions that made tracing, assertions, invariants, and model checking possible. It changed the internal ontology of the project. Instead of treating the existing implementation as fixed and finding somewhere to attach the requested feature, it recognized that the request implied a different foundational representation and rebuilt toward it.

That is a very particular kind of competence. It is easy to satisfy a checklist by adding a checker at the edge. It is much harder to notice that the code does not currently contain the right objects for the checker to say anything useful, introduce those objects, move the existing application onto them, and preserve behavior while doing so.

I had seen models perform large refactors by then. I had not often seen one respond to a research prompt by changing the ontology of the application so that the researched ideas had a natural home.

Then I asked it to make the identity provider scriptable.

## I asked it to make the IDP scriptable. It more or less refused.

The request was reasonable. I wanted the identity provider to be a building block rather than one hard-coded product. I wanted to express things like virtual users, invitations, project-specific signup flows, provider behavior, policy decisions, and other forms of customization without modifying the Go implementation every time.

The naive version of this request is straightforward: embed JavaScript, give it a context object, and expose the useful parts of the application.

Something like:

```javascript
ctx.store
ctx.sql
ctx.fetch
ctx.oauth
ctx.tokens
ctx.signingKey
```

This is also a good way to undo nearly every invariant the previous work had introduced.

Once arbitrary JavaScript can open stores, issue queries, fetch network resources, inspect credentials, mint tokens, sign values, write responses, or manipulate protocol objects, the scripting layer becomes a second identity provider hidden inside the first one. Every script path now has to preserve the full security model. The native implementation may be carefully typed, traced, checked, and modeled, while the actual behavior of the deployment is determined by a dynamic program with ambient authority.

The model rejected that premise.

It did not reject the feature. It rejected the idea that “scriptable” meant “give JavaScript access to the application.” Instead it designed something closer to a small policy and workflow language implemented using JavaScript syntax.

JavaScript could receive carefully bounded inputs. It could call explicitly granted, versioned capabilities. It could select among host-defined presentation objects. It could return one member of a closed set of outcomes. It could propose an inert sequence of effects for native code to validate and commit. It could name a legal next handler at a browser boundary.

It could not own the identity provider.

The distinction sounds obvious when stated afterward, which is often the sign of a good abstraction. But it has very large consequences.

The JavaScript layer does not get credentials. It may get an opaque password handle that can be passed to a native password verifier or into a native commit operation, but it does not get a string it can log, concatenate, retain, or accidentally serialize. It does not get the raw challenge code. It may get native evidence that a challenge succeeded. It does not get an HTTP response writer. It may choose a presentation from a host-controlled registry. It does not get a SQL transaction. It may construct a typed plan that the native runtime either accepts as one named atomic operation or rejects.

There is no generic “do whatever you need” escape hatch. The language is useful because the operations are narrow enough to have stable meaning.

This is where the design started to feel less like an ordinary embedding API and more like interpreter work.

A handler is not simply a JavaScript function. It has an input schema, an output schema, a set of allowed outcomes, a set of required capabilities, a set of permitted commit effects, a timeout, a call budget, and an output budget. The callback itself exists only inside one runtime, while the serializable program stores a stable callback identifier. The runtime has to prove that the identifier resolves to the same intended callback registry across independently created workers.

The model introduced deterministic callback registration and fingerprints for the source, the canonical program, the callback set, and the schemas. This matters because a browser workflow may persist the name of a handler today and resume it tomorrow. A string such as `signup.email_verified` is not enough. The system needs to know which program generation gave that string meaning, whether the input schema is still compatible, whether the callback exists in every worker, and whether a reload changed the semantics under an already-running workflow.

The browser boundary is where the design becomes especially interesting.

An ordinary JavaScript `await` can remain alive while one HTTP request is running. A browser interaction cannot. The user may close the tab, return hours later, hit a different server instance, or resume after the process has restarted. The system cannot persist a Promise, a JavaScript closure, a Goja object graph, or an interpreter stack and pretend that this is a stable application protocol.

Instead it stores an explicit continuation record. At the simplest mechanical level, this is just a state-machine field in a database: here is the handler to invoke next, and here is the data it needs. But almost all of the interesting work lies in the constraints around that field.

The next handler must be registered in the same workflow. Its input schema must be compatible with the event that will resume it. The carried data must be serializable, bounded, and allowed to cross a durable boundary. Secrets must not leak into it. Native evidence must have been created before resumption. The continuation must expire. It must be bound to an exact program generation or have an explicit migration path. Its revision must advance atomically so that replayed requests cannot consume it twice.

The system therefore never serializes “the callback.” It serializes a first-order description of what should happen next.

This is a known programming-languages move called defunctionalization when stated abstractly: replace a function or continuation with a finite data representation and a native dispatcher. In ordinary application code it may look like nothing more exotic than storing `next_state = "verify_email"`. The interesting part is recognizing it as the same computational pattern and then rigorously defining its schema, authority, lifetime, replay behavior, and relationship to code generations.

That is the kind of synthesis I am talking about. None of the ingredients is individually unprecedented:

- state machines;
- capability-based APIs;
- schema validation;
- opaque handles;
- worker pools;
- canonical hashes;
- effect plans;
- explicit continuations;
- generation pinning;
- fail-stop cleanup.

What impressed me was how they were strung together. Each technique solved one failure mode and made the next technique possible.

The closed outcome set makes native interpretation exhaustive. The capability set prevents ambient authority. The explicit continuation prevents VM state from becoming durable. The generation fingerprint prevents old continuations from silently changing meaning. The worker owner keeps all Goja operations on one goroutine. The settlement tracker prevents a runtime with late asynchronous work from being reused. The fail-stop pool discards a worker after a timeout or uncertain interruption instead of trying to clean up a state it cannot prove safe.

This is not just “a lot of security stuff.” It is a coordinated computational model.

[**IMAGE 1 — annotated continuation requirements and package plan**]

*Suggested caption: The page where I realized the scripting proposal was actually a small interpreter architecture: explicit continuation requirements, pure program contracts, a native workflow interpreter, a constrained Goja runtime, opaque secrets, and invocation capabilities.*

## What I mean by taste

Models have been able to generate elaborate architecture for a while. Elaborate architecture is not the same thing as good architecture. In fact, one of the easiest failure modes to recognize in model-generated systems is the architecture astronaut: the model has encountered a sufficiently serious prompt and responds by producing every pattern it associates with seriousness.

This did not feel like that.

It covered a great deal of ground, especially because identity systems deserve a great deal of security attention, but the abstractions seemed to pay rent. Every major construct corresponded to a concrete failure mode. Every design phase had a gate. The plan moved from an explicit continuation store, to host-owned presentation, to a real signup vertical slice, to provider integrations and production behavior. Restartability, replay, browser flow, runtime replacement, and exact field projection were treated as things to test, not merely things to mention.

More importantly, the model was willing to seriously modify the core of the project. It did not weasel its way to a successful checklist by preserving a weak foundation and adding adapters. It first built the abstract layer it needed and then rebased the application on top of it.

That aggressiveness is part of what felt new. Previous models were often locally obedient. They optimized for making the requested change fit inside the current shape of the code, even when the current shape was the reason the change was difficult. Here the model was willing to say, in effect: the application does not yet contain the right machinery, so we will build the machinery first.

Taste is a dangerous word because it can collapse into “the model made choices I personally like.” I mean something more operational:

- it challenged the framing rather than blindly implementing it;
- it introduced a smaller language instead of exposing a larger API;
- it kept authority native and data explicit;
- it made each abstraction correspond to a validation rule and a testable boundary;
- it changed the foundation when the new requirement exposed a foundational mismatch;
- it stopped short of making the scripting language a general-purpose application runtime.

There are codebases where this would be absurdly overengineered. An identity provider is not one of them.

[**IMAGE 2 — implementation phases and gates**]

*Suggested caption: What kept the design from feeling like architecture theater was the implementation plan: each abstract mechanism had a phase, a concrete purpose, and an end-to-end gate.*

## LLMs as abstraction machines

I keep coming back to the idea that LLMs are abstraction machines.

Saying that they are pattern-matching machines is not wrong. It is just too low-resolution to be useful for the work I am doing. The interesting question is what kinds of patterns they can recognize, at what level, how they can coordinate several abstractions, and whether they can descend from the abstraction back into a working concrete system without losing the original constraints.

The movement looks roughly like this:

```text
concrete artifacts
    -> recognize a recurring structure
    -> move into an abstract representation
    -> coordinate it with other abstractions
    -> lower the result into new concrete artifacts
```

In the identity provider, the concrete artifacts were routes, forms, stores, callbacks, protocol handlers, credentials, and tests. The model moved upward into concepts such as evidence, authority, state transitions, effects, continuations, generations, and runtime ownership. It then coordinated those with programming-language patterns and lowered the result back into packages, schemas, registries, worker pools, validators, and integration tests.

Moving upward is not the difficult part by itself. Models have always been able to suggest abstractions. The difficult part is returning to the code without becoming vague.

An architecture astronaut can tell you to “use capabilities” or “model the flow as a state machine.” A useful system has to answer much less glamorous questions:

- What is the capability value?
- Who creates it?
- How is it versioned?
- Can it be retained by a closure?
- What happens after the invocation ends?
- How are Promise settlements routed back to a non-thread-safe VM?
- What can be stored in a continuation?
- What happens when a worker times out?
- How does a callback ID link to a closure in a fresh runtime?
- What happens to a continuation after a deployment?

The abstraction becomes real only when these details have one coherent answer.

This is also why I find language design to be such a strong probe of model capability. A model can write a persuasive architecture document while hiding contradictions in prose. A language forces the abstractions to become operational. The nouns need representations. The operations need signatures. The effects need interpreters. The invalid combinations need errors. The authority needs a location. The state needs a lifetime.

If the model can design a language and then implement its interpreter, it has to walk both directions on the abstraction ladder.

## Ask for a language first

One of my most reliable prompting techniques over the last several years has been to ask for a language before asking for the application.

“Language” here can mean many things. It may be a YAML DSL if the problem is mostly declarative. It may be a JavaScript API if I need bindings, functions, loops, branching, or asynchronous composition. It may be a set of Go interfaces, a widget tree, a query notation, a command language, or a small collection of typed builders.

The point is not to invent syntax for its own sake. The point is to find the boundary where domain concepts and computational concepts meet.

On the domain side, a logistics system contains things such as orders, shipments, refunds, routes, appointments, exceptions, and plans. An identity system contains identities, credentials, invitations, challenges, consent, and sessions. A RAG experiment system contains corpora, retrievers, rankers, prompts, evaluators, datasets, runs, and artifacts.

On the computational side, there are values, bindings, branches, loops, effects, state transitions, retries, transactions, serialization, concurrency, and failure.

Application complexity often accumulates at the seam between these two worlds. A domain expert says “add a refund workflow.” The implementation of that sentence may require a database state transition, permissions, a form, validation, money calculations, an audit event, a queue, a notification, a page, and CSS. A single prompt now asks the model to bridge from a high-level domain intention all the way to dozens of unrelated implementation details.

That is extremely token-intensive in a deeper sense than merely consuming context. The model has to repeatedly reconstruct the same abstraction bridge. Every new feature prompt contains a hidden request to rediscover the architecture.

If the project instead has a small language of workflows, forms, effects, and domain operations, “add a refund workflow” may become twenty lines of code. The language already contains the bridge. The model no longer needs to infer where validation belongs, how a form is rendered, how a transaction is committed, or how an error is represented. Those decisions have been made once in the interpreter.

This is why a good language changes the effective intelligence of the model. It reshapes the problem into a surface on which the model can generalize more reliably.

I wrote about this before as generalization shaping: notation, tools, code, and APIs reduce a messy problem into a smaller one with stronger regularities. The current identity-provider work feels like the same idea applied recursively. I asked the model to build a scripting language, and in doing so it exposed the computational DNA of the host application itself.

There is an old idea in computer science that if you can design a language in which the solution is easy to express, much of the original problem has disappeared. I think “programming language” can actually distract from this. Programming makes us think of an activity performed by programmers. The more fundamental thing is computational language: a way to describe which computations exist, what they mean, and which details are handled by the machine.

This matters even more with LLMs because they are, quite literally, language machines. We have spent decades building abstractions so humans can direct computers with more useful words. Now the machine that writes the instructions also benefits from those abstractions. A well-designed DSL does not only make a human programmer more productive. It gives the model a more stable semantic surface to operate on.

I have generated thousands of small languages and APIs over the last three or four years. That number sounds more systematic than the process has been. Most of it has been vibed. I try a notation, see where the model struggles, add a primitive, remove an escape hatch, move something from script to runtime, generate more examples, and gradually accumulate patterns I no longer consciously name.

Some of those patterns are obvious API design. Some come from Common Lisp, macros, interpreter design, and old-fashioned framework work. Some are specific to how LLMs respond to concepts with strong representation in the training corpus. Some are likely things I have rediscovered badly. Until now, the optimization loop has mostly depended on my own taste and on whether the generated applications feel clean.

The thing 5.6 changes is that the model can participate in the research loop around the language itself.

## From codebase to textbook

Once the identity-provider scripting layer existed, I wanted to know whether the model could step back out of the codebase and identify what had actually been built.

I asked it to study the branch and write a textbook or report about the interesting interpreter constructs: serialized continuations, invocation capabilities, deterministic callback registration, closed outcomes, secret handles, runtime leasing, generation-aware resumption, and the rest.

It produced a long monograph that was surprisingly concise at the level of ideas. It did not simply walk the directory tree and explain that one package contained workflows and another contained scripts. It reconstructed a dependency of concepts.

It began with the danger of scripting an identity provider. From there it explained why protocol authority had to remain native, why JavaScript outcomes had to be closed, why durable control flow could not be a suspended Promise, why callbacks needed stable identities, why capabilities had invocation lifetimes, why a worker could only be reused after positive evidence of quiescence, and why hot reload created semantic generations.

That is what I mean when I say the model can teach. It can synthesize a complex thinking workflow and arrange it so that the next concept is motivated by the previous one. It can give names to techniques that exist in code but may never have been named by the implementer. It can connect those techniques to a wider literature without reducing the document to a literature review.

In a way, it reverse-compiled the codebase:

```text
implementation
    -> invariants
    -> computational patterns
    -> named concepts
    -> explanatory sequence
```

I ended the morning with around two hundred pages of textbook-style material across several related investigations. Normally that amount of generated prose becomes exhausting very quickly. You can feel the entropy rise. Sections begin repeating one another, the narrative stops advancing, and the text becomes polished sludge.

This material remained interesting because each section had a job. There was simply a lot of material because the project contained a lot of machinery.

There is an obvious warning here: a beautiful explanation can be beautifully wrong. Documentation generated by the same model that wrote the code can become a self-consistent mythology. The useful version needs exact source links, implementation status, test references, distinctions between what exists and what is proposed, and explicit unresolved concerns.

But when it has those anchors, the ability to turn a large unfamiliar codebase into a readable conceptual textbook changes how ownership can work. I do not need to reconstruct the architecture from a thousand functions and a stream of diffs. I can read the narrative, inspect the source behind the load-bearing claims, and then use the document as a map for deeper review.

That matters because agentic coding is making code production much faster than code comprehension. A model that can produce both the system and an inspectable theory of the system is doing something qualitatively different from autocomplete.

## The language optimization loop

This is the part I am most interested in now.

If the model can research programming-language ideas without immediately losing the thread, then my informal “ask for a language first” technique can become a much more systematic language optimization loop.

The current loop is roughly:

```text
describe the domain
    -> ask for a DSL or JavaScript API
    -> implement a few examples
    -> notice awkwardness
    -> patch the API
    -> repeat
```

This works remarkably well, but it is artisanal. The evaluation criteria live mostly in my head. A construction feels too verbose. The model repeatedly misuses one primitive. An abstraction leaks implementation detail. A supposedly generic operator creates too much authority. A domain expert cannot read the resulting program. I change the language and try again.

A research-capable model makes a different loop possible.

Start with a corpus of representative tasks, not one feature request. For an identity system, these might include invitation signup, virtual users, account recovery, multi-factor challenge, policy denial, consent, provider selection, and migration of an in-progress browser workflow. For a RAG lab, they might include comparing retrievers, freezing a corpus, varying a prompt, evaluating with several metrics, caching provider calls, and reproducing a run months later.

Ask the model to infer the domain ontology and the computational requirements separately. Which concepts belong to the domain? Which operations are effects? Which values need stable identity? Which things are secret? Which actions are durable? Which parts need loops or branches? Which choices should remain native policy?

Then ask it to propose competing languages rather than one answer.

One design may be highly declarative and easy to analyze but awkward for complex control flow. Another may use JavaScript callbacks and be pleasant to author but expose too much dynamic behavior. A third may compile direct-style async functions into explicit state machines. A fourth may separate a pure policy language from a transactional effect language.

Implement the smallest possible interpreter for each serious candidate. Generate real programs. Have the model use the language, not merely praise it. Feed it tasks it has not seen. Ask a second model to use it. Ask a human to read the result. Collect the errors.

Now the language can be evaluated on several axes:

- How long are representative programs?
- How many concepts must an author learn?
- How often does the model request authority it does not need?
- How many invalid states can be represented?
- Which mistakes are caught statically?
- Which mistakes survive until runtime?
- How local is a change?
- How legible is a semantic diff?
- Can a program be explained from its manifest?
- Can the interpreter enforce the hard guarantees once for every program?
- How expensive is the implementation and proof burden?
- Does the language remain honest about the domain, or does it hide important complexity?

The research step then becomes part of the loop rather than something done once at the beginning. The model can search for analogous designs in workflow systems, capability languages, effect systems, durable execution frameworks, theorem provers, protocol state machines, and compiler workbenches. It can compare the candidate language to those ideas, identify missing distinctions, and propose experiments rather than merely adding fashionable terminology.

Then revise the language, rerun the corpus, and compare.

This is not just prompt optimization. It is not “find the magic phrasing that makes the model produce the right code.” The artifact being optimized is the computational language between the model and the application.

That distinction matters because prompts are ephemeral and local. A language compounds.

Once the IDP has a good workflow language, every future identity feature becomes easier. The interpreter centralizes the security properties. The examples become training material for humans and models. The compiler can infer capability use. The static analyzer can reject secrets crossing a continuation boundary. The runtime can meter host calls. The documentation generator can produce a diagram. The deployment system can show that a new version added one effect and changed one continuation schema.

The language becomes a piece of infrastructure that reshapes all later work.

There is also a peculiar possibility here: the model is simultaneously the language designer, the language user, and part of the evaluation harness.

That could be dangerous. A language optimized only for one model may become alien to humans or brittle across model generations. The model may exploit accidental cues rather than understand the semantics. It may prefer verbose forms because they resemble its training data, or compact forms that are impossible to maintain. We need human readability, independent interpreters, static checks, cross-model tests, and domain-expert review.

But it is also an extraordinary experimental setup. We can generate hundreds of representative programs, mutate them, ask models to repair them, compare error rates, measure the authority each version requests, and observe where the notation helps or hinders generalization. Language design has traditionally been expensive to test because recruiting many skilled users is difficult. Models are not substitutes for users, but they are extremely cheap additional users with interesting failure modes.

The loop could eventually operate above the level of one project.

Imagine a malleable JavaScript compiler or interpreter where a project defines:

- its value types;
- its capabilities;
- its effects;
- its durable operations;
- its secret and ownership rules;
- its cost model;
- its verification passes;
- its native bindings;
- its permitted language features.

Tiny-IDP would be one profile. A reproducible RAG laboratory would be another. A deployment orchestrator, document approval system, policy engine, or agent tool runtime could share the compiler and runtime machinery while exposing different computational worlds.

The compiler could turn a familiar JavaScript-shaped surface into a much smaller semantic intermediate representation. It could derive callback manifests, capability requirements, effect rows, continuation schemas, and resource budgets. Different backends could execute the same verified program: Goja for compatibility, a small interpreter for assurance, a symbolic backend for model checking, perhaps generated Go or WebAssembly for deployment.

The flagship feature for Tiny-IDP would be a `durable await` that looks like ordinary direct-style code to the author but compiles into the explicit continuation records the runtime already uses.

```javascript
const form = await durable.present(SignupForm);
const proof = await durable.emailCode(form.email);
return commit.signup(form, proof);
```

At each durable suspension point, the compiler performs liveness analysis. Which values are needed afterward? Can they be serialized? Are they public? Are they bounded? Are any of them capabilities, secrets, closures, Promises, native resources, or engine-specific objects? If so, compilation fails or the value must be converted into an approved native reference.

The author gets pleasant direct style. The runtime still gets a small, explicit, reviewable state machine. We improve usability without weakening the semantic boundary.

This is the direction I mean by a language optimization loop: not merely having the model generate more code, but having it research, propose, implement, use, analyze, and refine the language in which future code will be expressed.

[**IMAGE 3 — annotated reproducible RAG operator design**]

*Suggested caption: The same shape appearing in a second domain: trusted source packages, canonical artifacts, declared host capabilities, fresh constrained runtimes, typed results, and reproducibility evidence. That recurrence is what makes me think this is a general language pattern rather than an IDP-specific trick.*

## Research without collage

The research capability is what makes this feel possible now rather than merely aspirational.

In the past, I could ask a model to survey effect systems, capability security, durable workflows, and formal verification, but I had to act as the synthesis layer. I had to notice when two papers used similar words for different ideas, when an analogy was superficial, when a technique depended on a closed-world assumption that did not apply, or when the proposed application had quietly lost the original security boundary.

With 5.6, the model is better at maintaining the shape of the research question while moving across sources and then returning to the project. It is not only summarizing papers. It is deciding which ideas matter for this codebase, how they relate, and what concrete refactor would make them useful.

This is what I somewhat recklessly called “PhD-level” in conversation. I do not mean that it is producing a groundbreaking dissertation or that it should receive credentials. I mean the more ordinary but still difficult behavior of sustained technical research: map a literature, identify a tractable core, choose methods, apply them to a complicated artifact, document limitations, and keep the work coherent over many steps.

I do not think it is postdoc-level yet, if we are going to keep abusing the metaphor. I can see it overgeneralize. I can see it become too enchanted by a formalism. I can see places where the bibliography is stronger than the actual argument. I can see it benefit enormously from a human who has enough taste to reject a clean but irrelevant theory.

But the floor has moved. The model can remain inside the research loop long enough that I am no longer merely using it to retrieve and summarize material. I can use it to create a research program around a piece of software.

That changes the economics of ambitious engineering. Many ideas that were previously unreasonable for a small project—not because implementation was impossible, but because the research and synthesis cost was too high—become plausible experiments.

Static analysis for a small identity provider. Model checking for selected protocol transitions. A compiler that derives explicit continuations from JavaScript. A project-specific capability and effect system. A textbook that reverse-engineers the resulting architecture. A comparative language-design loop across two unrelated domains.

Each of these would traditionally be a substantial side project before the application itself could move forward. With a model that can keep the threads coordinated, they become things I can explore in parallel with production work.

That does not make them free. It changes which cost is scarce. Generating a great deal of coherent work becomes cheaper. Deciding what deserves to exist, defining acceptance evidence, and maintaining contact with reality become more important.

## The cracks, and why “unsupervised” cannot mean unaccountable

There is a dangerous version of this story where the conclusion is that the model can now research, architect, implement, verify, and document a system, so the human can simply stop paying attention.

That is not my conclusion.

I built a codebase I largely did not read, and that is interesting partly because it is uncomfortable. A system can have beautiful design documents, passing tests, formal-looking models, and a coherent textbook while still being wrong in ways none of those artifacts represent. Identity protocols have hostile environments, integration assumptions, operational failure modes, cryptographic boundaries, and deployment realities that do not disappear because the internal architecture is elegant.

The model can also create a self-confirming world. It writes the code, writes the tests, writes the design document, and then writes the textbook explaining why the design is good. Without independent anchors, coherence becomes a liability because it is persuasive.

The response is not to abandon the workflow. It is to make the evidence harder to fake.

That means executable conformance suites, adversarial tests, restart tests, replay tests, race detectors, browser integration, source-linked claims, canonical manifests, semantic diffs, explicit generation identities, traceable native effects, and independent review of the most security-sensitive boundaries. It means distinguishing “the model produced a plausible formal model” from “the implementation refines the model under stated assumptions.” It means retaining old generations when a continuation cannot be safely migrated rather than trusting a prose compatibility argument.

It also means treating unsupervised as a description of interaction frequency, not responsibility.

I can let the model work for several hours without steering every step. I cannot let the resulting system enter production without a theory of what evidence makes it acceptable.

This is part of why the language-first approach matters. A smaller language makes independent evidence more tractable. If arbitrary JavaScript owns the identity provider, the review surface is every possible program behavior. If JavaScript can only choose among typed capabilities and return closed outcomes, the trusted boundary is smaller. If browser workflows compile to explicit continuation graphs, they can be inspected. If effects are inert plans, native committers can enforce the transaction shape. If every artifact carries a semantic manifest, deployment review can focus on authority and state changes rather than only text diffs.

Abstraction is not an escape from verification. A good abstraction creates a place where verification can be applied once.

## Where I am in the model cycle

So, returning to the five stages.

Stage zero was immediate: 5.6 produced several outputs that were conspicuously better than what I had become used to.

Stage one was brief because ordinary coding was already working well enough that I did not initially know what the new capability changed. A better patch is still a patch.

Stage two arrived when the identity-provider research kept going. The model did not merely collect material. It altered the fundamental representation of the application, built a scripting system that rejected my naive framing, and then extracted a coherent programming-languages textbook from the result.

That was the *oh, fuck* moment. The unit of delegation had moved from implementation to research-backed system design.

I am entering stage three now. I can see the cracks. The model still needs carefully chosen artifacts. It can write too much. It can construct an elegant conceptual system faster than the empirical evidence accumulates. It needs explicit instructions to separate implemented behavior from proposals. It benefits from being asked for competing designs and falsification criteria rather than one grand synthesis. It needs independent tests and sometimes a second model or a human domain expert to challenge the result.

I am beginning to turn those cracks into techniques:

- ask for a language before an application;
- ask for multiple candidate languages before selecting one;
- force the compiler or interpreter contract to become explicit;
- maintain diaries and research artifacts so the path remains inspectable;
- require source-linked textbooks rather than detached explanations;
- use semantic manifests and end-to-end gates;
- make the model use the language it designed;
- optimize against a corpus of real tasks;
- preserve native authority around the things that cannot be delegated safely.

Stage four will be fluency: being able to prompt this kind of research and language evolution almost blindly because the workflow has become internalized. I am not there yet.

The unusual thing is that I can already see the next workflow taking shape.

It is not “ask a larger model to write a larger application.” It is something closer to:

```text
ask the model to discover the computational language of the domain
    -> implement and verify the interpreter
    -> express the application in that language
    -> observe where humans and models struggle
    -> research better abstractions
    -> evolve the language
    -> regenerate and recheck the application
```

That loop happens above the level of ordinary code generation. The code becomes one compiled artifact of a more important design activity.

## The abstraction machine

I have spent a lot of time over the last few years trying to find prompts that do not work. Since GPT-5, that has become harder in ordinary programming. The failures increasingly appear not at the level of syntax or local implementation, but at the level of framing: choosing the wrong abstraction, exposing too much authority, failing to define evidence, designing a language that does not match the domain, or optimizing the wrong thing.

5.6 seems materially better at operating in that layer.

It can look at a concrete codebase and recognize that the requested feature is actually a language-design problem. It can look at a collection of papers and identify the subset that changes the implementation. It can introduce an abstract fundamental layer, move the application onto it, and then produce a narrative that teaches the layer back to me. It can be systematic without automatically becoming maximalist. At its best, it can display something close to taste.

The deepest part of this for me is not that the model knows more programming-language terminology. It is that it can coordinate domain abstractions and computational abstractions.

A challenge in an identity system is simultaneously a human concept, a protocol event, a security boundary, a piece of evidence, a browser interaction, a durable state transition, and an input to future policy. A good language decides which of those aspects the script author sees and which the runtime owns. A good interpreter makes that division executable. A good compiler can make the convenient source form lower into the safe runtime form. A good textbook can explain why the division exists.

The model was able to move among all of these views without immediately dropping one.

That is why “abstraction machine” feels like the right phrase to me. Not because the model floats away from concrete details, but because it can move up and down the ladder: recognize patterns in the concrete, manipulate them in the abstract, and return them to the concrete as working machinery.

The next step is to make that movement itself more systematic.

I want to turn the thousands of small languages I have generated by feel into a real experimental loop. I want task corpora, competing notations, interpreters, model users, human readers, static analyses, semantic diffs, and research passes. I want to know which language shapes make models generalize cleanly, which abstractions reduce authority, which errors become impossible, and where elegance merely hides complexity.

Maybe this will devolve. Maybe 5.6 is still better at producing the appearance of a research program than at sustaining one. Maybe the cracks will become obvious once the novelty wears off. I have only been using it for a couple of weeks, and I have learned by now not to confuse the first successful project with a universal capability claim.

But this is the first time I have felt that the language optimization loop is not just a personal prompting trick. It may be a practical research method.

And that is a much larger change than writing code faster.

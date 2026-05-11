---
title: "What Is a Stack-Based VM?"
aliases:
  - stack machine
  - stack-based virtual machine
  - bytecode vm
  - operand stack
tags: [knowledge-base, on-ramp, vm, interpreter, bytecode, stack-machine]
status: active
type: knowledge-base
created: 2026-05-11
---

# What Is a Stack-Based VM?

> [!summary]
> A stack-based VM executes bytecodes by pushing values onto an operand stack and popping them off for operations. The idea is standard textbook material, but our projects need a practical orientation: how the operand stack relates to contexts, method calls, temporaries, and bytecode dispatch when you are actually building one.

## The idea in one paragraph

In a stack-based VM, instructions mostly do not name registers. Instead, they operate on the top of a stack. A bytecode like “push constant 3” puts a value on the stack. A bytecode like “add” pops the top two values, adds them, and pushes the result. This makes bytecodes compact and interpreters conceptually simple.

## Why we care

Our VM-oriented projects — especially [[PROJ - Smalltalk-80 VM - Blue Book Interpreter in Go]] and the uLisp/PicoCalc line of work — are much easier to read if you already understand the stack-machine mental model. Otherwise project reports get stuck in low-level details before the reader has the basic picture.

## The minimum model

A stack VM usually has at least:
- an **operand stack** for temporary values,
- a **program counter / instruction pointer**,
- a **call frame / context** describing the current method/function,
- bytecodes that manipulate the stack and control flow.

Tiny example:

```text
push 2     ; stack = [2]
push 3     ; stack = [2, 3]
add        ; pop 3 and 2, push 5   -> stack = [5]
push 4     ; stack = [5, 4]
mul        ; pop 4 and 5, push 20  -> stack = [20]
```

This is why stack VMs are often taught first: the execution model is visible.

## Why stack VMs are attractive

**Compact bytecodes.** The bytecode does not need to name a register for every operation.

**Simple interpreters.** The dispatch loop can be a tight “fetch instruction → mutate stack → continue” structure.

**Good fit for high-level languages.** Temporary expression results naturally live on the stack.

## What gets more complicated in real systems

The simple story hides real complexity:
- method calls create new contexts or frames,
- locals/temporaries need stable storage beyond the operand stack,
- closures or blocks may capture outer contexts,
- object models and method lookup interact with execution,
- garbage collection must understand live stack/frame roots.

This is exactly why our Smalltalk VM work spends so much time on contexts, sender/home relationships, method cache behavior, and object memory.

## The gotchas we've hit

**The operand stack is not the whole VM state.** Beginners often think “stack VM” means “everything is on one stack.” In real systems, call frames, temporaries, and object references live in a larger runtime structure.

**Context bugs look like random later crashes.** If the frame or context layout is wrong, the visible failure may appear many instructions later.

**Tagged integers and object references matter.** A VM often uses compact tagged representations, so even “just an integer” can have representation rules that leak into execution semantics.

## Where to go deeper

- [[PROJ - Smalltalk-80 VM - Blue Book Interpreter in Go]] — full Blue Book interpreter in Go
- [[Tribal/goja-execution-model]] — different kind of runtime, but useful contrast in execution ownership
- Smalltalk-80: *The Language and its Implementation* — classic reference for one real stack VM design

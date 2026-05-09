Read this article in [Chinese](http://blog.csdn.net/szengtal/article/details/78726143).

1. [Introduction](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-2-lexical-environments-ecmascript-implementation/#introduction "Introduction")
2. [Definitions](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-2-lexical-environments-ecmascript-implementation/#definitions "Definitions")
3. [Environment record types](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-2-lexical-environments-ecmascript-implementation/#environment-record-types "Environment record types")
	1. [Declarative environment record](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-2-lexical-environments-ecmascript-implementation/#declarative-environment-record "Declarative environment record")
		1. [Eval and inner functions may break optimizations](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-2-lexical-environments-ecmascript-implementation/#codeevalcode-and-inner-functions-may-break-optimizations "Eval and inner functions may break optimizations")
		2. [Object environment record](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-2-lexical-environments-ecmascript-implementation/#object-environment-record "Object environment record")
4. [Structure of execution context](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-2-lexical-environments-ecmascript-implementation/#structure-of-execution-context "Structure of execution context")
	1. [This binding](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-2-lexical-environments-ecmascript-implementation/#this-binding "This binding")
		2. [Variable environment](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-2-lexical-environments-ecmascript-implementation/#variable-environment "Variable environment")
		3. [Lexical environment](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-2-lexical-environments-ecmascript-implementation/#lexical-environment "Lexical environment")
5. [Identifier resolution](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-2-lexical-environments-ecmascript-implementation/#identifier-resolution "Identifier resolution")
6. [Conclusion](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-2-lexical-environments-ecmascript-implementation/#conclusion "Conclusion")
7. [Additional literature](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-2-lexical-environments-ecmascript-implementation/#additional-literature "Additional literature")

## Introduction

In this chapter we continue our consideration of lexical environments. In the previous [sub chapter 3.1](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-1-lexical-environments-common-theory/) we clarified the general theory related with the topic. In particular we have learned that the concept of environments is closely related with concepts of [static scope](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-1-lexical-environments-common-theory/#static-lexical-scope) and [closures](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-1-lexical-environments-common-theory/#closure).

We have also said that ECMAScript uses the model of [chained environment frames](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-1-lexical-environments-common-theory/#environment-frames-model). And in this part we’ll tackle with lexical environments implementation in exactly ECMAScript. In particular we’ll discuss structures and terminology used in ES to reflect this common theory.

We start from definitions. Though we already gave the definition of a lexical environment in the common theory, here we give it already relatively to the ECMA-262-5 standard.

## Definitions

As we said in the general theory, environments are used to manage data (variables, functions, etc.) of logically nested blocks of a code. In the same way they are used in ECMAScript.

A *lexical environment* defines the association of *identifiers* to the *values* of variables and functions based upon the lexical nesting structures of ECMAScript code.

And as also we have mentioned this association of the name with the value is called a [binding](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-1-lexical-environments-common-theory/#name-binding).

A lexical environment in ES consists of two components: it’s an *environment record* and a *reference* to the *outer environment*. I.e. the definition of an environment corresponds to a single frame from the [model](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-1-lexical-environments-common-theory/#environment-definition) we’ve discussed. Thus,

An *environment record* records the identifier bindings that are created within the scope of this lexical environment.

That is, an *environment record* is the *storage* of variables appeared in the context.

Let’s consider the following example:

```
var x = 10;

function foo() {
  var y = 20;
}
```

Then we have two abstract environments corresponding to the global context and the context of the `foo` function:

```
// environment of the global context

globalEnvironment = {

  environmentRecord: {

    // built-ins:
    Object: function,
    Array: function,
    // etc ...

    // our bindings:
    x: 10

  },

  outer: null // no parent environment

};

// environment of the "foo" function

fooEnvironment = {
  environmentRecord: {
    y: 20
  },
  outer: globalEnvironment
};
```

The *outer* reference as we can see is used to chain the current environment with the parent one. The parent environment of course may have its own *outer* link. And the *outer* link of the *global environment* is set to `null`.

The global environment is the final link of this *chain of scopes*. This reminds how the prototypal inheritance works in ES: if a property isn’t found in the object itself, it’s searched in its prototype, then in the prototype of the prototype and so on, until it’s found, either the final link of the prototype chain is considered. The same with environments: the variables (or identifiers) appear in the context stand for the properties, and the *outer* link stands for the reference to the prototype.

A lexical environment as we [mentioned](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-1-lexical-environments-common-theory/#environment-definition) may surrounds multiple inner lexical environments. E.g., if a function contains two nested functions then the lexical environments of each of the nested functions will have as their *outer* environment the environment of the surrounding function.

```
function foo() {

  var x = 10;

  function bar() {
    var y = 20;
    console.log(x + y); // 30
  }

  function baz() {
    var z = 30;
    console.log(x + y); // 40
  }

}

// ----- Environments -----

// "foo" environmnet

fooEnvironment = {
  environmentRecord: {x: 10},
  outer: globalEnvironment
};

// both "bar" and "baz" have the same outer
// environment -- the environment of "foo"

barEnvironment = {
  environmentRecord: {y: 20},
  outer: fooEnvironment
};

bazEnvironment = {
  environmentRecord: {z: 30},
  outer: fooEnvironment
};
```

ECMAScript defines two types of environment records. They are mostly for implementation purposes, but we consider them in some details to have complete understanding.

## Environment record types

There are two kinds of environment records in ES5 specification: *declarative* environment records and *object* environment records.

### Declarative environment record

*Declarative environment records* are used to handle variables, functions, formal parameters, etc. appeared in *function scopes* (in this case this is very [activation object](https://dmitrysoshnikov.com/ecmascript/javascript-the-core/#activation-object) which we know from ES3 series) and *`catch` clauses*.

For example:

```
// all: "a", "b" and "c"
// bindings are bindings of
// a declarative record

function foo(a) {
  var b = 10;
  function c() {}
}
```

In case of the `catch` clause the binding is the exception argument:

```
try {
  ...
} catch (e) { // "e" is a binding of a declarative record
  ...
}
```

In general case the bindings of declarative records are assumed to be stored *directly at low level of the implementation* (for example, in registers of a virtual machine, thus providing fast access). This is the main difference from the old *activation object* concept used in ES3.

That is, the specification doesn’t require (and even indirectly doesn’t recommend) to implement declarative records as simple objects which are *inefficient* in this case. The consequence from this fact is that declarative environment records are not assumed to be exposed directly to the user-level, which means we cannot access these bindings as e.g. properties of the record. Actually, we couldn’t also before, even in ES3 — there *activation object* also was *inaccessible* directly to a user (except though Rhino implementation which nevertheless exposed it via [\_\_parent\_\_](https://dmitrysoshnikov.com/ecmascript/chapter-2-variable-object/#feature-of-implementations-property-__parent__) property).

Potentially, declarative records allow to use complete [lexical addressing](http://mitpress.mit.edu/sicp/full-text/book/book-Z-H-35.html#%_sec_5.5.6) technique, that is to get the direct access to needed variables without any scope chain lookup — regardless the depth of the nested scope (if the storage is fixed and unchangeable, all variable addresses can be known even at compile time). However, ES5 spec doesn’t mention this fact directly.

So once again, the main thing which we should understand why it was needed to replace old *activation object* concept with the *declarative environment record* is first of all the *efficiency of the implementation*.

Thus, as Brendan Eich also [mentioned](https://mail.mozilla.org/pipermail/es-discuss/2010-April/010915.html) (the last paragraph) — the activation object implementation in ES3 was just “a bug”: *“I will note that there are some real improvements in ES5, in particular to Chapter 10 which now uses declarative binding environments. ES1-3’s abuse of objects for scopes (again I’m to blame for doing so in JS in 1995, economizing on objects needed to implement the language in a big hurry) was a bug, not a feature”*.

Abstractly, an environment with the declarative record, can be presented in this way (thus, property `type` is not from the spec, but my explanatory convention):

```
environment = {
  // storage
  environmentRecord: {
    type: "declarative",
    // storage
  },
  // reference to the parent environment
  outer: <...>
};
```

#### Eval and inner functions may break optimizations

Notice though, that `eval` function can break this efficient concept and fall back us to inefficient handling, since in this case it’s hard to determine which bindings will be required by `eval`.

For example, V8 implementation (as well as others I guess) optimizes functions not creating neither `arguments` object (if it’s not in the function’s body), nor capturing non-used parent variables. That is, such functions are lightweight, and captures only used lexical variables. I.e. if none of parent variables is used — such functions are even not closures.

Take a look on the `Scope Variables` section of a function which doesn’t use `eval` (screen is from Chrome’s dev-tools):

![[Attachments/d97ac594d532972d3a182c0df25cef04_MD5.png]]

And then the same function, but with “empty” `eval` call inside:

![[Attachments/224948bc00357c0f0ef153e8209ece8d_MD5.png]]

Since it’s not known in advance which data will be used inside the `eval`, we should create all “heavyweight stuff” — you see both, `arguments` object and the `Closure` property, i.e. the parent environment.

Moreover, take a look on the `outerFn` in the later case. It also creates `arguments` object since has inner function inside and therefore it’s hard to analyze will the inner function refer `arguments` or not.

However, this is just one of the implementations, though it allows us to see which optimizations can be provided and how these optimizations can be canceled.

Let’s consider the second environment record type — object environment record.

### Object environment record

In contrast, an *object environment record* is used to define association of variables and functions appeared in the *global context* and inside the `with` -statements. These are exactly those inefficient variable storage implemented as *simple objects* which we’ve just mentioned above. In this case bindings are the *properties of the objects*.

The object which stores the bindings of such a context is called the *binding object*.

In case of the global context, the variables are associated with the global object itself. Exactly because of this we have the ability to refer them as properties of the global object:

```
var a = 10;
console.log(a); // 10

// "this" in the global context
// is the global object itself
console.log(this.a); // 10

// "window" is the reference to the
// global object in the browser environment
console.log(window.a); // 10
```

In case of the `with` statement, variables can be associated with the properties of the `with` -object:

```
with ({a: 10}) {
  console.log(a); // 10
}
```

Every time when `with` statement is executed a new lexical environment with object environment record is created. Thus, the environment of the running context is set as the *outer* environment. Then the environment of the running context is *replaced* with this newly created environment. After the `with` execution is completed the environment of the context is restored to the previous state:

```
var a = 10;
var b = 20;

with ({a: 30}) {
  console.log(a + b); // 50
}

console.log(a + b); // 30, restored
```

In pseudo-code:

```
// initial state
context.lexicalEnvironment = {
  environmentRecord: {a: 10, b: 20},
  outer: null
};

// "with" executed
previousEnvironment = context.lexicalEnvironment;

withEnvironment = {
  environmentRecord: {a: 30},
  outer: context.lexicalEnvironment
};

// replace current environment
context.lexicalEnvironment = withEnvironment;

// "with" completed, restore the environment back
context.lexicalEnvironment = previousEnvironment;
```

Absolutely the same effect has a `catch` clause — it also replaces the running context’s lexical environment with the newly created one, though in contrast with `with` statement, `catch` clause as we said uses *declarative record* but not the *object*:

```
var e = 10;

try {
  throw 20;
} catch (e) { // replace the environment
  console.log(e); // 20
}

// and now it's restored back
console.log(e); // 10
```

Below we will see that these *temporary* environments of `with` statements and `catch` clauses play role in using *function expressions* inside them.

Because of inefficiency of object environment records, `with` statement is already [removed](https://dmitrysoshnikov.com/ecmascript/es5-chapter-2-strict-mode/#codewithcode-statement) from the ES5-strict.

Moreover, `with` statements often may cause confusions (because of the effect of variables and *function declarations* [hoisting](https://dmitrysoshnikov.com/notes/note-4-two-words-about-hoisting/)) and [some](https://dmitrysoshnikov.com/ecmascript/the-quiz/#q9) of [them](https://dmitrysoshnikov.com/ecmascript/chapter-4-scope-chain/#affecting-on-scope-chain-during-code-execution) are really [confusing](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-2-lexical-environments-ecmascript-implementation/#comment-7070) cases. This is also the reason why the `with` statement was removed from ES5-strict.

Removing the global object from the bottom of the scope chain is also planned for the ES.next. That is, the global environment record will be also *declarative* but not *object*. With the system of planned [modules](http://wiki.ecmascript.org/doku.php?id=harmony:modules), global bindings such as `parseInt`, `Math`, etc. will just be imported to the global context, but technically we won’t be able to refer global variables as properties of the global object anymore, since there will be no any global object.

Abstractly, an environment with the object environment record, can be presented in this way:

```
environment = {
  // storage
  environmentRecord: {
    type: "object",
    bindingObject: {
      // storage
    }
  },
  // reference to the parent environment
  outer: <...>
};
```

The spec notices that the *binding object* is a kind of *reflection* of the real object (e.g. the global object), but not all properties of the original object are included as properties of the binding object. For example, property names which are *not identifiers* are not included in the binding object, which is quite logical since we cannot refer them as variables from the code:

```
// global properties
this['a'] = 10; // included in the binding object
this['hello world'] = 20; // isn't included

console.log(a); // 10, can refer
console.log(hello world); // cannot, syntax error
```

However, the exact implementation details of how the binding and original objects are synchronized are omitted in the spec.

## Structure of execution context

Here we mention briefly the structure of the [execution context](https://dmitrysoshnikov.com/ecmascript/javascript-the-core/#execution-context) in ES5. It’s a little bit different than in ES3 and has the following properties:

```
ExecutionContextES5 = {
  ThisBinding: <this value>,
  VariableEnvironment: { ... },
  LexicalEnvironment: { ... },
}
```

We see that a context has both *Variable* and *Lexical* environments which cause often the confusion of spec readers. We’ll clarify them shortly, but here just briefly notice that this is mainly to distinguish the value of the `[[Scope]]` property of [function declarations](https://dmitrysoshnikov.com/ecmascript/chapter-5-functions/#function-declaration) (FD) and [function expressions](https://dmitrysoshnikov.com/ecmascript/chapter-5-functions/#function-expression) (FE).

So let’s consider the properties of the execution context.

### This binding

[This](https://dmitrysoshnikov.com/ecmascript/chapter-3-this/) value is now called *this binding* (though, “this value” combination of words is still in ES5 spec). However, beside the terminology change, there are no big changes in semantics (except the *strict mode*, where `this` value can be `undefined`). In the global context, `this` binding is still the global object itself:

```
(function (global) {
  global.a = 10;
})(this);

console.log(a); // 10
```

And inside a function context `this` value is [still](https://dmitrysoshnikov.com/ecmascript/chapter-3-this/#this-value-in-the-function-code) determined by the form of how the function is *called*. If it’s called with a [reference](https://dmitrysoshnikov.com/ecmascript/chapter-3-this/#-reference-type), then the *base value* of the reference is used as `this` value, in all other cases — either global object or `undefined` in [strict mode](https://dmitrysoshnikov.com/ecmascript/es5-chapter-2-strict-mode/) is used for `this`.

```
var foo = {
  bar: function () {
    console.log(this);
  };
};

// --- Reference cases ---

// with a reference
foo.bar(); // \`this\` is foo - the base

var bar = foo.bar;

// with the reference
bar(); // \`this\` is the global or undefined, implicit base
this.bar(); // the same, explicit base, the global

// with also but another reference
bar.prototype.constructor(); // \`this\` is bar.prototype

// --- non-Reference cases ---

(foo.bar = foo.bar)(); // \`this\` is global or undefined
(foo.bar || foo.bar)(); // \`this\` is global or undefined
(function () { console.log(this); })(); // \`this\` is global or undefined
```

Notice again, in strict mode, it’s not possible anymore to get the global object with such a trick:

```
(function () {
  "use strict";
  var global = (function () { return this; })();
  console.log(global); // undefined!
})();
```

The techniques of how to handle this situation (including [indirect calls](https://dmitrysoshnikov.com/ecmascript/es5-chapter-2-strict-mode/#indirect-eval-call) to `eval`) are described in the [strict mode](https://dmitrysoshnikov.com/ecmascript/es5-chapter-2-strict-mode/#codethiscode-value-restrictions) chapter.

Let’s back to environments now and see what do *Variable* and *Lexical* environment components of the context mean in the spec. These two components that’s said cause often a confusion and unfortunately incorrectly described in some explanations.

### Variable environment

*Variable environment* component is exactly the initial storage of variables and functions of the context. Exactly its environment record is used as the data storage and is filled on [entering the context](https://dmitrysoshnikov.com/ecmascript/chapter-2-variable-object/#entering-the-execution-context) stage. This is very [variable object](https://dmitrysoshnikov.com/ecmascript/javascript-the-core/#variable-object) from ES3.

When entering the context of a function, recall also that a special `arguments` object is created which stores the values of formal parameters. In the *strict mode*, the `arguments` object has undergone [several changes](https://dmitrysoshnikov.com/ecmascript/es5-chapter-2-strict-mode/#codeevalcode-and-codeargumentscode-restrictions) among which are that the `arguments` does *not* [share](https://dmitrysoshnikov.com/ecmascript/chapter-2-variable-object/#variable-object-in-function-context) anymore values of its properties and real argument variables. Property `callee` (the reference to the function itself) was also [deprecated](https://dmitrysoshnikov.com/ecmascript/es5-chapter-2-strict-mode/#codecalleecode-and-codecallercode-restrictions) in strict mode.

For the code:

```
function foo(a) {
  var b = 20;
}

foo(10);
```

abstractly we have the following `VariableEnvironment` component of the `foo` function context:

```
fooContext.VariableEnvironment = {
  environmentRecord: {
    arguments: {0: 10, length: 1, callee: foo},
    a: 10,
    b: 20
  },
  outer: globalEnvironment
};
```

So what is `LexicalEnvironment` component then? The funny thing is that *initially* it’s just a *copy* of the `VariableEnvironment`.

### Lexical environment

Both `VariableEnvironment` and `LexicalEnvironment` by their nature are *lexical environments* (regardless possible confusion in their naming), i.e. both statically *(lexically)* captures the outer bindings for inner functions created in the context.

As we’ve just mentioned, initially (when the context is activated) the `LexicalEnvironment` component is just the blue-print *copy* of the `VariableEnvironment`. Considering the example from above, we have:

```
fooContext.LexicalEnvironment = copy(fooContext.VariableEnvironment);
```

However what happens next, at [code execution stage](https://dmitrysoshnikov.com/ecmascript/chapter-2-variable-object/#code-execution), is already related with the *augmenting* of the lexical environment by the `with` statements and `catch` clauses (though, as we said, in ES5 it’s already *replacement* of the context’s environment, but not augmentation as it [was](https://dmitrysoshnikov.com/ecmascript/chapter-4-scope-chain/#affecting-on-scope-chain-during-code-execution) in ES3).

The `with` statement and `catch` clause as was shown above *replace* the context’s environment for the time of their execution. And this case is related with *function expressions*.

From discussed [rules of function creation](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-1-lexical-environments-common-theory/#rules-of-function-creation-and-application), we know that a *closure* saves the lexical environment of the context in which it is created.

If a function expression (FE) is created inside a `with` statement (or a `catch` clause), it *should* save exactly *this current (replaced)* lexical environment.

Had we replaced the `VariableEnvironment` itself (instead of copied `LexicalEnvironment`), then we should have been *restore* it back after the `with` is completed. However this would mean, that FE would not be able to refer bindings which were created *during* the `with` statement execution, but the FE is needed these `with` -bindings.

Moreover, we can’t replace `VariableEnvironment` itself, because a FD can be also *called* inside the `with` statement, but in contrast with FE, FD should continue use binding values from initial state, and not from the `with` -object (we’ll see it on example below).

This is why, closures formed as *function declarations* (FD) save the `VariableEnvironment` component as their `[[Scope]]` property, and function expressions (FE) save exactly `LexicalEnvironment` component in this case. This is the main (and actually the only) reason of separation of these two, at first glance the same, components.

This fact becomes even more funny if to take into account that `with` statement is going to disappear completely from ES (in ES.next) as it did in ES5-strict. Once it’s happened, ES spec will be less confusing in this respect.

So let’s show again what we’ve just analyzed: FE saves `LexicalEnvironment`, since it’s needed the dynamic bindings created during the `with` execution, and FD saves `VariableEnvironment` since, by the spec cannot be created inside a block at all and is [hoisted](https://dmitrysoshnikov.com/notes/note-4-two-words-about-hoisting/) to the top.

```
var a = 10;

// FD
function foo() {
  console.log(a);
}

with ({a: 20}) {

  // FE
  var bar = function () {
    console.log(a);
  };

  foo(); // 10!, from VariableEnvrionment
  bar(); // 20,  from LexicalEnvrionment

}

foo(); // 10
bar(); // still 20
```

Schematically it looks like:

```
// "foo" is created
foo.[[Scope]] = globalContext.[[VariableEnvironment]];

// "with" is executed
previousEnvironment = globalContext.[[LexicalEnvironment]];

globalContext.[[LexicalEnvironment]] = {
  environmentRecord: {a: 20},
  outer: previousEnvironment
};

// "bar" is created
bar.[[Scope]] = globalContext.[[LexicalEnvironment]];

// "with" is completed, restore the environment
globalContext.[[LexicalEnvironment]] = previousEnvironment;
```

To see this distinction even more in action, we can take non-standard handling of FD which are placed *inside* blocks. By the spec [as we remember](https://dmitrysoshnikov.com/ecmascript/chapter-5-functions/#implementations-extension-function-statement) it should be a syntax error, but none of implementations throws it today, but handles this case in their own manner. Firefox had its own non-standard extension known as [Function Statements](https://dmitrysoshnikov.com/ecmascript/chapter-5-functions/#implementations-extension-function-statement) (FS), for years, and in ES5 other implementations, e.g. Chrome’s V8, had the following behavior:

```
var a = 10;

with ({a: 20}) {

  // FD
  function foo() { // do not test in Firefox!
    console.log(a);
  }

  // FE
  var bar = function () {
    console.log(a);
  };

  foo(); // 10!, from VariableEnvrionment
  bar(); // 20,  from LexicalEnvrionment

}

foo(); // 10
bar(); // still 20
```

And this is again happened because FD (being hoisted to the top in this case) saves `VariableEnvironment` component as its `[[Scope]]`, and the FE — the `LexicalEnvironment` which is replaced for the moment of `with` (or `catch`) work.

Note: since ES6 standardized block-level function declarations, and in the example above function `foo` also captures the lexical environment.

In abstract definitions and talks though, it’s possible not to make a strict distinction between these two components (for example when it’s not so essential environment of which exactly function type, declaration or expression is meant), therefore we may always say just *lexical environment* of a context.

However, exactly `LexicalEnvironment` component participates in the process of *identifier resolution*.

## Identifier resolution

Identifier resolution is the process of determining the binding of an identifier appeared in the context using the `LexicalEnvironment` component of the running execution context.

In other words, it’s the very [scope chain lookup](https://dmitrysoshnikov.com/ecmascript/javascript-the-core/#scope-chain) of variables. As we have said above, it’s similar to the prototype chain look up, just instead of prototype link, the `outer` link of an environment is considered.

Having the following example:

```
var a = 10;

(function foo() {

  var b = 20;

  (function bar() {

    var c = 30;
    console.log(a + b + c); // 60
    
  })();

})();
```

the identifier resolution for e.g. `a` binding is recursively managed with the following algorithm:

```
function resolveIdentifier(lexicalEnvironment, identifier) {
 
  // if it's the final link, and we didn't find
  // anything, we have a case of a reference error
  if (lexicalEnvironment == null) {
    throw ReferenceError(identifier + " is not defined");
  }
 
  // return the binding (reference) if it exists;
  // later we'll be able to get the value from the reference
  if (lexicalEnvironment.hasBinding(identifier)) {
    return new Reference(lexicalEnvironment, identifier);
  }
 
  // else try to find in the parent scope,
  // recursively analyzing the outer environment
  return resolveIdentifier(lexicalEnvironment.outer, identifier);

}

resolveIdentifier(bar.[[LexicalEnvironment]], "a") ->

-- bar.[[LexicalEnvironment]] - not found,
-- bar.[[LexicalEnvironment]].outer (i.e. foo.[[LexicalEnvironment]]) -> not found
-- bar.[[LexicalEnvironment]].outer.outer -> found reference, value 10
```

## Conclusion

In this chapter we clarified the concept of lexical environments in ECMAScript. We also have talked about the reasons of why it was needed to change old concepts of variable/activation objects and scope chains with chained lexical environments — most of these changes are related with efficiency of implementations.

We also have seen that the concept of lexical environments is closely related with the concept of closures (and noted again, that both, FD and FE in ECMScript are closures). We restored the concept of `this` binding and recall how it’s determined in different execution contexts.

Besides, we also have mentioned some plans related with environments for future version of ES, such as e.g. removing the global object. Hope this and the previous [chapter 3.1](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-1-lexical-environments-common-theory/) helped to see and understand the concept of lexical environments in detail. If you have questions, as always I’ll be glad to answer them in comments.

## Additional literature

ECMA-262-5 in detail:

- [Chapter 3.1. Lexical environments: Common Theory](https://dmitrysoshnikov.com/ecmascript/es5-chapter-3-1-lexical-environments-common-theory/)

ECMA-262-5 specification:

- [10.2 Lexical Environments](http://es5.github.com/#x10.2)
- [10.2.1 Environment Records](http://es5.github.com/#x10.2.1)
- [10.2.1.1 Declarative Environment Records](http://es5.github.com/#x10.2.1.1)
- [10.2.1.2 Object Environment Records](http://es5.github.com/#x10.2.1.2)
- [10.2.2.1 GetIdentifierReference](http://es5.github.com/#x10.2.2.1)
- [10.3 Execution Contexts](http://es5.github.com/#x10.3)
- [10.3.1 Identifier Resolution](http://es5.github.com/#x10.3.1)

  
  
**Written by:** Dmitry A. Soshnikov.  
**Published on:** 2011-07-26.
This post examines some of the details of how environments are handled in the ECMAScript 5 (ES5) specification \[1\]. In particular, there isn’t a single “current environment” in ES5, but two: the LexicalEnvironment and the VariableEnvironment. A piece of code at the end exploits these ES5 internals to produce different results on Firefox and Chrome.

**Note:** You will have a much easier time understanding this post if you already know how environments work in ECMAScript 5.

Let us start with a quick summary of environments and execution contexts in ECMAScript 5:

> *Lexical environments* hold variables and parameters. The currently active environment is managed via a stack of *execution contexts* (which grows and shrinks in sync with the call stack). Nested scopes are handled by chaining environments: each environment points to its *outer* environment (whose scope surrounds its scope). In order to enable lexical scoping, functions remember the *scope* (=environment) they were defined in. When a function is invoked, a new environment is created for is arguments and local variables. That environment’s outer environment is the function’s scope.

Another concept that is important to understand is *hoisting*: In JavaScript, any variable declaration var x=v; is split into two parts:
- The declaration is moved to the beginning of the surrounding function as var x;.
- The initializer becomes a simple assignment x=v; that replaces the declaration.
That means that even declarations made inside blocks such as for loops are made at function scope. This dominance of the function scope is the main motivation for keeping two current environments, as we shall see below.

## Data structures

![[Attachments/e5b1afc038364f75b330def35f4eb6ef_MD5.jpg]] A (lexical) environment is the following data structure \[ES5, 10.2\]:
- A reference to the outer environment (null in the global environment).
- An *environment record* maps identifiers to values. There are two kinds of environment records:
	- declarative environment records: store the effects of variable declarations, and function declarations.
		- object environment records: are used by the with statement and for the global environment. They turn an object into an environment. For with, that is the argument of the statement. For the global environment, that is the global object.
An execution context has the following fields \[ES5, 10.3\]:
- Environments: two references to environments.
	- LexicalEnvironment (lookup and change existing): resolve identifiers.
		- VariableEnvironment (add new): hold bindings made by variable declarations and function declarations.
	Both are usually the same. The next sections explain situations where they diverge.
- ThisBinding: the current value of this.

## Handling temporary scopes via LexicalEnvironment and VariableEnvironment

![[Attachments/0e66543a635dd0b85bc08161e8b7e4a8_MD5.jpg]] LexicalEnvironment and VariableEnvironment are always the same, except in one case: When there is a dominant outer scope and one temporarily wants to enter an inner scope. In the inner scope, a few new bindings should be accessible, but all new bindings made inside of it should be added to the outer scope. This is done as follows:
- LexicalEnvironment temporarily points to a new environment that has been put in front of the old LexicalEnvironment. The new environment holds the temporary bindings of the inner scope.
- VariableEnvironment does not change its value and is thus still the same as the old LexicalEnvironment, denoting the outer scope. New bindings are added here and will also be found when doing a lookup via LexicalEnvironment, because the latter comes before the former in the environment chain.
- After leaving the temporary scope, LexicalEnvironment’s old value is restored and it is again the same as VariableEnvironment.
These differences matter for with statements and catch clauses, which create temporary scopes. In both cases, the dominant scope is the surrounding function.
1. with statement \[ES5, 12.10\]: the object that is the argument of the statement becomes a temporary environment.
2. catch clause \[ES5, 12.14\]: the exception that is the argument of this clause is made available via a temporary environment.

## Functions and their scope: declarations versus expressions

Another area where the difference between LexicalEnvironment and VariableEnvironment can be observed are function definitions: function declarations use the VariableEnvironment as scope, while function expressions use the LexicalEnvironment. For function declarations, the motivation is to move the declaration to the (dominant) function scope. They should thus only see what exists at that level. The following code example illustrates how that works.
```
var foo = "abc";
    with({ foo: "bar" }) {
       function f() {
           console.log(foo);
       }
       f();
    }
```
Console output is “bar” on Firefox and Rhino, “abc” on V8 (Chrome, node.js). The latter more closely mirrors the specification, the former is probably what most programmers would expect.

If you instead use a function expression, the output is “bar” on all platforms.

```
var foo = "abc";
    with({ foo: "bar" }) {
        (function() { console.log(foo); }());
    }
```
\[Thanks to Allen Wirfs-Brock for helping me understand some of the finer points of LexicalEnvironment and VariableEnvironment.\]

References:

1. [Standard ECMA-262: ECMAScript Language Specification](http://www.ecma-international.org/publications/standards/Ecma-262.htm)
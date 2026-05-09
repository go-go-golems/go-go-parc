Many articles explain the differences between `var`, `let`, and `const` using terms such as **hoisting**, **Temporal Dead Zone(TDZ)**, **functional** and **block scope**, etc., often without referencing the standard. Some of those terms are not even included in the language standard. It's perfectly fine to explain the topic without referencing the language standard. However, I explain the topic by referencing it for those who want to dig a bit deeper, as understanding the ECMAScript standard is crucial for a comprehensive grasp of JavaScript.  

## ECMAScript

Many organisations have their references for JavaScript, such as [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript), [javascript.info](http://javascript.info/), and others. However, there is one standards organisation whose sole purpose is to standardise and document computer systems. This organisation is [Ecma International](https://ecma-international.org/), a reliable authority in the field. The organisation maintains a standard called [ECMA-262](https://ecma-international.org/publications-and-standards/standards/ecma-262/), a company's internal number to identify the standard. Ecma International defines this standard as the backbone of the ECMAScript general-purpose programming language, which we commonly call JavaScript. Understanding this standard is key to understanding the language itself. The latest standard as of August 2024 is the 15th edition of ECMAScript, also known as [**ECMAScript 2024**](https://262.ecma-international.org/15.0/index.html?_gl=1*t6jy41*_ga*MTI0NjkxODY1MC4xNzIxOTMxODM0*_ga_TDCK4DWEPP*MTcyNDUwMDI1OS4zNy4xLjE3MjQ1MDA5MjYuMC4wLjA.).  

## Execution Context

To understand the differences between `var`, `let`, and `const`, it's essential to understand the concept of [`Execution Context`](https://262.ecma-international.org/15.0/index.html?_gl=1*hea1h0*_ga*MTI0NjkxODY1MC4xNzIxOTMxODM0*_ga_TDCK4DWEPP*MTcyMTkzMTgzMy4xLjEuMTcyMTkzMjE1My4wLjAuMA..#running-execution-context).

`Execution Context` is an abstract structure defined in the ECMAScript standard. It is the environment where the current code is executed. To simplify things, we can assume a `Global Execution Context` and a `Functional Execution Context` exist.  

```
// Global Execution Context
let globalVariable = 'This is a global variable'

function outerFunction() {
  // Outer Function Execution Context
  let outerVariable = 'This is an outer variable'

  function innerFunction() {
    // Inner Function Execution Context
    let innerVariable = 'This is an inner variable'
  }

  innerFunction()
}

outerFunction()
```

To track the code's execution, `Execution Context` includes several components, known as state components. Among these, the `LexicalEnvironment` and `VariableEnvironment` are crucial when understanding the behaviour of `var`, `let`, and `const` keywords.  
  
Both `LexicalEnvironment` and `VariableEnvironment` are [`Environment Records`](https://262.ecma-international.org/15.0/index.html?_gl=1*hea1h0*_ga*MTI0NjkxODY1MC4xNzIxOTMxODM0*_ga_TDCK4DWEPP*MTcyMTkzMTgzMy4xLjEuMTcyMTkzMjE1My4wLjAuMA..#sec-environment-records). `Environment Record` is also an abstract data structure defined in the ECMAScript standard. It establishes the association of `Identifier` s to specific variables and functions. An `Identifier` is a name that references values, functions, classes and other data structures in JavaScript. In the following example, `let variable = 42`, `variable` is the variable's name (`Identifier`) that stores the value of the number 42.  
  
Every time code is executed, the `Execution Context` creates a new `Environment Record`. Besides storing `Identifier` s `Environment Record` has an `[[OuterEnv]]` field, either `null` or a reference to an outer `Environment Record`.  
  
Graphically, `Execution Context` and `Environment Record` from the previous example could be represented like this:  

```
// Global Execution Context
{
  // Environment Record
  {
    identifier: 'globalVariable'
    value: 'This is a global variable'
  }
  {
    identifier: 'outerFunction'
    value: Function
  }
  [[OuterEnv]]: null
}

// Outer Function Execution Context
{
  // Environment Record
  {
    identifier: 'outerVariable'
    value: 'This is an outer variable'
  }
  {
    identifier: 'innerFunction'
    value: Function
  }
  [[OuterEnv]]: Global Execution Context
}

// Inner Function Execution Context
{
  // Environment Record
  {
    identifier: 'innerVariable'
    value: 'This is an inner variable'
  }
  [[OuterEnv]]: Outer Function Execution Context
}
```

Another important point to remember about the `Execution Context` is that it has two distinct phases: the **Creation Phase** and the **Execution Phase**. These two phases are vital in understanding the difference between `var` and `let` or `const`.  

## Let and Const Declarations

In the paragraph [14.3.1 Let and Const Declarations](https://262.ecma-international.org/15.0/index.html?_gl=1*hea1h0*_ga*MTI0NjkxODY1MC4xNzIxOTMxODM0*_ga_TDCK4DWEPP*MTcyMTkzMTgzMy4xLjEuMTcyMTkzMjE1My4wLjAuMA..#sec-declarations-and-the-variable-statement) of ECMAScript standard the following is stated:

> `let` and `const` declarations define variables that are scoped to the running execution context's `LexicalEnvironment`. The variables are created when their containing `Environment Record` is instantiated but may not be accessed in any way until the variable's `LexicalBinding` is evaluated. A variable defined by a `LexicalBinding` with an `Initializer` is assigned the value of its `Initializer` 's `AssignmentExpression` when the `LexicalBinding` is evaluated, not when the variable is created. If a `LexicalBinding` in a let declaration does not have an Initializer the variable is assigned the value undefined when the `LexicalBinding` is evaluated.

To understand this statement, I will explain it sentence by sentence.

> `let` and `const` declarations define variables that are scoped to the running execution context's `LexicalEnvironment`.

It means variables created with the `let` or `const` keywords are scoped to the block where they were defined. The code block is any JavaScript code inside the curly braces.  

```
let condition = true
if (condition) {
  let blockScopedVariable = 'This is a block-scoped variable'
  console.log(blockScopedVariable) // This is a block-scoped variable
}

console.log(blockScopedVariable) // ReferenceError: blockScopedVariable is not defined

// Global Execution Context
{
  // Environment Record
  {
    identifier: 'condition'
    value: true
  }
  [[OuterEnv]]: null
  // Block Environment Record
  {
    identifier: 'variable'
    value: 'This is a block-scoped variable'
  }
  [[OuterEnv]]: Global Execution Context 
}
```

> The variables are created when their containing `Environment Record` is instantiated but may not be accessed in any way until the variable's `LexicalBinding` is evaluated.

As previously mentioned, the `Execution Context` has two phases. This statement means that during the **Creation Phase** of the `Execution Context`, variables are stored in their corresponding `Environment Record` but have not yet been assigned any value. They are `uninitialised`.  

```
console.log(varaible) // ReferenceError: Cannot access 'varaible' before initialization

let varaible = 42

// Global Execution Context Creation Phase
{
  // Environment Record
  {
    identifier: 'variable'
    value: uninitialised
  }
  [[OuterEnv]]: null
}
```

Because the variable is already created (instantiated) in the `Environment Record`, the `Execution Context` knows about it but can't access it before evaluation(the **Execution Phase** of the `Execution context`). The state of the variable being uninitialised is also known as a **Temporary Dead Zone(TDZ)**. We would have a different error if the variable hadn't been created in the `Environment Record`.  

```
console.log(varaible) // ReferenceError: varaible is not defined

// Global Execution Context Creation Phase
{
  // Environment Record
  {
  }
  [[OuterEnv]]: null
}
```

> A variable defined by a `LexicalBinding` with an `Initializer` is assigned the value of its `Initializer` 's `AssignmentExpression` when the `LexicalBinding` is evaluated, not when the variable is created.

`LexicalBinding` is a form of the `Identifier`, which represents the variable's name. The `Initializer` is the variable's value, and `AssignmentExpression` is the expression used to assign that value to the variable's name, such as the '=' sign in `let variable = 42`. Therefore, the statement above means that variables created with `let` or `const` keywords are assigned their value during the **Execution Phase** of the `Execution Context.`  

```
let variable = 42

// Global Execution Context Creation Phase
{
  // Environment Record
  {
    identifier: 'variable'
    value: uninitialised
  }
  [[OuterEnv]]: null
}

// Global Execution Context Execution Phase
{
  // Environment Record
  {
    identifier: 'variable'
    value: 42
  }
  [[OuterEnv]]: null
}
```

> If a `LexicalBinding` in a let declaration does not have an Initializer the variable is assigned the value undefined when the `LexicalBinding` is evaluated.

This means that if a `let` variable is created without an initial value, `undefined` is assigned to it during the **Execution Phase** of the `Execution Context.` Variables declared with the `const` keyword behave differently. I will explain it in a few paragraphs later.  

```
let variable
// Global Execution Context Creation Phase
{
  // Environment Record
  {
    identifier: 'variable'
    value: uninitialised
  }
  [[OuterEnv]]: null
}

// Global Execution Context Execution Phase
{
  // Environment Record
  {
    identifier: 'variable'
    value: undefined
  }
  [[OuterEnv]]: null
}
```

The standard also defines a subsection called [14.3.1.1 'Static Semantics: Early Errors](https://262.ecma-international.org/15.0/index.html?_gl=1*hea1h0*_ga*MTI0NjkxODY1MC4xNzIxOTMxODM0*_ga_TDCK4DWEPP*MTcyMTkzMTgzMy4xLjEuMTcyMTkzMjE1My4wLjAuMA..#sec-let-and-const-declarations-static-semantics-early-errors),' which explains other essential aspects of variables defined with the `let` and `const` keywords.

> *LexicalDeclaration*: *LetOrConst* *BindingList*;
> 
> - It is a `Syntax Error` if the `BoundNames` of `BindingList` contains "let".
> - It is a `Syntax Error` if the `BoundNames` of `BindingList` contains any duplicate entries. *LexicalBinding*: *BindingIdentifier* *Initializer*
> - It is a `Syntax Error` if `Initializer` is not present and `IsConstantDeclaration` of the `LexicalDeclaration` containing this `LexicalBinding` is true.

*LetOrConst* is a grammar rule which specifies that variable declarations can start with the `let` or `const` keywords.  
*BindingList* is a list of variables declared with `let` or `const` keywords. We could imagine *BindingList* as a data structure like this:  

```
let a = 1
let b = 2
let c = 3
const d = 4
const e = 5

BindingList: [
    { 
        identifier: 'a',
        value: 1
    },
    { 
        identifier: 'b',
        value: 2
    },
    { 
        identifier: 'c',
        value: 3
    },
    { 
        identifier: 'd',
        value: 4
    },
    { 
        identifier: 'e',
        value: 5
    }
]
```

A `Syntax Error` is an error that breaks the language's grammatical rules. They occur before the code's execution. Let's analyse the first `Syntax Error`.

> - It is a `Syntax Error` if the `BoundNames` of `BindingList` contains "let".

The `BoundNames` of `BindingList` are the names of variables declared with let or const keywords.  

```
let a = 1
let b = 2
let c = 3
const d = 4
const e = 5

BoundNames: ['a', 'b', 'c', 'd', 'e']
```

A Syntax Error will occur when the `BoundNames` list contains “let”.  

```
let let = 1 // SyntaxError: let is disallowed as a lexically bound name
const let = 1 // SyntaxError: let is disallowed as a lexically bound name
```

> - It is a `Syntax Error` if the `BoundNames` of `BindingList` contains any duplicate entries.

It means we can't use the same names for variables declared with the `let` or `const` keywords if they are already used in that scope.  

```
let a = 1
let a = 2 // SyntaxError: Identifier 'a' has already been declared
```

> - It is a `Syntax Error` if `Initializer` is not present and `IsConstantDeclaration` of the `LexicalDeclaration` containing this `LexicalBinding` is true.

`IsConstantDeclaration` is an abstract operation in the standard that checks if the variable is declared with the `const` keyword. This rule could be decrypted like that: if `IsConstantDeclaration` is `true` and the variable doesn't have an `Initializer`, a `Syntax Error` will be returned.  

```
const x; // SyntaxError: Missing initializer in const declaration
```

Another vital thing only related to the `const` keyword: variables declared with the `const` keyword can't be reassigned. It is not stated explicitly in the standard, but we can get it from the `IsConstantDeclaration` operation and the syntax rule that variables declared with the `const` keyword should always be initialised with the `Initializer`  

```
const variable = 42
variable = 46 // TypeError: Assignment to constant variable
```

## Variable Statement

Before 2015, when the ECMAScript 2015 wasn't released yet, only the `var` keyword was available to create a variable in JavaScript.

In the paragraph [14.3.2 Variable Statement](https://262.ecma-international.org/15.0/index.html?_gl=1*hea1h0*_ga*MTI0NjkxODY1MC4xNzIxOTMxODM0*_ga_TDCK4DWEPP*MTcyMTkzMTgzMy4xLjEuMTcyMTkzMjE1My4wLjAuMA..#sec-variable-statement) of ECMAScript standard the following is stated:

> A var statement declares variables scoped to the running `execution context` 's `VariableEnvironment`. `Var` variables are created when their containing `Environment Record` is instantiated and are initialized to undefined when created. Within the scope of any `VariableEnvironment` a common `BindingIdentifier` may appear in more than one `VariableDeclaration` but those declarations collectively define only one variable. A variable defined by a `VariableDeclaration` with an `Initializer` is assigned the value of its `Initializer` 's `AssignmentExpression` when the `VariableDeclaration` is executed, not when the variable is created.

I again explain it sentence by sentence.

> A var statement declares variables scoped to the running `execution context` 's `VariableEnvironment`.

This means that variables declared with the `var` keyword are either function-scoped if declared inside a function or global-scoped if declared outside any function.  

```
let condition = true
if (condition) {
    var globalVariable = 'This is a global variable'
}

console.log(globalVariable ) // This is a global variable

function outerFunction() {
  // Outer Function Execution Context
  var outerVariable = 'This is an outer variable'
}

outerFunction()

// Global Execution Context
{
  // Environment Record
  {
    identifier: 'condition'
    value: true
  }
  {
    identifier: 'globalVariable'
    value: 'This is a global variable'
  }
  {
    identifier: 'outerFunction'
    value: Function
  }
  [[OuterEnv]]: null
}

// Outer Function Execution Context
{
  // Environment Record
  {
    identifier: 'outerVariable'
    value: 'This is an outer variable'
  }
  [[OuterEnv]]: Global Execution Context
}
```

> `Var` variables are created when their containing `Environment Record` is instantiated and are initialized to undefined when created.

During the **Creation Phase** of the `Execution Context` variables are assigned the `undefined` value. The process of assigning the `undefined` to a variable during the **Creation Phase** is often referred to as **"hoisting"** or **declaration hoisting**. It is worth mentioning that the terms **"hoisting"** or **declaration hoisting** are not included in the standard. However, it is a convention used by many developers to explain the availability of variables "before" they were declared.  

```
console.log(globalVariable) // undefined

var globalVariable = 'This is a global variable'

// Global Execution Context Creation Phase
{
  // Environment Record
  {
    identifier: 'globalVariable'
    value: undefined
  }
  [[OuterEnv]]: null
}
```

Sometimes, it is explained that the code example above is possible because variables declared with the `var` keyword are "moved" to the top of the scope. However, nothing is moved anywhere; it is only possible by assigning the `undefined` value to the variable during the **Creation Phase** of `Execution Context`.

> Within the scope of any `VariableEnvironment` a common `BindingIdentifier` may appear in more than one `VariableDeclaration` but those declarations collectively define only one variable.

`BindingIdentifier` is a more specific type of the `Identifier`. We used the `Identifier` term before to explain the name of a variable. While `Identifier` also refers to the variable's name, `BindingIdentifier` is only used in the context of the declaration of variables (function or other data structure).  

```
let variable = 42 // BindingIdentifier
console.log(variable )  // Identifier
```

Now, let's go back to explaining the sentence's meaning.

> `BindingIdentifier` may appear in more than one `VariableDeclaration`

In the same scope, we can create multiple variables with the same name using the `var` keyword, whilst all these "variables" reference only one variable.  

```
var variable = 42
var variable = 66
var variable = 2015

// Execution context
{
    // Environment Record
    {
        identifier: 'variable '
        value: 2015
    }
    [[OuterEnv]]: null
}
```

It may appear we declared three variables with the `BindingIdentifier` `variable`, but we just reassigned the original variable `variable` twice. First, we reassigned it from `42` to `66`, then from `66` to `2015`

> A variable defined by a `VariableDeclaration` with an `Initializer` is assigned the value of its `Initializer` 's `AssignmentExpression` when the `VariableDeclaration` is executed, not when the variable is created.

The variable's value (`Initializer`) is assigned to it during the **Execution Phase**, not the `Creation Phase` of the `Execution Context`. Variables declared with the `let` and `const` keywords behave identically.  

```
var variable = 42

// Global Execution Context Creation Phase
{
    // Environment Record
    {
        identifier: variable
        value: undefined
    }
    [[OuterEnv]]: null
}

// Global Execution Context Execution Phase
{
    // Environment Record
    {
        identifier: variable
        value: 42
    }
    [[OuterEnv]]: null
}
```

## Diffrences

To sum up the article, I would like to highlight the following differences:

### Scope

The first difference between variables created with `var`, `let`, and `const` keywords is how they are scoped. Variables created with `let` and `const` are scoped to the `LexicalEnvironment`, meaning they are available in the `Environment Record` of a block, function, or the `Global Execution Context`. In contrast, variables created with `var` are scoped to the `VariableEnvironment`, meaning they are only available in the `Environment Record` of a function or the `Global Execution Context`.

### Creation Phase of the Execution Context

During the `Execution Context` 's **Creation Phase**, variables created with `let` and `const` are `uninitialised`, whilst `var` variables are assigned the `undefined` value. The state of `let` and `const` being `uninitialised` is sometimes referenced as a **Temporal Dead Zone or TDZ**. Also, the behaviour of `var` being assigned the `undefined` value is usually known as **“hoisting”**.

### Default Initializer value

Variables created with `let` and `var` keywords are assigned the `undefined` value if `Initializer` is not provided. Meanwhile, `const` variables must always have `Initializer`.

### Variables naming

Variables created with the `var` keyword can have duplicate names since they all reference the same variable. However, `let` and `const` variables can't have duplicate names — doing so results in a `Syntax Error`.

### Variables Initializer reassignment

Variables created with `let` and `var` keywords can reassign their initial `Initializer` (value) to a different one. But, `const` variables can't have their `Initializer` reassigned.
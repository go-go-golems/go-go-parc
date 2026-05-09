| ► |  | [The Racket Guide](https://docs.racket-lang.org/guide/index.html) |
| --- | --- | --- |

| ► | 17 | [Creating Languages](https://docs.racket-lang.org/guide/languages.html) |
| --- | --- | --- |

| ▼ | 17.3 | Defining new #lang Languages |
| --- | --- | --- |

| 17.3.1 | [Designating a #lang Language](https://docs.racket-lang.org/guide/hash-lang_syntax.html) |
| --- | --- |
| 17.3.2 | [Using #lang reader](https://docs.racket-lang.org/guide/hash-lang_reader.html) |
| 17.3.3 | [Using #lang s-  exp syntax/ module-  reader](https://docs.racket-lang.org/guide/syntax_module-reader.html) |
| 17.3.4 | [Installing a Language](https://docs.racket-lang.org/guide/language-collection.html) |
| 17.3.5 | [Source-  Handling Configuration](https://docs.racket-lang.org/guide/language-get-info.html) |
| 17.3.6 | [Module-  Handling Configuration](https://docs.racket-lang.org/guide/module-runtime-config.html) |

Racket

### 17.3 Defining new Languages

When loading a module as a source program that starts

> [#lang](https://docs.racket-lang.org/guide/Module_Syntax.html#%28part._hash-lang%29) language

the language determines the way that the rest of the module is parsed at the [reader](https://docs.racket-lang.org/guide/Pairs__Lists__and_Racket_Syntax.html#%28tech._reader%29) level. The [reader](https://docs.racket-lang.org/guide/Pairs__Lists__and_Racket_Syntax.html#%28tech._reader%29) -level parse must produce a [module](https://download.racket-lang.org/releases/9.1/doc/local-redirect/index.html?doc=reference&rel=module.html%23%2528form._%2528%2528quote._%7E23%7E25kernel%2529._module%2529%2529&version=9.1) form as a [syntax object](https://docs.racket-lang.org/guide/stx-obj.html#%28tech._syntax._object%29). As always, the second sub-form after [module](https://download.racket-lang.org/releases/9.1/doc/local-redirect/index.html?doc=reference&rel=module.html%23%2528form._%2528%2528quote._%7E23%7E25kernel%2529._module%2529%2529&version=9.1) specifies the [module language](https://docs.racket-lang.org/guide/module-languages.html#%28tech._module._language%29) that controls the meaning of the module’s body forms. Thus, a language specified after [#lang](https://docs.racket-lang.org/guide/Module_Syntax.html#%28part._hash-lang%29) controls both the [reader](https://docs.racket-lang.org/guide/Pairs__Lists__and_Racket_Syntax.html#%28tech._reader%29) -level and [expander](https://docs.racket-lang.org/guide/Pairs__Lists__and_Racket_Syntax.html#%28tech._expander%29) -level parsing of a module.

[17.3.1 Designating a #lang Language](https://docs.racket-lang.org/guide/hash-lang_syntax.html)

[17.3.2 Using #lang reader](https://docs.racket-lang.org/guide/hash-lang_reader.html)

[17.3.3 Using #lang s-exp syntax/module-reader](https://docs.racket-lang.org/guide/syntax_module-reader.html)

[17.3.4 Installing a Language](https://docs.racket-lang.org/guide/language-collection.html)

[17.3.5 Source-Handling Configuration](https://docs.racket-lang.org/guide/language-get-info.html)

[17.3.6 Module-Handling Configuration](https://docs.racket-lang.org/guide/module-runtime-config.html)
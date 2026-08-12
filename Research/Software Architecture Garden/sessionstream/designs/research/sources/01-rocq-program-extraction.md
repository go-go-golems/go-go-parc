$$
\begin{split}\newcommand{\as}{\kw{as}}
\newcommand{\case}{\kw{case}}
\newcommand{\cons}{\textsf{cons}}
\newcommand{\consf}{\textsf{consf}}
\newcommand{\emptyf}{\textsf{emptyf}}
\newcommand{\End}{\kw{End}}
\newcommand{\kwend}{\kw{end}}
\newcommand{\even}{\textsf{even}}
\newcommand{\evenO}{\textsf{even}_\textsf{O}}
\newcommand{\evenS}{\textsf{even}_\textsf{S}}
\newcommand{\Fix}{\kw{Fix}}
\newcommand{\fix}{\kw{fix}}
\newcommand{\for}{\textsf{for}}
\newcommand{\forest}{\textsf{forest}}
\newcommand{\Functor}{\kw{Functor}}
\newcommand{\In}{\kw{in}}
\newcommand{\ind}[3]{\kw{Ind}~[#1]\left(#2\mathrm{~:=~}#3\right)}
\newcommand{\Indp}[4]{\kw{Ind}_{#4}[#1](#2:=#3)}
\newcommand{\Indpstr}[5]{\kw{Ind}_{#4}[#1](#2:=#3)/{#5}}
\newcommand{\injective}{\kw{injective}}
\newcommand{\kw}[1]{\textsf{#1}}
\newcommand{\length}{\textsf{length}}
\newcommand{\letin}[3]{\kw{let}~#1:=#2~\kw{in}~#3}
\newcommand{\List}{\textsf{list}}
\newcommand{\lra}{\longrightarrow}
\newcommand{\Match}{\kw{match}}
\newcommand{\Mod}[3]{{\kw{Mod}}({#1}:{#2}\,\zeroone{:={#3}})}
\newcommand{\ModImp}[3]{{\kw{Mod}}({#1}:{#2}:={#3})}
\newcommand{\ModA}[2]{{\kw{ModA}}({#1}=={#2})}
\newcommand{\ModS}[2]{{\kw{Mod}}({#1}:{#2})}
\newcommand{\ModType}[2]{{\kw{ModType}}({#1}:={#2})}
\newcommand{\mto}{.\;}
\newcommand{\nat}{\textsf{nat}}
\newcommand{\Nil}{\textsf{nil}}
\newcommand{\nilhl}{\textsf{nil\_hl}}
\newcommand{\nO}{\textsf{O}}
\newcommand{\node}{\textsf{node}}
\newcommand{\nS}{\textsf{S}}
\newcommand{\odd}{\textsf{odd}}
\newcommand{\oddS}{\textsf{odd}_\textsf{S}}
\newcommand{\ovl}[1]{\overline{#1}}
\newcommand{\Pair}{\textsf{pair}}
\newcommand{\plus}{\mathsf{plus}}
\newcommand{\SProp}{\textsf{SProp}}
\newcommand{\Prop}{\textsf{Prop}}
\newcommand{\return}{\kw{return}}
\newcommand{\Set}{\textsf{Set}}
\newcommand{\Sort}{\mathcal{S}}
\newcommand{\Str}{\textsf{Stream}}
\newcommand{\Struct}{\kw{Struct}}
\newcommand{\subst}[3]{#1\{#2/#3\}}
\newcommand{\tl}{\textsf{tl}}
\newcommand{\tree}{\textsf{tree}}
\newcommand{\trii}{\triangleright_\iota}
\newcommand{\Type}{\textsf{Type}}
\newcommand{\WEV}[3]{\mbox{$#1[] \vdash #2 \lra  #3$}}
\newcommand{\WEVT}[3]{\mbox{$#1[] \vdash #2 \lra$}\\ \mbox{$ #3$}}
\newcommand{\WF}[2]{{\mathcal{W\!F}}(#1)[#2]}
\newcommand{\WFE}[1]{\WF{E}{#1}}
\newcommand{\WFT}[2]{#1[] \vdash {\mathcal{W\!F}}(#2)}
\newcommand{\WFTWOLINES}[2]{{\mathcal{W\!F}}\begin{array}{l}(#1)\\\mbox{}[{#2}]\end{array}}
\newcommand{\with}{\kw{with}}
\newcommand{\WS}[3]{#1[] \vdash #2 <: #3}
\newcommand{\WSE}[2]{\WS{E}{#1}{#2}}
\newcommand{\WT}[4]{#1[#2] \vdash #3 : #4}
\newcommand{\WTE}[3]{\WT{E}{#1}{#2}{#3}}
\newcommand{\WTEG}[2]{\WTE{\Gamma}{#1}{#2}}
\newcommand{\WTM}[3]{\WT{#1}{}{#2}{#3}}
\newcommand{\zeroone}[1]{[{#1}]}
\end{split}
$$

## Program extraction

Authors

Jean-Christophe Filliâtre and Pierre Letouzey

We present here the Coq extraction commands, used to build certified and relatively efficient functional programs, extracting them from either Coq functions or Coq proofs of specifications. The functional languages available as output are currently OCaml, Haskell and Scheme. In the following, "ML" will be used (abusively) to refer to any of the three.

Changed in version 8.11: Before using any of the commands or options described in this chapter, the extraction framework should first be loaded explicitly via `Require Extraction`, or via the more robust `From Coq Require Extraction`.

Require Extraction.

\[Loading ML file extraction\_plugin.cmxs (using legacy method)... done\]

## Generating ML Code

> [!note] Note
> In the following, a qualified identifier [`qualid`](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) can be used to refer to any kind of Coq global "object": [constant](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-constant), inductive type, inductive constructor or module name.

*Command* Extraction [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) [¶](#coq:cmd.Extraction "Permalink to this definition")

*Command* Recursive Extraction [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) + [¶](#coq:cmd.Recursive-Extraction "Permalink to this definition")

*Command* Extraction [string](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-string) [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) +

The first two forms display the extracted term(s) in Coq as a convenient preview of the extracted term(s):

- the first form extracts `qualid` and displays the resulting term;
- the second form extracts the listed `qualid` s and all their dependencies, and displays the resulting terms.

The third form produces a single extraction file named `string` for all the specified objects and all of their dependencies.

Global and local identifiers are renamed as needed to fulfill the syntactic requirements of the target language, keeping original names as much as possible.

The following commands also generate file(s). The generated file(s) are produced in the current working directory. It is possible to inspect what is the current directory with the command and to change it with the command.

*Command* Extraction Library [ident](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-ident) [¶](#coq:cmd.Extraction-Library "Permalink to this definition")

Extraction of the whole Coq library `ident.v` to an ML module `ident.ml`. In case of name clash, identifiers are here renamed using prefixes `coq_` or `Coq_` to ensure a session-independent renaming.

*Command* Recursive Extraction Library [ident](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-ident) [¶](#coq:cmd.Recursive-Extraction-Library "Permalink to this definition")

Extraction of the Coq library `ident.v` and all other modules `ident.v` depends on.

*Command* Separate Extraction [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) + [¶](#coq:cmd.Separate-Extraction "Permalink to this definition")

Recursive extraction of all the mentioned objects and all their dependencies, just as `Extraction string qualid+`, but instead of producing one monolithic file, this command splits the produced code in separate ML files, one per corresponding Coq `.v` file. This command is hence quite similar to, except that only the needed parts of Coq libraries are extracted instead of the whole. The naming convention in case of name clash is the same one as: identifiers are here renamed using prefixes `coq_` or `Coq_`.

The following command is meant to help automatic testing of the extraction, see for instance the `test-suite` directory in the Coq sources.

*Command* Extraction TestCompile [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) + [¶](#coq:cmd.Extraction-TestCompile "Permalink to this definition")

All the mentioned objects and all their dependencies are extracted to a temporary OCaml file, just as in `Extraction "file"`. Then this temporary file and its signature are compiled with the same OCaml compiler used to built Coq. This command succeeds only if the extraction and the OCaml compilation succeed. It fails if the current target language of the extraction is not OCaml.

*Command* Show Extraction [¶](#coq:cmd.Show-Extraction "Permalink to this definition")

*Command* Pwd [¶](#coq:cmd.Pwd "Permalink to this definition")

This command displays the current working directory (where the extracted files are produced).

*Command* Cd [string](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-string)?[¶](#coq:cmd.Cd "Permalink to this definition")

Deprecated since version 8.20: Use the command line option `-output-directory` instead (see [Command line options](https://rocq-prover.org/doc/v8.20/refman/practical-tools/coq-commands.html#command-line-options)), or the option.

If `string` is specified, changes the current directory according to [`string`](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-string) which can be any valid path. Otherwise, it displays the current directory as does.

## Extraction Options

### Setting the target language

*Command* Extraction Language [¶](#coq:cmd.Extraction-Language "Permalink to this definition")

`::=` OCaml `|` Haskell `|` Scheme `|` JSON

The ability to fix target language is the first and most important of the extraction options. Default is `OCaml`.

The JSON output is mostly for development or debugging: it contains the raw ML term produced as an intermediary target.

### Inlining and optimizations

Since OCaml is a strict language, the extracted code has to be optimized in order to be efficient (for instance, when using induction principles we do not want to compute all the recursive calls but only the needed ones). So the extraction mechanism provides an automatic optimization routine that will be called each time the user wants to generate an OCaml program. The optimizations can be split in two groups: the type-preserving ones (essentially constant inlining and reductions) and the non-type-preserving ones (some function abstractions of dummy types are removed when it is deemed safe in order to have more elegant types). Therefore some [constants](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-constant) may not appear in the resulting monolithic OCaml program. In the case of modular extraction, even if some inlining is done, the inlined constants are nevertheless printed, to ensure session-independent programs.

Concerning Haskell, type-preserving optimizations are less useful because of laziness. We still make some optimizations, for example in order to produce more readable code.

The type-preserving optimizations are controlled by the following Coq flags and commands:

*Flag* Extraction Optimize [¶](#coq:flag.Extraction-Optimize "Permalink to this definition")

Default is on. This [flag](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#term-flag) controls all type-preserving optimizations made on the ML terms (mostly reduction of dummy beta/iota redexes, but also simplifications on Cases, etc). Turn this flag off if you want a ML term as close as possible to the Coq term.

*Flag* Extraction Conservative Types [¶](#coq:flag.Extraction-Conservative-Types "Permalink to this definition")

Default is off. This [flag](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#term-flag) controls the non-type-preserving optimizations made on ML terms (which try to avoid function abstraction of dummy types). Turn this flag on to make sure that `e:t` implies that `e':t'` where `e'` and `t'` are the extracted code of `e` and `t` respectively.

*Flag* Extraction KeepSingleton [¶](#coq:flag.Extraction-KeepSingleton "Permalink to this definition")

Default is off. Normally, when the extraction of an inductive type produces a singleton type (i.e. a type with only one constructor, and only one argument to this constructor), the inductive structure is removed and this type is seen as an alias to the inner type. The typical example is `sig`. This [flag](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#term-flag) allows disabling this optimization when one wishes to preserve the inductive structure of types.

*Flag* Extraction AutoInline [¶](#coq:flag.Extraction-AutoInline "Permalink to this definition")

Default is off. When enabled, the extraction mechanism inlines the [bodies](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-body) of some defined [constants](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-constant), according to some heuristics like size of bodies, uselessness of some arguments, etc.

Even when this flag is off, recursors (`_rect` and `_rec` schemes, such as `nat_rect`), projections, and a few specific constants such as `andb` and `orb` (for the lazy behaviour) and well founded recursion combinators are still automatically inlined.

*Command* Extraction Inline [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) + [¶](#coq:cmd.Extraction-Inline "Permalink to this definition")

In addition to the automatic inline feature, the [constants](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-constant) mentioned by this command will always be inlined during extraction.

*Command* Extraction NoInline [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) + [¶](#coq:cmd.Extraction-NoInline "Permalink to this definition")

Conversely, the constants mentioned by this command will never be inlined during extraction.

*Command* Print Extraction Inline [¶](#coq:cmd.Print-Extraction-Inline "Permalink to this definition")

Prints the current state of the table recording the custom inlinings declared by the two previous commands.

*Command* Reset Extraction Inline [¶](#coq:cmd.Reset-Extraction-Inline "Permalink to this definition")

Empties the table recording the custom inlinings (see the previous commands).

**Inlining and printing of a constant declaration:**

The user can explicitly ask for a [constant](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-constant) to be extracted by two means:

> - by mentioning it on the extraction command line
> - by extracting the whole Coq module of this [constant](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-constant).

In both cases, the declaration of this [constant](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-constant) will be present in the produced file. But this same [constant](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-constant) may or may not be inlined in the following terms, depending on the automatic/custom inlining mechanism.

For the [constants](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-constant) non-explicitly required but needed for dependency reasons, there are two cases:

> - If an inlining decision is taken, whether automatically or not, all occurrences of this [constant](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-constant) are replaced by its extracted [body](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-body), and this [constant](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-constant) is not declared in the generated file.
> - If no inlining decision is taken, the [constant](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-constant) is normally declared in the produced file.

### Extra elimination of useless arguments

The following command provides some extra manual control on the code elimination performed during extraction, in a way which is independent but complementary to the main elimination principles of extraction (logical parts and types).

*Command* Extraction Implicit [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) \[ [ident](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-ident) [integer](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-integer) \* \] [¶](#coq:cmd.Extraction-Implicit "Permalink to this definition")

Declares some arguments of [`qualid`](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) as implicit, meaning that they are useless in extracted code. The extracted code will omit these arguments. Here [`qualid`](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) can be any function or inductive constructor, and the [`ident`](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-ident) s are the names of the useless arguments. Arguments can can also be identified positionally by [`integer`](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-integer) s starting from 1.

When an actual extraction takes place, an error is normally raised if the declarations cannot be honored, that is if any of the implicit arguments still occurs in the final code. This behavior can be relaxed via the following flag:

*Flag* Extraction SafeImplicits [¶](#coq:flag.Extraction-SafeImplicits "Permalink to this definition")

Default is on. When this [flag](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#term-flag) is off, a warning is emitted instead of an error if some implicit arguments still occur in the final code of an extraction. This way, the extracted code may be obtained nonetheless and reviewed manually to locate the source of the issue (in the code, some comments mark the location of these remaining implicit arguments). Note that this extracted code might not compile or run properly, depending of the use of these remaining implicit arguments.

### Realizing axioms

Extraction will fail if it encounters an informative axiom not realized. A warning will be issued if it encounters a logical axiom, to remind the user that inconsistent logical axioms may lead to incorrect or non-terminating extracted terms.

It is possible to assume some axioms while developing a proof. Since these axioms can be any kind of proposition or object or type, they may perfectly well have some computational content. But a program must be a closed term, and of course the system cannot guess the program which realizes an axiom. Therefore, it is possible to tell the system what ML term corresponds to a given axiom.

*Command* Extract Constant [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) [string <sub>tv</sub>](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-string) \* => [ident](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-ident) [string](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-string) [¶](#coq:cmd.Extract-Constant "Permalink to this definition")

Give an ML extraction for the given [constant](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-constant).

`string<sub>tv</sub>`

If the type scheme axiom is an arity (a sequence of products followed by a sort), then some type variables have to be given (as quoted strings).

The number of type variables is checked by the system. For example:

Axiom Y: Set -> Set -> Set.

Y is declared

Extract Constant Y "'a" "'b" => " 'a \* 'b ".

> [!note] Note
> The extraction recognizes whether the realized axiom should become a ML type constant or a ML object declaration. For example:
>
> Axiom X:Set.
>
> X is declared
>
> Axiom x:X.
>
> x is declared
>
> Extract Constant X => "int".
>
> Extract Constant x => "0".

> [!caution] Caution
> It is the responsibility of the user to ensure that the ML terms given to realize the axioms do have the expected types. In fact, the strings containing realizing code are just copied to the extracted files.

*Command* Extract Inlined Constant [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) => [ident](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-ident) [string](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-string) [¶](#coq:cmd.Extract-Inlined-Constant "Permalink to this definition")

Same as the previous one, except that the given ML terms will be inlined everywhere instead of being declared via a `let`.

> [!note] Note
> This command is sugar for an followed by a. Hence a will have an effect on the realized and inlined axiom.

*Error* The term [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) is already defined as foreign custom constant.[¶](#coq:exn.The-term-‘qualid’-is-already-defined-as-foreign-custom-constant "Permalink to this definition")

The `qualid` was previously used in a command. Using for `qualid` would override this command.

Realizing an axiom via is only useful in the case of an informative axiom (of sort `Type` or `Set`). A logical axiom has no computational content and hence will not appear in extracted terms. But a warning is nonetheless issued if extraction encounters a logical axiom. This warning reminds user that inconsistent logical axioms may lead to incorrect or non-terminating extracted terms.

If an informative axiom has not been realized before an extraction, a warning is also issued and the definition of the axiom is filled with an exception labeled `AXIOM TO BE REALIZED`. The user must then search these exceptions inside the extracted file and replace them by real code.

### Realizing inductive types

The system also provides a mechanism to specify ML terms for inductive types and constructors. For instance, the user may want to use the ML native boolean type instead of the Coq one. The syntax is the following:

*Command* Extract Inductive [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) => [ident](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-ident) [string](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-string) \[ [ident](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-ident) [string](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-string) \* \] [string <sub>match</sub>](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-string)?[¶](#coq:cmd.Extract-Inductive "Permalink to this definition")

Give an ML extraction for the given inductive type. You must specify extractions for the type itself (the initial `ident​string`) and all its constructors (the `[ ident​string* ]`). In this form, the ML extraction must be an ML inductive datatype, and the native pattern matching of the language will be used.

When the initial `ident​string` matches the name of the type of characters or strings (`char` and `string` for OCaml, `Prelude.Char` and `Prelude.String` for Haskell), extraction of literals is handled in a specialized way, so as to generate literals in the target language. This feature requires the type designated by `qualid` to be registered as the standard char or string type, using the [`Register`](https://rocq-prover.org/doc/v8.20/refman/proof-engine/vernacular-commands.html#coq:cmd.Register "Register") command.

`string<sub>match</sub>`

Indicates how to perform pattern matching over this inductive type. In this form, the ML extraction could be an arbitrary type. For an inductive type with $k$ constructors, the function used to emulate the pattern matching should expect $k+1$ arguments, first the $k$ branches in functional form, and then the inductive element to destruct. For instance, the match branch `| S n => foo` gives the functional form `(fun n -> foo)`. Note that a constructor with no arguments is considered to have one unit argument, in order to block early evaluation of the branch: `| O => bar` leads to the functional form `(fun () -> bar)`. For instance, when extracting `nat` into OCaml `int`, the code to be provided has type: `(unit->'a)->(int->'a)->int->'a`.

> [!caution] Caution
> As for, this command should be used with care:
>
> - The ML code provided by the user is currently **not** checked at all by extraction, even for syntax errors.
> - Extracting an inductive type to a pre-existing ML inductive type is quite sound. But extracting to a general type (by providing an ad-hoc pattern matching) will often **not** be fully rigorously correct. For instance, when extracting `nat` to OCaml `int`, it is theoretically possible to build `nat` values that are larger than OCaml `max_int`. It is the user's responsibility to be sure that no overflow or other bad events occur in practice.
> - Translating an inductive type to an arbitrary ML type does **not** magically improve the asymptotic complexity of functions, even if the ML type is an efficient representation. For instance, when extracting `nat` to OCaml `int`, the function `Nat.mul` stays quadratic. It might be interesting to associate this translation with some specific when primitive counterparts exist.

Typical examples are the following:

Extract Inductive unit => "unit" \[ "()" \].

Extract Inductive bool => "bool" \[ "true" "false" \].

Extract Inductive sumbool => "bool" \[ "true" "false" \].

> [!note] Note
> When extracting to OCaml, if an inductive constructor or type has arity 2 and the corresponding string is enclosed by parentheses, and the string meets OCaml's lexical criteria for an infix symbol, then the rest of the string is used as an infix constructor or type.

Extract Inductive list => "list" \[ "\[\]" "(::)" \].

Extract Inductive prod => "(\*)" \[ "(,)" \].

As an example of translation to a non-inductive datatype, let's turn `nat` into OCaml `int` (see caveat above):

Extract Inductive nat => int \[ "0" "succ" \] "(fun fO fS n -> if n=0 then fO () else fS (n-1))".

### Generating FFI Code

The plugin provides mechanisms to generate only OCaml code to interface the generated OCaml code with C programs. In order to link compiled OCaml code with C code, the linker needs to know

> - which C functions will be called by the ML code (external)
> - which ML functions shall be accessible by the C code (callbacks)

*Command* Extract Foreign Constant [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) => [string](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-string) [¶](#coq:cmd.Extract-Foreign-Constant "Permalink to this definition")

Like, except that the referenced ML terms will be declared in the form

`external` `qualid` `: ML type =` " `string` ".

For example:

Require Extraction.

Require Coq.extraction.ExtrOcamlNatInt.

\[Loading ML file ring\_plugin.cmxs (using legacy method)... done\]

Axiom f: nat -> nat -> nat.

f is declared

Extract Foreign Constant f => "f\_impl".

Here, the extracted external definition will be:

`external f : int -> int -> int = "f_impl"`

> [!caution] Caution
> - The external function name `string` is not checked in any way.
> - The user must ensure that the C functions given to realize the axioms have the expected or compatible types. In fact, the strings containing realizing code are just copied to the extracted files.

*Error* Extract Foreign Constant is supported only for OCaml extraction.[¶](#coq:exn.Extract-Foreign-Constant-is-supported-only-for-OCaml-extraction "Permalink to this definition")

Foreign function calls are only supported for OCaml.

*Error* Extract Foreign Constant is supported only for functions.[¶](#coq:exn.Extract-Foreign-Constant-is-supported-only-for-functions "Permalink to this definition")

This error is thrown if `qualid` is of sort `Type` as external functions only work for functions.

*Error* The term [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) is already defined as inline custom constant.[¶](#coq:exn.The-term-‘qualid’-is-already-defined-as-inline-custom-constant "Permalink to this definition")

The `qualid` was previously used in a command. Using for `qualid` would override this command.

*Command* Extract Callback [string](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-string)? [qualid](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) [¶](#coq:cmd.Extract-Callback "Permalink to this definition")

This command makes sure that after extracting the [constants](https://rocq-prover.org/doc/v8.20/refman/language/core/definitions.html#term-constant) specified by `qualid`, a constant ML function will be generated that registers `qualid` as callback, callable by `string`. This is done by declaring a function `let _ = Callback.register` " `string` " `qualid`.

This expression signals OCaml that the given ML function `qualid` shall be accessible via the alias `string`, when calling from C/C++. If no alias is specified, it is set to the string representation of `qualid`.

> [!caution] Caution
> - The optional alias `string` is currently **not** checked in any way.
> - The user must ensure that the callback aliases are unique, i.e. when multiple modules expose a callback, the user should make sure that no two `qualid` share the same alias.

> [!note] Note
> Using Extract Callback has no impact on the rest of the synthesised code since it is an additional declaration. Thus, there is no impact on the correctness and type safety of the generated code.

*Error* Extract Callback is supported only for OCaml extraction.[¶](#coq:exn.Extract-Callback-is-supported-only-for-OCaml-extraction "Permalink to this definition")

The callback registration mechanism `Callback.register` is specific to OCaml. Thus, the command is only usable when extracting OCaml code.

*Command* Print Extraction Foreign [¶](#coq:cmd.Print-Extraction-Foreign "Permalink to this definition")

Prints the current set of custom foreign functions declared by the command together with its associated foreign ML function name.

*Command* Print Extraction Callback [¶](#coq:cmd.Print-Extraction-Callback "Permalink to this definition")

Prints the map of callbacks declared by the command, showing the [`qualid`](https://rocq-prover.org/doc/v8.20/refman/language/core/modules.html#grammar-token-qualid) and callback alias [`string`](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-string) (if specified) for each callback.

*Command* Reset Extraction Callback [¶](#coq:cmd.Reset-Extraction-Callback "Permalink to this definition")

Resets the the map recording the callbacks declared by the command.

### Avoiding conflicts with existing filenames

When using, the names of the extracted files directly depend on the names of the Coq files. It may happen that these filenames are in conflict with already existing files, either in the standard library of the target language or in other code that is meant to be linked with the extracted code. For instance the module `List` exists both in Coq and in OCaml. It is possible to instruct the extraction not to use particular filenames.

*Command* Extraction Blacklist [ident](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-ident) + [¶](#coq:cmd.Extraction-Blacklist "Permalink to this definition")

Instruct the extraction to avoid using these names as filenames for extracted code.

*Command* Print Extraction Blacklist [¶](#coq:cmd.Print-Extraction-Blacklist "Permalink to this definition")

Show the current list of filenames the extraction should avoid.

*Command* Reset Extraction Blacklist [¶](#coq:cmd.Reset-Extraction-Blacklist "Permalink to this definition")

Allow the extraction to use any filename.

For OCaml, a typical use of these commands is `Extraction Blacklist String List`.

### Additional settings

This [option](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#term-option) provides a comment that is included at the beginning of the output files.

*Option* Extraction Flag [natural](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-natural) [¶](#coq:opt.Extraction-Flag "Permalink to this definition")

This [option](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#term-option) controls which optimizations are used during extraction, providing a finer-grained control than. The bits of [`natural`](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-natural) are used as a bit mask. Keeping an option off keeps the extracted ML more similar to the Coq term. Values are:

| Bit | Value | Optimization (default is on unless noted otherwise) |
| --- | --- | --- |
| 0 | 1 | Remove local dummy variables |
| 1 | 2 | Use special treatment for fixpoints |
| 2 | 4 | Simplify case with iota-redux |
| 3 | 8 | Factor case branches as functions |
| 4 | 16 | (not available, default false) |
| 5 | 32 | Simplify case as function of one argument |
| 6 | 64 | Simplify case by swapping case and lambda |
| 7 | 128 | Some case optimization |
| 8 | 256 | Push arguments inside a letin |
| 9 | 512 | Use linear let reduction (default false) |
| 10 | 1024 | Use linear beta reduction (default false) |

*Flag* Extraction TypeExpand [¶](#coq:flag.Extraction-TypeExpand "Permalink to this definition")

If this [flag](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#term-flag) is set, fully expand Coq types in ML. See the Coq source code to learn more.

*Option* Extraction Output Directory [string](https://rocq-prover.org/doc/v8.20/refman/language/core/basic.html#grammar-token-string) [¶](#coq:opt.Extraction-Output-Directory "Permalink to this definition")

Sets the directory where extracted files will be written. If not set, files will be written to the directory specified by the command line option `-output-directory`, if set (see [Command line options](https://rocq-prover.org/doc/v8.20/refman/practical-tools/coq-commands.html#command-line-options)) and otherwise, the current directory. Use to display the current directory.

## Differences between Coq and ML type systems

Due to differences between Coq and ML type systems, some extracted programs are not directly typable in ML. We now solve this problem (at least in OCaml) by adding when needed some unsafe casting `Obj.magic`, which give a generic type `'a` to any term.

First, if some part of the program is *very* polymorphic, there may be no ML type for it. In that case the extraction to ML works alright but the generated code may be refused by the ML type checker. A very well known example is the `distr-pair` function:

Definition dp {A B:Type}(x:A)(y:B)(f:forall C:Type, C->C):= (f A x, f B y).

dp is defined

In OCaml, for instance, the direct extracted term would be:

```
let dp x y f = Pair((f () x),(f () y))
```

and would have type:

```
dp : 'a -> 'a -> (unit -> 'a -> 'b) -> ('b,'b) prod
```

which is not its original type, but a restriction.

We now produce the following correct version:

```
let dp x y f = Pair ((Obj.magic f () x), (Obj.magic f () y))
```

Secondly, some Coq definitions may have no counterpart in ML. This happens when there is a quantification over types inside the type of a constructor; for example:

Inductive anything: Type:= dummy: forall A:Set, A -> anything.

anything is defined anything\_rect is defined anything\_ind is defined anything\_rec is defined anything\_sind is defined

which corresponds to the definition of an ML dynamic type. In OCaml, we must cast any argument of the constructor dummy (no GADT are produced yet by the extraction).

Even with those unsafe castings, you should never get error like `segmentation fault`. In fact even if your program may seem ill-typed to the OCaml type checker, it can't go wrong: it comes from a Coq well-typed terms, so for example inductive types will always have the correct number of arguments, etc. Of course, when launching manually some extracted function, you should apply it to arguments of the right shape (from the Coq point-of-view).

More details about the correctness of the extracted programs can be found in [\[Let02\]](https://rocq-prover.org/doc/v8.20/refman/zebibliography.html#let02).

We have to say, though, that in most "realistic" programs, these problems do not occur. For example all the programs of Coq library are accepted by the OCaml type checker without any `Obj.magic` (see examples below).

## Some examples

We present here two examples of extraction, taken from the Coq Standard Library. We choose OCaml as the target language, but everything, with slight modifications, can also be done in the other languages supported by extraction. We then indicate where to find other examples and tests of extraction.

### A detailed example: Euclidean division

The file `Euclid` contains the proof of Euclidean division. The natural numbers used here are unary, represented by the type `nat`, which is defined by two constructors `O` and `S`. This module contains a theorem `eucl_dev`, whose type is:

```
forall b:nat, b > 0 -> forall a:nat, diveucl a b
```

where `diveucl` is a type for the pair of the quotient and the modulo, plus some logical assertions that disappear during extraction. We can now extract this program to OCaml:

Require Extraction.

Require Import Euclid Wf\_nat.

Extraction Inline gt\_wf\_rec lt\_wf\_rec induction\_ltof2.

Recursive Extraction eucl\_dev.

type nat = | O | S of nat type sumbool = | Left | Right (\*\* val sub: nat -> nat -> nat \*\*) let rec sub n m = match n with | O -> n | S k -> (match m with | O -> n | S l -> sub k l) (\*\* val le\_lt\_dec: nat -> nat -> sumbool \*\*) let rec le\_lt\_dec n m = match n with | O -> Left | S n0 -> (match m with | O -> Right | S n1 -> le\_lt\_dec n0 n1) (\*\* val le\_gt\_dec: nat -> nat -> sumbool \*\*) let le\_gt\_dec = le\_lt\_dec type diveucl = | Divex of nat \* nat (\*\* val eucl\_dev: nat -> nat -> diveucl \*\*) let rec eucl\_dev n m = let s = le\_gt\_dec n m in (match s with | Left -> let d = let y = sub m n in eucl\_dev n y in let Divex (q, r) = d in Divex ((S q), r) | Right -> Divex (O, m))

The inlining of `gt_wf_rec` and others is not mandatory. It only enhances readability of extracted code. You can then copy-paste the output to a file `euclid.ml` or let Coq do it for you with the following command:

```
Extraction "euclid" eucl_dev.
```

Let us play the resulting program (in an OCaml toplevel):

```
#use "euclid.ml";;
type nat = O | S of nat
type sumbool = Left | Right
val sub : nat -> nat -> nat = <fun>
val le_lt_dec : nat -> nat -> sumbool = <fun>
val le_gt_dec : nat -> nat -> sumbool = <fun>
type diveucl = Divex of nat * nat
val eucl_dev : nat -> nat -> diveucl = <fun>

# eucl_dev (S (S O)) (S (S (S (S (S O)))));;
- : diveucl = Divex (S (S O), S O)
```

It is easier to test on OCaml integers:

```
# let rec nat_of_int = function 0 -> O | n -> S (nat_of_int (n-1));;
val nat_of_int : int -> nat = <fun>

# let rec int_of_nat = function O -> 0 | S p -> 1+(int_of_nat p);;
val int_of_nat : nat -> int = <fun>

# let div a b =
  let Divex (q,r) = eucl_dev (nat_of_int b) (nat_of_int a)
  in (int_of_nat q, int_of_nat r);;
val div : int -> int -> int * int = <fun>

# div 173 15;;
- : int * int = (11, 8)
```

Note that these `nat_of_int` and `int_of_nat` are now available via a mere `Require Import ExtrOcamlIntConv` and then adding these functions to the list of functions to extract. This file `ExtrOcamlIntConv.v` and some others in `plugins/extraction/` are meant to help building concrete program via extraction.

### Extraction's horror museum

Some pathological examples of extraction are grouped in the file `test-suite/success/extraction.v` of the sources of Coq.

### Users' Contributions

Several of the Coq Users' Contributions use extraction to produce certified programs. In particular the following ones have an automatic extraction test:

> - `additions`: [https://github.com/coq-contribs/additions](https://github.com/coq-contribs/additions)
> - `bdds`: [https://github.com/coq-contribs/bdds](https://github.com/coq-contribs/bdds)
> - `canon-bdds`: [https://github.com/coq-contribs/canon-bdds](https://github.com/coq-contribs/canon-bdds)
> - `chinese`: [https://github.com/coq-contribs/chinese](https://github.com/coq-contribs/chinese)
> - `continuations`: [https://github.com/coq-contribs/continuations](https://github.com/coq-contribs/continuations)
> - `coq-in-coq`: [https://github.com/coq-contribs/coq-in-coq](https://github.com/coq-contribs/coq-in-coq)
> - `exceptions`: [https://github.com/coq-contribs/exceptions](https://github.com/coq-contribs/exceptions)
> - `firing-squad`: [https://github.com/coq-contribs/firing-squad](https://github.com/coq-contribs/firing-squad)
> - `founify`: [https://github.com/coq-contribs/founify](https://github.com/coq-contribs/founify)
> - `graphs`: [https://github.com/coq-contribs/graphs](https://github.com/coq-contribs/graphs)
> - `higman-cf`: [https://github.com/coq-contribs/higman-cf](https://github.com/coq-contribs/higman-cf)
> - `higman-nw`: [https://github.com/coq-contribs/higman-nw](https://github.com/coq-contribs/higman-nw)
> - `hardware`: [https://github.com/coq-contribs/hardware](https://github.com/coq-contribs/hardware)
> - `multiplier`: [https://github.com/coq-contribs/multiplier](https://github.com/coq-contribs/multiplier)
> - `search-trees`: [https://github.com/coq-contribs/search-trees](https://github.com/coq-contribs/search-trees)
> - `stalmarck`: [https://github.com/coq-contribs/stalmarck](https://github.com/coq-contribs/stalmarck)

Note that `continuations` and `multiplier` are a bit particular. They are examples of developments where `Obj.magic` is needed. This is probably due to a heavy use of impredicativity. After compilation, those two examples run nonetheless, thanks to the correction of the extraction [\[Let02\]](https://rocq-prover.org/doc/v8.20/refman/zebibliography.html#let02).

**OMeta** is a specialized [object-oriented](https://en.wikipedia.org/wiki/Object-oriented_programming "Object-oriented programming") [programming language](https://en.wikipedia.org/wiki/Programming_language "Programming language") for [pattern matching](https://en.wikipedia.org/wiki/Pattern_matching "Pattern matching"), developed by Alessandro Warth and Ian Piumarta in 2007 at the [Viewpoints Research Institute](https://en.wikipedia.org/wiki/Viewpoints_Research_Institute "Viewpoints Research Institute"). The language is based on [parsing expression grammars](https://en.wikipedia.org/wiki/Parsing_expression_grammar "Parsing expression grammar") (PEGs), rather than [context-free grammars](https://en.wikipedia.org/wiki/Context-free_grammar "Context-free grammar"), with the intent to provide "a natural and convenient way for programmers to implement [tokenizers](https://en.wikipedia.org/wiki/Tokenization_\(lexical_analysis\) "Tokenization (lexical analysis)"), [parsers](https://en.wikipedia.org/wiki/Parsing "Parsing"), [visitors](https://en.wikipedia.org/wiki/Visitor_pattern "Visitor pattern"), and tree-transformers".[^1]

OMeta's main goal is to allow a broader audience to use techniques generally available only to language programmers, such as parsing.[^1] It is also known for its use in quickly creating prototypes, though programs written in OMeta are noted to be generally less efficient than those written in vanilla (base language) implementations, such as [JavaScript](https://en.wikipedia.org/wiki/JavaScript "JavaScript").[^2] [^3]

OMeta is noted for its use in creating [domain-specific languages](https://en.wikipedia.org/wiki/Domain-specific_language "Domain-specific language"), and especially for the maintainability of its implementations (Newcome). OMeta, like other [metalanguages](https://en.wikipedia.org/wiki/Metalanguage "Metalanguage"), requires a host language; it was originally created as a COLA implementation.[^1]

## Description

OMeta is a metalanguage used to prototype and create [domain-specific languages](https://en.wikipedia.org/wiki/Domain-specific_language "Domain-specific language"). It was introduced as "an object-oriented language for pattern matching".[^1] It uses [parsing expression grammars](https://en.wikipedia.org/wiki/Parsing_expression_grammar "Parsing expression grammar") (descriptions of languages "based on recognizing strings instead of generating them" [^4]) designed "to handle arbitrary kinds of data", such as characters, numbers, strings, atoms, and lists. This increases its versatility, enabling it to work on both structured and [unstructured data](https://en.wikipedia.org/wiki/Unstructured_data "Unstructured data").[^1]

The language's main advantage over similar languages is its ability to use the same code for all steps of compiling, e.g., lexing and parsing. OMeta also supports the defining of production rules based on arguments; this can be used to add such rules to OMeta, and the host language that OMeta is running in. Also, these rules can use each other as arguments, creating "higher-order rules", and inheriting each other to gain production rules from existing code. OMeta is capable of using host-language booleans (True/False) while pattern matching; these are referred to as "semantic predicates". OMeta uses generalized pattern-matching to allow programmers to more easily implement and extend phases of compilation with a single tool.[^1]

OMeta uses grammars to determine the rules in which it operates. The grammars are able to hold an indefinite number of variables due to the use of an \_\_init\_\_ function called when a grammar is created. Grammars can inherit and call each other (using the "foreign production invocation mechanism", enabling grammars to "borrow" each other's input streams), much like classes in full programming languages.[^1] OMeta also prioritizes options within a given grammar to remove ambiguity, unlike most metalanguages. After pattern-matching an input to a given grammar, OMeta then assigns each component of the pattern to a variable, which it then feeds into the host language.[^5]

OMeta uses pattern matching to perform all of the steps of traditional compiling by itself. It first finds patterns in characters to create tokens, then it matches those tokens to its grammar to make syntax trees. Typecheckers then match patterns on the syntax trees to make annotated trees, and visitors do the same to produce other trees. A code generator then pattern-matches the trees to produce the code.[^3] In OMeta, it is easy to "traverse through the parse tree since such functionality is natively supported".[^3]

The metalanguage is noted for its usability in most programming languages, though it is most commonly used in its language of implementation—OMeta/JS, for example, is used in JavaScript.[^5] Because it requires a host language, the creators of OMeta refer to it as a "parasitic language".[^6]

### Development

Alessandro Warth and Ian Piumarta developed OMeta at the Viewpoints Research Institute, an organization intended to improve research systems and personal computing, in 2007. They first used a Combined Object Lambda Architecture (COLA), a self-describing language investigated at Viewpoints Research Institute, as OMeta's host language, and later, assisted by Yoshiki Ohshima, ported it to [Squeak](https://en.wikipedia.org/wiki/Squeak "Squeak") [Smalltalk](https://en.wikipedia.org/wiki/Smalltalk "Smalltalk") to verify its usability with multiple host languages. OMeta was also used "to implement a nearly complete subset of…JavaScript" as a case study in its introductory paper.[^1]

### Use

OMeta, like other metalanguages, is used to mainly create [domain-specific languages](https://en.wikipedia.org/wiki/Domain-specific_language "Domain-specific language") (DSLs); specifically, it is used to quickly prototype DSLs — OMeta's slow running speed and unclear error reports remove much of its function as a full [programming language](https://en.wikipedia.org/wiki/Programming_language "Programming language") (Heirbaut 73–74). OMeta is useful thanks to its ability to use one syntax for every phase of compiling, allowing it to be used rather than several separate tools to create a compiler.[^5] Also, OMeta is valued both for the speed at which it can be used to create DSLs and the significantly lower amount of code it needs to perform such a task in contrast to vanilla implementations, with reports showing around 26% as many lines of functional code as vanilla.[^2]

### Examples

The following is an example of a basic calculator language in C# using OMeta:

```
ometa BasicCalc <: Parser
 {
  Digit  = super:d                    -> d.ToDigit(),
  Number = Number:n Digit:d           -> (n * 10 + d)
         | Digit,
  AddExpr = AddExpr:x ‘+’ MulExpr:y  -> (x + y)
          | AddExpr:x ‘-’ MulExpr:y  -> (x - y)
          | MulExpr,
  MulExpr = MulExpr:x ‘*’ primExpr:y -> (x * y)
          | MulExpr:x ‘/’ primExpr:y -> (x / y)
          | PrimExpr,
 PrimExpr = ‘(‘ Expr:x ‘)’        -> x
          | Number,
     Expr = AddExpr
 }
```

[^5]

It is also possible to create subclasses of languages you have written:

```
ometa ExponentCalc <: BasicCalc
 {
   MulExpr = MulExpr:x ‘^’ PrimExpr:e -> Math.pow(x,e)
           | super
 }
```

[^5]

Previously written languages can also be called rather than inherited:

```
ometa ScientificCalc <: Parser
 {
       MathFunc :n = Token(n) Spaces,
   AdvExp          = MathFunc(‘sqrt’) AdvExp:x -> Math.Sqrt(x)
                   | FacExp
   FacExp          = PrimExp:x ‘!’
                       ->  {
                                 var r = 1;
                                 for(; x > 1; x--)
                                 {
                                   r *= x;
                                 }
                                 return r;
                           }
                   | PrimExp
   PrimExp         = foreign(ExponentCalc.Expr):x -> x
   Expr     = AdvExp
 }
```

[^5]

## Versions

OMeta can theoretically be implemented into any host language, but it is used most often as OMeta/JS, a JavaScript implementation.[^5] Warth has stated that patterns in "OMeta/X---where X is some host language" are better left to be influenced by "X" than standardized within OMeta, due to the fact that different host languages recognize different types of objects.[^6]

### MetaCOLA

MetaCOLA was the first implementation of OMeta, used in the language's introductory paper. MetaCOLA implemented OMeta's first test codes, and was one of the three forms (the others being OMeta/Squeak and a nearly-finished OMeta/JS) of the language made prior to its release.[^1]

### OMeta/Squeak

OMeta/Squeak was a port of OMeta used during the initial demonstration of the system. OMeta/Squeak is used "to experiment with alternative syntaxes for the Squeak EToys system" OMeta/Squeak requires square brackets and "pointy brackets" (braces) in rule operations, unlike OMeta/JS, which requires only square brackets.[^6] OMeta/Squeak 2, however, features syntax more similar to that of OMeta/JS.[^7] Unlike the COLA implementation of OMeta, the Squeak version does not memorize intermediate results (store numbers already used in calculation).[^1]

### OMeta/JS

OMeta/JS is OMeta in the form of a JavaScript implementation. Language implementations using OMeta/JS are noted to be easier to use and more space-efficient than those written using only vanilla JavaScript, but the former have been shown to perform much more slowly. Because of this, OMeta/JS is seen as a highly useful tool for prototyping, but is not preferred for production language implementations.[^3]

#### Vs. JavaScript

The use of DSL development tools, such as OMeta, are considered much more maintainable than "vanilla implementations" (i. e. JavaScript) due to their low NCLOC (Non-Comment Lines of Code) count. This is due in part to the "semantic action code which creates the AST objects or performs limited string operations". OMeta's lack of "context-free syntax" allows it to be used in both parser and lexer creation at the cost of extra lines of code. Additional factors indicating OMeta's maintainability include a high maintainability index "while Halstead Effort indicate\[s\] that the vanilla parser requires three times more development effort compared to the OMeta parser". Like JavaScript, OMeta/JS supports "the complete syntax notation of Waebric".[^3]

One of the major advantages of OMeta responsible for the difference in NCLOC is OMeta's reuse of its "tree walking mechanism" by allowing the typechecker to inherit the mechanism from the parser, which causes the typechecker to adapt to changes in the OMeta parser, while JavaScript's tree walking mechanism contains more code and must be manually adapted to the changes in the parser. Another is the fact that OMeta's grammars have a "higher abstraction level...than the program code". It can also be considered "the result of the semantic action code which creates the AST objects or performs limited string operations", though the grammar's non-semantics create a need for relatively many lines of code per function because of explicit whitespace definition—a mechanism implemented to allow OMeta to act as a single tool for DSL creation.[^3]

In terms of performance, OMeta is found to run at slow speeds in comparison to vanilla implementations. The use of backtracking techniques by OMeta is a potential major cause for this (OMeta's parser "includes seven look-ahead operators...These operators are necessary to distinguish certain rules from each other and cannot be left out of the grammar"); however, it is more likely that this performance drop is due to OMeta's method of memoization:

> "The storage of intermediate parsing steps causes the size of the parsing table to be proportional with the number of terminals and non-terminals (operands) used in the grammar. Since the grammar of the OMeta parser contains 446 operands, it is believed that performance is affected negatively." [^3]

Where OMeta gains time on the vanilla implementation, however, is in lexing. JavaScript's vanilla lexer slows down significantly due to a method by which the implementation converts the entire program into a string through Java before the lexer starts. Despite this, the OMeta implementation runs significantly slower overall.[^3]

OMeta also falls behind in terms of error reporting. While vanilla implementations return the correct error message in about "92% of the test cases" in terms of error location, OMeta simply returns "Match failed!" to any given error. Finding the source through OMeta requires "manually...counting the newline characters in the semantic action code in order to output at least the line number at which parsing fails".[^3]

### OMeta#

OMeta# is a project by Jeff Moser meant to translate OMeta/JS into a C# function; as such, the design of OMeta# is based on Alessandro Warth's OMeta/JS design.. The goal of the project is to give users the ability to make working languages with high simplicity. Specifically, OMeta# is intended to work as a single tool for [.NET](https://en.wikipedia.org/wiki/.NET ".NET") language development, reduce the steep learning curve of language development, become a useful teaching resource, and be practical for use in real applications.[^5] OMeta# currently uses C# 3.0 as OMeta's host language rather than 4.0; because C# 3.0 is a static language rather than a dynamic one, recognition of the host language within OMeta# is "two to three times uglier and larger than it might have been" in a dynamically typed language.[^8]

OMeta# uses.NET classes, or Types, as grammars and methods for the grammars’ internal "rules". OMeta# uses braces ( { and } ) to recognize its host language in grammars. The language has a focus on strong, clean, static typing much like that of its host language, though this adds complexity to the creation of the language. New implementations in C# must also be compatible with the.NET metalanguage, making the creation even more complex. Also, to prevent users from accidentally misusing the metarules in OMeta#, Moser has opted to implement them as "an explicit interface exposed via a property (e.g. instead of "\_apply", I have "MetaRules.Apply")." Later parts of OMeta# are written in OMeta#, though the functions of the language remains fairly tied to C#.[^9] The OMeta# source code is posted on Codeplex, and is intended to remain as an open-source project. However, updates have been on indefinite hiatus since shortly after the project's beginnings, with recommits by the server on October 1, 2012.[^5]

### IronMeta

Gordon Tisher created [IronMeta](https://github.com/kulibali/ironmeta) for.NET in 2009, and while similar to OMeta#, it's a much more supported and robust implementation, distributed under BSD license on GitHub.

### Ohm

[Ohm](https://github.com/cdglabs/ohm) is a successor to Ometa that aims to improve on it by (amongst other things) separating the grammar from the semantic actions.[^10]

## See also

- [ANTLR](https://en.wikipedia.org/wiki/ANTLR "ANTLR") (ANother Tool for Language Recognition), a similar metalanguage
- [META II](https://en.wikipedia.org/wiki/META_II "META II") An early [compiler-compiler](https://en.wikipedia.org/wiki/Compiler-compiler "Compiler-compiler"), influential in OMeta's implementation

## References

## External links

- [OMeta/JS](https://github.com/alexwarth/ometa-js) on [GitHub](https://en.wikipedia.org/wiki/GitHub "GitHub"), for JavaScript

[^1]: Warth, Alessandro, and Ian Piumarta. " [OMeta: An Object-Oriented Language for Pattern Matching](http://tinlizzie.org/~awarth/papers/dls07.pdf)." ACM SIGPLAN 2007 Dynamic Languages Symposium (DLS '07). 03rd ed. Vol. TR-2007. Glendale, California: Viewpoints Research Institute, 2007. VPRI Technical Report. Web. 30 September 2013.

[^2]: Klint, Paul, Tijs Van Der Storm, and Jurgen Vinju. " [On the Impact of DSL Tools on the Maintainability of Language Implementations](http://homepages.cwi.nl/~paulk/publications/dsl-impl-metrics.pdf)." LDTA '10 Proceedings of the Tenth Workshop on Language Descriptions, Tools and Applications. New York, NY. N.p., 2010. Web. 30 September 2013.

[^3]: Heirbaut, Nickolas. "Two Implementation Techniques for Domain Specific Languages Compared: OMeta/JS vs. Javascript." Thesis. University of Amsterdam, 2009. Web. 30 September 2013.< [http://dare.uva.nl/document/153293](http://dare.uva.nl/document/153293) >.

[^4]: Mascarenhas, Fabio, Sergio Medeiros, and [Roberto Ierusalimschy](https://en.wikipedia.org/wiki/Roberto_Ierusalimschy "Roberto Ierusalimschy"). Parsing Expression Grammars for Structured Data. N.p.: n.p., n.d. Web.< [http://www.lbd.dcc.ufmg.br/colecoes/sblp/2011/003.pdf](http://www.lbd.dcc.ufmg.br/colecoes/sblp/2011/003.pdf) [Archived](https://web.archive.org/web/20131021055642/http://www.lbd.dcc.ufmg.br/colecoes/sblp/2011/003.pdf) 2013-10-21 at the [Wayback Machine](https://en.wikipedia.org/wiki/Wayback_Machine "Wayback Machine") >.

[^5]: Moser, Jeff. "Moserware.": [OMeta#: Who? What? When? Where? Why?](http://www.moserware.com/2008/06/ometa-who-what-when-where-why.html), Blogger, 24 June 2008. Web. 30 September 2013.

[^6]: Warth, Alessandro. "\[Ometa\] On OMeta's Syntax." \[Ometa\] On OMeta's Syntax. N.p., 4 July 2008. Web. 16 Oct. 2013.< [http://vpri.org/pipermail/ometa/2008-July/000051.html](http://vpri.org/pipermail/ometa/2008-July/000051.html) [Archived](https://web.archive.org/web/20081120195853/http://vpri.org/pipermail/ometa/2008-July/000051.html) 2008-11-20 at the [Wayback Machine](https://en.wikipedia.org/wiki/Wayback_Machine "Wayback Machine") >.

[^7]: Warth, Alessandro. "OMeta/Squeak 2." OMeta/Squeak 2. N.p., n.d. Web. 16 Oct. 2013.< [http://tinlizzie.org/ometa/ometa2.html](http://tinlizzie.org/ometa/ometa2.html) >.

[^8]: Moser, Jeff. "Moserware.": [Meta-FizzBuzz](http://www.moserware.com/2008/08/meta-fizzbuzz.html), Blogger, 25 August 2008. Web. 30 September 2013.

[^9]: Moser, Jeff. "Moserware.": Building an Object-Oriented Parasitic Metalanguage Blogger, 31 July 2008. Web. 30 September 2013.

[^10]: ["Ohm Philosophy"](https://github.com/cdglabs/ohm/blob/master/doc/philosophy.md). *[GitHub](https://en.wikipedia.org/wiki/GitHub "GitHub")*.
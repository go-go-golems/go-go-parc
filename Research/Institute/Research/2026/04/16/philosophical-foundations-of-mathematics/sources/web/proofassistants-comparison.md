$\\begingroup$

What is a good starting point to learn about proof assistants?

The answer will invariably depend on the area of interest: mathematics (and its areas, e.g. algebra,combinatorics, analysis, logic), CS - and overlapping with maths areas, etc.

Apart from this, practical issues:

- how is it is to pick as a language?
- how easy is it to install and connect with popular IDEs (such as Visual Studio Code)?
- availability of learning material
- availability of online forums willing to cater to beginners.

One hears about [Agda](https://github.com/agda/agda), [Coq](https://github.com/coq/coq), [Idris](https://github.com/idris-lang/Idris2), [Lean](https://leanprover-community.github.io/). However, it not clear, which one is the best pick for a first proof assistant. (One looking for the "Python of proof assistants".)

$\\endgroup$ 14 $\\begingroup$

## Lean

I am a professional mathematician with minimal experience in coding or computer science (and who has no idea what "leftpad" is;-) ), and I personally found it very hard to break into the proof assistant community; ultimately I succeeded by attempting to formalise in Lean the statements and the proofs of the undergraduate example sheets in the introduction to proof course which I was teaching in the mathematics department at Imperial College London, and asking on the [Lean chat](https://leanprover.zulipchat.com/) when I got stuck. I am eternally indebted to Mario Carneiro for all the time he spent patiently dealing with my questions at that early stage; without him, I am pretty sure that I would not be using proof assistants now, I would just have given up. My [header image on Twitter](https://twitter.com/XenaProject/header_photo) is a twisted and coloured-in version of part of the term created by my 100+ line tactic proof of the irrationality of $\\sqrt{3}$ which was on the second example sheet, written when I still had no idea what I was doing. I could write a far shorter proof now, although now I don't need to, because the result is easily deducible from irrationality results in our wonderful mathematics library [`mathlib`](https://github.com/leanprover-community/mathlib).

Since then, things have changed for mathematicians. Mohammed Pedramfar and myself wrote the [Natural Number Game](https://www.ma.imperial.ac.uk/%7Ebuzzard/xena/natural_number_game/), a tutorial for mathematicians interested in learning Lean, which you can play on a computer through a web browser *without having to install anything*. Patrick Massot wrote a [Lean tutorial project](https://github.com/leanprover-community/tutorials) going through some basic results in undergraduate analysis, but here you have to [install Lean 3](https://leanprover-community.github.io/get_started.html#regular-install) to play. If you want more, then the [youtube playlist](https://www.youtube.com/watch?v=8mVOIGW5US4&list=PLlF-CfQhukNlxexiNJErGJd2dte_J1t1N) of talks from the 2020 conference "Lean for the curious mathematician" (LFTCM) is well worth a watch, and if you're reading this in early 2022 and want to participate in such a conference then [applications are open right now for LFTCM 2022](https://icerm.brown.edu/topical_workshops/tw-22-lean/)!

Going back to the original question then, Lean is extremely easy to install on linux (I installed it on a new laptop recently and it was just cutting and pasting one line of code and letting things happen by magic), and more of a bore to install on Windows but certainly not difficult. As for learning how to use it, if you have a mathematical background then Lean has a lot of [resources for you to learn from](https://leanprover-community.github.io/learn.html); if you have a more computer-scientific background then Avigad et al's beautiful book [Theorem Proving In Lean](https://leanprover.github.io/theorem_proving_in_lean/) provides a great entry point. Either way, the Lean Zulip chat linked to above provides an efficient and polite and 24/7 helpline for questions of all levels; basic questions, for example, are welcome in the `#new members` stream.

$\\endgroup$ 3 $\\begingroup$

## Coq

The easiest proof assistant to start with is

1. The assistant with the best learning resources
2. The assistant with a great community
3. The assistant with the nicest libraries

in that order of priority.

I vote for Coq because of Software Foundations. The software foundation textbooks are like interactive literate programs which you can load into your IDE. The best thing about them is the exercises interspersed in the text, which you can attempt while reading the book if you are reading it on your IDE.

Coq is probably the most widely used proof assistant and I am sure it has many useful libraries. Unfortunately, most Coq tutorials focus on teaching the fundamentals of proof assistants and very few of them talk about using the libraries

$\\endgroup$ 6 $\\begingroup$

I believe it will depend *a lot* on your experience and sensibility, but that a good way of getting started is to have a look at [lets-prove-leftpad](https://github.com/hwayne/lets-prove-leftpad) :

> This is a repository of provably-correct versions of Leftpad.

It gives ~20 (and counting!) different ways of proving that an implementation of Leftpad is correct, and do so in a very pedagogical way. It is probably the best way to observe simple, comparable, examples, and to make an informed decision based on that.

$\\endgroup$ 5 $\\begingroup$

(This answer was originally for [another question](https://proofassistants.stackexchange.com/questions/549/verifying-combinatorial-constructions-choice-of-a-proof-assistant/566?noredirect=1#comment1061_566), but others thought it was better as an answer for this question, or for [this question](https://proofassistants.stackexchange.com/q/105/428).)

I think for these sorts of questions it depends a lot on your goals. Here is some general advice.

- **Is this a fun project to learn a proof assistant?** If so, you may just want to pick the proof assistant which is most appealing to you for other reasons. For example, maybe in the end you really want to start contributing to one of the big libraries of formal mathematics like AFP, mathlib, set.mm, Mizar, etc.
- **Do you want to use a specific logic like HoTT or intuisionistic logic, just to learn it?** Then pick a theorem prover and library which uses that kind of logic and has many good examples, tutorials.
- **Do you want to be able to say that you formalized a particular theorem (maybe because it is your favorite area of mathematics)?** Almost any theorem prover would work, but if you need lots of other areas of mathematics as prerequisite then you should look into what some of the larger math libraries (AFP, mathlib, set.mm, Mizar) already have available and ask if the prerequisites you need play well together.
- **Do you want your theorems and definitions to be used by others for further mathematics?** Then you should likely pick not only a proof assistant, but the formal mathematics library you would like it to eventually go into. If you put your code into another library, the library maintainers will make sure it doesn't "bit rot".
- **Do you want your theorems to be used by yourself or others for certifying software and hardware?** Then again, look for the proof assistants which focus on this sort of thing.
- **Do you want to compute with the objects you are creating?** This can get a bit tricky. Coq, Lean, Agda act as programming languages for working with your objects. (Lean 4 is a lot more capable in this area than Lean 3.) So if your definition is computable, you can compute with it. On a separate topic you can also extract programs from proofs in some proof assistants. I don't know much about this, but it seems from what I have heard this can be hit or miss. A proof is not necessarily optimized to be good code. Also, I think the proof needs to be constructive for automatic extraction. Another option is just to code up the algorithm used in the proof directly (in say Lean 4, Agda, or Coq) and then prove it has the properties you want. This way you have both an algorithm and proof. Also, you can use whatever axioms you want for the proof. It doesn't need to be constructive.

$\\endgroup$ $\\begingroup$

I'll answer the question "What is the easiest proof assistant to start with for a programmer" and take the sub-questions one-by-one.

## Which one is the easiest to pick as a language?

Agda, since theorem proving is programming in Agda: one uses forward reasoning, variable binding, and function calls.

There's also a great free book for Agda: [PLFA](https://plfa.github.io/), which is inspired by Software Foundations (Coq)

Some superficial difficulties are related to each other: it's hard to use an editor other than EMACS and many libraries skew toward function names that are heavy in gratuitious, unpronounceable unicode characters.

## Which one is the easiest to install and connect with popular IDEs (such as Visual Studio Code)?

Coq and Idris work great in VSCode. Agda seems partial to EMACS. I haven't tried others.

Arend was designed at JetBrains with great IntelliJ support in mind.

## More advice

I recommend starting with **what problem you're trying to solve** and then going from there.

If you just want to get something proven and start sledgehammering away, then start with the provers that have the best automation. Isabelle and Coq seem to have much better automation than Agda, for example.

If you want to get higher assurance that your software design, data model, or product design makes sense: then a model checker like Alloy or TLA will be much easier to pick up and give more bang for the effort. "Software Abstractions" is not free, but is a fun read, with good examples and practical advice mixed in with a detailled exposition of an incredibly expressive and succinct language.

If you're in it to learn something new, I really think Coq has incredible UX and is something we programmers can learn from. Idris is a little closer to home, but also has ideas that could bleed into future mainstream programming languages.

If you're in it for fun, then there are also some unusual ones. Andrej Bauer has a talk series ["Every proof assistant"](http://math.andrej.com/category/every-proof-assistant/) that covered proof assistants including a [a visual proof assistant](http://math.andrej.com/2020/11/24/homotopy-io/) and [a lispy metaprogramming-oriented prover](http://math.andrej.com/2020/06/22/cur-designing-a-less-devious-proof-assistant/).

$\\endgroup$ $\\begingroup$

[*The Incredible Proof Machine*](https://incredible.pm/)

![[Attachments/2ef159193aed0c0b54b8339a92b6d8a3_MD5.png]]

There is no need to learn syntax to enter, you just drag and drop boxes and connect them, and still learn a lot about rigorous proofs, intro and elim rules, local assumptions, dealing with negation. You’ll soon want to graduate to something bigger, but it’s a good and fun start!

$\\endgroup$ 1 $\\begingroup$

The part of your answer I like best is a "Python of proof assistants".:)

When I see "Python" I read "a programming language which is deceptively simple on the surface level but has totally crazy semantics". On the funnier side of this craziness we have ["Negatypes"](https://www.hillelwayne.com/negatypes/) and there are [long lists](https://github.com/satwikkansal/wtfpython) of "gotchas" including confusing *syntax*.

I don't think proof assistants even remotely approach **that** level of sophistication and "industrial strength".:'D

For one thing proof assistants are built on some variant of Type Theory thus they have *mostly* straightforward core semantics. Due to the fact you can't practically prove soundness for too hairy theory and soundness is a pretty much a requirement for an acceptable Type Theory. Though we're doing much better on the surface syntax level especially with user-extensible parsers of Coq and Lean!:D

Anyway jokes aside I would advertise Isabelle/HOL as a good proof assistant for beginners. Let's examine how it fares on criteria you mentioned.

## How is it is to pick as a language?

Funny thing it comprises several languages, two most important of which are a language for writing *programs* and a language for writing *proofs*.

I consider it a **good** thing for beginners: instead of learning one complicated language for everything (`Bool` vs. `Prop` vs. `Set` vs. `Type`? Wait there's also `SProp`?!) you can learn two simpler ones, or even only proof language (Isar in this case) if you don't care about programming per se. Even if you do care about programming Isabelle/HOL provides a variant of ML for that, which is in my opinion the closest to "Python of statically typed functional languages" in the sense of the most straightforward syntax and semantics. It doesn't have Dependent Types for a change!:D

And for writing proofs Isabelle offers aforementioned Isar language which is pretty much a benchmark for clear structured proofs. On top of that Isabelle/Isar seamlessly integrates very powerful proof automation keeping structure and readability intact which IMO helps beginners a great deal.

## How easy is it to install and connect with popular IDEs (such as Visual Studio Code)?

Installation consists of downloading and unpacking the official distribution. And there's no third step — it's immediately ready to run with "batteries included", including third-party tools like Z3, E prover, etc.

As for connecting to popular IDEs, I suspect not very well at all...:D But on the bright side Isabelle/HOL distribution includes its own jEdit-based IDE quite tailored for easy access to system's facilities.

And when built-in search facilities are not enough you can reach for [https://behemoth.cl.cam.ac.uk/search/](https://behemoth.cl.cam.ac.uk/search/) which also looks in the great [Archive of Formal Proofs](https://www.isa-afp.org/):)

## Availability of learning material

Again the standard distribution includes quite a number of PDFs ranging from tutorials to comprehensive manuals. The most important of them is [Programming and Proving in Isabelle/HOL](https://isabelle.in.tum.de/doc/prog-prove.pdf) which not only introduces Isabelle/HOL/Isar from scratch but also teaches basics of programming and formal logic.

Additionally there's a free book on [algorithms and data structures verification](https://functional-algorithms-verified.org/) and another one on [formally verified semantics](http://concrete-semantics.org/) of programming languages. Both are very approachable and beginner-friendly in my view.

## Availability of online forums willing to cater to beginners

Answer to this question I don't know but maybe this StackExchange corner will be of some help?:D

**PS.** I hope I don't sound mean or dismissive towards Python or other proof assistants... That's nothing more than my personal opinion based on very limited experience 'coz I am but a beginner myself and never formalized anything complicated.

$\\endgroup$ 1 $\\begingroup$

The main issue with this question is that it asks to *compare* proof assistants on several points but people who answer cannot know enough about all proof assistants to make this comparison point by point. Therefore, we end up with several independent answers that are very hard to align, and we do not get any proper answer to the initial question.

As an attempt to overcome this, I propose to answer with a "community wiki" answer. I will structure it and start populating it with answers for the Coq proof assistant, but the idea is that eventually users of other proof assistants update it to add information relevant to theirs.

## How easy is it to pick as a language?

- Coq might not be so easy to pick as a language because it has so many constructs (in particular tactics). However, the best way to not get lost is to start with one textbook and follow it through as this will teach one particular style. Afterward, it will be easier to learn about other styles and to eventually pick one.

## How easy is it to install?

- Coq has become incredibly easy to install thanks to the [Coq Platform](https://github.com/coq/platform/releases). The Coq Platform provides both binary installers for beginners for Linux, macOS, Windows and a set of interactive scripts to install Coq via the opam (source-based) package manager without having to learn opam. In both cases, it makes it trivial to get a working Coq environment where you not only get Coq, but also an IDE (CoqIDE) and a large set of standard libraries that extend Coq significantly in many ways. Since the strength of Coq as a language also comes from its large collection of external packages, it is really important to be up and ready with such packages from the start.

## How easy is it to connect with popular IDEs (such as Visual Studio Code)?

- Coq has great IDE support and from what I know they are all easy to set up. This is summarized on this page: [https://coq.inria.fr/user-interfaces.html](https://coq.inria.fr/user-interfaces.html). In just a few words, it has good editor support packages for VsCode, Emacs, Vim, and also has a standalone IDE for people who prefer that: CoqIDE (not the best editor, but certainly the most straightforward solution). It is also possible to run Coq in the browser (although it will be slower) thanks to jsCoq (related question on jsCoq [here](https://proofassistants.stackexchange.com/questions/29/what-are-the-differences-between-jscoq-and-the-versions-of-coq-that-can-be-downl/177#177)).

## Availability of learning material

- Coq probably surpasses any other proof assistant by the richness of its available learning material. The page [https://coq.inria.fr/documentation](https://coq.inria.fr/documentation) summarizes the most important resources, although others are available (in particular in other languages). There are many great books to start with, and the choice of which one really depends on the style. One of the most acclaimed and easy to follow is the Software Foundations series.

## Availability of online forums willing to cater to beginners

- Like most other important proof assistants today, Coq provides several forums to discuss. The most active is the [Zulip chat](https://coq.zulipchat.com/), but there is also a more structured (albeit less active) [Discourse forum](https://coq.discourse.group/), a mailing list, and Coq users are also quite active on the Stack Exchange forums, Reddit, IRC, Twitter, etc. On Discourse, there are non-English categories as well, and beyond that there are active non-English Coq communities in other places that I couldn't precisely cite. A lot of the available channels are summarized at [https://coq.inria.fr/community.html](https://coq.inria.fr/community.html).

$\\endgroup$ 0 $\\begingroup$

Theorema ([https://risc.jku.at/sw/theorema/](https://risc.jku.at/sw/theorema/)) is effectively a proof assistant built on top of Mathematica; it is an evolving project. If you are familiar with Mathematica and the Wolfram Language, the language is very easy to pick up, and installation of the package is as easy as installing any other package for Mathematica (trivial). As to the learning materials and forums, I am not sure. But I think it is worth checking out if you are at least familiar with the Wolfram Language.

In addition to Theorema, a bridge between Mathematica and Lean already exists (see [https://robertylewis.com/leanmm/](https://robertylewis.com/leanmm/)).

More information about either project can be found here: [https://community.wolfram.com/groups/-/m/t/2957419](https://community.wolfram.com/groups/-/m/t/2957419).

$\\endgroup$ $\\begingroup$

## Prooftoys - for true beginners

Prooftoys, on the [https://prooftoys.org/](https://prooftoys.org/) website, is a proof assistant and learning resources designed for learning about logic and computer-based reasoning. It is aimed specifically for users who are not experienced with proof assistants, including users new to mathematical logic.

About the bullet points in the question -

- How easy is it to pick (up)? This is what Prooftoys is all about.
	A big part of this is its point-and-click graphical user interface, but it also strives for conceptual simplicity and an easy learning curve.
	It does not ask the user to learn a language other than the language of formulas. A proof in progress displays as sequence of proved statements. From this display, in most cases the user selects a term or complete existing step by pointing and clicking, and the system offers a filtered menu of actions applicable to the selection, including any fact that can be used as a rewrite rule.
	There are several worked problems or puzzles. Also every proof and every proof step is a "white box" that can be displayed to any desired level of detail through the user interface.
	The logic is classical simple type theory with only booleans and individuals as base types. Numeric types are treated as sets (predicates) such as ℝ or ℕ.
- Installation - Prooftoys is Web-based, running in the user's browser, so there is no installation.
- Learning material -- the learning material is all collected on the website, and aimed at beginners. In particular there is a **[Natural Numbers Game](https://prooftoys.org/number-game/tutorial1/)** tutorial modeled closely on the tutorial developed at University College London for Lean.
- The author is delighted to be of personal assistance, but there is no forum at this time.

There is no significant library of mathematical results and Prooftoys is not set up for building theory libraries, so to work in a particular area of mathematics, look at some more well-established system.

The system does have conveniences such as tautology checking, automatic and semi-automated simplification. It also has tactics to do routine things such as moving or arranging terms.

$\\endgroup$
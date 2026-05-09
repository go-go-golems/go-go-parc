←

→

## Realizability as the Connection between Computable and Constructive Mathematics

- 23 August 2005
- Andrej Bauer
- ,

**Abstract:**  
These are lecture notes for a tutorial seminar which I gave at a satellite seminar of [Computability and Complexity in Analysis 2005](http://cca-net.de/cca2005/) in Kyoto. The main message of the notes is that *computable mathematics is the realizability interpretation of constructive mathematics*. The presentation is targeted at an audience which is familiar with computable mathematics but less so with constructive mathematics, category theory or realizability theory.

**Note:** I have revised the original version from August 23, 2005 and corrected the horrible error at the beginning of Section 2. I would appreciate reports on other mistakes that you find in these notes.

**Download (version of October 16, 2005):** [c2c.pdf](https://math.andrej.com/asset/data/c2c.pdf "Realizability as the Connection between Computable and Constructive Mathematics"), [c2c.ps.gz](https://math.andrej.com/asset/data/c2c.ps.gz "Realizability as the Connection between Computable and Constructive Mathematics")

### Comments

![[Attachments/2ef237532d7272fd7c4b63a6e0ee9dae_MD5.jpg]]

exa

14 October 2005 at 06:54

Although this draft goes beyond my current knowledge, it's interesting enough to make me want to refresh my knowledge about category theory.

I am wondering if there is any seminal resource on constructive set theory, though.

\-- Eray

![[Attachments/605c06badd80f09bef861a1748506a6a_MD5.jpg]]

[Andrej Bauer](http://andrej.com/)

15 October 2005 at 13:03

If you really mean constructive *set theory*, then I would recommend [Notes on Constructive Set Theory](http://www.mittag-leffler.se/preprints/meta/AczelMon_Sep_24_09_16_56.rdf.html) by [Peter Aczel](http://www.cs.man.ac.uk/~petera/) and [Michael Rathjen](http://www.amsta.leeds.ac.uk/Pure/staff/rathjen/rathjen.html). It should be easier to learn constructive set theory from this than from seminal work. If, however, by "constructive set theory" you really mean constructive *mathematics* then the book to read is definitely "Constructive Analysis" by Erret Bishop and Douglas Bridges. It's the constructive mathematics bible.

![[Attachments/2ef237532d7272fd7c4b63a6e0ee9dae_MD5.jpg]]

exa

16 October 2005 at 01:27

Thank you for your comments, Andrej. It's quite hard to learn about constructivism in Turkey, so your help is much appreciated.

We have been trying to understand a point in your paper in the yahoo group ai-philosophy. It might be due to our unfamiliarity with the intricacies of computability theory. (So excuse me if I come off ignorant) However, there is at least one thing that I do not understand.

In definition of Type II computability, you say that this is the definition of a computable real number. First, I am not sure what you mean by a computable sequence. I would ordinarily understand the same thing as Type I. Failing that, I would understand something akin to "computability in the limit" (i.e. finite program-size, infinite running time, infinite tape, no guarantee when a symbol will be written, but the output "converges" to the desired output in the limit).

You say that "Type II representation differs from Type I also in that it can be used to represent any real number, and not just a computable one". By this place, I change my mind into that you just mean each a\_k/b\_k are computable (by definition since they are rational?), and you mean an actually infinite tape which is basically isomorphic to the usual definition of a real number. But here is where I am lost. If I can represent any real number using Type II representation, then uncomputable reals, uncountably many of them, are included in this set. How can Type II be a definition of computability then? What am I misunderstanding?

Again, please excuse me if I am being stupid. I am very interested in theory, and I am just trying to learn.

Regards,

![[Attachments/605c06badd80f09bef861a1748506a6a_MD5.jpg]]

[Andrej Bauer](http://andrej.com/)

16 October 2005 at 02:27

A sequence \`(a\_n)\` is computable if there exists a Turing machine, which on input \`n\` produces output \`a\_n\`. In Type II computability, a real number \`x\` is said to be computable if there exists a computable sequence of rapidly converging approximations to \`x\`. More precisely, there must exist a Turing machine such that, on input \`n\` it outputs a rational number \`a\_n/b\_n\` such that \`|x - a\_n/b\_n| < 2^(-n)\`.

Please **beware** that there is an error in Theorem 2.2 in the version of the notes from August 23, 2005. Actually, I am going to fix this right away, since it is a really gross error on my part. I will post another comment when a new version is available. Hopefully it will also clarify your question.

![[Attachments/605c06badd80f09bef861a1748506a6a_MD5.jpg]]

[Andrej Bauer](http://andrej.com/)

16 October 2005 at 03:28

I have posted a new version of the notes in which the beginning of Section 2 is hopefully correct.

![[Attachments/2ef237532d7272fd7c4b63a6e0ee9dae_MD5.jpg]]

exa

18 October 2005 at 01:28

Andrej, I haven't looked at the updated version yet, but I fail to see how the definition of a computable sequence as you have just described in comment 4 is different from the Effectively Computable class of real numbers (i.e. Turing's definition). It had seemed to me that your intention was to identify the class EC with Type I, and Type II with something else. I, intuitively, can see no difference between the identities of a particular computable sequence, and the unique program that generates it. I shall have another look at the revised version when I have time since you say it will clarify my question.

Regards,

http://myspace.com/malfunct

![[Attachments/2ef237532d7272fd7c4b63a6e0ee9dae_MD5.jpg]]

exa

18 October 2005 at 01:44

That program is of course not unique, sorry. I have to sleep:)

![[Attachments/2ef237532d7272fd7c4b63a6e0ee9dae_MD5.jpg]]

exa

18 October 2005 at 16:16

Hi Andrej,

I've read the revised Section 2. I think it is much clearer right now. I'm glad that my comments helped you correct a theorem.

I would however, as a computer scientist, love to see a reference for the footnote 2. Why did you pick out this particular sense of convergence, it is not clear to me. Why "write-only"? Which class of computable numbers in the literature does this correspond to? (Some of them were mentioned in the h-monotonicity paper that I sent the link of) What happens if you take another sense of convergence?

Also missing (it seems) that the effective variation of Type II computability is identical to Type I computability. In fact, then you might want to say that Type II computability has two variations, rather than three. (?)

As another remark, you change the domain and co-domain of the function, which is nice. But I don't see why you don't change the sense of convergence (or why you change it in only a limited sense). Let me briefly commently on this and you can check for yourself it it makes any sense.:)

The rapid convergence criterion that you used in Type I and Type II computable real is the classical definition of a computable real, e.g. effective computability. But there are, for instance, monotonically converging procedures, that converge so slowly, that you can't put a time bound on the next digit to be output (the approximation procedure for Chaitin's Omega was like that if I'm not mistaken). So the def'n for Type I wouldn't include these (again IIRC and if I'm not mistaken!).

If we return to the footnote 2, you seem to want to get rid of the limitation of rapid convergence in Type II computable function, is that true?

But then I would have two questions: 1. Why aren't you saying that this is computability in the limit, rather than classical computability? (Class of semi-computable reals, etc.) Is this something different in footnote 2? Is "write-only" there to prevent computability in the limit, once a digit is output it can't be read, forever. Why is that so important? Why can't a machine that has unlimited time, go back and and read what it wrote, and re-write that digit? Because it already has infinite input, it can read magical numbers like Omega as input, why can't it do something that ordinary computers can do already?

1. Why aren't you using this different sense of "computable sequence" of Type II computable function directly in the definition for a Type III computable real number, or something like that?

I would be grateful if you could clear my mind about these questions.

Regards,

\-- Eray Ozkural, miserable phd student

PS: I am assuming that footnote "2" does change the meaning of "computable sequence". It is more loose than the usual rapid convergence criteria of the Cauchy sequence. Am I not right?

![[Attachments/605c06badd80f09bef861a1748506a6a_MD5.jpg]]

[Andrej Bauer](http://andrej.com/)

19 October 2005 at 15:03

A reference to footnote 2, which explains briefly how a Type II machine is supposed to perform its infinite computation, is Klaus Weihrauch's book "Computable Analysis". There the motivation for this definition is given. I also give a bit more detail about it in a later section when I formally define Type II computability.

I see now that I made another mistake. Instead of saying that a Type II machien has a "write-only" output tape I should have said that it has "write-once output tape". That is, once it writes something in a cell, it cannot change it. It can of course read its own output, if it so pleases, but this is irrelevant, as it has a working tape on which it can store a readable copy of its output. The motivation for "can write only once" is that we want to be able to know what the output is. If the machine were allowed to write some output and change later, we would never be sure it has written out the final answer.

![[Attachments/2ef237532d7272fd7c4b63a6e0ee9dae_MD5.jpg]]

exa

19 October 2005 at 20:06

I understand. Thus once a digit is decided it is decided, otherwise we would have allowed oscillating computations that don't converge. I had read about such write-once infinite output machines in Schmidhuber's work (a famous AI researcher) and in some papers on computable numbers (but I don't have the best memory so I can't say exactly where:) ). I still haven't gotten around to digesting Weihrauch's book. I'm sure it will be an interesting read. There is always a world that I don't know. I didn't even know Weihrauch's name two weeks ago.

Excuse me for my endless nitpicking but, isn't your revised definition of comment 9. equivalent to monotonic convergence as I say in comment 8.? Or what am I missing? I would be interested in understanding this detail.

You have also encouraged me to read the sections after 3 more carefully.:) I am trying to understand the significance of this metamathematical approach using category theory (right way to say it?), it seems to better defined than the classical debates.

Thanks for answering my comments.

Best Regards,

\-- Eray Ozkural

![[Attachments/605c06badd80f09bef861a1748506a6a_MD5.jpg]]

[Andrej Bauer](http://andrej.com/)

20 October 2005 at 18:34

Further answers to remark 8: Type I and the effective version of Type II are *not* equivalent. In Type I the machine has access to a *program* while in Type II it only has access to the output of a program. It can be shown that this difference is sufficient to make Type I and Type II inequivalent.

No, I do not want to remove the condition of rapid convergence of Cauchy sequences in the definition of reals. The time it takes for a machine to compute the next bit of output has nothing to do with how we describe reals. The point of rapid convergence is not how quickly we can compute approximations to the real, but rather how much information we obtain every time we compute the next term in the Cauchy sequence.

Let me emphasize something here: the correct definition of reals, as well as the correct definitions of every other structure we want to compute with (functions, distributions, etc.) is not something that we need to discover, or to use ingenuity to get at. It is something we can *compute* using standard category-theoretic interpretation of logic in the category of reprentations. This is a main theme of the notes. So I do not really feel it is necessary to defend the definition of reals, as it is simply computed (we may discuss whether I made a computational error, though). Of course, this is a cool "high-level" computation where the "unknown" is a mathematical structure rather than a single number.

![[Attachments/2ef237532d7272fd7c4b63a6e0ee9dae_MD5.jpg]]

exa

20 October 2005 at 20:28

Hi Andrej, thanks for these answers. There is just one thing that is not clear to me (yet). So I think you say that the Type II machine with the "write-once" requirement does not correspond to monotonically converging computable real numbers. That is, I suppose, a larger class of reals, then. (And indeed, one does not need to defend by giving separate arguments why rapid convergence is good enough, it turns out!)

Your remarks about the computation of the mathematical structure are quite interesting and thought-provoking, as well! Even to somebody who is only a beginner in category theory like me, I have seen how this is done in the paper. Would you care to post a few words on the significance of such a computation? I would like to forward that remark to our humble philosophy group which has some well known AI researchers, and I would definitely love to see you there if you'd care to join.

For instance, is it relevant to AI? I find the thesis of the paper quite interesting, that you can *derive* computable mathematics by a certain *representational* interpretation of constructive mathematics. Which sounds as if this would be the rational/epistemologically preferable thing to do. What implications do you think this connection might yield for foundational issues?

![[Attachments/879950e5228f5e0b3dda2d6aad5fd0a5_MD5.jpg]]

[Urs Schreiber](http://ncatlab.org/nlab/show/Urs+Schreiber)

02 March 2014 at 02:14

I happened upon these lecture notes of yours today and found them a nicely informative and enjoyable read. There are now a dozen or so nLab entries citing them...

By the way, vaguely related to this I am wondering if your contribution to the book collection "A Computable Universe: Understanding and Exploring Nature as Computation" by Zenil is available in electronic copy? I'd very much like to have a look (Google Books shows only the first handful of pages of your chapter) or else know what your main claim or punchline there is.
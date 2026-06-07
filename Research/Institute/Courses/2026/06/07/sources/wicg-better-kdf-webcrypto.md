## Introduction

\[I have an existing issue [here](https://github.com/w3c/webcrypto/issues/265), but I'm hoping to get more eyes on it.\]

The `SubtleCrypto.deriveKey` API exposes one password-based KDF, `pbkdf2`, which is quite old and is based on 
repeatedly performing SHA-1 or one of the SHA-2 variants. While it's still acceptable, society as a whole has put quite 
a lot of work into making SHA fast, including with custom hardware. For this reason `pbkdf2` is no longer the default 
recommendation for password-based key derivation. Specifically, as I understand it, `bcrypt` and `scrypt` are the 
standard boring choices these days (with `argon2` sometimes showing up).

Cite: the "password handling" section of [this 
essay](https://latacora.micro.blog/2018/04/03/cryptographic-right-answers.html) gives the right answers for password 
handling as

> Percival, 2009: scrypt or PBKDF2.  
> Ptacek, 2015: In order of preference, use scrypt, bcrypt, and then if nothing else is available PBKDF2.  
> Latacora, 2018: In order of preference, use scrypt, argon2, bcrypt, and then if nothing else is available PBKDF2.

It would be nice if the web platform exposed something other than the "if nothing else is available" option.

\[Edit a few years later: this conflates "password hashing" and "key derivation", which are different. `bcrypt` is a 
reasonable password hashing algorithm but not a reasonable KDF, per 
[this](https://soatok.blog/2021/08/24/programmers-dont-understand-hash-functions/#password-hashing-functions). 
Fortunately both `scrypt` and `argon2` can serve either role.\]

## Use Cases

All existing uses of `pbkdf2` could be replaced by a more secure KDF.

## Goals

Provide an implementation of a standard, more secure KDF.

## Non-goals

Providing any other non-standard KDF, or any other crypto functionality.

## Proposed Solution

`SubtleCrypto.deriveKey` should accept one or more new algorithms of the set { `scrypt`, `bcrypt`, `argon2` }, along 
with appropriate configuration (e.g. cost factor).

## Alternate Approaches

It is of course possible to implement these in userland, but a.) we shouldn't encourage implementing crypto algorithms 
and b.) that implementation will necessarily be much slower than a native one, which is bad for a KDF because you want 
to spend your resources as effectively as possible - a slower implementation means a lower cost factor for the KDF for 
a given amount of time.

The other alternative is to keep using the "if nothing else is available" option we currently have.

## Privacy & Security Considerations

No considerable privacy or security concerns are expected, but we welcome community feedback.

## Let’s Discuss

I don't know exactly which of the three reasonable choices are worth including. Personally I'd be inclined to add all 
of them, but maybe it would be better to just pick one.

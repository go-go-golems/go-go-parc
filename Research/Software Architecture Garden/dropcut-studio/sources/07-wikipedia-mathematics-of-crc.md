The [cyclic redundancy check](https://en.wikipedia.org/wiki/Cyclic_redundancy_check "Cyclic 
redundancy check") (CRC) is a check of the [remainder](https://en.wikipedia.org/wiki/Remainder 
"Remainder") after [division](https://en.wikipedia.org/wiki/Division_\(mathematics\) "Division 
(mathematics)") in the [ring of polynomials](https://en.wikipedia.org/wiki/Polynomial_ring 
"Polynomial ring") over [GF(2)](https://en.wikipedia.org/wiki/GF\(2\) "GF(2)") (the [finite 
field](https://en.wikipedia.org/wiki/Finite_field "Finite field") of [integers 
modulo](https://en.wikipedia.org/wiki/Modular_arithmetic "Modular arithmetic") 2). That is, the set 
of [polynomials](https://en.wikipedia.org/wiki/Polynomial "Polynomial") where each 
[coefficient](https://en.wikipedia.org/wiki/Coefficient "Coefficient") is either zero or one, and 
[arithmetic operations](https://en.wikipedia.org/wiki/Arithmetic_operations "Arithmetic 
operations") wrap around.

Any [string of bits](https://en.wikipedia.org/wiki/Bit_array "Bit array") can be interpreted as the 
coefficients of a polynomial of this sort, and a message has a valid CRC if it is divisible by 
(i.e. is a multiple of) an agreed-on *[generator 
polynomial](https://en.wikipedia.org/wiki/Generator_polynomial "Generator polynomial")*. As an 
example, the message ${\displaystyle 101100}$ is thought of as ${\displaystyle x^{5}+x^{3}+x^{2}}$ 
(which is divisible by ${\displaystyle x^{2}}$, see Polynomial arithmetic modulo 2 below for more 
details). CRCs are convenient and popular because they have good error-detection properties and 
such a multiple may be easily constructed from any *message polynomial* ${\displaystyle M(x)}$ by 
appending an ${\displaystyle n}$ -bit *remainder polynomial* ${\displaystyle R(x)}$ to produce 
${\displaystyle W(x)=M(x)\cdot x^{n}+R(x)}$, where ${\displaystyle n}$ is the degree of the 
generator polynomial.

Although the separation of ${\displaystyle W(x)}$ into the message part ${\displaystyle M(x)}$ and 
the checksum part ${\displaystyle R(x)}$ is convenient for use of CRCs, the error-detection 
properties do not make a distinction; errors are detected equally anywhere within ${\displaystyle 
W(x)}$.

## Formulation

In general, [computation of 
CRC](https://en.wikipedia.org/wiki/Computation_of_cyclic_redundancy_checks "Computation of cyclic 
redundancy checks") corresponds to [Euclidean 
division](https://en.wikipedia.org/wiki/Euclidean_division "Euclidean division") of polynomials 
over GF(2):

${\displaystyle M(x)\cdot x^{n}=Q(x)\cdot G(x)+R(x).}$

Here ${\displaystyle M(x)}$ is the original message polynomial and ${\displaystyle G(x)}$ is the 
degree- ${\displaystyle n}$ generator polynomial. The bits of ${\displaystyle M(x)\cdot x^{n}}$ are 
the original message with ${\displaystyle n}$ zeroes added at the end. The CRC 'checksum' is formed 
by the coefficients of the remainder polynomial ${\displaystyle R(x)}$ whose degree is strictly 
less than ${\displaystyle n}$ by the properties of Euclidean division. The quotient polynomial 
${\displaystyle Q(x)}$ is of no interest. Using [modulo 
operation](https://en.wikipedia.org/wiki/Modulo_operation "Modulo operation"), it can be stated that

${\displaystyle R(x)=M(x)\cdot x^{n}\,{\bmod {\,}}G(x).}$

In communication, the sender attaches the ${\displaystyle n}$ bits of R after the original message 
bits of M, which is equivalent to sending out ${\displaystyle W(x)=M(x)\cdot x^{n}+R(x)}$ (the 
*codeword*). This equivalence can be seen because we know that ${\displaystyle R(x)}$ has degree 
strictly less than ${\displaystyle n}$, and the binary message ${\displaystyle M(x)\cdot x^{n}}$ 
corresponds to is the original message bit shifted left ${\displaystyle n}$ times. Thus appending 
the ${\displaystyle n}$ bits of R (possibly with leading zeros) to the message by just adding the 
polynomials. Writing ${\displaystyle W(x)}$ this way demonstrates that ${\displaystyle W(x){\bmod 
{\,}}G(x)=0}$ as

${\displaystyle M(x)\cdot x^{n}=Q(x)\cdot G(x)+R(x)}$

${\displaystyle \Rightarrow }$

${\displaystyle M(x)\cdot x^{n}-R(x)=Q(x)\cdot G(x)}$

${\displaystyle \Rightarrow }$ because in GF(2) ${\displaystyle -1=1}$

${\displaystyle W(x)=M(x)\cdot x^{n}+R(x)=Q(x)\cdot G(x)}$

The receiver, knowing ${\displaystyle G(x)}$, divides ${\displaystyle W(x)}$ by ${\displaystyle 
G(x)}$ and checks that the remainder is zero. If it is, the receiver discards ${\displaystyle 
R(x)}$ (the last ${\displaystyle n}$ bits) and assumes the received message bits ${\displaystyle 
M(x)}$ are correct.

Software implementations sometimes separate the message into its parts and compare the received 
${\displaystyle R(x)}$ to a value reconstructed from the received message, but hardware 
implementations invariably find the full-length division described above to be simpler.

In practice CRC calculations most closely resemble [long 
division](https://en.wikipedia.org/wiki/Long_division "Long division") in binary, except that the 
subtractions involved do not borrow from more significant digits, and thus become [exclusive 
or](https://en.wikipedia.org/wiki/Exclusive_or "Exclusive or") operations.

A CRC is a [checksum](https://en.wikipedia.org/wiki/Checksum "Checksum") in a strict mathematical 
sense, as it can be expressed as the weighted modulo-2 sum of per-bit 
[syndromes](https://en.wikipedia.org/wiki/Syndrome_decoding#Syndrome_decoding "Syndrome decoding"), 
but that word is generally reserved more specifically for sums computed using larger moduli, such 
as 10, 256, or 65535.

CRCs can also be used as part of [error-correcting 
codes](https://en.wikipedia.org/wiki/Error-correcting_code_memory "Error-correcting code memory"), 
which allow not only the detection of transmission errors, but the reconstruction of the correct 
message. These codes are based on closely related mathematical principles.

## Polynomial arithmetic modulo 2

Since the coefficients are constrained to a single bit, any math operation on CRC polynomials must 
map the coefficients of the result to either zero or one. For example, in addition:

${\displaystyle (x^{3}+x)+(x+1)=x^{3}+2x+1\equiv x^{3}+1{\pmod {2}}.}$

Note that ${\displaystyle 2x}$ is equivalent to zero in the above equation because addition of 
coefficients is performed modulo 2:

${\displaystyle 2x=x+x=x\times (1+1)\equiv x\times 0=0{\pmod {2}}.}$

Polynomial addition modulo 2 is the same as [bitwise 
XOR](https://en.wikipedia.org/wiki/Exclusive_or#Bitwise_operation "Exclusive or"). Since XOR is the 
inverse of itself, polynominal subtraction modulo 2 is the same as bitwise XOR too.

Multiplication is similar (a [carry-less product](https://en.wikipedia.org/wiki/Carry-less_product 
"Carry-less product")):

${\displaystyle (x^{2}+x)(x+1)=x^{3}+2x^{2}+x\equiv x^{3}+x{\pmod {2}}.}$

We can also divide polynomials mod 2 and find the quotient and remainder. For example, suppose 
we're dividing ${\displaystyle x^{3}+x^{2}+x}$ by ${\displaystyle x+1}$. We would find that

${\displaystyle {\frac {x^{3}+x^{2}+x}{x+1}}=(x^{2}+1)-{\frac {1}{x+1}}.}$

In other words,

${\displaystyle (x^{3}+x^{2}+x)=(x^{2}+1)(x+1)-1\equiv (x^{2}+1)(x+1)+1{\pmod {2}}.}$

The division yields a quotient of ${\displaystyle x^{2}+1}$ with a remainder of −1, which, since 
it is odd, has a last bit of 1.

In the above equations, ${\displaystyle x^{3}+x^{2}+x}$ represents the original message bits `111`, 
${\displaystyle x+1}$ is the generator polynomial, and the remainder ${\displaystyle 1}$ 
(equivalently, ${\displaystyle x^{0}}$) is the CRC. The degree of the generator polynomial is 1, so 
we first multiplied the message by ${\displaystyle x^{1}}$ to get ${\displaystyle x^{3}+x^{2}+x}$.

## Variations

There are several standard variations on CRCs, any or all of which may be used with any CRC 
polynomial. *Implementation variations* such as 
[endianness](https://en.wikipedia.org/wiki/Endianness "Endianness") and CRC presentation only 
affect the mapping of bit strings to the coefficients of ${\displaystyle M(x)}$ and ${\displaystyle 
R(x)}$, and do not impact the properties of the algorithm.

- **The remainder on division does not need to be zero.** Although all of the preceding text is 
written in terms of divisibility by the generator polynomial, *any* fixed remainder ${\displaystyle 
S(x)}$ may be used and will perform just as well as a zero remainder. Most commonly, the all-ones 
polynomial ${\displaystyle (x^{n}+1)/(x+1)}$ is used, but, for example, the [asynchronous transfer 
mode](https://en.wikipedia.org/wiki/Asynchronous_transfer_mode "Asynchronous transfer mode") header 
error control field has a remainder of ${\displaystyle x^{6}+x^{4}+x^{2}+1.}$ The one complication 
arises if the same hardware which generates the CRC by finding ${\displaystyle R(x)=M(x)\cdot 
x^{n}{\bmod {G}}(x)+S(x)}$ is used to check the CRC with a full-width division of ${\displaystyle 
W(x)\cdot x^{n}{\bmod {G}}(x).}$ The latter will not produce a remainder of 0, nor of 
${\displaystyle S(x)}$, but of ${\displaystyle S(x)\cdot x^{n}{\bmod {G}}(x).}$ This does not make 
CRC checking any more difficult, you just have to know the expected pattern.
- **The long division may begin with a non-zero remainder.** The remainder is generally computed 
using an ${\displaystyle n}$ -bit [shift register](https://en.wikipedia.org/wiki/Shift_register 
"Shift register") holding the current remainder, while message bits are added and reduction modulo 
${\displaystyle G(x)}$ is performed. Normal division initializes the shift register to zero, but it 
may instead be initialized to a non-zero value. (Again, all-ones is most common, but any pattern 
may be used.) This is equivalent to adding (XORing) the initialization pattern with the first 
${\displaystyle n}$ bits of the message before feeding them into the algorithm. The CRC equation 
becomes ${\displaystyle M(x)\cdot x^{n}+\sum _{i=m}^{m+n-1}x^{i}=Q(x)\cdot G(x)+R(x)}$, where 
${\displaystyle m>\deg(M(x))}$ is the length of the message in bits. The change this imposes on 
${\displaystyle R(x)}$ is a function of the generating polynomial and the message length, 
${\displaystyle \sum _{i=m}^{m+n-1}x^{i}\,{\bmod {\,}}G(x)}$.

These two variations serve the purpose of detecting zero bits added to the message. A preceding 
zero bit adds a leading zero coefficient to ${\displaystyle W(x),}$ which does not change its 
value, and thus does not change its divisibility by the generator polynomial. By adding a fixed 
pattern to the first bits of a message, such extra zero bits can be detected.

Likewise, using a non-zero remainder detects trailing zero bits added to a message. If a 
CRC-protected message ${\displaystyle W(x)}$ has a zero bit appended, the received polynomial is 
${\displaystyle W(x)\cdot x.}$ If the former is divisible by the generator polynomial, so is the 
latter. Using a non-zero remainder ${\displaystyle S(x)}$, appending a zero bit will result in the 
different remainder ${\displaystyle S(x)\cdot x{\bmod {G}}(x)}$, and therefore the extra bit will 
be detected.

In practice, these two variations are invariably used together. They change the transmitted CRC, so 
must be implemented at both the transmitter and the receiver. Both ends must preset their division 
circuitry to all-ones, the transmitter must add the trailing inversion pattern to the result, and 
the receiver must expect this pattern when checking the CRC. If the receiver checks the CRC by 
full-length division, the remainder because the CRC of a full codeword that already includes a CRC 
is no longer zero. Instead, it is a fixed non-zero pattern, the CRC of the inversion pattern of 
${\displaystyle n}$ ones.

These inversions are extremely common but not universally performed, even in the case of the 
[CRC-32](https://en.wikipedia.org/wiki/CRC-32 "CRC-32") or CRC-16-CCITT polynomials. They are 
almost always included when sending variable-length messages, but often omitted when communicating 
fixed-length messages, as the problem of added zero bits is less likely to arise.

## Reversed representations and reciprocal polynomials

### Polynomial representations

All practical CRC generator polynomials have non-zero ${\displaystyle x^{n}}$ and ${\displaystyle 
x^{0}}$ coefficients. It is very common to convert this to a string of ${\displaystyle n}$ binary 
bits by omitting the ${\displaystyle x^{n}}$ coefficient.

This bit string may then be converted to a [binary 
number](https://en.wikipedia.org/wiki/Binary_number "Binary number") using one of two conventions:

- The msbit-first representation has the coefficient of ${\displaystyle x^{n-1}}$ as the most 
significant bit and the coefficient of ${\displaystyle x^{0}}$ (which is always 1) as the least 
significant bit.
- The lsbit-first representation has the coefficient of ${\displaystyle x^{n-1}}$ as the least 
significant bit and the coefficient of ${\displaystyle x^{0}}$ (which is always 1) as the most 
significant bit.

The msbit-first form is often referred to in the literature as the *normal* representation, while 
the lsbit-first is called the *reversed* representation. It is essential to use the correct form 
when implementing a CRC. If the coefficient of ${\displaystyle x^{n-1}}$ happens to be zero, the 
forms can be distinguished at a glance by seeing which end has the bit set.

For example, the degree-16 CCITT polynomial in the forms described (bits inside square brackets are 
included in the word representation; bits outside are implied 1 bits; vertical bars designate 
[nibble](https://en.wikipedia.org/wiki/Nibble "Nibble") boundaries):

```
16 15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0   coefficient
 1 [0  0  0  1 |0  0  0  0 |0  0  1  0 |0  0  0  1]  Normal                        
   [     1     |     0     |     2     |     1    ]  Nibbles of Normal
0x1021

 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
[1  0  0  0 |0  1  0  0 |0  0  0  0 |1  0  0  0] 1   Reverse                       
[     8     |     4     |     0     |     8    ]     Nibbles of Reverse
0x8408

16 15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0
 1 [0  0  0  0 |1  0  0  0 |0  0  0  1 |0  0  0  1]  Reciprocal                    
   [     0     |     8     |     1     |     1    ]  Nibbles of Reciprocal
0x0811

 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16   Reverse reciprocal
16 15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0   Koopman
[1  0  0  0 |1  0  0  0 |0  0  0  1 |0  0  0  0] 1    
[     8     |     8     |     1     |     0    ]     Nibbles
0x8810
```

All the well-known CRC generator polynomials of degree ${\displaystyle n}$ have two common 
hexadecimal representations. In both cases, the coefficient of ${\displaystyle x^{n}}$ is omitted 
and understood to be 1.

- The msbit-first representation is a hexadecimal number with ${\displaystyle n}$ bits, the least 
significant bit of which is always 1. The most significant bit represents the coefficient of 
${\displaystyle x^{n-1}}$ and the least significant bit represents the coefficient of 
${\displaystyle x^{0}}$.
- The lsbit-first representation is a hexadecimal number with ${\displaystyle n}$ bits, the most 
significant bit of which is always 1. The most significant bit represents the coefficient of 
${\displaystyle x^{0}}$ and the least significant bit represents the coefficient of ${\displaystyle 
x^{n-1}}$.

The msbit-first form is often referred to in the literature as the *normal* representation, while 
the lsbit-first is called the *reversed* representation. It is essential to use the correct form 
when implementing a CRC. If the coefficient of ${\displaystyle x^{n-1}}$ happens to be zero, the 
forms can be distinguished at a glance by seeing which end has the bit set.

To further confuse the matter, the paper by P. Koopman and T. Chakravarty [^1] [^2] converts CRC 
generator polynomials to hexadecimal numbers in yet another way: msbit-first, but including the 
${\displaystyle x^{n}}$ coefficient and omitting the ${\displaystyle x^{0}}$ coefficient. This 
"Koopman" representation has the advantage that the degree can be determined from the hexadecimal 
form and the coefficients are easy to read off in left-to-right order. However, it is not used 
anywhere else and is not recommended due to the risk of confusion.

### Reciprocal polynomials

A [reciprocal polynomial](https://en.wikipedia.org/wiki/Reciprocal_polynomial "Reciprocal 
polynomial") is created by assigning the ${\displaystyle x^{n}}$ through ${\displaystyle x^{0}}$ 
coefficients of one polynomial to the ${\displaystyle x^{0}}$ through ${\displaystyle x^{n}}$ 
coefficients of a new polynomial. That is, the reciprocal of the degree ${\displaystyle n}$ 
polynomial ${\displaystyle G(x)}$ is ${\displaystyle x^{n}G(x^{-1})}$.

The most interesting property of reciprocal polynomials, when used in CRCs, is that they have 
exactly the same error-detecting strength as the polynomials they are reciprocals of. The 
reciprocal of a polynomial generates the same *codewords*, only bit reversed — that is, if all 
but the first ${\displaystyle n}$ bits of a codeword under the original polynomial are taken, 
reversed and used as a new message, the CRC of that message under the reciprocal polynomial equals 
the reverse of the first ${\displaystyle n}$ bits of the original codeword. But the reciprocal 
polynomial is not the same as the original polynomial, and the CRCs generated using it are not the 
same (even modulo bit reversal) as those generated by the original polynomial.

## Error detection strength

The error-detection ability of a CRC depends on the degree of its generator polynomial and on the 
specific generator polynomial used. The "error polynomial" ${\displaystyle E(x)}$ is the [symmetric 
difference](https://en.wikipedia.org/wiki/Symmetric_difference "Symmetric difference") of the 
received message codeword and the correct message codeword. An error will go undetected by a CRC 
algorithm if and only if the error polynomial is divisible by the CRC polynomial.

- Because a CRC is based on division, no polynomial can detect errors consisting of a string of 
zeroes prepended to the data, or of missing leading zeroes. However, see [§ 
Variations](#Variations).
- All single bit errors will be detected by any polynomial with at least two terms with non-zero 
coefficients. The error polynomial is ${\displaystyle x^{k}}$, and ${\displaystyle x^{k}}$ is 
divisible only by polynomials ${\displaystyle x^{i}}$ where ${\displaystyle i\leq k}$.
- All two bit errors separated by a distance less than the 
[order](https://en.wikipedia.org/wiki/Order_\(group_theory\) "Order (group theory)") of the 
*primitive polynomial which is a factor of the generator polynomial* will be detected. The error 
polynomial in the two bit case is ${\displaystyle E(x)=x^{i}+x^{k}=x^{k}\cdot (x^{i-k}+1),\;i>k}$. 
As noted above, the ${\displaystyle x^{k}}$ term will not be divisible by the CRC polynomial, which 
leaves the ${\displaystyle x^{i-k}+1}$ term. By definition, the smallest value of ${\displaystyle 
{i-k}}$ such that a polynomial divides ${\displaystyle x^{i-k}+1}$ is the polynomial's order *or 
exponent*. The polynomials with the largest order are called [primitive 
polynomials](https://en.wikipedia.org/wiki/Primitive_polynomial_\(field_theory\) "Primitive 
polynomial (field theory)"), and for polynomials of degree ${\displaystyle n}$ with binary 
coefficients, have order ${\displaystyle 2^{n}-1}$.
- All errors in an odd number of bits will be detected by a polynomial which is a multiple of 
${\displaystyle x+1}$. This is equivalent to the polynomial having an even number of terms with 
non-zero coefficients. *This capacity assumes that the generator polynomial is the product of 
${\displaystyle x+1}$ and a primitive polynomial of degree ${\displaystyle n-i}$ since all 
primitive polynomials except ${\displaystyle x+1}$ have an odd number of non-zero coefficients.*
- All [burst errors](https://en.wikipedia.org/wiki/Error_burst "Error burst") of length 
${\displaystyle n}$ will be detected by any polynomial of degree ${\displaystyle n}$ or greater 
which has a non-zero ${\displaystyle x^{0}}$ term.

(As an aside, there is never reason to use a polynomial with a zero ${\displaystyle x^{0}}$ term. 
Recall that a CRC is the remainder of the message polynomial times ${\displaystyle x^{n}}$ divided 
by the CRC polynomial. A polynomial with a zero ${\displaystyle x^{0}}$ term always has 
${\displaystyle x}$ as a factor. So if ${\displaystyle K(x)}$ is the original CRC polynomial and 
${\displaystyle K(x)=x\cdot K'(x)}$, then

${\displaystyle M(x)\cdot x^{n-1}=Q(x)\cdot K'(x)+R(x)}$

${\displaystyle M(x)\cdot x^{n}=Q(x)\cdot x\cdot K'(x)+x\cdot R(x)}$

${\displaystyle M(x)\cdot x^{n}=Q(x)\cdot K(x)+x\cdot R(x)}$

That is, the CRC of any message with the ${\displaystyle K(x)}$ polynomial is the same as that of 
the same message with the ${\displaystyle K'(x)}$ polynomial with a zero appended. It is just a 
waste of a bit.)

The combination of these factors means that good CRC polynomials are often primitive polynomials 
(which have the best 2-bit error detection) or primitive polynomials of degree ${\displaystyle 
n-1}$, multiplied by ${\displaystyle x+1}$ (which detects all odd numbers of bit errors, and has 
half the two-bit error detection ability of a primitive polynomial of degree ${\displaystyle 
n}$).[^1]

### Bitfilters

Analysis using bitfilters [^1] allows one to very efficiently determine the properties of a given 
generator polynomial. The results are the following:

1. All burst errors (but one) with length no longer than the generator polynomial can be detected 
by any generator polynomial ${\displaystyle 1+\cdots +x^{n}}$. This includes 1-bit errors (burst of 
length 1). The maximum length is ${\displaystyle n+1}$, when ${\displaystyle n}$ is the degree of 
the generator polynomial (which itself has a length of ${\displaystyle n+1}$). The exception to 
this result is a bit pattern the same as that of the generator polynomial.
2. All uneven bit errors are detected by generator polynomials with even number of terms.
3. 2-bit errors in a (multiple) distance of the longest bitfilter of even parity to a generator 
polynomial are not detected; all others are detected. For degrees up to 32 there is an optimal 
generator polynomial with that degree and even number of terms; in this case the period mentioned 
above is ${\displaystyle 2^{n-1}-1}$. For ${\displaystyle n=16}$ this means that blocks of 32,767 
bits length do not contain undiscovered 2-bit errors. For uneven number of terms in the generator 
polynomial there can be a period of ${\displaystyle 2^{n}-1}$; however, these generator polynomials 
(with odd number of terms) do not discover all odd number of errors, so they should be avoided. A 
list of the corresponding generators with even number of terms can be found in the link mentioned 
at the beginning of this section.
4. All single bit errors within the bitfilter period mentioned above (for even terms in the 
generator polynomial) can be identified uniquely by their residual. So CRC method can be used to 
correct single-bit errors as well (within those limits, e.g. 32,767 bits with optimal generator 
polynomials of degree 16). Since all odd errors leave an odd residual, all even an even residual, 
1-bit errors and 2-bit errors can be distinguished. However, like other 
[SECDED](https://en.wikipedia.org/wiki/SECDED "SECDED") techniques, CRCs cannot always distinguish 
between 1-bit errors and 3-bit errors. When 3 or more bit errors occur in a block, CRC bit error 
correction will be erroneous itself and produce more errors.

[^1]: Koopman, Philip (July 2002). ["32-bit cyclic redundancy codes for Internet 
applications"](http://www.ece.cmu.edu/~koopman/networks/dsn02/dsn02_koopman.pdf) (PDF). 
*Proceedings International Conference on Dependable Systems and Networks*. pp. 459–468. 
[CiteSeerX](https://en.wikipedia.org/wiki/CiteSeerX_\(identifier\) "CiteSeerX (identifier)") 
[10.1.1.11.8323](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.11.8323). 
[doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi 
(identifier)"):[10.1109/DSN.2002.1028931](https://doi.org/10.1109%2FDSN.2002.1028931). 
[ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") 
[978-0-7695-1597-7](https://en.wikipedia.org/wiki/Special:BookSources/978-0-7695-1597-7 
"Special:BookSources/978-0-7695-1597-7"). 
[S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") 
[14775606](https://api.semanticscholar.org/CorpusID:14775606). Retrieved 14 January 2011. - 
verification of Castagnoli's results by exhaustive search and some new good polynomials

[^2]: Koopman, Philip; Chakravarty, Tridib (June 2004). ["Cyclic redundancy code (CRC) polynomial 
selection for embedded 
networks"](http://www.ece.cmu.edu/~koopman/roses/dsn04/koopman04_crc_poly_embedded.pdf) (PDF). 
*International Conference on Dependable Systems and Networks, 2004*. pp. 145–154. 
[CiteSeerX](https://en.wikipedia.org/wiki/CiteSeerX_\(identifier\) "CiteSeerX (identifier)") 
[10.1.1.648.9080](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.648.9080). 
[doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi 
(identifier)"):[10.1109/DSN.2004.1311885](https://doi.org/10.1109%2FDSN.2004.1311885). 
[ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") 
[978-0-7695-2052-0](https://en.wikipedia.org/wiki/Special:BookSources/978-0-7695-2052-0 
"Special:BookSources/978-0-7695-2052-0"). 
[S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") 
[793862](https://api.semanticscholar.org/CorpusID:793862). Retrieved 14 January 2011. – analysis 
of short CRC polynomials for embedded applications

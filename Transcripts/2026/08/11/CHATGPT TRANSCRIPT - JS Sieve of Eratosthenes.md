# JS Sieve of Eratosthenes

- URL: https://chatgpt.com/c/6a6e30f1-a5a4-83ea-b64e-c38ce6ef613a
- Created: 2026-08-01T17:46:54.068Z

---

> [image: sediment://file_00000000a1fc81f7a7c9a96c60ea86a2]
> Teach me I’m a js developer

<details><summary>💭 Thinking</summary>

**Teaching the sieve**

I’m reading the diagram as a lazy prime generator: take the first number, remove its multiples from the remaining stream, then recursively repeat. In JavaScript, generators provide the needed delayed evaluation; I’ll map each Lisp operation directly.

**Taught the sieve method**

</details>

## What the diagram is doing

This is the **Sieve of Eratosthenes**, expressed as a lazy stream pipeline.

Think of the input as an infinite JavaScript generator:

```js
2, 3, 4, 5, 6, 7, 8, 9, ...
```

The algorithm can be written conceptually as:

```txt
sieve(stream):
  prime = first item
  rest  = remaining items

  output prime

  remove multiples of prime from rest
  recursively sieve the filtered rest
```

Or mathematically:

```txt
sieve(p :: rest)
  = p :: sieve(filter(x => x % p !== 0, rest))
```

The `::` means “construct a stream with this head and a lazily evaluated tail.”

## Translating the boxes into JavaScript

| Diagram term | JavaScript equivalent |
|---|---|
| stream | iterable or generator |
| `car` | first value from `iterator.next()` |
| `cdr` | the remaining iterator |
| `filter: not divisible?` | lazy generator filter |
| inner `sieve` | recursive generator |
| `cons` | `yield head`, then `yield* tail` |

The dashed line matters: the first number is sent both to the output and into the filter as the divisor.

## Runnable JavaScript version

```js
function* integersFrom(start = 2) {
  let current = start;

  while (true) {
    yield current++;
  }
}

function* lazyFilter(iterable, predicate) {
  for (const value of iterable) {
    if (predicate(value)) {
      yield value;
    }
  }
}

function* sieve(iterable) {
  const iterator = iterable[Symbol.iterator]();

  // "uncons": split the stream into car and cdr
  const first = iterator.next();

  if (first.done) {
    return;
  }

  const prime = first.value; // car

  // "cons" the prime onto the output stream
  yield prime;

  // Filter the cdr, then recursively sieve it
  const candidates = lazyFilter(
    iterator,
    number => number % prime !== 0
  );

  yield* sieve(candidates);
}

function take(iterable, count) {
  const result = [];

  for (const value of iterable) {
    result.push(value);

    if (result.length === count) {
      break;
    }
  }

  return result;
}

const primes = sieve(integersFrom(2));

console.log(take(primes, 15));
// [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
```

## Walking through the first stages

Start with:

```txt
2, 3, 4, 5, 6, 7, 8, 9, 10, 11, ...
```

The outer sieve takes `2`.

```txt
output: 2
```

It creates a filter that removes multiples of `2`:

```txt
3, 5, 7, 9, 11, 13, 15, ...
```

The nested sieve takes `3`.

```txt
output: 2, 3
```

It creates another filter that removes multiples of `3`:

```txt
5, 7, 11, 13, 17, 19, ...
```

The next nested sieve takes `5`:

```txt
output: 2, 3, 5
```

This continues indefinitely. Conceptually, the pipeline grows like this:

```txt
integers
  → remove multiples of 2
  → remove multiples of 3
  → remove multiples of 5
  → remove multiples of 7
  → ...
```

Every prime discovered creates another filter stage.

## Why laziness is essential

This eager version cannot work:

```js
const numbers = [2, 3, 4, 5 /* ... infinity */];
```

You cannot construct an infinite array before processing it.

Generators solve that problem. Calling:

```js
primes.next();
```

only performs enough computation to produce the next prime. The remaining stream is suspended until another value is requested.

That is also what the diagram’s `cons` represents:

```js
yield prime;
yield* sieve(filteredRest);
```

The prime is available immediately. The recursive tail is evaluated incrementally.

## The key idea

The diagram is not showing a loop over a collection. It is showing a dynamically growing network of lazy transformations:

```txt
source → filter → filter → filter → ...
```

In JavaScript terms, it combines:

- iterators for stateful traversal,
- generators for lazy production,
- closures for remembering each prime,
- recursion for building the next pipeline stage,
- composition for treating the entire system as another stream.

The outer `sieve` consumes a stream and produces a stream, so another `sieve` can be placed inside it. That is the “modularity” the chapter is illustrating.


---

> How on esp32 with 32kB of ram

<details><summary>💭 Thinking</summary>

**Designing ESP32 implementation**

I’m translating the conceptual pipeline into memory-efficient Arduino C++. I’m using an odd-only packed bitset, static allocation, and loops instead of streams or boolean arrays; 200,000 values require roughly 12.5 KB.

**Designed ESP32 implementation**

**Sizing the memory plan**

I’m treating 32 KB as a tight overall budget. A bounded sieve is safer than an ever-growing lazy pipeline; I’d reserve RAM for runtime and networking, use static storage, and choose a smaller segment or packed bitset.

**Sized the memory plan**

</details>

Assuming **32 KB is the RAM available to your program**, do not implement the diagram literally as recursive generators and filters. Each discovered prime would create another filter object and eventually exhaust memory.

On the ESP32, flatten it into:

```text
counter/segment → packed bitset → emit prime
```

The “infinite stream” means values are produced as needed, not that they are stored.

## Fixed upper limit: packed odd-number sieve

Store one bit per odd number:

```text
RAM ≈ limit / 16 bytes
```

Examples:

| Maximum number | Bitmap RAM |
|---:|---:|
| 100,000 | 6.1 KB |
| 200,000 | 12.2 KB |
| 300,000 | 18.3 KB |
| 400,000 | 24.4 KB |

A limit around `200,000` leaves room for the stack, serial buffers, and other application state.

### Arduino/ESP32 implementation

```cpp
#include <Arduino.h>

constexpr uint32_t LIMIT = 200000;

// Only odd numbers are represented.
// Number n maps to bit index n / 2.
constexpr size_t ODD_COUNT = (LIMIT / 2) + 1;
constexpr size_t BITSET_BYTES = (ODD_COUNT + 7) / 8;

// Static storage avoids stack overflow and heap fragmentation.
static uint8_t composite[BITSET_BYTES];

static inline bool isComposite(uint32_t oddNumber) {
  const uint32_t index = oddNumber >> 1;

  return composite[index >> 3] &
         static_cast<uint8_t>(1U << (index & 7));
}

static inline void markComposite(uint32_t oddNumber) {
  const uint32_t index = oddNumber >> 1;

  composite[index >> 3] |=
      static_cast<uint8_t>(1U << (index & 7));
}

void emitPrime(uint32_t prime) {
  // Replace this with MQTT, storage, calculation, etc.
  Serial.println(prime);
}

void runSieve() {
  if (LIMIT >= 2) {
    emitPrime(2);
  }

  // Mark composites. p <= LIMIT / p avoids p*p overflow.
  for (uint32_t p = 3; p <= LIMIT / p; p += 2) {
    if (isComposite(p)) {
      continue;
    }

    // Smaller multiples were already handled by smaller primes.
    const uint32_t step = p * 2;

    for (uint32_t multiple = p * p;
         multiple <= LIMIT;
         multiple += step) {
      markComposite(multiple);
    }
  }

  // Emit values instead of storing a list of primes.
  for (uint32_t number = 3; number <= LIMIT; number += 2) {
    if (!isComposite(number)) {
      emitPrime(number);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.printf("Sieve bitmap: %u bytes\n",
                static_cast<unsigned>(sizeof(composite)));

  runSieve();
}

void loop() {
}
```

For `LIMIT = 200000`, the bitmap occupies approximately:

```text
200000 / 16 = 12,500 bytes
```

## How this corresponds to the book diagram

| Book concept | ESP32 implementation |
|---|---|
| Input stream | Integer loop |
| `car` | Current prime |
| `cdr` | Remaining numbers |
| divisibility filter | Marking multiples in the bitmap |
| recursive `sieve` | Nested loops |
| `cons` | Calling `emitPrime()` |
| lazy output | Process each prime without storing it |

The important memory optimization is this:

```cpp
emitPrime(number);
```

rather than:

```cpp
primes.push_back(number);
```

The prime is consumed immediately and forgotten unless the application actually needs to retain it.

## For numbers beyond the bitmap limit

Use a **segmented sieve**. For example, a 4 KB buffer can represent:

```text
4096 bytes × 8 bits = 32,768 odd numbers
```

That corresponds to a numeric interval approximately `65,536` integers wide. Process one interval, emit its primes, clear the same 4 KB buffer, and process the next interval.

Conceptually:

```js
for (let low = 3; low <= maximum; low += segmentWidth) {
  clear(segment);
  markMultiplesOfKnownPrimes(segment, low);
  emitUnmarkedNumbers(segment, low);
}
```

This is the embedded version of laziness: **bounded reusable storage**, not a growing chain of generator objects.

When JavaScript runs directly on the ESP32, use a `Uint8Array` bitmap and avoid normal arrays, objects, closures, and recursive generators in the sieve’s inner path. The same algorithm applies, but Arduino C++ or ESP-IDF C will use substantially less RAM.


---

> Give me exercises I am not a embedded developer

<details><summary>💭 Thinking</summary>

**Designing a learning path**

I’m building exercises that start with familiar JavaScript, then introduce fixed memory, bitsets, integer limits, timing, and C++/ESP32 constraints. I’ll use the prime sieve as a running project, with practical checkpoints and clear success criteria.

**Designed a learning path**

</details>

Use JavaScript first to learn the embedded constraints, then port the final exercises to ESP32 C++.

## Embedded mindset

On a small device:

- Memory has a fixed budget.
- Avoid arrays that grow indefinitely.
- Avoid recursion when depth can grow.
- Process data incrementally.
- Reuse buffers.
- Prefer fixed-width integers and check overflow.
- Output values instead of storing everything.

## Exercise 1: Calculate the memory budget

A sieve stores one byte for every integer.

```js
const limit = 100_000;
const bytesRequired = limit + 1;
```

Answer:

1. How many kilobytes does this require?
2. Does it fit in 32 KB?
3. What maximum `limit` fits if only 20 KB is available for the sieve?

Then calculate the memory when using one **bit** per integer:

```js
const bytesRequired = Math.ceil((limit + 1) / 8);
```

Expected result for `limit = 100_000`:

```txt
Byte array: about 100 KB
Bit array: about 12.2 KB
```

## Exercise 2: Produce values without storing them

Write a function that processes numbers from `1` to `1_000_000` without creating an array.

Bad embedded-style code:

```js
const numbers = [];

for (let i = 1; i <= 1_000_000; i++) {
  numbers.push(i);
}
```

Your version should call a consumer immediately:

```js
function emit(value) {
  // Pretend this sends the value over Serial.
}

function processNumbers(limit) {
  // Implement without an array.
}
```

Success condition:

```js
let sum = 0;

function emit(value) {
  sum += value;
}

processNumbers(100);

console.log(sum); // 5050
```

The lesson is that output does not need to remain in memory.

## Exercise 3: Implement a fixed-capacity buffer

Normal JavaScript arrays grow dynamically. Simulate an embedded buffer using `Uint8Array`.

```js
class FixedBuffer {
  constructor(capacity) {
    this.data = new Uint8Array(capacity);
    this.length = 0;
  }

  push(value) {
    // Return false when full.
  }

  clear() {
    // Reset the logical length.
  }
}
```

Required behavior:

```js
const buffer = new FixedBuffer(3);

console.log(buffer.push(10)); // true
console.log(buffer.push(20)); // true
console.log(buffer.push(30)); // true
console.log(buffer.push(40)); // false

console.log(buffer.data);   // Uint8Array containing 10, 20, 30
console.log(buffer.length); // 3
```

Constraint: do not replace `this.data` with a larger array.

## Exercise 4: Build a bitset

Create a class that stores boolean values using individual bits.

```js
class BitSet {
  constructor(bitCount) {
    this.bytes = new Uint8Array(Math.ceil(bitCount / 8));
  }

  set(index) {
    // Mark the bit as 1.
  }

  get(index) {
    // Return true or false.
  }

  clear(index) {
    // Mark the bit as 0.
  }
}
```

Useful formulas:

```js
const byteIndex = index >> 3;
const bitIndex = index & 7;
const mask = 1 << bitIndex;
```

Tests:

```js
const bits = new BitSet(100);

bits.set(3);
bits.set(19);

console.log(bits.get(3));  // true
console.log(bits.get(4));  // false
console.log(bits.get(19)); // true

bits.clear(3);

console.log(bits.get(3));  // false
```

Do not copy the array during `set`, `get`, or `clear`.

## Exercise 5: Write a packed prime sieve

Use your `BitSet` to find primes up to a fixed limit.

Starter:

```js
function sieve(limit, emitPrime) {
  const composite = new BitSet(limit + 1);

  for (let candidate = 2; candidate <= limit; candidate++) {
    // Skip marked composites.
    // Emit unmarked candidates.
    // Mark their multiples.
  }
}
```

Test:

```js
const primes = [];

sieve(30, prime => primes.push(prime));

console.log(primes);
// [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

Important constraint:

Start marking at:

```js
candidate * candidate
```

rather than:

```js
candidate * 2
```

Think about why smaller multiples have already been marked.

## Exercise 6: Store only odd numbers

Improve the sieve so that it does not represent even numbers.

Map an odd number to a bit index:

```js
const index = number >> 1;
```

Examples:

```txt
3  → index 1
5  → index 2
7  → index 3
9  → index 4
```

Required structure:

```js
function oddOnlySieve(limit, emitPrime) {
  if (limit >= 2) {
    emitPrime(2);
  }

  const composite = new BitSet(Math.floor(limit / 2) + 1);

  // Examine only odd candidates.
  // Mark only odd multiples.
}
```

The inner marking loop should advance by:

```js
candidate * 2
```

Test up to `100_000` and report:

```js
console.log(composite.bytes.length);
```

Target: approximately `6.1 KB`.

## Exercise 7: Avoid multiplication overflow

Embedded integers have fixed sizes. JavaScript numbers hide much of this problem.

Assume an unsigned 32-bit integer:

```txt
maximum = 4,294,967,295
```

This condition can overflow:

```cpp
p * p <= limit
```

Rewrite it as:

```cpp
p <= limit / p
```

In JavaScript, write two functions:

```js
function unsafeCondition(p, limit) {
  return /* p * p comparison */;
}

function safeCondition(p, limit) {
  return /* division comparison */;
}
```

Then explain why the second form is safer when ported to C or C++.

## Exercise 8: Process work in chunks

Embedded programs often need to continue handling Wi-Fi, buttons, or sensors. A long sieve loop can block everything.

Write a class that performs at most 100 iterations per call:

```js
class IncrementalCounter {
  constructor(limit) {
    this.current = 0;
    this.limit = limit;
    this.done = false;
  }

  step(maxIterations) {
    // Perform limited work.
    // Return true when completely finished.
  }
}
```

Test:

```js
const counter = new IncrementalCounter(1000);

let calls = 0;

while (!counter.step(100)) {
  calls++;
}

console.log(counter.current); // 1000
console.log(calls);           // around 9 or 10
```

Then apply the same idea to prime generation: each call should perform only a bounded amount of marking or scanning.

## Exercise 9: Implement a segmented sieve

Use a reusable buffer representing only a small range.

Constraints:

```js
const SEGMENT_BYTES = 256;
```

That provides:

```txt
256 × 8 = 2,048 bits
```

When storing only odd values, one segment can represent about 4,096 consecutive integers.

High-level structure:

```js
function segmentedSieve(limit, emitPrime) {
  const segment = new Uint8Array(256);

  for (let low = 3; low <= limit; low += 4096) {
    const high = Math.min(low + 4095, limit);

    segment.fill(0);

    // Mark composite values in [low, high].
    // Emit unmarked odd values.
    // Reuse the same segment for the next range.
  }
}
```

Test:

```js
let count = 0;

segmentedSieve(100_000, () => {
  count++;
});

console.log(count); // 9592
```

Hard part: calculate the first multiple of each prime inside the current segment.

A useful starting formula is:

```js
let first = Math.ceil(low / prime) * prime;
```

Then ensure `first` is at least `prime * prime` and is odd.

## Exercise 10: Port the fixed buffer to C++

Start with a small ESP32-style program:

```cpp
#include <Arduino.h>

constexpr size_t CAPACITY = 16;

struct FixedBuffer {
  uint8_t data[CAPACITY];
  size_t length = 0;

  bool push(uint8_t value) {
    // Return false if full.
  }

  void clear() {
    // Reset length.
  }
};

void setup() {
  Serial.begin(115200);

  FixedBuffer buffer;

  for (uint8_t value = 0; value < 20; value++) {
    if (!buffer.push(value)) {
      Serial.println("Buffer full");
      break;
    }
  }

  Serial.printf("Stored: %u\n",
                static_cast<unsigned>(buffer.length));
}

void loop() {}
```

Goals:

- Do not use `new`.
- Do not use `malloc`.
- Do not use `std::vector`.
- Do not allocate large arrays inside functions.
- Confirm that the seventeenth insertion fails.

## Capstone: Prime producer with a strict RAM limit

Create a prime generator with these requirements:

```txt
Maximum value: 1,000,000
Working bitmap: no more than 2 KB
No recursion
No growing arrays
No list of all discovered primes
Process at most 500 inner-loop iterations per tick
Emit each prime immediately
```

Suggested interface:

```js
class PrimeProducer {
  constructor(limit, emitPrime) {
    // Fixed-size state only.
  }

  tick(maxWork) {
    // Return true when complete.
  }
}
```

Simulate an embedded main loop:

```js
const producer = new PrimeProducer(
  1_000_000,
  prime => console.log(prime)
);

const timer = setInterval(() => {
  const done = producer.tick(500);

  // Other application work could run here.
  console.log("device is still responsive");

  if (done) {
    clearInterval(timer);
  }
}, 1);
```

Start with Exercises 1–4. Exercise 4 is the key transition from ordinary JavaScript data structures to embedded-style memory management.


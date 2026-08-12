## Reasoning about mutual exclusion with sync.Mutex

In this section, we study the [`Mutex` lock from Go's standard library](https://pkg.go.dev/sync#Mutex). As an example, we implement and specify `SafeCounter`, a variation of the `Counter` from the [goroutines example](https://viperproject.github.io/gobra-book/05/goroutine.html) that is safe to use concurrently. We use `Mutex` to guarantee mutual exclusion, ensuring that at most one goroutine can modify the field `count` at a time.

```
import "sync"

// SafeCounter is safe to use concurrently.
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

/*@
pred mutexInvariant(v *int) {
    acc(v)
}

pred (c *SafeCounter) Mem() {
    acc(c.mu.LockP()) && c.mu.LockInv() == mutexInvariant!<&c.count!>
}
@*/
```

The `Mem` predicate for `*SafeCounter` does not directly contain access permissions, but access to the resource `c.mu.LockP()` will allow us to `Lock` the mutex. Additionally, `c.mu.LockInv() == mutexInvariant!<&c.count!>` specifies the invariant associated with the mutex. `LockInv` returns a [first-class predicate](https://viperproject.github.io/gobra-book/05/first-class-predicates.html), which we compare with the predicate constructor applied with the memory location where `count` is stored. If we unlock, we will gain access to an instance of this predicate, which will allow us to modify `&c.count`. To lock, we will have to give up this predicate instance again.

When we import the `sync` package, Gobra provides predefined specs for this package. All predefined specs included in Gobra can be found [here](https://github.com/viperproject/gobra/tree/master/src/main/resources/stubs).

This declares, among others, the methods `LockInv`, `SetInv`, and the predicate `LockP`, which are not part of the Go API.

```
package sync

type Mutex struct {
    state int32
    stema uint32
}

pred (m *Mutex) LockP()
pred (m *Mutex) UnlockP()

ghost
requires inv() && acc(m) && *m == Mutex{}
ensures m.LockP() && m.LockInv() == inv
decreases
func (m *Mutex) SetInv(ghost inv pred())

ghost
requires acc(m.LockP(), _)
decreases _
pure func (m *Mutex) LockInv() pred()
```

We call them *stubs* as they are abstract and only the signature with a contract is given. Since no bodies are provided, the contracts are assumed to hold. In the case of `Mutex`, the specification models the mutual exclusion property.

The ghost method `SetInv` can be called to initialize a mutex. Access to the mutex (`acc(m)`) is required, and the mutex is zero-valued (`*m == Mutex{}`, it has not been locked yet). `acc(m)` is lost, so we may not interfere with the lock after initialization. To associate the first-class predicate `inv` with the lock, we need to give up access to an instance `inv()` of it. Afterwards, `LockInv` returns the first-class predicate `inv`, and we obtain access to the resource `m.LockP()`.

```
// @ ensures s.Mem()
func New() (s *SafeCounter) {
    c /*@@@*/ := SafeCounter{}
    // @ fold mutexInvariant!<&c.count!>()
    // @ (c.mu).SetInv(mutexInvariant!<&c.count!>)
    // @ fold c.Mem()
    return &c
}
```

When constructing a new `SafeCounter`, we first fold the first-class predicate `mutexInvariant<!&c.count!>` that denotes the resource protected by the lock. Then, we associate this invariant with the mutex using `SetInv`. Finally, we can fold the `Mem` predicate for the `SafeCounter`.

This way, clients only require holding `s.Mem()` predicates, and we can hide the implementation detail of how access is synchronized with a Mutex, again enforcing the information-hiding principle.

Before we annotate the `Increment` method, consider the specifications of `Lock` and `Unlock`:

```
requires acc(m.LockP(), _)
ensures m.LockP() && m.UnlockP() && m.LockInv()()
func (m *Mutex) Lock()

requires acc(m.LockP(), _) && m.UnlockP() && m.LockInv()()
ensures m.LockP()
decreases
func (m *Mutex) Unlock()
```

To call either `Lock` or `Unlock`, `acc(m.LockP(), _)` is required. Since the predicate `LockP` is abstract (it has no body), a client cannot obtain an instance by folding; it must have been obtained by `SetInv`. We may only call `Unlock` after previously calling `Lock`. This is modeled by the predicate instance `m.UnlockP()`, which is required to call `Unlock` and can only be obtained by calling `Lock`

```
// @ requires acc(c.Mem(), _)
func (c *SafeCounter) Increment() {
    // @ unfold acc(c.Mem(), _)
    c.mu.Lock()
    // @ unfold mutexInvariant!<&c.count!>()
    c.count += 1
    // @ fold mutexInvariant!<&c.count!>()
    c.mu.Unlock()
}
```

From unfolding `acc(c.Mem(), _)`, we obtain `acc(m.LockP(), _)` and satisfy the precondition of `c.mu.Lock`. In turn, we get access to the predicate instances `m.UnlockP()` and `m.LockInv()()`. Also from `c.Mem()`, we get that `c.mu.LockInv() == mutexInvariant!<&c.count!>`. We can unfold again to get permissions to increment `c.count`. To `Unlock` the mutex, the `mutexInvariant` must be folded back.

As `Increment` requires only `acc(c.Mem(), _)`, the caller retains `acc(c.Mem(), _)` and can dispatch the second goroutine. The program verifies.

```
func main() {
    ctr := New()
    go ctr.Increment()
    go ctr.Increment()
}
```

## Termination in the presence of locks

Programs using locks to synchronize memory access might not terminate. For example, this may happen due to [deadlocks](https://en.wikipedia.org/wiki/Deadlock_\(computer_science\)), or as in the following snippet, due to forgetting to unlock a mutex. Another thread trying to acquire the lock will block indefinitely. The `Lock` stub does not have a `decreases` clause, so we cannot prove the termination of any function, method, or loop that calls this method.

```
// @ requires acc(c.Mem(), _)
func (c *SafeCounter) Increment() {
    // @ unfold acc(c.Mem(), _)
    c.mu.Lock()
    // @ unfold mutexInvariant!<&c.count!>()
    c.count += 1
    // <----- no Unlock here
}
```

Gobra also verifies the program using the modified `Increment` method. It is not enforced that `Unlock` must be called after `Lock`. This is sound since mutual exclusion is not violated, and we specify only partial correctness.

## Full example

```
package main

import "sync"

// SafeCounter is safe to use concurrently.
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

/*@
pred mutexInvariant(v *int) {
    acc(v)
}

pred (c *SafeCounter) Mem() {
    acc(c.mu.LockP()) && c.mu.LockInv() == mutexInvariant!<&c.count!>
}
@*/

// @ requires acc(c.Mem(), _)
func (c *SafeCounter) Increment() {
    // @ unfold acc(c.Mem(), _)
    c.mu.Lock()
    // @ unfold mutexInvariant!<&c.count!>()
    c.count += 1
    // @ fold mutexInvariant!<&c.count!>()
    c.mu.Unlock()
}

// @ ensures s.Mem()
func New() (s *SafeCounter) {
    c /*@@@*/ := SafeCounter{}
    // @ fold mutexInvariant!<&c.count!>()
    // @ (c.mu).SetInv(mutexInvariant!<&c.count!>)
    // @ fold c.Mem()
    return &c
}

func main() {
    ctr := New()
    go ctr.Increment()
    go ctr.Increment()
}
```

## Full sync.Mutex stubs

```
// Copyright 2009 The Go Authors. All rights reserved.
// Use of this source code is governed by a BSD-style
// license that can be found in https://golang.org/LICENSE

package sync

type Mutex struct {
    state int32
    stema uint32
}

pred (m *Mutex) LockP()
pred (m *Mutex) UnlockP()

ghost
requires acc(m.LockP(), _)
decreases _
pure func (m *Mutex) LockInv() pred()

ghost
requires inv() && acc(m) && *m == Mutex{}
ensures m.LockP() && m.LockInv() == inv
decreases
func (m *Mutex) SetInv(ghost inv pred())

requires acc(m.LockP(), _)
ensures m.LockP() && m.UnlockP() && m.LockInv()()
func (m *Mutex) Lock()

requires acc(m.LockP(), _) && m.UnlockP() && m.LockInv()()
ensures m.LockP()
decreases
func (m *Mutex) Unlock()
```

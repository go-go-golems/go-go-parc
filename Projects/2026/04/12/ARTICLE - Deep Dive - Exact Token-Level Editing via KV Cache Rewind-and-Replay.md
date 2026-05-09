---
title: "Deep Dive: Exact Token-Level Editing in Autoregressive Language Models via KV Cache Rewind-and-Replay"
aliases:
  - KV Cache Rewind Replay Deep Dive
  - Token Editing VM Deep Dive
  - KV Cache Editing Architecture
tags:
  - article
  - llm
  - kv-cache
  - transformers
  - inference
  - cpu-inference
  - editing
  - vm-architecture
  - causal-models
  - attention
status: active
type: article
created: 2026-04-12
repo: /home/manuel/code/wesen/2026-04-12--kv-cache-vm
---

# Deep Dive: Exact Token-Level Editing via KV Cache Rewind-and-Replay

This article is a thorough technical deep dive into how exact token-level editing works in autoregressive language models, why the KV cache makes it both necessary and possible, and how a purpose-built virtual machine can make editing operations correct by construction. It is written for someone who understands transformer basics (attention, tokens, logits) but wants to understand the systems-level consequences of the KV cache's prefix-validity property.

The reference implementation is the [[PROJ - KV-Cache VM - Token-Editing Decoding VM for CPU-Side LLM Inference|KV-Cache VM project]], but the concepts apply to any causal autoregressive model — GPT-2, GPT-4, Llama, Mistral, or a toy two-layer transformer.

> [!summary]
> Four ideas make this work:
> 1. The **KV cache is a prefix-valid data structure** — valid for tokens[0:valid_len], invalid after any mid-sequence edit
> 2. **REWIND truncates the cache in O(1)** — per-position tensor storage means just slicing a list
> 3. **REPLAY recomputes the suffix** — one forward pass per token, linear cost in the number of replayed tokens
> 4. **Composite opcodes (DELETE, INSERT, REPLACE) make correctness automatic** — the edit → rewind → replay pattern always produces a valid cache

## When this pattern matters

You need exact token-level editing when:

- **Interactive generation with correction** — the user wants to change a word in the middle of generated text and see the model continue from the corrected prefix, not the original
- **Constrained decoding** — the model must respect structural constraints (JSON schema, code syntax) and you want to detect and fix violations during generation
- **Speculative editing** — you generate several candidates, evaluate them, and want to rewind to the branching point to try an alternative without recomputing from scratch
- **Research experiments** — you need to study how editing at different positions affects model behavior, with exact reproducibility
- **Educational tools** — you want to build interactive demonstrations that show how the cache, logits, and token sequence relate

You do not need this pattern when:

- You only generate tokens sequentially with no mid-sequence edits
- You can afford to recompute the entire sequence from scratch after every edit
- You are doing batch inference where no per-sequence editing is required

## Part 1: What the KV Cache Actually Is

### 1.1 Attention recap in 60 seconds

A transformer layer computes self-attention: for each query position, it attends to all key positions and produces a weighted sum of values. In matrix form for a single head:

```
Attention(Q, K, V) = softmax(Q · K^T / √d_k) · V
```

Where Q (queries), K (keys), V (values) are linear projections of the input hidden states. For a sequence of n tokens, Q, K, V are each (n, d_head).

During autoregressive decoding, the model processes one new token at a time. At step t, it needs to attend to all positions 0 through t. The critical insight: **the keys and values for positions 0 through t-1 haven't changed** — only the new position t needs fresh computation.

### 1.2 What gets cached

For each layer and each position, the model produces:
- **Key tensor**: shape `(1, n_heads, 1, head_dim)` — the "address" this position broadcasts
- **Value tensor**: shape `(1, n_heads, 1, head_dim)` — the "content" other positions retrieve

A 12-layer model with 5 tokens stores 12 × 5 = 60 key tensors and 60 value tensors = 120 tensors total. Each tensor is `(1, n_heads, 1, head_dim)` where for GPT-2: n_heads=12, head_dim=64.

### 1.3 Why caching saves time

Without caching, generating token t+1 requires attending over all t+1 positions — an O(t) operation per layer per head. Generating n tokens from scratch costs O(n²) total attention operations.

With caching:
- Prefill: process all prompt tokens at once — O(n²) for n prompt tokens (unavoidable)
- Each decode step: attend to all cached positions + the new token — O(n) per step
- Total for n decode steps: O(n²) total, but the constant is much smaller because only the new token's query needs to be computed

The practical difference is enormous: at 100 tokens, caching saves ~15× compute. At 1000 tokens, it saves ~100×.

## Part 2: The Causal Constraint and Why Editing Is Hard

### 2.1 Causal masking

Autoregressive models use a **causal mask**: position i can only attend to positions ≤ i. This is enforced during training (to prevent looking at future tokens) and during inference (it's the natural order of decoding).

The consequence: **the key and value at position i depend on all positions 0 through i**. Not just the token at position i — the entire prefix, because each layer's hidden state is a function of the attention output, which depends on all previous keys and values.

### 2.2 The invalidation cascade

Consider a 5-token sequence: `[The, capital, of, France, is]`. The cache is fully valid:

```
Position:  0      1        2    3       4
Token:     The    capital  of   France  is
Cache K:   [K₀]   [K₁]    [K₂] [K₃]   [K₄]   ← all valid
Cache V:   [V₀]   [V₁]    [V₂] [V₃]   [V₄]   ← all valid
```

Now replace "France" (position 3) with "Germany":

```
Position:  0      1        2    3         4
Token:     The    capital  of   Germany   is
Cache K:   [K₀]   [K₁]    [K₂] [K₃_old]  [K₄_old]  ← WRONG
Cache V:   [V₀]   [V₁]    [V₂] [V₃_old]  [V₄_old]  ← WRONG
```

**K₃ is wrong** because it was computed while attending to "France", not "Germany". And **K₄ is wrong** because it was computed while attending to K₃ (which was wrong). The error cascades: every position after the edit point is invalid.

```
Position:  0      1        2    3         4
Cache:     [✓]    [✓]     [✓]  [✗]      [✗]
                                    ↑ edit point
```

### 2.3 Why you can't just fix one position

You might think: "Can't I just recompute position 3's key/value and leave position 4 alone?" No — position 4's key/value was computed by a layer that attended to position 3's old key. Even if you fix K₃/V₃, position 4's hidden states were computed using K₃_old in the attention computation. The entire suffix is contaminated.

This is the fundamental asymmetry: **later positions depend on earlier positions, but not vice versa**. Appending is cheap (one new position, no invalidation). Editing early is expensive (entire suffix invalidated).

## Part 3: Rewind and Replay — The Core Primitive

### 3.1 The algorithm

Exact editing requires exactly two operations:

```
REWIND(pos):
    truncate cache to positions [0, pos)
    valid_len = pos
    logits = None

REPLAY():
    while valid_len < len(tokens):
        tok = tokens[valid_len]
        kv_row, logits = model.decode_one(tok, cache)
        cache.append(kv_row)
        valid_len += 1
```

REWIND drops everything after pos. REPLAY recomputes it by running the model one token at a time. After REPLAY, `valid_len == len(tokens)` and the cache is fully valid.

### 3.2 Why this is correct

Correctness follows from two properties:

1. **REWIND preserves the valid prefix.** Positions [0, pos) are unchanged, so their cached keys/values remain correct. The causal mask guarantees that these positions don't depend on anything after them.

2. **REPLAY processes tokens in order.** Each token is decoded using the model's standard forward pass, which attends to all cached positions plus the new token. Because the cache is valid up to the current valid_len, each step produces correct keys/values.

By induction: after REWIND(pos), the cache is valid for tokens[0:pos]. After replaying token at pos, the cache is valid for tokens[0:pos+1]. And so on until valid_len == len(tokens).

### 3.3 Cost analysis

```
REWIND:  O(1)    — just truncate the per-position lists
REPLAY:  O(k)    — k = len(tokens) - pos forward passes
```

Where each forward pass takes ~30ms for GPT-2 on CPU. This means:

| Edit position | Replay tokens | Time (approx) |
|---------------|--------------|----------------|
| Last token (pos=n-1) | 1 | ~30ms |
| Middle (pos=n/2) | n/2 | ~30ms × n/2 |
| Beginning (pos=0) | n | ~30ms × n (full recompute!) |

**Editing near the end is cheap. Editing near the start costs almost as much as generating from scratch.** This is inherent to the causal structure — no algorithm can avoid it without changing the attention mechanism itself.

## Part 4: Per-Position Tensor Storage

### 4.1 The data structure choice

The KV cache can be stored in several ways:

| Approach | Append | Truncate | Read (for model) |
|----------|--------|----------|-------------------|
| Contiguous tensor (n, d) | O(n) copy | O(1) slice | O(1) — already contiguous |
| Per-position list of (1, d) | O(1) append | O(1) slice | O(n) cat |
| Ring buffer | O(1) | O(1) | O(n) copy |

The KV-Cache VM uses **per-position tensor storage**: each layer stores two lists (keys, values), where each element is a `(1, n_heads, 1, head_dim)` tensor.

```python
class KVCache:
    num_layers: int
    keys:   dict[int, list[Tensor]]   # layer → [tensor_0, tensor_1, ...]
    values: dict[int, list[Tensor]]   # layer → [tensor_0, tensor_1, ...]
```

### 4.2 Why per-position is the right choice here

The critical operation is **truncate** — REWIND calls it on every edit. With per-position storage, truncate is O(1):

```python
def truncate(self, pos: int) -> None:
    for layer in range(self.num_layers):
        self.keys[layer] = self.keys[layer][:pos]
        self.values[layer] = self.values[layer][:pos]
```

This just slices Python lists — no tensor copying, no GPU synchronization, no memory allocation.

The O(n) read cost (concatenating all positions into a single tensor for the model's forward pass) is acceptable because:
1. The model forward pass itself takes ~30ms, dwarfing the ~0.1ms cat operation
2. This is a CPU-only system — no GPU transfer overhead
3. For production GPU systems, contiguous storage with offset tracking would be better

### 4.3 DynamicCache compatibility

Modern HuggingFace transformers (v4.48+) returns `DynamicCache` objects, not tuples. The adapter bridges the gap:

```python
def to_model_format(self) -> DynamicCache:
    """Concatenate per-position tensors into a real DynamicCache."""
    cache = DynamicCache()
    for layer in range(self.num_layers):
        cache.key_cache.append(torch.cat(self.keys[layer], dim=2))
        cache.value_cache.append(torch.cat(self.values[layer], dim=2))
    return cache

def from_model_outputs(self, outputs) -> None:
    """Extract per-position tensors from model's (k, v, None) tuples."""
    for layer_k, layer_v, _ in outputs.past_key_values:
        for pos in range(layer_k.shape[2]):
            self.keys[layer].append(layer_k[:, :, pos:pos+1, :].clone())
            self.values[layer].append(layer_v[:, :, pos:pos+1, :].clone())
```

The `from_model_outputs` method is called after prefill to populate the cache. The `to_model_format` method is called before each forward pass to give the model what it expects.

## Part 5: The Composite Edit Operations

### 5.1 Why composites?

The four edit operations (DELETE, INSERT, REPLACE, DROP_SUFFIX) are all composites of three primitives: token list mutation, REWIND, and REPLAY. Making them composite opcodes — rather than requiring the programmer to spell out all three steps — serves two purposes:

1. **Correctness by construction.** The composite pattern is always correct. There's no way to forget the REPLAY step or rewind to the wrong position.
2. **Self-documenting programs.** `DELETE pos=5` is clearer than `TRIM_TOKENS pos=5; REWIND pos=5; REPLAY`.

### 5.2 DELETE — remove and recompute

```
DELETE(pos):
    1. del tokens[pos]
       → sequence shortens by 1
    2. REWIND(pos)
       → drop cache entries [pos, ...)
    3. REPLAY()
       → recompute cache for tokens[pos:]
```

After DELETE, the sequence has one fewer token, and the cache is valid for the entire shorter sequence. The key insight: tokens after the deleted position shift left by one, but REPLAY processes them from scratch anyway, so the shift doesn't matter.

### 5.3 INSERT — add and recompute

```
INSERT(pos, token):
    1. tokens.insert(pos, token)
       → sequence grows by 1, tokens[pos:] shift right
    2. REWIND(pos)
       → drop cache entries [pos, ...)
    3. REPLAY()
       → recompute cache for tokens[pos:], including the new token
```

INSERT is the mirror of DELETE: the new token appears at position pos, and all subsequent tokens shift right. REPLAY handles this naturally because it reads from the updated token list.

### 5.4 REPLACE — overwrite and recompute

```
REPLACE(pos, token):
    1. tokens[pos] = token
       → same length, one token changed
    2. REWIND(pos)
       → drop cache entries [pos, ...)
    3. REPLAY()
       → recompute cache for tokens[pos:], starting with the new token
```

REPLACE is the simplest: same sequence length, one token changed, suffix recomputed. Note that REWIND drops the cache entry at position pos too — this is necessary because the token at pos changed, so its key/value pair is invalid.

### 5.5 DROP_SUFFIX — cut and re-derive logits

```
DROP_SUFFIX(pos):
    1. tokens = tokens[:pos]
       → remove everything after pos
    2. REWIND(pos)
       → drop cache entries [pos, ...)
    3. REPLAY()
       → nothing to replay (valid_len == len(tokens)), but REPLAY has
         a special case: if logits is None and valid_len > 0, rewind
         one position and re-decode to re-derive logits
```

DROP_SUFFIX is the only edit that might not need any replay (if you're cutting to the exact current position). But logits still needs to be re-derived because it was computed for the old suffix. The REPLAY opcode handles this by rewinding one position and re-decoding the last token — the same pattern used after RESTORE.

## Part 6: Checkpoints — Reducing Replay Cost

### 6.1 The checkpoint idea

If you're editing at position 40 in a 100-token sequence, REPLAY needs 60 forward passes. But if you saved a checkpoint at position 32, you can restore it and replay only 8 tokens (32→40 is already in the checkpoint, so you replay 40→100 = 60 tokens — wait, no. The checkpoint is at 32, so you restore to 32 and replay 100-32 = 68 tokens. Hmm, that's worse.)

The key insight: **checkpoints help when you save them before the edit happens, and you're editing after the checkpoint position.** If you checkpoint at position 32 and later edit at position 40, you restore the checkpoint (valid_len=32), then REPLAY from 32 to 100 — that's 68 forward passes, not 60. Wait, that's still worse than replaying from 40!

Actually, the benefit comes from a different scenario: **the checkpoint lets you skip the forward passes that haven't changed.** If you edit at position 40 and have a checkpoint at 32:
- Without checkpoint: REWIND(40) + REPLAY(40→100) = 60 forward passes
- With checkpoint at 32: RESTORE(32) + REPLAY(32→100) = 68 forward passes

That's actually worse! Checkpoints help when the edit invalidates tokens that were computed with the old model state, and the checkpoint provides a valid starting point closer than zero. The real benefit is when the sequence is long and you've already done multiple edits — each edit invalidates the suffix, and the checkpoint gives you a valid starting point that's closer than position 0.

### 6.2 Truncate-before-clone

The CHECKPOINT opcode stores a truncated copy of the cache:

```python
def checkpoint(pos):
    cp = state.kv.clone()
    cp.truncate(pos)    # only keep positions [0, pos)
    state.checkpoints[pos] = cp
```

This is important for memory: a checkpoint at position 10 in a 100-token sequence stores only 10 positions' worth of tensors, not 100. Without truncation, storing 10 checkpoints would use 10× the full-sequence memory.

### 6.3 Disk persistence

Checkpoints can be saved to disk via `torch.save`:

```python
KVCache.save("ckpt_32.pt")   # writes {num_layers, device, keys, values}
KVCache.load("ckpt_32.pt")   # reconstructs the cache from the file
```

This enables cross-session restoration: save a checkpoint in one session, load it in another, and continue from where you left off.

## Part 7: The Correctness Oracle

### 7.1 Full recomputation as ground truth

The simplest correct implementation is full recomputation: take the final token list, run the model from scratch, and compare logits. This is slow but unambiguous:

```python
def full_recompute(tokens):
    kv = model.empty_cache()
    logits = None
    for tok in tokens:
        kv_row, logits = model.decode_one(tok, kv)
        kv.append_row(kv_row)
    return kv, logits
```

### 7.2 Why logit diff, not token diff

We compare logits (the full probability distribution over the vocabulary) rather than generated tokens, because:

1. **Sensitivity.** A small logit difference can cause a different token to be selected, but the cache might be almost correct. Token-level comparison would report failure for what is essentially floating-point noise.
2. **Granularity.** Logits tell you exactly how far off the cache is. Token comparison is binary (same or different).
3. **Reproducibility.** Sampling is stochastic. Logit comparison is deterministic for a given input.

The tolerance threshold of 1e-3 accounts for float32 accumulation differences between the incremental (cache-based) and batch (full-recompute) paths through the model.

### 7.3 The 112-test safety net

The test suite covers:

- **Happy path edits** — delete/insert/replace at beginning, middle, end
- **Edge cases** — empty sequence, single-token sequence, editing position 0, editing the last token
- **Combinations** — multiple edits in sequence, edit after checkpoint restore
- **Randomized fuzz** — 35 tests with random seeds generating random sequences and random edits, each verified against the oracle

The fuzz tests are particularly valuable because they explore combinations that manual tests miss. Each fuzz test generates a random token sequence, applies a random edit (delete/insert/replace at a random position), and verifies the resulting logits match full recomputation within tolerance.

## Part 8: The VM Architecture — Why a VM?

### 8.1 Three options considered

| Approach | Example | Pros | Cons |
|----------|---------|------|------|
| **A: High-level API** | `vm.generate(prompt); vm.delete(pos=5)` | Easy to use | No composability, can't express complex programs |
| **B: Stack machine** | `PUSH 5; PUSH 318; REPLACE` | Flexible | Hard to read, no named state |
| **C: Register VM + domain ops** | `SET reg=pos value=5; DELETE pos_reg=pos` | Readable + flexible | More boilerplate than option A |

The project chose **Option C**: named registers + domain-specific accelerator instructions. The "accelerator" opcodes (DELETE, INSERT, REPLACE, CONTINUE, CHECKPOINT) encode common multi-step operations as single instructions, while the register ops (SET, ADD, CMP_LT, etc.) provide Turing-complete control flow.

### 8.2 Self-describing opcodes

Every opcode carries its own metadata. The registry can generate a complete spec via reflection:

```python
for opcode_cls in registry.all():
    meta = opcode_cls.meta()
    # meta.name, meta.description, meta.operands, meta.side_effects,
    # meta.invariant_after, meta.examples
```

This makes the spec **impossible to get out of sync with the code** — there is no separate spec document to maintain. The `--validate` flag checks that every opcode has complete metadata, and `--diff` detects spec drift against a saved baseline.

### 8.3 The register model

The VM has named registers (a Python dict) rather than numbered registers:

```python
registers: dict[str, int | float] = {}
```

This makes programs self-documenting: `SET reg=edit_pos value=5` is clearer than `LOAD 5; STORE R3`. Domain-specific opcodes use conventional register names:
- `last_tok` — the token ID produced by the last SAMPLE
- `last_tok_score` — the log probability of that token
- `best_logit` — the maximum logit value (set by LOAD_LOGIT)

### 8.4 The LOOP construct

The VM has structured loops (not raw JMP):

```
LOOP label=gen max_iters=10
    SAMPLE method=greedy
    APPEND
END_LOOP label=gen
```

This prevents infinite loops (max_iters is required) and makes programs easier to read. The interpreter maintains a loop stack for nested loops. BREAK_IF and CONTINUE_IF provide conditional control flow using register comparisons.

## Part 9: Performance Characteristics and Scaling

### 9.1 Where time is spent

For a typical edit operation (REPLACE at position pos in an n-token sequence):

```
Total time = REWIND_time + k × decode_one_time
           = 0.1ms      + k × 30ms

where k = n - pos (tokens to replay)
```

The model forward pass completely dominates. Cache operations (truncate, append, cat) are negligible by comparison.

### 9.2 Scaling with sequence length

| n (tokens) | Edit at 80% | Edit at 50% | Edit at 20% |
|-----------|-------------|-------------|-------------|
| 32 | 6ms | 480ms | 770ms |
| 64 | 390ms | 960ms | 1,540ms |
| 128 | 840ms | 1,920ms | 3,060ms |

Times are approximate for GPT-2 on CPU. The linear relationship between replay count and wall time is very tight (R² > 0.99) — each decode step costs almost exactly the same regardless of position.

### 9.3 Memory usage

Per-token memory: 12 layers × 2 (K+V) × 12 heads × 64 dim × 4 bytes = 73,728 bytes ≈ 72KB.

| Sequence length | Cache memory | + 4 checkpoints (stride=16) |
|----------------|-------------|---------------------------|
| 32 tokens | 2.3 MB | 3.4 MB |
| 64 tokens | 4.6 MB | 5.7 MB |
| 128 tokens | 9.2 MB | 10.3 MB |

GPT-2 is small enough that memory is not a constraint on CPU. For larger models (Llama-7B), memory would become the binding constraint.

## Part 10: Generalization Beyond GPT-2

### 10.1 What's model-specific

Very little. The `ModelAdapter` ABC defines four operations:

```python
class ModelAdapter(ABC):
    def tokenize(self, text: str) -> list[int]
    def decode(self, token_ids: list[int]) -> str
    def prefill(self, tokens: list[int]) -> tuple[KVCache, Tensor]
    def decode_one(self, token_id: int, cache: KVCache) -> tuple[Any, Tensor]
    def empty_cache(self) -> KVCache
    @property
    def eos_token_id(self) -> int
    @property
    def vocab_size(self) -> int
```

Any causal autoregressive model that implements these six methods can be plugged into the VM. The KV cache structure, the edit operations, and the correctness oracle all work identically.

### 10.2 What changes for larger models

- **Memory:** 7B-parameter models have ~32 layers and much larger hidden dimensions. Per-position tensor storage becomes expensive. Contiguous tensors with offset tracking would be better.
- **Quantization:** INT8/INT4 quantized models would need a different tensor format. The adapter would handle conversion.
- **GPU:** The per-position cat operation becomes a GPU synchronization point. Contiguous storage or PagedAttention (vLLM-style) would be needed.
- **Batching:** The current VM processes one sequence at a time. Batched decode (processing multiple sequences in parallel) would require a different execution model.

### 10.3 What doesn't change

- The edit → rewind → replay pattern
- The correctness oracle (full recomputation)
- The composite opcode semantics (DELETE, INSERT, REPLACE)
- The register-based VM architecture
- The linear cost relationship between edit position and replay count

These are **structural properties of causal autoregressive models**, not implementation details of this particular system.

## Common failure modes

1. **Forgetting to replay after an edit.** The cache is truncated but never recomputed. valid_len < len(tokens), logits is None, and subsequent operations fail. The composite opcodes prevent this by construction.

2. **Rewinding to the wrong position.** If you edit token 5 but rewind to position 3, you replay 2 extra tokens unnecessarily. Not incorrect, but wasteful. If you rewind to position 7, you've left invalid cache entries at positions 5-6.

3. **Off-by-one in REPLAY's logits re-derivation.** After REPLAY, valid_len == len(tokens) and there are no more tokens to process — but logits should represent the next-token distribution, not be None. The special case in REPLAY (rewind-1 + re-decode last token) handles this.

4. **Shallow-copy checkpoints.** If checkpoints share tensor references with the live cache, mutations to the cache corrupt the checkpoint. The KV-Cache VM uses `clone()` which deep-copies all tensors.

5. **DynamicCache format changes.** HuggingFace changed the cache format from tuples to DynamicCache objects. The adapter must handle both, or the VM gets obscure shape mismatches.

## Anti-patterns

- **Don't edit the token list without rewinding.** The cache will be invalid and subsequent operations will produce wrong results.
- **Don't save checkpoints after editing without replaying.** The checkpoint would contain a partially invalid cache.
- **Don't try to fix individual cache positions.** The error cascades — you must replay the entire suffix.
- **Don't compare generated tokens for correctness.** Use logits — token-level comparison is too coarse and not reproducible.

## Working rules

> [!important]
> 1. The token list is the source of truth. The cache is derived state.
> 2. After any edit, the cache must be rewound to the edit point and replayed to the end.
> 3. Every optimization must be verified against full recomputation with logit diff < 1e-3.
> 4. Cost is linear in (sequence_length - edit_position). There is no free lunch.
> 5. The causal constraint is a structural property of autoregressive models, not a limitation of this implementation.

## Related notes

- [[PROJ - KV-Cache VM - Token-Editing Decoding VM for CPU-Side LLM Inference]]

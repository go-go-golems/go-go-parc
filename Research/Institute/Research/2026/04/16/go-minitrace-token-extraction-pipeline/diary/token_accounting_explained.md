# Token Accounting Explained

## What Each Token Type Means

### 1. Input Tokens
- **What:** New tokens you send TO the API
- **Includes:** Your prompt, instructions, context, tool results
- **Example:** "Analyze this code: [code here]"
- **Billed:** YES (full rate)

### 2. Output Tokens  
- **What:** Tokens the AI generates and sends BACK
- **Includes:** The AI's response, thinking, code output
- **Example:** "Here's the analysis of your code..."
- **Billed:** YES (often higher rate than input)

### 3. Cache Read Tokens
- **What:** Tokens read FROM the conversation cache
- **Includes:** Previous turns, context that's already been processed
- **Why it exists:** Avoids re-processing the same context repeatedly
- **Billed:** DISCOUNTED or FREE (depends on provider)
  - Some providers: 50-90% discount
  - Some providers: completely free

### 4. Cache Write Tokens (usually 0)
- **What:** Tokens written TO the cache for future use
- **Billed:** Usually free

---

## What is "Billing"?

**Billing = Input Tokens + Output Tokens**

This is what you actually pay for. Cache tokens are typically not billed at full rates.

Example from Pi JSONL:
```json
{
  "usage": {
    "input": 410,           // You pay for this
    "output": 250,          // You pay for this (usually more expensive)
    "cacheRead": 7680,      // Discounted or free
    "cacheWrite": 0,        // Usually free
    "totalTokens": 8340     // Just a sum, not what you pay
  }
}
```

**Billing calculation:**
- Cost = (410 × input_price) + (250 × output_price)
- cacheRead (7680) = heavily discounted or free
- Don't use totalTokens for cost estimation!

---

## GLM-5.1 Example (April 15-16)

| Token Type | Count | Billed? | Typical Rate |
|------------|-------|---------|--------------|
| Input | 587,724 | YES | ~$0.50-2.00 per 1M |
| Output | 86,856 | YES | ~$1.00-5.00 per 1M |
| **Billing Total** | **674,580** | **= Cost** | **~$0.50-2.00 total** |
| Cache Read | 35,757,824 | NO/Discount | ~$0.00-0.10 per 1M |

### Why Cache is So High (35M tokens!)

The huge cache number means:
1. Long conversations with lots of context
2. Pi reuses cached context across multiple API calls
3. Each new turn only sends "input" (new stuff), but the model "sees" all cached context too
4. Cache hits = faster + cheaper than re-sending full context every time

### Real Cost Estimate (rough)

Assuming glm-5.1 pricing similar to other models:
- Input: 587,724 × $0.001/1K = ~$0.59
- Output: 86,856 × $0.003/1K = ~$0.26
- **Estimated total: ~$0.85** (not $35+!)

Cache tokens don't significantly add to cost.

---

## Summary

| Term | Meaning | Use For |
|------|---------|---------|
| **Input** | New tokens sent | Cost estimation |
| **Output** | Generated response | Cost estimation |
| **Cache Read** | Reused context | Understanding efficiency |
| **Billing** | Input + Output | **Actual cost** |
| **Total** | I + O + Cache | Not useful for billing |

**For cost analysis, use: Billing = 674,580 tokens**

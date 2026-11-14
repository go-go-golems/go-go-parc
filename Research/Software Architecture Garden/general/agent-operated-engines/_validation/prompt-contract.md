=== OUTPUT CONTRACT ===
Your FINAL message must be exactly one JSON object in a ```json fenced block, with these keys (example values shown):

```json
{
  "restatement": {
    "intent": "one or two sentences in your own words",
    "problem": "one sentence",
    "solution": "two to four sentences: the shape a reader must remember"
  },
  "quiz": [ { "id": "Q1", "answer": "short answer", "where": "the chapter section that supports it" } ],
  "transfer": [
    { "id": "T1", "fits": true, "why": "one or two sentences",
      "participants": { "<chapter participant>": "what plays that role in this situation" },
      "sketch": "short pseudocode of the pattern in this situation (empty if it does not fit)",
      "key_notes": ["the implementation notes (by number or lead) that matter most here, and why"],
      "risk": "the most likely way to get it wrong here" }
  ],
  "review_notes": [
    { "section": "chapter section", "kind": "unclear | wrong | missing | too-specific | too-long | other",
      "severity": "high | medium | low", "note": "what is the problem", "suggestion": "what would fix it" }
  ],
  "ratings": { "clarity": 1, "reusability": 1, "would_apply_it": 1,
               "comment": "ratings 1 to 5; one sentence on what drove them" }
}
```
Answer every quiz question and every transfer task listed above, in order, using their ids. Give at least five
review notes.

package judgekernel

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
)

// PopulationKey identifies one judged population: a step of one judge
// protocol version running on one model. Any change to any field is a new
// population — bumping PromptVersion invalidates every cached judgment at
// once, which is the frozen-instrument discipline both source repositories
// enforce (CoinVault judgePromptVersion; rag-ttc versioned Kind constants).
type PopulationKey struct {
	Step          string `json:"step"`
	PromptVersion string `json:"prompt_version"`
	Model         string `json:"model"`
}

// CacheKey derives the content-addressed cache key for one prompt within
// this population. The encoding is canonical JSON of the key fields plus the
// prompt, hashed; two keys are equal only if every field and the prompt are
// byte-equal.
func (k PopulationKey) CacheKey(prompt string) string {
	payload, err := json.Marshal(struct {
		PopulationKey
		Prompt string `json:"prompt"`
	}{PopulationKey: k, Prompt: prompt})
	if err != nil {
		// The struct contains only strings; Marshal cannot fail. Guard anyway.
		panic(err)
	}
	sum := sha256.Sum256(payload)
	return hex.EncodeToString(sum[:])
}

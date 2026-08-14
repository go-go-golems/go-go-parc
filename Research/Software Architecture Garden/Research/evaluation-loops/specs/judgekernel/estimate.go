package judgekernel

// Fraction is an explicit-denominator ratio. It exists so that faithfulness
// can never be laundered through an implicit division: a 0/0 fraction has no
// float value, and both source implementations' "vacuously 1.0" convention
// becomes an aggregation-time choice rather than a stored measurement.
type Fraction struct {
	Numerator   int
	Denominator int
}

// Value returns the ratio and whether it is defined (denominator nonzero).
func (f Fraction) Value() (float64, bool) {
	if f.Denominator == 0 {
		return 0, false
	}
	return float64(f.Numerator) / float64(f.Denominator), true
}

// CellStatus is the closed status vocabulary for one scored cell, adopted
// from rag-ttc's JudgeStatus but reduced to what the kernel itself decides.
type CellStatus string

const (
	// StatusJudged: at least one statement, every statement received an
	// admitted verdict.
	StatusJudged CellStatus = "judged"
	// StatusVacuousAbstention: zero statements were extracted; faithfulness
	// is 0/0 by construction and must not enter faithfulness means.
	StatusVacuousAbstention CellStatus = "vacuous_abstention"
)

// Score is the computed outcome for one cell. Every number in it is derived
// from admitted values by arithmetic the caller can re-run; nothing here was
// asked of a model.
type Score struct {
	Status       CellStatus
	Faithfulness Fraction
	Relevance    float64
	Abstained    bool
	Verdicts     []Verdict
}

// ScoreCell computes the cell score from admitted verdicts. Faithfulness is
// supported-over-total — computed, never asked for.
func ScoreCell(admitted Admitted) Score {
	verdicts := admitted.Verdicts()
	supported := 0
	for _, verdict := range verdicts {
		if verdict.Supported {
			supported++
		}
	}
	status := StatusJudged
	if len(verdicts) == 0 {
		status = StatusVacuousAbstention
	}
	return Score{
		Status:       status,
		Faithfulness: Fraction{Numerator: supported, Denominator: len(verdicts)},
		Relevance:    admitted.Relevance(),
		Abstained:    admitted.Abstained(),
		Verdicts:     verdicts,
	}
}

// MeanReport is a mean with its denominator attached. A zero denominator
// yields Defined=false rather than zero, so an empty population cannot be
// mistaken for a population that scored zero.
type MeanReport struct {
	Mean        float64
	Denominator int
	Defined     bool
}

// Summary aggregates cell scores with the denominator discipline both
// source implementations converged on: abstained and vacuous cells are
// excluded from the faithfulness mean (an arm cannot buy faithfulness by
// abstaining), relevance averages over every judged cell, and every mean
// carries its denominator.
type Summary struct {
	Cells              int
	Judged             int
	VacuousAbstentions int
	JudgeAbstentions   int
	Faithfulness       MeanReport
	Relevance          MeanReport
}

// Summarize aggregates scores.
func Summarize(scores []Score) Summary {
	summary := Summary{Cells: len(scores)}
	var faithSum, relevanceSum float64
	var faithN, relevanceN int
	for _, score := range scores {
		if score.Status == StatusVacuousAbstention {
			summary.VacuousAbstentions++
		} else {
			summary.Judged++
		}
		if score.Abstained {
			summary.JudgeAbstentions++
		}
		relevanceSum += score.Relevance
		relevanceN++
		if score.Abstained || score.Status == StatusVacuousAbstention {
			continue
		}
		if value, defined := score.Faithfulness.Value(); defined {
			faithSum += value
			faithN++
		}
	}
	if faithN > 0 {
		summary.Faithfulness = MeanReport{Mean: faithSum / float64(faithN), Denominator: faithN, Defined: true}
	}
	if relevanceN > 0 {
		summary.Relevance = MeanReport{Mean: relevanceSum / float64(relevanceN), Denominator: relevanceN, Defined: true}
	}
	return summary
}

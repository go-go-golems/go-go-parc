package runcustody

import "fmt"

// Plan returns the coordinates a resumed writer must execute: exactly the
// scheduled coordinates absent from the committed set, in schedule order.
// It rejects committed keys outside the schedule so a journal from a
// different identity cannot silently shrink the plan.
func Plan(schedule []Coord, completed map[string]Record) ([]Coord, error) {
	expected := make(map[string]struct{}, len(schedule))
	for _, coord := range schedule {
		expected[coord.Key()] = struct{}{}
	}
	for key := range completed {
		if _, exists := expected[key]; !exists {
			return nil, fmt.Errorf("completed coordinate %q is not in the schedule", key)
		}
	}
	var plan []Coord
	for _, coord := range schedule {
		if _, exists := completed[coord.Key()]; exists {
			continue
		}
		plan = append(plan, coord)
	}
	return plan, nil
}

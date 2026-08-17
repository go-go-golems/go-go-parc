#!/usr/bin/env python3
"""A minimal, dependency-free reflective program-evolution harness.

The proposer is deterministic Python rather than an LLM so the example is
reproducible. Replace SemanticProposer with an adapter that returns the same
JSON policy language to connect an LLM while keeping build_candidate as the
trusted boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class Example:
    name_similarity: float
    address_match: bool
    distance_m: float | None
    label: bool


@dataclass(frozen=True)
class Policy:
    sure_match: float
    sure_miss: float
    address_rescue: float
    near_m: float
    far_m: float


@dataclass(frozen=True)
class TraceEvent:
    kind: str
    detail: str


@dataclass(frozen=True)
class RunResult:
    prediction: bool
    model_calls: int
    events: tuple[TraceEvent, ...]


@dataclass(frozen=True)
class Score:
    accuracy: float
    negative_call_rate: float
    negative_complexity: float


@dataclass(frozen=True)
class Candidate:
    source: str
    policy: Policy
    digest: str


@dataclass(frozen=True)
class Evaluation:
    score: Score
    failures: tuple[tuple[Example, RunResult], ...]


EXPECTED_POLICY_FIELDS = {
    "sure_match",
    "sure_miss",
    "address_rescue",
    "near_m",
    "far_m",
}


def build_candidate(source: str) -> Candidate:
    """Parse and validate the policy DSL.

    This function is the trusted build boundary. Proposer output is untrusted
    until this function returns a Candidate.
    """
    try:
        raw = json.loads(source)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError("policy must be a JSON object")
    if set(raw) != EXPECTED_POLICY_FIELDS:
        raise ValueError(f"expected fields {sorted(EXPECTED_POLICY_FIELDS)}")

    try:
        policy = Policy(**{key: float(value) for key, value in raw.items()})
    except (TypeError, ValueError) as exc:
        raise ValueError("every policy field must be numeric") from exc

    unit_fields = (
        policy.sure_match,
        policy.sure_miss,
        policy.address_rescue,
    )
    all_fields = (*unit_fields, policy.near_m, policy.far_m)
    if not all(math.isfinite(value) for value in all_fields):
        raise ValueError("all policy values must be finite")
    if not all(0.0 <= value <= 1.0 for value in unit_fields):
        raise ValueError("similarity thresholds must be in [0, 1]")
    if not policy.sure_miss < policy.address_rescue <= policy.sure_match:
        raise ValueError("threshold ordering is invalid")
    if not 0.0 <= policy.near_m < policy.far_m:
        raise ValueError("distance bounds are invalid")

    canonical = json.dumps(asdict(policy), sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return Candidate(source=canonical, policy=policy, digest=digest)


def run(policy: Policy, example: Example) -> RunResult:
    """Execute one typed routing policy and emit structured trace evidence."""
    events: list[TraceEvent] = []
    similarity = example.name_similarity

    if similarity >= policy.sure_match:
        if example.address_match and (
            example.distance_m is None or example.distance_m <= policy.near_m
        ):
            events.append(TraceEvent("route", "deterministic same"))
            return RunResult(True, 0, tuple(events))
        if example.distance_m is not None and example.distance_m >= policy.far_m:
            events.append(TraceEvent("route", "deterministic different: far"))
            return RunResult(False, 0, tuple(events))

    if similarity <= policy.sure_miss:
        events.append(TraceEvent("route", "deterministic different: low similarity"))
        return RunResult(False, 0, tuple(events))

    if example.address_match and similarity >= policy.address_rescue:
        events.append(TraceEvent("route", "deterministic same: address rescue"))
        return RunResult(True, 0, tuple(events))

    # Deterministic stand-in for an LM effect. A real adapter should log the
    # model/version, input, output, token/call cost, and retry behavior.
    events.append(TraceEvent("route", "fallback model"))
    model_prediction = similarity >= 0.66 and (
        example.address_match
        or example.distance_m is None
        or example.distance_m < 250.0
    )
    return RunResult(model_prediction, 1, tuple(events))


def evaluate(candidate: Candidate, data: Sequence[Example]) -> Evaluation:
    """Return soft objectives and failure traces; this is not a proof."""
    correct = 0
    calls = 0
    failures: list[tuple[Example, RunResult]] = []

    for example in data:
        result = run(candidate.policy, example)
        calls += result.model_calls
        if result.prediction == example.label:
            correct += 1
        else:
            failures.append((example, result))

    count = max(1, len(data))
    score = Score(
        accuracy=correct / count,
        negative_call_rate=-(calls / count),
        negative_complexity=-float(len(candidate.source)),
    )
    return Evaluation(score=score, failures=tuple(failures))


def dominates(left: Score, right: Score) -> bool:
    """Strict Pareto dominance with all objectives oriented upward."""
    left_vector = (
        left.accuracy,
        left.negative_call_rate,
        left.negative_complexity,
    )
    right_vector = (
        right.accuracy,
        right.negative_call_rate,
        right.negative_complexity,
    )
    return all(a >= b for a, b in zip(left_vector, right_vector)) and any(
        a > b for a, b in zip(left_vector, right_vector)
    )


def pareto_insert(
    archive: list[tuple[Candidate, Evaluation]],
    item: tuple[Candidate, Evaluation],
) -> list[tuple[Candidate, Evaluation]]:
    """Return a de-duplicated Pareto antichain containing item when admissible."""
    candidate, evaluation = item
    if any(dominates(old_eval.score, evaluation.score) for _, old_eval in archive):
        return archive

    kept = [
        old
        for old in archive
        if not dominates(evaluation.score, old[1].score)
    ]
    if all(old_candidate.digest != candidate.digest for old_candidate, _ in kept):
        kept.append(item)
    return kept


class Proposer(Protocol):
    def propose(
        self,
        parent: Candidate,
        evidence: Evaluation,
        rng: random.Random,
    ) -> str:
        """Return untrusted source in the policy DSL."""
        ...


class SemanticProposer:
    """A trace-conditioned semantic mutation operator.

    An LLM replacement can read richer traces and textual feedback, but should
    still return source accepted by build_candidate rather than bypassing it.
    """

    def propose(
        self,
        parent: Candidate,
        evidence: Evaluation,
        rng: random.Random,
    ) -> str:
        policy = dict(asdict(parent.policy))

        false_positives = [
            example
            for example, result in evidence.failures
            if result.prediction and not example.label
        ]
        false_negatives = [
            example
            for example, result in evidence.failures
            if not result.prediction and example.label
        ]

        mode = rng.random()
        if mode < 0.30:
            # Cost/coverage pressure: make more cases deterministic. This can
            # reduce fallback calls while sacrificing accuracy, creating a
            # genuine Pareto tradeoff rather than a single scalar winner.
            move = rng.choice(("low", "middle", "high", "distance"))
            if move == "low":
                policy["sure_miss"] += 0.03
            elif move == "middle":
                policy["address_rescue"] -= 0.03
            elif move == "high":
                policy["sure_match"] -= 0.03
            else:
                policy["near_m"] += 35.0
                policy["far_m"] -= 35.0
        elif false_positives and (not false_negatives or rng.random() < 0.6):
            policy["sure_match"] += 0.02
            policy["address_rescue"] += 0.02
            policy["far_m"] -= 20.0
        elif false_negatives:
            policy["sure_match"] -= 0.02
            policy["sure_miss"] -= 0.02
            policy["near_m"] += 20.0
        else:
            policy["sure_miss"] += 0.01
            policy["address_rescue"] -= 0.01

        # Occasionally explore one semantically isolated dimension. This is
        # still structure-aware mutation, not arbitrary source-token damage.
        if rng.random() < 0.25:
            dimension = rng.choice(("sure_match", "sure_miss", "near_m", "far_m"))
            if dimension in {"sure_match", "sure_miss"}:
                policy[dimension] += rng.choice((-0.01, 0.01))
            else:
                policy[dimension] += rng.choice((-10.0, 10.0))

        # Keep this deterministic proposer mostly productive. The authoritative
        # builder still checks these conditions and would reject a bad LLM edit.
        policy["sure_miss"] = min(0.94, max(0.01, policy["sure_miss"]))
        policy["address_rescue"] = min(
            0.97, max(policy["sure_miss"] + 0.01, policy["address_rescue"])
        )
        policy["sure_match"] = min(
            0.99, max(policy["address_rescue"], policy["sure_match"])
        )
        policy["near_m"] = max(0.0, policy["near_m"])
        policy["far_m"] = max(policy["near_m"] + 1.0, policy["far_m"])
        for field in ("sure_match", "sure_miss", "address_rescue"):
            policy[field] = round(policy[field], 4)
        for field in ("near_m", "far_m"):
            policy[field] = round(policy[field], 1)

        return json.dumps(policy)


def optimize(
    seed_source: str,
    train: Sequence[Example],
    *,
    steps: int = 100,
    random_seed: int = 0,
    proposer: Proposer | None = None,
) -> tuple[list[tuple[Candidate, Evaluation]], int]:
    """Evolve a Pareto archive and return it with the rejection count."""
    if steps < 0:
        raise ValueError("steps must be non-negative")

    rng = random.Random(random_seed)
    active_proposer = proposer or SemanticProposer()

    seed = build_candidate(seed_source)
    archive = [(seed, evaluate(seed, train))]
    rejected = 0

    for _ in range(steps):
        parent, parent_evaluation = rng.choice(archive)
        proposal_source = active_proposer.propose(parent, parent_evaluation, rng)
        try:
            child = build_candidate(proposal_source)
        except (ValueError, TypeError):
            rejected += 1
            continue
        child_evaluation = evaluate(child, train)
        archive = pareto_insert(archive, (child, child_evaluation))

    ordered = sorted(
        archive,
        key=lambda item: (
            -item[1].score.accuracy,
            -item[1].score.negative_call_rate,
            item[0].digest,
        ),
    )
    return ordered, rejected


def generate_dataset(size: int, random_seed: int) -> list[Example]:
    """Generate a reproducible entity-resolution-like data set."""
    if size < 1:
        raise ValueError("dataset size must be positive")

    rng = random.Random(random_seed)
    data: list[Example] = []

    for _ in range(size):
        label = rng.random() < 0.5
        branch = rng.random()

        if label and branch < 0.70:
            similarity = min(1.0, max(0.0, rng.gauss(0.86, 0.08)))
            address_match = rng.random() < 0.90
            distance: float | None = max(0.0, rng.gauss(70.0, 55.0))
        elif label:
            # Difficult positive: spelling drift or partial address evidence.
            similarity = min(1.0, max(0.0, rng.gauss(0.67, 0.10)))
            address_match = rng.random() < 0.60
            distance = None if rng.random() < 0.25 else max(0.0, rng.gauss(150.0, 90.0))
        elif branch < 0.65:
            similarity = min(1.0, max(0.0, rng.gauss(0.35, 0.14)))
            address_match = rng.random() < 0.08
            distance = max(0.0, rng.gauss(750.0, 280.0))
        else:
            # Difficult negative: same brand or similar name at another branch.
            similarity = min(1.0, max(0.0, rng.gauss(0.79, 0.09)))
            address_match = rng.random() < 0.20
            distance = max(0.0, rng.gauss(520.0, 230.0))

        # A small amount of label noise makes empirical evaluation visibly
        # different from theorem proving.
        if rng.random() < 0.02:
            label = not label

        data.append(
            Example(
                name_similarity=round(similarity, 4),
                address_match=address_match,
                distance_m=None if distance is None else round(distance, 1),
                label=label,
            )
        )

    return data


def assert_archive_is_antichain(
    archive: Sequence[tuple[Candidate, Evaluation]],
) -> None:
    for index, (_, left) in enumerate(archive):
        for _, right in archive[index + 1 :]:
            assert not dominates(left.score, right.score)
            assert not dominates(right.score, left.score)


def run_self_tests() -> None:
    valid = json.dumps(
        {
            "sure_match": 0.88,
            "sure_miss": 0.45,
            "address_rescue": 0.70,
            "near_m": 140.0,
            "far_m": 420.0,
        }
    )
    candidate = build_candidate(valid)
    assert candidate.policy.sure_miss < candidate.policy.address_rescue
    assert candidate.policy.address_rescue <= candidate.policy.sure_match

    invalid_cases = (
        "not-json",
        "[]",
        json.dumps({"sure_match": 0.8}),
        json.dumps(
            {
                "sure_match": 0.60,
                "sure_miss": 0.50,
                "address_rescue": 0.70,
                "near_m": 100.0,
                "far_m": 200.0,
            }
        ),
    )
    for source in invalid_cases:
        try:
            build_candidate(source)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid candidate was accepted: {source}")

    archive, _ = optimize(valid, generate_dataset(80, 9), steps=40, random_seed=9)
    assert_archive_is_antichain(archive)


def _score_record(
    candidate: Candidate,
    train_evaluation: Evaluation,
    test_evaluation: Evaluation,
) -> dict[str, object]:
    return {
        "digest": candidate.digest[:12],
        "train_accuracy": round(train_evaluation.score.accuracy, 4),
        "train_call_rate": round(-train_evaluation.score.negative_call_rate, 4),
        "test_accuracy": round(test_evaluation.score.accuracy, 4),
        "test_call_rate": round(-test_evaluation.score.negative_call_rate, 4),
        "policy": asdict(candidate.policy),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=250)
    parser.add_argument("--train-size", type=int, default=500)
    parser.add_argument("--test-size", type=int, default=500)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()

    if not args.skip_tests:
        run_self_tests()

    seed_source = json.dumps(
        {
            "sure_match": 0.88,
            "sure_miss": 0.45,
            "address_rescue": 0.70,
            "near_m": 140.0,
            "far_m": 420.0,
        }
    )
    train = generate_dataset(args.train_size, args.seed)
    test = generate_dataset(args.test_size, args.seed + 1)
    archive, rejected = optimize(
        seed_source,
        train,
        steps=args.steps,
        random_seed=args.seed,
    )
    assert_archive_is_antichain(archive)

    rows = [
        _score_record(candidate, train_eval, evaluate(candidate, test))
        for candidate, train_eval in archive
    ]

    if args.json:
        print(json.dumps({"rejected": rejected, "archive": rows}, indent=2))
        return 0

    print(f"Pareto archive: {len(rows)} candidates; rejected proposals: {rejected}")
    print("digest       train_acc  train_calls  test_acc  test_calls  policy")
    for row in rows:
        policy = row["policy"]
        print(
            f"{row['digest']:<12} "
            f"{row['train_accuracy']:>9.3f} "
            f"{row['train_call_rate']:>12.3f} "
            f"{row['test_accuracy']:>9.3f} "
            f"{row['test_call_rate']:>11.3f}  "
            f"{json.dumps(policy, sort_keys=True)}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

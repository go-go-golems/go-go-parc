/**
 * A dependency-free reference kernel for the presentation-type calculus in
 * Semantic Interfaces.
 *
 * This code favors explicit semantics and inspectable evidence over maximum
 * performance. It is intended as a correctness oracle, teaching artifact, and
 * starting point—not as a finished UI framework.
 */

export type AtomId = string;
export type CapabilityId = string;
export type RefinementId = string;
export type TranslatorId = string;
export type MethodId = string;
export type GenericFunctionId = string;

export interface PresentationReference<T = unknown> {
  readonly type: AtomId;
  readonly value: T;
}

export interface SemanticIdentity {
  readonly namespace: string;
  readonly key: string | number;
}

export interface DependencyFingerprint {
  readonly definitionId: string;
  readonly parts: readonly (string | number | boolean | null)[];
}

export type TypeExpr<T = unknown> =
  | TopExpr
  | BottomExpr
  | AtomExpr<T>
  | CapabilityExpr<T>
  | UnionExpr<T>
  | IntersectionExpr<T>
  | DifferenceExpr<T>
  | RefinementExpr<T>;

export interface TopExpr {
  readonly kind: "top";
}

export interface BottomExpr {
  readonly kind: "bottom";
}

export interface AtomExpr<T = unknown> {
  readonly kind: "atom";
  readonly atom: AtomId;
  readonly __representation?: T;
}

export interface CapabilityExpr<T = unknown> {
  readonly kind: "capability";
  readonly capability: CapabilityId;
  readonly __representation?: T;
}

export interface UnionExpr<T = unknown> {
  readonly kind: "union";
  readonly members: readonly TypeExpr<T>[];
}

export interface IntersectionExpr<T = unknown> {
  readonly kind: "intersection";
  readonly members: readonly TypeExpr<T>[];
}

export interface DifferenceExpr<T = unknown> {
  readonly kind: "difference";
  readonly base: TypeExpr<T>;
  readonly excluded: TypeExpr;
}

export interface RefinementExpr<T = unknown, Args = unknown> {
  readonly kind: "refinement";
  readonly refinement: RefinementId;
  readonly base: TypeExpr<T>;
  readonly args: Args;
}

const TOP: TopExpr = Object.freeze({ kind: "top" });
const BOTTOM: BottomExpr = Object.freeze({ kind: "bottom" });

export function top(): TopExpr {
  return TOP;
}

export function bottom(): BottomExpr {
  return BOTTOM;
}

export function atom<T = unknown>(id: AtomId): AtomExpr<T> {
  requireNonEmpty("atom id", id);
  return Object.freeze({ kind: "atom", atom: id });
}

export function capability<T = unknown>(id: CapabilityId): CapabilityExpr<T> {
  requireNonEmpty("capability id", id);
  return Object.freeze({ kind: "capability", capability: id });
}

/** Build a normalized union. */
export function or<T>(...inputs: readonly TypeExpr<T>[]): TypeExpr<T> {
  const members: TypeExpr<T>[] = [];
  for (const input of inputs) {
    if (input.kind === "top") return top() as TypeExpr<T>;
    if (input.kind === "bottom") continue;
    if (input.kind === "union") members.push(...input.members);
    else members.push(input);
  }
  const unique = deduplicateExpressions(members);
  if (unique.length === 0) return bottom() as TypeExpr<T>;
  if (unique.length === 1) return unique[0]!;
  return Object.freeze({ kind: "union", members: Object.freeze(unique) });
}

/** Build a normalized intersection. */
export function and<T>(...inputs: readonly TypeExpr<T>[]): TypeExpr<T> {
  const members: TypeExpr<T>[] = [];
  for (const input of inputs) {
    if (input.kind === "bottom") return bottom() as TypeExpr<T>;
    if (input.kind === "top") continue;
    if (input.kind === "intersection") members.push(...input.members);
    else members.push(input);
  }
  const unique = deduplicateExpressions(members);
  if (unique.length === 0) return top() as TypeExpr<T>;
  if (unique.length === 1) return unique[0]!;
  return Object.freeze({ kind: "intersection", members: Object.freeze(unique) });
}

export function difference<T>(
  base: TypeExpr<T>,
  excluded: TypeExpr,
): TypeExpr<T> {
  if (base.kind === "bottom" || excluded.kind === "top") {
    return bottom() as TypeExpr<T>;
  }
  if (excluded.kind === "bottom") return base;
  if (expressionKey(base) === expressionKey(excluded)) {
    return bottom() as TypeExpr<T>;
  }
  return Object.freeze({ kind: "difference", base, excluded });
}

export function refine<T, Args>(
  base: TypeExpr<T>,
  refinement: RefinementId,
  args: Args,
): RefinementExpr<T, Args> {
  requireNonEmpty("refinement id", refinement);
  return Object.freeze({ kind: "refinement", refinement, base, args });
}

export function printType(expression: TypeExpr): string {
  switch (expression.kind) {
    case "top":
      return "⊤";
    case "bottom":
      return "⊥";
    case "atom":
      return expression.atom;
    case "capability":
      return `cap(${expression.capability})`;
    case "union":
      return `(${expression.members.map(printType).join(" ∨ ")})`;
    case "intersection":
      return `(${expression.members.map(printType).join(" ∧ ")})`;
    case "difference":
      return `(${printType(expression.base)} \\ ${printType(expression.excluded)})`;
    case "refinement":
      return `${expression.refinement}(${stableStringify(expression.args)}; ${printType(expression.base)})`;
  }
}

export interface AtomDescriptor<T, Environment> {
  readonly label?: (value: T, environment: Environment) => string;
  readonly identity?: (
    value: T,
    environment: Environment,
  ) => SemanticIdentity | undefined;
  readonly revision?: (
    value: T,
    environment: Environment,
  ) => string | number | undefined;
}

export interface DynamicCapabilityDefinition<T, Environment> {
  readonly id: string;
  readonly atom: AtomId;
  readonly capability: CapabilityId;
  readonly test: (value: T, environment: Environment) => boolean;
  readonly dependencies?: (
    value: T,
    environment: Environment,
  ) => DependencyFingerprint;
}

export interface RefinementDefinition<T, Args, Environment> {
  readonly id: RefinementId;
  readonly base: TypeExpr<T>;
  readonly test: (
    value: T,
    args: Args,
    environment: Environment,
  ) => boolean;
  readonly dependencies?: (
    value: T,
    args: Args,
    environment: Environment,
  ) => DependencyFingerprint;
}

export interface TranslatorDefinition<From, To, Environment> {
  readonly id: TranslatorId;
  readonly from: AtomId;
  readonly to: AtomId;
  readonly cost?: number;
  readonly priority?: number;
  readonly preservesIdentity?: boolean;
  readonly applicable?: (value: From, environment: Environment) => boolean;
  readonly translate: (
    value: From,
    environment: Environment,
  ) => To | undefined | Promise<To | undefined>;
}

export interface MethodDefinition<Result, Environment> {
  readonly id: MethodId;
  readonly generic: GenericFunctionId;
  readonly subject: TypeExpr;
  readonly context?: TypeExpr;
  readonly priority?: number;
  readonly invoke: (input: {
    readonly subject: Match;
    readonly context?: Match;
    readonly environment: Environment;
  }) => Result;
}

export type MembershipEvidence =
  | { readonly kind: "top" }
  | {
      readonly kind: "atom";
      readonly actual: AtomId;
      readonly requested: AtomId;
      readonly nominalPath: readonly AtomId[];
    }
  | {
      readonly kind: "capability";
      readonly capability: CapabilityId;
      readonly implementation: "static" | string;
      readonly declaredOn: AtomId;
    }
  | {
      readonly kind: "union";
      readonly branch: number;
      readonly evidence: MembershipEvidence;
    }
  | {
      readonly kind: "intersection";
      readonly members: readonly MembershipEvidence[];
    }
  | {
      readonly kind: "difference";
      readonly base: MembershipEvidence;
      readonly excluded: TypeExpr;
      readonly excludedDependencies: readonly DependencyFingerprint[];
    }
  | {
      readonly kind: "refinement";
      readonly refinement: RefinementId;
      readonly base: MembershipEvidence;
      readonly dependency?: DependencyFingerprint;
    };

export interface TranslationEvidence {
  readonly translator: TranslatorId;
  readonly from: AtomId;
  readonly to: AtomId;
  readonly cost: number;
  readonly preservesIdentity: boolean;
}

export interface ValidityToken {
  readonly registryVersion: number;
  readonly environmentEpoch: string | number;
  readonly sourceIdentity?: SemanticIdentity;
  readonly sourceRevision?: string | number;
  readonly dependencies: readonly DependencyFingerprint[];
}

export interface Match<T = unknown> {
  readonly source: PresentationReference;
  readonly accepted: PresentationReference<T>;
  readonly requestedType: TypeExpr<T>;
  readonly membership: MembershipEvidence;
  readonly translationPath: readonly TranslationEvidence[];
  readonly validity: ValidityToken;
}

export interface MatchFailure {
  readonly reason:
    | "unknown-atom"
    | "not-a-member"
    | "unknown-definition"
    | "malformed-refinement"
    | "translation-budget"
    | "ambiguous-translation";
  readonly message: string;
  readonly expression: TypeExpr;
  readonly reference: PresentationReference;
  readonly causes?: readonly MatchFailure[];
  readonly dependencies?: readonly DependencyFingerprint[];
}

export type MatchResult<T = unknown> =
  | { readonly ok: true; readonly match: Match<T> }
  | { readonly ok: false; readonly failure: MatchFailure };

export interface MatchOptions {
  readonly translations?: "none" | "direct" | "paths";
  readonly maxTranslationDepth?: number;
  readonly maxTranslationStates?: number;
}

export type TypeComparison = "less" | "equal" | "greater" | "incomparable";

interface RegisteredDynamicCapability<Environment> {
  readonly id: string;
  readonly atom: AtomId;
  readonly capability: CapabilityId;
  readonly test: (value: unknown, environment: Environment) => boolean;
  readonly dependencies?: (
    value: unknown,
    environment: Environment,
  ) => DependencyFingerprint;
}

interface RegisteredRefinement<Environment> {
  readonly id: RefinementId;
  readonly base: TypeExpr;
  readonly test: (
    value: unknown,
    args: unknown,
    environment: Environment,
  ) => boolean;
  readonly dependencies?: (
    value: unknown,
    args: unknown,
    environment: Environment,
  ) => DependencyFingerprint;
}

interface RegisteredTranslator<Environment> {
  readonly id: TranslatorId;
  readonly from: AtomId;
  readonly to: AtomId;
  readonly cost: number;
  readonly priority: number;
  readonly preservesIdentity: boolean;
  readonly applicable?: (value: unknown, environment: Environment) => boolean;
  readonly translate: (
    value: unknown,
    environment: Environment,
  ) => unknown | undefined | Promise<unknown | undefined>;
}

interface RegisteredMethod<Result, Environment> {
  readonly id: MethodId;
  readonly generic: GenericFunctionId;
  readonly subject: TypeExpr;
  readonly context?: TypeExpr;
  readonly priority: number;
  readonly invoke: MethodDefinition<Result, Environment>["invoke"];
}

export interface RegistryOptions<Environment> {
  readonly environmentEpoch?: (environment: Environment) => string | number;
}

let nextRegistryVersion = 1;

/**
 * Mutable declaration phase. Call freeze() before runtime matching.
 */
export class RegistryBuilder<Environment = unknown> {
  readonly #atoms = new Map<AtomId, AtomDescriptor<unknown, Environment>>();
  readonly #subtypeEdges = new Map<AtomId, Set<AtomId>>();
  readonly #capabilities = new Set<CapabilityId>();
  readonly #staticCapabilities = new Map<AtomId, Set<CapabilityId>>();
  readonly #dynamicCapabilities: RegisteredDynamicCapability<Environment>[] = [];
  readonly #refinements = new Map<RefinementId, RegisteredRefinement<Environment>>();
  readonly #translators: RegisteredTranslator<Environment>[] = [];
  readonly #methods: RegisteredMethod<unknown, Environment>[] = [];
  readonly #environmentEpoch: (environment: Environment) => string | number;

  constructor(options: RegistryOptions<Environment> = {}) {
    this.#environmentEpoch = options.environmentEpoch ?? (() => 0);
  }

  addAtom<T>(
    id: AtomId,
    descriptor: AtomDescriptor<T, Environment> = {},
  ): AtomExpr<T> {
    requireNonEmpty("atom id", id);
    if (this.#atoms.has(id)) throw new Error(`Duplicate atom: ${id}`);
    this.#atoms.set(id, descriptor as AtomDescriptor<unknown, Environment>);
    this.#subtypeEdges.set(id, new Set());
    return atom<T>(id);
  }

  declareSubtype<Sub extends Super, Super>(
    sub: AtomExpr<Sub>,
    sup: AtomExpr<Super>,
  ): this {
    this.#requireAtom(sub.atom);
    this.#requireAtom(sup.atom);
    this.#subtypeEdges.get(sub.atom)!.add(sup.atom);
    return this;
  }

  addCapability(id: CapabilityId): CapabilityExpr {
    requireNonEmpty("capability id", id);
    if (this.#capabilities.has(id)) {
      throw new Error(`Duplicate capability: ${id}`);
    }
    this.#capabilities.add(id);
    return capability(id);
  }

  implementStatic<T>(
    on: AtomExpr<T>,
    cap: CapabilityExpr,
  ): this {
    this.#requireAtom(on.atom);
    this.#requireCapability(cap.capability);
    let set = this.#staticCapabilities.get(on.atom);
    if (!set) {
      set = new Set();
      this.#staticCapabilities.set(on.atom, set);
    }
    set.add(cap.capability);
    return this;
  }

  implementDynamic<T>(
    definition: DynamicCapabilityDefinition<T, Environment>,
  ): this {
    requireNonEmpty("dynamic capability implementation id", definition.id);
    this.#requireAtom(definition.atom);
    this.#requireCapability(definition.capability);
    if (this.#dynamicCapabilities.some((item) => item.id === definition.id)) {
      throw new Error(`Duplicate dynamic capability implementation: ${definition.id}`);
    }
    this.#dynamicCapabilities.push(
      definition as RegisteredDynamicCapability<Environment>,
    );
    return this;
  }

  addRefinement<T, Args>(
    definition: RefinementDefinition<T, Args, Environment>,
  ): (args: Args) => RefinementExpr<T, Args> {
    requireNonEmpty("refinement id", definition.id);
    if (this.#refinements.has(definition.id)) {
      throw new Error(`Duplicate refinement: ${definition.id}`);
    }
    this.#refinements.set(
      definition.id,
      definition as RegisteredRefinement<Environment>,
    );
    return (args: Args) => refine(definition.base, definition.id, args);
  }

  addTranslator<From, To>(
    definition: TranslatorDefinition<From, To, Environment>,
  ): this {
    requireNonEmpty("translator id", definition.id);
    this.#requireAtom(definition.from);
    this.#requireAtom(definition.to);
    if (this.#translators.some((item) => item.id === definition.id)) {
      throw new Error(`Duplicate translator: ${definition.id}`);
    }
    const cost = definition.cost ?? 1;
    if (!Number.isFinite(cost) || cost < 0) {
      throw new Error(`Translator ${definition.id} has invalid cost ${cost}`);
    }
    this.#translators.push({
      ...definition,
      cost,
      priority: definition.priority ?? 0,
      preservesIdentity: definition.preservesIdentity ?? false,
    } as RegisteredTranslator<Environment>);
    return this;
  }

  addMethod<Result>(definition: MethodDefinition<Result, Environment>): this {
    requireNonEmpty("method id", definition.id);
    if (this.#methods.some((method) => method.id === definition.id)) {
      throw new Error(`Duplicate method: ${definition.id}`);
    }
    this.#methods.push({
      ...definition,
      priority: definition.priority ?? 0,
    } as RegisteredMethod<unknown, Environment>);
    return this;
  }

  freeze(): RegistrySnapshot<Environment> {
    if (this.#atoms.size === 0) throw new Error("A registry needs at least one atom");
    validateAcyclic(this.#subtypeEdges);

    const ancestors = computeAncestorClosure(this.#subtypeEdges);
    const staticCapabilities = new Map<AtomId, ReadonlySet<CapabilityId>>();
    for (const id of this.#atoms.keys()) {
      const inherited = new Set<CapabilityId>();
      for (const ancestor of ancestors.get(id)!) {
        for (const cap of this.#staticCapabilities.get(ancestor) ?? []) {
          inherited.add(cap);
        }
      }
      staticCapabilities.set(id, inherited);
    }

    for (const refinement of this.#refinements.values()) {
      validateExpressionNames(
        refinement.base,
        this.#atoms,
        this.#capabilities,
        this.#refinements,
        true,
      );
    }
    for (const method of this.#methods) {
      validateExpressionNames(
        method.subject,
        this.#atoms,
        this.#capabilities,
        this.#refinements,
      );
      if (method.context) {
        validateExpressionNames(
          method.context,
          this.#atoms,
          this.#capabilities,
          this.#refinements,
        );
      }
    }

    const version = nextRegistryVersion++;
    const hash = hashText(
      stableStringify({
        atoms: [...this.#atoms.keys()].sort(),
        edges: [...this.#subtypeEdges.entries()]
          .map(([sub, supers]) => [sub, [...supers].sort()] as const)
          .sort(([a], [b]) => a.localeCompare(b)),
        capabilities: [...this.#capabilities].sort(),
        staticCapabilities: [...this.#staticCapabilities.entries()]
          .map(([id, caps]) => [id, [...caps].sort()] as const)
          .sort(([a], [b]) => a.localeCompare(b)),
        dynamicCapabilities: this.#dynamicCapabilities.map((item) => item.id).sort(),
        refinements: [...this.#refinements.keys()].sort(),
        translators: this.#translators.map((item) => item.id).sort(),
        methods: this.#methods.map((item) => item.id).sort(),
      }),
    );

    return new RegistrySnapshot({
      version,
      hash,
      atoms: new Map(this.#atoms),
      ancestors,
      capabilities: new Set(this.#capabilities),
      staticCapabilities,
      dynamicCapabilities: Object.freeze([...this.#dynamicCapabilities]),
      refinements: new Map(this.#refinements),
      translators: Object.freeze([...this.#translators]),
      methods: Object.freeze([...this.#methods]),
      environmentEpoch: this.#environmentEpoch,
    });
  }

  #requireAtom(id: AtomId): void {
    if (!this.#atoms.has(id)) throw new Error(`Unknown atom: ${id}`);
  }

  #requireCapability(id: CapabilityId): void {
    if (!this.#capabilities.has(id)) throw new Error(`Unknown capability: ${id}`);
  }
}

interface SnapshotState<Environment> {
  readonly version: number;
  readonly hash: string;
  readonly atoms: ReadonlyMap<AtomId, AtomDescriptor<unknown, Environment>>;
  readonly ancestors: ReadonlyMap<AtomId, ReadonlySet<AtomId>>;
  readonly capabilities: ReadonlySet<CapabilityId>;
  readonly staticCapabilities: ReadonlyMap<AtomId, ReadonlySet<CapabilityId>>;
  readonly dynamicCapabilities: readonly RegisteredDynamicCapability<Environment>[];
  readonly refinements: ReadonlyMap<RefinementId, RegisteredRefinement<Environment>>;
  readonly translators: readonly RegisteredTranslator<Environment>[];
  readonly methods: readonly RegisteredMethod<unknown, Environment>[];
  readonly environmentEpoch: (environment: Environment) => string | number;
}

/** Immutable runtime view of the semantic declarations. */
export class RegistrySnapshot<Environment = unknown> {
  readonly version: number;
  readonly hash: string;

  readonly #atoms: SnapshotState<Environment>["atoms"];
  readonly #ancestors: SnapshotState<Environment>["ancestors"];
  readonly #capabilities: SnapshotState<Environment>["capabilities"];
  readonly #staticCapabilities: SnapshotState<Environment>["staticCapabilities"];
  readonly #dynamicCapabilities: SnapshotState<Environment>["dynamicCapabilities"];
  readonly #refinements: SnapshotState<Environment>["refinements"];
  readonly #translators: SnapshotState<Environment>["translators"];
  readonly #methods: SnapshotState<Environment>["methods"];
  readonly #environmentEpoch: SnapshotState<Environment>["environmentEpoch"];
  readonly #objectIdentity = new WeakMap<object, number>();
  #nextObjectIdentity = 1;

  constructor(state: SnapshotState<Environment>) {
    this.version = state.version;
    this.hash = state.hash;
    this.#atoms = state.atoms;
    this.#ancestors = state.ancestors;
    this.#capabilities = state.capabilities;
    this.#staticCapabilities = state.staticCapabilities;
    this.#dynamicCapabilities = state.dynamicCapabilities;
    this.#refinements = state.refinements;
    this.#translators = state.translators;
    this.#methods = state.methods;
    this.#environmentEpoch = state.environmentEpoch;
  }

  isNominalSubtype(sub: AtomId, sup: AtomId): boolean {
    return this.#ancestors.get(sub)?.has(sup) ?? false;
  }

  nominalPath(sub: AtomId, sup: AtomId): readonly AtomId[] | undefined {
    if (!this.#atoms.has(sub) || !this.#atoms.has(sup)) return undefined;
    if (sub === sup) return [sub];

    // Reconstruct one shortest path from the transitive relation. The registry
    // is small in this reference implementation, so scanning registered atoms
    // keeps the frozen state compact.
    const queue: { id: AtomId; path: AtomId[] }[] = [{ id: sub, path: [sub] }];
    const visited = new Set<AtomId>([sub]);
    while (queue.length > 0) {
      const current = queue.shift()!;
      for (const candidate of this.#atoms.keys()) {
        if (visited.has(candidate)) continue;
        const candidateAncestors = this.#ancestors.get(current.id)!;
        const directOrIntermediate =
          candidateAncestors.has(candidate) &&
          ![...this.#atoms.keys()].some(
            (middle) =>
              middle !== current.id &&
              middle !== candidate &&
              candidateAncestors.has(middle) &&
              this.#ancestors.get(middle)!.has(candidate),
          );
        if (!directOrIntermediate) continue;
        const path = [...current.path, candidate];
        if (candidate === sup) return path;
        visited.add(candidate);
        queue.push({ id: candidate, path });
      }
    }
    return this.isNominalSubtype(sub, sup) ? [sub, sup] : undefined;
  }

  identityFor(
    reference: PresentationReference,
    environment: Environment,
  ): SemanticIdentity | undefined {
    const descriptor = this.#atoms.get(reference.type);
    if (!descriptor) return undefined;
    const declared = descriptor.identity?.(reference.value, environment);
    if (declared) return declared;

    const value = reference.value;
    if (
      typeof value === "string" ||
      typeof value === "number" ||
      typeof value === "boolean" ||
      typeof value === "bigint"
    ) {
      return {
        namespace: reference.type,
        key: `${typeof value}:${String(value)}`,
      };
    }
    if ((typeof value === "object" && value !== null) || typeof value === "function") {
      const object = value as object;
      let key = this.#objectIdentity.get(object);
      if (key === undefined) {
        key = this.#nextObjectIdentity++;
        this.#objectIdentity.set(object, key);
      }
      return { namespace: `runtime-object:${reference.type}`, key };
    }
    return undefined;
  }

  revisionFor(
    reference: PresentationReference,
    environment: Environment,
  ): string | number | undefined {
    return this.#atoms.get(reference.type)?.revision?.(reference.value, environment);
  }

  sameObject(
    left: PresentationReference,
    right: PresentationReference,
    environment: Environment,
  ): boolean {
    const a = this.identityFor(left, environment);
    const b = this.identityFor(right, environment);
    return a !== undefined && b !== undefined && sameIdentity(a, b);
  }

  labelFor(reference: PresentationReference, environment: Environment): string {
    const descriptor = this.#atoms.get(reference.type);
    if (!descriptor) return `<unknown:${reference.type}>`;
    return descriptor.label?.(reference.value, environment) ?? String(reference.value);
  }

  direct<T>(
    reference: PresentationReference,
    expression: TypeExpr<T>,
    environment: Environment,
  ): MatchResult<T> {
    const checked = this.#membership(reference, expression, environment);
    if (!checked.ok) return checked;
    return {
      ok: true,
      match: this.#buildMatch(
        reference,
        reference as PresentationReference<T>,
        expression,
        checked.evidence,
        [],
        checked.dependencies,
        environment,
      ),
    };
  }

  async match<T>(
    source: PresentationReference,
    expression: TypeExpr<T>,
    environment: Environment,
    options: MatchOptions = {},
  ): Promise<MatchResult<T>> {
    const direct = this.direct(source, expression, environment);
    if (direct.ok || (options.translations ?? "paths") === "none") return direct;

    const mode = options.translations ?? "paths";
    const maxDepth = mode === "direct" ? 1 : options.maxTranslationDepth ?? 4;
    const maxStates = options.maxTranslationStates ?? 128;

    interface State {
      readonly reference: PresentationReference;
      readonly path: readonly TranslationEvidence[];
      readonly cost: number;
      readonly priority: number;
    }

    const queue: State[] = [{ reference: source, path: [], cost: 0, priority: 0 }];
    const bestCost = new Map<string, number>([[this.#stateKey(source, environment), 0]]);
    const successes: { state: State; evidence: MembershipEvidence; dependencies: DependencyFingerprint[] }[] = [];
    let explored = 0;
    let bestSuccessCost = Number.POSITIVE_INFINITY;

    while (queue.length > 0) {
      queue.sort(compareStates);
      const state = queue.shift()!;
      if (state.cost > bestSuccessCost) break;
      if (state.path.length >= maxDepth) continue;
      explored += 1;
      if (explored > maxStates) {
        return {
          ok: false,
          failure: {
            reason: "translation-budget",
            message: `Translation search exceeded ${maxStates} states`,
            expression,
            reference: source,
          },
        };
      }

      for (const translator of this.#candidateTranslators(state.reference.type)) {
        if (translator.applicable?.(state.reference.value, environment) === false) {
          continue;
        }
        const value = await translator.translate(state.reference.value, environment);
        if (value === undefined) continue;

        const translated: PresentationReference = {
          type: translator.to,
          value,
        };
        const edge: TranslationEvidence = {
          translator: translator.id,
          from: state.reference.type,
          to: translator.to,
          cost: translator.cost,
          preservesIdentity: translator.preservesIdentity,
        };
        const next: State = {
          reference: translated,
          path: [...state.path, edge],
          cost: state.cost + translator.cost,
          priority: state.priority + translator.priority,
        };
        const key = this.#stateKey(translated, environment);
        const previous = bestCost.get(key);
        if (previous !== undefined && previous < next.cost) continue;
        bestCost.set(key, next.cost);

        const checked = this.#membership(translated, expression, environment);
        if (checked.ok) {
          bestSuccessCost = Math.min(bestSuccessCost, next.cost);
          successes.push({
            state: next,
            evidence: checked.evidence,
            dependencies: checked.dependencies,
          });
        }
        if (next.path.length < maxDepth) queue.push(next);
      }
    }

    if (successes.length === 0) return direct;
    successes.sort((a, b) => compareStates(a.state, b.state));
    const winner = successes[0]!;
    const equivalentWinners = successes.filter(
      (candidate) =>
        candidate.state.cost === winner.state.cost &&
        candidate.state.priority === winner.state.priority,
    );
    const distinct = new Map<string, typeof winner>();
    for (const candidate of equivalentWinners) {
      distinct.set(
        `${this.#stateKey(candidate.state.reference, environment)}|${candidate.state.path
          .map((edge) => edge.translator)
          .join(">")}`,
        candidate,
      );
    }
    if (distinct.size > 1) {
      return {
        ok: false,
        failure: {
          reason: "ambiguous-translation",
          message: `Several equal-cost translation paths satisfy ${printType(expression)}: ${[
            ...distinct.values(),
          ]
            .map((candidate) =>
              candidate.state.path.map((edge) => edge.translator).join(" → "),
            )
            .join("; ")}`,
          expression,
          reference: source,
        },
      };
    }

    return {
      ok: true,
      match: this.#buildMatch(
        source,
        winner.state.reference as PresentationReference<T>,
        expression,
        winner.evidence,
        winner.state.path,
        winner.dependencies,
        environment,
      ),
    };
  }

  /**
   * Sound but intentionally incomplete subtype proof search. A true answer is
   * justified by the finite registry semantics; false may mean either "no" or
   * "not proved by this small algorithm".
   */
  isSubtype(left: TypeExpr, right: TypeExpr): boolean {
    if (expressionKey(left) === expressionKey(right)) return true;
    if (left.kind === "bottom" || right.kind === "top") return true;
    if (right.kind === "bottom") return false;
    if (left.kind === "top") return false;

    if (left.kind === "atom" && right.kind === "atom") {
      return this.isNominalSubtype(left.atom, right.atom);
    }
    if (left.kind === "atom" && right.kind === "capability") {
      return this.#staticCapabilities.get(left.atom)?.has(right.capability) ?? false;
    }
    if (left.kind === "union") {
      return left.members.every((member) => this.isSubtype(member, right));
    }
    if (right.kind === "intersection") {
      return right.members.every((member) => this.isSubtype(left, member));
    }
    if (left.kind === "intersection") {
      return left.members.some((member) => this.isSubtype(member, right));
    }
    if (right.kind === "union") {
      return right.members.some((member) => this.isSubtype(left, member));
    }
    if (left.kind === "difference") {
      return this.isSubtype(left.base, right);
    }
    if (left.kind === "refinement") {
      if (right.kind === "refinement") {
        return (
          left.refinement === right.refinement &&
          stableStringify(left.args) === stableStringify(right.args) &&
          this.isSubtype(left.base, right.base)
        );
      }
      return this.isSubtype(left.base, right);
    }
    if (right.kind === "difference") {
      return (
        this.isSubtype(left, right.base) &&
        this.isProvablyDisjoint(left, right.excluded)
      );
    }
    return false;
  }

  isProvablyDisjoint(left: TypeExpr, right: TypeExpr): boolean {
    if (left.kind === "bottom" || right.kind === "bottom") return true;
    if (expressionKey(left) === expressionKey(right)) return false;
    if (left.kind === "union") {
      return left.members.every((member) => this.isProvablyDisjoint(member, right));
    }
    if (right.kind === "union") {
      return right.members.every((member) => this.isProvablyDisjoint(left, member));
    }
    if (left.kind === "intersection") {
      return left.members.some((member) => this.isProvablyDisjoint(member, right));
    }
    if (right.kind === "intersection") {
      return right.members.some((member) => this.isProvablyDisjoint(left, member));
    }
    if (left.kind === "difference" && expressionKey(left.excluded) === expressionKey(right)) {
      return true;
    }
    if (right.kind === "difference" && expressionKey(right.excluded) === expressionKey(left)) {
      return true;
    }
    if (left.kind === "atom" && right.kind === "atom") {
      for (const candidate of this.#atoms.keys()) {
        if (
          this.isNominalSubtype(candidate, left.atom) &&
          this.isNominalSubtype(candidate, right.atom)
        ) {
          return false;
        }
      }
      return true;
    }
    return false;
  }

  compareTypes(left: TypeExpr, right: TypeExpr): TypeComparison {
    const leftToRight = this.isSubtype(left, right);
    const rightToLeft = this.isSubtype(right, left);
    if (leftToRight && rightToLeft) return "equal";
    if (leftToRight) return "less";
    if (rightToLeft) return "greater";
    return "incomparable";
  }

  dispatch<Result>(
    generic: GenericFunctionId,
    subjectReference: PresentationReference,
    environment: Environment,
    contextReference?: PresentationReference,
  ): DispatchResult<Result> {
    requireNonEmpty("generic function id", generic);
    const applicable: {
      readonly method: RegisteredMethod<unknown, Environment>;
      readonly subject: Match;
      readonly context?: Match;
    }[] = [];

    for (const method of this.#methods) {
      if (method.generic !== generic) continue;
      const subject = this.direct(subjectReference, method.subject, environment);
      if (!subject.ok) continue;
      let context: Match | undefined;
      if (method.context) {
        if (!contextReference) continue;
        const contextResult = this.direct(contextReference, method.context, environment);
        if (!contextResult.ok) continue;
        context = contextResult.match;
      }
      applicable.push(
        context
          ? { method, subject: subject.match, context }
          : { method, subject: subject.match },
      );
    }

    if (applicable.length === 0) {
      return { ok: false, reason: "no-method", applicable: [] };
    }

    const maximal = applicable.filter((candidate) =>
      !applicable.some(
        (other) =>
          other !== candidate &&
          this.#methodMoreSpecific(other.method, candidate.method),
      ),
    );
    maximal.sort((a, b) => {
      const priority = b.method.priority - a.method.priority;
      return priority !== 0 ? priority : a.method.id.localeCompare(b.method.id);
    });
    const highestPriority = maximal[0]!.method.priority;
    const winners = maximal.filter((item) => item.method.priority === highestPriority);
    if (winners.length !== 1) {
      return {
        ok: false,
        reason: "ambiguous-method",
        applicable: winners.map((item) => item.method.id),
      };
    }

    const winner = winners[0]!;
    return {
      ok: true,
      methodId: winner.method.id,
      value: winner.method.invoke(
        winner.context
          ? {
              subject: winner.subject,
              context: winner.context,
              environment,
            }
          : {
              subject: winner.subject,
              environment,
            },
      ) as Result,
    };
  }

  isStillValid(token: ValidityToken, environment: Environment): boolean {
    return (
      token.registryVersion === this.version &&
      token.environmentEpoch === this.#environmentEpoch(environment)
    );
  }

  #membership(
    reference: PresentationReference,
    expression: TypeExpr,
    environment: Environment,
  ):
    | {
        readonly ok: true;
        readonly evidence: MembershipEvidence;
        readonly dependencies: DependencyFingerprint[];
      }
    | { readonly ok: false; readonly failure: MatchFailure } {
    if (!this.#atoms.has(reference.type)) {
      return {
        ok: false,
        failure: {
          reason: "unknown-atom",
          message: `Unknown presentation atom: ${reference.type}`,
          expression,
          reference,
        },
      };
    }

    switch (expression.kind) {
      case "top":
        return { ok: true, evidence: { kind: "top" }, dependencies: [] };
      case "bottom":
        return this.#notMember(reference, expression, "The bottom type has no members");
      case "atom": {
        const path = this.nominalPath(reference.type, expression.atom);
        return path
          ? {
              ok: true,
              evidence: {
                kind: "atom",
                actual: reference.type,
                requested: expression.atom,
                nominalPath: path,
              },
              dependencies: [],
            }
          : this.#notMember(
              reference,
              expression,
              `${reference.type} is not a subtype of ${expression.atom}`,
            );
      }
      case "capability": {
        if (!this.#capabilities.has(expression.capability)) {
          return {
            ok: false,
            failure: {
              reason: "unknown-definition",
              message: `Unknown capability: ${expression.capability}`,
              expression,
              reference,
            },
          };
        }
        const ancestors = this.#ancestors.get(reference.type)!;
        for (const declaredOn of ancestors) {
          if (
            this.#staticCapabilities.get(declaredOn)?.has(expression.capability)
          ) {
            return {
              ok: true,
              evidence: {
                kind: "capability",
                capability: expression.capability,
                implementation: "static",
                declaredOn,
              },
              dependencies: [],
            };
          }
        }
        const negativeDependencies: DependencyFingerprint[] = [];
        for (const implementation of this.#dynamicCapabilities) {
          if (
            implementation.capability !== expression.capability ||
            !ancestors.has(implementation.atom)
          ) {
            continue;
          }
          const dependency = implementation.dependencies?.(
            reference.value,
            environment,
          );
          if (implementation.test(reference.value, environment)) {
            return {
              ok: true,
              evidence: {
                kind: "capability",
                capability: expression.capability,
                implementation: implementation.id,
                declaredOn: implementation.atom,
              },
              dependencies: dependency ? [dependency] : [],
            };
          }
          if (dependency) negativeDependencies.push(dependency);
        }
        return this.#notMember(
          reference,
          expression,
          `${reference.type} does not implement ${expression.capability}`,
          negativeDependencies,
        );
      }
      case "union": {
        const causes: MatchFailure[] = [];
        for (let index = 0; index < expression.members.length; index += 1) {
          const result = this.#membership(
            reference,
            expression.members[index]!,
            environment,
          );
          if (result.ok) {
            return {
              ok: true,
              evidence: {
                kind: "union",
                branch: index,
                evidence: result.evidence,
              },
              dependencies: result.dependencies,
            };
          }
          causes.push(result.failure);
        }
        const dependencies = deduplicateFingerprints(
          causes.flatMap((cause) => cause.dependencies ?? []),
        );
        return {
          ok: false,
          failure: {
            reason: "not-a-member",
            message: `No union branch accepted ${reference.type}`,
            expression,
            reference,
            causes,
            ...(dependencies.length > 0 ? { dependencies } : {}),
          },
        };
      }
      case "intersection": {
        const evidence: MembershipEvidence[] = [];
        const dependencies: DependencyFingerprint[] = [];
        for (const member of expression.members) {
          const result = this.#membership(reference, member, environment);
          if (!result.ok) return result;
          evidence.push(result.evidence);
          dependencies.push(...result.dependencies);
        }
        return {
          ok: true,
          evidence: { kind: "intersection", members: evidence },
          dependencies,
        };
      }
      case "difference": {
        const base = this.#membership(reference, expression.base, environment);
        if (!base.ok) return base;
        const excluded = this.#membership(
          reference,
          expression.excluded,
          environment,
        );
        if (excluded.ok) {
          return this.#notMember(
            reference,
            expression,
            `${reference.type} belongs to the excluded type ${printType(
              expression.excluded,
            )}`,
            excluded.dependencies,
          );
        }
        if (excluded.failure.reason !== "not-a-member") return excluded;
        const excludedDependencies = excluded.failure.dependencies ?? [];
        return {
          ok: true,
          evidence: {
            kind: "difference",
            base: base.evidence,
            excluded: expression.excluded,
            excludedDependencies,
          },
          dependencies: [...base.dependencies, ...excludedDependencies],
        };
      }
      case "refinement": {
        const definition = this.#refinements.get(expression.refinement);
        if (!definition) {
          return {
            ok: false,
            failure: {
              reason: "unknown-definition",
              message: `Unknown refinement: ${expression.refinement}`,
              expression,
              reference,
            },
          };
        }
        if (expressionKey(definition.base) !== expressionKey(expression.base)) {
          return {
            ok: false,
            failure: {
              reason: "malformed-refinement",
              message: `Refinement ${expression.refinement} must use its declared base ${printType(
                definition.base,
              )}`,
              expression,
              reference,
            },
          };
        }
        const base = this.#membership(reference, expression.base, environment);
        if (!base.ok) return base;
        const dependency = definition.dependencies?.(
          reference.value,
          expression.args,
          environment,
        );
        if (!definition.test(reference.value, expression.args, environment)) {
          return this.#notMember(
            reference,
            expression,
            `Refinement ${expression.refinement} rejected ${reference.type}`,
            dependency ? [dependency] : [],
          );
        }
        return {
          ok: true,
          evidence: dependency
            ? {
                kind: "refinement",
                refinement: expression.refinement,
                base: base.evidence,
                dependency,
              }
            : {
                kind: "refinement",
                refinement: expression.refinement,
                base: base.evidence,
              },
          dependencies: [
            ...base.dependencies,
            ...(dependency ? [dependency] : []),
          ],
        };
      }
    }
  }

  #notMember(
    reference: PresentationReference,
    expression: TypeExpr,
    message: string,
    dependencies: readonly DependencyFingerprint[] = [],
  ): { readonly ok: false; readonly failure: MatchFailure } {
    const uniqueDependencies = deduplicateFingerprints(dependencies);
    return {
      ok: false,
      failure: {
        reason: "not-a-member",
        message,
        expression,
        reference,
        ...(uniqueDependencies.length > 0
          ? { dependencies: uniqueDependencies }
          : {}),
      },
    };
  }

  #buildMatch<T>(
    source: PresentationReference,
    accepted: PresentationReference<T>,
    requestedType: TypeExpr<T>,
    membership: MembershipEvidence,
    translationPath: readonly TranslationEvidence[],
    dependencies: readonly DependencyFingerprint[],
    environment: Environment,
  ): Match<T> {
    return {
      source,
      accepted,
      requestedType,
      membership,
      translationPath,
      validity: buildValidityToken({
        registryVersion: this.version,
        environmentEpoch: this.#environmentEpoch(environment),
        sourceIdentity: this.identityFor(source, environment),
        sourceRevision: this.revisionFor(source, environment),
        dependencies: deduplicateFingerprints(dependencies),
      }),
    };
  }

  #candidateTranslators(source: AtomId): readonly RegisteredTranslator<Environment>[] {
    return this.#translators
      .filter((translator) => this.isNominalSubtype(source, translator.from))
      .sort((a, b) => {
        if (a.cost !== b.cost) return a.cost - b.cost;
        if (a.priority !== b.priority) return b.priority - a.priority;
        return a.id.localeCompare(b.id);
      });
  }

  #stateKey(reference: PresentationReference, environment: Environment): string {
    const identity = this.identityFor(reference, environment);
    if (identity) {
      return `${reference.type}|${identity.namespace}|${String(identity.key)}`;
    }
    return `${reference.type}|${stableStringify(reference.value)}`;
  }

  #methodMoreSpecific(
    left: RegisteredMethod<unknown, Environment>,
    right: RegisteredMethod<unknown, Environment>,
  ): boolean {
    const subjectAtLeast = this.isSubtype(left.subject, right.subject);
    const contextAtLeast =
      right.context === undefined ||
      (left.context !== undefined && this.isSubtype(left.context, right.context));
    if (!subjectAtLeast || !contextAtLeast) return false;

    const subjectStrict = !this.isSubtype(right.subject, left.subject);
    const contextStrict =
      left.context !== undefined &&
      right.context !== undefined &&
      !this.isSubtype(right.context, left.context);
    const hasContextWhereRightDoesNot =
      left.context !== undefined && right.context === undefined;
    return subjectStrict || contextStrict || hasContextWhereRightDoesNot;
  }
}

export type DispatchResult<Result> =
  | {
      readonly ok: true;
      readonly methodId: MethodId;
      readonly value: Result;
    }
  | {
      readonly ok: false;
      readonly reason: "no-method" | "ambiguous-method";
      readonly applicable: readonly MethodId[];
    };

export type InputContextState = "pending" | "resolved" | "aborted";

/**
 * Minimal at-most-once input context. The caller supplies the environment used
 * for each offer, making revalidation at commitment explicit.
 */
export class InputContext<T, Environment> {
  readonly #registry: RegistrySnapshot<Environment>;
  readonly #requestedType: TypeExpr<T>;
  readonly #options: MatchOptions;
  readonly #promise: Promise<Match<T> | null>;
  #resolve!: (value: Match<T> | null) => void;
  #state: InputContextState = "pending";

  constructor(
    registry: RegistrySnapshot<Environment>,
    requestedType: TypeExpr<T>,
    options: MatchOptions = {},
  ) {
    this.#registry = registry;
    this.#requestedType = requestedType;
    this.#options = options;
    this.#promise = new Promise((resolve) => {
      this.#resolve = resolve;
    });
  }

  get state(): InputContextState {
    return this.#state;
  }

  get result(): Promise<Match<T> | null> {
    return this.#promise;
  }

  async offer(
    reference: PresentationReference,
    environment: Environment,
  ): Promise<boolean> {
    if (this.#state !== "pending") return false;
    const result = await this.#registry.match(
      reference,
      this.#requestedType,
      environment,
      this.#options,
    );
    if (!result.ok || this.#state !== "pending") return false;
    this.#state = "resolved";
    this.#resolve(result.match);
    return true;
  }

  abort(): boolean {
    if (this.#state !== "pending") return false;
    this.#state = "aborted";
    this.#resolve(null);
    return true;
  }
}

export interface SubjectView {
  readonly id: string;
  readonly bindingId?: string;
  readonly subjects: Readonly<Record<string, string>>;
}

/** Private view bindings are represented by the view ID itself. */
export function effectiveBindingId(view: SubjectView): string {
  return view.bindingId ?? view.id;
}

/**
 * Merge the target binding group into the source group. Source subjects win at
 * link time, after which all members share one materialized role map.
 */
export function linkSubjectViews(
  views: readonly SubjectView[],
  sourceId: string,
  targetId: string,
): readonly SubjectView[] {
  const source = requireView(views, sourceId);
  const target = requireView(views, targetId);
  const sourceBinding = effectiveBindingId(source);
  const targetBinding = effectiveBindingId(target);
  const members = views.filter((view) => {
    const binding = effectiveBindingId(view);
    return binding === sourceBinding || binding === targetBinding;
  });
  const mergedSubjects = Object.freeze({
    ...target.subjects,
    ...source.subjects,
  });
  return views.map((view) =>
    members.includes(view)
      ? Object.freeze({
          ...view,
          bindingId: sourceBinding,
          subjects: mergedSubjects,
        })
      : view,
  );
}

export function setSubject(
  views: readonly SubjectView[],
  viewId: string,
  role: string,
  subjectId: string,
): readonly SubjectView[] {
  const view = requireView(views, viewId);
  const binding = effectiveBindingId(view);
  const nextSubjects = Object.freeze({ ...view.subjects, [role]: subjectId });
  return views.map((candidate) =>
    effectiveBindingId(candidate) === binding
      ? Object.freeze({ ...candidate, bindingId: binding, subjects: nextSubjects })
      : candidate,
  );
}

export function unlinkSubjectView(
  views: readonly SubjectView[],
  viewId: string,
): readonly SubjectView[] {
  const view = requireView(views, viewId);
  return views.map((candidate) =>
    candidate.id === viewId
      ? Object.freeze({
          ...candidate,
          bindingId: candidate.id,
          subjects: Object.freeze({ ...candidate.subjects }),
        })
      : candidate,
  );
}

export function bindingsAreCoherent(views: readonly SubjectView[]): boolean {
  const byBinding = new Map<string, string>();
  for (const view of views) {
    const binding = effectiveBindingId(view);
    const subjects = stableStringify(view.subjects);
    const previous = byBinding.get(binding);
    if (previous !== undefined && previous !== subjects) return false;
    byBinding.set(binding, subjects);
  }
  return true;
}

function requireView(views: readonly SubjectView[], id: string): SubjectView {
  const view = views.find((candidate) => candidate.id === id);
  if (!view) throw new Error(`Unknown view: ${id}`);
  return view;
}

function validateAcyclic(edges: ReadonlyMap<AtomId, ReadonlySet<AtomId>>): void {
  const visiting = new Set<AtomId>();
  const visited = new Set<AtomId>();

  const visit = (id: AtomId, path: AtomId[]): void => {
    if (visiting.has(id)) {
      throw new Error(`Nominal subtype cycle: ${[...path, id].join(" -> ")}`);
    }
    if (visited.has(id)) return;
    visiting.add(id);
    for (const parent of edges.get(id) ?? []) visit(parent, [...path, id]);
    visiting.delete(id);
    visited.add(id);
  };

  for (const id of edges.keys()) visit(id, []);
}

function computeAncestorClosure(
  edges: ReadonlyMap<AtomId, ReadonlySet<AtomId>>,
): ReadonlyMap<AtomId, ReadonlySet<AtomId>> {
  const memo = new Map<AtomId, ReadonlySet<AtomId>>();
  const ancestorsOf = (id: AtomId): ReadonlySet<AtomId> => {
    const existing = memo.get(id);
    if (existing) return existing;
    const result = new Set<AtomId>([id]);
    for (const parent of edges.get(id) ?? []) {
      for (const ancestor of ancestorsOf(parent)) result.add(ancestor);
    }
    memo.set(id, result);
    return result;
  };
  for (const id of edges.keys()) ancestorsOf(id);
  return memo;
}

function validateExpressionNames<Environment>(
  expression: TypeExpr,
  atoms: ReadonlyMap<AtomId, AtomDescriptor<unknown, Environment>>,
  capabilities: ReadonlySet<CapabilityId>,
  refinements: ReadonlyMap<RefinementId, RegisteredRefinement<Environment>>,
  allowSelfRefinement = false,
): void {
  switch (expression.kind) {
    case "top":
    case "bottom":
      return;
    case "atom":
      if (!atoms.has(expression.atom)) throw new Error(`Unknown atom: ${expression.atom}`);
      return;
    case "capability":
      if (!capabilities.has(expression.capability)) {
        throw new Error(`Unknown capability: ${expression.capability}`);
      }
      return;
    case "union":
    case "intersection":
      for (const member of expression.members) {
        validateExpressionNames(member, atoms, capabilities, refinements, allowSelfRefinement);
      }
      return;
    case "difference":
      validateExpressionNames(expression.base, atoms, capabilities, refinements, allowSelfRefinement);
      validateExpressionNames(expression.excluded, atoms, capabilities, refinements, allowSelfRefinement);
      return;
    case "refinement":
      if (!refinements.has(expression.refinement) && !allowSelfRefinement) {
        throw new Error(`Unknown refinement: ${expression.refinement}`);
      }
      validateExpressionNames(expression.base, atoms, capabilities, refinements, allowSelfRefinement);
  }
}

function deduplicateExpressions<T>(members: readonly TypeExpr<T>[]): TypeExpr<T>[] {
  const seen = new Set<string>();
  const result: TypeExpr<T>[] = [];
  for (const member of members) {
    const key = expressionKey(member);
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(member);
  }
  result.sort((a, b) => expressionKey(a).localeCompare(expressionKey(b)));
  return result;
}

export function expressionKey(expression: TypeExpr): string {
  switch (expression.kind) {
    case "top":
      return "top";
    case "bottom":
      return "bottom";
    case "atom":
      return `atom:${expression.atom}`;
    case "capability":
      return `capability:${expression.capability}`;
    case "union":
      return `or(${expression.members.map(expressionKey).sort().join(",")})`;
    case "intersection":
      return `and(${expression.members.map(expressionKey).sort().join(",")})`;
    case "difference":
      return `difference(${expressionKey(expression.base)},${expressionKey(expression.excluded)})`;
    case "refinement":
      return `refine(${expression.refinement},${stableStringify(expression.args)},${expressionKey(
        expression.base,
      )})`;
  }
}

function stableStringify(value: unknown): string {
  const seen = new WeakSet<object>();
  const normalize = (input: unknown): unknown => {
    if (
      input === null ||
      typeof input === "string" ||
      typeof input === "number" ||
      typeof input === "boolean"
    ) {
      return input;
    }
    if (typeof input === "bigint") return `${input}n`;
    if (typeof input === "undefined") return "<undefined>";
    if (typeof input === "function") return `<function:${input.name || "anonymous"}>`;
    if (typeof input === "symbol") return `<symbol:${String(input.description)}>`;
    if (Array.isArray(input)) return input.map(normalize);
    if (typeof input === "object") {
      if (seen.has(input)) return "<cycle>";
      seen.add(input);
      const record = input as Record<string, unknown>;
      return Object.fromEntries(
        Object.keys(record)
          .sort()
          .map((key) => [key, normalize(record[key])]),
      );
    }
    return String(input);
  };
  return JSON.stringify(normalize(value));
}

function hashText(text: string): string {
  let hash = 0x811c9dc5;
  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return `fnv1a32:${(hash >>> 0).toString(16).padStart(8, "0")}`;
}

function compareStates(
  left: { readonly cost: number; readonly priority: number; readonly path: readonly TranslationEvidence[] },
  right: { readonly cost: number; readonly priority: number; readonly path: readonly TranslationEvidence[] },
): number {
  if (left.cost !== right.cost) return left.cost - right.cost;
  if (left.priority !== right.priority) return right.priority - left.priority;
  return left.path
    .map((edge) => edge.translator)
    .join(">")
    .localeCompare(right.path.map((edge) => edge.translator).join(">"));
}

function sameIdentity(left: SemanticIdentity, right: SemanticIdentity): boolean {
  return left.namespace === right.namespace && left.key === right.key;
}

function deduplicateFingerprints(
  fingerprints: readonly DependencyFingerprint[],
): readonly DependencyFingerprint[] {
  const byKey = new Map<string, DependencyFingerprint>();
  for (const fingerprint of fingerprints) {
    byKey.set(
      `${fingerprint.definitionId}:${stableStringify(fingerprint.parts)}`,
      fingerprint,
    );
  }
  return Object.freeze([...byKey.values()]);
}

function buildValidityToken(input: {
  readonly registryVersion: number;
  readonly environmentEpoch: string | number;
  readonly sourceIdentity: SemanticIdentity | undefined;
  readonly sourceRevision: string | number | undefined;
  readonly dependencies: readonly DependencyFingerprint[];
}): ValidityToken {
  return {
    registryVersion: input.registryVersion,
    environmentEpoch: input.environmentEpoch,
    dependencies: input.dependencies,
    ...(input.sourceIdentity ? { sourceIdentity: input.sourceIdentity } : {}),
    ...(input.sourceRevision !== undefined
      ? { sourceRevision: input.sourceRevision }
      : {}),
  };
}

function requireNonEmpty(label: string, value: string): void {
  if (value.trim().length === 0) throw new Error(`${label} must not be empty`);
}

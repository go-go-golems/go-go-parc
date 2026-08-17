import {
  InputContext,
  RegistryBuilder,
  and,
  atom,
  bindingsAreCoherent,
  bottom,
  difference,
  effectiveBindingId,
  expressionKey,
  linkSubjectViews,
  or,
  setSubject,
  top,
  unlinkSubjectView,
  type MatchResult,
  type PresentationReference,
  type SubjectView,
  type TypeExpr,
} from "./presentation-type-kernel.js";

interface Entity {
  readonly id: string;
}

interface Project extends Entity {
  readonly title: string;
  readonly ownerId: string;
  readonly archived: boolean;
  readonly revision: number;
}

interface Environment {
  readonly epoch: number;
  readonly currentUserId: string;
  readonly projects: Readonly<Record<string, Project | undefined>>;
}

interface InteractionContext {
  readonly kind: string;
}

interface AdminContext extends InteractionContext {
  readonly kind: "admin";
}

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(`Assertion failed: ${message}`);
}

function assertEqual<T>(actual: T, expected: T, message: string): void {
  if (!Object.is(actual, expected)) {
    throw new Error(
      `Assertion failed: ${message}\nexpected ${String(expected)}\nactual   ${String(actual)}`,
    );
  }
}

function assertOk<T>(result: MatchResult<T>, message: string) {
  assert(result.ok, `${message}: ${result.ok ? "" : result.failure.message}`);
  return result.match;
}

async function main(): Promise<void> {
  const compiler: Project = {
    id: "compiler",
    title: "Incremental compiler",
    ownerId: "person-1",
    archived: false,
    revision: 4,
  };
  const renderer: Project = {
    id: "renderer",
    title: "Presentation renderer",
    ownerId: "person-2",
    archived: false,
    revision: 7,
  };
  const oldPrototype: Project = {
    id: "old-prototype",
    title: "Archived prototype",
    ownerId: "person-1",
    archived: true,
    revision: 11,
  };
  const environment: Environment = {
    epoch: 3,
    currentUserId: "person-1",
    projects: {
      compiler,
      renderer,
      "old-prototype": oldPrototype,
    },
  };

  const builder = new RegistryBuilder<Environment>({
    environmentEpoch: (current) => current.epoch,
  });

  const EntityType = builder.addAtom<Entity>("entity", {
    identity: (entity) => ({ namespace: "project", key: entity.id }),
  });
  const ProjectType = builder.addAtom<Project>("project", {
    label: (project) => project.title,
    identity: (project) => ({ namespace: "project", key: project.id }),
    revision: (project) => project.revision,
  });
  const ProjectIdType = builder.addAtom<string>("project-id", {
    identity: (projectId) => ({ namespace: "project", key: projectId }),
  });
  builder.addAtom<string>("project-alias", {
    identity: (projectId) => ({ namespace: "project", key: projectId }),
  });
  const ContextType = builder.addAtom<InteractionContext>("interaction-context");
  const AdminContextType = builder.addAtom<AdminContext>("admin-context");

  builder.declareSubtype(ProjectType, EntityType);
  builder.declareSubtype(AdminContextType, ContextType);

  const Inspectable = builder.addCapability("inspectable");
  const Archived = builder.addCapability("archived");
  builder.implementStatic(EntityType, Inspectable);
  builder.implementDynamic<Project>({
    id: "project-is-archived",
    atom: ProjectType.atom,
    capability: Archived.capability,
    test: (project) => project.archived,
    dependencies: (project) => ({
      definitionId: "project-is-archived",
      parts: [project.id, project.revision],
    }),
  });

  const OwnedBy = builder.addRefinement<Project, { readonly ownerId: string }>({
    id: "owned-by",
    base: ProjectType,
    test: (project, args) => project.ownerId === args.ownerId,
    dependencies: (project, args) => ({
      definitionId: "owned-by",
      parts: [project.id, project.revision, args.ownerId],
    }),
  });

  const ActiveProject: TypeExpr<Project> = difference(ProjectType, Archived);
  const MyActiveProject: TypeExpr<Project> = and<Project>(
    ActiveProject,
    Inspectable as TypeExpr<Project>,
    OwnedBy({ ownerId: environment.currentUserId }),
  );

  // The lower-cost two-edge path must beat the costlier direct translator.
  builder.addTranslator<string, Project>({
    id: "project-id/direct-project",
    from: ProjectIdType.atom,
    to: ProjectType.atom,
    cost: 3,
    preservesIdentity: true,
    translate: (id, current) => current.projects[id],
  });
  builder.addTranslator<string, string>({
    id: "project-id/to-alias",
    from: ProjectIdType.atom,
    to: "project-alias",
    cost: 1,
    preservesIdentity: true,
    translate: (id) => id,
  });
  builder.addTranslator<string, Project>({
    id: "project-alias/to-project",
    from: "project-alias",
    to: ProjectType.atom,
    cost: 1,
    preservesIdentity: true,
    translate: (id, current) => current.projects[id],
  });

  builder.addMethod<string>({
    id: "inspect-entity",
    generic: "inspect",
    subject: EntityType,
    invoke: ({ subject }) => `entity:${String((subject.accepted.value as Entity).id)}`,
  });
  builder.addMethod<string>({
    id: "inspect-project",
    generic: "inspect",
    subject: ProjectType,
    invoke: ({ subject }) => `project:${(subject.accepted.value as Project).title}`,
  });
  builder.addMethod<string>({
    id: "archive-active-project",
    generic: "archive",
    subject: ActiveProject,
    context: AdminContextType,
    invoke: ({ subject }) => `archive:${(subject.accepted.value as Project).id}`,
  });

  const registry = builder.freeze();
  const compilerReference: PresentationReference<Project> = {
    type: ProjectType.atom,
    value: compiler,
  };
  const rendererReference: PresentationReference<Project> = {
    type: ProjectType.atom,
    value: renderer,
  };
  const archivedReference: PresentationReference<Project> = {
    type: ProjectType.atom,
    value: oldPrototype,
  };
  const compilerIdReference: PresentationReference<string> = {
    type: ProjectIdType.atom,
    value: compiler.id,
  };

  // Boolean smart-constructor laws.
  assertEqual(expressionKey(or(ProjectType, ProjectType)), expressionKey(ProjectType), "union idempotence");
  assertEqual(expressionKey(and(ProjectType, top())), expressionKey(ProjectType), "top is intersection identity");
  assertEqual(expressionKey(or(ProjectType, bottom())), expressionKey(ProjectType), "bottom is union identity");
  assertEqual(expressionKey(difference(ProjectType, bottom())), expressionKey(ProjectType), "subtracting bottom changes nothing");

  // Nominal and capability subtyping.
  assert(registry.isSubtype(ProjectType, EntityType), "project is an entity");
  assert(registry.isSubtype(ProjectType, Inspectable), "entity capability is inherited");
  assert(registry.isSubtype(ActiveProject, ProjectType), "a difference is contained in its base");
  assert(registry.isSubtype(MyActiveProject, ProjectType), "intersection proof search finds a project conjunct");
  assert(!registry.isSubtype(EntityType, ProjectType), "entity is not project");

  // Direct matching returns proof-relevant evidence and dependency tokens.
  const compilerMatch = assertOk(
    registry.direct(compilerReference, MyActiveProject, environment),
    "owned active project should match",
  );
  assertEqual(compilerMatch.accepted.value.id, compiler.id, "accepted value is compiler");
  assertEqual(compilerMatch.validity.dependencies.length, 2, "negative archived evidence and owner refinement are tracked");
  assert(registry.isStillValid(compilerMatch.validity, environment), "evidence is valid in its environment epoch");
  assert(
    !registry.isStillValid(compilerMatch.validity, { ...environment, epoch: 4 }),
    "environment epoch invalidates evidence conservatively",
  );

  const wrongOwner = registry.direct(rendererReference, MyActiveProject, environment);
  assert(!wrongOwner.ok, "another user's project must be rejected");
  const archived = registry.direct(archivedReference, MyActiveProject, environment);
  assert(!archived.ok, "archived project must be excluded");

  // Semantic identity crosses presentation roles.
  assert(
    registry.sameObject(compilerReference, compilerIdReference, environment),
    "project object and project-id token denote one domain object",
  );

  // Translation search retains the winning proof path.
  const translated = assertOk(
    await registry.match(compilerIdReference, MyActiveProject, environment),
    "project id should translate to a project",
  );
  assertEqual(translated.translationPath.length, 2, "lower-cost two-edge path wins");
  assertEqual(translated.translationPath[0]!.translator, "project-id/to-alias", "first edge is alias conversion");
  assertEqual(translated.translationPath[1]!.translator, "project-alias/to-project", "second edge resolves the project");
  assertEqual(translated.accepted.value.id, compiler.id, "translated project is correct");

  // Product-order multimethod specificity.
  const inspection = registry.dispatch<string>("inspect", compilerReference, environment);
  assert(inspection.ok, "inspect dispatch succeeds");
  assertEqual(inspection.methodId, "inspect-project", "more-specific project method wins");
  assertEqual(inspection.value, "project:Incremental compiler", "specific method result");

  const adminReference: PresentationReference<AdminContext> = {
    type: AdminContextType.atom,
    value: { kind: "admin" },
  };
  const archiveDispatch = registry.dispatch<string>(
    "archive",
    compilerReference,
    environment,
    adminReference,
  );
  assert(archiveDispatch.ok, "archive dispatch succeeds in admin context");
  assertEqual(archiveDispatch.value, "archive:compiler", "archive result");
  const noContext = registry.dispatch<string>("archive", compilerReference, environment);
  assert(!noContext.ok && noContext.reason === "no-method", "context requirement is enforced");

  // Input contexts resolve at most once and can accept translated presentations.
  const input = new InputContext(registry, MyActiveProject);
  assert(await input.offer(compilerIdReference, environment), "first acceptable offer resolves input");
  assert(!(await input.offer(rendererReference, environment)), "resolved input rejects later offers");
  const accepted = await input.result;
  assert(accepted !== null, "input result is a match");
  assertEqual(accepted.accepted.value.id, compiler.id, "input accepted translated compiler project");
  assertEqual(input.state, "resolved", "input state is resolved");
  assert(!input.abort(), "resolved input cannot be aborted again");

  // Linked subject cells preserve group coherence.
  const initialViews: readonly SubjectView[] = [
    { id: "chart", subjects: { primary: "doc-a" } },
    { id: "pipeline", subjects: { primary: "doc-b" } },
    { id: "table", subjects: { primary: "doc-c" } },
  ];
  const linked = linkSubjectViews(initialViews, "chart", "pipeline");
  assert(bindingsAreCoherent(linked), "link operation creates a coherent group");
  const chart = linked.find((view) => view.id === "chart")!;
  const pipeline = linked.find((view) => view.id === "pipeline")!;
  assertEqual(effectiveBindingId(chart), effectiveBindingId(pipeline), "linked views share binding identity");
  assertEqual(pipeline.subjects.primary, "doc-a", "source subject wins at link time");

  const changed = setSubject(linked, "pipeline", "primary", "doc-z");
  assert(bindingsAreCoherent(changed), "subject update preserves group coherence");
  assertEqual(changed.find((view) => view.id === "chart")!.subjects.primary, "doc-z", "chart observes pipeline update");

  const unlinked = unlinkSubjectView(changed, "pipeline");
  assert(bindingsAreCoherent(unlinked), "unlink preserves coherence");
  const detached = unlinked.find((view) => view.id === "pipeline")!;
  assertEqual(effectiveBindingId(detached), "pipeline", "detached view regains a private binding");
  assertEqual(detached.subjects.primary, "doc-z", "detached view keeps its current subject");

  // Cycles are rejected during the declaration phase.
  const cyclic = new RegistryBuilder();
  const A = cyclic.addAtom<{ readonly a: true }>("A");
  const B = cyclic.addAtom<{ readonly a: true; readonly b: true }>("B");
  cyclic.declareSubtype(B, A);
  cyclic.declareSubtype(A, A);
  let cycleRejected = false;
  try {
    cyclic.freeze();
  } catch {
    cycleRejected = true;
  }
  assert(cycleRejected, "nominal cycles are rejected before runtime interaction");

  console.log("semantic-interfaces reference kernel: all executable laws passed");
}

await main();

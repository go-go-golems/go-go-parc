# CLIM UI Extensions

- URL: https://chatgpt.com/c/6a6aa9a2-5568-83ea-93f3-5bc24ce44116
- Created: 2026-07-30T01:32:19.188Z

---

> Extensions to the Common Lisp clim presentation based ui principles, for example creating presentations for different individual objects or dynamic object types, or for example creating new objects by assigning widgets or text selection to an object or object type for actions

I’ll map this onto standard CLIM mechanisms, then show extension patterns for object-specific, dynamic, widget-backed, and text-selection-backed presentations.

<details><summary>💭 Thinking</summary>

**Framing extensions**

I’m treating this as a design question about extending CLIM’s presentation model. I’ll connect new object types, presentation methods, editing gadgets, commands, and translators into one coherent extension pattern.

**Framed extensions**

</details>

```json
{"search_query":[{"q":"Common Lisp CLIM II specification presentations presentation types define-presentation-type official"},{"q":"McCLIM manual presentation types translators gadgets official"},{"q":"McCLIM source define-presentation-type GitHub"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 15 websites**

</details>

```json
{"search_query":[{"q":"site:lispworks.com/documentation clim define-presentation-action presentation translator with-output-as-presentation"},{"q":"site:lispworks.com/documentation clim define-presentation-to-command-translator syntax"},{"q":"site:mcclim.common-lisp.dev/static/manual presentation action translator define-presentation-method present accept"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

**Extending presentation behavior**

I’m separating stable presentation types from runtime object identity. I’d use parameterized types for dynamic behavior, object-specific translators for actions, and commands or gadgets for creating and editing objects.

**Extended presentation behavior**

</details>

```json
{"search_query":[{"q":"site:mcclim.common-lisp.dev/static/manual \"gadget-view\" presentation"},{"q":"site:github.com/McCLIM/McCLIM \"gadget-view\" \"define-presentation-method\""},{"q":"site:lispworks.com/documentation/lw81/clim \"gadget-view\" presentation type"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

**Designing CLIM extensions**

I’m treating CLIM presentations as semantic links between objects, types, views, and actions. I’ll distinguish per-class rendering, per-instance identity, dynamic predicates, editing widgets, and object-creation commands.

**Designed CLIM extensions**

</details>

```json
{"search_query":[{"q":"site:lispworks.com/documentation/lw81/clim \"member presentation type\" CLIM"},{"q":"site:mcclim.common-lisp.dev/static/manual \"(member\" \"presentation type\""},{"q":"site:lispworks.com/documentation/lw81/clim \"completion presentation type\" CLIM"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

**Generalizing presentations**

I’m extending CLIM around first-class presentation descriptors: object, semantic type, view, source location, and available actions. This supports per-instance behavior, runtime predicates, text selections, widgets, and constructor commands without creating a class for every object.

**Generalized presentations**

</details>

```json
{"search_query":[{"q":"site:lispworks.com/documentation/lw81/clim \"execute-frame-command\""},{"q":"site:mcclim.common-lisp.dev/static/manual \"execute-frame-command\""},{"q":"site:github.com/McCLIM/McCLIM \"activate-callback\" \"execute-frame-command\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 8 websites**

</details>

```unknown
bash -lc command -v sbcl || true; command -v ecl || true; ls -la /mnt/data | head
```

The key distinction is that CLIM already supports arbitrary objects and parameterized presentation types; the extension should unify gadgets and selections with translator/command machinery.

<details><summary>💭 Thinking</summary>

**Checked Lisp environment availability**

</details>

# Generalizing CLIM presentations beyond output records

These ideas fit CLIM’s architecture well. The useful extension is to treat a presentation as a **semantic binding attached to any interactive UI locus**, rather than only as a typed object attached to recorded output.

Standard CLIM already associates:

```text
displayed output ↔ Lisp object ↔ presentation type
```

The object may be any Lisp object, and the presentation type expresses its meaning in the interaction rather than merely its Common Lisp type. A presentation can also carry a `modifier` describing how an edited value should be stored. citeturn628722view0turn628722view1

A broader model would be:

```text
UI source
  + object or place
  + presentation type
  + occurrence state
  + revision/provenance
  + optional modifier
  = semantic presentation
```

A UI source could be:

- an ordinary CLIM output record;
- a gadget;
- a text selection;
- a selected region of a canvas;
- a drag payload;
- a blank area and coordinates;
- an editor insertion point.

The existing CLIM type lattice, command tables, translators, gestures, pointer documentation, and commands can remain the action-dispatch layer.

## 1. Presenting one specific object

For an exact individual object, CLIM can use a singleton presentation type:

```lisp
(defun present-specific-object (object stream)
  (with-output-as-presentation
      (stream object `(member ,object) :single-box t)
    (write-string (object-label object) stream)))
```

This is appropriate when the identity of the object is itself part of the input contract.

For most object-specific actions, however, a stable type plus a translator tester is cleaner:

```lisp
(define-presentation-to-command-translator archive-current-document
    (document com-archive-document workspace
      :gesture :select
      :documentation "Archive this document"
      :tester ((object frame)
               (and (eq object (current-document frame))
                    (archivable-p object))))
    (object)
  (list object))
```

Here:

- `document` remains a reusable semantic type;
- `eq` restricts the action to one particular object;
- `archivable-p` reflects current object state;
- the frame can contribute contextual policy.

Translator applicability already takes the presentation type, gesture, type parameters, and tester into account. citeturn628722view2

Creating one new presentation-type definition per object would usually be undesirable. It would grow the type namespace, complicate subtype reasoning, and tie ephemeral identity to global definitions. Singleton types, testers, or occurrence wrappers are preferable.

## 2. Different presentations of the same object occurrence

The same domain object may occur several times on screen with different meanings:

- one occurrence is the source of an operation;
- another is a target;
- one is selected;
- one is read-only;
- one represents the object in a historical revision.

In that case, present an **occurrence object**, not necessarily the raw domain object:

```lisp
(defclass document-occurrence ()
  ((document
    :initarg :document
    :reader occurrence-document)
   (id
    :initarg :id
    :reader occurrence-id)))

(defclass source-document-occurrence
    (document-occurrence)
  ())

(defclass target-document-occurrence
    (document-occurrence)
  ())

(defun present-document-occurrence (occurrence stream)
  (with-output-as-presentation
      (stream occurrence
              (class-name (class-of occurrence))
              :single-box t)
    (write-string
     (document-title
      (occurrence-document occurrence))
     stream)))
```

Commands can then specialize on the semantic occurrence:

```lisp
(define-presentation-to-command-translator choose-source-document
    (source-document-occurrence
     com-choose-source
     workspace
     :gesture :select)
    (occurrence)
  (list (occurrence-document occurrence)))
```

This separates three things that are often incorrectly conflated:

```text
domain object       the document
occurrence          this appearance of the document
presentation type   the role of this appearance
```

McCLIM’s Clouseau inspector uses essentially this pattern: separate occurrences of the same inspected object have independent state and style, and the state class determines the presentation type and applicable commands. citeturn286033view3

A role slot is another option:

```lisp
(defclass object-occurrence ()
  ((object :initarg :object :reader occurrence-object)
   (role   :initarg :role   :reader occurrence-role)
   (id     :initarg :id     :reader occurrence-id)))
```

Then use a common occurrence presentation type and translator testers based on `occurrence-role`. Classes are more appropriate when the roles form a real hierarchy; a slot is better for a small, dynamic set of labels.

## 3. Dynamic object types and capabilities

There are two materially different kinds of “dynamic type.”

### Dynamic semantic classification

An object may satisfy a capability such as:

```text
editable
archivable
linkable
drop-target for image
convertible to date
```

When the capability should participate in CLIM’s type lattice, define a parameterized presentation type:

```lisp
(define-presentation-type capable-object (capability)
  :description "capable object")

(define-presentation-method presentation-typep
    (object (type capable-object))
  (supports-capability-p object capability))
```

A presentation can then have a runtime-generated type specifier:

```lisp
(with-output-as-presentation
    (stream object '(capable-object :archivable))
  (draw-object object stream))
```

A complete parameterized presentation type must also implement appropriate `presentation-subtypep` behavior. For example, a capability registry might say that `:fully-editable` implies `:renameable`. CLIM requires parameter-aware `presentation-typep` and `presentation-subtypep` methods for parameterized types; its `inherit-from` form is intentionally restricted and should not contain arbitrary dynamic tests. citeturn628722view1

### Dynamic action availability

Current permissions, selection state, application mode, locks, or network state usually do **not** belong in the type hierarchy. Put them in a translator tester:

```lisp
:tester ((object frame)
         (and (supports-capability-p object :archivable)
              (archive-mode-p frame)
              (user-may-archive-p frame object)
              (not (object-locked-p object))))
```

A useful division is:

| Requirement | CLIM mechanism |
|---|---|
| Exact individual object | `(member object)` or `eq` tester |
| Stable semantic category | Presentation type |
| Parameterized capability | Parameterized presentation type |
| Current permission or mode | Translator `:tester` |
| Different rendering only | View |
| One screen occurrence | Occurrence wrapper/state |
| Writable location | Place or presentation modifier |

Views should describe how something is rendered, not whether it supports a domain operation. CLIM presentation methods can specialize on a view while retaining the same semantic presentation type. citeturn628722view1

## 4. Text selection as a first-class presented object

A selected string alone is generally insufficient. The semantic object should preserve where it came from and whether it is still valid:

```lisp
(defclass text-selection ()
  ((document
    :initarg :document
    :reader selection-document)
   (start
    :initarg :start
    :reader selection-start)
   (end
    :initarg :end
    :reader selection-end)
   (revision
    :initarg :revision
    :reader selection-revision)
   (text
    :initarg :text
    :reader selection-text)))
```

The revision token prevents an action from applying stale offsets after the document changes.

When the editor can express its selection highlight as recorded output, it can be an ordinary presentation:

```lisp
(defun present-text-selection (selection stream)
  (with-output-as-presentation
      (stream selection 'text-selection
              :single-box t)
    (write-string (selection-text selection) stream)))
```

For a native editor or gadget whose selection is not part of an output history, the editor should expose the same object through a semantic-source adapter.

An action can create a new domain object from the selection:

```lisp
(define-presentation-to-command-translator
    create-task-from-selection
    (text-selection
     com-create-task-from-selection
     workspace
     :gesture :select
     :documentation "Create a task from this text"
     :tester ((object frame)
              (and
               (= (selection-revision object)
                  (document-revision
                   (selection-document object)))
               (valid-task-title-p
                (selection-text object)))))
    (object)
  (list object))
```

The command performs the actual creation:

```lisp
(define-command
    (com-create-task-from-selection
     :command-table workspace
     :name "Create task from selection")
    ((selection 'text-selection))
  (let ((task
          (make-instance
           'task
           :title (selection-text selection)
           :source-document
           (selection-document selection)
           :source-range
           (cons (selection-start selection)
                 (selection-end selection)))))
    (add-task-to-workspace
     *application-frame*
     task)))
```

This arrangement is important. Translator bodies can be evaluated during applicability checking in some translation situations, so they should perform pure conversion, validation, or argument construction—not persistent mutation, database writes, or object registration. Commands should commit those effects. citeturn628722view2turn844423view4

The same selection can support several interpretations:

```text
text-selection → task draft
text-selection → URL
text-selection → date
text-selection → person name
text-selection → search query
```

Ambiguity should produce a menu or completion interaction rather than silently selecting one constructor.

## 5. Model widgets and editable selections as places

For assignment operations, the more powerful abstraction is not merely “object” but **place**:

```text
object = a value
place  = a location that may contain a value
```

Examples include:

- an object slot;
- a text-selection range that can be replaced;
- a text-field gadget’s value;
- a table cell;
- a canvas property;
- an insertion point;
- a selected list position.

A minimal protocol could be:

```lisp
(defclass semantic-place () ())

(defgeneric place-value (place))
(defgeneric (setf place-value) (new-value place))
(defgeneric place-value-type (place))
(defgeneric place-mutable-p (place))
(defgeneric place-valid-p (place))
```

A widget-backed place:

```lisp
(defclass gadget-place (semantic-place)
  ((gadget
    :initarg :gadget
    :reader place-gadget)
   (type
    :initarg :type
    :reader place-declared-type)))

(defmethod place-value ((place gadget-place))
  (gadget-value (place-gadget place)))

(defmethod (setf place-value)
    (new-value (place gadget-place))
  (setf (gadget-value (place-gadget place))
        new-value))

(defmethod place-value-type ((place gadget-place))
  (place-declared-type place))

(defmethod place-mutable-p
    ((place gadget-place))
  t)
```

A writable text range could similarly implement `(setf place-value)` by replacing the range, after checking its revision.

This supports general actions such as:

```text
copy object to place
move object to place
swap place values
replace selection
instantiate target type here
convert then assign
```

Clouseau provides a strong precedent. It represents slots, list elements, array elements, hash-table entries, and similar locations as first-class places with commands separate from the objects currently contained in them. It can present the place and its child value independently. citeturn286033view1turn286033view2

For example, a generic assignment command could conceptually perform:

```lisp
(defun assign-to-place (value place)
  (unless (place-valid-p place)
    (error "The target place is stale."))
  (unless (place-mutable-p place)
    (error "The target place is immutable."))
  (unless (presentation-typep
           value
           (place-value-type place))
    (error "The value is not acceptable to the target."))
  (setf (place-value place) value))
```

This gives drag-and-drop a precise semantic interpretation:

```text
drag source object presentation
onto target place presentation
→ command with (source-value target-place)
```

## 6. Treating gadgets as presentations

Standard CLIM gadgets primarily use callbacks. A push button has an activation callback; value gadgets have value-change callbacks. Gadgets can be distinguished through their client, ID, or installed callback function. citeturn844423view3

To integrate gadgets with presentation semantics, introduce a binding object:

```lisp
(defclass semantic-binding ()
  ((source
    :initarg :source
    :reader binding-source)
   (object
    :initarg :object
    :reader binding-object)
   (type
    :initarg :type
    :reader binding-type)
   (occurrence
    :initarg :occurrence
    :reader binding-occurrence)
   (revision
    :initarg :revision
    :reader binding-revision)
   (modifier
    :initarg :modifier
    :initform nil
    :reader binding-modifier)))
```

A gadget callback then produces a semantic gesture rather than directly containing application logic:

```lisp
(make-pane
 'push-button
 :label "Archive"
 :client frame
 :id 'archive
 :activate-callback
 (lambda (gadget)
   (dispatch-semantic-gesture
    (semantic-binding-for gadget)
    :activate
    (gadget-client gadget))))
```

`dispatch-semantic-gesture` is the proposed extension. It should:

1. Resolve the gadget to a semantic binding.
2. Find actions whose source type matches `binding-type`.
3. Run their testers in the current frame and command-table context.
4. Construct a command and its arguments.
5. Execute the command through the application’s normal command path.

There are two implementation strategies.

### Shared action registry

Define actions once:

```lisp
(define-semantic-action archive-document
  (:from document
   :command com-archive-document
   :gesture :activate
   :tester archivable-in-current-frame-p)
  (document)
  (list document))
```

The macro can generate:

- a CLIM presentation-to-command translator;
- a gadget callback adapter;
- a text-selection context-menu item;
- pointer documentation;
- a drag/drop handler.

This is the most portable approach because it does not require manufacturing implementation-specific output records.

### Presentation proxies

A deeper McCLIM extension could create presentation-like proxy objects for gadgets and selections, then use CLIM’s low-level translator functions. CLIM exposes operations for finding, testing, documenting, invoking, and displaying menus of applicable presentation translators. citeturn844423view4

The proxy should satisfy the presentation protocol and preserve:

```text
presentation-object
presentation-type
source sheet
event coordinates
modifier
occurrence identity
```

This approach gives gadgets the full standard translator machinery, but it is more tightly coupled to presentation/output-record internals.

## 7. Creation targets and blank areas

Creating a new object does not always require an existing source object. CLIM already defines `blank-area` as a presentation source, including coordinates, specifically for commands applicable where no ordinary presentation exists. citeturn844423view5

For example:

```lisp
(define-presentation-to-command-translator
    create-node-here
    (blank-area
     com-create-node
     workspace
     :documentation "Create a node here")
    (x y)
  (list x y))
```

The command can then create the persistent node:

```lisp
(define-command
    (com-create-node
     :command-table workspace
     :name "Create node")
    ((x 'real) (y 'real))
  (add-node
   *application-frame*
   (make-instance 'node :x x :y y)))
```

The same principle generalizes:

```text
blank area + coordinates → new spatial object
text selection           → new semantic object
widget value              → new configured object
existing object           → derived object
object + target place     → assignment
```

## 8. A compact extension protocol

A practical library could center on four protocols:

```lisp
(defgeneric semantic-binding-at-event (source event))
(defgeneric applicable-semantic-actions (binding frame gesture))
(defgeneric invoke-semantic-action (action binding frame event))
(defgeneric replace-semantic-value (binding new-value))
```

Its execution model would be:

```text
physical event
    ↓
source adapter
    ↓
semantic binding
    ↓
presentation-type and tester matching
    ↓
translator or constructor
    ↓
command arguments
    ↓
command commits mutation
    ↓
redisplay
```

The important rules are:

1. **Keep presentation types stable.** Use parameters, wrappers, or testers instead of generating a global type symbol for every object.
2. **Separate object identity from occurrence identity.** One domain object may have several independent interactive representations.
3. **Represent writable targets as places.** This makes text ranges, fields, slots, and cells participate in the same assignment operations.
4. **Keep translators pure.** Persistent creation and mutation belong in commands.
5. **Give selections provenance and revisions.** Raw offsets or raw strings become unsafe as soon as the source document changes.
6. **Use views for appearance and types for meaning.**
7. **Do not parse selected text with unrestricted `read` or `eval`.** Constructors should use explicit parsers and validation.
8. **Compile one semantic action definition into several front ends.** A visible presentation, push button, menu item, keyboard gesture, and text-selection action should invoke the same command rather than duplicate application logic.

The resulting principle is:

> A presentation is a typed semantic binding between an application concept and an interactive locus—not merely a piece of recorded graphical output.

That formulation preserves CLIM’s command-oriented model while extending it naturally to gadgets, selections, editable locations, object constructors, and dynamically changing interaction roles.


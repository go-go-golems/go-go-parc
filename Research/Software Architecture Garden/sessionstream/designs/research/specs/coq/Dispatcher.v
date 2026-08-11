(** * Dispatcher.v

    Abstract transition kernel of the Bounded Asynchronous Observer
    Dispatcher, with inductive invariant proofs.

    This is the same Step relation as the TLA+ model and the Lean
    development, stripped of scheduling detail:

      submitAccepted / submitDropped / submitRejected
      closeFirst / closeAgain
      deliver / workerExit / waitReturn

    Proved for ARBITRARY capacity, item type, and run length:
      - queue bound                       (D1)
      - admitted = offered ++ queue       (D3 shape, I6)
      - close at most once, sticky        (D6, I4)
      - no queue growth after close       (D7, I2/I5)
      - drain completeness at worker exit (D8, I7)
      - wait only after worker exit       (D9)
      - dropped monotone                  (I8)

    The concurrency justification (why real Go executions refine this
    sequential kernel) lives in the TLA+ model and the study document:
    the admission mutex serializes submit/close decisions, so any
    observed interleaving is a legal sequence of these steps. *)

From Coq Require Import Lists.List Arith.Arith Bool.Bool Lia.
Import ListNotations.

Section Dispatcher.

Context {Item : Type}.
Variable cap : nat.

(** ** State and transition relation *)

Record state : Type := mkState {
  queue       : list Item;
  admitted    : list Item;
  offered     : list Item;
  dropped     : nat;
  closing     : bool;
  close_count : nat;
  worker_done : bool;
  waited      : bool
}.

Definition init_state : state :=
  mkState [] [] [] 0 false 0 false false.

Inductive step : state -> state -> Prop :=
| step_submit_accepted : forall (s : state) (x : Item),
    closing s = false ->
    length (queue s) < cap ->
    step s (mkState (queue s ++ [x]) (admitted s ++ [x]) (offered s)
                    (dropped s) (closing s) (close_count s)
                    (worker_done s) (waited s))
| step_submit_dropped : forall (s : state) (x : Item),
    closing s = false ->
    ~ length (queue s) < cap ->
    step s (mkState (queue s) (admitted s) (offered s)
                    (S (dropped s)) (closing s) (close_count s)
                    (worker_done s) (waited s))
| step_submit_rejected : forall (s : state) (x : Item),
    closing s = true ->
    step s s
| step_close : forall (s : state),
    closing s = false ->
    step s (mkState (queue s) (admitted s) (offered s)
                    (dropped s) true (S (close_count s))
                    (worker_done s) (waited s))
| step_close_again : forall (s : state),
    closing s = true ->
    step s s
| step_deliver : forall (s : state) (x : Item) (rest : list Item),
    queue s = x :: rest ->
    step s (mkState rest (admitted s) (offered s ++ [x])
                    (dropped s) (closing s) (close_count s)
                    (worker_done s) (waited s))
| step_worker_exit : forall (s : state),
    closing s = true ->
    queue s = [] ->
    step s (mkState (queue s) (admitted s) (offered s)
                    (dropped s) (closing s) (close_count s)
                    true (waited s))
| step_wait_return : forall (s : state),
    worker_done s = true ->
    step s (mkState (queue s) (admitted s) (offered s)
                    (dropped s) (closing s) (close_count s)
                    (worker_done s) true).

Inductive reachable : state -> Prop :=
| reachable_init : reachable init_state
| reachable_step : forall s t, reachable s -> step s t -> reachable t.

(** ** The invariant bundle

    The key strengthening clause is [inv_shape]: the admitted history
    always factors as [offered ++ queue].  Order-correctness (D3) and
    drain completeness (D8) both follow from it. *)

Record inv (s : state) : Prop := {
  inv_bound      : length (queue s) <= cap;
  inv_shape      : offered s ++ queue s = admitted s;
  inv_close_once : close_count s <= 1;
  inv_closed_iff : closing s = true <-> close_count s = 1;
  inv_exit       : worker_done s = true -> closing s = true /\ queue s = [];
  inv_wait       : waited s = true -> worker_done s = true
}.

Lemma reachable_inv : forall s, reachable s -> inv s.
Proof.
  intros s H. induction H as [| s t Hr IH Hst].
  - (* reachable_init *)
    constructor; simpl.
    + lia.
    + reflexivity.
    + lia.
    + split; intros Hc; discriminate Hc.
    + intros Hc; discriminate Hc.
    + intros Hc; discriminate Hc.
  - (* reachable_step *)
    destruct IH as [Hb Hs Hc Hi Hw Hwt].
    destruct Hst as
      [s0 x Hcl Hcap | s0 x Hcl Hfull | s0 x Hcl | s0 Hcl
      |s0 Hcl | s0 x rest Hq | s0 Hcl Hq | s0 Hd];
      simpl in *.
    + (* submit_accepted *)
      constructor; simpl.
      * rewrite length_app. simpl. lia.
      * rewrite app_assoc. rewrite Hs. reflexivity.
      * exact Hc.
      * split; intros Hc1.
        -- congruence.
        -- apply (proj2 Hi) in Hc1. congruence.
      * intros Hd. destruct (Hw Hd) as [Hc2 Hq2]. congruence.
      * exact Hwt.
    + (* submit_dropped *)
      constructor; simpl.
      * exact Hb.
      * exact Hs.
      * exact Hc.
      * split; intros Hc1.
        -- congruence.
        -- apply (proj2 Hi) in Hc1. congruence.
      * intros Hd. destruct (Hw Hd) as [Hc2 Hq2]. congruence.
      * exact Hwt.
    + (* submit_rejected : identity step *)
      constructor; assumption.
    + (* close *)
      assert (Hc0 : close_count s0 = 0).
      { assert (Hn1 : close_count s0 <> 1).
        { intros Heq. apply (proj2 Hi) in Heq. congruence. }
        lia. }
      constructor; simpl.
      * exact Hb.
      * exact Hs.
      * lia.
      * split; intros _.
        -- rewrite Hc0. reflexivity.
        -- reflexivity.
      * intros Hd. destruct (Hw Hd) as [Hc2 Hq2].
        split; [reflexivity | exact Hq2].
      * exact Hwt.
    + (* close_again : identity step *)
      constructor; assumption.
    + (* deliver *)
      constructor; simpl.
      * rewrite Hq in Hb. simpl in Hb. lia.
      * rewrite <- app_assoc. simpl. rewrite <- Hq. exact Hs.
      * exact Hc.
      * exact Hi.
      * intros Hd. destruct (Hw Hd) as [Hc2 Hq2].
        rewrite Hq2 in Hq. discriminate Hq.
      * exact Hwt.
    + (* worker_exit *)
      constructor; simpl.
      * exact Hb.
      * exact Hs.
      * exact Hc.
      * exact Hi.
      * intros _. split; [exact Hcl | exact Hq].
      * intros _. reflexivity.
    + (* wait_return *)
      constructor; simpl.
      * exact Hb.
      * exact Hs.
      * exact Hc.
      * exact Hi.
      * exact Hw.
      * intros _. exact Hd.
Qed.

(** ** Single-step and multi-step monotonicity lemmas *)

Lemma step_dropped_mono : forall s t,
  step s t -> dropped s <= dropped t.
Proof.
  intros s t H. destruct H; simpl; lia.
Qed.

Lemma step_closing_sticky : forall s t,
  step s t -> closing s = true -> closing t = true.
Proof.
  intros s t H. destruct H; simpl; intros Hc;
    first [congruence | assumption | reflexivity].
Qed.

Lemma step_closed_shrinks : forall s t,
  step s t -> closing s = true ->
  length (queue t) <= length (queue s).
Proof.
  intros s t H. destruct H; simpl; intros Hc; try congruence; try lia.
  - (* deliver *) rewrite H. simpl. lia.
Qed.

Inductive steps : state -> state -> Prop :=
| steps_refl : forall s, steps s s
| steps_cons : forall s t u, step s t -> steps t u -> steps s u.

Lemma steps_dropped_mono : forall s t,
  steps s t -> dropped s <= dropped t.
Proof.
  intros s t H. induction H as [| s t u Hst Hss IH].
  - lia.
  - assert (dropped s <= dropped t) by (eapply step_dropped_mono; eauto).
    lia.
Qed.

Lemma steps_closing_sticky : forall s t,
  steps s t -> closing s = true -> closing t = true.
Proof.
  intros s t H. induction H as [| s t u Hst Hss IH]; intros Hc.
  - exact Hc.
  - apply IH. eapply step_closing_sticky; eauto.
Qed.

Lemma steps_closed_shrinks : forall s t,
  steps s t -> closing s = true ->
  length (queue t) <= length (queue s).
Proof.
  intros s t H. induction H as [| s t u Hst Hss IH]; intros Hc.
  - lia.
  - assert (Hct : closing t = true) by (eapply step_closing_sticky; eauto).
    assert (Hle : length (queue t) <= length (queue s))
      by (eapply step_closed_shrinks; eauto).
    specialize (IH Hct). lia.
Qed.

(** ** Exported correctness theorems *)

Theorem queue_bound : forall s,
  reachable s -> length (queue s) <= cap.
Proof. intros s H. apply (reachable_inv _ H). Qed.

Theorem admitted_factors : forall s,
  reachable s -> admitted s = offered s ++ queue s.
Proof.
  intros s H. symmetry. apply (reachable_inv _ H).
Qed.

Theorem offered_prefix : forall s,
  reachable s -> exists rest, admitted s = offered s ++ rest.
Proof.
  intros s H. exists (queue s). apply admitted_factors. exact H.
Qed.

Theorem close_once : forall s,
  reachable s -> close_count s <= 1.
Proof. intros s H. apply (reachable_inv _ H). Qed.

Theorem closed_sticky_reachable : forall s t,
  reachable s -> steps s t -> closing s = true -> closing t = true.
Proof. intros s t Hr Hss. apply (steps_closing_sticky _ _ Hss). Qed.

Theorem no_send_after_close : forall s t,
  reachable s -> steps s t -> closing s = true ->
  length (queue t) <= length (queue s).
Proof. intros s t Hr Hss. apply (steps_closed_shrinks _ _ Hss). Qed.

Theorem drain_complete : forall s,
  reachable s -> worker_done s = true ->
  offered s = admitted s /\ closing s = true.
Proof.
  intros s H Hd. destruct (reachable_inv _ H) as [Hb Hs Hc Hi Hw Hwt].
  destruct (Hw Hd) as [Hcl Hq]. split; [| exact Hcl].
  rewrite <- Hs. rewrite Hq. rewrite app_nil_r. reflexivity.
Qed.

Theorem wait_after_exit : forall s,
  reachable s -> waited s = true -> worker_done s = true.
Proof.
  intros s H Hw2. apply (reachable_inv _ H). exact Hw2.
Qed.

Theorem dropped_monotone_reachable : forall s t,
  reachable s -> steps s t -> dropped s <= dropped t.
Proof. intros s t Hr Hss. apply (steps_dropped_mono _ _ Hss). Qed.

End Dispatcher.

(** Audit: the development must be axiom-free. *)
Print Assumptions queue_bound.
Print Assumptions admitted_factors.
Print Assumptions drain_complete.
Print Assumptions no_send_after_close.
Print Assumptions wait_after_exit.
Print Assumptions close_once.
Print Assumptions dropped_monotone_reachable.

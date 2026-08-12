---
title: CNC Spindle Speed Control - Integrators, Dead Zones and Feedforward in the Carvera Firmwares
aliases:
  - spindle PID case study
  - velocity-form PID pitfalls
  - Carvera spindle control
tags:
  - article
  - control-theory
  - cnc
  - firmware
  - pid
status: active
type: article
created: 2026-08-12
repo: /home/manuel/workspaces/2026-08-11/cnc-control-dropcut/dropcut-studio/makera-z1-cli
---

# CNC Spindle Speed Control — Integrators, Dead Zones and Feedforward in the Carvera Firmwares

This note preserves what an evening of hardware observation and firmware
reading taught about closed-loop spindle speed control, using two real,
shipping implementations as the material: the stock Makera/Carvera firmware's
`PWMSpindleControl` (what a Makera Z1 runs today) and the community fork's
opt-in `PIDPWMSpindleControl`. The two modules control the same class of
plant and differ in almost every decision a control implementer has to make,
which makes them an unusually clean paired case study: one shows the failure
modes, the other shows the standard remedies, and both are small enough to
read in full.

The triggering observation, from the [[PROJ - Makera Z1 Control - What the Machine Does Not Say|z1ctl bring-up]]:
commanded to 1000 RPM, the Z1's spindle spins up, stops, spins up, stops,
indefinitely. Commanded to 10000 RPM it regulates correctly but takes
noticeably long to get there. Both behaviours fall out of six lines of
firmware, and neither is a bug in the colloquial sense — they are properties
of a specific, common control structure meeting a specific, common actuator
nonlinearity.

> [!summary]
> - The stock loop accumulates `P·error` into the PWM duty every tick. In
>   velocity (incremental) form, that term is **integral** action regardless
>   of its name: the stock controller is a pure integrator, which explains
>   both the slow ramp and the limit cycle at low targets.
> - A pure integrator meeting an actuator dead zone produces a permanent
>   oscillation — the limit cycle is structural, and no gain value removes
>   it.
> - The community module applies the two standard remedies: **static
>   feedforward** (an affine inverse model of the plant, whose offset term
>   jumps the dead zone) and a true positional PID with **conditional
>   integration** for anti-windup.
> - Config names outlive control laws. The stock firmware loads, prints and
>   accepts `control_I` at runtime while using it nowhere, and its `P` and
>   `D` terms act as I and P respectively. Reading the update loop is the
>   only way to know what a gain does.

## Why this note exists

Spindle speed regulation is the least discussed control loop on a hobby-class
CNC machine — position control gets the attention — yet it is the loop most
likely to misbehave visibly, because its actuator (a PWM-driven brushless
motor) has a hard nonlinearity at low speed and its load (cutting) is a
genuine disturbance. The two Carvera implementations bracket the design
space: the simplest thing that mostly works, and the textbook structure that
fixes its failure modes. Everything below is grounded in vendored source
with exact paths, and the observed behaviour is from a real Z1 on firmware
1.0.15.

## The plant and the problem

The controlled system, common to both implementations:

- **Actuator:** a hardware PWM output driving the spindle motor controller;
  commanded duty in [0, `max_pwm`]. The motor cannot sustain rotation below
  some minimum speed, and starting it requires more duty than keeping it
  turning — a **dead zone** plus hysteresis at the bottom of the range.
- **Sensor:** a pulse input (`pulses_per_rev`, default 1) timed by interrupt.
  One pulse per revolution at, say, 6000 RPM is one measurement per 10 ms —
  the feedback is quantised and noisy at exactly the rates where control is
  interesting.
- **Loop rate:** a 100 Hz ticker (`UPDATE_FREQ 100`), with the control
  update decimated to every 5th tick (20 Hz) in the stock module.
- **Disturbance:** cutting load, which can shed a large fraction of free-run
  speed; the controller's job is to hold RPM through it.

The stock module low-passes the RPM estimate with an exponential filter
whose decay is `1/(UPDATE_FREQ · smoothing_time)` (default τ = 0.1 s). The
community module additionally replaces the single-interval measurement with
a ring of the last `pulses_per_rev` pulse intervals summed — averaging over
exactly one revolution, which cancels the once-per-rev asymmetry of the
sensor before the filter ever sees it.

## The stock loop, read precisely

The whole control law (`stock-carvera-firmware/src/modules/tools/spindle/
PWMSpindleControl.cpp`, update loop):

```cpp
float error   = target_rpm * (factor / 100) - current_rpm;
float acc_pwm = control_P_term * error;
if (CARVERA_AIR == THEKERNEL->factory_set->MachineModel) {
    if (target_change_count > UPDATE_FREQ * 5) {          // suppressed ~5s after a target change
        acc_pwm += control_D_term * (error - prev_error);
    }
}
current_pwm_value = confine(current_pwm_value + acc_pwm, 0.0f, max_pwm);
```

The decisive detail is the last line: the computed term is **added to the
accumulated duty**, not written to it. This is the velocity (incremental)
form of a discrete controller, and in that form the roles shift by one
derivative relative to the familiar positional form:

| Term in code | Acts on | Positional-form equivalent |
|---|---|---|
| `control_P_term · e` accumulated | error | **integral** action |
| `control_D_term · Δe` accumulated | error difference | **proportional** action |
| (would be `· Δ²e`) | second difference | derivative action — implemented nowhere |

So the stock Z1/C1 controller is a **pure integrator** (gain 0.0001
duty/RPM·tick by default), and the Carvera Air variant is a **PI**
controller. `control_I` is loaded from config, printed by `M958`, settable
at runtime — and used in no expression; `current_I_value` is only ever
zeroed. The configuration surface survived from the original Smoothieware
module, which implemented a genuine positional PID; the fork replaced the
law and kept the knobs.

### Consequence 1: the slow ramp

A pure integrator's output can only walk. From standstill to the duty that
sustains 10000 RPM (~0.5 by the community module's feedforward constants),
the duty must accumulate through every intermediate value at a rate bounded
by `P · error`. Large error at the start makes the first phase brisk, but as
RPM approaches target the error — and therefore the step size — collapses,
producing the long creep into the setpoint that is visible from the
operator's chair. Proportional action would supply an immediate,
error-sized contribution; there is none.

### Consequence 2: the limit cycle at low targets

Commanded to 1000 RPM — below the motor's minimum sustainable speed — the
system cannot converge, and the specific way it fails is characteristic:

1. Motor stopped, error = +1000. Duty integrates upward from zero.
2. Nothing happens until duty crosses the starting threshold; by then the
   accumulated duty spins the motor well above 1000 RPM.
3. Error is now strongly negative; the integrator walks the duty back down.
4. Duty falls below the *sustaining* threshold; the motor stops.
5. Error is +1000 again. Repeat, forever.

The spin-up/stop/spin-up cycle observed on hardware is this loop executing
at the timescale of the integrator gain. It is worth being precise about
what would and would not fix it: no value of the integral gain removes the
cycle (it only changes its period), and no controller of any structure can
regulate a speed the motor cannot physically sustain. What better structure
*can* do is fail legibly — reach the dead-zone boundary and hold, rather
than oscillate — and regulate correctly at every speed the motor can hold.

### Consequence 3: the setpoint-kick patch

In velocity form, proportional action appears as a term on Δerror — and a
setpoint step makes Δerror spike for one sample, kicking the actuator. The
textbook remedies are setpoint weighting or taking the term from the
measurement rather than the error. The Air branch instead disables its
Δerror term for roughly five seconds after any target change, with a
comment explaining the symptom ("to rapid speed up/down"). It works, and it
reads as what it is: an empirical patch applied to one machine model,
gated by `if (CARVERA_AIR == MachineModel)` so no shipped machine's
behaviour changed. Model-gated control changes are risk containment;
the cost is a codebase where the control law depends on a factory enum.

### The supervisory layer

Above the loop sits stall protection: if the target exceeds
`stall_count_rpm` (8000) while measured RPM stays below `stall_alarm_rpm`
(5000) for `stall_s` (100 s), the firmware raises a spindle-stall alarm
(reset-class halt). Two things follow. First, protection is not control —
at a 1000 RPM target the detector never arms, which is why the limit cycle
runs indefinitely without an alarm. Second, thresholds encode the intended
envelope: the designers expected regulation targets above 8000 and treated
sub-5000 as failure, which independently corroborates the low end of the
usable range.

## The community module: the standard remedies

The fork's `PIDPWMSpindleControl` (selected by `spindle.type pid_pwm`;
default remains the stock loop) inherits the module and replaces the law
(`carvera-community-firmware/src/modules/tools/spindle/
PIDPWMSpindleControl.cpp`):

```cpp
float error = target_rpm * (factor / 100) - current_rpm;
if (current_pwm_value < 1.0f || error <= 0) {              // conditional integration
    current_I_value += control_I_term * error / UPDATE_FREQ;
}
float new_pwm = ff_slope * target_rpm + ff_offset;         // static feedforward
new_pwm += control_P_term * error;                          // true proportional
new_pwm += current_I_value;                                 // true integral
new_pwm += control_D_term * (error - prev_error) * UPDATE_FREQ;  // true derivative
current_pwm_value = confine(new_pwm, 0.0f, max_pwm);
```

This is the positional form, so the names mean what they say, and three
standard techniques appear:

**Static feedforward as an inverse plant model.** `ff_slope · target +
ff_offset` (defaults 4.85e-5 duty/RPM and 0.02 duty) is an affine fit of
the steady-state duty-vs-RPM curve. The controller starts at the duty the
target *will* need — at 10000 RPM, ~0.505 immediately, instead of
integrating toward it — and the feedback terms only correct model error and
load disturbance. The offset term is the dead-zone treatment: 2% duty is
applied the moment any nonzero target exists, pre-loading the actuator to
the edge of its dead band. Division of labour is the principle: feedforward
handles the operating point, feedback handles what feedforward cannot
predict.

**Conditional integration as anti-windup.** The integrator accumulates only
when the output is unsaturated (`current_pwm_value < 1.0`) or the error is
negative. Without this, a long saturated spin-up winds the integral term
far past what steady state needs, and the stored excess must be *unwound*
through overshoot after the target is reached. Conditional integration is
the crudest effective anti-windup; back-calculation is the refined
alternative, and nothing here needs it.

**Better measurement before better control.** The per-revolution
pulse-interval ring removes once-per-rev measurement asymmetry ahead of the
filter. Derivative action is only usable at all because the measurement was
cleaned up first — D on a noisy, quantised RPM estimate amplifies exactly
the noise the EMA was hiding.

The fork also adds a `VESCSpindleControl`, which relocates the entire speed
loop into a dedicated motor controller over serial — the architectural
endpoint of this progression: when the actuator vendor's firmware runs a
well-tuned loop at kilohertz rates, the CNC firmware's job reduces to
sending a target and reading telemetry.

## Tuning methodology, grounded in these loops

The generic procedure, with the machine-specific levers this project now
exposes (`z1ctl spindle report` → `M957` prints current/target RPM and PWM
duty; `z1ctl spindle pid` → `M958` sets gains at runtime, reset at power
cycle):

1. **Identify the form before touching a knob.** Read the update loop and
   classify each term by what it multiplies and where it lands. On the
   stock Z1 there is exactly one live gain, and it is integral action; its
   trade is ramp speed against overshoot, nothing else.
2. **Instrument, then step.** Log `M957` (or the status report's `S:`
   current/target pair) through target steps. Rise time, overshoot, and
   ring count are the whole state of knowledge.
3. **Tune an integrator by doubling.** Raise the gain by factors of two
   until the response rings around the target, then back off one step. The
   best pure-integrator gain sits just below the ringing threshold; there
   is no windup guard in the stock loop, so overshoot after long ramps is
   the expected artefact, not a mystery.
4. **Calibrate feedforward from steady states, not dynamics.** Hold several
   RPM targets, record converged duty at each, fit the affine model: slope
   and offset drop out. This is a five-minute measurement that replaces the
   integrator's entire climb.
5. **Find the physical floor by bisection and encode it.** The dead-zone
   boundary is a property of the motor, not the controller. Locate it once
   (the report command shows duty sawing and RPM collapsing when below it)
   and make the *tool* refuse or warn below it — the firmware will not.
6. **Persist deliberately.** Runtime gains vanish at power-off; writing
   `spindle.control_P` to config is a separate, explicit act after the
   value has survived several sessions.

## Common failure modes, named

| Failure | Mechanism | Where seen | Remedy |
|---|---|---|---|
| Limit cycle at low target | integrator + actuator dead zone | Z1 at S1000, measured | feedforward offset; refuse/warn below the physical floor |
| Sluggish approach | pure-I output can only walk | Z1 at S10000, measured | proportional action or feedforward slope |
| Overshoot after long ramp | integration during saturation | predicted by structure | conditional integration / back-calculation |
| Setpoint kick | Δerror spike in velocity form | Air branch, patched by suppression window | setpoint weighting; derivative-on-measurement |
| Gain names lie | config surface outlives the law | `control_I` dead; P acts as I; D acts as P | classify terms from the update loop, never from names |
| Silent unprotected region | supervision thresholds narrower than command range | stall detector arms only above 8000 target | read the thresholds as the intended envelope |

## Working rules

- Classify controller terms by what they multiply and where the result
  lands. Velocity form shifts every role by one derivative; names shift
  nothing.
- An integrator meeting a dead zone limit-cycles by structure. Tuning
  changes the period, never the existence.
- Feedforward is the cheapest large improvement available to any loop whose
  plant has a measurable static curve — and its offset term is the honest
  place to encode an actuator's dead zone.
- Anti-windup is not optional in a loop that saturates during normal
  operation; a spin-up from standstill is a saturation event.
- Protection thresholds document the designer's intended envelope. Read
  them.
- Fix the measurement before adding derivative action.

## References

Vendored, line-citable, in
`dropcut-studio/ttmp/2026/08/11/MZ1-003--motion-and-job-control-with-a-manual-control-ui/vendor/`:

| File | Shows |
|---|---|
| `stock-carvera-firmware/src/modules/tools/spindle/PWMSpindleControl.cpp` | the velocity-form loop, the Air gate, dead `control_I`, smoothing, stall thresholds |
| `stock-carvera-firmware/src/modules/tools/spindle/SpindleControl.cpp` | `M957` telemetry / `M958` runtime gains dispatch |
| `carvera-community-firmware/src/modules/tools/spindle/PIDPWMSpindleControl.cpp` | positional PID + feedforward + conditional integration + per-rev measurement |

Observed behaviour and the tooling used to measure it:
[[PROJ - Makera Z1 Control - What the Machine Does Not Say]] (the bring-up
session), [[PROJ - Makera Z1 Control - Crossing into Motion]] (the motion
architecture that made the experiments safe to run). The `z1ctl` levers:
`spindle report`, `spindle pid --p … --confirm`, `spindle on --rpm …`, with
low targets warned about at every surface.

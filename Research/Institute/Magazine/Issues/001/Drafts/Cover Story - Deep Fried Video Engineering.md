# Deep-Fried Video Engineering

**Generating Gen-Z podcast intros with Remotion: squash-and-stretch rabbits spiraling into black holes, chromatic aberration via CSS drop-shadows, and eerie synthesized drones. A technical love letter to intentionally terrible aesthetics.**

*By the Editors of The Golem Review*

---

There is a rabbit on the screen and it is about to have a very bad day.

For the first eight frames — a quarter of a second at 30 FPS — it squashes. Its horizontal scale inflates to 1.3x while its vertical scale compresses to 0.7x, the classic animator's anticipation beat: something is about to move, but first it gathers itself. The rabbit does not know what is behind it. The audience does. There is a black hole at pixel coordinate (640, 360) and the math is already written.

At frame 8, the pull begins. Over the next 45 frames, the rabbit accelerates along a parameterized path from x=250 to x=640, stretching horizontally to 0.8x and vertically to 1.2x as the speed increases — the elongation of a body under acceleration, as old as the Fleischer brothers. The scale factor simultaneously collapses from 2.5 to 0.1. Spiral rings appear. Particle debris streams inward. The background darkens from 10% gray to 3% gray. Chromatic aberration — red and cyan drop-shadows offset by increasingly aggressive pixel counts — splits the rabbit into trembling afterimages. A synthesized drone, bitcrushed to 4-bit resolution and lowpass-filtered at 800 Hz, rises in volume from 0 to 0.6 as the motion phase passes 0.1.

At frame 53, the rabbit enters the spiral phase. It rotates, shrinks to nearly nothing, and vanishes. The void drone peaks. A deep-fried impact hit — tanh-clipped at distortion amount 5, which means the waveform is a series of brutalized plateaus — slams in at frame 60. Glitch blocks flash. The screen goes black.

The whole thing takes three seconds. It is the intro for a podcast about falling down rabbit holes with ChatGPT, and every pixel of it was generated programmatically by a React component.

---

## I. Why Programmatic Video

The conventional path to a podcast intro involves After Effects, a timeline, keyframes, and a render queue. It works. It has worked for decades. But it produces an artifact — a `.mp4` file — not a program. The intro cannot be parameterized. It cannot accept different text, different durations, different color palettes without manual re-editing. It cannot be version-controlled. It cannot be reviewed in a pull request. It cannot be tested.

Remotion is a React framework that inverts this relationship. A video is a React component. Each frame is a render. The component receives the current frame number via `useCurrentFrame()` and returns JSX that describes what that frame looks like. The result is code that produces video, not video that was produced by a human moving keyframes in a timeline.

This matters for a podcast with recurring segments. The "rabbit hole" concept — a rabbit being sucked into a void — is a template. Different episodes could have different text overlays, different audio, different visual intensity. A programmatic intro is a function call: change the parameters, render again. The source of truth is a TypeScript file, not a binary project file locked in a proprietary application.

The Rabbit Hole project (`003-rabbit-hole/`) contains three compositions:

| Composition | Concept | Duration | Frames |
|---|---|---|---|
| **TheVoid** | Rabbit sucked into black hole, squash-and-stretch | 3.0s | 90 |
| **TikTokTitle** | "RABBITHOLE" text, letter-by-letter bounce reveal | 5.5s | 165 |
| **RabbitHole** | Original laser-eyes version (superseded) | 3.0s | 90 |

The aesthetic is deliberate: Gen-Z deep-fried. Monochrome. Glitchy. Scanlines. Noise overlays. Bitcrushed audio. The visual language of shitposts, ironic memes, and TikTok chaos — applied to a podcast about AI. The ugliness is the point.

This article documents how every effect in the pipeline works, from the mathematical structure of squash-and-stretch animation through the signal-processing chain that produces eerie synthesized audio, to the performance patterns required to make Remotion render it all without choking.

---

## II. The Frame as Unit of Computation

Everything in Remotion starts with `useCurrentFrame()`. The hook returns an integer — 0, 1, 2, ..., 89 for a 90-frame composition — and the component's job is to compute everything about the current visual state from that single number. There is no timeline. There is no stored state between frames. Each frame is a pure function of its index.

```tsx
const frame = useCurrentFrame();
const { fps, width, height, durationInFrames } = useVideoConfig();
```

`useVideoConfig()` provides the composition's metadata: frame rate (30 FPS), dimensions (1280x720), and total duration (90 frames for TheVoid). These values are declared in `Root.tsx` when the composition is registered:

```tsx
<Composition
  id="TheVoid"
  component={TheVoid}
  durationInFrames={90}
  fps={30}
  width={1280}
  height={720}
/>
```

The frame number is the only input. All motion, all visual effects, all audio dynamics are computed from it. This is the key conceptual shift from timeline-based animation: instead of recording keyframes and interpolating between them in an editor, you write a function that maps frame numbers to visual properties. The function is the animation.

The core mapping function is `interpolate()`:

```tsx
const opacity = interpolate(frame, [0, 30], [0, 1]);
```

This maps frame 0 to opacity 0, frame 30 to opacity 1, with linear interpolation between. The function generalizes to multi-stop mappings:

```tsx
const position = interpolate(frame, [0, 15, 30, 45], [300, 250, 500, 640]);
```

Here, the value moves from 300 to 250 (frames 0-15), then accelerates to 500 (frames 15-30), then continues to 640 (frames 30-45). Each segment interpolates linearly between its stops. The motion is piecewise linear — a rough approximation of a smooth curve, but often good enough, and when it's not, easing functions smooth it out.

Without clamping, `interpolate()` extrapolates beyond its defined range. Frame 60 in a `[0, 30]` input range produces a value beyond the output range. In practice, nearly every `interpolate()` call wants clamping:

```tsx
const scale = interpolate(frame, [0, 30], [0, 1], {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});
```

This is so common that forgetting it is the most frequent source of visual bugs in Remotion code. A particle that should have faded to zero opacity instead has negative opacity (clamped to 0 by CSS, so invisible — correct by accident). A scale factor that should stay at 1.0 after the animation ends instead grows to 3.0 and the element distorts. The fix is always the same: add clamping.

---

## III. The Anatomy of a Squash-and-Stretch

The central animation in TheVoid is a squash-and-stretch cycle — the oldest trick in character animation, codified by Disney's Twelve Principles in the 1930s and still the fastest way to make a moving object feel like it has mass, elasticity, and inertia.

The principle: when an object anticipates motion, it compresses along the axis of movement (squash). When it accelerates, it elongates along the axis of movement (stretch). When it decelerates, it compresses again. The volume should remain roughly constant — wider means shorter, taller means thinner.

In TheVoid, the rabbit's entire 90-frame life is parameterized by a single variable, `motionPhase`, which progresses from 0 (rest) to 1 (consumed by void):

```tsx
const anticipationFrames = 8;
const pullFrames = 45;

const motionPhase = interpolate(
  frame,
  [0, anticipationFrames, anticipationFrames + pullFrames, durationInFrames],
  [0, 0.15, 0.8, 1]
);
```

Frames 0-8 map to motionPhase 0-0.15 (anticipation). Frames 8-53 map to 0.15-0.8 (the pull). Frames 53-90 map to 0.8-1.0 (spiral and vanish). The mapping is not linear in time — anticipation is short and slow, the pull is long and accelerating, the spiral is fast.

The squash and stretch factors are then functions of `motionPhase`, not of `frame` directly. This is the layered parameterization pattern: frame -> motionPhase -> squashX/squashY. It allows the timing to be adjusted (change the frame breakpoints) without affecting the shape of the deformation (the squash/stretch values at each phase), and vice versa.

```tsx
const squashX = interpolate(
  motionPhase, [0, 0.1, 0.5, 0.9, 1],
  [1, 1.3, 0.8, 1.2, 2]
);
const squashY = interpolate(
  motionPhase, [0, 0.1, 0.5, 0.9, 1],
  [1, 0.7, 1.2, 0.8, 0.5]
);
```

The five stops describe the deformation through the entire motion:

| motionPhase | squashX | squashY | What's happening |
|---|---|---|---|
| 0.0 | 1.0 | 1.0 | Rest. Rabbit is normal proportions. |
| 0.1 | 1.3 | 0.7 | **Anticipation squash.** Rabbit widens and shortens — gathering itself, compressing like a spring. |
| 0.5 | 0.8 | 1.2 | **Pull stretch.** Rabbit narrows and elongates — accelerating toward the hole, body stretching under the force. |
| 0.9 | 1.2 | 0.8 | **Spaghettification begins.** Rabbit re-widens slightly as it reaches the hole's event horizon. |
| 1.0 | 2.0 | 0.5 | **Consumed.** Extreme horizontal stretch, extreme vertical compression — the rabbit is pulled into an impossibly wide, impossibly flat shape. |

Note the volume approximation: at motionPhase 0.1, squashX * squashY = 1.3 * 0.7 = 0.91. At 0.5, it's 0.8 * 1.2 = 0.96. At 1.0, it's 2.0 * 0.5 = 1.0. The volume is approximately conserved, as the principle requires.

On top of the squash/stretch, the rabbit's overall scale shrinks from 2.5 (looming, close to camera) to 0.1 (nearly invisible, consumed by the void):

```tsx
const rabbitScale = interpolate(motionPhase, [0, 1], [2.5, 0.1]);
```

The final transform combines all three:

```tsx
transform: `scaleX(${rabbitScale * squashX}) scaleY(${rabbitScale * squashY})`
```

At motionPhase 0 (frame 0): scaleX = 2.5 * 1.0 = 2.5, scaleY = 2.5 * 1.0 = 2.5. The rabbit is large and round.

At motionPhase 0.1 (frame ~8): scaleX = ~2.3 * 1.3 = ~3.0, scaleY = ~2.3 * 0.7 = ~1.6. The rabbit bulges outward — fat and squat, like a ball hitting a wall.

At motionPhase 0.5 (frame ~30): scaleX = ~1.2 * 0.8 = ~1.0, scaleY = ~1.2 * 1.2 = ~1.4. The rabbit is tall and thin — a streak of motion.

At motionPhase 1.0 (frame 90): scaleX = 0.1 * 2.0 = 0.2, scaleY = 0.1 * 0.5 = 0.05. The rabbit is an impossibly flat smear — a last glimpse before the void swallows it.

The spatial path follows a similar multi-stop interpolation:

```tsx
const rabbitX = interpolate(motionPhase, [0, 0.1, 0.5, 1], [300, 250, 500, 640]);
const rabbitY = 360 + Math.sin(frame * 0.3) * (20 * (1 - motionPhase));
```

The X path has the anticipation pull-back: the rabbit starts at x=300, retreats to x=250 during the squash (motionPhase 0-0.1), then accelerates through x=500 to x=640 (the hole's center). The Y path adds a sinusoidal wobble — `Math.sin(frame * 0.3) * 20` — that dampens as `motionPhase` approaches 1. The wobble gives the rabbit a sense of struggling against the pull, and its dampening gives the pull a sense of inevitability.

---

## IV. Deep-Fried Visual Effects as CSS

The "deep-fried" aesthetic is a specific visual language originating from internet meme culture: images that have been JPEG-compressed, contrast-boosted, color-shifted, and noise-overlaid until they look like they were rescued from a dumpster behind a screen printing shop. The aesthetic communicates irony, absurdity, and a deliberate rejection of polish.

In motion graphics, the deep-fried look requires several simultaneous effects. Each is implemented as CSS on the Remotion component tree.

### Chromatic Aberration

Real chromatic aberration occurs when a lens fails to focus all wavelengths of light to the same point, producing color fringing at high-contrast edges. The deep-fried version exaggerates this to the point of visual discomfort: red and cyan afterimages offset by multiple pixels.

The implementation uses CSS `drop-shadow`, which creates a colored copy of the element's alpha channel at an offset position:

```tsx
const pulse = (Math.sin(frame * 0.3) + 1) / 2;
const aberration = 2 + pulse * 6;

<div style={{
  filter: `
    drop-shadow(${aberration}px 0 0 rgba(255,0,0,0.5))
    drop-shadow(-${aberration}px 0 0 rgba(0,255,255,0.5))
  `,
}}>
  ���
</div>
```

Two drop-shadows: one red, offset right; one cyan, offset left. The offset distance (`aberration`) oscillates between 2 and 8 pixels, driven by a sinusoidal pulse at frequency 0.3 radians per frame. The result: the rabbit shimmers with red and cyan afterimages that breathe in and out.

Why `drop-shadow` and not `box-shadow`? `box-shadow` creates a shadow of the element's rectangular bounding box. `drop-shadow` creates a shadow of the element's alpha channel — the actual shape of the rendered content. For emoji and text, this produces properly shaped color fringing. For a rectangular `div`, they would be equivalent.

The 0.5 alpha on the shadow colors is important. Full opacity (1.0) would create opaque red and cyan copies that obscure the original element. At 0.5, the copies are translucent — they tint the edges without hiding the content. The visual effect is that the rabbit appears to vibrate between color channels, as if the signal carrying it from screen to eye is degrading.

### Monochrome Palette

All color is eliminated through CSS filter stacking:

```tsx
<AbsoluteFill style={{
  background: `hsl(0, 0%, ${gray}%)`,
  filter: `contrast(${contrast}) grayscale(1)`,
}}>
```

The `grayscale(1)` filter desaturates everything to zero chroma. The contrast multiplier (which increases with `bgIntensity`, itself a function of frame) pushes the midtones toward black and white, increasing the harshness. The background gray value decreases over the animation — the world literally darkens as the void grows stronger.

The monochrome palette is critical to the deep-fried aesthetic because it eliminates the "designed" quality of color palettes. A monochrome image looks like it's been through something — photocopied, faxed, screen-captured, re-compressed. It suggests degradation.

### Screen Shake

Pseudo-random displacement, driven by the frame number through a hash-like trigonometric function:

```tsx
const fastShake = (frame: number, intensity: number) => {
  const f = Math.floor(frame * 3);
  return {
    x: Math.sin(f * 7.31) * intensity,
    y: Math.cos(f * 11.17) * intensity,
  };
};
```

The `frame * 3` multiplier makes the shake update three times per frame (since the input is floored, this creates a stepped, jittery motion rather than a smooth oscillation). The irrational-ish multipliers 7.31 and 11.17 ensure that the X and Y shake are not correlated — the displacement looks random rather than circular.

The intensity parameter increases over the animation, so the shake builds from a gentle tremor to a violent seizure as the void's pull intensifies.

Why not actual random numbers? Remotion renders each frame independently. If the shake used `Math.random()`, each render of the same frame would produce different displacement, causing visual inconsistency in the preview (where frames can be rendered out of order) and making the output non-deterministic. The trigonometric pseudo-random function is deterministic — frame 42 always produces the same shake offset — while looking random to the eye.

### Scanlines

Horizontal lines overlaid at low opacity, simulating a CRT display:

```tsx
<div style={{
  position: "absolute",
  inset: 0,
  background: `repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0,0,0,0.15) 2px,
    rgba(0,0,0,0.15) 4px
  )`,
  pointerEvents: "none",
  zIndex: 80,
}} />
```

Every 4 pixels, a 2-pixel-tall dark band at 15% opacity. The effect is subtle at 720p but immediately reads as "old technology" or "surveillance footage" — connoting the mediated, degraded quality that the deep-fried aesthetic requires.

### Noise Overlay

Fractal noise generated via an inline SVG data URI:

```tsx
<div style={{
  position: "absolute",
  inset: 0,
  opacity: 0.1,
  backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200'
    xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E
    %3CfeTurbulence type='fractalNoise' baseFrequency='0.8'
    numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25'
    height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
  pointerEvents: "none",
  zIndex: 90,
}} />
```

The SVG uses `feTurbulence` to generate Perlin noise at high frequency (0.8) with 4 octaves of detail. The noise is static — the same pattern every frame — which reads as film grain or analog noise rather than digital interference. At 10% opacity, it adds a barely-visible texture that prevents the monochrome background from looking digitally clean.

The inline SVG trick avoids a separate image file. The data URI is generated once and applied as a CSS background. It tiles automatically. No external dependencies.

### Glitch Blocks

Rectangular blocks of white that flash on screen for 1-2 frames, simulating digital compression artifacts:

```tsx
{frame % 17 === 0 && (
  <div style={{
    position: "absolute",
    left: Math.sin(frame * 3.7) * 400 + 640,
    top: Math.cos(frame * 5.3) * 200 + 360,
    width: 40 + Math.sin(frame * 2.1) * 30,
    height: 8 + Math.cos(frame * 4.7) * 6,
    background: "white",
    opacity: 0.8,
    zIndex: 95,
  }} />
)}
```

The glitch appears every 17th frame (chosen because 17 is prime, so the pattern doesn't sync with any other periodic effect). The position and size are pseudo-random functions of the frame number, using the same trigonometric hash technique as the shake. The blocks are bright white against the monochrome background — a burst of visual noise that breaks the smoothness of the animation for a single frame.

---

## V. Easing: The Shape of Time

Linear interpolation produces motion that starts and stops instantaneously — physically impossible and visually jarring. Easing functions reshape the interpolation curve to produce motion that accelerates, decelerates, or overshoots.

Remotion provides `Easing.bezier(x1, y1, x2, y2)`, which defines a cubic-bezier curve identical to CSS `cubic-bezier()`. The four control points determine the shape of the mapping from input progress (0 to 1) to output progress (0 to 1).

Three curves appear repeatedly in the Rabbit Hole compositions:

```tsx
// Crisp UI entrance (strong ease-out)
const enter = Easing.bezier(0.16, 1, 0.3, 1);

// Playful overshoot (bounces past target)
const bouncy = Easing.bezier(0.34, 1.56, 0.64, 1);

// Extreme bounce for squash-stretch
const extreme = Easing.bezier(0.68, -0.55, 0.265, 1.55);
```

The second curve is the one that gives TikTokTitle its character. A `y1` value of 1.56 means the curve overshoots 1.0 — the output progress exceeds 100% before settling back. Applied to scale, this means a letter bounces in slightly too large before settling to its final size. Applied to position, it means a letter slides past its target and bounces back.

The TikTokTitle uses this overshoot for its letter reveal:

```tsx
const bounce = interpolate(frame, [0, 20, 30], [0, 1.4, 1], {
  easing: Easing.bezier(0.34, 1.56, 0.64, 1),
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});
```

Each letter appears, overshoots to scale 1.4, and settles back to 1.0. With letters staggered 6 frames apart, the word "RABBITHOLE" bounces across the screen letter by letter, each one slightly too enthusiastic before finding its place.

For the anticipation beat in TheVoid, the curve needs the opposite character — a brief reversal before the forward motion:

```tsx
const progress = interpolate(frame, [0, 20, 50], [0, 0.15, 1], {
  easing: Easing.bezier(0.25, 0.1, 0.5, 1),
});
```

This curve starts slow (the rabbit gathering itself), then accelerates smoothly through the pull phase. Combined with the spatial pull-back (x retreats from 300 to 250 before advancing to 640), the result feels like a slingshot: the rabbit is pulled backward by the void's gravity, held for a beat, then released.

---

## VI. Synthesized Audio: Making a Void Sound Like Something

A void has no sound. This is inconvenient for a podcast intro. The audio for TheVoid was synthesized from scratch using Python with NumPy and SciPy — no samples, no sound libraries, no recorded material. Every sound is generated mathematically and processed through a signal chain designed to produce the specific character of "eerie, cheap, and broken."

### The Audio Stack

Six audio files, each synthesized for a specific role in the animation:

| File | Duration | Role | Key frequency | Processing |
|---|---|---|---|---|
| `void_drone.wav` | Loops | Background atmosphere | 55 Hz fundamental | Bitcrush 4-bit, lowpass 800 Hz |
| `rabbit_pull.wav` | 3.0s | Motion-synced bass | 80 Hz sweep | Distortion 5, lowpass 1200 Hz |
| `squish.wav` | 0.5s | Anticipation impact | Noise burst | Envelope: fast attack, fast decay |
| `suck_whirl.wav` | 1.5s | Spiral entry | 2000 Hz descending | Bitcrush 6-bit, bandpass |
| `deep_fried_hit.wav` | 0.3s | Final impact | Broadband | Distortion 8, bitcrush 3-bit |
| `glitch_burst.wav` | 0.8s | Random texture | White noise | Bitcrush 2-bit, gate |

### The Signal Chain

Every sound passes through the same processing chain, with different parameters:

```python
base_tone + oscillators → envelope → distortion → bitcrush → filter → normalize
```

**Base tone generation:** Simple sine waves, combined additively. The void drone starts with a 55 Hz fundamental (low A, the bottom of audible rumble) and adds harmonics at intervals that produce dissonance — minor seconds, tritones, frequencies that clash and beat against each other.

**Envelope shaping:** Each sound gets an amplitude envelope that controls its volume over time. The void drone has no envelope (it loops). The squish has a near-instantaneous attack (2ms) and a fast decay (50ms) — a percussive impulse that hits and dies. The pull sound has a slow attack (500ms) and sustains through the animation, matching the visual motion.

**Distortion** is `tanh` clipping:

```python
def apply_distortion(audio, amount=5):
    return np.tanh(audio * amount) / np.tanh(amount)
```

`tanh` maps any input to the range (-1, 1), but with a soft knee — values near zero pass through nearly unchanged, while large values are compressed toward the limits. The `amount` parameter controls how aggressively signals are pushed into the compression region. At amount=5, any sample above about 0.2 is driven hard into the tanh curve's plateau, producing a warm, buzzing distortion. At amount=8 (used for the final impact), even quiet signals are distorted — the waveform is nearly a square wave, all plateau and no transition.

The division by `np.tanh(amount)` normalizes the output so that the peak amplitude is still 1.0 regardless of the distortion amount. Without normalization, higher distortion amounts would reduce the peak level.

**Bitcrushing** reduces the effective bit depth:

```python
def bitcrush(audio, bits=4):
    levels = 2 ** bits
    return np.round(audio * levels) / levels
```

At 4 bits, the signal is quantized to 16 discrete levels. The smooth curves of a sine wave become a staircase. The audible result is a grainy, lo-fi quality — the sound equivalent of a low-resolution image. At 2 bits (4 levels), the sound is nearly a square wave: only four possible amplitudes, producing a harsh, retro-game-console buzz. At 3 bits (8 levels), the deep-fried hit lands somewhere between — recognizably a sound, but audibly damaged.

**Filtering** uses SciPy's Butterworth filter:

```python
def lowpass_filter(audio, cutoff=800, sr=44100, order=4):
    nyq = sr / 2
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low')
    return filtfilt(b, a, audio)
```

The void drone's 800 Hz lowpass removes all high-frequency content, leaving only the rumbling fundamental and low harmonics. The result sounds muffled, underground, distant — as if heard through a wall. This is the sonic equivalent of the monochrome visual palette: stripping away clarity to suggest degradation and mediation.

### Audio Placement in Remotion

Each synthesized file is placed in the composition using Remotion's `<Audio>` component. The simplest usage is a looping background drone:

```tsx
<Audio src={staticFile("void_drone.wav")} loop volume={0.4} />
```

More interesting is the motion-synced pull sound, whose volume tracks the animation's progress:

```tsx
<Audio
  src={staticFile("rabbit_pull.wav")}
  volume={(f) => interpolate(
    motionPhase, [0, 0.1, 0.8, 1], [0, 0.6, 0.6, 0]
  )}
/>
```

The volume is zero during the anticipation phase (motionPhase 0 to 0.1), rises to 0.6 during the pull (0.1 to 0.8), sustains through the spiral, and fades to zero as the rabbit vanishes (0.8 to 1.0). The audio literally follows the visual motion — louder as the rabbit accelerates, silent when it's gone.

The squish sound is timed to the anticipation beat:

```tsx
<Audio
  src={staticFile("squish.wav")}
  volume={(f) => interpolate(frame, [0, 8, 13], [0, 0.5, 0])}
/>
```

Volume rises from 0 to 0.5 over frames 0-8 (the anticipation squash), then fades to 0 by frame 13. The sound exists for less than half a second — a subliminal impact that registers in the body more than the ear.

The deep-fried hit arrives at the climax:

```tsx
<Audio
  src={staticFile("deep_fried_hit.wav")}
  volume={(f) => interpolate(frame, [60, 70, 90], [0, 0.7, 0])}
/>
```

Frame 60 to 70: the hit rises from silence to 0.7. Frame 70 to 90: it fades. The timing places the peak impact just as the rabbit reaches maximum spiral velocity — the visual and auditory climaxes coincide.

The full audio stack for TheVoid:

```tsx
<Audio src={staticFile("void_drone.wav")} loop volume={0.4} />
<Audio src={staticFile("rabbit_pull.wav")}
  volume={(f) => interpolate(motionPhase, [0, 0.1, 0.8, 1], [0, 0.6, 0.6, 0])} />
<Audio src={staticFile("squish.wav")}
  volume={(f) => interpolate(frame, [0, 8, 13], [0, 0.5, 0])} />
<Audio src={staticFile("suck_whirl.wav")}
  volume={(f) => interpolate(motionPhase, [0.5, 0.8, 1], [0, 0.5, 0.7])} />
<Audio src={staticFile("deep_fried_hit.wav")}
  volume={(f) => interpolate(frame, [60, 70, 90], [0, 0.7, 0])} />
<Audio src={staticFile("glitch_burst.wav")} playbackRate={0.8} volume={0.3} />
```

Six audio sources, all driven by the same frame number that drives the visuals. The volume functions reference the same `motionPhase` and `frame` variables as the visual effects. Audio and video are unified under a single parameterization — there is no separate audio timeline to keep in sync.

---

## VII. The TikTok Title: Text as Motion Graphics

The TikTokTitle composition spells out "RABBITHOLE" one letter at a time, each bouncing into place with overshoot easing. The aesthetic reference is TikTok's native text animation: letters that appear with a playful, physics-y bounce, slightly too energetic, slightly too fast.

The letter reveal uses staggered timing:

```tsx
const letters = "RABBITHOLE".split("");

letters.map((letter, i) => {
  const delay = i * 6;  // 6 frames between each letter
  const letterFrame = frame - delay;

  const scale = letterFrame >= 0
    ? interpolate(letterFrame, [0, 20, 30], [0, 1.4, 1], {
        easing: Easing.bezier(0.34, 1.56, 0.64, 1),
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;

  return (
    <span style={{
      transform: `scale(${scale})`,
      display: "inline-block",
      color: "white",
      WebkitTextStroke: "3px black",
    }}>
      {letter}
    </span>
  );
});
```

Each letter's local frame (`letterFrame`) starts counting when its delay has elapsed. Before the delay, the letter is at scale 0 (invisible). After the delay, it follows the bounce curve: 0 -> 1.4 -> 1.0 over 30 frames.

The stagger (6 frames = 0.2 seconds between letters) produces a wave effect. "R" appears first, bouncing in. By the time "R" has settled, "A" is at maximum overshoot. By the time "A" settles, "B" is overshooting. The wave propagates through the word.

The total reveal time: 9 letters * 6 frame stagger + 30 frames for the last letter to settle = 84 frames (2.8 seconds). The composition is 165 frames (5.5 seconds), so the remaining 81 frames (2.7 seconds) show the complete word with deep-fried visual treatment: scanlines, noise, subtle pulse.

The audio for TikTokTitle is different from TheVoid — it uses the podcast's actual logo audio (`RABBIT_HOLE_logo_trimmed.wav`), a 3.58-second clip trimmed from the full podcast theme at the 6-second mark. The composition length (5.5 seconds) accommodates the full audio clip with padding for the opening bounce.

---

## VIII. Particles, Rings, and Environmental Effects

The void at (640, 360) is not just a destination for the rabbit — it's an active element with its own visual presence. Three environmental effects establish the void as a force:

### Spiral Rings

Concentric circles that rotate around the void's center, suggesting a whirlpool or accretion disk:

```tsx
const rings = useMemo(() =>
  [...Array(4)].map((_, i) => ({
    radius: 40 + i * 30,
    speed: 0.05 + i * 0.02,
    opacity: 0.3 - i * 0.05,
  })),
  []
);

{rings.map((ring, i) => (
  <div key={i} style={{
    position: "absolute",
    left: 640 - ring.radius,
    top: 360 - ring.radius,
    width: ring.radius * 2,
    height: ring.radius * 2,
    borderRadius: "50%",
    border: `1px solid rgba(255,255,255,${ring.opacity})`,
    transform: `rotate(${frame * ring.speed * 360}deg)`,
  }} />
))}
```

Four rings at radii 40, 70, 100, and 130 pixels. Each rotates at a different speed (faster rings are closer to the center, mimicking gravitational orbital mechanics). The opacity decreases with distance (inner rings are brighter). The `useMemo` is important — creating the ring configuration array every frame would cause unnecessary garbage collection pressure during rendering.

### Particle Debris

Small dots that stream toward the void's center, suggesting matter being consumed:

```tsx
const PARTICLES = [...Array(12)].map((_, i) => ({
  angle: (i / 12) * Math.PI * 2,
  speed: 0.5 + (i % 3) * 0.3,
  size: 2 + (i % 4),
}));

{PARTICLES.map((p, i) => {
  const dist = interpolate(
    motionPhase, [0.2, 1],
    [150, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const angle = p.angle + frame * p.speed * 0.1;

  return (
    <div key={i} style={{
      position: "absolute",
      left: 640 + Math.cos(angle) * dist,
      top: 360 + Math.sin(angle) * dist,
      width: p.size,
      height: p.size,
      borderRadius: "50%",
      background: "white",
      opacity: dist / 150,
    }} />
  );
})}
```

Twelve particles distributed evenly around the void. As `motionPhase` progresses from 0.2 to 1.0, each particle's distance from center decreases from 150 pixels to 0 — they spiral inward. The angle rotates over time (frame * speed * 0.1), so the inward motion follows a spiral path rather than a straight line. Opacity tracks distance: particles fade as they approach the center, as if the void is consuming their light.

The particle array is allocated once (outside the component function, or via `useMemo`) rather than recreated every frame. This is the first performance rule of Remotion: static data must not be created inside the render path.

### Motion Lines

Speed lines that appear during the pull phase, radiating outward from the direction of motion:

```tsx
{motionPhase > 0.15 && motionPhase < 0.85 && (
  <div style={{
    position: "absolute",
    left: rabbitX - 100,
    top: rabbitY,
    width: 80,
    height: 2,
    background: `linear-gradient(
      90deg,
      rgba(255,255,255,${0.5 * (1 - motionPhase)}),
      transparent
    )`,
  }} />
)}
```

The lines appear only during the pull phase (motionPhase 0.15 to 0.85), positioned behind the rabbit and fading as the rabbit nears the void. They are a comic-book convention — visual shorthand for speed — applied to a 3-second animation about an emoji.

---

## IX. Performance Patterns

Remotion renders each frame as a React component render, which means that performance matters in ways specific to this environment. A 90-frame composition at 1280x720 requires 90 render passes. At higher resolutions or longer durations (a 60-second composition at 60 FPS is 3,600 renders), inefficiencies compound.

Three patterns dominate the performance concerns in this project:

### Static Data Outside the Render Path

```tsx
// Bad: creates a new array every frame
const particles = [...Array(12)].map((_, i) => ({ ... }));

// Good: created once, reused every frame
const PARTICLES = [...Array(12)].map((_, i) => ({ ... }));
// (outside the component, or via useMemo with empty deps)
```

The particle configuration (angle, speed, size) does not change between frames. Creating it every render allocates memory that is immediately discarded — 90 allocations for a 90-frame composition, each requiring garbage collection. Moving it outside the component (or into a `useMemo` with empty dependencies) reduces this to a single allocation.

### Memoized Expensive Computations

```tsx
const rings = useMemo(() =>
  [...Array(4)].map((_, i) => ({
    radius: 40 + i * 30,
    speed: 0.05 + i * 0.02,
    opacity: 0.3 - i * 0.05,
  })),
  []
);
```

`useMemo` with empty dependencies computes the value once and caches it for the component's lifetime. For data that depends on `frame`, memoization doesn't help (the dependency changes every render). For configuration data, it prevents redundant computation.

### Simple Transforms

```tsx
// Avoid: multiple transform operations that the browser must compose
transform: `translate(-50%, -50%) scale(${s}) rotate(${r}deg) translateX(${x}px)`

// Prefer: pre-compute the final position
transform: `translate(${x - halfWidth}px, ${y - halfHeight}px) scale(${s}) rotate(${r}deg)`
```

Fewer transform operations means less work for the browser's compositor. In a render-to-video pipeline (where the browser renders a headless page for each frame), compositor efficiency directly affects render time.

### Template Literals for Dynamic Styles

A Remotion-specific requirement: dynamic CSS values must use template literals, not string concatenation or regular strings:

```tsx
// Works
filter: `drop-shadow(${size}px 0 0 ${color})`

// Doesn't work reliably
filter: "drop-shadow(" + size + "px 0 0 " + color + ")"
```

The template literal form is parsed correctly by Remotion's rendering pipeline. The concatenation form may produce identical strings but can fail in edge cases related to how Remotion serializes styles for the headless browser.

---

## X. The Render Pipeline

Development and rendering use different commands with different characteristics:

### Development Preview

```bash
cd 003-rabbit-hole
tmux new-session -d -s remotion "npx remotion studio --no-open"
# Preview at http://localhost:3000
```

The studio provides a browser-based preview with a frame scrubber, composition selector, and real-time rendering. Audio does not play reliably in preview mode — it is rendered only during final export. This means audio timing must be validated through actual renders, not preview scrubbing.

### Single-Frame Preview

```bash
npx remotion still TheVoid --frame=35 --scale=0.5 --output=preview.png
```

Renders a single frame as a PNG. The `--scale=0.5` flag renders at half resolution for faster output. Useful for checking a specific animation state without rendering the entire composition.

### Final Render

```bash
npx remotion render TheVoid --output=the-void.mp4
```

Renders all 90 frames to an MP4 file with audio. This is the authoritative output — the only rendering mode where audio synchronization is correct and all visual effects are composited at full quality.

The render pipeline:

1. For each frame (0 to 89): render the React component in a headless browser, capture the viewport as a bitmap.
2. Encode all bitmaps as video frames using FFmpeg (bundled with Remotion).
3. Mix all `<Audio>` sources with their frame-dependent volume curves.
4. Mux video and audio into the output container.

The entire pipeline is deterministic. Running `npx remotion render TheVoid` twice produces byte-identical output (assuming no changes to the component code or audio files). This is a consequence of the pure-function-of-frame-number architecture: there is no random state, no real-time input, and no dependency on render order.

---

## XI. The Aesthetics of Damage

There is a question lurking beneath the technical details: why make something deliberately ugly?

The deep-fried aesthetic is not the absence of design decisions. It is a specific set of design decisions that communicate specific things. Monochrome communicates degradation — the image has been through something. Chromatic aberration communicates instability — the display is failing. Scanlines communicate mediation — you are watching a recording of a recording. Noise communicates analog materiality — this signal traveled through a physical medium. Bitcrushed audio communicates lo-fi provenance — this was made with cheap equipment, or old equipment, or no equipment at all.

Together, these signals construct a specific persona: the maker who does not care about polish, or who actively rejects it. This is the persona of the shitpost, the ironic meme, the late-night TikTok. It is a generational signal: "I know what good production looks like, and I am choosing not to do it, because the content matters more than the container."

For a podcast about falling down rabbit holes with ChatGPT — an inherently chaotic, associative, improvised activity — this aesthetic is appropriate in a way that slick motion graphics would not be. A polished intro would promise a polished experience. A deep-fried intro promises exactly what the podcast delivers: a messy, enthusiastic descent into whatever seemed interesting at 2 AM.

The technical sophistication of the implementation is invisible to the viewer. They see a rabbit getting sucked into a hole with some glitchy effects and weird sounds. They do not see the squash-and-stretch parameterization, the layered interpolation, the deterministic pseudo-random shake, the six-layer synthesized audio stack, the CSS drop-shadow chromatic aberration hack, the performance-optimized particle system, or the frame-driven volume curves.

That invisibility is the point. The best technical work in aesthetic production is the work the audience never notices — the work that makes the thing feel the way it's supposed to feel, without calling attention to how it was made. The rabbit looks like it has weight because the squash-and-stretch preserves volume. The void feels threatening because the shake intensifies and the background darkens in sync with the motion. The impact feels physical because the audio and visual climaxes coincide.

The whole thing takes three seconds. The code that generates it fits in a single file. The aesthetic it achieves would take hours to replicate manually in After Effects — and the result would be a file, not a function. This is the argument for programmatic video in a sentence: the same level of authorial control, expressed as code, producing an artifact that is reproducible, parameterizable, versionable, and testable.

The rabbit falls into the void. The drone peaks. The screen goes black. Cut to podcast.

---

*The Rabbit Hole project is located at `/home/manuel/code/wesen/patreon/videos/003-rabbit-hole/`. Audio synthesis is handled by `generate_audio.py`. Compositions are defined in `src/Root.tsx` with implementations in `src/RabbitHole.tsx` and `src/TikTokTitle.tsx`.*

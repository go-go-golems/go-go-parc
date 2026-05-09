---
title: "Rabbit Hole Podcast Intros - Remotion Video Generation"
aliases:
  - Remotion Rabbit Hole Videos
  - Podcast Intros Remotion
tags:
  - project
  - video
  - remotion
  - animation
  - audio
  - podcast
  - deep-fried
status: active
type: project
created: 2026-04-11
repo: /home/manuel/code/wesen/patreon/videos/003-rabbit-hole
---

# Rabbit Hole Podcast Intros - Remotion Video Generation

This project generates video intros/inserts for the Rabbit Hole podcast about exploring topics with ChatGPT. The animations feature a rabbit falling into a black hole, stylized with deep-fried Gen-Z aesthetics—monochrome palette, chromatic aberration, squash-and-stretch animation, and eerie synthesized audio.

> [!summary]
> - Three Remotion compositions: RabbitHole (laser eyes), TheVoid (squash-stretch suction), TikTokTitle (RABBITHOLE text)
> - Monochrome black & white aesthetic with deep-fried visual effects
> - Programmatically generated eerie audio with bitcrushing and distortion
> - Logo audio integrated from existing podcast track

## Why this project exists

The Rabbit Hole podcast needs video inserts and intros that communicate the "falling down the rabbit hole with ChatGPT" concept. Rather than using stock footage or manual editing, this project generates the animations programmatically using Remotion—a React framework for creating videos.

The aesthetic is deliberately Gen-Z / deep-fried: chaotic, glitchy, oversaturated (in the visual treatment), with synthesized eerie sounds. This matches the chaotic energy of rabbit-holing through AI topics.

## Current project status

Three compositions are ready for preview and rendering:

| Composition | Description | Duration | Audio |
|-------------|-------------|----------|-------|
| **RabbitHole** | Rabbit with red laser eyes, deep-fried chaos | 90 frames (3s) | Eerie SFX stack |
| **TheVoid** | Rabbit sucked into black hole with squash-stretch | 90 frames (3s) | Void drone + pull sounds |
| **TikTokTitle** | R A B B I T H O L E bouncing text reveal | 165 frames (5.5s) | Logo audio |

## Project structure

```
003-rabbit-hole/
├── src/
│   ├── Root.tsx              # Composition definitions
│   ├── RabbitHole.tsx        # TheVoid + RabbitHole components
│   └── TikTokTitle.tsx       # Text reveal animation
├── public/                   # Static assets (audio, fonts)
│   └── *.wav                 # Generated audio files
├── generate_audio.py         # Python script for audio synthesis
└── rabbit-hole-deepfried.mp4 # Previous render
```

## Compositions

### TheVoid

The main animation: a rabbit gets sucked into a black hole with squash-and-stretch animation physics.

**Animation phases:**
1. **Anticipation (0-8 frames)**: Rabbit pulls back slightly (squash)
2. **Stretch & Pull (8-53 frames)**: Rabbit accelerates toward hole, stretches, motion lines appear
3. **Spiral (53-90 frames)**: Rabbit spins and shrinks into the void

**Visual effects:**
- Monochrome background that darkens as intensity builds
- Spiral rings around the hole
- Particle debris being sucked inward
- Motion lines during pull phase
- Chromatic aberration (RGB split)
- Shake that intensifies throughout
- Scanlines and noise overlay
- Glitch blocks
- Final black fade

### TikTokTitle

A TikTok-style text reveal spelling out "RABBITHOLE".

**Animation:**
- Letters bounce in one by one (6 frames apart) with overshoot easing
- White text with black stroke for legibility on dark background
- Monochrome gradient background with vignette
- Scanlines and subtle noise for deep-fried effect

**Audio sync:**
- Logo audio from RABBIT+HOLE.mp3 (trimmed to 3.58s)
- Starts at frame 0 with the text
- Video length matches full audio duration

### RabbitHole

The original deep-fried composition with red laser eyes. Still available but TheVoid supersedes it for the main rabbit-into-hole concept.

## Audio generation

Audio is synthesized programmatically using Python with numpy and scipy.

### Audio files generated

| File | Description | Character |
|------|-------------|------------|
| `void_drone.wav` | Constant eerie drone | Loops continuously |
| `rabbit_pull.wav` | Bass drone that follows motion | Intensifies with pull |
| `squish.wav` | Rubber-like impact | Anticipation squash |
| `suck_whirl.wav` | Swirling high-pitched tone | As rabbit enters |
| `deep_fried_hit.wav` | Impact crunch with distortion | End impact |
| `glitch_burst.wav` | Random glitchy noise | Random glitches |
| `RABBIT_HOLE_logo_trimmed.wav` | Podcast logo audio | 3.58s from 0:06 of track |

### Audio processing chain

```python
# Each sound uses this chain:
base_tone + oscillators → envelope → distortion → bitcrush → filter → normalize

# Distortion: tanh clipping
apply_distortion(audio, amount=5)  # harder clipping = more crunch

# Bitcrushing: reduce bit depth
bitcrush(audio, bits=4)  # lower bits = more lo-fi

# Filtering
lowpass_filter(audio, cutoff=800)  # muffled void sound
```

### Adding audio to Remotion

```tsx
import { Audio } from "@remotion/media";
import { staticFile } from "remotion";

// Simple audio
<Audio src={staticFile("sound.wav")} volume={0.8} />

// Dynamic volume
<Audio 
  src={staticFile("sound.wav")}
  volume={(f) => interpolate(f, [0, 30], [0, 1])}
/>

// Delayed start
<Sequence from={15}>
  <Audio src={staticFile("sound.wav")} />
</Sequence>
```

## Deep-fried visual techniques

### Chromatic aberration

RGB split using offset drop shadows:

```tsx
filter: `
  drop-shadow(${aberration}px 0 0 rgba(255,0,0,0.5))
  drop-shadow(-${aberration}px 0 0 rgba(0,255,255,0.5))
`
```

### Squash and stretch

Animation principle applied to the rabbit:

```tsx
const squashX = interpolate(motionPhase, [0, 0.1, 0.5, 0.9, 1], [1, 1.3, 0.8, 1.2, 2]);
const squashY = interpolate(motionPhase, [0, 0.1, 0.5, 0.9, 1], [1, 0.7, 1.2, 0.8, 0.5]);

transform: `scaleX(${rabbitScale * squashX}) scaleY(${rabbitScale * squashY})`
```

### Monochrome palette

All colors forced to grayscale via CSS filter and HSL with zero saturation:

```tsx
background: `hsl(0, 0%, ${gray}%)`
filter: `contrast(${contrast}) grayscale(1)`
```

### Shake effect

Fast pseudo-random displacement:

```tsx
const fastShake = (frame, intensity) => {
  const f = Math.floor(frame * 3);
  return {
    x: Math.sin(f * 7.31) * intensity,
    y: Math.cos(f * 11.17) * intensity,
  };
};
```

## Technical Deep-Dive: Remotion Code and APIs

This section documents the actual code patterns, APIs, and implementation details used in this project. It serves as both a reference for this project and a guide for future Remotion work.

---

## Core Hooks

### `useCurrentFrame()`

The fundamental hook that returns the current frame number. All animation is driven by this value.


```tsx
const frame = useCurrentFrame();
```

Frame number starts at 0 and increments each frame. At 30fps, frame 30 = 1 second.


### `useVideoConfig()`

Returns composition metadata:

```tsx
const { fps, width, height, durationInFrames } = useVideoConfig();
```

Use this for:
- Converting seconds to frames: `2 * fps` = 2 seconds
- Responsive sizing based on dimensions
- Duration-based calculations

---

## Animation: `interpolate()`

The core animation function. Maps input values (typically frame ranges) to output values.

### Basic syntax

```tsx
import { interpolate } from "remotion";

const opacity = interpolate(frame, [0, 30], [0, 1]);
// Frame 0 → opacity 0
// Frame 30 → opacity 1
// Linear interpolation between
```


### With clamping (most common)

Without clamping, values can exceed the range. Clamp to keep values in bounds:

```tsx
const scale = interpolate(frame, [0, 30], [0, 1], {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});
```


### Multi-stop interpolation

Map through multiple values:


```tsx
const position = interpolate(frame, [0, 15, 30, 45], [300, 250, 500, 640]);
// 0-15: moves toward 250 (anticipation pull-back)
// 15-30: accelerates toward 500
// 30-45: continues to 640 (hole position)
```

### With easing

```tsx
const bounce = interpolate(frame, [0, 20, 30], [0, 1.4, 1], {
  easing: Easing.bezier(0.34, 1.56, 0.64, 1),
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});
```

---

## Easing Functions

### `Easing.bezier(x1, y1, x2, y2)`

Custom cubic-bezier curves. Same as CSS `cubic-bezier()`.

```tsx
import { Easing } from "remotion";

// Crisp UI entrance (strong ease-out)
const enter = Easing.bezier(0.16, 1, 0.3, 1);

// Playful overshoot (bounces past target)
const bouncy = Easing.bezier(0.34, 1.56, 0.64, 1);


// Extreme bounce for squash-stretch
const extreme = Easing.bezier(0.68, -0.55, 0.265, 1.55);
```

### Preset easings

```tsx
Easing.in(Easing.cubic)      // Start slow, accelerate
Easing.out(Easing.cubic)     // Start fast, decelerate  
Easing.inOut(Easing.cubic)   // Slow both ends


Easing.bezier(0.45, 0, 0.55, 1)  // Symmetric ease
```

### Anticipation pattern

For squash-and-stretch, use a curve that creates overshoot:

```tsx
// Pull back first (0 → 0.15), then overshoot (0.15 → 1.2)
const progress = interpolate(frame, [0, 20, 50], [0, 0.15, 1], {
  easing: Easing.bezier(0.25, 0.1, 0.5, 1),
});
```

---


## Squash and Stretch Pattern

The classic animation principle: objects squash when pulling back and stretch when moving fast.

### Implementation


```tsx
export const TheVoid: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Define animation phases
  const anticipationFrames = 8;
  const pullFrames = 45;
  
  // Phase 1: anticipation → 0.15
  // Phase 2: pull → builds to 0.8
  // Phase 3: finish → 1.0
  const motionPhase = interpolate(
    frame, 
    [0, anticipationFrames, anticipationFrames + pullFrames, durationInFrames],
    [0, 0.15, 0.8, 1]
  );

  // Squash X: wider when pulling back
  const squashX = interpolate(motionPhase, [0, 0.1, 0.5, 0.9, 1], [1, 1.3, 0.8, 1.2, 2]);
  
  // Squash Y: shorter when pulling back
  const squashY = interpolate(motionPhase, [0, 0.1, 0.5, 0.9, 1], [1, 0.7, 1.2, 0.8, 0.5]);

  // Size shrinks as it gets sucked in
  const rabbitScale = interpolate(motionPhase, [0, 1], [2.5, 0.1]);

  return (
    <div
      style={{
        transform: `
          scaleX(${rabbitScale * squashX}) 
          scaleY(${rabbitScale * squashY})
        `,
      }}
    >
      🐰
    </div>
  );
};
```

### Motion phase values explained

| Phase | motionPhase | squashX | squashY | rabbitScale |
|-------|-------------|---------|---------|-------------|
| Start | 0 | 1.0 | 1.0 | 2.5 |
| Anticipation | 0.1 | 1.3 | 0.7 | ~2.3 |
| Fast pull | 0.5 | 0.8 | 1.2 | ~1.2 |
| Sucked in | 1.0 | 2.0 | 0.5 | 0.1 |

---

## Position and Movement

### Moving along a path

```tsx
// X position: starts at 300, pulls back to 250, then accelerates to 640
const rabbitX = interpolate(motionPhase, [0, 0.1, 0.5, 1], [300, 250, 500, 640]);


// Y position: subtle wobble that dampens as it gets sucked in
const rabbitY = 360 + Math.sin(frame * 0.3) * (20 * (1 - motionPhase));
```

### Parabolic arc

```tsx
const rabbitY = interpolate(
  motionPhase,
  [0, 0.5, 1],
  [400, 200, 360],  // rises then falls
  { easing: Easing.out(Easing.quad) }
);
```


---

## Compound Animations

### Building up intensity

```tsx
// Multiple parameters that ramp up together
const bgIntensity = interpolate(frame, [0, 60], [0, 1], {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});

const contrast = 1 + bgIntensity * 2;
const saturate = 1.5 + bgIntensity * 3;
const aberration = 3 + pulse * 8;
```


### Fade in / Fade out pattern


```tsx
// Fade in at start
const fadeIn = interpolate(frame, [0, 15], [0, 1], {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});


// Fade out at end  
const fadeOut = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], {
  easing: Easing.in(Easing.cubic),
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});

// Combine
<div style={{ opacity: fadeIn * fadeOut }} />
```

---

## Visual Effects

### Chromatic aberration (RGB split)


```tsx
const aberration = 2 + pulse * 6;

<div style={{
  filter: `
    drop-shadow(${aberration}px 0 0 rgba(255,0,0,0.5))
    drop-shadow(-${aberration}px 0 0 rgba(0,255,255,0.5))
  `,
}}>
  🐰
</div>
```


### Pulsing effect


```tsx
const pulse = (Math.sin(frame * 0.3) + 1) / 2;  // 0 to 1
const pulse2 = (Math.sin(frame * 0.7 + 1) + 1) / 2;

// Use in any property
fontSize: 100 + pulse * 20;
boxShadow: `0 0 ${20 + pulse * 40}px rgba(255,255,255,${pulse2})`;
```

### Shake effect


```tsx
const fastShake = (frame: number, intensity: number) => {
  const f = Math.floor(frame * 3);  // 3x faster
  return {
    x: Math.sin(f * 7.31) * intensity,
    y: Math.cos(f * 11.17) * intensity,
  };
};

const shakeOffset = fastShake(frame, shakeIntensity);

<div style={{
  left: 640 + shakeOffset.x,
  top: 360 + shakeOffset.y,
}} />
```


### Noise overlay


```tsx
<div style={{
  position: "absolute",
  inset: 0,
  opacity: 0.1,
  backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
  pointerEvents: "none",
  zIndex: 90,
}} />
```

### Conditional rendering

```tsx
{/* Only show after frame 20 */}
{_frame > 20 && (
  <div style={{ /* laser beam styles */ }} />
)}

{/* Fade in then out */}
{interpolate(frame, [0, 30, 60], [0, 1, 0], {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
}) > 0 && (
  <div />
)}
```

---

## Audio in Remotion

### Setup


```bash
npx remotion add @remotion/media
```


### Import


```tsx
import { Audio } from "@remotion/media";
import { staticFile } from "remotion";
```


### Basic usage


```tsx
// Simple playback
<Audio src={staticFile("sound.wav")} />


// With volume
<Audio src={staticFile("sound.wav")} volume={0.5} />

// Loop
<Audio src={staticFile("drone.wav")} loop volume={0.4} />

// Playback speed
<Audio src={staticFile("sound.wav")} playbackRate={0.8} />
```

### Dynamic volume

Volume can be a callback function. The argument `f` is the frame count since audio started:

```tsx
<Audio 
  src={staticFile("pull.wav")}
  volume={(f) => interpolate(f, [0, 30], [0, 0.8])}
/>

// Or with full motion tracking
<Audio 
  src={staticFile("pull.wav")}
  volume={(f) => interpolate(motionPhase, [0, 0.1, 0.8, 1], [0, 0.6, 0.6, 0])}
/>
```


### Audio synchronization pattern

For audio that needs to sync with visuals:


```tsx
// Audio starts when rabbit starts moving
const audioProgress = interpolate(frame, [0, 30], [0, 1]);

<Audio 
  src={staticFile("whoosh.wav")}
  volume={(f) => interpolate(audioProgress, [0, 1], [0, 0.7])}
/>
```

---

## Composition Setup


### Root.tsx structure

```tsx
import { Composition } from "remotion";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MyAnimation"
        component={MyAnimation}
        durationInFrames={90}      // 3 seconds at 30fps
        fps={30}
        width={1280}
        height={720}
      />
    </>
  );
};
```


### Multiple compositions

```tsx
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="TheVoid" component={TheVoid} ... />
      <Composition id="TikTokTitle" component={TikTokTitle} ... />
      <Composition id="RabbitHole" component={RabbitHole} ... />
    </>
  );
};
```

---

## Layout: AbsoluteFill


### Basic usage

```tsx
import { AbsoluteFill } from "remotion";

<div style={{ position: "absolute", inset: 0 }}>
  {/* Child elements positioned absolutely within this area */}
</div>
```

### AbsoluteFill vs regular div

- `AbsoluteFill` from Remotion is optimized for video rendering
- Positions content to fill the composition frame
- Use instead of `<div style={{ position: "absolute", inset: 0 }}>`

### Layering with z-index

```tsx
<AbsoluteFill>
  <div style={{ zIndex: 1 }}>Background</div>
  <div style={{ zIndex: 10 }}>Main content</div>
  <div style={{ zIndex: 20 }}>Foreground</div>
  <div style={{ zIndex: 100 }}>Flash overlay</div>
</AbsoluteFill>
```

---

## String interpolation in styles

Remotion requires template literals for dynamic styles (not regular objects):


```tsx
// ✓ Works - template literal
<div style={{ 
  left: x + shakeOffset.x,
  filter: `drop-shadow(${size}px 0 0 ${color})`,
}} />


// ✗ Doesn't work - regular string
<div style={{ 
  left: x + shakeOffset.x,
  filter: "drop-shadow(5px 0 0 red)",  // hardcoded works, but can't mix
}} />
```

---


## Common patterns reference

### Frame-to-seconds conversion

```tsx
const { fps } = useVideoConfig();

// 2 seconds in frames
const twoSeconds = 2 * fps;

// Frame range [0, 2s] → [0, 1]
interpolate(frame, [0, twoSeconds], [0, 1]);
```

### Condition based on frame

```tsx
// Show something after frame 60
{_frame >= 60 && <Component />}

// Show something only between frames 20-50
{_frame >= 20 && _frame <= 50 && <Component />}

```

### Repeat animation

```tsx
// Pattern that repeats every 30 frames
const cycleFrame = frame % 30;
const scale = interpolate(cycleFrame, [0, 15, 30], [1, 1.5, 1]);
```

### Sinusoidal motion

```tsx
// Gentle bobbing
const bobY = Math.sin(frame * 0.1) * 20;

// Wobble that dampens
const wobble = Math.sin(frame * 0.3) * (20 * (1 - progress));

// Wobble stops as progress approaches 1
```

### Random-ish values from frame

```tsx
// Pseudo-random based on frame
const seed = Math.floor(frame / 2);
const value = Math.sin(seed * 12.34) * intensity;
```


---

## Performance tips

1. **Avoid creating arrays on every frame**
   ```tsx
   // ✗ Bad - creates new array every render
   {[...Array(10)].map(...)}
   
   // ✓ Better - static array
   const ITEMS = [0,1,2,3,4,5,6,7,8,9];
   {ITEMS.map(...)}
   ```


2. **Memoize expensive calculations**
   ```tsx
   const rings = useMemo(() => 
     [...Array(4)].map(...),
     []
   );
   ```

3. **Keep transforms simple**
   ```tsx
   // ✗ Complex
   transform: `translate(-50%, -50%) scale(${s}) rotate(${r}deg) translateX(${x}px)`
   
   // ✓ Simple - combine operations
   transform: `translate(${x - 50}px, ${y - 50}px) scale(${s}) rotate(${r}deg)`
   ```

---

## Error troubleshooting

### "particles is not defined"

Likely moved the array creation outside the component or removed the `const particles = ` line. Re-add:

```tsx
const particles = [...Array(12)].map((_, i) => { ... });
```

### Audio doesn't play in preview

- Audio only works during render, not all preview modes
- Use `npx remotion render` with `--output=` for final video with audio
- Check that audio files are in `public/` folder and use `staticFile()`

### Build errors

```bash
# Clear cache
rm -rf .remotion
npx remotion studio
```

---

## Complete component example

Here is the minimal structure of TheVoid component:

```tsx
import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  AbsoluteFill,
} from "remotion";
import { Audio } from "@remotion/media";
import { staticFile } from "remotion";

export const TheVoid: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 1. Calculate animation values
  const motionPhase = interpolate(
    frame,
    [0, 20, 60, durationInFrames],
    [0, 0.2, 0.8, 1]
  );

  const rabbitX = interpolate(motionPhase, [0, 1], [300, 640]);
  const rabbitY = 360 + Math.sin(frame * 0.3) * 20;
  const rabbitScale = interpolate(motionPhase, [0, 1], [2.5, 0.1]);

  // 2. Return JSX with AbsoluteFill
  return (
    <AbsoluteFill
      style={{
        background: "hsl(0, 0%, 10%)",
        filter: "contrast(2) grayscale(1)",
      }}
    >
      {/* Visual elements */}
      <div
        style={{
          position: "absolute",
          left: 640,
          top: 360,
          fontSize: 200,
        }}
      >
        🕳️
      </div>

      <div
        style={{
          position: "absolute",
          left: rabbitX,
          top: rabbitY,
          transform: `scale(${rabbitScale})`,
          fontSize: 150,
        }}
      >
        🐰
      </div>

      {/* Audio */}
      <Audio src={staticFile("void_drone.wav")} loop volume={0.4} />
    </AbsoluteFill>
  );
};
```


## Related Remotion documentation

- Official docs: https://www.remotion.dev/docs
- interpolate: https://www.remotion.dev/docs/interpolate
- Easing: https://www.remotion.dev/docs/Easing
- Audio: https://www.remotion.dev/docs/audio
- useCurrentFrame: https://www.remotion.dev/docs/use-current-frame
- Composition: https://www.remotion.dev/docs/composition

---

## Working with Remotion

### Starting the dev server

```bash
cd 003-rabbit-hole
tmux new-session -d -s remotion "npx remotion studio --no-open"
# Preview at http://localhost:3000
```

### Rendering frames for preview

```bash
npx remotion still TheVoid --frame=35 --scale=0.5 --output=preview.png
```

### Rendering final video

```bash
npx remotion render TheVoid --output=the-void.mp4
```

### Key Remotion concepts

- **`useCurrentFrame()`** — drives all animation
- **`useVideoConfig()`** — access fps, dimensions, duration
- **`interpolate()`** — map frame ranges to values with easing
- **`Easing.bezier()`** — custom cubic-bezier curves
- **`AbsoluteFill`** — fills the composition area
- **`<Audio>`** — audio playback (from @remotion/media)
- **`staticFile()`** — reference files in public/ folder
- **`<Sequence>`** — delay when audio/animation starts

## Current audio setup for TheVoid

```tsx
<Audio src={staticFile("void_drone.wav")} loop volume={0.4} />
<Audio src={staticFile("rabbit_pull.wav")} volume={(f) => interpolate(motionPhase, [0, 0.1, 0.8, 1], [0, 0.6, 0.6, 0])} />
<Audio src={staticFile("squish.wav")} volume={(f) => interpolate(frame, [0, 8, 13], [0, 0.5, 0])} />
<Audio src={staticFile("suck_whirl.wav")} volume={(f) => interpolate(motionPhase, [0.5, 0.8, 1], [0, 0.5, 0.7])} />
<Audio src={staticFile("deep_fried_hit.wav")} volume={(f) => interpolate(frame, [60, 70, 90], [0, 0.7, 0])} />
<Audio src={staticFile("glitch_burst.wav")} playbackRate={0.8} volume={0.3} />
```

## Open questions

- [ ] Should RabbitHole (laser eyes version) be kept or removed?
- [ ] Audio mixing levels need real-world testing
- [ ] Add fade-out at end of TikTokTitle after audio ends?

## Near-term next steps

- [ ] Render final versions of all three compositions
- [ ] Test audio sync with actual playback
- [ ] Adjust audio levels based on feedback
- [ ] Add more compositions if needed for podcast structure

## Important project docs

- Remotion skill: `/home/manuel/code/wesen/patreon/videos/.pi/skills/remotion-best-practices/SKILL.md`
- Audio rule: `/home/manuel/code/wesen/patreon/videos/.pi/skills/remotion-best-practices/rules/audio.md`
- Animation rule: `/home/manuel/code/wesen/patreon/videos/.pi/skills/remotion-best-practices/rules/animations.md`
- Timing rule: `/home/manuel/code/wesen/patreon/videos/.pi/skills/remotion-best-practices/rules/timing.md`

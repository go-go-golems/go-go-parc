# Concevoir lecteur musical MAUI

- URL: https://chatgpt.com/c/6a85da07-5e74-83ea-ad42-bb2f7b244894
- Created: 2026-08-19T16:30:00.996Z

---

> projet perso pour mes enfants qui apprennent la musique:
>
> - charger un fichier audio
> - affichage de la waveforme
> - etre capable de decouper en section pour mettre des boucles / marqueurs de sections, repeter en boucle
>
> \---
>
> dot-net, MAUI
>
> \---
>
> Sketch out design + technology

Je partirais sur une architecture où **la waveform et les sections sont 100% en C#/.NET**, mais où **la lecture audio est abstraite derrière un moteur**. Ça évite de coincer toute l’app sur une librairie audio MAUI trop limitée pour le looping précis.

```json
{"system1_search_query":[{"q":"site:learn.microsoft.com .NET MAUI current version .NET 10 2026 official"},{"q":"site:github.com/jfversluis/Plugin.Maui.Audio Plugin.Maui.Audio README seek position loop official"},{"q":"site:github.com/naudio/NAudio NAudio GitHub official supported platforms"},{"q":"site:developer.android.com media3 exoplayer clipping media source loop official"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Planning the voice-practice app**

I’m designing a local-first .NET MAUI app with MVVM, SQLite, and an audio abstraction. I’ll prioritize trimming, looping, waveform previews, and future cloud sync, while isolating playback for painless engine replacement.

**Planned the voice-practice app**

**Searched 7 websites**

</details>

Pour le MVP, je limiterais volontairement l’import à **MP3 + WAV**. Ça simplifie énormément l’extraction de la waveform; AAC/M4A peut venir ensuite via des décodeurs spécifiques aux plateformes. Pour le fichier choisi, il vaut mieux copier le stream dans le stockage de l’app plutôt que dépendre d’un chemin physique, notamment sur Android où MAUI peut retourner une URI `content://`.

<details><summary>💭 Thinking</summary>

**Comparing playback options**

I’m choosing a high-level audio library for the MVP, then hiding it behind `IPlaybackService`. I’ll implement section looping with position checks, while treating truly seamless looping as a later native-engine upgrade.

**Compared playback options**

</details>

```json
{"system1_search_query":[{"q":"site:github.com/naudio/NLayer NLayer MP3 decoder .NET official"},{"q":"site:github.com/naudio/NAudio NAudio WaveFileReader cross platform NLayer official"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

Oui. Je le construirais comme un **petit “audio practice player”**, pas comme un éditeur audio. L’objectif est de garder le modèle simple : un morceau, une waveform, des sections, une section active qu’on peut répéter.

Pour un nouveau projet aujourd’hui, je ciblerais **.NET 10 / .NET MAUI 10** : .NET 10 est la version LTS active, supportée jusqu’en novembre 2028. citeturn961825search0turn957387view2

## UX proposée

Quelque chose de ce genre :

```text
┌─────────────────────────────────────────────────────────┐
│  🎵 Bach - Minuet.mp3                       [Changer]    │
│                                                         │
│  Intro          Mes. 1             Passage difficile    │
│    ▼               ▼                       ▼             │
│    │               │                       │             │
│ ▂▃▅▆▃▂▂▄▇█▆▃▂▃▆▇▅▃▂▂▅▆██▅▃▂▃▅▇█▆▃▂                 │
│          ├──────────── LOOP ─────────────┤               │
│          A                              B                │
│                       ▲                                 │
│                     playhead                             │
│                                                         │
│          00:38.4                    00:52.7              │
│                                                         │
│      [ -5s ]      [ ▶ / ❚❚ ]      [ +5s ]              │
│                                                         │
│       🔁 Section ON          Vitesse: [ 0.75× ]          │
│                                                         │
│ Sections                                                │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 1. Intro                  0:00 → 0:18       ▶       │ │
│ │ 2. Mesures 1–8           0:18 → 0:42       🔁      │ │
│ │ 3. Passage difficile     0:42 → 0:55       ▶       │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

Sur tablette, je donnerais énormément d'espace à la waveform. Les enfants doivent pouvoir toucher directement une zone, poser `A`, poser `B`, puis appuyer sur un gros bouton **Boucle**.

Un bonus particulièrement utile pour la pratique musicale est **0.5× / 0.75× / 1×**, avant même d'ajouter beaucoup d'autres fonctions. `Plugin.Maui.Audio` expose justement la position courante, le seek et le changement de vitesse; les plages de vitesse varient légèrement selon la plateforme. citeturn957387view0

## Architecture

```text
┌────────────────────────── .NET MAUI UI ────────────────────────┐
│                                                               │
│   PlayerPage                                                  │
│      │                                                        │
│      ├── WaveformView (SkiaSharp)                             │
│      ├── TransportControls                                    │
│      └── SectionsView                                         │
│                │                                              │
│          PlayerViewModel                                      │
│                │                                              │
└────────────────┼──────────────────────────────────────────────┘
                 │
       ┌─────────┼──────────┐
       ▼         ▼          ▼
 AudioService  Waveform   ProjectStore
       │        Service       │
       │          │           └── JSON
       │          │
       │       AudioDecoder
       │        ├── WAV
       │        └── MP3
       │
       ▼
  IAudioEngine
       │
       └── Plugin.Maui.Audio   ← MVP
```

Je mettrais **une interface `IAudioEngine` dès le début** :

```csharp
public interface IAudioEngine
{
    TimeSpan Position { get; }
    TimeSpan Duration { get; }
    bool IsPlaying { get; }

    Task LoadAsync(Stream audio);
    void Play();
    void Pause();
    void Seek(TimeSpan position);
    void SetSpeed(double speed);

    void SetLoop(TimeSpan? start, TimeSpan? end);
}
```

La raison est importante : `Plugin.Maui.Audio` est très bien adapté au MVP et prend en charge Android, iOS/Mac Catalyst et Windows avec les formats audio supportés par les moteurs natifs. Son API fournit `CurrentPosition`, `Seek()`, `Speed` et `Loop`. En revanche, son `Loop` correspond à la répétition du **fichier en entier**, pas à une boucle arbitraire A→B. citeturn110699view1turn957387view0

### Boucle A → B

Pour V1 :

```text
Play section
    ↓
Seek(A)
    ↓
Play
    ↓
Position >= B ?
    ├── non → continuer
    └── oui → Seek(A)
               ↓
             continuer
```

Donc un `LoopController` surveille la position indépendamment de l'UI :

```csharp
while (player.IsPlaying && activeLoop is not null)
{
    if (player.Position >= activeLoop.End)
        player.Seek(activeLoop.Start);

    await Task.Delay(20);
}
```

C'est suffisant pour valider le produit.

Il faut cependant prévoir que cette approche **ne garantit pas une boucle musicalement “sample-perfect”**. C'est une déduction du niveau d'abstraction utilisé : le plugin s'appuie sur les lecteurs audio des différentes plateformes et n'expose qu'un `Seek(seconds)`. citeturn110699view1turn957387view0 Si tes enfants remarquent un petit “trou” au raccord A/B, `IAudioEngine` te permettra ensuite de remplacer cette partie par un moteur natif spécialisé sans réécrire l'application. Android Media3, par exemple, possède des mécanismes de clipping d'un média et des modes de répétition natifs. citeturn358456search26turn358456search9

## Waveform : je ne stockerais pas une image

Je stockerais des **peaks** :

```csharp
public sealed record WaveformData(
    TimeSpan Duration,
    float[] Min,
    float[] Max
);
```

Lors de l'import :

```text
MP3/WAV
   ↓
decode PCM
   ↓
échantillons
   ↓
regrouper par fenêtres
   ↓
min/max
   ↓
[-0.81,+0.72]
[-0.45,+0.55]
[-0.91,+0.88]
...
```

Puis le dessin est fait dynamiquement.

Pour MP3, **NLayer** est intéressant ici : c'est un décodeur MPEG/MP3 entièrement managed qui peut retourner directement les samples PCM en `float[]`. citeturn990125search0 Pour WAV, le parsing est beaucoup plus simple; `NAudio.Core` peut également fournir les lecteurs WAV nécessaires. Le projet `NAudio.WaveFormRenderer` montre d'ailleurs précisément une architecture “decode → peak calculation → rendering” et explique comment utiliser WAV ou MP3/NLayer hors Windows. citeturn110699view2

Je ne reprendrais cependant **pas son rendu `System.Drawing`**. Seulement l'idée du calcul des peaks.

Pour afficher :

**SkiaSharp + `SKCanvasView`**.

C'est exactement le type de contrôle adapté : dessin custom 2D, invalidation rapide et événements tactiles; si un jour la quantité de dessin devient importante, `SKGLView` fournit une option accélérée GPU. citeturn961825search7

Cela rend simples :

```text
waveform
playhead
marqueurs
zone A/B semi-transparente
labels
grille temporelle
zoom
pan
touch/drag
```

sans créer des centaines de contrôles MAUI.

## Interaction avec la waveform

Je ferais de `WaveformView` un composant complètement indépendant :

```csharp
public sealed class WaveformView : SKCanvasView
{
    public WaveformData? Waveform { get; set; }

    public TimeSpan Position { get; set; }

    public TimeSpan? SelectionStart { get; set; }
    public TimeSpan? SelectionEnd { get; set; }

    public IReadOnlyList<Section> Sections { get; set; }

    public event EventHandler<TimeSpan>? SeekRequested;
    public event EventHandler<LoopChangedEventArgs>? LoopChanged;
}
```

Et toute conversion devient :

```text
time → X

x = (time / duration) * waveformWidth
```

inversement :

```text
X → time

time = (x / waveformWidth) * duration
```

Donc toucher la waveform = seek, déplacer A/B = modifier la boucle, déplacer un marqueur = modifier la section.

## Modèle de données

Je garderais ça très petit :

```csharp
public sealed class PracticeProject
{
    public Guid Id { get; init; }

    public string Title { get; set; } = "";
    public string AudioFile { get; set; } = "";

    public List<Section> Sections { get; set; } = [];

    public double PlaybackSpeed { get; set; } = 1.0;
}

public sealed class Section
{
    public Guid Id { get; init; }

    public string Name { get; set; } = "";
    public TimeSpan Start { get; set; }
    public TimeSpan End { get; set; }

    public bool IsFavorite { get; set; }
}
```

Je n'utiliserais **pas SQLite au début**.

```text
AppData/
  songs/
    abc123.mp3

  projects/
    abc123.json

  waveforms/
    abc123.waveform
```

Ça suffit largement et rend le projet très facile à debugger.

## Import

MAUI fournit `FilePicker` directement. Il fonctionne sur les plateformes MAUI principales et permet de filtrer les types de fichiers. Il faut utiliser `OpenReadAsync()` plutôt que supposer que `FullPath` est un vrai chemin de fichier, particulièrement sous Android. citeturn725907search0

Flow :

```text
[Choisir un morceau]
        ↓
FilePicker
        ↓
OpenReadAsync()
        ↓
copie vers AppData/songs/
        ↓
AudioService.Load()
        ↓
WaveformService.AnalyzeAsync()
        ↓
cache waveform
        ↓
affichage
```

L'analyse de waveform peut s'effectuer une seule fois à l'import.

## Stack que je choisirais

| Élément | Technologie |
|---|---|
| Framework | **.NET 10 + MAUI 10** |
| UI | XAML |
| Architecture UI | **CommunityToolkit.Mvvm** |
| Waveform | **SkiaSharp `SKCanvasView`** |
| Playback V1 | **Plugin.Maui.Audio** |
| MP3 → PCM | **NLayer** |
| WAV → PCM | NAudio.Core / lecteur WAV maison |
| Import | MAUI `FilePicker` |
| Projets / sections | `System.Text.Json` |
| Tests | xUnit pour logique sections/waveform |
| DI | `Microsoft.Extensions.DependencyInjection` intégré MAUI |

`CommunityToolkit.Mvvm` est le toolkit MVVM moderne de Microsoft et fonctionne indépendamment du framework UI, donc il se prête bien à la séparation ViewModel/services ici. citeturn961825search2

### Ordre de développement

Je ferais le prototype dans cet ordre :

1. **MP3/WAV → Play/Pause/Seek**
2. **waveform statique**
3. playhead qui suit l'audio
4. toucher waveform → seek
5. poignées **A / B**
6. loop A→B
7. transformer A/B en **Section**
8. sauvegarde/restauration du projet
9. vitesse 0.5× / 0.75× / 1×
10. zoom/pan de la waveform

À la fin de l'étape 6, tu as déjà l'application réellement utile.

Le point architectural que je considérerais comme le plus important est donc : **ne pas coupler `WaveformView`, `LoopController` et `Plugin.Maui.Audio`**. Si le looping de `Plugin.Maui.Audio` est assez précis, tu gardes une app extrêmement simple. Sinon, seule l'implémentation de `IAudioEngine` change.


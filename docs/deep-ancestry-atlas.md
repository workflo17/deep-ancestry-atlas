# Deep Ancestry Atlas — build plan

An interactive 3D globe that plays back the migration of human genetic lineages across
300,000 years. This document is the research and the plan; `prototypes/deep-ancestry-atlas/`
is a working prototype of the rendering engine.

**See also [`deep-ancestry-atlas-layers.md`](deep-ancestry-atlas-layers.md)** — the catalogue of
other data layers (archaeological sites, radiocarbon, isotopes, pathogens, language,
domestication) and the argument for what turns a visualization into a research instrument.

---

## 1. The thing nobody tells you first

**You cannot download migration paths.** They do not exist as a dataset. What exists is:

- **Points in space-time.** Ancient remains that were dated and genotyped: a latitude, a
  longitude, a date in years before present, and a genome.
- **A tree.** The haplogroup phylogeny — which lineage split from which, and roughly when.

A migration path is what you get when you *combine* those two and infer the missing middle.
Every arc on every "human migration map" you have ever seen is a drawn inference, usually
drawn by hand, usually with no uncertainty attached.

So the app has a core algorithm, and it is not a rendering algorithm:

```
dated georeferenced genomes  +  dated phylogeny
        ↓  attach samples to tree nodes
        ↓  infer each ancestral node's location          ← the scientific crux
        ↓  route each branch over the landscape of its own era
   a path network with a start date, an end date, and an error envelope
```

Get that pipeline right and the visualization is the easy half. Get it wrong and you have
built a very beautiful lie. Almost all the intellectual risk in this project is in step 3.

### Three tiers, in order of ambition

| Tier | What it draws | Inference | Honesty |
|---|---|---|---|
| **1 — Observed** | Dated sample points appearing and fading as you scrub time. No paths. | None | 100% data |
| **2 — Lineage paths** | The phylogeny itself, laid on the globe: each branch runs from its ancestor's inferred location to its descendant's. | Ancestral location estimation | Defensible, uncertainty quantifiable |
| **3 — Routed paths** | Branches follow least-cost routes over the paleo-landscape of their own date — bending around ice, hugging coastlines, waiting for Beringia. | + cost-surface routing | Best-looking *and* most defensible, because the route respects real terrain |

Tier 1 is a weekend. Tier 2 is the product. Tier 3 is what makes it unforgettable.

---

## 2. Data you need, and where it actually is

### 2.1 The one file that matters

**Allen Ancient DNA Resource (AADR)** — Reich Lab, Harvard. Current release **v66.0
(13 April 2026)**: 19,119 sequences representing **17,634 ancient individuals**, plus up to
6,399 present-day individuals. Released every few months, DOI-versioned on Harvard Dataverse.

The genotype files are large (1240K panel ≈ 1.24M SNPs; Human Origins panel ≈ 600K SNPs, in
EIGENSTRAT and PLINK). **You do not need them for Tiers 1 or 2.**

What you need is the **`.anno` annotation file** — a single TSV with ~35 columns, including:

- latitude and longitude
- date in years BP (with the calibrated 95.4% interval, and the posterior mean and SD, for
  radiocarbon-dated individuals)
- **Y-chromosome haplogroup** and **mtDNA haplogroup**
- Group ID (the archaeological/population label)
- coverage and assay metrics

That is the entire v1 dataset in one file: ~17,600 rows of `(lat, lon, date±σ, Y-hap,
mt-hap, culture)`. It is tens of megabytes. You can parse it in an afternoon.

> Since v52.2 the AADR also ships a mitochondrial repository — mtDNA genomes for 4,122
> ancient individuals.

### 2.2 The tree

Haplogroup nomenclature *is* the tree topology. `R1b1a1b1a1a2` is literally a path from the
root: R → R1 → R1b → R1b1 → … Each added character is a branch. This means you can build the
topology by string parsing, and you only need external data for the **dates**.

- **Y-DNA:** YFull YTree (**v14.05.00**, August 2026) publishes both a "formed" age and a
  TMRCA per node; updated roughly monthly since 2015. ISOGG's tree for nomenclature
  reconciliation. FTDNA Discover for cross-checking ages.
- **mtDNA:** PhyloTree build 17 is the standard reference (frozen — plan for it not to move).

Budget real time for a **nomenclature normalizer**. AADR haplogroup calls, YFull names and
ISOGG names drift apart between versions, and a mismatched string silently drops a sample
from the tree. This is the most likely source of quiet data loss in the whole pipeline.

### 2.3 The world as it was — the visual jackpot

This is where the project stops looking like a map and starts looking like a time machine.

- **Beyer, Krapp & Manica 2020** (*Sci Data* 7:236). Global terrestrial climate, bioclimate
  and vegetation for the **last 120,000 years**, 0.5° resolution, 1–2 ka steps: monthly
  temperature, precipitation, cloud, humidity, wind; 17 bioclim variables; net primary
  productivity; leaf area index; **biomes**. On OSF (`10.17605/osf.io/p86rt`) and figshare.
- **`pastclim`** (R package) wraps it and — critically — gives you **`get_land_mask()`** and
  **`get_ice_mask()`** per time step. Your paleo-coastlines and ice sheets are a function
  call, not a research project. Also carries **Krapp et al. 2021** (800 ka, HadCM3 emulator).
- **De Groeve et al. 2022** (*Glob Ecol Biogeogr* 31:2162): global raster of coastline
  positions and shelf-sea extents since the LGM, 0.0333° cells, 500-year steps, built from
  GEBCO bathymetry plus a global relative-sea-level curve. The cleanest ready-made
  paleo-coastline product; on figshare (UvA).
- **ICE-6G_C (VM5a)**, Peltier — NetCDF, 1°×1°, ice thickness and topography through the
  deglaciation.

At the LGM (~26 ka) sea level was **>130 m below present**. That single number is why this
layer matters: Doggerland is dry land, Britain is a peninsula, Sundaland is a subcontinent,
the Persian Gulf is a river valley, and Beringia is a thousand-kilometre-wide plain. Scrub
the timeline and all of that floods in front of you. No other choice you make will buy as
much "oh —" per hour of work.

### 2.4 Supporting

- **Natural Earth** (public domain) — modern coastlines, rivers, glaciated areas. The
  110m land file is ~138 KB of GeoJSON; the prototype uses it.
- **GEBCO** — bathymetry, for deriving paleo-coastlines yourself at any sea level.
- **HGDP / SGDP / 1000 Genomes** — present-day reference populations, i.e. where lineages
  ended up.

### 2.5 The other lens: ancestry components

Modern ancient-DNA papers mostly do **not** talk in haplogroups. They talk in admixture
proportions from **qpAdm** — "this population is 45% Steppe, 35% Anatolian Neolithic farmer,
20% Western hunter-gatherer." Published examples: Sardinian early farmers ≈ 62.5% Anatolian
Neolithic + 9.7% WHG; Ötzi ≈ 90% ± 2.5% early Neolithic farmer.

This is a *fundamentally better* migration signal than haplogroups, because it measures the
whole genome rather than one locus — and it visualizes gorgeously as **flowing proportional
ribbons** rather than lines. It is Phase 5, not Phase 1, because the numbers have to be
harvested from supplementary tables paper by paper, but it is where the project gets its
second act.

---

## 3. What already exists (and the gap)

- **DORA** (*Nucleic Acids Research* 2024) — interactive map, pre-loaded with AADR plus
  CHELSA climate. Draw a region, pick a time window, export the sample subset. A research
  tool: 2D, static, selection-oriented.
- **Human AGEs** (*NAR* 2023) — spatiotemporal visualization over a graph database of
  archaeogenomic data.
- **AADR Visualizer** — an ArcGIS Experience Builder front end on the AADR.
- **MAPMIXTURE**, **ADGAP** — ancestry/admixture plotting.

All of them plot **points**. None of them animate **paths**, none reconstruct the landscape
of the era, and none are built to be watched rather than queried. That is the whole gap: the
existing tools are instruments for specialists, and there is no equivalent of a planetarium.

---

## 4. Architecture

### 4.1 Offline pipeline (Python) → static asset bundle

Do every expensive thing once, at build time, and ship JSON/binary. The app should need no
backend at all — which also means it can live on GitHub Pages forever, for free.

```
aadr_v66.anno ─┐
yfull_tree     ├─→  1. parse + normalize haplogroup names
phylotree17    │    2. attach samples to tree nodes
               │    3. infer ancestral node locations
beyer2020 ─────┤    4. build per-timeslice cost surfaces
icemasks       │    5. route each branch (A* / Dijkstra on raster)
gebco/degroeve ┘    6. emit: tree.json, samples.bin, paths.bin, coast_<t>.bin
```

**Step 3 is the crux.** Three implementations, increasing in rigor:

1. **Descendant centroid** — a node's location is the (date- and coverage-weighted) centroid
   of all samples below it. Fast, crude, and badly biased by where archaeologists dug. Fine
   for a prototype; label it as such.
2. **Continuous phylogeography** — model movement as a relaxed random walk (Brownian motion
   in lat/lon) over the dated tree, and solve for ancestral states. This is the standard
   method, borrowed from pathogen phylogeography. A lightweight version is a few hundred
   lines on a fixed tree.
3. **Full Bayesian** — BEAST's continuous diffusion models, validated against `spreaD3` /
   SPREAD4. Slow, but it gives you a genuine **posterior**, which means you can render the
   uncertainty cloud instead of pretending it is a line.

> **Known failure mode, worth reading before you trust your own output:** continuous
> phylogeography on a random walk is provably sensitive to sampling bias — the literature
> on this is titled *"getting lost on a random walk"* for a reason. Where samples are
> dense, the inferred path follows the samples, not the people. Your app should render
> sample density as a visible layer precisely so this is legible rather than hidden.

**Step 5, routing.** Build a cost surface per time slice from: slope (from paleo-elevation),
biome and NPP (Beyer2020 — deserts and ice cost more, productive grassland costs less),
ice mask (impassable), water (impassable, except short crossings), and a coastal-corridor
bonus. Then least-cost path from ancestor to descendant. Published hominin-dispersal LCP
studies use exactly this recipe — topographic roughness, drainage density and elevation —
and recover, for example, the Nile corridor and the northern Sinai as favoured routes out
of East Africa. Precompute offline; it is far too slow for the browser.

### 4.2 Renderer

**Recommendation: hand-rolled WebGL2, or bare Three.js.** Reasons, from the research:

- **deck.gl `GlobeView`** is still flagged experimental: no high-precision rendering above
  zoom 12, and — directly relevant — **`TripsLayer` trails go invisible from some angles on
  a globe**, because `GlobeView` enables back-face culling by default. Trails on a globe are
  the entire product. Do not build the core on a layer with that caveat.
- **CesiumJS** is the only library that renders a genuinely authoritative globe, but it is
  heavy, and benchmarks put it far behind MapLibre+deck.gl on large point sets.
- You need one unusual thing that no library gives you: **time as a GPU uniform**. Every
  path vertex carries its own start and end date, and a single `uNow` uniform decides what
  has grown. That makes scrubbing 300,000 years cost the same as scrubbing one year, with
  zero CPU work per frame. It is ~20 lines of GLSL and it is the reason the prototype
  scrubs smoothly.

**Techniques that buy the most visual impact per hour:**

| Technique | Effect |
|---|---|
| Time as a vertex-shader uniform | Instant, free scrubbing over the whole dataset |
| Path atlas in a float texture; particles as `(pathID, phase)` | Millions of flowing motes, zero CPU per frame |
| Per-slice elevation texture + sea level as a uniform | Coastlines that **animate**: Doggerland drowns while you watch |
| Ice mask as a blended overlay | Ice sheets breathe in and out across the glacial cycle |
| Great-circle arcs lifted by distance | Long migrations arc high; local ones hug the ground |
| Uniform-density land points (Fibonacci sphere) | An 8 KB globe, no texture, no pole bunching |

That last one is worth stealing: sample a Fibonacci sphere, test each point against land
polygons **once, offline**, and ship only a bitmask. 48,000 points → 8,000 bytes of base64,
and the point positions are regenerated from the index at load. The prototype's entire
geography is 8 KB.

### 4.3 Scale check

Nothing here is big. 17,600 sample points, a few thousand branches × 128 samples ≈ 500k
vertices. That is a rounding error for a GPU. **This project is not performance-constrained
— it is inference-constrained and design-constrained.** Do not spend time optimizing.

---

## 5. What makes it addictive

Addictive is a design problem, not a graphics problem. Specifics:

1. **Time is the primary control, not a filter.** Big scrubber, always visible, plays on its
   own. The app should be watchable with your hands off it.
2. **Warp the time axis.** Linear time wastes 90% of the slider on the Middle Pleistocene.
   A power-law mapping (`age = MAX · (1−p)^2.6`) gives the last 20,000 years — where almost
   everything happens — most of the bar.
3. **Name things as they appear.** Labels that fade in the moment a lineage is born make
   scrubbing feel like watching a world get populated.
4. **One click collapses the world to one story.** Select a lineage: everything else dims,
   its ancestry chain lights up root-to-tip, the camera flies to it.
5. **Ride the path.** A "follow" camera that travels along a branch as time advances.
6. **Set-piece moments, and build the schedule around them.** Beringia opening ~15.5 ka.
   Doggerland drowning ~8 ka. The Sahul crossing ~50 ka — open water, no land bridge, ever.
   The Bantu expansion crossing a continent in two millennia. The Austronesian leap from
   Taiwan to Rapa Nui. Steppe ancestry arriving in Britain and replacing most of the
   existing paternal line inside a few centuries.
7. **"Find my line."** Enter a haplogroup from a consumer test, watch your own maternal or
   paternal line light up from the root. This is the single highest-engagement feature and
   also the one that most needs the caveat in §6 attached to it — literally on the same
   screen.

---

## 6. Integrity constraints — which are design constraints

These are not a disclaimer page. Each one changes what the interface may draw.

**A haplogroup is not a population, an ethnicity, or a "race."** It is *one* line of descent
— purely paternal or purely maternal — out of the exponentially many ancestors each person
has. Two people in the same haplogroup can share no genealogical ancestor in recorded time.
Haplogroups long predate every modern nation and identity. This is the single most common
misreading of exactly the kind of map this app draws, so the UI has to state it where people
actually look, not in an About page.

**Absence of data is not absence of people.** The AADR is heavily Eurasian; DNA survives
badly in warm, humid ground, so the tropics are sparse for reasons of chemistry, not
history. **Render sample density as a first-class layer**, so an empty region reads as "no
one has sampled here" rather than "no one lived here."

**Dates have error bars, so draw them.** A radiocarbon date is a distribution. A sample
should be a smear in time, not a dot. The AADR gives you the posterior mean and SD — use them.

**Uncertainty must survive the aesthetic.** A crisp glowing arc reads as a fact. If the
underlying posterior is a 2,000 km cloud, the render has to show a cloud. Resist making the
uncertain parts prettier than the certain parts — that is the specific way this genre of
visualization lies.

**Indigenous data sovereignty is a real constraint, not a formality.** The **CARE
principles** (Collective benefit, Authority to control, Responsibility, Ethics) were written
because open-data norms — FAIR — ignore power and history. Some ancient genomic data is
deliberately access-controlled under Indigenous governance; the Aotearoa Genomic Data
Repository is the standard example, holding Māori ancestral data under community control.
Practically: use only openly released data, honour Biocultural Labels and provenance
metadata, do not scrape restricted repositories, and be careful about drawing arcs that
assert origins for living communities who have their own account of where they came from.

---

## 7. Phases

| Phase | Scope | Rough effort |
|---|---|---|
| **0 — Engine** | Globe, time scrubber, tree-as-network, particles, selection. | **done** |
| **1 — Real points** | Real AADR v66: 19,029 dated georeferenced individuals, via the Poseidon `aadr-archive` (the Reich Lab host is unreachable from a sandbox; Poseidon republishes the same release as `.janno`). | **done** |
| **2 — Real tree** | 701 Y and 705 mtDNA clades prefix-parsed from AADR haplogroup calls; centroid **and** oldest-member position estimators; oldest-observed dates rather than TMRCAs. | **done** |
| **3 — Paleo-world** | `pastclim` land/ice masks per slice; animated coastlines and ice sheets. **Highest impact per hour of the whole plan.** | ~3–4 weeks |
| **4 — Routing** | Cost surfaces, least-cost paths, offline precompute. | ~4 weeks |
| **5 — Better inference** | Continuous phylogeography; render the posterior, not a line. | ~3–4 weeks |
| **6 — Ancestry components** | qpAdm proportions as flowing ribbons — the modern framing. | open-ended |
| **+ Evidence layers** | Radiocarbon, places, routes, language, societies, pathogens; coverage views; cross-layer query with cited export. | **done** |
| **7 — Stories** | Guided tours of the set pieces; "find my line"; share links. | ~2 weeks |

Running alongside these, the non-genetic data layers have their own sequence — radiocarbon
first, then deep-time archaeology, then individual isotope mobility. See the layers document.

Phase 1 alone is already a better public artifact than anything currently online. Ship at
every phase boundary.

---

## 8. Risks

- **Ancestral location inference is the whole ballgame** and the easiest thing to get
  quietly, confidently wrong. Budget for reading, not just coding. Validate Tier-2 output
  against known cases (steppe → Europe, Beringia → Americas) before trusting it anywhere.
- **Sampling bias masquerading as history.** Mitigate with the density layer; it is the
  honest fix and it also looks good.
- **Nomenclature drift** between AADR calls and tree versions. Write the normalizer early
  and make it *report* how many samples it failed to place.
- **Scope gravity.** Tier 3 is seductive. Tier 1 shipped beats Tier 3 abandoned.
- **Publishing responsibly.** Before anything public names living populations, re-read §6.

---

## 9. The prototype

`prototypes/deep-ancestry-atlas/index.html` — one file, no build step, no dependencies, no
network requests except a web font. Open it directly in a browser.

**What is real:**

- Hand-rolled WebGL2: globe, atmosphere, star field, arc network, GPU particle flow.
- **32,902 ancient places from the Pleiades gazetteer** (v4.1, CC BY 3.0), carried at full
  coordinate precision with the gazetteer's own `location_precision` flag preserved and
  rendered — rough positions are drawn dimmer and flagged in the inspector.
- **A working cross-layer query:** select a lineage node, set a radius, and it returns the
  matching places broken down by class, exportable as CSV with a citable Pleiades URI on
  every row.
- Geography is genuine Natural Earth 110m land, resampled to 48,000 uniform points and
  shipped as an 8 KB bitmask.
- The **engine is the real engine**: dated tree → great-circle branches → time as a GPU
  uniform → particles riding the grown portion. Swapping in AADR-derived paths is a data
  change, not an architecture change.
- Categorical colours were computationally validated for colour-vision deficiency at
  all-pairs separation against the near-black surface (worst CVD ΔE 9.4 against a target of
  8.0; worst normal-vision ΔE 15.4 against a floor of 15.0), which is why they are not the
  obvious hues.

**What is a scaffold:** only the *reference backbone* mode — the ~75 Y and ~41 mtDNA hand-entered
nodes — which the interface labels as not-observed. The default tree is derived from real data.

### What the data turned out to say

Three findings fell out of building it, all now surfaced in the interface rather than buried:

- **99.3% of ancient genomes are younger than 15,000 BP** (radiocarbon: 95.8%). The deep-time
  story this project exists to tell rests on well under 1% of the evidence. The coverage tab
  plots this per layer, on a log scale, because it should condition every other view.
- **The observed Y tree is a forest, not a tree.** Its macro-haplogroups have no connections
  above them: the AADR's nomenclature does not encode the deep backbone, and no sampled
  individual is basal enough to bridge them. The textbook single-rooted tree is an inference
  the sampled record does not contain — which is exactly why the reference mode is labelled.
- **The oldest genome in the AADR is 185,000 BP at 51.40°N, 84.67°E** — Denisova Cave. The
  compendium reaches back past our own species, and a naive time axis will happily draw it.

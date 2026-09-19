# Deep Ancestry Atlas

An open-source research instrument for human migration: **262,000 georeferenced records** from
eight published datasets on one 3D globe, a lineage tree computed from real ancient genomes, and
a cross-layer query that exports results with their citations attached.

One HTML file, hand-rolled WebGL2, no framework and no dependencies. The data arrives as static
files, so the whole thing is a directory you can serve from anywhere.

Live: **[deep-ancestry-atlas-workflo17.vercel.app](https://deep-ancestry-atlas-workflo17.vercel.app)** ·
Sources and obligations: [`ATTRIBUTION.md`](ATTRIBUTION.md) ·
Plan and layer research: [`docs/`](docs/)

![Every layer on at 2,500 BP: 262,000 records on the globe, and the strata timeline showing sampling density in every period](docs/atlas.jpg)

---

## The premise

**You cannot download migration paths.** They are not a dataset. What exists is points in
space-time — dated, georeferenced ancient genomes — and a tree of which lineage split from which.
A path is what you get by inferring the missing middle, and every migration map you have ever
seen is that inference, drawn by hand, with the uncertainty left off.

So this tool is built to keep the inference visible as an inference. It will not draw you a
confident arrow it cannot support, and where it has to guess it tells you how much of the answer
is coming from the guess.

## Using the atlas

- **Search** (`/`) finds lineages on both markers, places, samples and named periods; pick one and
  the globe flies to it.
- **The strata timeline** along the bottom is the main control. Named periods are drawn as bands,
  and the sediment inside them is the density of dated records for every layer that is on — so the
  sampling bias stays in view the whole time. Drag it, press `space` to play, `←` `→` to step.
- **The panel** has four tabs. *Layers* switches evidence on and off, with per-class filters, the
  AADR quality grades and the date range. *Lineages* picks the marker, the tree source, the
  placement estimator and the detail cut. *Selection* is the dossier for whatever you clicked: a
  clade's route from the root, a record's citation, and every loaded layer within a radius,
  exportable as CSV. *Sources* carries the licences and the coverage chart.
- **Click** anything on the globe to inspect it; hover to identify it. `Esc` clears the selection,
  `L` hides the panel, `?` opens the guide.
- **The URL is the view.** Marker, tree, placement, selection, time, camera and layers all live in
  the hash, so a link reproduces exactly what you were looking at. The link button copies it.

![Y-DNA R1b1a1b traced from its root at 4,200 BP: the dossier, the route card and its waypoints on the globe](docs/atlas-route.jpg)

## Layers

| Layer | Records | Source | Licence |
|---|---:|---|---|
| Ancient genomes | 19,029 | AADR v66 via Poseidon | cite the release DOI ×2 |
| Radiocarbon dates | 175,426 | p3k14c (PEOPLE 3000) | MIT code · tDAR data |
| Ancient places | 32,902 | Pleiades gazetteer v4.1 | CC BY 3.0 |
| Roads & routes | 3,840 polylines | AWMC / Barrington Atlas | **ODbL 1.0 — share-alike** |
| Languages | 26,696 | Glottolog CLDF | CC BY 4.0 |
| Documented societies | 1,291 | D-PLACE Ethnographic Atlas | CC BY 4.0 |
| Ancient metagenomes | 3,241 | AncientMetagenomeDir | CC BY 4.0 |
| Land outlines | 48,000 points | Natural Earth 110m | public domain |

Read [`ATTRIBUTION.md`](ATTRIBUTION.md) before redistributing any built data. The route layer is
share-alike and MIT on the code does not launder that.

## The tree is computed, not typed in

Haplogroup nomenclature **is** the topology — `R1b1a1` nests inside `R1b1` inside `R1b` — so the
tree is built by prefix-parsing the AADR's own Y and mtDNA calls across 19,029 dated individuals.
701 Y clades and 705 mtDNA clades fall out.

Two constraints are baked into the result and stated in the interface:

- **A node's date is its oldest observed member, not a TMRCA.** A clade is always older than the
  oldest person we happened to dig up carrying it. Because membership is nested, a parent's
  oldest member is automatically at least as old as any child's, so branches run forward in time
  without needing an assumption.
- **A node's position is a summary of where its carriers were excavated**, which is not where the
  clade arose. Both estimators ship — spherical centroid, and the location of the single oldest
  member — because they disagree, and the disagreement is the point.

A **reference backbone** mode carries the hand-entered published tree instead, for the deep
structure the sampled record cannot reach. It is labelled as not-observed.

## Tracing a lineage

Select a clade and the **route** card lays out its path from the root: numbered waypoints on the
globe, every hop with position, leg distance, elapsed time, implied pace and member count,
exportable as CSV. **Fly the route** walks the camera through the waypoints while the clock
advances with it.

The card is built to argue with itself:

- It reports path length under **both** estimators and flags disagreement past 1.6×. Y-DNA
  `N1a1a1a1a` is 1,757 km by centroid and 10,063 km by oldest sample — a 5.7× gap that is route
  supplied by the choice of statistic rather than by data.
- It flags legs spanning **zero years**, where parent and child share one oldest sampled
  individual and the leg therefore dates nothing.
- It **refuses an implausible pace**. `Q1b1a1a` on the oldest-sample estimator implies 11,508 km
  per millennium. The card says plainly that this is not a rate of travel: Q's oldest sampled
  carrier is Anzick-1, in Montana, so the waypoints are not in ancestral order at all. A parent
  clade's oldest carrier can sit deep inside a descendant population.

## Filters

- **Only carriers of the selected clade** — matches each individual's own haplogroup call against
  the clade tree, collapsing the evidence layer to exactly the people carrying that lineage
  (`R1b1a1b1a1a2`: 19,029 genomes → 725). Matching walks the tokenised haplogroup path rather
  than string prefixes, because mtDNA **H11 is a sibling of H1, not its descendant** — a
  `startsWith` would silently produce wrong carrier sets.
- **Date range** — a hard filter in years BP; the scrubber then animates inside it.
- **Genome quality** — the AADR's own assessment grades.
- **Per-layer class filters**, and a **search** that reaches below the detail cut.

## The cross-layer query

The thing no existing tool does. Pick a clade or a record, set a radius, and every loaded layer
answers at once — 11,595 records across six datasets within 500 km of `R1b1a1`. Export is CSV
carrying layer, source, licence, coordinates, date, uncertainty, distance and a **resolvable
reference per row**. If you cannot cite it, it is not a research tool.

## What the data says, whether or not you wanted to know

- **99.3% of ancient genomes are younger than 15,000 BP** (radiocarbon: 95.8%). The deep-time
  story this project exists to tell rests on well under 1% of the evidence. The timeline draws it
  as sediment under every period and the Sources tab plots it per layer on a log scale, because
  it should condition every other view.
- **The observed Y tree is a forest, not a tree.** Its macro-haplogroups have no connections above
  them: the AADR's nomenclature does not encode the deep backbone and no sampled individual
  bridges it. The single-rooted textbook tree is an inference the sampled record does not contain.
- **Pleiades lights up the Mediterranean and nothing else.** That is where classicists worked, not
  where people lived.

## Build it

```sh
cd build
./fetch-sources.sh          # every upstream source; all public, no keys
pip install pyreadr
python3 build-tree.py       # AADR haplogroup calls -> clade trees
python3 build-haplink.py    # genome -> clade index, for lineage filtering
python3 build-layers.py     # everything else -> out/
cd .. && mkdir -p d && cp build/out/* d/
python3 -m http.server 8000
```

`index.html` fetches from a sibling `d/`, so it needs a server, not `file://`. Any static host
works; there is no build step and nothing to install for the page itself.

## Formats

Point layers are 15-byte records — `int32` lat and lon at 1e-5°, `int32` years BP, `uint16`
uncertainty, `uint8` class and flags — base64'd into `.txt`, because artifact hosting serves no
binary media type. Metadata rides in tab-separated sidecars loaded lazily, only when a record is
inspected or a query is exported. Geography is a 48,000-point Fibonacci-sphere bitmask: 8 KB for
the whole world, uniform density, no polar bunching.

Categorical colour was computed rather than chosen. Both palettes — eight lineage groups and
seven layers — were validated for colour-vision deficiency at all-pairs separation against the
near-black surface (lineages: worst CVD ΔE 9.4 against an 8.0 target; layers: 10.0). That is why
they are not the obvious hues.

## Known gaps

Four datasets would materially improve this and are not in it, because they were unreachable from
the sandbox this was built in: **paleoclimate rasters** (animated coastlines and ice sheets — the
biggest remaining visual upgrade), the **28,347-value bioavailable strontium compilation**
(individual-scale mobility, the genuinely novel view nobody has built), **Neotoma**
(palaeoecology), and **ROAD** (deep-time archaeology — the most damaging gap, since Pleiades
starts around 1200 BCE and the migration story is largely over by then).

The honest next step for the science is to replace both position estimators with a Brownian-bridge
ancestral-state reconstruction. Centroid compresses routes toward zero, oldest-sample is hostage
to a single skeleton, and neither is defensible as *the* answer. The fix is a posterior rather
than a point — which is also what would let the globe render uncertainty as a cloud instead of a
line.

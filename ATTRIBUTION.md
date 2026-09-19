# Sources, licences and obligations

This project redistributes **derived databases** built from eleven upstream sources: eight that
are evidence, and three that draw the ground the evidence sits on. Each carries its own terms, and
two of them impose obligations beyond attribution. Every licence below was read from the source's
own `LICENSE` file, README, metadata record or landing page, not from memory.

If you fork, deploy or publish this, these terms travel with the data.

---

## The code

Everything in this repository that is not derived data — the page, the shaders, the build
pipeline — is **MIT**. See `LICENSE`.

## The derived data

`build/` regenerates every data file from the upstream sources, and the built output **is**
committed under `d/` so the site deploys without a build step. That means this repository
redistributes derived databases, and everything below applies to it directly — not only to
downstream forks.

### 1. Ancient genomes — AADR v66

Obtained through the [Poseidon `aadr-archive`](https://github.com/poseidon-framework/aadr-archive),
which republishes the Allen Ancient DNA Resource as Poseidon packages.

**The AADR requires two citations, not one:**

> Mallick, S., & Reich, D. (2024). *The Allen Ancient DNA Resource (AADR): A curated compendium of
> ancient human genomes*, v66.0. Harvard Dataverse. https://doi.org/10.7910/DVN/FFIDCW
>
> Mallick, S., Micco, A., Mah, M., Ringbauer, H., Lazaridis, I., Olalde, I., Patterson, N., &
> Reich, D. (2024). The Allen Ancient DNA Resource (AADR) a curated compendium of ancient human
> genomes. *Scientific Data* 11. https://doi.org/10.1038/s41597-024-03031-7

Cite the specific version used (this build: **v66_p1_1240K**). Cite Poseidon as the route, not as
the source.

### 2. Radiocarbon — p3k14c

Package code MIT; the database is archived at tDAR.

> Bird, D., Miranda, L., Vander Linden, M., et al. (2022). p3k14c, a synthetic global database of
> archaeological radiocarbon dates. *Scientific Data* 9, 27.
> https://doi.org/10.1038/s41597-022-01118-7 · data: https://doi.org/10.48512/XCV8459173

### 3. Ancient places — Pleiades v4.1 · **CC BY 3.0**

> *Pleiades: A Gazetteer of Past Places.* Institute for the Study of the Ancient World, NYU.
> https://pleiades.stoa.org

Pleiades additionally **asks to be told about reuse** — `pleiades.admin@nyu.edu` — because reuse
reports are what justify its continued funding. If you deploy this publicly, send that email. It
costs nothing and it is the reason the gazetteer still exists.

### 4. Roads and routes — AWMC · **ODbL 1.0 — share-alike**

> *Ancient World Mapping Center.* University of North Carolina at Chapel Hill.
> https://github.com/AWMC/geodata — derived from the *Barrington Atlas of the Greek and Roman
> World* and from AWMC modifications to OpenStreetMap.

**This is the one with teeth.** The [ODbL](https://opendatacommons.org/licenses/odbl/1-0/) is
share-alike for databases: the route layer this project builds is a *Derivative Database*, so if
you publicly distribute it you must

- release **that derived database** under ODbL 1.0,
- keep the attribution to AWMC, the Barrington Atlas and OpenStreetMap visible, and
- offer the derived database in a machine-readable open form.

MIT on the code does **not** launder this. This repository satisfies it by naming AWMC, the
Barrington Atlas and OpenStreetMap in the page's own provenance panel and in this file, shipping
`d/routes.bin.txt` in an open format documented in the README, and placing that derived route
database under **ODbL 1.0** — which it is, regardless of the MIT licence on the code around it.

### 5. Languages — Glottolog CLDF · **CC BY 4.0**

> Hammarström, H., Forkel, R., Haspelmath, M., & Bank, S. *Glottolog.* Max Planck Institute for
> Evolutionary Anthropology. https://glottolog.org

### 6. Societies — D-PLACE Ethnographic Atlas · **CC BY 4.0**

> Kirby, K. R., et al. (2016). D-PLACE: A Global Database of Cultural, Linguistic and
> Environmental Diversity. *PLOS ONE* 11(7): e0158391.
> https://doi.org/10.1371/journal.pone.0158391

### 7. Ancient metagenomes — AncientMetagenomeDir · **CC BY 4.0**

> Fellows Yates, J. A., et al. *AncientMetagenomeDir.* SPAAM Community.
> https://github.com/SPAAM-community/AncientMetagenomeDir

### 8. Land outlines — Natural Earth · **public domain**

> https://www.naturalearthdata.com · via https://github.com/nvkelso/natural-earth-vector

The 110m land polygons make the 48,000-point dotted globe that draws while the rasters load. The
10m set does more. Its coastline is the thin modern outline on the globe, and its lakes are drawn
as water at every date. Its land polygons, with the minor islands, are the mask that stops dry
ground below sea level (the Dutch polders, the Caspian depression, Qattara) from flooding when the
sea moves. The 10m Antarctic ice shelves fill in what the PaleoMIST grounding line leaves bare.

### 9. Terrain and sea floor: ETOPO 2022 · **not copyrighted in the US**

The 60 arc-second surface-elevation grid, downsampled to 4096 × 2048 and 2048 × 1024.

> NOAA National Centers for Environmental Information. 2022: *ETOPO 2022 15 Arc-Second Global
> Relief Model.* NOAA National Centers for Environmental Information.
> https://doi.org/10.25921/fd45-gt74. Accessed 2026-09-19.

NOAA's metadata record states the terms: "Produced by the NOAA National Centers for Environmental
Information. Not subject to copyright protection within the United States." It asks for the
citation above with an access date, and adds "Not to be used for navigation." The record is silent
about other jurisdictions, so treat the citation as the obligation everywhere.

### 10. Sea level: Spratt & Lisiecki 2016 · **cite the paper**

> Spratt, R. M., & Lisiecki, L. E. (2016). A Late Pleistocene sea level stack. *Climate of the
> Past* 12, 1079-1092. https://doi.org/10.5194/cp-12-1079-2016 (the paper is CC BY 3.0)
>
> Data: NOAA World Data Service for Paleoclimatology, study 19982.
> https://www.ncei.noaa.gov/access/paleo-search/study/19982. Accessed 2026-09-19.

The data file's own header sets the terms: "Please cite original publication, online resource and
date accessed when using this data." The atlas ships 301 values of the short stack, 0 to 300 ka,
with their standard deviations, in `d/earth.json`.

One change is made to them, and that file declares it: the values for 0 to 5 ka are drawn as 0 m.
The authors scaled the stack to 0 m at 5 ka, which leaves +3 to +8 m for the four thousand years
since. That is inside the stack's own 95% interval of zero and contradicts what Holocene
shorelines record, and it would have put today's coast under water. (The DOI printed in NOAA's
file header, 10.5194/cp-12-1-2016, resolves to a different article. The one above is the paper.)

### 11. Ice sheets: PaleoMIST 1.0 · **CC BY 4.0**

> Gowan, E. J., Zhang, X., Khosravi, S., Rovere, A., Stocchi, P., Hughes, A. L. C.,
> Gyllencreutz, R., Mangerud, J., Svendsen, J.-I., & Lohmann, G. (2021). A new global ice sheet
> reconstruction for the past 80 000 years. *Nature Communications* 12, 1199.
> https://doi.org/10.1038/s41467-021-21469-w
>
> Gowan, E. J. (2019). *Global ice sheet reconstruction for the past 80000 years* [dataset].
> PANGAEA. https://doi.org/10.1594/PANGAEA.905800

The licence is stated on the PANGAEA landing page. The atlas uses the ice **margins** only (North
America with Greenland, Eurasia, Antarctica and Patagonia, in the minimal MIS 3 scenario),
rasterised into `d/ice.png`. That is a changed version of the original, which CC BY asks you to
say.

PaleoMIST stops at 80,000 BP. Whatever the atlas draws before that is an analogue picked from
these slices by sea level. It is the atlas's guess, and it should not be cited as Gowan et al.'s
reconstruction.

## Considered and not shipped

Two sources the globe could have used were left out, because their terms could not be verified
from their own pages.

**Yale Bright Star Catalogue (BSC5).** It is often described as public domain, but neither
distributor says so. The CDS ReadMe for catalogue V/50 carries no licence, the CDS terms for
VizieR say catalogues are "free of usage in a scientific context" with citation, and NASA
HEASARC's page states none. That is not an open licence, so the sky stays procedural.

**Batchelor et al. 2019**, *The configuration of Northern Hemisphere ice sheets through the
Quaternary.* The paper is CC BY 4.0, but the shapefiles sit in an OSF project (osf.io/7jen3) whose
licence field is empty. It would have covered the glacial cycles before 80,000 BP.

---

## Beyond licensing

Licence compliance is the floor, not the ceiling.

**Human remains are not just data points.** Every dot in the genomes layer was a person, and many
were excavated under arrangements their descendants had no say in.

**The CARE Principles for Indigenous Data Governance** — Collective benefit, Authority to control,
Responsibility, Ethics — exist because open-data norms (FAIR) were written without reference to
power or history. "It is publicly downloadable" and "it is mine to publish on a globe" are
different claims. Some ancient genomic data is deliberately held under community governance; the
[Aotearoa Genomic Data Repository](https://data.agdr.org.nz/) is the standard example. This
project uses only openly released data, and anyone extending it should check what they are adding
against https://www.gida-global.org/careprinciples before adding it.

**Be careful what the arcs assert.** A line drawn from one clade position to another is an
inference about where somebody's ancestors came from. Living communities have their own accounts
of that, and a glowing arc on a black globe is a rhetorically strong way to contradict them. The
interface's job — and the reason it argues with its own pace figures and flags its estimator
disagreements — is to keep that inference visible as an inference.

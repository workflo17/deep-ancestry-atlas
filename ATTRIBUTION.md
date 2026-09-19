# Sources, licences and obligations

This project redistributes **derived databases** built from eight upstream sources. Each carries
its own terms, and two of them impose obligations beyond attribution. Every licence below was
read from the source's own `LICENSE` file or README, not from memory.

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

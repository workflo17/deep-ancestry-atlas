#!/usr/bin/env bash
# Fetch every upstream source the atlas is built from. All are public.
# Run from this directory; writes into ./raw and ./clones.
set -euo pipefail
mkdir -p raw clones

echo "== Pleiades gazetteer v4.1 (CC BY 3.0) =="
P=https://raw.githubusercontent.com/isawnyu/pleiades.datasets/main/data/gis
for f in places.csv places_place_types.csv place_types.csv; do
  curl -fsSL -o "raw/pl_$f" "$P/$f"
done

echo "== p3k14c radiocarbon (179,689 dates) =="
curl -fsSL -o raw/p3k14c_data.rda \
  https://raw.githubusercontent.com/people3k/p3k14c/main/data/p3k14c_data.rda

echo "== Glottolog (CC BY 4.0) =="
curl -fsSL -o raw/glottolog.csv \
  https://raw.githubusercontent.com/glottolog/glottolog-cldf/master/cldf/languages.csv

echo "== D-PLACE Ethnographic Atlas (CC BY 4.0) =="
curl -fsSL -o raw/dplace_soc.csv \
  https://raw.githubusercontent.com/D-PLACE/dplace-data/master/datasets/EA/societies.csv

echo "== AncientMetagenomeDir (CC BY 4.0) =="
A=https://raw.githubusercontent.com/SPAAM-community/AncientMetagenomeDir/master
curl -fsSL -o raw/amd_host.tsv   "$A/ancientmetagenome-hostassociated/samples/ancientmetagenome-hostassociated_samples.tsv"
curl -fsSL -o raw/amd_env.tsv    "$A/ancientmetagenome-environmental/samples/ancientmetagenome-environmental_samples.tsv"
curl -fsSL -o raw/amd_single.tsv "$A/ancientsinglegenome-hostassociated/samples/ancientsinglegenome-hostassociated_samples.tsv"

echo "== Natural Earth 110m land (public domain) =="
curl -fsSL -o raw/ne110_land.geojson \
  https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson

echo "== AADR v66 via Poseidon (clone; LFS skipped) =="
[ -d clones/aadr-archive ] || GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 \
  https://github.com/poseidon-framework/aadr-archive clones/aadr-archive

echo "== AWMC geodata — roads, canals, aqueducts, walls (ODbL) =="
# NB: ~640 MB, mostly physical-data files the atlas does not use.
[ -d clones/awmc-geodata ] || git clone --depth 1 \
  https://github.com/AWMC/geodata clones/awmc-geodata

echo
echo "Done. Now:  pip install pyreadr && python3 build-tree.py && python3 build-layers.py"

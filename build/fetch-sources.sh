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

echo "== Natural Earth 10m: coastline, land mask, lakes, Antarctic ice shelves (public domain) =="
N=https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson
for f in ne_10m_coastline ne_10m_land ne_10m_minor_islands ne_10m_lakes ne_10m_antarctic_ice_shelves_polys; do
  curl -fsSL -o "raw/$f.geojson" "$N/$f.geojson"
done

echo "== ETOPO 2022, 60 arc-second surface elevation (NOAA NCEI; 466 MB) =="
curl -fSL --retry 5 -C - -o raw/etopo2022_60s_surface.tif \
  https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/60s/60s_surface_elev_gtif/ETOPO_2022_v1_60s_N90W180_surface.tif

echo "== Sea level: Spratt & Lisiecki 2016 (NOAA WDS-Paleo study 19982) =="
curl -fsSL -o raw/spratt2016.txt \
  https://www.ncei.noaa.gov/pub/data/paleo/contributions_by_author/spratt2016/spratt2016.txt

echo "== PaleoMIST 1.0 ice margins (CC-BY-4.0) =="
# The archive is 3.5 GB; only its margin polygons are needed, about 45 MB, read by range request.
Z=https://hs.pangaea.de/Maps/Global_Ice_Sheets/Gowan_ice_reconstruction.zip
for r in North_America Eurasia Antarctica Patagonia; do
  python3 remotezip.py "$Z" "raw/paleomist/margins/$r" "margins/$r/"
done

echo "== AADR v66 via Poseidon (clone; LFS skipped) =="
[ -d clones/aadr-archive ] || GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 \
  https://github.com/poseidon-framework/aadr-archive clones/aadr-archive

echo "== AWMC geodata — roads, canals, aqueducts, walls (ODbL) =="
# NB: ~640 MB, mostly physical-data files the atlas does not use.
[ -d clones/awmc-geodata ] || git clone --depth 1 \
  https://github.com/AWMC/geodata clones/awmc-geodata

echo
echo "Done. Now:  pip install pyreadr rasterio numpy pillow scipy"
echo "            python3 build-tree.py && python3 build-haplink.py && python3 build-layers.py"
echo "            python3 build-ice.py && python3 build-earth.py"

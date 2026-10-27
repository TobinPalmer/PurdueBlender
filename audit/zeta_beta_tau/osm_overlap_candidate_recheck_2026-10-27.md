# Recheck of overlapping OSM candidate — 2026-10-27

## Question

The read-only master audit found `Asset_massing_house_301841334_fa7e5a2` reachable as a separate root whose footprint overlaps 97.4% of the smaller bottom-mesh footprint of Rossen's ZBT asset. This recheck asks whether current OpenStreetMap history identifies that candidate as a distinct neighboring building.

## Source record

The OpenStreetMap API full response for [way 301841334](https://api.openstreetmap.org/api/0.6/way/301841334/full.json), retrieved 2026-10-27, is preserved in `sources/osm_way_301841334_full_2026-10-27.json`; its version history is in `sources/osm_way_301841334_history_2026-10-27.json`. The way has only version 1, created 2014-09-04 20:26:31 UTC. Its only tag is `building=school`; it has no name, address, organization, or other identifier. The geometry encloses four nodes near 900 David Ross Road.

The associated [changeset 25235634](https://api.openstreetmap.org/api/0.6/changeset/25235634.json), also retrieved 2026-10-27 and saved in `sources/osm_changeset_25235634_2026-10-27.json`, was created by OSM user `lrhill` on 2014-09-04. It reports Bing imagery as the imagery used and contains 86 total changes across a broad campus-area bounding box. It gives no building identity or survey provenance for this specific way.

## Finding and limitation

This history does **not** establish a distinct structure or a separate current occupant. It shows that an anonymous building polygon was traced at this location in 2014. The near-total overlap between the candidate asset and the ZBT envelope is consistent with the candidate being an older massing for the same building, but footprint overlap and an anonymous OSM tag are not enough to prove identity. Do not delete or merge the candidate based on this record alone. Tobin should compare the candidate against the source imagery and master scene when resolving the outstanding integration handoff.

The candidate remains outside Rossen's assigned ZBT asset. No changes were made to either Blender file or the campus master.

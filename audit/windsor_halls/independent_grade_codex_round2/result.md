# Independent Grade — Windsor Halls, revision 2

**Result: 7.8/10 — below the 8.0 finish threshold.** This review applies to the exact asset SHA-256 `38f4aad7181339a573c2eeb5b6151d116d68bb9c60bb92c040b09516ae676135` only. The independent Blender 5.2.3 LTS reopen passed; details are in [fresh_open_probe.json](fresh_open_probe.json).

## What is working

- The asset scope is documented as Warren, Wood, Vawter, and the Windsor Dining Court (FIDs 63–66), with adjacent Shealy and separately modeled Duhme excluded.
- The exact structural-shell footprint comparison is excellent: the reported IoU values are 0.9999984–0.9999990, with roughly 0.00003 m boundary error.
- Materials are self-contained and distinguish brick, slate, stone trim, windows, doors, frames, and schematic interiors. The fresh-open found 10 used materials and no missing image or library dependencies.
- The model now has hall-specific entry treatments and explicit schematic room/lounges and dining objects. Its evidence clearly marks unsupported vertical and interior details as estimates or schematics.

## Why it does not pass

The main issue is the roof geometry. The overall and frontage previews show broad, continuous roof caps that hide large portions of the upper facades and courtyards. Some transitions look intersecting or detached, and the roof silhouettes are not supported by the available per-hall elevation evidence. The residential facades also rely on a repeated window grid and mostly generic entry details, so the model reads as a set of textured massing shells rather than three distinct historic halls. The cutaway previews do not make the documented room furniture and circulation easy to read.

The Dining Court's subgrade volume is explicitly uncertain: Purdue Housing says it is under Warren and Vawter, while FID 66's GIS polygon has no shared horizontal area with FIDs 63–65 (it touches their boundaries). The model preserves the GIS ring rather than inventing overlap, which is appropriate, but its physical vertical connection remains unverified.

## Weighted review

| Criterion | Score | Weight |
| --- | ---: | ---: |
| Identity and source attribution | 9.5 | 10% |
| Structural footprints | 9.9 | 20% |
| Placement and component relationships | 8.4 | 10% |
| Roof and overall silhouette | 5.2 | 20% |
| Facade and entrances | 6.9 | 20% |
| Materials and texturing | 8.6 | 10% |
| Interior representation | 5.0 | 5% |
| Reopen, portability, and evidence | 9.8 | 5% |

The weighted total is **7.79/10** (reported to one decimal as **7.8/10**).

## Highest-value revisions

1. Redesign roof planes separately for each hall: reduce broad caps, expose upper rows and courtyard walls, and remove intersections at the inside corners. Keep roof forms labeled estimated unless a source confirms them.
2. Strengthen building-specific facade and entrance cues using direct imagery, rather than repeating one generic window/entry pattern.
3. Make the schematic room and dining interiors visibly readable in cutaway views; keep their non-surveyed status explicit.
4. Keep the FID 66 horizontal shell intact until reliable evidence resolves how its footprint relates to the officially described under-hall dining space.

## Sources checked

- [Purdue Housing — Windsor Halls](https://housing.purdue.edu/my-housing/options/residence-halls/windsor.html): confirms the connected hall names, Dining Court relationship, generic room sizes and amenities.
- [Purdue Emergency Plan — Warren Hall](https://www.purdue.edu/operations/emergency-preparedness/warn/) and [Vawter Hall](https://www.purdue.edu/operations/emergency-preparedness/vawt/): support four-story descriptions and partial-basement context, but do not establish exact elevations or roof geometry.
- [RGCollaborative — Wood Hall renovation](https://www.rgcollaborative.com/projects/Education/purdue-university-wood-hall): confirms Wood's historic-feature renovation; its visual details do not validate all three modeled elevations.
- [Purdue Housing exterior reference image](https://purdue.starrezhousing.com/StarRezPortalXConference/File/GetImage?dateCreatedTicks=638309106832699833&hash=3B0DB762&imageName=52483840151_ea5f2e6ade_k.jpg&tableID=13617&tableName=PortalPageWidget): supports the broad brick/stone/slate palette, but is not a hall-specific elevation.

Visuals reviewed: the overall overview, Warren frontage, Wood frontage, Vawter frontage, residential interior schematic, and Dining Court schematic under `audit/windsor_halls/previews/`.

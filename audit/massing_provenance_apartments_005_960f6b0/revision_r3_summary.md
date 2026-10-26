# Provenance Apartments 005 — r3 revision

## Decision

The asset is identified as BLDG F / 143 using county plan sheet C1.4 and current overhead roof imagery. Purdue GIS FID 506 is a pre-planning feature whose ring closely matches the current roof outline. The ring is not treated as a surveyed wall registration.

A focused search found no defensible Building F-specific street-level photograph, approved elevation, or section in the accessible sources. A nearby listing image labeled 1505 was excluded because it does not identify Building F / 143 and is not the 1509 address context associated with the target. Studio M imagery was treated as project-wide only and was not used to place facade details.

## r3 changes

- Removed unsupported windows, mullions, balconies, entries, canopies, accent bays, and facade material/color stationing.
- Kept a plain neutral shell from the assigned FID 506 ring.
- Retained a five-break roof rhythm as an estimate inferred from the exact-block overhead image. Ridge count, positions, pitch, eave and ridge heights are estimates; no F/143 elevation or section supports exact values.
- Updated source register, build evidence, and reopen validator to record evidence limits and the simplified model.

## Separate-process reopen validation

Blender 5.2.3 LTS reopened the saved `.blend` in a fresh process. Result: **pass, 16/16 checks**. The 32 source ring vertices match within 0.000060 m maximum XY/Z error. The asset contains one mesh, 132 vertices, 44 faces, two neutral material slots, no modifiers, and no external image dependencies.

Evaluated campus-coordinate bounds (m):

- X: -1573.2703 to -1523.5427
- Y: -466.8532 to -447.5692
- Z: 0 to 11.4000 (estimated)

The Y range is governed by the roof geometry; it does not certify wall position. Validation details are in `reopen_validation.json` and source search notes are in `source_search_r3.json`.

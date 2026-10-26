# Independent PGU Asset Grade

**Score: 8.15/10 — PASS (threshold 8.0)**

Fresh-opened the saved library in Blender 5.2.3 and inspected its scene, collection, evaluated geometry, materials and external image dependencies. Separately compared the saved preview with the preserved CE Solutions project photo and checked the evidence against Purdue GIS Feature FID 260.

**SHA-256:** observed `0cee0625c38ea3742e553c07cd76f65e363b7be63bdba90881e8beb95fc59760`. This matches the pre-existing `asset_sha256.json`; the SHA supplied in the grading assignment differs by one hex character.

| Criterion | Grade |
|---|---:|
| Identity and source match | 0.95/1.00 |
| Footprint, dimensions and orientation | 1.85/2.00 |
| Placement anchor and modular coordinates | 0.95/1.00 |
| Floor count and vertical dimensions | 0.70/1.00 |
| Exterior facade fidelity | 1.35/2.00 |
| Parking interior and circulation | 0.55/1.00 |
| Materials, dependencies and asset portability | 0.90/1.00 |
| Evidence quality and uncertainty reporting | 0.90/1.00 |

### Findings

- Fresh-opened collection contains 857 objects; evaluated bounds are 83.00 x 96.45 x 15.06 m.
- GIS footprint bounds are 82.36 x 95.93 m and GIS records six levels. The asset contains six deck plates and the documented anchor [-303.865845, -72.763426] m.
- Facade material families and open-air composition resemble the reference photograph. The spandrel bands appear too thin/uniform and four large corner cores are not supported by the reference.
- Internal layout and ramps are generalized. They should not be treated as a verified driveable route or exact parking plan. Height is an estimate because GIS vertical fields are ambiguous.
- Procedural materials are self-contained; no unpacked external image dependency was found.

### Evidence and limitations

See `result.json` for per-criterion rationale and `fresh_blender_probe.json` for object-level bounds/material assignments. This review evaluates the standalone library; it does not verify placement in the full campus master.

# Original OSM source consistency

Supplementary input-source consistency, not an independent accuracy audit. Official Purdue master audit statuses are unchanged.

Checked every massing asset: 1908 records. Threshold: 0.01 m maximum difference across four XY bounding edges.

{'input_source_bounds_consistent_within_1cm': 1908}

Snapshots: {'purdue_campus_buildings.json': '2026-10-22T03:45:50Z', 'ross_ade_stadium.json': '2026-10-22T03:48:50Z'}

Exact House_ID or exact named way matching is required; Blender numeric suffixes are stripped to identify repeated imports. Source coordinate filtering reproduces build_campus_base.py. Multiple ways sharing a name retain an ambiguity flag. Comparison uses the original imported source, so agreement verifies import placement/bounds consistency only. It cannot establish current real-world correctness, exact footprint shape, elevations, or inferred heights. Per-way edit timestamps were not requested in the original OSM snapshots; snapshot base times are preserved without inventing edit dates.

Every massing asset has its own JSON/CSV row, including unmatched assets and discrepancies. Official campus audit statuses were not modified.
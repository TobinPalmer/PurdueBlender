# Master building audit

Exhaustive asset ledger against official Purdue 2D polygon snapshot. Bounding comparisons are review flags, not measured shell errors. No building certified. Explicit placement corrections are recorded separately; this audit does not mutate geometry.

Assets: 1933; buildings: 1932. One record per asset in JSON and CSV.

{'needs_shell_and_height_verification': 113, 'environment_not_building': 1, 'ambiguous_source_match': 397, 'no_official_match': 1421, 'gross_placement_corrected_precision_and_dimensions_unverified': 1}

## Detailed buildings

| Asset | Official code | Match | Bounds center difference (m) | Screening | Shell candidates |
|---|---|---|---:|---|---:|
| armory | AR | official_code_by_detailed_group_name | 0.31 | bounds_close_not_verified | 8 |
| beering_hall | BRNG | official_code_by_detailed_group_name | 0.291 | bounds_close_not_verified | 3 |
| bell_tower | BELL | official_code_by_detailed_group_name | 0.488 | bounds_close_not_verified | 5 |
| class_of_1950 | CL50 | official_code_by_detailed_group_name | 1.19 | bounds_close_not_verified | 6 |
| electrical_engineering | BHEE | spatial_candidate_only_identity_unverified | 3.868 | bounds_close_not_verified | 1 |
| elliott_hall_of_music | ELLT | official_code_by_detailed_group_name | 3.858 | bounds_close_not_verified | 11 |
| felix_haas_hall | HAAS | official_code_by_detailed_group_name | 0.391 | bounds_close_not_verified | 4 |
| frieda_parker_hall | PKRF | official_code_by_detailed_group_name | 0.958 | bounds_close_not_verified | 5 |
| hovde_hall | HOVD | official_code_by_detailed_group_name | 0.382 | bounds_close_not_verified | 6 |
| mackey_arena | MACK | official_code_by_detailed_group_name | 44.275 | large_bounds_discrepancy_review_shell | 3 |
| math_sciences | MATH | official_code_by_detailed_group_name | 1.019 | bounds_close_not_verified | 46 |
| mechanical_engineering | ME | official_code_by_detailed_group_name | 12.728 | large_bounds_discrepancy_review_shell | 2 |
| neil_armstrong_hall | ARMS | official_code_by_detailed_group_name | 6.577 | large_bounds_discrepancy_review_shell | 7 |
| owen_hall | OWEN | official_code_by_detailed_group_name | 0.328 | bounds_close_not_verified | 19 |
| potter_engineering | POTR | official_code_by_detailed_group_name | 35.871 | large_bounds_discrepancy_review_shell | 1 |
| purdue_memorial_union | PMU | official_code_by_detailed_group_name | 0.223 | bounds_close_not_verified | 14 |
| ross_ade | STDM | official_code_by_detailed_group_name | 7.802 | large_bounds_discrepancy_review_shell | 59 |
| south_hall | SH | official_code_by_detailed_group_name | 9.423 | large_bounds_discrepancy_review_shell | 2 |
| stewart_center | STEW | official_code_by_detailed_group_name | 1.975 | bounds_close_not_verified | 11 |
| tarkington_hall | TARK | official_code_by_detailed_group_name | 0.114 | bounds_close_not_verified | 19 |
| university_hall | UNIV | official_code_by_detailed_group_name | 0.391 | bounds_close_not_verified | 7 |
| walc | WALC | official_code_by_detailed_group_name | 2.101 | bounds_close_not_verified | 8 |
| wiley_hall | WILY | official_code_by_detailed_group_name | 0.0 | bounds_close_not_verified | 4 |
| winifred_parker_hall | PKRW | official_code_by_detailed_group_name | 1.31 | bounds_close_not_verified | 7 |

All position, orientation and height criteria remain unverified until a shell-specific measurement and evidence review establishes them. A source match and similar bounds do not establish accuracy. No dimensions were changed from inferred bounding boxes. See GEOSPATIAL_REFERENCE.md for provenance and acceptance method.

Duplicate extent screening: 187 groups containing 374 assets have identical 3D bounds rounded to 1 mm. These are collision candidates, not proven duplicate meshes. See JSON groups and CSV per-asset records.
# Purdue Campus Map

This project covers Purdue West Lafayette campus buildings and Purdue-operated residences, plus verified fraternity, sorority, and cooperative houses even when they sit off campus. Unrelated off-campus housing is excluded; Granite Student Living is out of scope. Purdue's 508-record campus-map snapshot is indexed below, but its features include split polygons, support structures, and duplicates, so it is not a count of unique buildings. The source inventory is complete; asset-level reconciliation is still in progress. The duplicate Beering Hall BRNG massing record (Purdue GIS feature 251) is excluded from the master; its removal is recorded in `TODO.md`. A detailed model counts as finished only when the latest independent grade is at least 8/10 and it is integrated into the master blend.

Current per-building Blender sources and builders live in [`modular/buildings/`](modular/buildings/). Shared building workflow tools, older building-specific scripts, and miscellaneous utilities are organized under [`scripts/`](scripts/README.md).

## Detailed models: status and latest grader score (159 buildings)

| Building | Detailed model | Status | Latest independent grade | Assigned to |
| --- | --- | --- | ---: | --- |
| FUSE | [massing_fuse_39cf4b5.blend](modular/buildings/massing_fuse_39cf4b5.blend) | Finished | [8.25/10](audit/massing_fuse_39cf4b5/independent_grade_r3/result.json) | — |
| Grant Street Parking Garage (PGG) | [massing_grant_street_parking_garage_pgg_f46c894.blend](modular/buildings/massing_grant_street_parking_garage_pgg_f46c894.blend) | Finished | [8.75/10](audit/massing_grant_street_parking_garage_pgg_f46c894/review/pgg_independent_grade.json) | — |
| Hall of Data Science and AI | [massing_hall_of_data_science_and_ai_dsai_c8a41cc.blend](modular/buildings/massing_hall_of_data_science_and_ai_dsai_c8a41cc.blend) | Finished | [8.8/10](audit/dsai/independent_grade_r2/result.json) | — |
| Bob & Trudy Hull “All-American” Marching Band Complex | [massing_hull_all_american_marching_band_complex_665bcb7.blend](modular/buildings/massing_hull_all_american_marching_band_complex_665bcb7.blend) | Finished; height and facade details remain estimated | [8.4/10](audit/hull_all_american_marching_band_complex/independent_grade_current/result.json) | — |
| Grissom Hall | [massing_grissom_hall_01fd0e0.blend](modular/buildings/massing_grissom_hall_01fd0e0.blend) | Finished | [8.0/10](audit/massing_grissom_hall_01fd0e0/grader/r2/result.json) | — |
| Hampton Hall of Civil Engineering (HAMP) | [massing_hampton_hall_of_civil_engineering_hamp_9715f0e.blend](modular/buildings/massing_hampton_hall_of_civil_engineering_hamp_9715f0e.blend) | Finished | [8.2/10](audit/massing_hampton_hall_of_civil_engineering_hamp_9715f0e/independent_grade/result.json) | — |
| Hanley Hall | [massing_hanley_hall_c8a4551.blend](modular/buildings/massing_hanley_hall_c8a4551.blend) | Finished | [8.1/10](audit/massing_hanley_hall_c8a4551/independent_grader/r3/result.json) | — |
| Harrison Street Parking Garage | [massing_harrison_street_parking_garage_823c7d2.blend](modular/buildings/massing_harrison_street_parking_garage_823c7d2.blend) | Finished | [8.2/10](audit/massing_harrison_street_parking_garage_823c7d2_independent_grade_r3/grade_result.json) | — |
| Hawkins Hall | [massing_hawkins_hall_282335f.blend](modular/buildings/massing_hawkins_hall_282335f.blend) | Finished | [8.2/10](audit/massing_hawkins_hall_282335f/independent_grade/result.json) | — |
| Henni's Hair Shop | [massing_henni_s_hair_shop_57f732b.blend](modular/buildings/massing_henni_s_hair_shop_57f732b.blend) | Finished | [8.2/10](audit/massing_henni_s_hair_shop_57f732b/independent_grade/r1/result.json) | — |
| Herrick Laboratories (HERL) | [massing_herrick_laboratories_2138103.blend](modular/buildings/massing_herrick_laboratories_2138103.blend) | Finished | [8.4/10](audit/massing_herrick_laboratories_2138103/independent_grade/r2/result.json) | — |
| Hi Vine | [massing_hi_vine_dbdf0c5.blend](modular/buildings/massing_hi_vine_dbdf0c5.blend) | Finished | [8.3/10](audit/massing_hi_vine_dbdf0c5_independent_grade_r1/grade_result.json) | — |
| Hillel | [massing_hillel_36d2ba1.blend](modular/buildings/massing_hillel_36d2ba1.blend) | Finished | [8.3/10](audit/massing_hillel_36d2ba1/independent_grade/r2/result.json) | — |
| Hillenbrand Hall | [massing_hillenbrand_hall_a71e418.blend](modular/buildings/massing_hillenbrand_hall_a71e418.blend) | Finished | [8.0/10](audit/massing_hillenbrand_hall_a71e418/independent_grade/r3/result.json) | — |
| Hockmeyer Hall of Structural Biology (HOCK) | [massing_hockmeyer_hall_of_structural_biology_hock_4d524ab.blend](modular/buildings/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab.blend) | Finished | [8.0/10](audit/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab/independent_grade/r3/result.json) | — |
| Jimmy John's | [massing_jimmy_john_s_12edba1.blend](modular/buildings/massing_jimmy_john_s_12edba1.blend) | Finished | [8.0/10](audit/massing_jimmy_john_s_12edba1/independent_grade/r3/result.json) | — |
| Johnson Hall of Nursing (JNSN) | [massing_johnson_hall_of_nursing_jnsn_823fca7.blend](modular/buildings/massing_johnson_hall_of_nursing_jnsn_823fca7.blend) | Finished; other elevations and entrance remain uncertain | [9.3/10](audit/massing_johnson_hall_of_nursing_jnsn_823fca7/independent_grade/r2/result.json) | — |
| Kappa Sigma | [massing_kappa_sigma_c1b36ec.blend](modular/buildings/massing_kappa_sigma_c1b36ec.blend) | Finished | [8.5/10](audit/massing_kappa_sigma_c1b36ec/independent_grade/result.json) | — |
| Kappa Delta Rho | [massing_house_1089876362_14ecd2c.blend](modular/buildings/massing_house_1089876362_14ecd2c.blend) | Finished; master fresh-open PASS; wall/ridge heights and facade colors remain estimated; interior is schematic | [8.4/10](audit/kappa_delta_rho/independent_grade_r3/result.json) | — |
| 3rd and West | [massing_3rd_and_west_ffa3d05.blend](modular/buildings/massing_3rd_and_west_ffa3d05.blend) | Finished | [8.1/10](audit/massing_3rd_and_west_ffa3d05_independent_grade/result.json) | — |
| Agricultural Administration Building | [agricultural_administration_building.blend](modular/buildings/agricultural_administration_building.blend) | Finished | 8.5/10 | — |
| Agricultural and Biological Engineering | [agricultural_and_biological_engineering_abe.blend](modular/buildings/agricultural_and_biological_engineering_abe.blend) | Finished | 8.0/10 | — |
| Acacia | [massing_house_301841251_8a9a05b.blend](modular/buildings/massing_house_301841251_8a9a05b.blend) | Finished | [8.35/10](audit/acacia/independent_grade_r2/result.json) | — |
| Alpha Chi Rho | [massing_alpha_chi_rho_0cb591a.blend](modular/buildings/massing_alpha_chi_rho_0cb591a.blend) | Finished | [8.15/10](audit/alpha_chi_rho_independent_grade_r2/result.json) | — |
| Alpha Epsilon Pi | [alpha_epsilon_pi.blend](modular/buildings/alpha_epsilon_pi.blend) | Finished; current address/roof match modeled, GIS name conflict remains | [8.25/10](audit/alpha_epsilon_pi/independent_grade_revision_2/result.json) | — |
| Alpha Gamma Rho | [massing_house_301841253_f0b3be3.blend](modular/buildings/massing_house_301841253_f0b3be3.blend) | Finished | [8.4/10](audit/alpha_gamma_rho/independent_grade_master_integration/master_integration_grade.json) | — |
| Beta Sigma Psi | [massing_house_301841254_29ab02d.blend](modular/buildings/massing_house_301841254_29ab02d.blend) | Finished | [9.0/10](audit/beta_sigma_psi/independent_grade_master_integration/result.json) | — |
| Alpha Sigma Phi | [massing_house_301841603_654031c.blend](modular/buildings/massing_house_301841603_654031c.blend) | Finished | [8.2/10](audit/alpha_sigma_phi/independent_grade_current/result.json) | — |
| Alpha Tau Omega | [massing_house_301840870_c45a5f4.blend](modular/buildings/massing_house_301840870_c45a5f4.blend) | Finished; historic tower/roof-wing silhouette remains estimated | [8.5/10](audit/alpha_tau_omega/independent_grade/result.json) | — |
| Alpha Kappa Lambda | [massing_alpha_kappa_lambda_88dda6c.blend](modular/buildings/massing_alpha_kappa_lambda_88dda6c.blend) | Finished | [8.0/10](audit/alpha_kappa_lambda_independent_grade_r3/result.json) | — |
| American Railway Building | [american_railway_building.blend](modular/buildings/american_railway_building.blend) | Finished | 8.5/10 | — |
| Animal Disease Diagnostic Laboratory | [animal_disease_diagnostic_laboratory.blend](modular/buildings/animal_disease_diagnostic_laboratory.blend) | Finished | 8.3/10 | — |
| Animal Holding Facility | [massing_animal_holding_facility_4733f46.blend](modular/buildings/massing_animal_holding_facility_4733f46.blend) | Finished | [8.25/10](audit/animal_holding_facility_independent_grade_r7/result.json) | — |
| Armory | [armory.blend](modular/buildings/armory.blend) | Finished | 8.4/10 | — |
| Asian American and Asian Resource and Cultural Center | [asian_american_resource_and_cultural_center.blend](modular/buildings/asian_american_resource_and_cultural_center.blend) | Finished | 8.5/10 | — |
| Baptist Student Foundation | [massing_baptist_student_foundation_c3d8114.blend](modular/buildings/massing_baptist_student_foundation_c3d8114.blend) | Finished | [8.0/10](audit/baptist_student_foundation_independent_grade_r2/result.json) | — |
| Bechtel Innovation Design Center | [bechtel_innovation_design_center_bidc.blend](modular/buildings/bechtel_innovation_design_center_bidc.blend) | Finished | 8.75/10 | — |
| Beering Hall | [beering_hall.blend](modular/buildings/beering_hall.blend) | Finished | 8.0/10 | — |
| Bell Tower | [bell_tower.blend](modular/buildings/bell_tower.blend) | Finished | 9.3/10 | — |
| Benjamin Harrison Hall | [benjamin_harrison_hall.blend](modular/buildings/benjamin_harrison_hall.blend) | Finished | 8.5/10 | — |
| Bindley Bioscience Center | [bindley_bioscience_center.blend](modular/buildings/bindley_bioscience_center.blend) | Finished | 8.8/10 | — |
| Biochemistry Building | [biochemistry_building.blend](modular/buildings/biochemistry_building.blend) | Finished | 8.5/10 | — |
| Birck Nanotechnology Center | [birck_nanotechnology_center.blend](modular/buildings/birck_nanotechnology_center.blend) | Finished | 8.0/10 | — |
| Black Cultural Center | [black_cultural_center.blend](modular/buildings/black_cultural_center.blend) | Finished | 9.0/10 | — |
| Brown Laboratory of Chemistry | [brown_laboratory_of_chemistry.blend](modular/buildings/brown_laboratory_of_chemistry.blend) | Finished | 8.8/10 | — |
| Burton D. Morgan Center for Entrepreneurship | [burton_morgan_center.blend](modular/buildings/burton_morgan_center.blend) | Finished | [8.4/10](audit/burton_morgan_center_independent_grade/result.json) | — |
| Campus Edge | [massing_campus_edge_343e3d8.blend](modular/buildings/massing_campus_edge_343e3d8.blend) | Finished | [8.5/10](audit/massing_campus_edge_343e3d8_independent_grade_r2/result.json) | — |
| Cary Quadrangle East (CQE) | [massing_cary_quadrangle_east_cqe_230c813.blend](modular/buildings/massing_cary_quadrangle_east_cqe_230c813.blend) | Finished | [8.0/10](audit/massing_cary_quadrangle_east_cqe_independent_grade_r3/result.json) | — |
| Cary Quadrangle South (CQS) | [massing_cary_quadrangle_south_cqs_7ee2283.blend](modular/buildings/massing_cary_quadrangle_south_cqs_7ee2283.blend) | Finished | [8.5/10](audit/massing_cary_quadrangle_south_cqs_independent_grade/result.json) | — |
| Cary Quadrangle West (CQW) | [massing_cary_quadrangle_west_cqw_3d47a7d.blend](modular/buildings/massing_cary_quadrangle_west_cqw_3d47a7d.blend) | Finished | [8.7/10](audit/massing_cary_quadrangle_west_cqw_independent_grade_r3/independent_grade_result.json) | — |
| Chi Omega | [massing_chi_omega_a9eb08d.blend](modular/buildings/massing_chi_omega_a9eb08d.blend) | Finished | [9.0/10](audit/chi_omega_independent_grade_r2/result.json) | — |
| Creighton Hall of Animal Sciences | [massing_creighton_hall_of_animal_sciences_crtn_a88d450.blend](modular/buildings/massing_creighton_hall_of_animal_sciences_crtn_a88d450.blend) | Finished | [8.5/10](audit/massing_creighton_hall_of_animal_sciences_crtn_a88d450/independent_grade/result.json) | — |
| Crosswalk Commons | [massing_crosswalk_commons_7c01ecd.blend](modular/buildings/massing_crosswalk_commons_7c01ecd.blend) | Finished | [8.1/10](audit/crosswalk_commons/independent_grade_result.json) | — |
| Class Of 1950 | [class_of_1950.blend](modular/buildings/class_of_1950.blend) | Finished | 8.5/10 | — |
| Delta Sigma Phi | [massing_house_860826641_2c90f97.blend](modular/buildings/massing_house_860826641_2c90f97.blend) | Finished; FID 798 identity and wall footprint verified; no interior and roof/story details remain estimated | [8.3/10](audit/delta_sigma_phi/independent_grade_codex/result.json) | — |
| Delta Tau Delta | [massing_delta_tau_delta_e06b0b5.blend](modular/buildings/massing_delta_tau_delta_e06b0b5.blend) | Finished | [8.25/10](audit/delta_tau_delta_e06b0b5/independent_grade_r2/result.json) | — |
| Delta Upsilon | [massing_house_301841256_1cc7641.blend](modular/buildings/massing_house_301841256_1cc7641.blend) | Finished; exact FID 751 wall footprint; master fresh-open PASS; height/roof estimated; no interior plan found | [8.4/10](audit/delta_upsilon/independent_grade_codex/result.json) | — |
| Convergence Center for Innovation and Collaboration | [convergence_center.blend](modular/buildings/convergence_center.blend) | Needs independent grade | Not graded | Rohan |
| Dauch Alumni Center | [dauch_alumni_center.blend](modular/buildings/dauch_alumni_center.blend) | In progress | 7.2/10 | Rohan |
| David and Bonnie Brunner Farm Animal Hospital | [david_and_bonnie_brunner_farm_animal_hospital.blend](modular/buildings/david_and_bonnie_brunner_farm_animal_hospital.blend) | In progress | 6.7/10 | Rohan |
| Drew and Brittany Brees Student Athletic Academic Center | [brees_student_athletic_academic_center.blend](modular/buildings/brees_student_athletic_academic_center.blend) | In progress | 7.3/10 | Rohan |
| Duhme (Ophelia) Residence Hall | [massing_duhme_ophelia_residence_hall_1bb4e9c.blend](modular/buildings/massing_duhme_ophelia_residence_hall_1bb4e9c.blend) | Finished | [8.5/10](audit/duhme_ophelia_residence_hall_independent_grade/result.json) | — |
| Dudley Hall | [dudley_hall.blend](modular/buildings/dudley_hall.blend) | Finished | [8.0/10](audit/dudley_hall/independent_grade/result.json) | — |
| Electrical Engineering | [electrical_engineering.blend](modular/buildings/electrical_engineering.blend) | In progress | 5.2/10 | Rohan |
| Earhart Hall | [massing_earhart_hall_0f14209.blend](modular/buildings/massing_earhart_hall_0f14209.blend) | Finished | [8.0/10](audit/earhart_hall_independent_grade/result.json) | — |
| Elliott Hall Of Music | [elliott_hall_of_music.blend](modular/buildings/elliott_hall_of_music.blend) | In progress | 7.1/10 | Rohan |
| Fairway Cooperative | [massing_fairway_cooperative_2101b77.blend](modular/buildings/massing_fairway_cooperative_2101b77.blend) | Finished | [8.1/10](audit/fairway_cooperative_independent_grade/result.json) | — |
| Family Express | [massing_family_express_a07e1fb.blend](modular/buildings/massing_family_express_a07e1fb.blend) | Finished | [8.4/10](audit/family_express_independent_grade/result.json) | — |
| FarmHouse Fraternity, Purdue Chapter | [massing_farmhouse_fraternity_purdue_chapter_0b8908b.blend](modular/buildings/massing_farmhouse_fraternity_purdue_chapter_0b8908b.blend) | Finished | [8.1/10](audit/farmhouse_fraternity_purdue_chapter_independent_grade/revision2_result.json) | — |
| Faith West Community Center | [massing_faith_west_community_center_84aa829.blend](modular/buildings/massing_faith_west_community_center_84aa829.blend) | Finished | [8.0/10](audit/faith_west_community_center_independent_grade/result.json) | — |
| Felix Haas Hall | [felix_haas_hall.blend](modular/buildings/felix_haas_hall.blend) | In progress | 7.4/10 | Rohan |
| First Street Towers, Central (FSTC) | [massing_first_street_towers_central_fstc_929924d.blend](modular/buildings/massing_first_street_towers_central_fstc_929924d.blend) | Finished | [8.4/10](audit/first_street_towers_central_fstc_independent_grade/result.json) | — |
| First Street Towers, East (FSTE) | [massing_first_street_towers_east_fste_c9b22d3.blend](modular/buildings/massing_first_street_towers_east_fste_c9b22d3.blend) | Finished | [8.1/10](audit/first_street_towers_east_independent_grade_r2/result.json) | — |
| First Street Towers, West (FSTW) | [massing_first_street_towers_west_fstw_b6c3bbe.blend](modular/buildings/massing_first_street_towers_west_fstw_b6c3bbe.blend) | Finished | [8.7/10](audit/first_street_towers_west_fstw_independent_grade/grade_result.json) | — |
| Flex Lab | [flex_lab.blend](modular/buildings/flex_lab.blend) | In progress | 7.5/10 | Rohan |
| Ford Dining Court | [ford_dining_court.blend](modular/buildings/ford_dining_court.blend) | In progress | 6.8/10 | Rohan |
| Forney Hall of Chemical Engineering | [massing_forney_hall_of_chemical_engineering_frny_d94ba3a.blend](modular/buildings/massing_forney_hall_of_chemical_engineering_frny_d94ba3a.blend) | Finished | [8.2/10](audit/forney_hall_of_chemical_engineering_frny_d94ba3a_independent_grade/result.json) | — |
| France A. Córdova Recreational Sports Center | [massing_france_a_c_rdova_recreational_sports_center_ae69df0.blend](modular/buildings/massing_france_a_c_rdova_recreational_sports_center_ae69df0.blend) | Finished | 8.1/10 | — |
| Frieda Parker Hall | [frieda_parker_hall.blend](modular/buildings/frieda_parker_hall.blend) | Needs independent grade | Not graded | Rohan |
| Hall for Discovery and Learning Research | [hall_for_discovery_and_learning_research.blend](modular/buildings/hall_for_discovery_and_learning_research.blend) | In progress | 7.3/10 | Rohan |
| Hansen Life Sciences | [hansen_life_sciences.blend](modular/buildings/hansen_life_sciences.blend) | Needs independent grade | Not graded | Rohan |
| Heine Pharmacy | [heine_pharmacy.blend](modular/buildings/heine_pharmacy.blend) | In progress | 7.5/10 | Rohan |
| Hicks Library | [hicks_library.blend](modular/buildings/hicks_library.blend) | In progress | 6.6/10 | Rohan |
| Horticulture Building | [horticulture_building.blend](modular/buildings/horticulture_building.blend) | In progress | 7.0/10 | Rohan |
| Honors College and Residences North | [massing_honors_college_and_residences_north_3de3b7c.blend](modular/buildings/massing_honors_college_and_residences_north_3de3b7c.blend) | Finished | [8.0/10](audit/honors_college_and_residences_north/independent_grade/grade_result.json) | — |
| Honors College and Residences South | [massing_honors_college_and_residences_south_c663781.blend](modular/buildings/massing_honors_college_and_residences_south_c663781.blend) | Finished | [8.5/10](audit/honors_college_residences_south_c663781/independent_grade/grade_result.json) | — |
| Horizon Bank | [massing_horizon_bank_debc8f2.blend](modular/buildings/massing_horizon_bank_debc8f2.blend) | Finished | [8.9/10](audit/horizon_bank/independent_grade/grade_result.json) | — |
| Hovde Hall | [hovde_hall.blend](modular/buildings/hovde_hall.blend) | Finished | 8.7/10 | — |
| Knoy Hall | [knoy_hall.blend](modular/buildings/knoy_hall.blend) | Finished | [8.1/10](audit/batch4_knoy/independent_grade_r23.md) | — |
| Krach Leadership Center | [krach_leadership_center.blend](modular/buildings/krach_leadership_center.blend) | Finished | 8.1/10 | — |
| Krannert Building | [krannert_building.blend](modular/buildings/krannert_building.blend) | Finished | 8.0/10 | — |
| Lawson Hall | [lawson_hall.blend](modular/buildings/lawson_hall.blend) | Finished | [8.1/10](audit/batch2_lawson/INDEPENDENT_REVIEW_round8.md) | — |
| Life Science Plant and Soils Laboratory | [life_science_plant_and_soils_laboratory.blend](modular/buildings/life_science_plant_and_soils_laboratory.blend) | Finished | 8.0/10 | — |
| Lyles-Porter Hall | [lyles_porter_hall.blend](modular/buildings/lyles_porter_hall.blend) | Finished | 8.2/10 | — |
| Mackey Arena | [mackey_arena.blend](modular/buildings/mackey_arena.blend) | Finished | 8.0/10 | — |
| Materials Science and Electrical Engineering | [materials_science_and_electrical_engineering_msee.blend](modular/buildings/materials_science_and_electrical_engineering_msee.blend) | Finished | 8.2/10 | — |
| Math Sciences | [math_sciences.blend](modular/buildings/math_sciences.blend) | Finished | 8.1/10 | — |
| Mccutcheon Hall | [mccutcheon_hall.blend](modular/buildings/mccutcheon_hall.blend) | Finished | 8.1/10 | — |
| Mechanical Engineering | [mechanical_engineering.blend](modular/buildings/mechanical_engineering.blend) | Finished | 8.0/10 | — |
| Morgan J. Burke Boilermaker Aquatic Center | [morgan_j_burke_boilermaker_aquatic_center.blend](modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend) | Finished | [8.5/10](audit/batchC_boilermaker_aquatic_r1/independent_grade_r9.md) | — |
| National Soil Erosion Laboratory | [national_soil_erosion_laboratory.blend](modular/buildings/national_soil_erosion_laboratory.blend) | Finished | 8.0/10 | — |
| Native American Educational and Cultural Center | [native_american_educational_and_cultural_center_nacc.blend](modular/buildings/native_american_educational_and_cultural_center_nacc.blend) | Finished | [8.0/10](audit/build_nacc/nacc_independent_report_r3.md) | — |
| Neil Armstrong Hall | [neil_armstrong_hall.blend](modular/buildings/neil_armstrong_hall.blend) | Finished | [8.0/10](audit/neil_armstrong_hall_refine/INDEPENDENT_REVIEW_R12_9.md) | — |
| Niswonger Aviation Tech | [niswonger_aviation_tech.blend](modular/buildings/niswonger_aviation_tech.blend) | Finished | [8.0/10](audit/niswonger_aviation_tech_refine/independent_grade_r4.md) | — |
| Northwest Chiller Plant | [northwest_chiller_plant.blend](modular/buildings/northwest_chiller_plant.blend) | Finished | [8.3/10](audit/northwest_chiller_plant_refine/independent_grade_r1.md) | — |
| Owen Hall | [owen_hall.blend](modular/buildings/owen_hall.blend) | Finished | [8.0/10](audit/owen_hall_independent_grade/independent_report_r3.md) | — |
| Peirce Hall | [peirce_hall.blend](modular/buildings/peirce_hall.blend) | Finished | 8.8/10 | — |
| Physics Building | [physics_building_phys_3bf42f3.blend](modular/buildings/physics_building_phys_3bf42f3.blend) | Finished | [8.4/10](audit/physics_building/independent_report_r2.md) | — |
| Potter Engineering | [potter_engineering.blend](modular/buildings/potter_engineering.blend) | Finished | [8.0/10](audit/potter_engineering_refine/INDEPENDENT_GRADE_R3.md) | — |
| Psychological Sciences Building | [psychological_sciences.blend](modular/buildings/psychological_sciences.blend) | Finished | 9.0/10 | — |
| Purdue Center for Regional Development (Schowe House) | [massing_purdue_center_for_regional_development_scho_a2375c9.blend](modular/buildings/massing_purdue_center_for_regional_development_scho_a2375c9.blend) | Finished | [8.5/10](audit/schowe_house/independent_grade_localized/result.json) | — |
| Purdue Drug Discovery Facility | [massing_purdue_drug_discovery_facility_fc72a4a.blend](modular/buildings/massing_purdue_drug_discovery_facility_fc72a4a.blend) | Finished | [9.1/10](audit/purdue_drug_discovery_facility/independent_grade_localized/result.json) | — |
| Purdue Fire Department | [massing_purdue_fire_department_520430b.blend](modular/buildings/massing_purdue_fire_department_520430b.blend) | Finished | [8.4/10](audit/purdue_fire_department/independent_grade_localized/result.json) | — |
| Purdue Football Performance Complex (Kozuch Football Performance Center) | [massing_purdue_football_performance_complex_f106c29.blend](modular/buildings/massing_purdue_football_performance_complex_f106c29.blend) | Finished | [8.5/10](audit/purdue_football_performance_complex/independent_grade_localized/result.json) | — |
| Purdue Graduate Student Center | [massing_purdue_graduate_student_center_af9c5c7.blend](modular/buildings/massing_purdue_graduate_student_center_af9c5c7.blend) | Finished | [8.6/10](audit/purdue_graduate_student_center/independent_grade/result.json) | — |
| Purdue Lutheran Ministry | [massing_purdue_lutheran_ministry_5425b3c.blend](modular/buildings/massing_purdue_lutheran_ministry_5425b3c.blend) | Finished | [8.4/10](audit/purdue_lutheran_ministry/independent_grade/result.json) | — |
| Purdue Memorial Union | [purdue_memorial_union.blend](modular/buildings/purdue_memorial_union.blend) | Finished | [8.0/10](audit/purdue_memorial_union_independent_grade/independent_grade_r4.md) | — |
| R. B. Wetherill Laboratory of Chemistry | [wetherill_laboratory_of_chemistry.blend](modular/buildings/wetherill_laboratory_of_chemistry.blend) | Finished | 8.3/10 | — |
| Rawls Hall | [rawls_hall.blend](modular/buildings/rawls_hall.blend) | Finished | [8.14/10](audit/batch4_rawls/independent_review_round11.md) | — |
| Ray W. Herrick Laboratories | [ray_w_herrick_laboratories.blend](modular/buildings/ray_w_herrick_laboratories.blend) | Finished | [8.1/10](audit/ray_w_herrick_refine/independent_grade_r2.md) | — |
| Ross Ade | [ross_ade.blend](modular/buildings/ross_ade.blend) | Finished | [8.0/10](audit/ross_ade/independent_grade.md) | — |
| SAMARA (John and Catherine Christian House) | [massing_samara_f6b8e61.blend](modular/buildings/massing_samara_f6b8e61.blend) | Finished | [8.6/10](audit/samara/independent_grade.json) | — |
| South Hall | [south_hall.blend](modular/buildings/south_hall.blend) | Finished | [8.2/10](audit/south_hall_refine/independent_grade_r2.md) | — |
| Stanley Coulter Hall | [stanley_coulter_hall.blend](modular/buildings/stanley_coulter_hall.blend) | Finished | [8.1/10](audit/batch3_stanley/independent_grade_r6.md) | — |
| St. Thomas Aquinas Center | [massing_st_thomas_aquinas_5535390.blend](modular/buildings/massing_st_thomas_aquinas_5535390.blend) | Finished | [8.2/10](audit/st_thomas_aquinas_5535390/independent_grade_r4.md) | — |
| Stewart Center | [stewart_center.blend](modular/buildings/stewart_center.blend) | Finished | [8.0/10](audit/stewart_center_independent_grade/independent_grade_r4.md) | — |
| Tarkington Hall | [tarkington_hall.blend](modular/buildings/tarkington_hall.blend) | Finished | [8.0/10](audit/tarkington_hall/independent_grade_r4.md) | — |
| University Book Store | [massing_university_book_store_717bf2c.blend](modular/buildings/massing_university_book_store_717bf2c.blend) | Finished | [8.25/10](audit/purdue_university_book_store/independent_grade/grade.json) | — |
| University Church | [massing_university_church_84b2a1b.blend](modular/buildings/massing_university_church_84b2a1b.blend) | Finished | [8.2/10](audit/purdue_university_church/independent_grade_revised/result.json) | — |
| University Lutheran Church | [massing_university_lutheran_church_20903f1.blend](modular/buildings/massing_university_lutheran_church_20903f1.blend) | Finished | [8.5/10](audit/university_lutheran_church/independent_grade_final/result.json) | — |
| University Street Parking Garage | [massing_university_street_parking_garage_pgu_be81bec.blend](modular/buildings/massing_university_street_parking_garage_pgu_be81bec.blend) | Finished | [8.15/10](audit/university_street_garage_pgu/independent_grade_final/result.json) | — |
| Utility Plant Office Facility | [massing_utility_plant_office_facility_e219ef5.blend](modular/buildings/massing_utility_plant_office_facility_e219ef5.blend) | Finished | [8.45/10](audit/utility_plant_office_facility/independent_grade_r2/evaluation.json) | — |
| Veterinary Animal Isolation Building 2 (VA2) | [massing_veterinary_animal_isolation_building_2_ebb4142.blend](modular/buildings/massing_veterinary_animal_isolation_building_2_ebb4142.blend) | Finished | [8.0/10](audit/veterinary_animal_isolation_building_2/independent_grade/result.json) | — |
| Veterinary Medicine Isolation Facility | [massing_veterinary_medicine_isolation_facility_66d1305.blend](modular/buildings/massing_veterinary_medicine_isolation_facility_66d1305.blend) | Finished | [8.5/10](audit/veterinary_medicine_isolation_facility/independent_grade_r2/result.json) | — |
| Veterinary Pathology Building | [massing_veterinary_pathology_building_48b5a5b.blend](modular/buildings/massing_veterinary_pathology_building_48b5a5b.blend) | Finished | [8.2/10](audit/veterinary_pathology_building/independent_grade_r2/grade_result.json) | — |
| University Hall | [university_hall.blend](modular/buildings/university_hall.blend) | Finished | [8.0/10](audit/university_hall_refine/independent_grade_r7.md) | — |
| Walc | [walc.blend](modular/buildings/walc.blend) | Finished | [8.25/10](audit/walc_refine/independent_grade_r5.md) | — |
| Wang Hall | [massing_wang_hall_wang_0dac5ab.blend](modular/buildings/massing_wang_hall_wang_0dac5ab.blend) | Finished | [8.4/10](audit/wang_hall/independent_grade_final/result.json) | — |
| Wiley Hall | [wiley_hall.blend](modular/buildings/wiley_hall.blend) | Finished | [8.3/10](audit/wiley_hall/independent_grade_r2.md) | — |
| Wood Street Parking Garage | [massing_wood_street_garage_pgw_2fa056e.blend](modular/buildings/massing_wood_street_garage_pgw_2fa056e.blend) | Finished | [8.7/10](audit/purdue_wood_street_garage_pgw/independent_grade/result.json) | — |
| Winifred Parker Hall | [winifred_parker_hall.blend](modular/buildings/winifred_parker_hall.blend) | Finished | [8.05/10](audit/winifred_parker_hall/independent_grade_r5.md) | — |
| Ernest C. Young Hall (YONG) | [massing_young_hall_yong_cae1b95.blend](modular/buildings/massing_young_hall_yong_cae1b95.blend) | Finished | [8.35/10](audit/young_hall_yong_cael95/independent_grade_master_integration/result.json) | — |
| Yue-Kong Pao Hall | [massing_yue_kong_pao_hall_a3cb766.blend](modular/buildings/massing_yue_kong_pao_hall_a3cb766.blend) | Finished | [8.0/10](audit/yue_kong_pao_hall/independent_grade_r1.md) | — |
| Zeta Tau Alpha | [zeta_tau_alpha.blend](modular/buildings/zeta_tau_alpha.blend) | Finished | [8.2/10](audit/zeta_tau_alpha/independent_grade_r2.md) | — |

| Zundo Family Dentistry | [zundo_family_dentistry.blend](modular/buildings/zundo_family_dentistry.blend) | Finished | [8.0/10](audit/zundo_family_dentistry/independent_grade_r2.md) | — |
| Islamic Society of Greater Lafayette (ISGL) | [massing_islamic_societyof_greater_lafayette_0130012.blend](modular/buildings/massing_islamic_societyof_greater_lafayette_0130012.blend) | Finished; GIS identity/address and roof/height details remain uncertain; interior is schematic | [8.2/10](audit/islamic_society_greater_lafayette/independent_grade_codex_r3/result.json) | — |
| Village Bottle Shoppe | [massing_village_bottle_shoppe_6a17e23.blend](modular/buildings/massing_village_bottle_shoppe_6a17e23.blend) | Finished; entry bearing, height, and unseen elevations remain uncertain | [8.7/10](audit/village_bottle_shoppe/independent_grade_r3/result.json) | — |
| Phi Gamma Delta | [massing_house_301837281_58ead22.blend](modular/buildings/massing_house_301837281_58ead22.blend) | Finished; facade divisions, roof, heights remain estimated; interior unmodeled because plans are not registered to GIS | [8.5/10](audit/phi_gamma_delta/independent_grade_r2/grade_report.md) | — |
| Phi Kappa Sigma | [massing_phi_kappa_sigma_fid829.blend](modular/buildings/massing_phi_kappa_sigma_fid829.blend) | Finished; master fresh-open PASS; wing heights remain estimates; interior omitted because no verified plan was found | [8.55/10](audit/phi_kappa_sigma/independent_grade_revision_2/result.json) | — |
| Lambertus Hall | [lambertus_hall.blend](modular/buildings/lambertus_hall.blend) | Finished; 16 m height and some facade-wing attribution estimated | [8.0/10](audit/lambertus_hall/independent_grade/grade.json) | — |
| Latino Cultural Center (current, FID 925) | [massing_latino_cultural_center_lcc_9cc71b3.blend](modular/buildings/massing_latino_cultural_center_lcc_9cc71b3.blend) | Finished; height and schematic interior remain estimates | [9.0/10](audit/latino_cultural_center_lcc_9cc71b3/independent_grade/grade.json) | — |
| Life Science Ranges Greenhouse & Service Building (LSR) | [massing_life_science_ranges_greenhouse_and_service_building_c96231f.blend](modular/buildings/massing_life_science_ranges_greenhouse_and_service_building_c96231f.blend) | Finished; master fresh-open PASS; heights remain estimates | [8.1/10](audit/life_science_ranges_greenhouse_and_service_building_c96231f/independent_grade_r2/result.json) | — |
| Ward L. Lambert Fieldhouse and Gymnasium | [lambert_fieldhouse.blend](modular/buildings/lambert_fieldhouse.blend) | Finished; exact FID 261 footprint registered, grade and master link verified; height/roof and historic hall/gym arrangement remain estimated | [8.2/10](audit/lambert_fieldhouse/independent_grade_r9_clean/result.json) | — |
| Lilly Hall of Life Sciences | [massing_lilly_hall_e7fc13e.blend](modular/buildings/massing_lilly_hall_e7fc13e.blend) | Finished | [8.0/10](audit/massing_lilly_hall_e7fc13e/independent_grade/r1/grade.json) | — |
| Mann Hall | [massing_mann_hall_2b4ebda.blend](modular/buildings/massing_mann_hall_2b4ebda.blend) | Finished | [8.2/10](audit/massing_mann_hall_2b4ebda/independent_grade/r1/grade.json) | — |
| Ralph & Bettye Bailey Hall (BALY) | [massing_ralph_bettye_bailey_hall_406c4db.blend](modular/buildings/massing_ralph_bettye_bailey_hall_406c4db.blend) | Finished; master fresh-open PASS; facade direction, heights, and first-floor interior layout remain estimates or schematic | [8.1/10](audit/ralph_bettye_bailey_hall/independent_grade_new/grade.json) | — |
| Roy L. Whistler Hall of Agricultural Research (WSLR) | [massing_whistler_hall_6f6bf8d.blend](modular/buildings/massing_whistler_hall_6f6bf8d.blend) | Finished; master fresh-open PASS; roof, facade, and interior details remain estimates or schematic | [8.9/10](audit/whistler_hall/independent_grade_r2/result.json) | — |
| Wiley Dining Court (WDCT) | [massing_wiley_dining_court_wdct_8a6c669.blend](modular/buildings/massing_wiley_dining_court_wdct_8a6c669.blend) | Finished; master fresh-open PASS; eaves/ridge height and dining layout remain estimated or schematic | [8.0/10](audit/wiley_dining_court/independent_grade/grade.json) | — |
| Joyful Journeys | [massing_joyful_journeys_abaf5c3.blend](modular/buildings/massing_joyful_journeys_abaf5c3.blend) | Finished; independently regraded on exact SHA and linked in master; height/facade details estimated; no interior modeled | [8.0/10](audit/joyful_journeys/independent_grade_current/grade.json) | — |
## Unfinished buildings (108 total)

This inventory covers the full 508-record campus-map snapshot; features can be duplicate or support structures, so unresolved source records remain under review rather than being invented as separate buildings. The 106 current projects below are supplemented by two newer West Lafayette construction projects not represented as modeled assets in that snapshot, for 108 known unfinished projects. Current pending assignments: Tobin 9, Rossen 29, Kyle 22, Rohan 28, Arjav 20, Brady 0. These totals count work awaiting master integration as unfinished: Rossen's 29 currently comprise 26 independently passed models awaiting master-blend integration and 3 buildings or facility identities still needing research. The Tobin, Rossen, and Kyle queues now contain 60 projects; 48 remain with Rohan, Arjav, and Brady.

### New West Lafayette construction projects (2)

These projects are absent from the modeled-asset inventory and need current plan/site research plus a verified GIS footprint before modeling. They are separate from Indianapolis projects and off-campus housing.

| Building | Current source / map match | Work needed | Assigned to |
| --- | --- | --- | --- |
| Nursing and Pharmacy Education Building | [Purdue project page](https://www.purdue.edu/provost/academic-facilities-upcoming-facilities/); no confirmed campus-map FID or master asset | Build from current plans and site imagery; establish footprint and placement | Kyle |
| Daniels School of Business, new building | [Purdue project page](https://www.purdue.edu/provost/academic-facilities-upcoming-facilities/); campus-map reference FID 548 has no linked asset | Reconcile FID 548 with the construction footprint, then build and place the new facility | Kyle |

### Detailed models in progress, awaiting a grade, or awaiting master integration (51)

| Building | Current detailed model | Latest grader score | Assigned to |
| --- | --- | ---: | --- |
| The Caretaker’s Cottage | [`massing_the_caretaker_s_cottage_6b24af9.blend`](modular/buildings/massing_the_caretaker_s_cottage_6b24af9.blend) | [8.1/10](audit/massing_the_caretaker_s_cottage_6b24af9/independent_grade_r2.json); linked in latest master; awaiting Tobin validation | Rossen |
| Purdue University Daniel Turf Center | [`massing_purdue_university_daniel_turf_center_e69b7da.blend`](modular/buildings/massing_purdue_university_daniel_turf_center_e69b7da.blend) | [8.6/10](audit/massing_purdue_university_daniel_turf_center_e69b7da/independent_grade_r3/independent_grade_r3.json); linked in latest master; awaiting Tobin validation | Rossen |
| The Moosehead Lounge | [`massing_the_moosehead_lounge_f81529e.blend`](modular/buildings/massing_the_moosehead_lounge_f81529e.blend) | [8.2/10](audit/massing_the_moosehead_lounge_f81529e/independent_grade_r2.json); linked in latest master; awaiting Tobin validation | Rossen |
| The Church of Jesus Christ of Latter-day Saints Institute of Religion | [`massing_the_church_of_jesus_christ_of_latter_day_saints_6f2a451.blend`](modular/buildings/massing_the_church_of_jesus_christ_of_latter_day_saints_6f2a451.blend) | [8.3/10](audit/massing_the_church_of_jesus_christ_of_latter_day_saints_6f2a451/independent_grade_r2.json); linked in latest master; awaiting Tobin validation | Rossen |
| Convergence Center for Innovation and Collaboration | [`convergence_center.blend`](modular/buildings/convergence_center.blend) | Not graded | Rohan |
| Dauch Alumni Center | [`dauch_alumni_center.blend`](modular/buildings/dauch_alumni_center.blend) | 7.2/10 | Rohan |
| David and Bonnie Brunner Farm Animal Hospital | [`david_and_bonnie_brunner_farm_animal_hospital.blend`](modular/buildings/david_and_bonnie_brunner_farm_animal_hospital.blend) | 6.7/10 | Rohan |
| Drew and Brittany Brees Student Athletic Academic Center | [`brees_student_athletic_academic_center.blend`](modular/buildings/brees_student_athletic_academic_center.blend) | 7.3/10 | Rohan |
| Electrical Engineering | [`electrical_engineering.blend`](modular/buildings/electrical_engineering.blend) | 5.2/10 | Rohan |
| Elliott Hall Of Music | [`elliott_hall_of_music.blend`](modular/buildings/elliott_hall_of_music.blend) | 7.1/10 | Rohan |
| Felix Haas Hall | [`felix_haas_hall.blend`](modular/buildings/felix_haas_hall.blend) | 7.4/10 | Rohan |
| Flex Lab | [`flex_lab.blend`](modular/buildings/flex_lab.blend) | 7.5/10 | Rohan |
| Ford Dining Court | [`ford_dining_court.blend`](modular/buildings/ford_dining_court.blend) | 6.8/10 | Rohan |
| Frieda Parker Hall | [`frieda_parker_hall.blend`](modular/buildings/frieda_parker_hall.blend) | Not graded | Rohan |
| Hall for Discovery and Learning Research | [`hall_for_discovery_and_learning_research.blend`](modular/buildings/hall_for_discovery_and_learning_research.blend) | 7.3/10 | Rohan |
| Hansen Life Sciences | [`hansen_life_sciences.blend`](modular/buildings/hansen_life_sciences.blend) | Not graded | Rohan |
| Heine Pharmacy | [`heine_pharmacy.blend`](modular/buildings/heine_pharmacy.blend) | 7.5/10 | Rohan |
| Hicks Library | [`hicks_library.blend`](modular/buildings/hicks_library.blend) | 6.6/10 | Rohan |
| Horticulture Building | [`horticulture_building.blend`](modular/buildings/horticulture_building.blend) | 7.0/10 | Rohan |
| Purdue Police Department (TERY) | [`massing_purdue_police_department_19f467e.blend`](modular/buildings/massing_purdue_police_department_19f467e.blend) | [8.4/10](audit/massing_purdue_police_department_19f467e/independent_grade/grade_result.json); linked in latest master; awaiting Tobin validation | Rossen |
| Purdue Village Administration Building | [`massing_purdue_village_administration_building_3faae6c.blend`](modular/buildings/massing_purdue_village_administration_building_3faae6c.blend) | [8.5/10](audit/massing_purdue_village_administration_building_3faae6c/independent_grade/evaluation_r2.json); linked in latest master; awaiting Tobin validation | Rossen |
| Provenance Apartments 005 | [`massing_provenance_apartments_005_960f6b0.blend`](modular/buildings/massing_provenance_apartments_005_960f6b0.blend) | [8.3/10](audit/massing_provenance_apartments_005_960f6b0/independent_grade_r4.json); linked in latest master; awaiting Tobin validation | Rossen |
| Pete Dye Clubhouse | [`massing_the_pete_dye_clubhouse_a3a9641.blend`](modular/buildings/massing_the_pete_dye_clubhouse_a3a9641.blend) | [8.5/10](audit/massing_the_pete_dye_clubhouse_a3a9641/independent_grade/pete_dye_independent_grade_r2.json); linked in latest master; awaiting Tobin validation | Rossen |
| Phi Delta Theta | [`massing_phi_delta_theta_258cddd.blend`](modular/buildings/massing_phi_delta_theta_258cddd.blend) | [8.3/10](audit/massing_phi_delta_theta_258cddd/independent_grade_r1/independent_grade.json); linked in latest master; awaiting Tobin validation | Rossen |
| Pi Kappa Alpha (Pike) | [`massing_house_301841252_e4f8f05.blend`](modular/buildings/massing_house_301841252_e4f8f05.blend) | [8.7/10](audit/massing_house_301841252_e4f8f05/independent_grade_r1/grade.json); linked in latest master; awaiting Tobin validation | Rossen |
| Pi Kappa Phi (Omega) | [`massing_pi_kappa_phi_50e4645.blend`](modular/buildings/massing_pi_kappa_phi_50e4645.blend) | [8.4/10](audit/pi_kappa_phi/independent_grade/grade_result.json); linked in latest master; awaiting Tobin validation; proposed replacement permit status unverified | Rossen |
| Phi Kappa Tau | [`massing_phi_kappa_tau_139b9d7.blend`](modular/buildings/massing_phi_kappa_tau_139b9d7.blend) | [8.3/10](audit/phi_kappa_tau/independent_grade/independent_grade_result.json); linked in latest master; awaiting Tobin validation; corrected to FID 820 / 416 N Chauncey; roof and facade details remain estimated | Rossen |
| Sigma Nu | [`massing_house_301841330_f58ae87.blend`](modular/buildings/massing_house_301841330_f58ae87.blend) | [8.0/10](audit/sigma_nu/independent_grade_r3/independent_grade_r3.json); linked in latest master; awaiting Tobin validation | Rossen |
| Sigma Alpha Epsilon | [`massing_sigma_alpha_epsilon_fid849.blend`](modular/buildings/massing_sigma_alpha_epsilon_fid849.blend) | [8.0/10](audit/sae_fid849/independent_grade_result.json); linked in latest master; awaiting Tobin validation; roof, height and facade remain estimated | Rossen |
| Sigma Phi Epsilon | [`massing_house_301841250_d63b09a.blend`](modular/buildings/massing_house_301841250_d63b09a.blend) | [8.65/10](audit/sigma_phi_epsilon/independent_grade_r3/independent_grade_r3.json); linked in latest master; awaiting Tobin validation | Rossen |
| Sigma Pi | [`massing_house_301836568_0fbca0e.blend`](modular/buildings/massing_house_301836568_0fbca0e.blend) | [8.1/10](audit/sigma_pi/independent_grade/grade_result_r5.json); linked in latest master; awaiting Tobin validation; wall line/story count and LiDAR-derived roof remain estimates | Rossen |
| Theta Chi | [`massing_house_301841328_39f169f.blend`](modular/buildings/massing_house_301841328_39f169f.blend) | [8.5/10](audit/theta_chi/independent_grade/grade_result.json); linked in latest master; awaiting Tobin validation | Rossen |
| Stone Hall (STON) | [`massing_stone_hall_ston_d3f479a.blend`](modular/buildings/massing_stone_hall_ston_d3f479a.blend) | [8.0/10](audit/massing_stone_hall_ston_d3f479a/independent_grade_r2.json); linked in latest master; awaiting Tobin validation | Rossen |
| Student Health Center (PUSH) | [`massing_student_health_center_push_1200c3b.blend`](modular/buildings/massing_student_health_center_push_1200c3b.blend) | [8.2/10](audit/massing_student_health_center_push_1200c3b/independent_grade/independent_grade_r2.json); linked in latest master; awaiting Tobin validation | Rossen |
| Union Club Hotel | [`massing_union_club_hotel_0d22460.blend`](modular/buildings/massing_union_club_hotel_0d22460.blend) | [8.1/10](audit/massing_union_club_hotel_0d22460/independent_grade_r2.json); linked in latest master; awaiting Tobin validation | Rossen |
| Redeemer Lutheran Church | [`massing_redeemer_lutheran_church_2e5ce2f.blend`](modular/buildings/massing_redeemer_lutheran_church_2e5ce2f.blend) | [8.0/10](audit/redeemer_lutheran_church/independent_grade_kyle.json); awaiting master integration | Kyle |
| Marc and Sharon Hagle Hall (HAGL) | [`massing_marc_and_sharon_hagle_hall_hagl_071ffd6.blend`](modular/buildings/massing_marc_and_sharon_hagle_hall_hagl_071ffd6.blend) | [8.5/10](audit/massing_marc_and_sharon_hagle_hall_hagl_071ffd6/grade.json); awaiting master integration | Kyle |
| Matthews Hall (MTHW) | [`massing_matthews_hall_mthw_9326885.blend`](modular/buildings/massing_matthews_hall_mthw_9326885.blend) | [8.75/10](audit/matthews_hall_mthw_9326885/grade_result.json); awaiting master integration | Kyle |
| McDonald's | [`massing_mcdonald_s_ab77b70.blend`](modular/buildings/massing_mcdonald_s_ab77b70.blend) | [9.0/10](audit/mcdonald_s/independent_grade_revision2.json); awaiting master integration | Kyle |
| MRI Modular Facility (MRI1 / PMRI) | [`massing_mri_modular_facility_mri1_a93e22b.blend`](modular/buildings/massing_mri_modular_facility_mri1_a93e22b.blend) | [8.0/10](audit/mri_modular_facility/independent_grade_mri.json); awaiting master integration | Kyle |
| Our Saviour Lutheran Church | [`massing_our_saviour_lutheran_church_118afa2.blend`](modular/buildings/massing_our_saviour_lutheran_church_118afa2.blend) | [8.75/10](audit/massing_our_saviour_lutheran_church_118afa2/independent_grade.json); awaiting master integration | Kyle |
| Smith Hall | [`massing_smith_hall_4c2018f.blend`](modular/buildings/massing_smith_hall_4c2018f.blend) | [8.5/10](audit/smith_hall/independent_grade_kyle.json); awaiting master integration | Kyle |
| Marriott Hall | [`massing_marriot_hall_7cd3eb5.blend`](modular/buildings/massing_marriot_hall_7cd3eb5.blend) | [8.5/10](audit/marriott_hall/grade.json); awaiting master integration | Kyle |
| Martin C. Jischke Hall of Biomedical Engineering | [`massing_martin_c_jischke_hall_of_biomedical_engineering_1a34d6a.blend`](modular/buildings/massing_martin_c_jischke_hall_of_biomedical_engineering_1a34d6a.blend) | [8.0/10](audit/martin_c_jischke_hall/grade.json); awaiting master integration | Kyle |
| Philip E. Nelson Hall of Food Science (NLSN) | [`massing_philip_e_nelson_hall_of_food_science_nlsn_6b2ba6b.blend`](modular/buildings/massing_philip_e_nelson_hall_of_food_science_nlsn_6b2ba6b.blend) | [8.5/10](audit/massing_philip_e_nelson_hall_of_food_science_nlsn_6b2ba6b/independent_grade_kyle.json); awaiting master integration | Kyle |
| Virginia C. Meredith Residence Hall | [`massing_meredith_hall_4bb4188.blend`](modular/buildings/massing_meredith_hall_4bb4188.blend) | [8.5/10](audit/meredith_hall/independent_grade.json); awaiting master integration | Kyle |
| Telecommunications Building (TEL) | [`massing_telecommunications_building_tel_8dfaccf.blend`](modular/buildings/massing_telecommunications_building_tel_8dfaccf.blend) | [8.0/10](audit/massing_telecommunications_building_tel_8dfaccf/independent_grade/grade.json); linked in latest master; awaiting Tobin validation | Rossen |
| Twin Pines Cooperative | [`massing_twin_pines_cooperative_8f606f9.blend`](modular/buildings/massing_twin_pines_cooperative_8f606f9.blend) | [8.3/10](audit/massing_twin_pines_cooperative_8f606f9/independent_grade/twin_pines_independent_grade.json); linked in latest master; awaiting Tobin validation | Rossen |
| Turf Recreation Exercise Center (TREC) | [`massing_turf_recreation_exercise_center_9622f45.blend`](modular/buildings/massing_turf_recreation_exercise_center_9622f45.blend) | [8.1/10](audit/massing_turf_recreation_exercise_center_9622f45/independent_grade_r4.json); linked in latest master; awaiting Tobin validation | Rossen |
| Triangle | [`massing_triangle_fraternity_8477ad9.blend`](modular/buildings/massing_triangle_fraternity_8477ad9.blend) | [8.0/10](audit/triangle/independent_grade/result.json); linked in latest master; awaiting Tobin validation; height, story count and facade detail remain estimated | Rossen |
| Unitarian Universalist Church of Tippecanoe County | [`massing_unitarian_universalist_church_of_tippecanoe_county_2a6793d.blend`](modular/buildings/massing_unitarian_universalist_church_of_tippecanoe_county_2a6793d.blend) | [8.5/10](audit/unitarian_universalist_church_of_tippecanoe_county_2a6793d/independent_grade_kyle.json); awaiting master integration | Kyle |



### Buildings that still have only massing models (16)

Verify each stable asset ID in `modular/manifest.json` before starting a new model. The master scene controls campus placement through its placement markers.

| Building | Current massing asset | Assigned to |
| --- | --- | --- |
| marstellar | [`massing_marstellar_0c2ea90.blend`](modular/buildings/marstellar_0c2ea90.blend) | Kyle |
| meredith hall south | [`massing_meredith_hall_south_ffbc444.blend`](modular/buildings/massing_meredith_hall_south_ffbc444.blend) | Kyle |
| northwestern parking garage | [`massing_northwestern_parking_garage_979f1a2.blend`](modular/buildings/massing_northwestern_parking_garage_979f1a2.blend) | Kyle |
| provenance apartments | [`massing_provenance_apartments_d913384.blend`](modular/buildings/massing_provenance_apartments_d913384.blend) | Kyle |
| provenance apartments 001 | [`massing_provenance_apartments_001_1b3223b.blend`](modular/buildings/massing_provenance_apartments_001_1b3223b.blend) | Kyle |
| provenance apartments 002 | [`massing_provenance_apartments_002_a9a7f4a.blend`](modular/buildings/massing_provenance_apartments_002_a9a7f4a.blend) | Kyle |
| provenance apartments 003 | [`massing_provenance_apartments_003_682c8e8.blend`](modular/buildings/massing_provenance_apartments_003_682c8e8.blend) | Kyle |
| provenance apartments 004 | [`massing_provenance_apartments_004_1bc10e3.blend`](modular/buildings/massing_provenance_apartments_004_1bc10e3.blend) | Kyle |
| riverside covenannt church | [`massing_riverside_covenannt_church_3a60684.blend`](modular/buildings/massing_riverside_covenannt_church_3a60684.blend) | Arjav |
| schleman hall schm | [`massing_schleman_hall_schm_ad4b05b.blend`](modular/buildings/massing_schleman_hall_schm_ad4b05b.blend) | Arjav |
| shealy frances m residence hall | [`massing_shealy_frances_m_residence_hall_a210e50.blend`](modular/buildings/massing_shealy_frances_m_residence_hall_a210e50.blend) | Arjav |
| shreve hall | [`massing_shreve_hall_06d270a.blend`](modular/buildings/massing_shreve_hall_06d270a.blend) | Arjav |
| slayter center for performing arts | [`massing_slayter_center_for_performing_arts_f45259b.blend`](modular/buildings/massing_slayter_center_for_performing_arts_f45259b.blend) | Arjav |
| smalley center | [`massing_smalley_center_1902608.blend`](modular/buildings/massing_smalley_center_1902608.blend) | Arjav |

| von s | [`massing_von_s_d207e41.blend`](modular/buildings/massing_von_s_d207e41.blend) | Tobin |
| west lafayette intermediate school | [`massing_west_lafayette_intermediate_school_d72f0fa.blend`](modular/buildings/massing_west_lafayette_intermediate_school_d72f0fa.blend) | Tobin |
| west lafayette junior senior high school | [`massing_west_lafayette_junior_senior_high_school_fa45bd1.blend`](modular/buildings/massing_west_lafayette_junior_senior_high_school_fa45bd1.blend) | Tobin |
| windsor halls | [`massing_windsor_halls_80aeb51.blend`](modular/buildings/massing_windsor_halls_80aeb51.blend) | Tobin |


### Fraternity, sorority, and cooperative facilities

The unfinished fraternity table below currently lists 17 facility or identity-resolution cases: 5 assigned to Tobin and 12 to Rossen. The legacy Kappa Sigma house is independently graded 8.5/10 and appears in the finished table above. Sixteen of the current 36 IFC-listed organizations have finished entries above: Acacia, Alpha Chi Rho, Alpha Epsilon Pi, Alpha Gamma Rho, Alpha Kappa Lambda, Alpha Sigma Phi, Alpha Tau Omega, Beta Sigma Psi, Beta Upsilon Chi (formerly Fairway Cooperative), Delta Sigma Phi, Delta Tau Delta, Delta Upsilon, FarmHouse, Kappa Delta Rho, Phi Gamma Delta, and Phi Kappa Sigma. Rows without a confirmed campus-map match remain facility-research work; do not invent a house location from organization membership alone.

Across the detailed-model and fraternity tables, Rossen has 29 open assignment records: 26 graded models awaiting final master-integration validation and 3 facility-research cases. A fresh read-only Blender 5.2.3 audit of the latest master found all 26 asset paths linked, with counts and bounds matching the manifest. Tobin still needs to confirm that all prior massings were removed; the 26 handoffs therefore remain open. The three research cases still lack a confirmed current facility and footprint, so no additional model is justified. The number 29 counts open assignment records, not buildings still needing an initial build or 29 confirmed distinct structures. See [the latest master integration audit](audit/rossen_master_integration_audit_2026-10-26.md) and the building-specific research records.

Coverage was checked against Purdue's current [IFC](https://www.purdue.edu/fscl/councils/ifc/chapters.php), [Panhellenic](https://www.purdue.edu/fscl/councils/pha/chapters.php), [MGC](https://www.purdue.edu/fscl/councils/mgc/chapters.php), [NPHC](https://www.purdue.edu/fscl/councils/nphc/chapters.php), and [cooperative-house](https://www.purdue.edu/fscl/councils/cooperatives/houses.php) lists. Purdue describes FSCL as five councils with 90 organizations; the model inventory tracks physical facilities rather than treating each organization as a separate building ([FSCL overview](https://www.purdue.edu/vpsl/news/featured-stories/2026_0105-fscl-150-recap.php)). Add any MGC or NPHC facility if a dedicated physical house is verified. A spatial candidate is not treated as a confirmed match until its footprint is checked.

#### Fraternity houses (17 listed unfinished cases: Tobin 5, Rossen 12)

| House / building | GIS FID and asset | Work status | Assigned to |
| --- | --- | --- | --- |

| Beta Theta Pi | FID 826; New asset/source mapping required | No reliable asset match; build from GIS FID 826 and house evidence | Tobin |
| Chi Psi | No reliable map FID; New asset/source mapping required | No official map feature or asset match; research chapter facility | Tobin |
| Delta Chi | No reliable map FID; New asset/source mapping required | No official map feature or asset match; research chapter facility | Tobin |
| Phi Kappa Psi | FID 856 is a candidate at 1307 Tower Dr; GIS label conflicts with the current official chapter address | Reconcile the FID 856 / existing asset crosswalk before modeling | Tobin |
| Phi Kappa Theta | No verified current house/FID; FID 762 at 900 David Ross is supported by current ZBT sources, while the Purdue GIS label remains Phi Kappa Theta | Verify Phi Kappa Theta's current facility independently; do not duplicate FID 762 | Tobin |
| Pi Kappa Alpha (Pike) | FID 790; [massing_house_301841252_e4f8f05](modular/buildings/massing_house_301841252_e4f8f05.blend) | Independently graded 8.7/10; linked in latest master; awaiting Tobin validation; wall height and roof remain estimates | Rossen |
| Psi Upsilon | Delta Omicron chapter status is verified; current dedicated facility/address is not. No current chapter-linked address or campus GIS match was found; 400 Northwestern and 1198 Third remain excluded | Verify a dedicated facility and address, then match occupancy to a parcel/GIS feature; see the [latest facility recheck](audit/psi_upsilon/current_facility_recheck_2026-10-26_addendum4.md) | Rossen |
| Sigma Alpha Mu | Current national roll and property page support a Purdue management account but give no property address; campus GIS and county parcel address queries found no current match. A Sigma Eta page calling the group an Interest Group is stale | Current house and GIS crosswalk remain unresolved; see the [latest facility recheck](audit/sigma_alpha_mu/current_facility_recheck_2026-10-26_addendum2.md) | Rossen |
| Sigma Chi | FID 828; [massing_sigma_chi_fid828](modular/buildings/massing_sigma_chi_fid828.blend) | [8.25/10 pass](audit/sigma_chi/independent_grade_r3/sigma_chi_independent_grade_r3.json); linked in latest master; awaiting Tobin validation; height/floors and detailed facade remain uncertain | Rossen |
| Sigma Nu | FID 758; [massing_house_301841330_f58ae87](modular/buildings/massing_house_301841330_f58ae87.blend) | Independently graded 8.0/10; linked in latest master; awaiting Tobin validation; wall line, height and roof remain uncertain | Rossen |
| Sigma Phi Epsilon | FID 789; [massing_house_301841250_d63b09a](modular/buildings/massing_house_301841250_d63b09a.blend) | Independently graded 8.65/10; linked in latest master; awaiting Tobin validation; dimensions and roof remain estimates | Rossen |
| Sigma Pi | FID 776; [massing_house_301836568_0fbca0e](modular/buildings/massing_house_301836568_0fbca0e.blend) | [8.1/10](audit/sigma_pi/independent_grade/grade_result_r5.json); linked in latest master; awaiting Tobin validation; GIS roof outline ring error 0.000017 m; wall/story and LiDAR roof elevations remain estimates | Rossen |
| Theta Chi | FID 760; [massing_house_301841328_39f169f](modular/buildings/massing_house_301841328_39f169f.blend) | Independently graded 8.5/10; linked in latest master; awaiting Tobin validation; 8.8 m height and roof details remain estimates | Rossen |
| Zeta Beta Tau | FID 762 / 900 David Ross; current ZBT sources support this site, while GIS retains the historic/conflicting Phi Kappa Theta label; [massing_house_301841332_9b3bd1f](modular/buildings/massing_house_301841332_9b3bd1f.blend) | [8.5/10](audit/zeta_beta_tau/independent_grade/grade_result.json); linked in latest master; awaiting Tobin validation; 12 GIS ring vertices match within 0.000043 m; roof height/floors and facade remain estimates | Rossen |
| Zeta Psi | Tau Gamma student affiliation is current, but its residential address is not established; the undated 237 S Grant lead appears stale, and occupancy at 950 David Ross conflicts with a Chi Psi lodge source. Existing geometry is insufficient for a passing model | No defensible current FID/address/footprint yet; see the [latest occupancy recheck](audit/zeta_psi/occupancy_recheck_2026-10-26_addendum7.md) and [build feasibility assessment](audit/zeta_psi/build_feasibility_2026-10-26.md) | Rossen |
| Phi Kappa Tau | FID 820 (historic GIS label Theta Tau); [massing_phi_kappa_tau_139b9d7](modular/buildings/massing_phi_kappa_tau_139b9d7.blend) | Independently graded 8.3/10; linked in latest master; awaiting Tobin validation; current chapter source and alumni history support 416 N Chauncey; height and roof details remain estimated | Rossen |
| Triangle | FID 777; [massing_triangle_fraternity_8477ad9](modular/buildings/massing_triangle_fraternity_8477ad9.blend) | Independently graded 8.0/10; linked in latest master; awaiting Tobin validation; height, floor count, and facade detail remain estimated | Rossen |

#### Panhellenic chapters and house coverage (16 unfinished houses; two chapters have no house)

| House / building | GIS FID and asset | Work status | Assigned to |
| --- | --- | --- | --- |
| Alpha Chi Omega | FID 765; [massing_house_301841602_8190d79](modular/buildings/massing_house_301841602_8190d79.blend) | Spatial candidate; verify before detailing | Rohan |
| Kappa Delta | No reliable map FID; New asset/source mapping required | No official map feature or asset; research the chapter-house location | Rohan |
| Alpha Gamma Delta | FID 757; [massing_house_301841608_d56a4c4](modular/buildings/massing_house_301841608_d56a4c4.blend) | Massing asset; verify and detail | Arjav |
| Kappa Kappa Gamma | FID 782; [massing_house_301840871_5d1bc06](modular/buildings/massing_house_301840871_5d1bc06.blend) | Massing asset; verify and detail | Arjav |
| Alpha Omicron Pi | FID 756; [massing_house_301841607_63d85b5](modular/buildings/massing_house_301841607_63d85b5.blend) | Massing asset; verify and detail | Rohan |
| Phi Beta Chi | No verified house asset | PHA says two chapters have no house; no dedicated physical facility verified here, so hold outside the building backlog | — |
| Alpha Phi | FID 764; [massing_house_301841331_735e92f](modular/buildings/massing_house_301841331_735e92f.blend) | Massing asset; verify and detail | Arjav |
| Phi Mu | FID 772; [massing_house_301836574_fff1661](modular/buildings/massing_house_301836574_fff1661.blend) | Massing asset; verify and detail | Arjav |
| Alpha Xi Delta | FID 788; [massing_house_301841248_fe939c7](modular/buildings/massing_house_301841248_fe939c7.blend) | Massing asset; verify and detail | Arjav |
| Phi Sigma Rho | FID 744; [massing_house_301840873_a67ad63](modular/buildings/massing_house_301840873_a67ad63.blend) | Possible spatial candidate is 22.5 m from GIS center; confirm before reuse | Rohan |
| Pi Beta Phi | FID 774; [massing_house_301838781_891384f](modular/buildings/massing_house_301838781_891384f.blend) | Massing asset; verify and detail | Rohan |
| Delta Delta Delta | FID 753; [massing_house_301841333_affe21e](modular/buildings/massing_house_301841333_affe21e.blend) | Massing asset; verify and detail | Rohan |
| Sigma Alpha | No verified house asset | Purdue College of Agriculture reports this chapter has no house; GIS FID 795 stays in the general campus building queue pending identity review | — |
| Delta Gamma | FID 783; [massing_house_301840872_582df9d](modular/buildings/massing_house_301840872_582df9d.blend) | Massing asset; verify and detail | Arjav |
| Delta Zeta | FID 752; [massing_house_301841601_7ae6159](modular/buildings/massing_house_301841601_7ae6159.blend) | Massing asset; verify and detail | Arjav |
| Gamma Phi Beta | FID 759; [massing_house_301841329_bed5cb6](modular/buildings/massing_house_301841329_bed5cb6.blend) | Massing asset; verify and detail | Rohan |
| Sigma Kappa | FID 780; [massing_house_301840869_1b80ace](modular/buildings/massing_house_301840869_1b80ace.blend) | Massing asset; verify and detail | Arjav |
| Kappa Alpha Theta | FID 786; [massing_house_301840865_cbf7de2](modular/buildings/massing_house_301840865_cbf7de2.blend) | Candidate is 37 m from GIS center; verify mapping before reuse | Rohan |

#### Cooperative houses (11 unfinished)

| House / building | GIS FID and asset | Work status | Assigned to |
| --- | --- | --- | --- |
| Chauncey | FID 805; New asset/source mapping required | Several competing nearby assets; reconcile before modeling | Rohan |
| Ann Tweedale | FID 824; New asset/source mapping required | No nearby reliable asset match; build from official GIS reference | Rohan |
| Circle Pines | FID 761; [massing_house_301841609_c6c9ac4](modular/buildings/massing_house_301841609_c6c9ac4.blend) | Massing asset; verify and detail | Arjav |
| Devonshire | FID 405; New asset/source mapping required | No reliable asset match; research current house location | Arjav |
| Gemini | FID 825; New asset/source mapping required | No nearby reliable asset match; build from official GIS reference | Rohan |
| Glenwood | FID 794; [massing_house_301841249_f827941](modular/buildings/massing_house_301841249_f827941.blend) | Massing asset; verify and detail | Arjav |
| Marwood | FID 827; New asset/source mapping required | No nearby reliable asset match; build from official GIS reference | Arjav |
| Maclure | FID 822; New asset/source mapping required | Nearest candidate is over 112 m away; build/reconcile from official GIS reference | Rohan |
| Stewart | FID 802; [massing_house_1089875810_8c9b95d](modular/buildings/massing_house_1089875810_8c9b95d.blend) | Massing asset; verify and detail | Arjav |
| Shoemaker | FID 800; [massing_shoemaker_cooperative_2159ea4](modular/buildings/massing_shoemaker_cooperative_2159ea4.blend) | Existing assignment; massing only | Arjav |

#### Other Greek/co-ed house buildings (1 unfinished)

| House / building | GIS FID and asset | Work status | Assigned to |
| --- | --- | --- | --- |
| Evans Scholars House | FID 755; [massing_house_301841610_b6ad6ed](modular/buildings/massing_house_301841610_b6ad6ed.blend) | Co-ed Greek housing; separate from the current IFC assignment split | Rohan |

### Complete official campus-map reference inventory (508 records)

The reference layer includes named buildings, infrastructure/support structures, subdivisions, and duplicate candidates. “Direct FID match” means the master-building audit has a source-FID crosswalk; it does not certify the geometry or grade. Records without a direct match remain reconciliation work. Unrelated off-campus housing is outside the project scope even if it appears in an asset or nearby map data. The independent project-status tables above determine grade and ownership.

| GIS FID | Official map name | Master asset candidates | Crosswalk state |
| ---: | --- | --- | --- |
| 1 | Grounds Maintenance Facility | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 31 | Limestone Silo | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 32 | ASH SILO | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 33 | Fuel Oil Tank | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 34 | Waste Water Retention Tank | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 35 | Water Cooling Vent | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 36 | Overhead Conveyor | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 37 | U/G Conveyer | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 39 | Water Cooling Vent Tower A | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 40 | Water Cooling Vent Tower B | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 41 | Water Cooling Vent Tower C | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 42 | Water Cooling Vent Tower E | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 43 | Water Cooling Vent Tower F | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 48 | Water Cooling Vent Tower D | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 51 | Equine Health Sciences Annex | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 52 | Forney Hall Of Chemical Engineering | [massing_forney_hall_of_chemical_engineering_frny_d94ba3a](modular/buildings/massing_forney_hall_of_chemical_engineering_frny_d94ba3a.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 53 | Physical Facilities Service Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 54 | Krannert Building | [massing_krannert_school_of_management_26f5358](modular/buildings/massing_krannert_school_of_management_26f5358.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 55 | Boiler Television Building | [massing_house_1095763272_3c11463](modular/buildings/massing_house_1095763272_3c11463.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 56 | Stanley Coulter Hall | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 57 | John T. Mccutcheon Residence Hall | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 59 | Richard & Patricia Lawson Computer Science Building | [massing_lawson_hall_lwsn_49bd255](modular/buildings/massing_lawson_hall_lwsn_49bd255.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 60 | Franklin Levering Cary Quadrangle (West) | [massing_cary_quadrangle_west_cqw_3d47a7d](modular/buildings/massing_cary_quadrangle_west_cqw_3d47a7d.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 61 | Amelia Earhart Residence Hall | [massing_earhart_hall_0f14209](modular/buildings/massing_earhart_hall_0f14209.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 62 | Tom Spurgeon Golf Training Center | [massing_house_278460783_2bd1220](modular/buildings/massing_house_278460783_2bd1220.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 63 | Martha E. & Eugene K. Warren Residence Hall | [massing_windsor_halls_80aeb51](modular/buildings/massing_windsor_halls_80aeb51.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 64 | Elizabeth G. & William R. Wood Residence Hall | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 65 | Everett B. Vawter Residence Hall | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 66 | Windsor Dining Court | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 67 | Melvin L. Ollman Golf Cart Barn | [massing_house_278460782_43e46e7](modular/buildings/massing_house_278460782_43e46e7.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 68 | Water Tower | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 69 | Jerry S. Rawls Hall | [massing_house_1040689751_60aed07](modular/buildings/massing_house_1040689751_60aed07.blend)<br>[massing_house_1040689752_dcf4072](modular/buildings/massing_house_1040689752_dcf4072.blend)<br>[massing_house_1040689753_0542323](modular/buildings/massing_house_1040689753_0542323.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+6 more candidates) |
| 70 | Ernest C. Young Hall | [massing_young_hall_yong_cae1b95](modular/buildings/massing_young_hall_yong_cae1b95.blend) | Purdue GIS FID 70 footprint match within 0.000032 m; independently graded 8.35/10 in the integrated master. Placement/linked asset pass; GIS 11-level and Archives 10-story conflict, estimated height remains unresolved |
| 71 | Dick & Sandy Dauch Alumni Center | [massing_dauch_alumni_center_3cb1249](modular/buildings/massing_dauch_alumni_center_3cb1249.blend)<br>[massing_house_970455227_7c1ccac](modular/buildings/massing_house_970455227_7c1ccac.blend)<br>[massing_house_970455230_bc2f9b8](modular/buildings/massing_house_970455230_bc2f9b8.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 72 | Yue-Kong Pao Hall of Visual And Performing Arts | [massing_yue_kong_pao_hall_a3cb766](modular/buildings/massing_yue_kong_pao_hall_a3cb766.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 73 | Cooling Tower Equipment Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 74 | Northwest Chiller Plant | [massing_northwest_chiller_plant_nwcp_2b32fa6](modular/buildings/massing_northwest_chiller_plant_nwcp_2b32fa6.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 75 | Ross-Ade Stadium Locker Room | [massing_house_301840194_bc45c5c](modular/buildings/massing_house_301840194_bc45c5c.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 77 | Coal Storage Facility | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 78 | Veterinary Medicine Isolation Facility | [massing_veterinary_medicine_isolation_facility_66d1305](modular/buildings/massing_veterinary_medicine_isolation_facility_66d1305.blend) | Direct FID crosswalk; graded 8.5/10 and integrated in master; see audit/veterinary_medicine_isolation_facility/master_integration_2026-10-26.json |
| 79 | Richard Owen Residence Hall | [owen_hall](modular/buildings/owen_hall.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 80 | Burton D. Morgan Center For Entrepreneurship | [massing_morgan_center_for_entrepreneurship_mrgn_9ba681c](modular/buildings/massing_morgan_center_for_entrepreneurship_mrgn_9ba681c.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 81 | Fred And Mary Ford Dining Court | [massing_ford_dining_court_71eede4](modular/buildings/massing_ford_dining_court_71eede4.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 82 | David C. Pfendler Hall of Agriculture | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 83 | George A. Hawkins Hall | [massing_hawkins_hall_282335f](modular/buildings/massing_hawkins_hall_282335f.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 84 | Roy L. Whistler Hall Of Agricultural Research | [massing_whistler_hall_6f6bf8d](modular/buildings/massing_whistler_hall_6f6bf8d.blend) | Finished; independent grade 8.9/10; master fresh-open PASS; see audit/whistler_hall/ |
| 85 | Benjamin Harrison Residence Hall | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 87 | Northwest Campus Substation | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 88 | Gas Meter (at Airport) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 89 | Line Shack (at Airport) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 91 | Varsity Softball Press Box | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 92 | Purdue International Teleport Building 1 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 95 | Materials Management Storage Building 3 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 96 | Materials Management Storage Building 2 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 97 | Track Press Box | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 99 | University Residence Halls Satellite Transportation Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 101 | Well House No. 7 | [massing_house_936947593_6c6c6ff](modular/buildings/massing_house_936947593_6c6c6ff.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 102 | Well House No. 8 | [massing_house_1095755958_1200bd8](modular/buildings/massing_house_1095755958_1200bd8.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 103 | Well House No. 4 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 105 | Well House No. 5 | [massing_house_301911805_b68f48c](modular/buildings/massing_house_301911805_b68f48c.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 106 | Track Toilet + Storage Building | [massing_house_1034030154_5a9c337](modular/buildings/massing_house_1034030154_5a9c337.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 107 | American Railway Building | [massing_american_railway_building_rail_fc0f9a2](modular/buildings/massing_american_railway_building_rail_fc0f9a2.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 108 | Mechanical Engineering Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 109 | Max W & Maileen Brown Family Hall | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 110 | American Railway Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 111 | Horticultural Greenhouse Pavilion | [massing_house_301831856_0e54f11](modular/buildings/massing_house_301831856_0e54f11.blend)<br>[massing_house_942297382_8113f7f](modular/buildings/massing_house_942297382_8113f7f.blend)<br>[massing_marstellar_0c2ea90](modular/buildings/massing_marstellar_0c2ea90.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 116 | Oliver Perkins Terry House (OB2) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 117 | Oliver Perkins Terry House (OB3) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 118 | Oliver Perkins Terry House (OB1) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 157 | Northwest Chiller Cooling Towers | [massing_house_1196645144_a743419](modular/buildings/massing_house_1196645144_a743419.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 172 | Hilltop Apartment 23 | [massing_house_301841841_cae63c5](modular/buildings/massing_house_301841841_cae63c5.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 173 | Hilltop Apartment 26 | [massing_house_301841844_e14ef98](modular/buildings/massing_house_301841844_e14ef98.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 174 | Hilltop Apartment 24 | [massing_house_301841842_b941594](modular/buildings/massing_house_301841842_b941594.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 175 | Hilltop Apartment 25 | [massing_house_301841845_03c671f](modular/buildings/massing_house_301841845_03c671f.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 176 | Hilltop Apartment 27 | [massing_house_301841843_b4dfa04](modular/buildings/massing_house_301841843_b4dfa04.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 177 | Hilltop Apartment 10 | [massing_house_301842859_4c611ad](modular/buildings/massing_house_301842859_4c611ad.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 178 | Hilltop Apartment 9 | [massing_house_1095763307_9bc177c](modular/buildings/massing_house_1095763307_9bc177c.blend)<br>[massing_house_301842858_512c124](modular/buildings/massing_house_301842858_512c124.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 179 | Hilltop Apartment 15 | [massing_house_301841846_106a910](modular/buildings/massing_house_301841846_106a910.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 180 | Hilltop Apartment 20 | [massing_house_301842059_bdc2c0a](modular/buildings/massing_house_301842059_bdc2c0a.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 181 | Hilltop Apartment 8 | [massing_house_1095763308_1207499](modular/buildings/massing_house_1095763308_1207499.blend)<br>[massing_house_301842061_6244fcb](modular/buildings/massing_house_301842061_6244fcb.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 182 | Hilltop Apartment 17 | [massing_house_301842050_ac72696](modular/buildings/massing_house_301842050_ac72696.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 183 | Hilltop Apartment 16 | [massing_house_301842052_9138b2d](modular/buildings/massing_house_301842052_9138b2d.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 184 | Composites Laboratory | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 185 | Hilltop Apartment 7 | [massing_house_301842057_7fb5781](modular/buildings/massing_house_301842057_7fb5781.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 186 | Veterinary Laboratory Animal Building | [massing_house_301832121_95d8806](modular/buildings/massing_house_301832121_95d8806.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 187 | Hilltop Apartment 14 | [massing_house_301842860_5bdf00a](modular/buildings/massing_house_301842860_5bdf00a.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 188 | Hilltop Apartment 5 | [massing_house_301842055_5e4c54c](modular/buildings/massing_house_301842055_5e4c54c.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 189 | Hilltop Apartment 13 | [massing_house_301842861_9565929](modular/buildings/massing_house_301842861_9565929.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 190 | Hilltop Apartment 18 | [massing_house_301842049_62a05ee](modular/buildings/massing_house_301842049_62a05ee.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 191 | Hilltop Apartment 3 | [massing_house_301842051_bb4fe2a](modular/buildings/massing_house_301842051_bb4fe2a.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 192 | Hilltop Apartment 19 | [massing_house_301842056_5bc980e](modular/buildings/massing_house_301842056_5bc980e.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 193 | Hilltop Apartment 4 | [massing_house_301842053_03b2d5e](modular/buildings/massing_house_301842053_03b2d5e.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 194 | Hilltop Apartment 2 | [massing_house_301842060_c96be34](modular/buildings/massing_house_301842060_c96be34.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 196 | Hall of Data Science and AI | [massing_hall_of_data_science_and_ai_dsai_c8a41cc](modular/buildings/massing_hall_of_data_science_and_ai_dsai_c8a41cc.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 197 | John W. Hicks Undergraduate Library | [massing_hicks_undergraduate_library_hiks_9467680](modular/buildings/massing_hicks_undergraduate_library_hiks_9467680.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 199 | Telecommunications Building | [massing_telecommunications_building_tel_8dfaccf](modular/buildings/massing_telecommunications_building_tel_8dfaccf.blend) | Independently graded 8.0/10; FID 199 identity, footprint and placement verified; awaiting master integration (see TODO.md); facade and height remain uncertain |
| 201 | Tee-hangar No. 2 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 202 | Tee-hangar No. 3 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 203 | Hilltop Apartment 29 | [massing_house_301842867_f640b11](modular/buildings/massing_house_301842867_f640b11.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 204 | Hilltop Apartment 30 | [massing_house_301841840_00c1c70](modular/buildings/massing_house_301841840_00c1c70.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 205 | Hilltop Apartment 32 | [massing_house_301841839_64126a1](modular/buildings/massing_house_301841839_64126a1.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 206 | Hilltop Apartment 28 | [massing_house_301842868_b9233d2](modular/buildings/massing_house_301842868_b9233d2.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 207 | Hilltop Apartment 31 | [massing_house_301841838_ae21839](modular/buildings/massing_house_301841838_ae21839.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 208 | William H. Daniel Turfgrass Research & Diagnostic Court | [massing_purdue_university_daniel_turf_center_e69b7da](modular/buildings/massing_purdue_university_daniel_turf_center_e69b7da.blend) | FID 208 identity and plan ring verified; independently graded 8.6/10; awaiting master integration; height and facade bearing remain estimated |
| 209 | Airport Service Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 210 | Intramural Storage Shed | [massing_house_301911802_84bf1cd](modular/buildings/massing_house_301911802_84bf1cd.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 211 | Clayton W. Dement Fire Station | [massing_purdue_fire_department_520430b](modular/buildings/massing_purdue_fire_department_520430b.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 212 | Equine Health Sciences Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 213 | University Hall | [university_hall](modular/buildings/university_hall.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 214 | Leo Philip Doyle Laboratory | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 215 | Materials Management Storage Building 1 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 216 | Peirce Hall | [massing_pierce_hall_prce_e5f59eb](modular/buildings/massing_pierce_hall_prce_e5f59eb.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 218 | Helen R. Johnson Hall Of Nursing | [massing_johnson_hall_of_nursing_jnsn_823fca7](modular/buildings/massing_johnson_hall_of_nursing_jnsn_823fca7.blend) | Direct-linked in master; independent grade 9.3/10; fresh-open validation PASS; facade uncertainty retained |
| 219 | Entomology Environmental Lab | [massing_house_301958646_8b88cf5](modular/buildings/massing_house_301958646_8b88cf5.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 220 | Veterinary Pathology Building | [massing_veterinary_pathology_building_48b5a5b](modular/buildings/massing_veterinary_pathology_building_48b5a5b.blend) | Direct FID crosswalk; graded 8.2/10 and integrated in master; see audit/veterinary_pathology_building/master_integration_2026-10-26.json |
| 221 | Hangar No. 5 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 223 | Forestry Building | [massing_house_117396612_888779e](modular/buildings/massing_house_117396612_888779e.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 224 | Helen B. Schleman Hall | [massing_schleman_hall_schm_ad4b05b](modular/buildings/massing_schleman_hall_schm_ad4b05b.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 225 | John C. Smalley Center For Housing & Food Service Administration | [massing_smalley_center_1902608](modular/buildings/massing_smalley_center_1902608.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 227 | Mathematical Sciences Building | [math_sciences](modular/buildings/math_sciences.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 228 | Slayter Center of Performing Arts | [massing_house_1193671969_9b81773](modular/buildings/massing_house_1193671969_9b81773.blend)<br>[massing_slayter_center_for_performing_arts_f45259b](modular/buildings/massing_slayter_center_for_performing_arts_f45259b.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 230 | Class of 1950 Lecture Hall | [class_of_1950](modular/buildings/class_of_1950.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 231 | Life Science Animal Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 232 | Horticulture Building | [massing_horticulture_286a904](modular/buildings/massing_horticulture_286a904.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 233 | Felix Haas Hall | [felix_haas_hall](modular/buildings/felix_haas_hall.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 235 | Matthews Hall | [massing_matthews_hall_mthw_9326885](modular/buildings/massing_matthews_hall_mthw_9326885.blend) | Direct FID 235 verified; 8.75/10 pass; awaiting master integration |
| 236 | Grissom Hall | [massing_grissom_hall_01fd0e0](modular/buildings/massing_grissom_hall_01fd0e0.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 237 | Arthur G. Hansen Life Sciences Research Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 238 | Biochemistry Building | [massing_biochemistry_building_a267b8d](modular/buildings/massing_biochemistry_building_a267b8d.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 239 | Psychological Sciences Building | [massing_psychological_sciences_building_psyc_34efd04](modular/buildings/massing_psychological_sciences_building_psyc_34efd04.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 240 | Winthrop E. Stone Hall | [massing_house_1149668161_25bb857](modular/buildings/massing_house_1149668161_25bb857.blend)<br>[massing_stone_hall_ston_d3f479a](modular/buildings/massing_stone_hall_ston_d3f479a.blend) | Stone Hall asset independently graded 8.0/10; its mesh ring matches FID 240. Reconcile the second candidate massing during master integration (see TODO.md). Height remains estimated. |
| 241 | Willie M. Reed Animal Disease Diagnostic Laboratory | [massing_animal_disease_diagnostic_laboratory_b934354](modular/buildings/massing_animal_disease_diagnostic_laboratory_b934354.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 242 | Soil Erosion Lab | [massing_national_soil_erosion_laboratory_soil_0a1864c](modular/buildings/massing_national_soil_erosion_laboratory_soil_0a1864c.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 243 | Maurice G. Knoy Hall of Technology | [massing_knoy_hall_knoy_f598616](modular/buildings/massing_knoy_hall_knoy_f598616.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 244 | Hangar No. 6 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 245 | Aerospace Science Lab (hangar No. 3) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 246 | Herrick Acoustics | [massing_house_117396597_757136b](modular/buildings/massing_house_117396597_757136b.blend)<br>[massing_house_117396616_13da063](modular/buildings/massing_house_117396616_13da063.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 247 | Herbert C. Brown Laboratory of Chemistry | [massing_brown_laboratory_of_chemistry_brwn_aed3885](modular/buildings/massing_brown_laboratory_of_chemistry_brwn_aed3885.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 248 | Terminal Building (Hangar No. 2) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 249 | Smith Hall | [massing_smith_hall_4c2018f](modular/buildings/massing_smith_hall_4c2018f.blend) | Direct FID 249 footprint rebuilt; independent grade 8.5/10; awaiting master integration; height remains estimated |
| 250 | Philip E. Nelson Hall of Food Science | [massing_philip_e_nelson_hall_of_food_science_nlsn_6b2ba6b](modular/buildings/massing_philip_e_nelson_hall_of_food_science_nlsn_6b2ba6b.blend) | Direct FID 250 verified; all 24 ring vertices match within 0.000028 m; independent grade 8.5/10; awaiting master integration |
| 251 | Steven C. Beering Hall of Liberal Arts & Education | [beering_hall](modular/buildings/beering_hall.blend) | Duplicate BRNG massing record removed from the master; see `TODO.md` |
| 252 | Hangar No. 4 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 253 | Virginia C. Meredith Residence Hall | [massing_meredith_hall_4bb4188](modular/buildings/massing_meredith_hall_4bb4188.blend) | Direct FID 253 verified; 20 structural edges match within 0.000031 m; 8.5/10 pass; awaiting master integration |
| 254 | Wood Street Parking Garage | [massing_house_1040689750_cf5f616](modular/buildings/massing_house_1040689750_cf5f616.blend)<br>[massing_wood_street_garage_pgw_2fa056e](modular/buildings/massing_wood_street_garage_pgw_2fa056e.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 255 | Drew & Brittany Brees Student Athletic Center | [massing_drew_and_brittany_brees_student_athletic_academic_center_bres_da89033](modular/buildings/massing_drew_and_brittany_brees_student_athletic_academic_center_bres_da89033.blend)<br>[massing_house_1095763314_3ae3005](modular/buildings/massing_house_1095763314_3ae3005.blend)<br>[massing_house_1095763315_77ff7a6](modular/buildings/massing_house_1095763315_77ff7a6.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 256 | Armory | [armory](modular/buildings/armory.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 257 | Richard Benbridge Wetherill Lab Of Chemistry | [massing_r_b_wetherill_laboratory_of_chemistry_wthr_1577024](modular/buildings/massing_r_b_wetherill_laboratory_of_chemistry_wthr_1577024.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 258 | Eleanor B. Shreve Residence Hall | [massing_shreve_hall_06d270a](modular/buildings/massing_shreve_hall_06d270a.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 259 | Hillenbrand Residence Hall | [massing_hillenbrand_hall_a71e418](modular/buildings/massing_hillenbrand_hall_a71e418.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 260 | University Street Parking Garage | [massing_university_street_parking_garage_pgu_be81bec](modular/buildings/massing_university_street_parking_garage_pgu_be81bec.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 261 | Ward L. Lambert Field House & Gymnasium | [massing_lambert_ward_l_fieldhouse_and_gymnasium_1656862](modular/buildings/massing_lambert_ward_l_fieldhouse_and_gymnasium_1656862.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 262 | Stewart Center | [stewart_center](modular/buildings/stewart_center.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 263 | Forest Products Building | [massing_house_117396588_9fd9cca](modular/buildings/massing_house_117396588_9fd9cca.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 264 | Grant Street Parking Garage | [massing_grant_street_parking_garage_pgg_f46c894](modular/buildings/massing_grant_street_parking_garage_pgg_f46c894.blend)<br>[massing_house_1039675245_39cb220](modular/buildings/massing_house_1039675245_39cb220.blend)<br>[massing_house_1039675246_d5325ff](modular/buildings/massing_house_1039675246_d5325ff.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+2 more candidates) |
| 266 | Animal Holding Facility | [massing_animal_holding_facility_4733f46](modular/buildings/massing_animal_holding_facility_4733f46.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 267 | Agricultural Administration Building | [massing_agricultural_administration_building_120d92c](modular/buildings/massing_agricultural_administration_building_120d92c.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 268 | Horticultural Greenhouse | [massing_house_117396624_247aca3](modular/buildings/massing_house_117396624_247aca3.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 269 | Purdue International Teleport Building 2 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 270 | Purdue International Teleport Building 3 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 271 | Well House No. 6 | [massing_house_936947592_2c9982f](modular/buildings/massing_house_936947592_2c9982f.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 272 | Delon and Elizabeth Hampton Hall of Civil Engineering | [massing_hampton_hall_of_civil_engineering_hamp_9715f0e](modular/buildings/massing_hampton_hall_of_civil_engineering_hamp_9715f0e.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 273 | Physics Building | [massing_physics_building_phys_3bf42f3](modular/buildings/massing_physics_building_phys_3bf42f3.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 274 | Purdue University Student Health Center | [massing_student_health_center_push_1200c3b](modular/buildings/massing_student_health_center_push_1200c3b.blend) | Independently graded 8.2/10; orthophoto-supported massing and FID 274 footprint; awaiting master integration (see TODO.md); vertical dimensions remain estimates |
| 275 | Oliver Perkins Terry House | [massing_purdue_police_department_19f467e](modular/buildings/massing_purdue_police_department_19f467e.blend) | Verified operational PUPD / TERY match; independently graded 8.4/10; awaiting master integration (see TODO.md) |
| 276 | Oliver Perkins Terry Garage | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 277 | Frances M. Shealy Residence Hall | [massing_shealy_frances_m_residence_hall_a210e50](modular/buildings/massing_shealy_frances_m_residence_hall_a210e50.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 278 | Ophelia Duhme Residence Hall | [massing_duhme_ophelia_residence_hall_1bb4e9c](modular/buildings/massing_duhme_ophelia_residence_hall_1bb4e9c.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 279 | Golf Storage Maintenance Barn | [massing_house_1326355761_0268ebf](modular/buildings/massing_house_1326355761_0268ebf.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 280 | Golf Course Maintenance Barn | [massing_house_1326355760_f740868](modular/buildings/massing_house_1326355760_f740868.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 281 | Samuel Voinoff Golf Pavillion | [massing_house_278460784_e0d562b](modular/buildings/massing_house_278460784_e0d562b.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 282 | Pete Dye Clubhouse | [massing_house_278460781_155ff0c](modular/buildings/massing_house_278460781_155ff0c.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 283 | Women's Golf Locker Room | [massing_house_1047163440_bb941a5](modular/buildings/massing_house_1047163440_bb941a5.blend)<br>[massing_house_1047163441_47e194e](modular/buildings/massing_house_1047163441_47e194e.blend)<br>[massing_house_1047163442_f5496f3](modular/buildings/massing_house_1047163442_f5496f3.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+6 more candidates) |
| 284 | Purdue West - Building F | [massing_house_283526731_fae21ae](modular/buildings/massing_house_283526731_fae21ae.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 285 | Hilltop Apartment 11 | [massing_house_301842863_9739c93](modular/buildings/massing_house_301842863_9739c93.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 286 | Hilltop Apartment 12 | [massing_house_301842865_7ebc1e1](modular/buildings/massing_house_301842865_7ebc1e1.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 287 | Hilltop Apartment 1 | [massing_house_301842862_fca3f38](modular/buildings/massing_house_301842862_fca3f38.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 288 | Center For Paralysis Research | [massing_house_301832122_743e508](modular/buildings/massing_house_301832122_743e508.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 289 | Hilltop Apartment 21 | [massing_house_1193765873_b32830c](modular/buildings/massing_house_1193765873_b32830c.blend)<br>[massing_house_301842864_7652494](modular/buildings/massing_house_301842864_7652494.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 290 | Bell Tower | [bell_tower](modular/buildings/bell_tower.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 291 | Hilltop Apartment 6 | [massing_house_301842058_085f626](modular/buildings/massing_house_301842058_085f626.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 292 | Max W & Maileen Brown Family Hall | [electrical_engineering](modular/buildings/electrical_engineering.blend)<br>[massing_max_w_maileen_brown_family_hall_of_electrical_engineering_bhee_078fbfb](modular/buildings/massing_max_w_maileen_brown_family_hall_of_electrical_engineering_bhee_078fbfb.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 293 | Flight Operations Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 295 | Hilltop Apartment 22 | [massing_house_301842866_18acd00](modular/buildings/massing_house_301842866_18acd00.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 296 | Utility Plant Office Facility | [massing_utility_plant_office_facility_e219ef5](modular/buildings/massing_utility_plant_office_facility_e219ef5.blend) | Direct FID crosswalk; graded 8.45/10 and integrated in master; see audit/utility_plant_office_facility/master_integration_2026-10-26.json |
| 297 | Laboratory Materials Storage Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 402 | Bill & Sally Hanley Human Development Institute | [massing_house_1072474689_8bfed5e](modular/buildings/massing_house_1072474689_8bfed5e.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 403 | Beta Upsilon Chi | [massing_fairway_cooperative_2101b77](modular/buildings/massing_fairway_cooperative_2101b77.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 404 | Ross-Ade Stadium | [massing_house_1095763312_0b46f63](modular/buildings/massing_house_1095763312_0b46f63.blend)<br>[massing_house_1095763313_928099c](modular/buildings/massing_house_1095763313_928099c.blend)<br>[ross_ade](modular/buildings/ross_ade.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 405 | Devonshire Coop | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 406 | Agricultural And Biological Engineering | [massing_agricultural_and_biological_engineering_abe_0ebc7b3](modular/buildings/massing_agricultural_and_biological_engineering_abe_0ebc7b3.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 407 | Martin C. Jischke Hall of Biomedical Engineering | [massing_martin_c_jischke_hall_of_biomedical_engineering_1a34d6a](modular/buildings/massing_martin_c_jischke_hall_of_biomedical_engineering_1a34d6a.blend) | Direct FID 407 verified; generalized outline maximum deviation 1.011 m; 8.0/10 pass; awaiting master integration |
| 408 | David and Bonnie Brunner Farm Animal Hospital | [massing_david_and_bonnie_brunner_farm_animal_hospital_dada82b](modular/buildings/massing_david_and_bonnie_brunner_farm_animal_hospital_dada82b.blend)<br>[massing_house_938230644_776d050](modular/buildings/massing_house_938230644_776d050.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 409 | Frieda Parker Residence Hall | [frieda_parker_hall](modular/buildings/frieda_parker_hall.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 410 | Virginia C. Meredith Residence Hall South | [massing_meredith_hall_south_ffbc444](modular/buildings/massing_meredith_hall_south_ffbc444.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 411 | Ralph and Bettye Bailey Hall | [massing_ralph_bettye_bailey_hall_406c4db](modular/buildings/massing_ralph_bettye_bailey_hall_406c4db.blend) | Finished; exact 22-vertex FID 411 shell, independent grade 8.1/10, master fresh-open PASS; alternate legacy candidates remain separate reconciliation work |
| 413 | Hangar No. 6 Addition | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 414 | Lambert Green Dining | [massing_circle_k_fa39c23](modular/buildings/massing_circle_k_fa39c23.blend)<br>[massing_house_1034040095_378b714](modular/buildings/massing_house_1034040095_378b714.blend)<br>[massing_house_1034040098_68f2f90](modular/buildings/massing_house_1034040098_68f2f90.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+3 more candidates) |
| 430 | Marc and Sharon Hagle Hall | [massing_marc_and_sharon_hagle_hall_hagl_071ffd6](modular/buildings/massing_marc_and_sharon_hagle_hall_hagl_071ffd6.blend) | Direct FID 430 verified; 8.5/10 pass; canopy extends beyond GIS wall outline; awaiting master integration |
| 431 | Bob & Trudy Marching Band Complex | [massing_hull_all_american_marching_band_complex_665bcb7](modular/buildings/massing_hull_all_american_marching_band_complex_665bcb7.blend) | Integrated detailed asset; independent grade 8.4/10; master fresh-open PASS; height/facade remain estimated |
| 432 | Dudley Hall | [massing_house_860822250_df21db0](modular/buildings/massing_house_860822250_df21db0.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 433 | Lambertus Hall | [lambertus_hall](modular/buildings/lambertus_hall.blend) | Detailed asset independently graded 8.0/10; FID 433 footprint matched; master fresh-open integration PASS; five-level height/facade attribution partly estimated |
| 434 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 435 | David and Bonnie Brunner Equine Hospital | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 436 | David and Bonnie Brunner Small Animal Hospital | [massing_house_1106726513_3842fee](modular/buildings/massing_house_1106726513_3842fee.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 445 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 446 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 447 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 448 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 449 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 450 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 451 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 452 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 453 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 454 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 455 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 468 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 469 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 470 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 471 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 472 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 473 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 474 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 475 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 476 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 477 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 478 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 479 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 480 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 481 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 482 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 484 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 485 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 486 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 487 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 488 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 489 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 490 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 491 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 492 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 493 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 494 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 495 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 496 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 497 | (unnamed official map feature) | [massing_house_1261877810_b142449](modular/buildings/massing_house_1261877810_b142449.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 498 | (unnamed official map feature) | [massing_house_1319324779_4f702c9](modular/buildings/massing_house_1319324779_4f702c9.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 499 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 500 | (unnamed official map feature) | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 501 | Building E | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 502 | Building D | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 503 | Building C | [massing_provenance_apartments_d913384](modular/buildings/massing_provenance_apartments_d913384.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 504 | Building B | [massing_provenance_apartments_001_1b3223b](modular/buildings/massing_provenance_apartments_001_1b3223b.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 505 | Building A | [massing_provenance_apartments_002_a9a7f4a](modular/buildings/massing_provenance_apartments_002_a9a7f4a.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 506 | Building F | [massing_provenance_apartments_005_960f6b0](modular/buildings/massing_provenance_apartments_005_960f6b0.blend) | County C1.4 labels Building F / 143; independently graded 8.3/10; awaiting master integration (see TODO.md); GIS is pre-planning/roof-level, not a surveyed wall line |
| 507 | Building G | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 508 | Building I | [massing_provenance_apartments_003_682c8e8](modular/buildings/massing_provenance_apartments_003_682c8e8.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 509 | Building H | [massing_provenance_apartments_004_1bc10e3](modular/buildings/massing_provenance_apartments_004_1bc10e3.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 516 | Aspire at Discovery Park Building B | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 517 | Aspire at Discovery Park Building C | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 518 | Aspire at Discovery Park Building C | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 519 | Aspire at Discovery Park Building C | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 524 | Purdue Village Administration Building | [massing_purdue_village_administration_building_3faae6c](modular/buildings/massing_purdue_village_administration_building_3faae6c.blend) | Independently graded 8.5/10; 14-vertex FID 524 footprint and archived facade photo documented; awaiting master integration (see TODO.md); height and facade bearing remain uncertain |
| 526 | Purdue Graduate Student Center | [massing_purdue_graduate_student_center_af9c5c7](modular/buildings/massing_purdue_graduate_student_center_af9c5c7.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 527 | Amelia Earhart Terminal | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 528 | South Hall | [massing_house_1558636642_742e366](modular/buildings/massing_house_1558636642_742e366.blend)<br>[south_hall](modular/buildings/south_hall.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 529 | Tee-hangar No. 1 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 530 | Aspire at Discovery Park Building A | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 531 | Aspire at Discovery Park Building A | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 532 | Aspire at Discovery Park Building A | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 540 | 410 STEELY ST | [massing_house_301832482_f46c376](modular/buildings/massing_house_301832482_f46c376.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 541 | 333 S GRANT ST | [massing_house_301832484_66da771](modular/buildings/massing_house_301832484_66da771.blend)<br>[massing_house_301832489_dafe945](modular/buildings/massing_house_301832489_dafe945.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 542 | WALDRON 19 | [massing_house_301838782_35890d9](modular/buildings/massing_house_301838782_35890d9.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 543 | Continuum Discovery Park | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 544 | Lees-Such Tower | [massing_honors_college_and_residences_north_3de3b7c](modular/buildings/massing_honors_college_and_residences_north_3de3b7c.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 545 | New Pete Dye Clubhouse | [massing_the_pete_dye_clubhouse_a3a9641](modular/buildings/massing_the_pete_dye_clubhouse_a3a9641.blend) | Independently graded 8.5/10; matches the new clubhouse OSM footprint; legacy FID 233 is the distinct 1998 clubhouse; awaiting master integration (see TODO.md); height and facade remain estimated |
| 546 | Darr-Chaney Hall of Pharmacy and Dauch Hall of Nursing | [massing_house_1558638276_ff1ad9e](modular/buildings/massing_house_1558638276_ff1ad9e.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 547 | Third and West | [massing_3rd_and_west_ffa3d05](modular/buildings/massing_3rd_and_west_ffa3d05.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 548 | Daniels School of Business | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 549 | Ross-Ade Dining | [massing_house_1087563877_79ceae1](modular/buildings/massing_house_1087563877_79ceae1.blend)<br>[massing_house_1095763309_5a378e2](modular/buildings/massing_house_1095763309_5a378e2.blend)<br>[massing_house_1095763310_0819a80](modular/buildings/massing_house_1095763310_0819a80.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+1 more candidates) |
| 550 | Northwestern Avenue Parking Garage | [massing_house_1089873412_fa01af5](modular/buildings/massing_house_1089873412_fa01af5.blend)<br>[massing_house_301932790_1daa02a](modular/buildings/massing_house_301932790_1daa02a.blend)<br>[massing_house_607137011_7fa2854](modular/buildings/massing_house_607137011_7fa2854.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+4 more candidates) |
| 575 | Walter W. Wade Utility Plant | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 576 | Utility Plant Office Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 577 | Ash Vac Pump Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 578 | Utility Plant Storage Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 581 | Lilly Hall of Life Sciences | [massing_lilly_hall_e7fc13e](modular/buildings/massing_lilly_hall_e7fc13e.blend) | Finished; independently graded 8.0/10; see finished table |
| 604 | Birck Nanotechnology Center | [massing_birck_nanotechnology_center_362d0b7](modular/buildings/massing_birck_nanotechnology_center_362d0b7.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 605 | Bindley Bioscience Center | [massing_bindley_bioscience_center_641f939](modular/buildings/massing_bindley_bioscience_center_641f939.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 606 | Robert E. Heine Pharmacy Building | [massing_heine_pharmacy_rhph_2f36735](modular/buildings/massing_heine_pharmacy_rhph_2f36735.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 607 | Harriet O. & James M. Fowler Jr. Memorial House | [massing_fowler_memorial_house_9970560](modular/buildings/massing_fowler_memorial_house_9970560.blend)<br>[massing_house_1095783106_b3c63f4](modular/buildings/massing_house_1095783106_b3c63f4.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 608 | Coal Hopper | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 609 | Purdue Coal Handling Facility | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 610 | Conveyer Tunnel | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 611 | FAA Tower | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 615 | Westwood Manor Garage | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 616 | Westwood Manor | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 617 | Edward C. Elliott Hall of Music | [elliott_hall_of_music](modular/buildings/elliott_hall_of_music.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 618 | Frederick L. Hovde Hall of Administration | [hovde_hall](modular/buildings/hovde_hall.blend)<br>[massing_house_1033674920_dcd3b76](modular/buildings/massing_house_1033674920_dcd3b76.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 619 | Intercollegiate Athletic Sports Turf Building | [massing_house_1326355762_a7d46fc](modular/buildings/massing_house_1326355762_a7d46fc.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 635 | Gerald D. and Edna E. Mann Hall | [massing_mann_hall_2b4ebda](modular/buildings/massing_mann_hall_2b4ebda.blend) | Finished; independently graded 8.2/10; see finished table |
| 636 | Materials Management & Distribution Center | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 637 | Surplus Operations Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 638 | Franklin Levering Cary Quadrangle (NE) | [massing_cary_quadrangle_northeast_cqne_0a76fca](modular/buildings/massing_cary_quadrangle_northeast_cqne_0a76fca.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 639 | Franklin Levering Cary Quadrangle (East) | [massing_cary_quadrangle_east_cqe_230c813](modular/buildings/massing_cary_quadrangle_east_cqe_230c813.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 641 | Charles J. Lynn Hall of Veterinary Medicine | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 642 | Neil Armstrong Hall of Engineering | [neil_armstrong_hall](modular/buildings/neil_armstrong_hall.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 643 | McCutcheon Drive Parking Garage | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 644 | Purdue Memorial Union | [purdue_memorial_union](modular/buildings/purdue_memorial_union.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 645 | Black Cultural Center | [massing_black_cultural_center_bcc_e2b2544](modular/buildings/massing_black_cultural_center_bcc_e2b2544.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 646 | Materials And Electrical Engineering | [massing_materials_science_and_electrical_engineering_msee_003a4e2](modular/buildings/massing_materials_science_and_electrical_engineering_msee_003a4e2.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 647 | Franklin Levering Cary Quadrangle (NW) | [massing_cary_quadrangle_northwest_cqnw_e8a861e](modular/buildings/massing_cary_quadrangle_northwest_cqnw_e8a861e.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 649 | Wiley Dinning Court | [massing_wiley_dining_court_wdct_8a6c669](modular/buildings/massing_wiley_dining_court_wdct_8a6c669.blend) | Finished; 0.9959 GIS footprint IoU, independent grade 8.0/10, master fresh-open PASS; facade-height and interior limits documented |
| 651 | First Street Towers Eastern | [massing_first_street_towers_east_fste_c9b22d3](modular/buildings/massing_first_street_towers_east_fste_c9b22d3.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 653 | Franklin Levering Cary Quadrangle (South) | [massing_cary_quadrangle_south_cqs_7ee2283](modular/buildings/massing_cary_quadrangle_south_cqs_7ee2283.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 655 | Pesticide Applicator Training Facility | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 656 | Ross-Ade Stadium 2 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 657 | Ross-Ade Stadium 1 | [massing_house_1122575972_943bd44](modular/buildings/massing_house_1122575972_943bd44.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 658 | Ross-Ade Stadium 4 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 659 | Ross-Ade Stadium 3 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 660 | Airport Storage Building No. 1 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 661 | Harvey W. Wiley Residence Hall | [wiley_hall](modular/buildings/wiley_hall.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 662 | Newton Booth Tarkington Residence Hall | [tarkington_hall](modular/buildings/tarkington_hall.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 663 | Purdue Memorial Union Club | [massing_union_club_hotel_0d22460](modular/buildings/massing_union_club_hotel_0d22460.blend) | Independently graded 8.1/10; all 53 GIS shell vertices match within 0.000019 m; awaiting master integration (see TODO.md); roof heights, floor spacing, and facade proportions remain estimated |
| 664 | First Street Towers Central | [massing_first_street_towers_central_fstc_929924d](modular/buildings/massing_first_street_towers_central_fstc_929924d.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 667 | Schowe House | [massing_house_1096999537_7fd4916](modular/buildings/massing_house_1096999537_7fd4916.blend)<br>[massing_house_1096999538_459c2d6](modular/buildings/massing_house_1096999538_459c2d6.blend)<br>[massing_house_1096999539_fee06bc](modular/buildings/massing_house_1096999539_fee06bc.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+2 more candidates) |
| 668 | Coal Handling Control/Fire Pump Bldg | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 669 | Hockmeyer Hall of Structural Biology | [massing_hockmeyer_hall_of_structural_biology_hock_4d524ab](modular/buildings/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 670 | Hall for Discovery and Learning Research | [massing_hall_for_discovery_and_learning_research_dlr_ed8395e](modular/buildings/massing_hall_for_discovery_and_learning_research_dlr_ed8395e.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 707 | 1580 W State Street | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 710 | P143 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 711 | Purdue West - Building C | [massing_house_256639576_9afc35e](modular/buildings/massing_house_256639576_9afc35e.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 712 | 523 Russell Street | [massing_house_301840866_8242fa6](modular/buildings/massing_house_301840866_8242fa6.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 713 | 525 Russell Street | [massing_house_301840865_cbf7de2](modular/buildings/massing_house_301840865_cbf7de2.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 714 | 412R | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 715 | Garage for 600 Russell Street | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 716 | Garage for 412 Russell | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 717 | Garage for 425 Waldron | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 718 | 1007F | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 719 | 425W | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 720 | 122W | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 721 | 130W | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 722 | Garage for 915 W 5th street | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 723 | Garage for 426 Waldron | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 724 | Garage for 903 W 5th street | [massing_house_888437579_110cebc](modular/buildings/massing_house_888437579_110cebc.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 728 | 256 MARSTELLAR ST | [massing_house_302407523_e1fc7f2](modular/buildings/massing_house_302407523_e1fc7f2.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 729 | 530 HARRISON ST | [massing_house_302407525_522f858](modular/buildings/massing_house_302407525_522f858.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 730 | 231 SHEETZ ST | [massing_house_1088706537_899763d](modular/buildings/massing_house_1088706537_899763d.blend)<br>[massing_house_301831860_bd9412f](modular/buildings/massing_house_301831860_bd9412f.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 731 | 215 SHEETZ ST | [massing_house_301831859_8845fdc](modular/buildings/massing_house_301831859_8845fdc.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 732 | 241/253 SHEETZ ST | [massing_house_301831858_2cb1dfc](modular/buildings/massing_house_301831858_2cb1dfc.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 733 | 442 STEELY ST | [massing_house_1149668149_0f39a3a](modular/buildings/massing_house_1149668149_0f39a3a.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 734 | 442 STEELY ST GARAGE | [massing_house_301832485_097683c](modular/buildings/massing_house_301832485_097683c.blend)<br>[massing_house_301832486_1ae6b17](modular/buildings/massing_house_301832486_1ae6b17.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 735 | 432 STEELY ST GARAGE | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 736 | 432 STEELY ST | [massing_house_1149668150_e7159f0](modular/buildings/massing_house_1149668150_e7159f0.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 737 | 422 STEELY ST GARAGE | [massing_house_301832487_1a9bf56](modular/buildings/massing_house_301832487_1a9bf56.blend)<br>[massing_house_301832488_7ce7933](modular/buildings/massing_house_301832488_7ce7933.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 738 | 422 STEELY ST | [massing_house_1149668151_51fa035](modular/buildings/massing_house_1149668151_51fa035.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 739 | 155-157 PIERCE ST | [massing_campus_edge_343e3d8](modular/buildings/massing_campus_edge_343e3d8.blend)<br>[massing_house_302408071_c1699d0](modular/buildings/massing_house_302408071_c1699d0.blend)<br>[massing_house_970455231_4f1810c](modular/buildings/massing_house_970455231_4f1810c.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+4 more candidates) |
| 740 | Purdue West - Building B | [massing_house_283526730_8a84f50](modular/buildings/massing_house_283526730_8a84f50.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 741 | Purdue West - Building D | [massing_house_283526729_9075050](modular/buildings/massing_house_283526729_9075050.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 743 | Latino Cultural Center (former 2006–2017 site) | [massing_latino_cultural_center_5f0d139](modular/buildings/massing_latino_cultural_center_5f0d139.blend) | Historical feature only: former building demolished; 600 N Russell parcel now incorporated into Phi Gamma Delta property/parking reconfiguration. Excluded from current master; see audit/latino_cultural_center_5f0d139/identity_review.md |
| 744 | Phi Sigma Rho | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 746 | na | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 747 | 252-254 MARSTELLAR ST | [massing_house_302407517_95bad8f](modular/buildings/massing_house_302407517_95bad8f.blend)<br>[massing_house_302407520_3c52fd4](modular/buildings/massing_house_302407520_3c52fd4.blend)<br>[massing_house_302407521_340fbd2](modular/buildings/massing_house_302407521_340fbd2.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+1 more candidates) |
| 748 | Zeta Psi / Chi Psi address conflict | [massing_house_301841600_c1351aa](modular/buildings/massing_house_301841600_c1351aa.blend) | Spatial match at 950 David Ross; Zeta Psi and Chi Psi primary sources both claim the address; exclusive occupancy unresolved (see audit/zeta_psi/crosswalk_resolution.md) |
| 749 | 818 Northwestern Avenue | [massing_house_1089875804_27ad64c](modular/buildings/massing_house_1089875804_27ad64c.blend)<br>[massing_house_1089875806_71bd68b](modular/buildings/massing_house_1089875806_71bd68b.blend)<br>[massing_house_1089875813_c6129f5](modular/buildings/massing_house_1089875813_c6129f5.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+6 more candidates) |
| 750 | 224 SHEETZ ST | [massing_house_301831861_e126d5c](modular/buildings/massing_house_301831861_e126d5c.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 751 | Delta Upsilon | [massing_house_301841256_1cc7641](modular/buildings/massing_house_301841256_1cc7641.blend) | Exact GIS match; independently graded 8.4/10; master fresh-open PASS |
| 752 | Delta Zeta | [massing_crosswalk_commons_7c01ecd](modular/buildings/massing_crosswalk_commons_7c01ecd.blend)<br>[massing_house_301841601_7ae6159](modular/buildings/massing_house_301841601_7ae6159.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 753 | Delta Delta Delta | [massing_house_301841333_affe21e](modular/buildings/massing_house_301841333_affe21e.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 754 | Chi Phi | [massing_house_301841605_8eef95d](modular/buildings/massing_house_301841605_8eef95d.blend)<br>[alpha_epsilon_pi](modular/buildings/alpha_epsilon_pi.blend) | FID 754 address/roof is used for current AEPi listing; GIS still says Chi Phi. AEPi graded 8.25/10 and integrated; prior massing superseded to prevent duplication; current occupancy conflict remains documented |
| 755 | Evans Scholars | [massing_house_301841610_b6ad6ed](modular/buildings/massing_house_301841610_b6ad6ed.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 756 | Alpha Omicron Pi | [massing_house_301841607_63d85b5](modular/buildings/massing_house_301841607_63d85b5.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 757 | Alpha Gamma Delta | [massing_house_301841608_d56a4c4](modular/buildings/massing_house_301841608_d56a4c4.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 758 | Sigma Nu | [massing_house_301841330_f58ae87](modular/buildings/massing_house_301841330_f58ae87.blend) | Confirmed FID 758 and parcel identity; independently graded 8.0/10; awaiting master integration; GIS ring matches within 0.000038 m |
| 759 | Gamma Phi Beta | [massing_house_301841329_bed5cb6](modular/buildings/massing_house_301841329_bed5cb6.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 760 | Theta Chi | [massing_house_301841328_39f169f](modular/buildings/massing_house_301841328_39f169f.blend) | Named FID 760 / 800 David Ross identity verified; independently graded 8.5/10; awaiting master integration; source ring matches within 0.000049 m |
| 761 | Circle Pines | [massing_house_301841609_c6c9ac4](modular/buildings/massing_house_301841609_c6c9ac4.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 762 | Zeta Beta Tau (current sources) / Phi Kappa Theta (historic GIS label) | [massing_house_301841332_9b3bd1f](modular/buildings/massing_house_301841332_9b3bd1f.blend) is independently graded 8.5/10; [massing_house_301841334_fa7e5a2](modular/buildings/massing_house_301841334_fa7e5a2.blend) remains a separate nearby candidate outside this assignment | One GIS feature at 900 David Ross; current ZBT identity is source-supported; the stable FID 762 asset now matches the transformed roof ring within 0.000043 m; Phi Kappa Theta's current site remains unresolved. See audit/zeta_beta_tau/crosswalk_resolution.md
| 763 | Alpha Sigma Phi | [massing_house_301841603_654031c](modular/buildings/massing_house_301841603_654031c.blend) | Integrated detailed asset; independent grade 8.2/10; master fresh-open PASS; story count/facade details remain uncertain |
| 764 | Alpha Phi | [massing_house_301841331_735e92f](modular/buildings/massing_house_301841331_735e92f.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 765 | Alpha Chi Omega | [massing_house_301841602_8190d79](modular/buildings/massing_house_301841602_8190d79.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 766 | Twin Pines | [massing_twin_pines_cooperative_8f606f9](modular/buildings/massing_twin_pines_cooperative_8f606f9.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 767 | Phi Sigma Kappa | [massing_house_301934833_f6640d1](modular/buildings/massing_house_301934833_f6640d1.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 768 | SO115 | [massing_house_1035795838_d0eb5ac](modular/buildings/massing_house_1035795838_d0eb5ac.blend)<br>[massing_house_301921256_ccfad26](modular/buildings/massing_house_301921256_ccfad26.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 769 | Baptist Student Foundation | [massing_baptist_student_foundation_c3d8114](modular/buildings/massing_baptist_student_foundation_c3d8114.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 770 | Christian Campus House | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 771 | Muslim Student Association | [massing_house_1089328580_bcd08c0](modular/buildings/massing_house_1089328580_bcd08c0.blend)<br>[massing_islamic_societyof_greater_lafayette_0130012](modular/buildings/massing_islamic_societyof_greater_lafayette_0130012.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 772 | Phi Mu | [massing_house_301836574_fff1661](modular/buildings/massing_house_301836574_fff1661.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 773 | Zeta Tau Alpha | [massing_zeta_tau_alpha_af8a443](modular/buildings/zeta_tau_alpha.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 774 | Pi Beta Phi | [massing_house_301838781_891384f](modular/buildings/massing_house_301838781_891384f.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 775 | Alpha Chi Rho | [massing_alpha_chi_rho_0cb591a](modular/buildings/massing_alpha_chi_rho_0cb591a.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 776 | Sigma Pi | [massing_house_301836568_0fbca0e](modular/buildings/massing_house_301836568_0fbca0e.blend) | Named FID 776 / 130 N Russell identity verified; R5 independently graded 8.1/10; awaiting master integration; GIS ring max error 0.000017 m; height/story remain estimates |
| 777 | Triangle | [massing_triangle_fraternity_8477ad9](modular/buildings/massing_triangle_fraternity_8477ad9.blend) | FID 777 / SOTRI at 103 University St; 20-point GIS shell matches within 0.000014 m; independent 2018 IndianaMap outline has 0.856 IoU; independently graded 8.0/10; awaiting master integration |
| 778 | Farmhouse | [massing_farmhouse_fraternity_purdue_chapter_0b8908b](modular/buildings/massing_farmhouse_fraternity_purdue_chapter_0b8908b.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 779 | Lds Institute of Religion | [massing_the_church_of_jesus_christ_of_latter_day_saints_6f2a451](modular/buildings/massing_the_church_of_jesus_christ_of_latter_day_saints_6f2a451.blend) | Official 14 Waldron identity and GIS wall ring verified; independently graded 8.3/10; awaiting master integration (see TODO.md); roof heights and facade stationing remain estimated |
| 780 | Sigma Kappa | [massing_house_301840869_1b80ace](modular/buildings/massing_house_301840869_1b80ace.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 781 | Chi Omega | [massing_chi_omega_a9eb08d](modular/buildings/massing_chi_omega_a9eb08d.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 782 | Kappa Kappa Gamma | [massing_house_301840871_5d1bc06](modular/buildings/massing_house_301840871_5d1bc06.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 783 | Delta Gamma | [massing_house_301840872_582df9d](modular/buildings/massing_house_301840872_582df9d.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 784 | Alpha Kappa Lambda | [massing_alpha_kappa_lambda_88dda6c](modular/buildings/massing_alpha_kappa_lambda_88dda6c.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 785 | Alpha Tau Omega | [massing_house_301840870_c45a5f4](modular/buildings/massing_house_301840870_c45a5f4.blend) | Campus-world source linked in master; independent grade 8.5/10; structural footprint IoU 0.942; historic tower/roof details remain estimated |
| 786 | Kappa Alpha Theta | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 787 | Phi Gamma Delta | [massing_house_301837281_58ead22](modular/buildings/massing_house_301837281_58ead22.blend) | Current fraternity site; 600 N Russell former LCC parcel was added to the unified property and Lyles Addition/parking reconfiguration (see audit/latino_cultural_center_5f0d139/identity_review.md) |
| 788 | Alpha Xi Delta | [massing_house_301841248_fe939c7](modular/buildings/massing_house_301841248_fe939c7.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 789 | Sigma Phi Epsilon | [massing_house_301841250_d63b09a](modular/buildings/massing_house_301841250_d63b09a.blend) | Named chapter sources and OSM way 301841250 confirmed; independently graded 8.65/10; awaiting integration; shell matches within 0.000021 m |
| 790 | Pi Kappa Alpha | [massing_house_301841252_e4f8f05](modular/buildings/massing_house_301841252_e4f8f05.blend) | Named FID 790 / Beta Phi chapter identity confirmed; independently graded 8.7/10; awaiting integration; shell matches within 0.000017 m |
| 791 | Acacia | [massing_house_301841251_8a9a05b](modular/buildings/massing_house_301841251_8a9a05b.blend) | Finished; 8.35/10 independent grade and master integration PASS; see audit/acacia/ |
| 792 | Alpha Gamma Rho | [massing_house_301841253_f0b3be3](modular/buildings/massing_house_301841253_f0b3be3.blend) | Purdue FID 792 remains a spatial candidate; independently graded 8.4/10 and integrated through a placement marker. OSM footprint is community mapped; campus registration remains unverified |
| 793 | Beta Sigma Psi | [massing_house_301841254_29ab02d](modular/buildings/massing_house_301841254_29ab02d.blend) | Direct Purdue GIS FID 793 asset; independently graded 9.0/10 in master and integrated through its placement marker. Shape__Area/Length attributes conflict with polygon vertices; floor count conflicts with current Street View |
| 794 | Glenwood | [massing_house_301841249_f827941](modular/buildings/massing_house_301841249_f827941.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 795 | Sigma Alpha | [massing_house_970455228_6d2e64a](modular/buildings/massing_house_970455228_6d2e64a.blend)<br>[massing_house_970455234_bfc586d](modular/buildings/massing_house_970455234_bfc586d.blend)<br>[massing_house_970455236_6e54930](modular/buildings/massing_house_970455236_6e54930.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+6 more candidates) |
| 796 | Phi Delta Theta | [massing_phi_delta_theta_258cddd](modular/buildings/massing_phi_delta_theta_258cddd.blend) | Official FID 796 / SOFDH identity and 30-point ring verified; independently graded 8.3/10; awaiting master integration; heights and roof dimensions remain estimated |
| 797 | University Church | [massing_university_church_84b2a1b](modular/buildings/massing_university_church_84b2a1b.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 798 | Delta Sigma Phi | [massing_house_860826641_2c90f97](modular/buildings/massing_house_860826641_2c90f97.blend) | Exact GIS match, detailed model independently graded 8.3/10; adjacent candidate 860826640 is not this building |
| 799 | Pi Kappa Phi | [massing_pi_kappa_phi_50e4645](modular/buildings/massing_pi_kappa_phi_50e4645.blend) | Named FID 799 / Omega chapter house confirmed; independently graded 8.4/10; awaiting master integration; proposed replacement permit status unverified |
| 800 | Shoemaker | [massing_house_1497291146_031c06e](modular/buildings/massing_house_1497291146_031c06e.blend)<br>[massing_house_1497291147_0af41bc](modular/buildings/massing_house_1497291147_0af41bc.blend)<br>[massing_house_860903232_2890c53](modular/buildings/massing_house_860903232_2890c53.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+1 more candidates) |
| 801 | Kappa Delta Rho | [massing_house_1089876362_14ecd2c](modular/buildings/massing_house_1089876362_14ecd2c.blend) | Direct Purdue FID crosswalk; 20 GIS ring vertices match within 0.000057 m; exact-SHA independent grade 8.4/10; integrated and fresh-open verified |
| 802 | Stewart | [massing_fuse_39cf4b5](modular/buildings/massing_fuse_39cf4b5.blend)<br>[massing_house_1089875805_7e35374](modular/buildings/massing_house_1089875805_7e35374.blend)<br>[massing_house_1089875807_2bd9d47](modular/buildings/massing_house_1089875807_2bd9d47.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+5 more candidates) |
| 803 | Hillel Foundation | [massing_hillel_36d2ba1](modular/buildings/massing_hillel_36d2ba1.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 804 | Kappa Sigma | [massing_house_301838017_9e20680](modular/buildings/massing_house_301838017_9e20680.blend)<br>[massing_house_301838020_d902112](modular/buildings/massing_house_301838020_d902112.blend)<br>[massing_house_671108497_7c12a3a](modular/buildings/massing_house_671108497_7c12a3a.blend) | Direct FID crosswalk; graded 8.5/10 and integrated in master; see audit/massing_kappa_sigma_c1b36ec/independent_grade/result.json |
| 805 | Chauncey | [massing_house_1149668160_21c8b31](modular/buildings/massing_house_1149668160_21c8b31.blend)<br>[massing_house_860808220_b0ead89](modular/buildings/massing_house_860808220_b0ead89.blend)<br>[massing_house_970455229_ac730ab](modular/buildings/massing_house_970455229_ac730ab.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+9 more candidates) |
| 820 | Historic Theta Tau / current Phi Kappa Tau | [massing_phi_kappa_tau_139b9d7](modular/buildings/massing_phi_kappa_tau_139b9d7.blend)<br>[massing_house_970736968_fa1edef](modular/buildings/massing_house_970736968_fa1edef.blend)<br>[massing_house_970737027_6544e29](modular/buildings/massing_house_970737027_6544e29.blend) | Current Phi Kappa Tau at 416 N Chauncey is supported by its chapter House page and alumni house-transition history; corrected massing independently graded 8.3/10, awaiting integration |
| 821 | Alpha Epsilon Pi | — | Legacy/alternate GIS label at 116 Fowler is not used for the current 1051 David Ross address model; reconcile whether this is a separate in-scope facility or a stale map label. See audit/alpha_epsilon_pi/evidence.md |
| 822 | Maclure | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 823 | Fairway | [massing_house_1497291148_3e4e79b](modular/buildings/massing_house_1497291148_3e4e79b.blend)<br>[massing_house_860901801_babb527](modular/buildings/massing_house_860901801_babb527.blend)<br>[massing_house_860901803_330065b](modular/buildings/massing_house_860901803_330065b.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+3 more candidates) |
| 824 | Ann Tweedale | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 825 | Gemini | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 826 | Beta Theta Pi | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 827 | Marwood | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 828 | Sigma Chi | [massing_sigma_chi_fid828](modular/buildings/massing_sigma_chi_fid828.blend) | Current Delta Delta chapter house at 202 Littleton matched to FID 828; independent grade 8.25/10 pass; awaiting master integration; height, floor count and facade detail remain uncertain |
| 829 | Phi Kappa Sigma | [massing_phi_kappa_sigma_fid829](modular/buildings/massing_phi_kappa_sigma_fid829.blend) | Direct Purdue FID crosswalk; 13 GIS ring vertices match within 0.000024 m; exact-SHA independent grade 8.55/10; integrated and fresh-open verified |
| 835 | Baptist Collegiate Ministry | [massing_house_301841246_ab0aa75](modular/buildings/massing_house_301841246_ab0aa75.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 836 | 621W | [massing_house_301837282_cfcd365](modular/buildings/massing_house_301837282_cfcd365.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 837 | 506W | [massing_house_301934127_d64990c](modular/buildings/massing_house_301934127_d64990c.blend)<br>[massing_house_301934128_95df24c](modular/buildings/massing_house_301934128_95df24c.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 838 | 318W | [massing_house_301934834_362a2ed](modular/buildings/massing_house_301934834_362a2ed.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 839 | 219W | [massing_house_301836571_50b7700](modular/buildings/massing_house_301836571_50b7700.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 840 | 221W | [massing_house_301836572_9834d6c](modular/buildings/massing_house_301836572_9834d6c.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 841 | Pi Beta Phi | [massing_house_301921259_e784bea](modular/buildings/massing_house_301921259_e784bea.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 842 | 27W | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 843 | 24R | [massing_house_301921260_4bea287](modular/buildings/massing_house_301921260_4bea287.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 844 | 115W | [massing_house_301921257_b7eb626](modular/buildings/massing_house_301921257_b7eb626.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 845 | Baptist Student Foundation | [massing_house_301934830_7cb26ae](modular/buildings/massing_house_301934830_7cb26ae.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 846 | SODC | [massing_house_301840867_1cab527](modular/buildings/massing_house_301840867_1cab527.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 849 | Sigma Alpha Epsilon | [massing_sigma_alpha_epsilon_fid849](modular/buildings/massing_sigma_alpha_epsilon_fid849.blend) | FID/name/address reconciled to 406 Littleton and county parcel; independently graded 8.0/10; awaiting master integration; roof and height estimated |
| 850 | Levee Plaza | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 852 | St. Thomas Aquinas Center | [massing_st_thomas_aquinas_5535390](modular/buildings/massing_st_thomas_aquinas_5535390.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 855 | Old Purdue Exponent Building | [massing_house_301932783_497fc8a](modular/buildings/massing_house_301932783_497fc8a.blend)<br>[massing_house_301932785_141a3c3](modular/buildings/massing_house_301932785_141a3c3.blend)<br>[massing_house_301932786_5e0e793](modular/buildings/massing_house_301932786_5e0e793.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+6 more candidates) |
| 856 | GIS-labeled Phi Kappa Tau; current-address candidate Phi Kappa Psi | [massing_house_301841257_c23233c](modular/buildings/massing_house_301841257_c23233c.blend) | GIS address 1307 Tower Dr is corroborated by the official Phi Kappa Psi contact page; the chapter assignment and existing asset still need owner/crosswalk confirmation. See audit/phi_kappa_tau/crosswalk_findings.md |
| 857 | Mechanical Engineering Building | [massing_mechanical_engineering_me_8940174](modular/buildings/massing_mechanical_engineering_me_8940174.blend)<br>[mechanical_engineering](modular/buildings/mechanical_engineering.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 858 | First Street Towers, Western | [massing_first_street_towers_west_fstw_b6c3bbe](modular/buildings/massing_first_street_towers_west_fstw_b6c3bbe.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 859 | Grounds Maintenance Greenhouse Facilities | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 860 | Grounds Maintenance Pesticide Storage Facility | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 861 | Bill & Sally Hanley Human Development Institute | [massing_hanley_hall_c8a4551](modular/buildings/massing_hanley_hall_c8a4551.blend)<br>[massing_house_988509816_d9662c5](modular/buildings/massing_house_988509816_d9662c5.blend)<br>[massing_house_988509817_c56a2a6](modular/buildings/massing_house_988509817_c56a2a6.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+1 more candidates) |
| 862 | Marriott Hall | [massing_marriot_hall_7cd3eb5](modular/buildings/massing_marriot_hall_7cd3eb5.blend) | Direct FID 862 verified; 33 source vertices match within 0.000065 m; 8.5/10 pass; awaiting master integration |
| 863 | Turf Recreation Center | [massing_turf_recreation_exercise_center_9622f45](modular/buildings/massing_turf_recreation_exercise_center_9622f45.blend) | Independently graded 8.1/10; named GIS and OSM identity confirmed, but perimeter/area conflicts remain unresolved (see TODO.md) |
| 864 | A. A. Potter Engineering Center | [massing_potter_engineering_center_potr_89c4c33](modular/buildings/massing_potter_engineering_center_potr_89c4c33.blend)<br>[potter_engineering](modular/buildings/potter_engineering.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 865 | Salt Storage | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 866 | Heavy Equipment Storage | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 868 | Well House No. 9 | [massing_house_1034030158_496610b](modular/buildings/massing_house_1034030158_496610b.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 869 | Agricultural Innovation Center | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 870 | Niswonger Aviation Technology Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 873 | Guy J. Mackey Arena | [mackey_arena](modular/buildings/mackey_arena.blend)<br>[massing_house_195521218_d6f2648](modular/buildings/massing_house_195521218_d6f2648.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 877 | Schowe House Garage | [massing_house_1047163466_001_1a3c49f](modular/buildings/massing_house_1047163466_001_1a3c49f.blend)<br>[massing_house_1047163466_86694e1](modular/buildings/massing_house_1047163466_86694e1.blend)<br>[massing_house_1047163467_001_e8f4b99](modular/buildings/massing_house_1047163467_001_e8f4b99.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+3 more candidates) |
| 878 | Herrick Laboratories | [massing_herrick_laboratories_2138103](modular/buildings/massing_herrick_laboratories_2138103.blend)<br>[massing_ray_w_herrick_laboratories_36b11c6](modular/buildings/massing_ray_w_herrick_laboratories_36b11c6.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 879 | Winifred Parker Residence Hall | [winifred_parker_hall](modular/buildings/winifred_parker_hall.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 885 | (unnamed official map feature) | [massing_house_941664819_9c60e13](modular/buildings/massing_house_941664819_9c60e13.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 886 | (unnamed official map feature) | [massing_house_942369305_1f2ca62](modular/buildings/massing_house_942369305_1f2ca62.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 887 | (unnamed official map feature) | [massing_house_1033674918_d029bd0](modular/buildings/massing_house_1033674918_d029bd0.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 888 | (unnamed official map feature) | [massing_house_1033674919_47f34c7](modular/buildings/massing_house_1033674919_47f34c7.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 889 | Hazardous Materials Management Trailer | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 890 | Laboratory Material Storage Trailer | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 891 | Lyles-Porter Hall | [massing_lyles_porter_hall_lyle_604c08e](modular/buildings/massing_lyles_porter_hall_lyle_604c08e.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 892 | Harrison Street Parking Garage | [massing_harrison_street_parking_garage_823c7d2](modular/buildings/massing_harrison_street_parking_garage_823c7d2.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 893 | Drug Discovery Facility | [massing_purdue_drug_discovery_facility_fc72a4a](modular/buildings/massing_purdue_drug_discovery_facility_fc72a4a.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 895 | Seng-Liang Wang Hall | [massing_house_607137017_b536fb7](modular/buildings/massing_house_607137017_b536fb7.blend)<br>[massing_house_607137024_c0e976b](modular/buildings/massing_house_607137024_c0e976b.blend)<br>[massing_house_607137025_d0a05d7](modular/buildings/massing_house_607137025_d0a05d7.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+5 more candidates) |
| 896 | Morgan J. Burke Boilermaker Aquatic Center | [massing_house_936947563_226b58e](modular/buildings/massing_house_936947563_226b58e.blend)<br>[massing_morgan_j_burke_boilermaker_aquatic_center_2e6697f](modular/buildings/massing_morgan_j_burke_boilermaker_aquatic_center_2e6697f.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 897 | France A. Córdova Recreational Sports Center | [massing_france_a_c_rdova_recreational_sports_center_ae69df0](modular/buildings/massing_france_a_c_rdova_recreational_sports_center_ae69df0.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 898 | Radiological & Environ Mgmt Storage Bldg | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 902 | Krach Leadership Center | [massing_krach_leadership_center_krch_debcdf8](modular/buildings/massing_krach_leadership_center_krch_debcdf8.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 904 | (unnamed official map feature) | [massing_house_1088705223_ad6a78b](modular/buildings/massing_house_1088705223_ad6a78b.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 905 | Honors College Residence Hall South | [massing_honors_college_and_residences_south_c663781](modular/buildings/massing_honors_college_and_residences_south_c663781.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 906 | Thomas S. and Harvey D. Wilmeth Active Learning Center | [walc](modular/buildings/walc.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 907 | Well House #2 | [massing_house_936976277_52fabbb](modular/buildings/massing_house_936976277_52fabbb.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 909 | Flex Laboratories | [massing_flex_lab_flex_cc297ea](modular/buildings/massing_flex_lab_flex_cc297ea.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 910 | Land O Lakes Center for Experiential Learning and Purina Pavilion | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 911 | Purdue University Early Care & Education Center | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 912 | Bechtel Innovation Design Center | [massing_bechtel_innovation_design_center_bidc_5488863](modular/buildings/massing_bechtel_innovation_design_center_bidc_5488863.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 914 | Hobart and Russel Creighton Hall of Animal Sciences | [massing_creighton_hall_of_animal_sciences_crtn_a88d450](modular/buildings/massing_creighton_hall_of_animal_sciences_crtn_a88d450.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 915 | Life Science Ranges | [massing_life_science_ranges_greenhouse_and_service_building_c96231f](modular/buildings/massing_life_science_ranges_greenhouse_and_service_building_c96231f.blend)<br>Other spatial candidates: [massing_house_159752239_8e7a81a](modular/buildings/massing_house_159752239_8e7a81a.blend), [massing_house_587549840_07f2e96](modular/buildings/massing_house_587549840_07f2e96.blend) | Current LSR model independently graded 8.1/10 and integrated; FID 915 candidate/GIS IoU 0.8757; other spatial candidates remain unreviewed |
| 916 | Ag Alumni Seed Phenotyping Facility | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 917 | Life Science Plant And Soils Laboratory | [massing_house_587540581_cd4d006](modular/buildings/massing_house_587540581_cd4d006.blend)<br>[massing_life_science_plant_and_soils_laboratory_5963acd](modular/buildings/massing_life_science_plant_and_soils_laboratory_5963acd.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 918 | Purdue Magnetic Resonance Imagin | [massing_mri_modular_facility_mri1_a93e22b](modular/buildings/massing_mri_modular_facility_mri1_a93e22b.blend) | Direct FID 918 verified; four structural edges match within 0.000028 m; 8.0/10 pass; awaiting master integration |
| 925 | Latino Cultural Center at Purdue | [massing_latino_cultural_center_lcc_9cc71b3](modular/buildings/massing_latino_cultural_center_lcc_9cc71b.blend) | Integrated campus asset; independent grade 9.0/10; 12 GIS footprint vertices match within 0.00002 m; height and interior plan remain estimated |
| 926 | Asian American Resource and Cultural Center | [massing_asian_american_and_asian_resource_and_cultural_center_aacc_da08bb2](modular/buildings/massing_asian_american_and_asian_resource_and_cultural_center_aacc_da08bb2.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 927 | Native American Educational and Cultural Center | [massing_native_american_educational_and_cultural_center_nacc_faa0f59](modular/buildings/massing_native_american_educational_and_cultural_center_nacc_faa0f59.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 928 | 440 HARRISON ST | [massing_house_1149668154_e3d2416](modular/buildings/massing_house_1149668154_e3d2416.blend)<br>[massing_house_301836115_31fe152](modular/buildings/massing_house_301836115_31fe152.blend)<br>[massing_house_301836117_14fb0cb](modular/buildings/massing_house_301836117_14fb0cb.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+1 more candidates) |
| 929 | (unnamed official map feature) | [massing_house_970455221_7b8f388](modular/buildings/massing_house_970455221_7b8f388.blend)<br>[massing_house_970455225_f4626b1](modular/buildings/massing_house_970455225_f4626b1.blend)<br>[massing_house_970455248_409f32c](modular/buildings/massing_house_970455248_409f32c.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+5 more candidates) |
| 930 | (unnamed official map feature) | [massing_house_970455222_90fa014](modular/buildings/massing_house_970455222_90fa014.blend)<br>[massing_house_970455233_5143fd8](modular/buildings/massing_house_970455233_5143fd8.blend)<br>[massing_house_970455246_2258fdc](modular/buildings/massing_house_970455246_2258fdc.blend) | Direct FID crosswalk candidate; geometry/grade still require review (+1 more candidates) |
| 932 | Waldron Place II | [massing_house_301836569_223074a](modular/buildings/massing_house_301836569_223074a.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 933 | 414R | [massing_house_301840873_a67ad63](modular/buildings/massing_house_301840873_a67ad63.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 934 | Purdue Student Farm | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 936 | Mollenkopf Athletic Center | [massing_purdue_football_performance_complex_f106c29](modular/buildings/massing_purdue_football_performance_complex_f106c29.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 937 | Kozuch Football Performance Complex | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 939 | Airport Emergency Vehical Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 940 | Gravil Pit Equipment Storage Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 942 | Veterinary Animal Isolation Building 2 | [massing_veterinary_animal_isolation_building_2_ebb4142](modular/buildings/massing_veterinary_animal_isolation_building_2_ebb4142.blend) | Direct FID crosswalk; graded 8.0/10 and integrated in master; see audit/veterinary_animal_isolation_building_2/master_integration_2026-10-26.json |
| 943 | Veterinary Animal Isolation Building 1 | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 944 | Veterinary Pathobiology Research Building | — | No direct FID crosswalk; reconcile to a master asset or create one |
| 945 | Chaney-Hale Hall of Science | [massing_chaney_hale_hall_of_science_chas_6bb9ef7](modular/buildings/massing_chaney_hale_hall_of_science_chas_6bb9ef7.blend) | Direct FID crosswalk candidate; geometry/grade still require review |
| 946 | Convergence | [massing_convergence_center_for_innovation_and_collaboration_conv_ce5226e](modular/buildings/massing_convergence_center_for_innovation_and_collaboration_conv_ce5226e.blend) | Direct FID crosswalk candidate; geometry/grade still require review |

## Adding a building

Follow [AGENT.md](AGENT.md) for the required modular build and grading process.

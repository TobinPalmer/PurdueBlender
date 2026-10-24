"""Register the independently built campus batch in the modular manifest.

Run this from Blender with the campus master open, then run
rebuild_linked_master.py. Asset files remain independently editable libraries.
"""
import bpy
import json
from pathlib import Path

MODULAR = Path(__file__).resolve().parent
PROJECT = MODULAR.parent
MANIFEST_PATH = MODULAR / "manifest.json"

ASSETS = [
    # Five libraries completed before this 25-building batch.
    ("black_cultural_center", "massing_black_cultural_center_bcc_e2b2544", "buildings/black_cultural_center.blend", "Asset_black_cultural_center", [-493.868, 14.068], "audit/black_cultural_center_evidence.json"),
    ("birck_nanotechnology_center", "massing_birck_nanotechnology_center_362d0b7", "buildings/birck_nanotechnology_center.blend", "Asset_birck_nanotechnology_center", [-927.154, -525.430], "audit/birck_nanotechnology_center/evidence.json"),
    ("asian_american_resource_and_cultural_center", "massing_asian_american_and_asian_resource_and_cultural_center_aacc_da08bb2", "buildings/asian_american_resource_and_cultural_center.blend", "Asset_asian_american_resource_and_cultural_center", [-335.25090182338033, 192.38045006796483], "modular/buildings/evidence/aaarcc_evidence.json"),
    ("convergence_center", "massing_convergence_center_for_innovation_and_collaboration_conv_ce5226e", "buildings/convergence_center.blend", "Asset_convergence_center", [-1131.698568664057, -405.52500592356535], "audit/convergence_center_evidence.json"),
    ("lyles_porter_hall", "massing_lyles_porter_hall_lyle_604c08e", "buildings/lyles_porter_hall.blend", "Asset_lyles_porter_hall", [-257.675, -717.457], "audit/lyles_porter_hall/evidence.json"),

    # Batch A: eight source libraries.
    ("agricultural_administration_building", "massing_agricultural_administration_building_120d92c", "buildings/agricultural_administration_building.blend", "Asset_agricultural_administration_building", [-57.69633181530767, -443.67338239975965], "audit/build_batch_a/agricultural_administration_building_evidence.json"),
    ("agricultural_and_biological_engineering_abe", "massing_agricultural_and_biological_engineering_abe_0ebc7b3", "buildings/agricultural_and_biological_engineering_abe.blend", "Asset_agricultural_and_biological_engineering_abe", [-246.71846085020562, -632.8773862787382], "audit/build_batch_a/agricultural_and_biological_engineering_abe_evidence.json"),
    ("animal_disease_diagnostic_laboratory", "massing_animal_disease_diagnostic_laboratory_b934354", "buildings/animal_disease_diagnostic_laboratory.blend", "Asset_animal_disease_diagnostic_laboratory", [-196.3559772433905, -1028.3665309334529], "audit/build_batch_a/animal_disease_diagnostic_laboratory_evidence.json"),
    ("bechtel_innovation_design_center_bidc", "massing_bechtel_innovation_design_center_bidc_5488863", "buildings/bechtel_innovation_design_center_bidc.blend", "Asset_bechtel_innovation_design_center_bidc", [-431.49312776561794, 14.837793060113258], "audit/build_batch_a/bechtel_innovation_design_center_bidc_evidence.json"),
    ("bindley_bioscience_center", "massing_bindley_bioscience_center_641f939", "buildings/bindley_bioscience_center.blend", "Asset_bindley_bioscience_center", [-825.9724870358015, -512.0082823935928], "audit/build_batch_a/bindley_bioscience_center_evidence.json"),
    ("biochemistry_building", "massing_biochemistry_building_a267b8d", "buildings/biochemistry_building.blend", "Asset_biochemistry_building", [-233.02125685161437, -509.4598104037796], "audit/build_batch_a/biochemistry_building_evidence.json"),
    ("david_and_bonnie_brunner_farm_animal_hospital", "massing_david_and_bonnie_brunner_farm_animal_hospital_dada82b", "buildings/david_and_bonnie_brunner_farm_animal_hospital.blend", "Asset_david_and_bonnie_brunner_farm_animal_hospital", [220.99837938145174, -1034.971977165294], "audit/build_batch_a/david_and_bonnie_brunner_farm_animal_hospital_evidence.json"),
    ("dauch_alumni_center", "massing_dauch_alumni_center_3cb1249", "buildings/dauch_alumni_center.blend", "Asset_dauch_alumni_center", [241.19898675231826, -618.1852061961912], "audit/build_batch_a/dauch_alumni_center_evidence.json"),

    # Batch B: eight source libraries.
    ("brees_student_athletic_academic_center", "massing_drew_and_brittany_brees_student_athletic_academic_center_bres_da89033", "buildings/brees_student_athletic_academic_center.blend", "Asset_brees_student_athletic_academic_center", [-243.35271339058767, 745.9921385884661], "audit/batch_b_buildings/brees_student_athletic_academic_center_evidence.json"),
    ("ford_dining_court", "massing_ford_dining_court_71eede4", "buildings/ford_dining_court.blend", "Asset_ford_dining_court", [-503.91569473304673, 523.647572063777], "audit/batch_b_buildings/ford_dining_court_evidence.json"),
    ("flex_lab", "massing_flex_lab_flex_cc297ea", "buildings/flex_lab.blend", "Asset_flex_lab", [-845.379510951895, -650.9923391799532], "audit/batch_b_buildings/flex_lab_evidence.json"),
    ("hall_for_discovery_and_learning_research", "massing_hall_for_discovery_and_learning_research_dlr_ed8395e", "buildings/hall_for_discovery_and_learning_research.blend", "Asset_hall_for_discovery_and_learning_research", [-741.4700609090767, -684.1321541267735], "audit/batch_b_buildings/hall_for_discovery_and_learning_research_evidence.json"),
    ("heine_pharmacy", "massing_heine_pharmacy_rhph_2f36735", "buildings/heine_pharmacy.blend", "Asset_heine_pharmacy", [-193.84218632570293, 259.60496004008974], "audit/batch_b_buildings/heine_pharmacy_evidence.json"),
    ("ray_w_herrick_laboratories", "massing_ray_w_herrick_laboratories_36b11c6", "buildings/ray_w_herrick_laboratories.blend", "Asset_ray_w_herrick_laboratories", [-531.9590659304099, -569.0631943790936], "audit/batch_b_buildings/ray_w_herrick_laboratories_evidence.json"),
    ("horticulture_building", "massing_horticulture_286a904", "buildings/horticulture_building.blend", "Asset_horticulture_building", [-61.82494487966297, -630.9233289999372], "audit/batch_b_buildings/horticulture_building_evidence.json"),
    ("krach_leadership_center", "massing_krach_leadership_center_krch_debcdf8", "buildings/krach_leadership_center.blend", "Asset_krach_leadership_center", [-639.8641814249419, 22.387328434462006], "audit/batch_b_buildings/krach_leadership_center_evidence.json"),

    # Batch C and the two reassigned follow-ups.
    ("lambert_fieldhouse", "massing_lambert_ward_l_fieldhouse_and_gymnasium_1656862", "buildings/lambert_fieldhouse.blend", "Asset_lambert_fieldhouse", [-190.035, 531.692], "audit/batchC_lambert_evidence.json"),
    ("life_science_plant_and_soils_laboratory", "massing_life_science_plant_and_soils_laboratory_5963acd", "buildings/life_science_plant_and_soils_laboratory.blend", "Asset_life_science_plant_and_soils_laboratory", [-426.819, -466.398], "audit/batchC_life_science_plant_soils_evidence.json"),
    ("burton_morgan_center", "massing_morgan_center_for_entrepreneurship_mrgn_9ba681c", "buildings/burton_morgan_center.blend", "Asset_burton_morgan_center", [-775.751, -404.568], "audit/batchC_morgan_center_evidence.json"),
    ("morgan_j_burke_boilermaker_aquatic_center", "massing_morgan_j_burke_boilermaker_aquatic_center_2e6697f", "buildings/morgan_j_burke_boilermaker_aquatic_center.blend", "Asset_morgan_j_burke_boilermaker_aquatic_center", [-808.683, 80.337], "audit/batchC_boilermaker_aquatic_evidence.json"),
    ("national_soil_erosion_laboratory", "massing_national_soil_erosion_laboratory_soil_0a1864c", "buildings/national_soil_erosion_laboratory.blend", "Asset_national_soil_erosion_laboratory", [-548.283, -674.398], "audit/batchC_national_soil_erosion_evidence.json"),
    ("native_american_educational_and_cultural_center_nacc", "massing_native_american_educational_and_cultural_center_nacc_faa0f59", "buildings/native_american_educational_and_cultural_center_nacc.blend", "Asset_native_american_educational_and_cultural_center_nacc", [-278.928, 190.077], "audit/build_nacc/native_american_educational_and_cultural_center_nacc_evidence.json"),
    ("northwest_chiller_plant", "massing_northwest_chiller_plant_nwcp_2b32fa6", "buildings/northwest_chiller_plant.blend", "Asset_northwest_chiller_plant", [-994.953, 200.167], "audit/build_batch_a2/northwest_chiller_plant_evidence.json"),
    ("materials_science_and_electrical_engineering_msee", "massing_materials_science_and_electrical_engineering_msee_003a4e2", "buildings/materials_science_and_electrical_engineering_msee.blend", "Asset_materials_science_and_electrical_engineering_msee", [87.421, 215.992], "audit/build_batch_a2/materials_science_and_electrical_engineering_msee_evidence.json"),
    ("physics_building", "massing_physics_building_phys_3bf42f3", "buildings/physics_building_phys_3bf42f3.blend", "Asset_physics_building", [20.732372, 300.324127], "audit/physics_building/physics_building_evidence.json"),
]

manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
by_id = {asset["id"]: asset for asset in manifest["assets"]}
registered = []
errors = []

for asset_id, old_id, file_rel, collection_name, origin_xy, evidence_rel in ASSETS:
    source_path = (MODULAR / file_rel).resolve()
    evidence_path = (PROJECT / evidence_rel).resolve()
    if not source_path.is_file():
        errors.append(f"missing source library: {source_path}")
        continue
    if not evidence_path.is_file():
        errors.append(f"missing evidence record: {evidence_path}")
        continue
    old = by_id.get(old_id)
    if old is None or old.get("kind") != "massing":
        errors.append(f"missing source massing record: {old_id}")
        continue
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid evidence JSON {evidence_path}: {exc}")
        continue
    with bpy.data.libraries.load(str(source_path), link=False) as (data_from, _data_to):
        if collection_name not in data_from.collections:
            errors.append(f"{collection_name} absent from {source_path.name}; available={data_from.collections}")
            continue
        scene_names = list(data_from.scenes)
    if asset_id in by_id:
        record = by_id[asset_id]
        if record.get("kind") != "detailed":
            errors.append(f"asset id collides with non-detailed record: {asset_id}")
            continue
        record.update({"file": file_rel, "collection": collection_name, "scene": scene_names[0] if scene_names else None,
                       "placement_origin_xy_m": list(origin_xy), "local_coordinates": True,
                       "evidence_file": evidence_rel})
        registered.append(asset_id)
        continue
    source_meta = {
        "evidence_file": evidence_rel,
        "source_massing_id": old_id,
        "feature": evidence.get("source_feature") or evidence.get("official_gis") or evidence.get("gis_source"),
        "retrieved_date": evidence.get("retrieved_date") or evidence.get("retrieval_date") or evidence.get("retrieved_utc_date"),
    }
    record = {
        "id": asset_id,
        "kind": "detailed",
        "file": file_rel,
        "collection": collection_name,
        "scene": scene_names[0] if scene_names else None,
        "objects": [],
        "object_count": 0,
        "bounds_world_m": None,
        "accuracy_status": f"Purdue GIS footprint/source identity and imagery evidence documented; remaining facade, height, interior and position limits are listed in {evidence_rel}",
        "placement_transform": "master Placement_<id> translates local geometry to placement_origin_xy_m",
        "source_metadata": source_meta,
        "placement_origin_xy_m": [float(origin_xy[0]), float(origin_xy[1])],
        "local_coordinates": True,
        "evidence_file": evidence_rel,
    }
    manifest["assets"].append(record)
    by_id[asset_id] = record
    registered.append(asset_id)

if errors:
    raise RuntimeError("Batch registration stopped: " + " | ".join(errors))

manifest["detailed_asset_count"] = sum(a.get("kind") == "detailed" for a in manifest["assets"])
MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps({"registered_or_refreshed": registered, "registered_count": len(registered),
                  "detailed_asset_count": manifest["detailed_asset_count"]}))

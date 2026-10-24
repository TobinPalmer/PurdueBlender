"""Rebuild the campus scene from linked building libraries and placement markers."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

MODULAR = Path(__file__).resolve().parent
manifest_path = MODULAR / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
scene = bpy.context.scene
root_collection = scene.collection
asset_by_id = {a["id"]: a for a in manifest["assets"]}
detailed = [a for a in manifest["assets"] if a.get("kind") == "detailed"]

def resolve_library(collection):
    if collection.library is None:
        return None
    return Path(bpy.path.abspath(collection.library.filepath)).resolve()

def get_linked_collection(record):
    expected = (MODULAR / record["file"]).resolve()
    collection = bpy.data.collections.get(record["collection"])
    if collection is not None and resolve_library(collection) == expected:
        return collection
    with bpy.data.libraries.load(str(expected), link=True, relative=True) as (src, dst):
        if record["collection"] not in src.collections:
            raise RuntimeError(f"{record['collection']} missing from {expected}")
        dst.collections = [record["collection"]]
    collection = dst.collections[0]
    if collection is None:
        raise RuntimeError(f"Failed to link {record['collection']}")
    return collection

def collection_local_matrix(obj, cache=None):
    """Get an object's transform within its source collection, ignoring master instances."""
    if cache is None:
        cache = {}
    if obj in cache:
        return cache[obj]
    matrix = obj.matrix_local.copy()
    if obj.parent is not None:
        matrix = collection_local_matrix(obj.parent, cache) @ matrix
    cache[obj] = matrix
    return matrix

# Detailed source libraries use local geometry; one collection instance per building
# carries the campus placement. This keeps edits in the small building file.
for record in detailed:
    collection = get_linked_collection(record)
    if collection in list(root_collection.children):
        root_collection.children.unlink(collection)
    marker_name = f"Placement_{record['id']}"
    marker = bpy.data.objects.get(marker_name)
    if marker is None:
        marker = bpy.data.objects.new(marker_name, None)
        root_collection.objects.link(marker)
    marker.empty_display_type = "PLAIN_AXES"
    marker.empty_display_size = 8.0
    marker.instance_type = "COLLECTION"
    marker.instance_collection = collection
    xy = record["placement_origin_xy_m"]
    marker.location = (xy[0], xy[1], 0.0)
    marker.rotation_euler = (0.0, 0.0, 0.0)
    marker.scale = (1.0, 1.0, 1.0)
    marker["asset_id"] = record["id"]
    marker["placement_origin_xy_m"] = list(xy)
    marker["linked_library"] = record["file"]
    marker["placement_method"] = "linked collection instance; geometry stored in local coordinates"

# Remove the simple footprint blocks that the new detailed shells replace.
superseded = {
    "massing_hicks_undergraduate_library_hiks_9467680": "hicks_library",
    "massing_krannert_school_of_management_26f5358": "krannert_building",
    "massing_lawson_hall_lwsn_49bd255": "lawson_hall",
    "massing_rawls_hall_44eb4c3": "rawls_hall",
    "massing_potter_engineering_center_potr_89c4c33": "potter_engineering",
    "massing_mechanical_engineering_me_8940174": "mechanical_engineering",
    "massing_max_w_maileen_brown_family_hall_of_electrical_engineering_bhee_078fbfb": "electrical_engineering",
    "massing_house_1033674920_dcd3b76": "elliott_hall_of_music",
    "massing_house_860822250_df21db0": "dudley_hall and lambertus_hall",
    "massing_knoy_hall_knoy_f598616": "knoy_hall",
    "massing_american_railway_building_rail_fc0f9a2": "american_railway_building",
    "massing_brown_laboratory_of_chemistry_brwn_aed3885": "brown_laboratory_of_chemistry",
    "massing_pierce_hall_prce_e5f59eb": "peirce_hall",
    "massing_psychological_sciences_building_psyc_34efd04": "psychological_sciences",
    "massing_r_b_wetherill_laboratory_of_chemistry_wthr_1577024": "wetherill_laboratory_of_chemistry",
    "massing_black_cultural_center_bcc_e2b2544": "black_cultural_center",
    "massing_birck_nanotechnology_center_362d0b7": "birck_nanotechnology_center",
    "massing_asian_american_and_asian_resource_and_cultural_center_aacc_da08bb2": "asian_american_resource_and_cultural_center",
    "massing_convergence_center_for_innovation_and_collaboration_conv_ce5226e": "convergence_center",
    "massing_lyles_porter_hall_lyle_604c08e": "lyles_porter_hall",
    "massing_agricultural_administration_building_120d92c": "agricultural_administration_building",
    "massing_agricultural_and_biological_engineering_abe_0ebc7b3": "agricultural_and_biological_engineering_abe",
    "massing_animal_disease_diagnostic_laboratory_b934354": "animal_disease_diagnostic_laboratory",
    "massing_bechtel_innovation_design_center_bidc_5488863": "bechtel_innovation_design_center_bidc",
    "massing_bindley_bioscience_center_641f939": "bindley_bioscience_center",
    "massing_biochemistry_building_a267b8d": "biochemistry_building",
    "massing_david_and_bonnie_brunner_farm_animal_hospital_dada82b": "david_and_bonnie_brunner_farm_animal_hospital",
    "massing_dauch_alumni_center_3cb1249": "dauch_alumni_center",
    "massing_drew_and_brittany_brees_student_athletic_academic_center_bres_da89033": "brees_student_athletic_academic_center",
    "massing_ford_dining_court_71eede4": "ford_dining_court",
    "massing_flex_lab_flex_cc297ea": "flex_lab",
    "massing_hall_for_discovery_and_learning_research_dlr_ed8395e": "hall_for_discovery_and_learning_research",
    "massing_heine_pharmacy_rhph_2f36735": "heine_pharmacy",
    "massing_ray_w_herrick_laboratories_36b11c6": "ray_w_herrick_laboratories",
    "massing_horticulture_286a904": "horticulture_building",
    "massing_krach_leadership_center_krch_debcdf8": "krach_leadership_center",
    "massing_lambert_ward_l_fieldhouse_and_gymnasium_1656862": "lambert_fieldhouse",
    "massing_life_science_plant_and_soils_laboratory_5963acd": "life_science_plant_and_soils_laboratory",
    "massing_materials_science_and_electrical_engineering_msee_003a4e2": "materials_science_and_electrical_engineering_msee",
    "massing_morgan_center_for_entrepreneurship_mrgn_9ba681c": "burton_morgan_center",
    "massing_morgan_j_burke_boilermaker_aquatic_center_2e6697f": "morgan_j_burke_boilermaker_aquatic_center",
    "massing_national_soil_erosion_laboratory_soil_0a1864c": "national_soil_erosion_laboratory",
    "massing_native_american_educational_and_cultural_center_nacc_faa0f59": "native_american_educational_and_cultural_center_nacc",
    "massing_northwest_chiller_plant_nwcp_2b32fa6": "northwest_chiller_plant",
    "massing_physics_building_phys_3bf42f3": "physics_building",
}
for old_id, replacement in superseded.items():
    old = asset_by_id.get(old_id)
    if old is None:
        orphan = bpy.data.collections.get('Asset_' + old_id)
        if orphan is not None and orphan in list(root_collection.children):
            root_collection.children.unlink(orphan)
        continue
    collection = bpy.data.collections.get(old["collection"])
    if collection is not None and collection in list(root_collection.children):
        root_collection.children.unlink(collection)
    old["master_visibility"] = f"superseded by detailed {replacement}"

# Newly registered massing modules (including split Dudley/Lambertus) link directly.
for record in manifest['assets']:
    if record.get('kind') != 'massing' or record['id'] in superseded or record.get('master_visibility','').startswith('superseded'):
        continue
    collection = get_linked_collection(record)
    if collection not in list(root_collection.children):
        root_collection.children.link(collection)

# Source edits may add or retire geometry; refresh counts from loaded libraries.
for record in detailed:
    collection = get_linked_collection(record)
    objects = list(collection.all_objects)
    record['objects'] = [obj.name for obj in objects]
    record['object_count'] = len(objects)
    local_matrices = {}
    points = [collection_local_matrix(obj, local_matrices) @ Vector(corner)
              for obj in objects if obj.type in {'MESH','CURVE','FONT'}
              for corner in obj.bound_box]
    if points:
        local = [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
        record['local_bounds_m'] = local
        xy=record['placement_origin_xy_m']
        record['bounds_world_m'] = [[v+xy[i] for v in local[i]] if i<2 else local[i] for i in range(3)]

# Persist the placement convention and current build details.
manifest["detailed_asset_count"] = len(detailed)
manifest["placement_model"] = "Detailed assets are local-coordinate linked collections. Placement_<id> empties in the master supply XY campus coordinates. Massing assets retain their original campus coordinates and are linked directly."
manifest["last_master_build"] = "2026-10-24"
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

bpy.context.view_layer.update()
expected = {f"Placement_{a['id']}": a for a in detailed}
errors = []
for name, record in expected.items():
    marker = bpy.data.objects.get(name)
    if marker is None or marker.instance_collection is None:
        errors.append(f"missing collection instance: {name}")
        continue
    if marker.instance_collection.name != record["collection"]:
        errors.append(f"wrong collection on {name}: {marker.instance_collection.name}")
    expected_path = (MODULAR / record["file"]).resolve()
    linked_path = resolve_library(marker.instance_collection)
    if linked_path != expected_path:
        errors.append(f"wrong source path on {name}: {linked_path}")
    expected_xy = record["placement_origin_xy_m"]
    actual_xy = marker.location[:2]
    if any(abs(float(actual_xy[i]) - float(expected_xy[i])) > 0.001 for i in range(2)):
        errors.append(f"wrong placement on {name}: actual={list(actual_xy)}, expected={expected_xy}")
for old_id in superseded:
    old = asset_by_id.get(old_id)
    if old:
        col = bpy.data.collections.get(old["collection"])
        if col is not None and col in list(root_collection.children):
            errors.append(f"superseded massing still linked: {old_id}")

verification = {
    "status": "PASS" if not errors else "FAIL",
    "asset_count": len(manifest["assets"]),
    "building_count": sum(a.get("kind") != "site" for a in manifest["assets"]),
    "detailed_asset_count": len(detailed),
    "master_placement_markers": sum(1 for o in scene.objects if o.name.startswith("Placement_")),
    "master_scene_object_count": len(scene.objects),
    "source_asset_object_count": sum(a.get("object_count", 0) for a in manifest["assets"]),
    "superseded_massing_assets": list(superseded),
    "errors": errors,
    "placement_model": manifest["placement_model"],
}
(MODULAR / "verification.json").write_text(json.dumps(verification, indent=2), encoding="utf-8")
if errors:
    raise RuntimeError("Master build verification failed: " + "; ".join(errors))

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps(verification))

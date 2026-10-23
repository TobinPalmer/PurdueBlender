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
    points = [obj.matrix_world @ Vector(corner) for obj in objects if obj.type in {'MESH','CURVE','FONT'} for corner in obj.bound_box]
    if points:
        local = [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
        record['local_bounds_m'] = local
        xy=record['placement_origin_xy_m']
        record['bounds_world_m'] = [[v+xy[i] for v in local[i]] if i<2 else local[i] for i in range(3)]

# Persist the placement convention and current build details.
manifest["detailed_asset_count"] = len(detailed)
manifest["placement_model"] = "Detailed assets are local-coordinate linked collections. Placement_<id> empties in the master supply XY campus coordinates. Massing assets retain their original campus coordinates and are linked directly."
manifest["last_master_build"] = "2026-10-23"
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
    if tuple(round(float(v), 4) for v in marker.location[:2]) != tuple(round(float(v), 4) for v in record["placement_origin_xy_m"]):
        errors.append(f"wrong placement on {name}")
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

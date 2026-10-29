"""Replace three fast-map proxy collections with Rossen's reviewed source revisions."""
import bpy,json,math,time,traceback
from collections import Counter
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT_DIR=ROOT/"audit"/"master_open_optimization"
ASSET_LIST=OUT_DIR/"active_assets.json"
PROXY_FILE=OUT_DIR/"campus_proxy_library.blend"
OUTPUT_FILE=OUT_DIR/"campus_proxy_library_rossen.blend"
REPORT_FILE=OUT_DIR/"rossen_proxy_update_report.json"
assets=json.loads(ASSET_LIST.read_text(encoding="utf-8"))
revisions=json.loads((OUT_DIR/"rossen_source_revisions.json").read_text(encoding="utf-8"))
revision_by_id={r["id"]:r for r in revisions}
modular=ROOT/"modular"
bpy.ops.wm.open_mainfile(filepath=str(PROXY_FILE))
scene=bpy.context.scene
proxy_root=bpy.data.collections.get("CampusProxyLibrary")
if proxy_root is None: raise RuntimeError("CampusProxyLibrary collection missing")
palette={}
for material in bpy.data.materials:
    if not material.name.startswith("CampusPalette_"): continue
    c=material.diffuse_color
    q=tuple(round(max(0.0,min(1.0,float(v)))*31.0)/31.0 for v in c[:3])+(1.0,)
    palette[q]=material
for material in palette.values(): material.use_fake_user=True
results=[]
failures=[]
def remove_proxy_collection(name):
    old=bpy.data.collections.get(name)
    if old is None: raise RuntimeError(f"Existing proxy collection missing: {name}")
    for obj in list(old.all_objects):
        if obj.library is None: bpy.data.objects.remove(obj,do_unlink=True)
    for child in reversed(descendants(old)):
        bpy.data.collections.remove(child,do_unlink=True)
    bpy.data.collections.remove(old,do_unlink=True)
def descendants(collection):
    found = []
    stack = list(collection.children)
    while stack:
        child = stack.pop()
        found.append(child)
        stack.extend(list(child.children))
    return found

def object_bounds(objects):
    points = []
    for obj in objects:
        if obj.type not in {"MESH", "CURVE", "FONT", "SURFACE"}:
            continue
        try:
            points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
        except Exception:
            pass
    if not points:
        return None
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]

def mesh_bounds(obj):
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    if not points:
        return None
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]

def palette_material(source_material):
    color = None
    if source_material is not None:
        node_tree = getattr(source_material, "node_tree", None)
        if node_tree is not None:
            bsdf = next((n for n in node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if bsdf is not None:
                base = bsdf.inputs.get("Base Color")
                if base is not None and not base.is_linked:
                    color = tuple(base.default_value)
        if color is None:
            color = tuple(source_material.diffuse_color)
    if color is None:
        color = (0.68, 0.68, 0.68, 1.0)
    q = tuple(round(max(0.0, min(1.0, float(v))) * 31.0) / 31.0 for v in color[:3]) + (1.0,)
    material = palette.get(q)
    if material is None:
        suffix = "".join(f"{round(v * 31):02x}" for v in q[:3])
        material = bpy.data.materials.new("CampusPalette_" + suffix)
        material.diffuse_color = q
        material.use_nodes = True
        bsdf = next((n for n in material.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf is not None:
            base = bsdf.inputs.get("Base Color")
            if base is not None:
                base.default_value = q
            roughness = bsdf.inputs.get("Roughness")
            if roughness is not None:
                roughness.default_value = 0.82
        palette[q] = material
    return material

def remap_materials(obj):
    if obj.type != "MESH":
        return
    if obj.data.library is not None:
        obj.data = obj.data.copy()
    slots = list(obj.material_slots)
    old_materials = [slot.material for slot in slots]
    if not old_materials:
        old_materials = [None]
    mapped = [palette_material(material) for material in old_materials]
    unique = []
    slot_map = {}
    for material in mapped:
        if material not in slot_map:
            slot_map[material] = len(unique)
            unique.append(material)
    for polygon in obj.data.polygons:
        index = polygon.material_index
        polygon.material_index = slot_map.get(mapped[index] if index < len(mapped) else mapped[0], 0)
    if any(slot.link == "OBJECT" for slot in slots) and obj.data.users > 1:
        obj.data = obj.data.copy()
    obj.data.materials.clear()
    for material in unique:
        obj.data.materials.append(material)
    for slot in obj.material_slots:
        slot.link = "DATA"

def realize_collection_instances(collection):
    realized = 0
    for _ in range(8):
        instancers = [o for o in collection.all_objects if o.type == "EMPTY" and o.instance_type == "COLLECTION"]
        if not instancers:
            return realized
        if len(instancers) > 5000:
            raise RuntimeError(f"Refusing to realize {len(instancers)} nested collection instances")
        bpy.ops.object.select_all(action="DESELECT")
        for obj in instancers:
            obj.hide_set(False)
            obj.select_set(True)
        bpy.context.view_layer.objects.active = instancers[0]
        bpy.ops.object.duplicates_make_real(use_base_parent=False, use_hierarchy=False)
        realized += len(instancers)
        for obj in instancers:
            if obj.name in bpy.data.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
        bpy.context.view_layer.update()
    remaining = [o.name for o in collection.all_objects if o.type == "EMPTY" and o.instance_type == "COLLECTION"]
    if remaining:
        raise RuntimeError("Unrealized collection instances: " + ", ".join(remaining[:5]))
    return realized

def apply_garage_cutout(collection):
    pgsc = next((a for a in assets if a["id"] == "massing_purdue_graduate_student_center_af9c5c7"), None)
    if pgsc is None or pgsc.get("kind") != "detailed":
        return False
    garage = next((o for o in collection.all_objects if o.type == "MESH" and o.name.startswith("Northwestern Parking Garage")), None)
    if garage is None:
        raise RuntimeError("Northwestern Parking Garage source mesh is unavailable for the PGSC cutout")
    cutout_path = ROOT / "audit" / "purdue_graduate_student_center" / "pgsc_garage_cutout_polygon.json"
    cutout = json.loads(cutout_path.read_text(encoding="utf-8"))
    ring = cutout["cutout_ring_xy_m"][:-1]
    n = len(ring)
    inverse = garage.matrix_world.inverted()
    vertices = [tuple(inverse @ Vector((x, y, z))) for z in (-0.5, 4.5) for x, y in ring]
    faces = [tuple(range(n)), tuple(reversed(range(n, 2 * n)))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    cutter_mesh = bpy.data.meshes.new("PGSC_MasterCutout_CutterMesh")
    cutter_mesh.from_pydata(vertices, [], faces)
    cutter_mesh.update()
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(cutter_mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(cutter_mesh)
    bm.free()
    cutter = bpy.data.objects.new("PGSC_MasterCutout_Cutter", cutter_mesh)
    collection.objects.link(cutter)
    cutter.matrix_world = garage.matrix_world.copy()
    bpy.ops.object.select_all(action="DESELECT")
    garage.select_set(True)
    bpy.context.view_layer.objects.active = garage
    boolean = garage.modifiers.new("Master_PGSC_Interface_Cutout", "BOOLEAN")
    boolean.operation = "DIFFERENCE"
    boolean.solver = "EXACT"
    boolean.object = cutter
    bpy.ops.object.modifier_apply(modifier=boolean.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    if cutter_mesh.users == 0:
        bpy.data.meshes.remove(cutter_mesh)
    return True

def flatten_asset(record):
    source = (modular / record["file"]).resolve()
    collection_name = record["collection"]
    with bpy.data.libraries.load(str(source), link=False) as (data_from, data_to):
        if collection_name not in data_from.collections:
            raise RuntimeError(f"Collection {collection_name} missing from {source}")
        data_to.collections = [collection_name]
    collection = data_to.collections[0]
    if collection is None:
        raise RuntimeError(f"Failed to append {collection_name}")
    instance_offset = tuple(collection.instance_offset)
    scene.collection.children.link(collection)
    bpy.context.view_layer.update()
    before_objects = list(collection.all_objects)
    realized = realize_collection_instances(collection)
    boolean_cutout = apply_garage_cutout(collection) if record["id"] == "massing_northwestern_parking_garage_979f1a2" else False
    source_objects = list(collection.all_objects)
    conversion_targets = [o for o in source_objects if o.type in {"FONT", "CURVE", "SURFACE"} or (o.type == "MESH" and len(o.modifiers) > 0)]
    if conversion_targets:
        bpy.ops.object.select_all(action="DESELECT")
        for obj in conversion_targets:
            obj.hide_set(False)
            obj.select_set(True)
        bpy.context.view_layer.objects.active = conversion_targets[0]
        bpy.ops.object.convert(target="MESH")
    source_objects = list(collection.all_objects)
    source_bounds = object_bounds(source_objects)
    mesh_objects = [o for o in source_objects if o.type == "MESH"]
    if mesh_objects:
        for obj in mesh_objects:
            obj.hide_set(False)
            remap_materials(obj)
        bpy.ops.object.select_all(action="DESELECT")
        for obj in mesh_objects:
            obj.select_set(True)
        active = next((o for o in mesh_objects if o.library is None), mesh_objects[0])
        bpy.context.view_layer.objects.active = active
        bpy.ops.object.join()
        joined = active
        joined.name = "CampusProxy_" + record["id"]
        joined.data.update()
        proxy_bounds = mesh_bounds(joined)
    else:
        joined = None
        proxy_bounds = None
    # Keep non-mesh context objects (camera, light, and root empties) with the merged geometry.
    keep = [o for o in collection.all_objects if o.type != "MESH" and not (o.type == "EMPTY" and o.instance_type == "COLLECTION")]
    if joined is not None:
        keep.append(joined)
    keep = list(dict.fromkeys(keep))
    keep_set = set(keep)
    for obj in keep:
        if obj.parent is not None and obj.parent not in keep_set:
            matrix = obj.matrix_world.copy()
            obj.parent = None
            obj.matrix_world = matrix
    child_collections = descendants(collection)
    for obj in keep:
        for owner in list(obj.users_collection):
            if owner != collection:
                owner.objects.unlink(obj)
        if collection not in obj.users_collection:
            collection.objects.link(obj)
    # Remove every non-mesh source object after the merged geometry has been created,
    # then flatten the source collection hierarchy into one lightweight collection.
    for obj in list(collection.all_objects):
        if obj not in keep_set:
            bpy.data.objects.remove(obj, do_unlink=True)
    for child in reversed(child_collections):
        for nested in list(child.children):
            child.children.unlink(nested)
        parent = next((p for p in [collection] + child_collections if child.name in p.children), None)
        if parent is not None:
            parent.children.unlink(child)
        if child.users == 0:
            bpy.data.collections.remove(child)
    collection.instance_offset = instance_offset
    collection["proxy_asset_id"] = record["id"]
    collection["proxy_source_kind"] = record.get("kind", "")
    collection["proxy_source_library"] = record["file"]
    collection["proxy_original_collection"] = collection_name
    collection["proxy_source_object_count"] = int(record.get("object_count") or len(before_objects))
    if joined is not None:
        joined["proxy_source_asset_id"] = record["id"]
        joined["proxy_source_library"] = record["file"]
    if collection.name not in proxy_root.children:
        proxy_root.children.link(collection)
    # Remove any orphaned source materials, images, meshes, and nested library IDs.
    bpy.data.orphans_purge(do_recursive=True)
    row = {
        "id": record["id"], "kind": record.get("kind"), "file": record["file"],
        "source_object_count": len(before_objects), "realized_collection_instances": realized,
        "mesh_objects_before_join": len(mesh_objects), "converted_objects": len(conversion_targets),
        "merged_vertices": len(joined.data.vertices) if joined else 0,
        "merged_polygons": len(joined.data.polygons) if joined else 0,
        "proxy_materials": len(joined.data.materials) if joined else 0,
        "retained_non_mesh_types": dict(Counter(o.type for o in keep if o != joined)),
        "garage_cutout_applied": boolean_cutout, "source_bounds": source_bounds, "proxy_bounds": proxy_bounds,
        "instance_offset": list(instance_offset),
    }
    return row



start=time.time()
selected=[a for a in assets if a["id"] in revision_by_id]
if len(selected)!=len(revisions): raise RuntimeError(f"Matched {len(selected)} of {len(revisions)} revision records")
for index,base_record in enumerate(selected,1):
    record=dict(base_record)
    record["object_count"]=None
    metadata=revision_by_id[record["id"]]
    try:
        remove_proxy_collection(record["collection"])
        row=flatten_asset(record)
        collection=bpy.data.collections.get(record["collection"])
        if collection is None: raise RuntimeError("Updated proxy collection missing after flatten")
        collection["proxy_source_git_commit"]=metadata["source_commit"]
        collection["proxy_source_git_branch"]=metadata["branch"]
        collection["proxy_review_status"]=metadata["review_status"]
        if metadata.get("review_score") is not None: collection["proxy_review_score"]=float(metadata["review_score"])
        row["source_commit"]=metadata["source_commit"]
        row["source_branch"]=metadata["branch"]
        row["review_status"]=metadata["review_status"]
        results.append(row)
        print(f"ROSSEN_PROXY_UPDATED {record['id']} objects={row['source_object_count']} verts={row['merged_vertices']} polys={row['merged_polygons']}",flush=True)
    except Exception as exc:
        failures.append({"id":record.get("id"),"error":repr(exc),"traceback":traceback.format_exc()})
        print(f"ROSSEN_PROXY_ERROR {record.get('id')}: {exc}",flush=True)
        break
if failures: raise RuntimeError(f"Rossen proxy update failed: {failures[0]['error']}")
for material in palette.values(): material.use_fake_user=False
bpy.data.orphans_purge(do_recursive=True)
if len(proxy_root.children)!=838: raise RuntimeError(f"Expected 838 proxy collections, found {len(proxy_root.children)}")
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_FILE))
report={"status":"PASS","updated_assets":len(results),"expected_assets":len(revisions),"asset_results":results,"proxy_collection_count":len(proxy_root.children),"external_libraries":len(bpy.data.libraries),"source_revisions":revisions,"output_file":str(OUTPUT_FILE),"elapsed_seconds":round(time.time()-start,2)}
REPORT_FILE.write_text(json.dumps(report,indent=2),encoding="utf-8")
print("ROSSEN_PROXY_UPDATE_COMPLETE "+json.dumps({k:v for k,v in report.items() if k!="asset_results"}),flush=True)

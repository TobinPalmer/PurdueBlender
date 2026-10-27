import bpy, hashlib, json
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
BLEND = ROOT / "modular/buildings/electrical_engineering.blend"
OUT = ROOT / "audit/electrical_engineering_independent_grade_r2/probe.json"
SOURCE = ROOT / "audit/official_building_references.json"
EXPECTED_SHA = "535ff224bd0105389a2fea01c5542e219d48716ad6089b173a42efbe0a7b4612"

sha = hashlib.sha256(BLEND.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
scene = bpy.context.scene
col = bpy.data.collections.get("Asset_electrical_engineering")
all_objects = list(col.all_objects) if col else []
mesh_objects = [o for o in all_objects if o.type == 'MESH']
materials = sorted({m.name for o in all_objects if o.type in {'MESH', 'FONT'}
                    for m in o.data.materials if m})
external_images = []
for im in bpy.data.images:
    if im.source == 'FILE' and im.filepath:
        path = bpy.path.abspath(im.filepath)
        if not Path(path).exists(): external_images.append({"name": im.name, "path": im.filepath, "missing": True})

def bounds_of(objects):
    corners = [(o.matrix_world @ Vector(c)) for o in objects if o.type == 'MESH' for c in o.bound_box]
    if not corners: return None
    return [[round(min(p[i] for p in corners), 5), round(max(p[i] for p in corners), 5)] for i in range(3)]

objects = []
for o in all_objects:
    objects.append({"name": o.name, "type": o.type,
                    "vertices": len(o.data.vertices) if o.type == 'MESH' else None,
                    "polygons": len(o.data.polygons) if o.type == 'MESH' else None,
                    "dimensions": [round(v, 4) for v in o.dimensions],
                    "location": [round(v, 5) for v in o.location],
                    "world_bounds": bounds_of([o]),
                    "modifiers": [{"name": m.name, "type": m.type} for m in o.modifiers]})

source = json.loads(SOURCE.read_text(encoding='utf-8'))
origin = (143.8499984741211, 135.0)
footprints = {}
for fid in (292, 109):
    f = next(x for x in source['buildings'] if x['fid'] == fid)
    rings = f['rings_xy_m']
    ob = bpy.data.objects.get(f"BHEE_ClippedSlabFID{fid}")
    if not ob:
        footprints[str(fid)] = {"present": False}
        continue
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    vertices = [(ev.matrix_world @ v.co) for v in mesh.vertices]
    ev.to_mesh_clear()
    model_xy = {(round(v.x, 5), round(v.y, 5)) for v in vertices}
    source_xy = []
    for ring in rings:
        source_xy.extend([(round(x-origin[0],5), round(y-origin[1],5)) for x,y in ring])
    nearest = []
    for sx, sy in source_xy:
        nearest.append(min(((sx-x)**2+(sy-y)**2)**0.5 for x,y in model_xy))
    footprints[str(fid)] = {
        "present": True, "ring_count": len(rings), "source_boundary_vertices": len(source_xy),
        "model_mesh_vertices": len(vertices), "max_source_vertex_to_mesh_vertex_m": round(max(nearest), 5),
        "mean_source_vertex_to_mesh_vertex_m": round(sum(nearest)/len(nearest), 5),
        "source_bbox_xy": [round(min(x for x,y in source_xy),5), round(min(y for x,y in source_xy),5),
                           round(max(x for x,y in source_xy),5), round(max(y for x,y in source_xy),5)],
        "model_bbox_xy": [round(min(x for x,y in model_xy),5), round(min(y for x,y in model_xy),5),
                          round(max(x for x,y in model_xy),5), round(max(y for x,y in model_xy),5)]}

scene_names = sorted(s.name for s in bpy.data.scenes)
collection_names = sorted(c.name for c in bpy.data.collections)
root = bpy.data.objects.get('AssetRoot_electrical_engineering')
report = {
    "inspected_sha256": sha, "expected_sha256": EXPECTED_SHA,
    "sha_matches_requested": sha == EXPECTED_SHA,
    "scene": scene.name, "all_scenes": scene_names,
    "collection_present": col is not None,
    "collection_name": col.name if col else None,
    "collection_object_count": len(all_objects), "mesh_object_count": len(mesh_objects),
    "materials": materials, "missing_external_images": external_images,
    "collection_bounds_xyz": bounds_of(all_objects),
    "asset_root": ({"location": list(root.location), "rotation": list(root.rotation_euler),
                    "scale": list(root.scale), "dimensions": list(root.dimensions)} if root else None),
    "footprint_vertex_comparison": footprints,
    "object_inventory": objects
}
OUT.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k != 'object_inventory'}, indent=2))
if not report['sha_matches_requested']:
    raise RuntimeError('Frozen SHA mismatch')
if not col or scene.name != 'Building_electrical_engineering':
    raise RuntimeError('Expected scene/collection missing')

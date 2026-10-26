"""Fresh-process structural validation for the FSTE candidate Blender asset."""
import bpy, json, hashlib
from pathlib import Path

root=Path(__file__).resolve().parents[2]
asset=root/"modular/buildings/massing_first_street_towers_east_fste_c9b22d3.blend"
out=Path(__file__).resolve().parent/"validation_fresh_open.json"
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene_name="Building_massing_first_street_towers_east_fste_c9b22d3"
collection_name="Asset_massing_first_street_towers_east_fste_c9b22d3"
scene=bpy.data.scenes.get(scene_name)
col=bpy.data.collections.get(collection_name)
if scene is None or col is None: raise RuntimeError("Required scene or export collection missing")
if bpy.context.scene.name != scene_name: bpy.context.window.scene=scene
allcoords=[]
mesh_objects=[]
materials=set()
for obj in col.objects:
    if obj.type=="MESH":
        mesh_objects.append(obj)
        for v in obj.data.vertices:
            allcoords.append(obj.matrix_world @ v.co)
        materials.update(m.name for m in obj.data.materials if m)
if not mesh_objects: raise RuntimeError("No mesh objects exported")
if not allcoords: raise RuntimeError("No exported mesh vertices")
low=[min(v[i] for v in allcoords) for i in range(3)]
high=[max(v[i] for v in allcoords) for i in range(3)]
wall=bpy.data.objects.get("FSTE | six-story GIS perimeter walls")
wallcoords=[wall.matrix_world @ v.co for v in wall.data.vertices]
wall_bounds=[[min(v[i] for v in wallcoords),max(v[i] for v in wallcoords)] for i in range(3)]
# Recover the GIS perimeter from the boundary edges of the triangulated level-3
# floorplate, so the doorway gap in the wall mesh does not affect the footprint.
floor_obj=bpy.data.objects.get("FSTE | floor plate level 3 on source footprint")
edge_counts={}
edge_directed={}
for poly in floor_obj.data.polygons:
    ids=list(poly.vertices)
    for j,a_id in enumerate(ids):
        b_id=ids[(j+1)%len(ids)]
        a=floor_obj.matrix_world @ floor_obj.data.vertices[a_id].co
        b=floor_obj.matrix_world @ floor_obj.data.vertices[b_id].co
        pa=(round(a.x,8),round(a.y,8)); pb=(round(b.x,8),round(b.y,8))
        key=tuple(sorted((pa,pb)))
        edge_counts[key]=edge_counts.get(key,0)+1
        edge_directed[key]=(pa,pb)
boundary=[edge_directed[k] for k,c in edge_counts.items() if c==1]
structural_outline_xy=[]
if boundary:
    first=boundary.pop(0); structural_outline_xy=[first[0],first[1]]
    while boundary and structural_outline_xy[-1]!=structural_outline_xy[0]:
        end=structural_outline_xy[-1]
        match=next((i for i,e in enumerate(boundary) if e[0]==end),None)
        if match is None: break
        edge=boundary.pop(match); structural_outline_xy.append(edge[1])
    if structural_outline_xy[-1]==structural_outline_xy[0]: structural_outline_xy.pop()
missing_nodes=[]
for m in bpy.data.materials:
    if m.name.startswith("FSTE |") and m.use_nodes and not m.node_tree.nodes.get("Principled BSDF"):
        missing_nodes.append(m.name)
record={
  "fresh_open":True,
  "asset":str(asset),
  "asset_sha256":hashlib.sha256(asset.read_bytes()).hexdigest(),
  "scene":scene.name,
  "export_collection":col.name,
  "scene_provenance":scene.get("source_feature"),
  "height_uncertainty":scene.get("height_uncertainty"),
  "roof_uncertainty":scene.get("roof_uncertainty"),
  "entry_uncertainty":scene.get("entry_uncertainty"),
  "representative_entry_edge_index":scene.get("representative_entry_edge_index"),
  "representative_entry_distance_to_osm_1st_street_m":scene.get("representative_entry_distance_to_osm_1st_street_m"),
  "representative_entry_facing_alignment_to_1st_street":scene.get("representative_entry_facing_alignment_to_1st_street"),
  "representative_room_count_per_level":scene.get("representative_room_count_per_level"),
  "representative_gable_count":scene.get("representative_gable_count"),
  "collection_object_count":len(col.objects),
  "collection_mesh_object_count":len(mesh_objects),
  "unique_collection_material_count":len(materials),
  "material_names":sorted(materials),
  "all_mesh_bounds_xyz_m":[[round(x,4) for x in low],[round(x,4) for x in high]],
  "structural_wall_mesh_bounds_xyz_m":[[round(x,4) for x in b] for b in wall_bounds],
  "structural_wall_outline_xy_m":structural_outline_xy,
  "mesh_face_count":sum(len(o.data.polygons) for o in mesh_objects),
  "mesh_vertex_count":sum(len(o.data.vertices) for o in mesh_objects),
  "objects_in_collection":[o.name for o in col.objects],
  "principled_materials_missing_bsdf":missing_nodes,
  "external_texture_files":[],
  "errors":[]
}
if col.name!=collection_name: record["errors"].append("export collection mismatch")
if missing_nodes: record["errors"].append("one or more FSTE materials lack Principled BSDF")
if record["errors"]: raise RuntimeError(json.dumps(record,indent=2))
out.write_text(json.dumps(record,indent=2),encoding="utf-8")
print("FSTE_FRESH_VALIDATION",json.dumps(record,indent=2))

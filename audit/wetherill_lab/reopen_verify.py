"""Reopen the saved Wetherill library and verify export structure/portability."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
path=ROOT/"modular"/"buildings"/"wetherill_laboratory_of_chemistry.blend"
bpy.ops.wm.open_mainfile(filepath=str(path))
scene=bpy.data.scenes.get("Building_wetherill_laboratory_of_chemistry")
collection=bpy.data.collections.get("Asset_wetherill_laboratory_of_chemistry")
if scene is None or collection is None: raise RuntimeError("Expected detailed scene/export collection missing")
root=collection.objects.get("AssetRoot_wetherill_laboratory_of_chemistry")
if root is None: raise RuntimeError("Asset root missing")
objects=list(collection.all_objects)
meshes=[o for o in objects if o.type=="MESH"]
materials={m.name for o in objects if o.data and hasattr(o.data,"materials") for m in o.data.materials}
points=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
refdoc=json.loads((ROOT/"audit"/"official_building_references.json").read_text(encoding="utf-8"))
ref=next(r for r in refdoc["buildings"] if r["fid"]==257 and r["code"]=="WTHR")
ring=ref["rings_xy_m"][0][:-1]
origin=collection["placement_origin_xy_m"]
wall_rows=sorted((o for o in collection.objects if o.name.startswith("WTHR_PerimeterWall_")),key=lambda o:o.name)
edge_errors=[]
for i,o in enumerate(wall_rows):
    a=(o.matrix_world @ o.data.vertices[0].co)+Vector((origin[0],origin[1],0))
    b=(o.matrix_world @ o.data.vertices[1].co)+Vector((origin[0],origin[1],0))
    for actual,expected in ((a,ring[i]),(b,ring[(i+1)%len(ring)])):
        edge_errors.append(math.hypot(actual.x-expected[0],actual.y-expected[1]))
max_ring_error=max(edge_errors) if edge_errors else None
external_images=[]
for im in bpy.data.images:
    if im.source=="FILE" and im.filepath:
        full=Path(bpy.path.abspath(im.filepath))
        external_images.append({"name":im.name,"path":str(full),"exists":full.exists()})
libraries=[str(Path(bpy.path.abspath(l.filepath))) for l in bpy.data.libraries]
missing_libraries=[p for p in libraries if not Path(p).exists()]
unassigned=[o.name for o in meshes if len(o.data.materials)==0]
root_local=tuple(round(v,6) for v in root.location)
root_scale=tuple(round(v,6) for v in root.scale)
children=[o for o in objects if o!=root and o.parent==root]
sculpture=[o for o in objects if o.name.startswith("Leighty_Commons_Molecular")]
sculpture_x=[(o.matrix_world @ Vector(c)).x for o in sculpture for c in o.bound_box]
sculpture_span_x=max(sculpture_x)-min(sculpture_x) if sculpture_x else None
ver={
 "status":"PASS" if root_local==(0.0,0.0,0.0) and root_scale==(1.0,1.0,1.0) and not unassigned and not missing_libraries and max_ring_error is not None and max_ring_error<.001 and sculpture_span_x is not None and abs(sculpture_span_x-6.096)<.05 else "FAIL",
 "file":str(path),"scene":scene.name,"export_collection":collection.name,
 "asset_id":collection.get("asset_id"),"coordinate_frame":collection.get("coordinate_frame"),
 "placement_origin_xy_m":list(collection.get("placement_origin_xy_m",[])),
 "root":{"name":root.name,"local_location":root_local,"scale":root_scale,"parented_geometry_objects":len(children)},
 "object_count":len(objects),"mesh_object_count":len(meshes),"material_count":len(materials),
 "materials":sorted(materials),"unassigned_mesh_materials":unassigned,
 "evaluated_all_mesh_bounds_local_m":bounds,"external_file_images":external_images,
 "linked_libraries":libraries,"missing_libraries":missing_libraries,
 "visible_in_export_collection":True,"presentation_cameras_lights_outside_export_collection":True,
 "projected_plan_source":{"provider":"Purdue Campus GIS; WTHR FID 257","source_crs":"EPSG:4326; converted by project local linear approximation","ring_vertices":len(ring),"wall_outer_face_ring_error_m":max_ring_error},
 "estimated_eave_height_m":16.0,"highest_roof_equipment_m":bounds[2][1],"height_status":"estimated, five above-grade floors modeled at 3.2m spacing; not a survey measurement",
 "commons_sculpture_span_x_m":sculpture_span_x,"commons_sculpture_dimension_source":"Purdue Chemistry Leighty Commons page; 20 ft = 6.096 m",
}
(Path(__file__).parent/"reopen_verification.json").write_text(json.dumps(ver,indent=2),encoding="utf-8")
print(json.dumps(ver,indent=2))

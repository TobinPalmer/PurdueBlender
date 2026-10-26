import bpy, json
from pathlib import Path

asset = Path(__file__).resolve().parents[3] / "modular/buildings/massing_islamic_societyof_greater_lafayette_0130012.blend"
bpy.ops.wm.open_mainfile(filepath=str(asset))
coll = bpy.data.collections.get("Asset_massing_islamic_societyof_greater_lafayette_0130012")
scene = bpy.data.scenes.get("Building_massing_islamic_societyof_greater_lafayette_0130012")
deps = bpy.context.evaluated_depsgraph_get()
objects=[]; points=[]
for ob in coll.objects if coll else []:
    ev=ob.evaluated_get(deps); mesh=ev.to_mesh()
    verts=[ev.matrix_world @ v.co for v in mesh.vertices]
    if verts: points.extend(verts)
    objects.append({"name":ob.name,"type":ob.type,"vertices":len(mesh.vertices),"faces":len(mesh.polygons),"bounds_xyz_m":[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)] if verts else None,"materials":[m.name if m else None for m in mesh.materials]})
    ev.to_mesh_clear()
report={"asset":str(asset),"scene":scene.name if scene else None,"collection":coll.name if coll else None,"scene_objects":[o.name+":"+o.type for o in scene.objects] if scene else [],"objects":objects,"bounds_xyz_m":[[min(v[i] for v in points),max(v[i] for v in points)] for i in range(3)] if points else None,"modifiers":[m.name for o in coll.objects for m in o.modifiers] if coll else [],"linked_libraries":[lib.filepath for lib in bpy.data.libraries],"external_images":[im.filepath for im in bpy.data.images if im.source=="FILE" and im.filepath and not im.packed_file]}
out=Path(__file__).with_name("initial_asset_inspection.json")
out.write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))

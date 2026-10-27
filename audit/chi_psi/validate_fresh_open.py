"""Fresh-open checks and evidence render for chi_psi.blend.

Invoke with:
  blender -b modular/buildings/chi_psi.blend --python audit/chi_psi/validate_fresh_open.py
"""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
path=Path(bpy.data.filepath)
assert path.resolve()==(ROOT/"modular"/"buildings"/"chi_psi.blend").resolve(), bpy.data.filepath
scene=bpy.context.scene
assert scene.name=="Building_chi_psi"
col=bpy.data.collections.get("Asset_chi_psi")
assert col is not None
objs=list(col.all_objects)
meshes=[o for o in objs if o.type=="MESH"]
assert len(objs)==225, f"expected 225 recursively exported asset objects, got {len(objs)}"
assert len(col.objects)==214, f"expected 214 direct collection objects, got {len(col.objects)}"
assert len(meshes)>200
foundation=bpy.data.objects.get("ChiPsi_LiDAR_Footprint_Foundation")
shell=bpy.data.objects.get("ChiPsi_Main_Red_Brick_Shell")
assert foundation and shell and foundation in objs and shell in objs
fdims=tuple(round(float(v),6) for v in foundation.dimensions)
sdims=tuple(round(float(v),6) for v in shell.dimensions)
assert abs(fdims[0]-24.868676)<0.01 and abs(fdims[1]-19.013603)<0.01, fdims
deps=bpy.context.evaluated_depsgraph_get()
pts=[]
for ob in objs:
    if ob.type not in {"MESH","FONT","CURVE"}: continue
    evaluated=ob.evaluated_get(deps)
    for corner in evaluated.bound_box:
        pts.append(ob.matrix_world @ Vector(corner))
bounds={axis:[round(min(getattr(p,axis) for p in pts),4),round(max(getattr(p,axis) for p in pts),4)] for axis in "xyz"}
external=[]
for image in bpy.data.images:
    if image.source=="FILE" and image.filepath and not image.packed_file:
        p=Path(bpy.path.abspath(image.filepath))
        if not p.exists(): external.append(image.filepath)
assert not external, external
schem=bpy.data.collections.get("Schematic_Interior_chi_psi")
assert schem and len(schem.objects)==11
assert all(o.get("representation","").startswith("Schematic interior cue") for o in schem.objects)
materials=sorted({m.name for ob in meshes for m in ob.data.materials if m})
sha=hashlib.sha256(path.read_bytes()).hexdigest()
scene.render.filepath=str(ROOT/"audit"/"chi_psi"/"chi_psi_fresh_open.png")
bpy.ops.render.render(write_still=True)
report={"status":"PASS","blender_version":bpy.app.version_string,"asset_path":str(path.relative_to(ROOT)).replace("\\","/"),"asset_sha256":sha,"scene":scene.name,"export_collection":col.name,"export_object_count_recursive":len(objs),"direct_collection_object_count":len(col.objects),"export_mesh_count_recursive":len(meshes),"schematic_interior_object_count":len(schem.objects),"foundation_local_dimensions_m":fdims,"main_wall_local_dimensions_m":sdims,"asset_world_local_bounds_m":bounds,"material_names":materials,"external_missing_image_paths":external,"fresh_open_render":"audit/chi_psi/chi_psi_fresh_open.png","placement_origin_xy_m":list(scene.get("placement_origin_xy_m")),"structural_footprint_source":scene.get("structural_footprint_source")}
(ROOT/"audit"/"chi_psi"/"fresh_open_verification.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,indent=2))

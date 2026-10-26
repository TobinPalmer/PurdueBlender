"""Fresh-open validation and review renders for Horizon Bank. Run in Blender."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/"modular/buildings/massing_horizon_bank_debc8f2.blend"
OUT=ROOT/"audit/horizon_bank"
ID="massing_horizon_bank_debc8f2"
EXPECTED_SCENE="Building_"+ID
EXPECTED_COLLECTION="Asset_"+ID
errors=[]

if bpy.data.filepath.lower()!=str(ASSET).lower(): errors.append("Blender did not open the assigned asset file directly")
scene=bpy.data.scenes.get(EXPECTED_SCENE)
asset=bpy.data.collections.get(EXPECTED_COLLECTION)
interior_scene=bpy.data.scenes.get("Horizon_Bank_Interior_Schematic_NOT_AS_BUILT")
interior=bpy.data.collections.get("Horizon_Bank_Interior_Schematic_NOT_AS_BUILT")
if not scene: errors.append("Expected building scene is missing")
if not asset: errors.append("Expected exported collection is missing")
if not interior_scene or not interior: errors.append("Separate schematic interior scene/collection is missing")
if scene and asset and asset.name not in [c.name for c in scene.collection.children]: errors.append("Asset collection is not a direct scene child")

objects=list(asset.all_objects) if asset else []
mesh_objects=[o for o in objects if o.type=="MESH"]
missing_materials=[o.name for o in mesh_objects if len(o.data.materials)==0]
if missing_materials: errors.append("Mesh objects without a material: "+", ".join(missing_materials))
image_paths=[]
for im in bpy.data.images:
    if im.source=="FILE": image_paths.append({"name":im.name,"filepath":im.filepath,"packed":bool(im.packed_file)})
unportable=[x for x in image_paths if not x["packed"] and Path(bpy.path.abspath(x["filepath"])).is_absolute()]
if unportable: errors.append("Unpacked absolute image dependencies exist")

deps=bpy.context.evaluated_depsgraph_get()
coords=[]
for ob in objects:
    if ob.type!="MESH": continue
    ev=ob.evaluated_get(deps)
    for v in ev.to_mesh().vertices:
        coords.append(ob.matrix_world @ v.co)
    ev.to_mesh_clear()
bounds=None
if coords:
    bounds={axis:{"min":min(getattr(v,axis) for v in coords),"max":max(getattr(v,axis) for v in coords)} for axis in ("x","y","z")}
else: errors.append("No evaluated mesh geometry in exported collection")
if len(mesh_objects)<20: errors.append("Expected detailed exterior mesh set, got too few meshes")
if asset and asset.get("source_footprint_feature_id")!="Indiana Building Footprints 2016-2020 / objectid 430274": errors.append("Asset source feature metadata is absent")

# Compare the actual exported wall-outline vertices with the preserved raw state GIS polygon.
src=json.loads((OUT/"sources/indiana_footprint_objectid_430274_2026-10-26.json").read_text(encoding="utf-8"))
feature=next(f for f in src["features"] if int(f["properties"]["objectid"])==430274)
ring=feature["geometry"]["coordinates"][0][:-1]
expected=[((lon+86.9137)*84810.60416539927,(lat-40.4274)*111040.0) for lon,lat in ring]
wall=bpy.data.objects.get("Horizon_Bank_LiDAR_Footprint_Walls")
outline_error={"vertex_count_source":len(expected),"vertex_count_model":0,"max_vertex_error_m":None,"rms_vertex_error_m":None}
if not wall or wall.type!="MESH":
    errors.append("Source-footprint wall mesh is missing")
else:
    model=[wall.matrix_world@v.co for v in wall.data.vertices[:len(expected)]]
    outline_error["vertex_count_model"]=len(model)
    if len(model)!=len(expected): errors.append("Model/GIS outline vertex count differs")
    else:
        errs=[((p.x-q[0])**2+(p.y-q[1])**2)**.5 for p,q in zip(model,expected)]
        outline_error["max_vertex_error_m"]=max(errs)
        outline_error["rms_vertex_error_m"]=(sum(e*e for e in errs)/len(errs))**.5
        if max(errs)>0.01: errors.append("Model outline does not register to raw GIS polygon within 1 cm")

# Render independent exterior and top-down review views without saving preview cameras into the file.
def add_camera(sc, name, loc, target, ortho):
    data=bpy.data.cameras.new(name+"Data"); cam=bpy.data.objects.new(name,data); sc.collection.objects.link(cam)
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler(); data.type="ORTHO"; data.ortho_scale=ortho
    return cam

views=[]
if scene and asset:
    scene.render.engine="BLENDER_EEVEE"
    scene.render.resolution_x=1200; scene.render.resolution_y=850; scene.render.resolution_percentage=100
    ex=add_camera(scene,"Audit_Exterior_Camera",(-775,2305,24),(-733,2258,2.5),42)
    scene.camera=ex
    scene.render.filepath=str(OUT/"horizon_bank_exterior_review.png")
    bpy.ops.render.render(write_still=True); views.append(str(OUT/"horizon_bank_exterior_review.png"))
    # The one-story facade is at the north/front edge. This plan view independently checks the L footprint.
    top=add_camera(scene,"Audit_Plan_Camera",(-733,2257,70),(-733,2257,0),31)
    top.rotation_euler=(0,0,0); top.data.type="ORTHO"; scene.camera=top
    scene.render.resolution_x=1000; scene.render.resolution_y=1000; scene.render.filepath=str(OUT/"horizon_bank_plan_review.png")
    bpy.ops.render.render(write_still=True); views.append(str(OUT/"horizon_bank_plan_review.png"))

if interior_scene and interior:
    interior_scene.render.engine="BLENDER_EEVEE"
    interior_scene.render.resolution_x=1000; interior_scene.render.resolution_y=700; interior_scene.render.resolution_percentage=100
    # Interior layout occupies roughly the bank XY extent at eye height near Z=11.
    cam=add_camera(interior_scene,"Audit_Interior_Schematic_Camera",(-733,2257,30),(-733,2257,0),32)
    cam.rotation_euler=(0,0,0)
    interior_scene.camera=cam
    ld=bpy.data.lights.new("Audit_Interior_Schematic_Light","AREA"); lo=bpy.data.objects.new("Audit_Interior_Schematic_Light",ld); interior_scene.collection.objects.link(lo)
    lo.location=(-733,2257,15); ld.energy=5000; ld.size=20; lo.rotation_euler=(Vector((-733,2257,2.5))-lo.location).to_track_quat("-Z","Y").to_euler()
    interior_scene.render.filepath=str(OUT/"horizon_bank_interior_schematic_review.png")
    bpy.ops.render.render(scene=interior_scene.name,write_still=True); views.append(str(OUT/"horizon_bank_interior_schematic_review.png"))

sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
result={
  "building_id":ID,"asset":str(ASSET),"asset_sha256":sha,"fresh_open":True,
  "scene":EXPECTED_SCENE,"collection":EXPECTED_COLLECTION,"exported_collection_object_count":len(objects),
  "mesh_object_count":len(mesh_objects),"unique_material_count":len({m.name for o in mesh_objects for m in o.data.materials if m}),
  "evaluated_geometry_bounds_m":bounds,"gis_outline_registration":outline_error,"materialless_mesh_objects":missing_materials,
  "external_images":image_paths,"interior_scene":"Horizon_Bank_Interior_Schematic_NOT_AS_BUILT",
  "interior_object_count":len(interior.all_objects) if interior else 0,
  "review_renders":views,"errors":errors,"status":"PASS" if not errors else "FAIL"
}
(OUT/"validation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))

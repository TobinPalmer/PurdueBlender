"""Fresh standalone reopen, portability check, and model review renders."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
AUDIT=Path(__file__).resolve().parent
ASSET=ROOT/"modular/buildings/massing_st_thomas_aquinas_5535390.blend"
COLLECTION="Asset_massing_st_thomas_aquinas_5535390"
EXPECTED_SCENE="Building_massing_st_thomas_aquinas_5535390"
scene=bpy.context.scene
asset=bpy.data.collections.get(COLLECTION)
if scene.name!=EXPECTED_SCENE or asset is None:
    raise RuntimeError("Fresh reopen has an unexpected scene or missing stable export collection")
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
objects=list(asset.all_objects)
root=bpy.data.objects.get("AssetRoot_massing_st_thomas_aquinas_5535390")
if root is None or root.parent is not None:
    raise RuntimeError("Local asset root is absent or parented unexpectedly")
if any(abs(float(v))>1e-6 for v in root.location) or any(abs(float(v))>1e-6 for v in root.rotation_euler) or any(abs(float(v)-1)>1e-6 for v in root.scale):
    raise RuntimeError("AssetRoot transform is not identity")
depsgraph=bpy.context.evaluated_depsgraph_get()
mins=[float("inf")]*3;maxs=[float("-inf")]*3
materialless=[];invalid=[];mesh_count=0
for obj in objects:
    if obj.type!="MESH":
        continue
    mesh_count+=1
    if len(obj.data.materials)==0:
        materialless.append(obj.name)
    if any(poly.material_index<0 or poly.material_index>=len(obj.data.materials) for poly in obj.data.polygons):
        invalid.append(obj.name)
    evaluated=obj.evaluated_get(depsgraph)
    mesh=evaluated.to_mesh()
    try:
        for v in mesh.vertices:
            p=evaluated.matrix_world@v.co
            for i in range(3):
                mins[i]=min(mins[i],float(p[i]));maxs[i]=max(maxs[i],float(p[i]))
    finally:
        evaluated.to_mesh_clear()
missing=[]
for img in bpy.data.images:
    if img.source=="FILE" and img.filepath and not Path(bpy.path.abspath(img.filepath)).exists():
        missing.append(img.filepath)
evidence={"reopened_saved_asset":True,"asset":str(ASSET),"sha256":sha,
          "scene":scene.name,"export_collection":asset.name,"object_count":len(objects),"mesh_count":mesh_count,
          "identity_root":True,"bounds_local_axis_major_m":[[mins[i],maxs[i]] for i in range(3)],
          "materialless_meshes":materialless,"invalid_material_meshes":invalid,
          "missing_external_images":missing,"linked_libraries":[lib.filepath for lib in bpy.data.libraries if lib.filepath],
          "placement_origin_xy_m":[21.32823749544109,-412.2141452954931]}
(AUDIT/"independent_reopen_r1_builder.json").write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if materialless or invalid or missing or evidence["linked_libraries"]:
    raise RuntimeError("Asset portability/material check failed")

# Renderer setup lives outside the exported collection; these cameras and lights are not asset payload.
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
scene.view_settings.view_transform="AgX"
world=bpy.data.worlds.new("SOTAC_Review_World") if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world;world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.32,0.38,0.46,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.7
def add_area(name,loc,energy,size,color,target):
    data=bpy.data.lights.new(name,"AREA");data.energy=energy;data.shape="DISK";data.size=size;data.color=color
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=loc
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    return obj
sun_data=bpy.data.lights.new("SOTAC_Review_Sun","SUN");sun_data.energy=2.0;sun_data.angle=math.radians(12)
sun=bpy.data.objects.new("SOTAC_Review_Sun",sun_data);scene.collection.objects.link(sun);sun.location=(-40,-60,80)
sun.rotation_euler=(Vector((0,0,0))-sun.location).to_track_quat("-Z","Y").to_euler()
add_area("SOTAC_Review_Fill",(35,40,50),1800,25,(1.0,0.83,0.66),(0,0,8))
def camera_at(name,location,target,ortho=None):
    data=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,data);scene.collection.objects.link(cam)
    cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    if ortho:
        data.type="ORTHO";data.ortho_scale=ortho
    else:
        data.lens=45
    scene.camera=cam
    return cam
def render(name,location,target,ortho=None):
    camera_at("SOTAC_ReviewCamera_"+name,location,target,ortho)
    scene.render.filepath=str(AUDIT/(name+"_r1.png"))
    bpy.ops.render.render(write_still=True)

render("exterior_entry_northwest",(-42,60,29),(0,0,7))
render("exterior_southeast",(54,-60,38),(0,0,8))
render("topdown_footprint",(0,0,95),(0,0,0),105)

# Interior evidence: temporarily open the shell and roof for an honest schematic cutaway view.
hidden=[]
hide_prefixes=("SOTAC_Stone_Foundation_and_Plinth","SOTAC_Continuous_Brick_Base_Shell",
               "SOTAC_Original_Church_Upper_Walls","SOTAC_New_Church_Addition_Upper_Walls",
               "SOTAC_Office_Classroom_Upper_Walls","SOTAC_Original_Church_Gable_Roof",
               "SOTAC_Original_Church_RidgeCap","SOTAC_Original_Church_Eave_",
               "SOTAC_New_Church_Roof_","SOTAC_Office_Classroom_Roof_",
               "SOTAC_New_Church_Roof_Parapet","SOTAC_Office_Classroom_Coping",
               "SOTAC_Office_Wing_Coping","SOTAC_Limestone_BaseBand","SOTAC_Corner_Pilaster",
               "SOTAC_Window_","SOTAC_BellTower_")
for obj in objects:
    if obj.name.startswith(hide_prefixes):
        hidden.append((obj,obj.hide_render));obj.hide_render=True
render("interior_sanctuary_cutaway",(12,-16,9),(9,16,5))
render("interior_classroom_cutaway",(-10,-48,13),(0,-21,2.5))
for obj,value in hidden:obj.hide_render=value
print(json.dumps(evidence,indent=2,ensure_ascii=False))

"""Fresh saved-file reopen, portability audit, and focused R4 review renders."""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
AUDIT=Path(__file__).resolve().parent
ASSET_PATH=ROOT/"modular/buildings/massing_st_thomas_aquinas_5535390.blend"
asset=bpy.data.collections.get("Asset_massing_st_thomas_aquinas_5535390")
if asset is None or bpy.context.scene.name!="Building_massing_st_thomas_aquinas_5535390":raise RuntimeError("Standalone library did not reopen correctly")
root=bpy.data.objects.get("AssetRoot_massing_st_thomas_aquinas_5535390")
if root is None or root.parent is not None:raise RuntimeError("Stable identity root is absent or parented")
if any(abs(float(x))>1e-7 for x in root.location) or any(abs(float(x))>1e-7 for x in root.rotation_euler) or any(abs(float(x)-1)>1e-7 for x in root.scale):raise RuntimeError("Root transform is not identity")
objects=list(asset.all_objects);deps=bpy.context.evaluated_depsgraph_get();mins=[float("inf")]*3;maxs=[float("-inf")]*3
materialless=[];invalid=[]
for ob in objects:
    if ob.type!="MESH":continue
    if not ob.data.materials:materialless.append(ob.name)
    if any(p.material_index<0 or p.material_index>=len(ob.data.materials) for p in ob.data.polygons):invalid.append(ob.name)
    ev=ob.evaluated_get(deps);me=ev.to_mesh()
    try:
        for v in me.vertices:
            co=ev.matrix_world@v.co
            for i in range(3):mins[i]=min(mins[i],float(co[i]));maxs[i]=max(maxs[i],float(co[i]))
    finally:ev.to_mesh_clear()
missing=[im.filepath for im in bpy.data.images if im.source=="FILE" and im.filepath and not Path(bpy.path.abspath(im.filepath)).exists()]
sha=hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
integrity={"fresh_process_reopen":True,"asset":str(ASSET_PATH),"sha256":sha,"scene":bpy.context.scene.name,
 "export_collection":asset.name,"object_count":len(objects),"mesh_count":sum(o.type=="MESH" for o in objects),
 "identity_root":True,"bounds_local_axis_major_m":[[mins[i],maxs[i]] for i in range(3)],
 "materialless_meshes":materialless,"invalid_material_meshes":invalid,"missing_external_images":missing,
 "linked_libraries":[l.filepath for l in bpy.data.libraries],"placement_origin_xy_m":[21.32823749544109,-412.2141452954931]}
if materialless or invalid or missing or integrity["linked_libraries"]:raise RuntimeError("Reopened asset failed portability/material checks")

scene=bpy.context.scene;scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG";scene.render.film_transparent=False
scene.view_settings.view_transform="AgX";scene.view_settings.look="AgX - Medium High Contrast";scene.view_settings.exposure=.55;scene.view_settings.gamma=1
world=bpy.data.worlds.new("SOTAC_R4_Review_World");world.use_nodes=True;scene.world=world
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.34,.38,.43,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.55
setup=bpy.data.collections.new("SOTAC_R4_Temporary_Review_Setup");scene.collection.children.link(setup)
def link(ob):setup.objects.link(ob);return ob
def light(name,kind,loc,target,energy,size=1,color=(1,1,1)):
    dat=bpy.data.lights.new(name,kind);dat.energy=energy
    if kind=="AREA":dat.shape="DISK";dat.size=size;dat.color=color
    else:dat.angle=math.radians(18)
    ob=link(bpy.data.objects.new(name,dat));ob.location=loc
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat("-Z","Y").to_euler();return ob
light("SOTAC_R4_Sun","SUN",(-70,90,100),(0,0,0),2.8)
light("SOTAC_R4_Fill","AREA",(35,-15,55),(0,0,5),3200,42,(1,.86,.72))
ground_mat=bpy.data.materials.new("SOTAC_R4_Review_Concrete");ground_mat.use_nodes=True
ground_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.34,.37,.36,1)
ground_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=.9
ground_mesh=bpy.data.meshes.new("SOTAC_R4_Review_GroundMesh")
ground_mesh.from_pydata([(-100,-100,-.16),(100,-100,-.16),(100,100,-.16),(-100,100,-.16)],[],[(0,1,2,3)])
ground=link(bpy.data.objects.new("SOTAC_R4_Review_Ground",ground_mesh));ground.data.materials.append(ground_mat)
def render(label,loc,target,scale):
    cam_data=bpy.data.cameras.new("SOTAC_R4_Camera_"+label);cam_data.type="ORTHO";cam_data.ortho_scale=scale
    cam=link(bpy.data.objects.new("SOTAC_R4_Camera_"+label,cam_data));cam.location=loc
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler();scene.camera=cam
    scene.render.filepath=str(AUDIT/(label+"_r4.png"));bpy.ops.render.render(write_still=True)
render("exterior_north_entry",(-10,106,33),(-4,6,7),84)
render("exterior_southeast",(74,-80,48),(0,0,7),100)
render("topdown_footprint",(0,0,115),(0,0,0),91)

saved=[]
cut_prefixes=("SOTAC_Stone_Foundation_and_Plinth","SOTAC_Continuous_Brick_Base_Shell",
 "SOTAC_Original_Church_Upper_Walls","SOTAC_New_Church_Addition_Upper_Walls","SOTAC_Office_Classroom_Upper_Walls",
 "SOTAC_Original_Church_Gable_Roof","SOTAC_Original_Church_RidgeCap","SOTAC_Original_Church_Eave_",
 "SOTAC_New_Church_Roof_","SOTAC_Office_Classroom_Roof_","SOTAC_New_Church_Stone_Coping",
 "SOTAC_Office_Wing_Coping","SOTAC_Limestone_BaseBand","SOTAC_R3_Stone_Stringcourse_","SOTAC_R4_Stone_Stringcourse_","SOTAC_R4_Sanctuary_North_GableEnd",
 "SOTAC_Corner_Pilaster","SOTAC_Window_","SOTAC_BellTower_","SOTAC_Belfry_","SOTAC_MainEntry_",
 "SOTAC_Facade_Sign_","SOTAC_Entrance_","SOTAC_Ramp_")
for ob in objects:
    if ob.name.startswith(cut_prefixes):saved.append((ob,ob.hide_render));ob.hide_render=True
truss_hidden=[]
for ob in objects:
    if ob.name.startswith(("SOTAC_R4_SanctuaryTruss_","SOTAC_Sanctuary_Pendant_")):
        truss_hidden.append((ob,ob.hide_render));ob.hide_render=True
render("interior_sanctuary_cutaway",(-10,-20,21),(-11.5,19,3.5),36)
for ob,val in truss_hidden:ob.hide_render=val
# A side-on section shows the gable trusses and the side-wall piers supporting them.
render("interior_sanctuary_structure",(-29,-2,18),(-11.5,12,5),42)
# Hide the ground-floor shell furniture for this plan-like view, leaving the upstairs room layout,
# furniture, stairwell opening and stairs visible together.
for ob in objects:
    if ob.name.startswith(("SOTAC_Classroom_Table_","SOTAC_Classroom_Chair_","SOTAC_R4_Classroom_R1_")):
        saved.append((ob,ob.hide_render));ob.hide_render=True
render("interior_classroom_cutaway",(43,-56,37),(1,-23.5,3.5),48)
for ob,val in saved:ob.hide_render=val

integrity["renders"]=[str(AUDIT/(name+"_r4.png")) for name in ("exterior_north_entry","exterior_southeast","topdown_footprint","interior_sanctuary_cutaway","interior_sanctuary_structure","interior_classroom_cutaway")]
(AUDIT/"independent_reopen_r4.json").write_text(json.dumps(integrity,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
for ob in list(setup.objects):
    data=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
    if data and data.users==0:
        if data.bl_rna.identifier=="Camera":bpy.data.cameras.remove(data)
        elif data.bl_rna.identifier.endswith("Light"):bpy.data.lights.remove(data)
        elif data.bl_rna.identifier=="Mesh":bpy.data.meshes.remove(data)
bpy.data.collections.remove(setup)
print(json.dumps(integrity,indent=2,ensure_ascii=False))


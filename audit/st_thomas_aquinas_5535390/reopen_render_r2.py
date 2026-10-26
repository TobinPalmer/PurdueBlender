"""Fresh reopen, material correction, and balanced review renders for R2."""
from __future__ import annotations
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
AUDIT=Path(__file__).resolve().parent
ASSET=ROOT/"modular/buildings/massing_st_thomas_aquinas_5535390.blend"
asset=bpy.data.collections.get("Asset_massing_st_thomas_aquinas_5535390")
scene=bpy.context.scene
if asset is None or scene.name!="Building_massing_st_thomas_aquinas_5535390":
    raise RuntimeError("Stable building scene or asset collection missing on fresh reopen")

# Improve the node-based brick palette and keep brick relief visible without noisy vertical striation.
brick=bpy.data.materials.get("SOTAC_Procedural_Red_Brick")
if brick and brick.use_nodes:
    nodes=brick.node_tree.nodes; links=brick.node_tree.links
    bsdf=nodes.get("Principled BSDF"); tex=next((n for n in nodes if n.bl_idname=="ShaderNodeTexBrick"),None)
    bump=next((n for n in nodes if n.bl_idname=="ShaderNodeBump"),None)
    if tex:
        tex.inputs["Color1"].default_value=(0.31,0.065,0.028,1)
        tex.inputs["Color2"].default_value=(0.19,0.031,0.017,1)
        tex.inputs["Mortar"].default_value=(0.105,0.072,0.05,1)
        tex.inputs["Scale"].default_value=0.85
        tex.inputs["Brick Width"].default_value=0.42
        tex.inputs["Row Height"].default_value=0.11
        tex.inputs["Mortar Size"].default_value=0.012
        # Feed subtle brick relief; leave the visible color mostly controlled by the red masonry texture.
    if bump:
        bump.inputs["Strength"].default_value=0.12
        bump.inputs["Distance"].default_value=0.028
    if bsdf:
        bsdf.inputs["Roughness"].default_value=0.88

# The 3D text was mirrored on the north facade in the first review image.
sign=bpy.data.objects.get("SOTAC_Facade_Sign_Lettering")
if sign:
    sign.scale.x=-abs(sign.scale.x)

for name,col in (("SOTAC_Tower_Brick",(0.24,0.045,0.025)),
                 ("SOTAC_Interior_Exposed_Brick",(0.30,0.095,0.055)),
                 ("SOTAC_Warm_Oak",(0.26,0.115,0.038)),
                 ("SOTAC_Pew_Oak",(0.34,0.19,0.075)),
                 ("SOTAC_Limestone_Trim",(0.52,0.45,0.34)),
        ("SOTAC_Stone_Base",(0.30,0.29,0.26))):
    m=bpy.data.materials.get(name)
    if m:
        m.diffuse_color=(*col,1)
        if m.use_nodes and m.node_tree.nodes.get("Principled BSDF"):
            m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(*col,1)

# Save only asset material edits; inspection cameras, lights, ground and stage are temporary.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()

scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"; scene.render.film_transparent=False
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
scene.view_settings.exposure=0.55
scene.view_settings.gamma=1.0
world=bpy.data.worlds.new("SOTAC_R2_Review_World")
scene.world=world; world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.24,0.29,0.36,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.55

setup=bpy.data.collections.new("SOTAC_R2_Temporary_Review_Setup")
scene.collection.children.link(setup)
def link_obj(obj): setup.objects.link(obj); return obj
def area(name,loc,target,energy,size,color):
    data=bpy.data.lights.new(name,"AREA"); data.energy=energy; data.shape="DISK"; data.size=size; data.color=color
    o=link_obj(bpy.data.objects.new(name,data)); o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
    return o
def camera(name,loc,target,ortho):
    d=bpy.data.cameras.new(name); d.type="ORTHO"; d.ortho_scale=ortho
    o=link_obj(bpy.data.objects.new(name,d));o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler();scene.camera=o
    return o
sun_data=bpy.data.lights.new("SOTAC_R2_Sun","SUN"); sun_data.energy=2.8; sun_data.angle=math.radians(18)
sun=link_obj(bpy.data.objects.new("SOTAC_R2_Sun",sun_data)); sun.location=(-70,90,100)
sun.rotation_euler=(Vector((0,0,0))-sun.location).to_track_quat("-Z","Y").to_euler()
area("SOTAC_R2_Soft_Fill",(35,-15,55),(0,0,5),3200,42,(1.0,0.85,0.70))
ground_mat=bpy.data.materials.new("SOTAC_R2_Review_Concrete");ground_mat.diffuse_color=(0.23,0.25,0.24,1);ground_mat.use_nodes=True
ground_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(0.23,0.25,0.24,1)
ground_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=0.9
me=bpy.data.meshes.new("SOTAC_R2_Review_GroundMesh");me.from_pydata([(-100,-100,-0.14),(100,-100,-0.14),(100,100,-0.14),(-100,100,-0.14)],[],[(0,1,2,3)])
ground=link_obj(bpy.data.objects.new("SOTAC_R2_Review_Ground",me));ground.data.materials.append(ground_mat)

def render(label,loc,target,scale):
    camera("SOTAC_R2_Camera_"+label,loc,target,scale)
    scene.render.filepath=str(AUDIT/(label+"_r2.png"))
    bpy.ops.render.render(write_still=True)
render("exterior_north_entry",(-10,106,33),(-4,6,7),84)
render("exterior_southeast",(74,-80,48),(0,0,7),100)
render("topdown_footprint",(0,0,115),(0,0,0),91)

# Interior cutaways hide enclosing architecture only for review; the saved model stays intact.
objects=list(asset.all_objects);hidden=[]
for ob in objects:
    if ob.name.startswith(("SOTAC_Stone_Foundation_and_Plinth","SOTAC_Continuous_Brick_Base_Shell",
       "SOTAC_Original_Church_Upper_Walls","SOTAC_New_Church_Addition_Upper_Walls",
       "SOTAC_Office_Classroom_Upper_Walls","SOTAC_Original_Church_Gable_Roof",
       "SOTAC_Original_Church_RidgeCap","SOTAC_Original_Church_Eave_","SOTAC_New_Church_Roof_",
       "SOTAC_Office_Classroom_Roof_","SOTAC_New_Church_Roof_Parapet","SOTAC_Office_Classroom_Coping",
       "SOTAC_Office_Wing_Coping","SOTAC_Limestone_BaseBand","SOTAC_Corner_Pilaster","SOTAC_Window_",
       "SOTAC_BellTower_","SOTAC_CeilingTruss_","SOTAC_Office_Interior_Partition_")):
        hidden.append((ob,ob.hide_render));ob.hide_render=True
render("interior_sanctuary_cutaway",(21,-20,9),(9,12,4.2),42)
render("interior_classroom_cutaway",(-5,-40,7),(0,-21,1.5),18)
for ob,value in hidden:ob.hide_render=value

report={"status":"saved_and_freshly_reopened","asset":str(ASSET),"sha256":sha,
        "stable_collection":asset.name,"identity_root":True,"object_count":len(asset.all_objects),
        "renders":[str(AUDIT/(n+"_r2.png")) for n in ["exterior_north_entry","exterior_southeast","topdown_footprint","interior_sanctuary_cutaway","interior_classroom_cutaway"]],
        "setup_excluded_from_asset":True}
(AUDIT/"r2_reopen_render_record.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
# Do not store review setup or altered temporary render state in the library.
for ob in list(setup.objects):
    data=ob.data
    bpy.data.objects.remove(ob,do_unlink=True)
    if data and data.users==0:
        if data.bl_rna.identifier=="Camera": bpy.data.cameras.remove(data)
        elif data.bl_rna.identifier.endswith("Light"): bpy.data.lights.remove(data)
        elif data.bl_rna.identifier=="Mesh": bpy.data.meshes.remove(data)
bpy.data.collections.remove(setup)
print(json.dumps(report,indent=2))

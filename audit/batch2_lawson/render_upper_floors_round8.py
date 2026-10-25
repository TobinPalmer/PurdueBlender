"""Render plan-derived upper floors from a reopened saved Lawson asset."""
import bpy
from mathutils import Vector

ASSET=r"C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lawson_hall.blend"
OUT=r"C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson"
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=24
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
scene.view_settings.exposure=1.15
scene.render.film_transparent=False
scene.world.use_nodes=True
scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value=(0.18,0.20,0.22,1)
scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.32

def area(name,loc,power,size,target):
    bpy.ops.object.light_add(type="AREA",location=loc)
    ob=bpy.context.object;ob.name="LWSN_R8_TEMP_"+name;ob.data.energy=power;ob.data.shape="DISK";ob.data.size=size
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat("-Z","Y").to_euler()
def camera(name,loc,target,path):
    bpy.ops.object.camera_add(location=loc)
    cam=bpy.context.object;cam.name="LWSN_R8_TEMP_"+name;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.type="ORTHO";cam.data.ortho_scale=100;scene.camera=cam
    scene.render.resolution_x=1500;scene.render.resolution_y=1250;scene.render.filepath=path
    bpy.ops.render.render(write_still=True)

excluded_prefix=("LWSN_R8_TEMP_",)
hide_names={"LWSN_Exterior_Brick","LWSN_Limestone_Bands","LWSN_Window_Glazing","LWSN_Window_Frames","LWSN_Rotunda_Curtain_Glass","LWSN_Rotunda_Spandrel_Panels","LWSN_Rotunda_Mullions","LWSN_Rotunda_Parapet_Coping","LWSN_Roof_Surface","LWSN_Mechanical_Penthouse","LWSN_Rooftop_Mechanical_Units","LWSN_First_Floor_Surface","LWSN_Foundation_Base"}
for ob in list(bpy.data.objects):
    if ob.name in hide_names or ob.name.startswith("LWSN_R3_") or ob.name.startswith("LWSN_Plan_") or ob.name.startswith("LWSN_1142_") or ob.name.startswith("LWSN_Office_") or ob.name.startswith("LWSN_Commons_") or ob.name.startswith("LWSN_R5_") or ob.name.startswith("LWSN_R7_"):
        ob.hide_render=True
    if ob.type=="LIGHT": ob.hide_render=True

# Temporary plan-view lighting for interpretable wall traces.
area("Plan_Key",(5,-12,38),7800,48,(0,-2,5))
area("Plan_Fill",(-28,24,28),5200,36,(0,-2,5))
# Hide the rest of the library so this is a clean view of the two registered
# source-plan layers, without exterior site or L1 furniture obscuring them.
for ob in list(bpy.data.objects):
    if ob.name in {"AssetRoot_lawson_hall"} or ob.name.startswith("LWSN_R8_Floor_") or ob.name.startswith("LWSN_R8_TEMP_"):
        continue
    ob.hide_render=True
for ob in bpy.data.objects:
    if ob.name.startswith("LWSN_R8_Floor_3_") or "Roof_Surface_With_L3_Terrace" in ob.name:
        ob.hide_render=True
camera("Floor_2_Plan_View",(62,-97,85),(0,-2,4),OUT+r"/floor2_layout_round8.png")
for ob in bpy.data.objects:
    if ob.name.startswith("LWSN_R8_Floor_2_"): ob.hide_render=True
    if ob.name.startswith("LWSN_R8_Floor_3_"): ob.hide_render=False
camera("Floor_3_Plan_View",(62,-97,85),(0,-2,7.2),OUT+r"/floor3_layout_round8.png")
print("Rendered floor plans 2 and 3 from saved/reopened asset")

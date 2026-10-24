"""Render R6 exterior and atrium cutaway without saving temporary scene edits."""
import bpy, math, os
from mathutils import Vector

ROOT = r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET = os.path.join(ROOT,"modular","buildings","neil_armstrong_hall.blend")
OUT = os.path.join(ROOT,"audit","complete_neil_armstrong","renders_r6")
os.makedirs(OUT,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=32
scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
scene.view_settings.exposure=-0.35
scene.view_settings.gamma=1.0
scene.render.film_transparent=False
world=scene.world or bpy.data.worlds.new("Neil_R6_Review_World")
scene.world=world; world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=="BACKGROUND")
bg.inputs["Color"].default_value=(0.16,0.22,0.30,1)
bg.inputs["Strength"].default_value=0.28

def camera(name,loc,target,ortho_scale):
    data=bpy.data.cameras.new(name+"_Data"); obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj)
    obj.location=loc; obj.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat("-Z","Y").to_euler()
    data.type="ORTHO"; data.ortho_scale=ortho_scale; data.clip_end=1000
    return obj
def area(name,loc,target,energy,size):
    data=bpy.data.lights.new(name+"_Data","AREA"); obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj)
    obj.location=loc; data.energy=energy; data.shape="DISK"; data.size=size
    obj.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat("-Z","Y").to_euler()
    return obj
lights=[area("R6_Key",(-90,-25,100),(0,-8,8),2300,60),
        area("R6_Fill",(80,75,65),(0,-8,8),1250,55)]
oldcam=scene.camera
ext=camera("R6_Exterior_Northwest",(-125,105,49),(0,-9,8),172)
scene.camera=ext; scene.render.filepath=os.path.join(OUT,"exterior_northwest_r6.png")
bpy.ops.render.render(write_still=True)

# The cutaway is a render-only visibility treatment. It demonstrates the two
# documented bridge levels but does not claim a complete or measured route.
hide=[]
keep={"ARMS_Balcony_Level2_Slab","ARMS_Balcony_Level2_GlassRail","ARMS_Balcony_Level2_Handrail",
      "ARMS_Balcony_Level3_Slab","ARMS_Balcony_Level3_GlassRail","ARMS_Balcony_Level3_Handrail",
      }
for obj in bpy.data.collections["Asset_neil_armstrong_hall"].objects:
    if obj.name not in keep:
        hide.append((obj,obj.hide_render)); obj.hide_render=True
inside=camera("R6_Atrium_Bridge_Section",(0,5,7.5),(0,-12,7.5),72)
scene.camera=inside
bg.inputs["Color"].default_value=(0.12,0.16,0.22,1); bg.inputs["Strength"].default_value=0.26
for light in lights:
    light.data.energy *= 0.75
scene.view_settings.exposure=-0.15
scene.render.filepath=os.path.join(OUT,"atrium_bridges_section_r6.png")
# The saved asset's safety-glass shader is transparent. For this isolated
# proof render only, use a tinted opaque display proxy so rail locations are
# legible; this override is not saved back into the asset.
render_glass=bpy.data.materials.new("R6_Render_Only_Rail_Glass")
render_glass.use_nodes=True
render_bs=next(n for n in render_glass.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
render_bs.inputs["Base Color"].default_value=(0.23,0.42,0.50,1)
render_bs.inputs["Metallic"].default_value=0.05
render_bs.inputs["Roughness"].default_value=0.32
for name in ("ARMS_Balcony_Level2_GlassRail","ARMS_Balcony_Level3_GlassRail"):
    obj=bpy.data.objects[name]
    obj.data.materials.clear(); obj.data.materials.append(render_glass)
bpy.ops.render.render(write_still=True)
for obj,value in hide: obj.hide_render=value
for obj in lights+[ext,inside]: bpy.data.objects.remove(obj,do_unlink=True)
scene.camera=oldcam
print("R6 review renders written to",OUT)

"""Render a whole-building R9 view and an atrium-context feature section."""
import bpy, os, math
from mathutils import Vector
ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET=os.path.join(ROOT,"modular","buildings","neil_armstrong_hall.blend")
OUT=os.path.join(ROOT,"audit","complete_neil_armstrong","renders_r9")
os.makedirs(OUT,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
scene.render.engine="CYCLES"; scene.cycles.samples=36
scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.view_settings.view_transform="AgX"; scene.view_settings.look="AgX - Medium High Contrast"
scene.view_settings.exposure=-0.25; scene.view_settings.gamma=1.0
scene.render.film_transparent=False
world=scene.world or bpy.data.worlds.new("Neil_R9_Review_World")
scene.world=world; world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=="BACKGROUND")
bg.inputs["Color"].default_value=(0.20,0.25,0.32,1); bg.inputs["Strength"].default_value=0.25

def camera(name,loc,target,scale):
    data=bpy.data.cameras.new(name+"_Data"); obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj)
    obj.location=loc; obj.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat("-Z","Y").to_euler()
    data.type="ORTHO"; data.ortho_scale=scale; data.clip_end=1200
    return obj
def area(name,loc,target,power,size):
    data=bpy.data.lights.new(name+"_Data","AREA"); obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj)
    obj.location=loc; data.energy=power; data.shape="DISK"; data.size=size
    obj.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat("-Z","Y").to_euler(); return obj

old_camera=scene.camera
lights=[area("R9_Exterior_Key",(-80,-75,130),(0,-8,9),2600,60),
        area("R9_Exterior_Fill",(95,65,85),(0,-8,9),900,75)]
exterior=camera("R9_Envelope_Oblique",(-145,130,125),(0,-6,8),205)
scene.camera=exterior; scene.render.filepath=os.path.join(OUT,"exterior_lidar_silhouette_r9.png")
bpy.ops.render.render(write_still=True)

# Registered overhead roof review view: same local frame, no master marker changes.
topdown=camera("R9_Roof_Plan_Review",(0,-8,190),(0,-8,0),210)
scene.camera=topdown; scene.render.filepath=os.path.join(OUT,"roof_registered_plan_r9.png")
bpy.ops.render.render(write_still=True)

# Approximate eye-level review from the geotagged 2016 camera point. It is a
# vantage check, not a recovered camera bearing.
photo_view=camera("R9_Geotag_Approx_View",(-154.0,47.3,1.7),(0.0,-8.0,8.5),180)
photo_view.data.type="PERSP"; photo_view.data.lens=48; photo_view.data.sensor_width=36
scene.camera=photo_view; scene.view_settings.exposure=-0.4
scene.render.filepath=os.path.join(OUT,"facade_geotag_approx_r9.png")
bpy.ops.render.render(write_still=True)

# Isolated section context. The south edge is opened for the view; the remaining
# modeled curtain wall and roof glazing enclose the bridges. The opaque glass,
# material overrides, and hidden-object set are render-only; none are saved.
collection=bpy.data.collections["Asset_neil_armstrong_hall"]
keep={"ARMS_Atrium_Terrazzo_Floor","ARMS_Atrium_Skylight_Glazing",
      "ARMS_Balcony_Level2_Slab","ARMS_Balcony_Level2_GlassRail","ARMS_Balcony_Level2_Handrail",
      "ARMS_Balcony_Level3_Slab","ARMS_Balcony_Level3_GlassRail","ARMS_Balcony_Level3_Handrail"}
keep.update(o.name for o in collection.objects if o.name.startswith("ARMS_Curtain_Glass_Bay_"))
keep.update(o.name for o in collection.objects if o.name.startswith("ARMS_Roof_Steel_Truss_"))
# The existing GIS-footprint floor proxy is too broad for an atrium-only view.
# Replace it with a temporary neutral display plane whose size is deliberately
# not used as a floor-plan claim.
keep.discard("ARMS_Atrium_Terrazzo_Floor")
hidden=[]
for obj in collection.objects:
    if obj.name not in keep:
        hidden.append((obj,obj.hide_render)); obj.hide_render=True
# Open a small render-only camera reveal through the central glazed face so
# the bridge ends are visible; the side curtain remains as the enclosure cue.
for name in ("ARMS_Curtain_Glass_Bay_7","ARMS_Curtain_Glass_Bay_8","ARMS_Curtain_Glass_Bay_9"):
    obj=bpy.data.objects.get(name)
    if obj:
        hidden.append((obj,obj.hide_render)); obj.hide_render=True

# Render-only clay materials make the original spatial objects readable under
# a controlled studio light, especially translucent glass rails and the GIS
# footprint-based floor placeholder. They are never written into the asset.
def render_material(name,color,roughness=0.5,metal=0.0):
    mat=bpy.data.materials.new(name); mat.diffuse_color=(*color,1); mat.use_nodes=True
    bs=next(n for n in mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    bs.inputs["Base Color"].default_value=(*color,1); bs.inputs["Roughness"].default_value=roughness; bs.inputs["Metallic"].default_value=metal
    return mat
clay=render_material("R9_RenderOnly_ConcreteClay",(0.56,0.56,0.54),0.72)
glass=render_material("R9_RenderOnly_GlassDisplay",(0.18,0.35,0.44),0.28,0.04)
roof_glass=render_material("R9_RenderOnly_SkylightDisplay",(0.10,0.19,0.25),0.32,0.0)
rail=render_material("R9_RenderOnly_RailDisplay",(0.25,0.48,0.56),0.25,0.05)
bridge_mat=render_material("R9_RenderOnly_BridgeConcrete",(0.62,0.60,0.55),0.74)
for mat in (clay,bridge_mat):
    bs=next(n for n in mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    if "Emission Color" in bs.inputs:
        bs.inputs["Emission Color"].default_value=bs.inputs["Base Color"].default_value
        bs.inputs["Emission Strength"].default_value=0.18
render_overrides=[]
for name,mat in (("ARMS_Atrium_Skylight_Glazing",roof_glass),):
    obj=bpy.data.objects[name]; render_overrides.append((obj,list(obj.data.materials)))
    obj.data.materials.clear(); obj.data.materials.append(mat)
    # The GIS floor mesh originally has a second base material slot; remap all
    # faces to the render-only clay slot to avoid unassigned black faces.
    for poly in obj.data.polygons: poly.material_index=0
for obj in collection.objects:
    if obj.name.startswith("ARMS_Curtain_Glass_Bay_"):
        render_overrides.append((obj,list(obj.data.materials))); obj.data.materials.clear(); obj.data.materials.append(glass)
for name in ("ARMS_Balcony_Level2_GlassRail","ARMS_Balcony_Level3_GlassRail"):
    obj=bpy.data.objects[name]; render_overrides.append((obj,list(obj.data.materials)))
    obj.data.materials.clear(); obj.data.materials.append(rail)
for name in ("ARMS_Balcony_Level2_Slab","ARMS_Balcony_Level3_Slab"):
    obj=bpy.data.objects[name]; render_overrides.append((obj,list(obj.data.materials)))
    obj.data.materials.clear(); obj.data.materials.append(bridge_mat)
# This neutral render-only plane provides a height reference for the two bridge
# levels. It is display staging only and does not assert an atrium-floor plan.
floor_mesh=bpy.data.meshes.new("R9_RenderOnly_Atrium_Stage_Mesh")
floor_mesh.from_pydata([(-34,-30,0.0),(30,-30,0.0),(30,8,0.0),(-34,8,0.0)],[],[(0,1,2,3)])
floor_mesh.materials.append(clay); floor_mesh.update()
floor_stage=bpy.data.objects.new("R9_RenderOnly_Atrium_Stage",floor_mesh); scene.collection.objects.link(floor_stage)

bg.inputs["Color"].default_value=(0.18,0.22,0.28,1); bg.inputs["Strength"].default_value=0.13
inside_lights=[area("R9_Atrium_Key",(-25,-22,30),(0,-10,8),1550,32),
               area("R9_Atrium_Fill",(28,-3,23),(0,-10,8),1050,35)]
inside=camera("R9_Atrium_Enclosure_Section",(0,1.5,12.0),(0,-13,8.5),72)
scene.camera=inside; scene.view_settings.exposure=0.0
scene.render.filepath=os.path.join(OUT,"atrium_bridges_enclosure_r9.png")
bpy.ops.render.render(write_still=True)

for obj,materials in render_overrides:
    obj.data.materials.clear()
    for mat in materials: obj.data.materials.append(mat)
for obj,value in hidden: obj.hide_render=value
for obj in lights+inside_lights+[exterior,inside,floor_stage]: bpy.data.objects.remove(obj,do_unlink=True)
scene.camera=old_camera
print("R9 review renders written to",OUT)



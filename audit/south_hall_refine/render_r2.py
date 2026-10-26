import bpy, math, os
from mathutils import Vector

ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET=os.path.join(ROOT,"modular","buildings","south_hall.blend")
OUT=os.path.join(ROOT,"audit","south_hall_refine")
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
asset=bpy.data.collections["Asset_south_hall"]
geo=next(o for o in asset.all_objects if o.name=="SouthHall_GIS_GroundFloor_Glass_Podium")
pts=[geo.matrix_world @ Vector(v) for v in geo.bound_box]
mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
target=Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,13.0))

# Simple daylight rig and neutral paving for review renders only.
world=scene.world or bpy.data.worlds.new("SouthHall_R1_ReviewWorld")
scene.world=world; world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=="BACKGROUND")
bg.inputs["Color"].default_value=(.38,.50,.65,1); bg.inputs["Strength"].default_value=.16
sun_data=bpy.data.lights.new("SouthHall_R1_ReviewSun","SUN"); sun=bpy.data.objects.new("SouthHall_R1_ReviewSun",sun_data); scene.collection.objects.link(sun)
sun.rotation_euler=(math.radians(25),math.radians(-18),math.radians(-30)); sun.data.energy=1.0
area_data=bpy.data.lights.new("SouthHall_R1_ReviewArea","AREA"); area=bpy.data.objects.new("SouthHall_R1_ReviewArea",area_data); scene.collection.objects.link(area)
area.location=(30,-70,48); area.data.energy=180; area.data.shape="DISK"; area.data.size=55
area.rotation_euler=(target-area.location).to_track_quat("-Z","Y").to_euler()
ground_mat=bpy.data.materials.new("SouthHall_R1_Review_Paving"); ground_mat.diffuse_color=(.29,.30,.28,1); ground_mat.use_nodes=True
ground_bsdf=next(n for n in ground_mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
ground_bsdf.inputs["Base Color"].default_value=(.29,.30,.28,1); ground_bsdf.inputs["Roughness"].default_value=.9
bpy.ops.mesh.primitive_plane_add(size=360,location=(0,0,-.34)); plane=bpy.context.object; plane.name="SouthHall_R1_Review_Ground"; plane.data.materials.append(ground_mat)

scene.render.engine="CYCLES"; scene.cycles.samples=32
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
scene.view_settings.exposure=0; scene.view_settings.gamma=1
cam_data=bpy.data.cameras.new("SouthHall_R1_ReviewCamera"); cam=bpy.data.objects.new("SouthHall_R1_ReviewCamera",cam_data); scene.collection.objects.link(cam); scene.camera=cam

def aim(camera,pt): camera.rotation_euler=(Vector(pt)-camera.location).to_track_quat("-Z","Y").to_euler()
cam.location=(85,-87,5.2); aim(cam,(10,-30,12.0)); cam.data.lens=42
scene.render.filepath=os.path.join(OUT,"south_hall_human_scale_east_entry_r2.png")
bpy.ops.render.render(write_still=True)

cam.location=(145,-160,112); aim(cam,target); cam.data.lens=45
scene.render.filepath=os.path.join(OUT,"south_hall_oblique_full_r2.png")
bpy.ops.render.render(write_still=True)

# Schematic amenity cutaway/top-down view: hide only the exterior envelope for this review frame.
for name in ["SouthHall_GIS_GroundFloor_Glass_Podium","SouthHall_GIS_Residential_Brick_Envelope","SouthHall_Roof_Parapet_Estimated","SouthHall_Roof_Slab","SouthHall_Roof_Membrane_Seams_LowConfidence_6m","SouthHall_Repetitive_Residential_Windows","SouthHall_GroundFloor_Curtainwall_Mullions","SouthHall_Estimated_OneStorey_North_DiningLink_Mullions","SouthHall_FullHeight_Glazed_Atrium_Bay_Estimated","SouthHall_MacArthur_Glass_Entry_Vestibule_and_Canopy","SouthHall_Entry_Stone_Pylon_Estimated"]:
    ob=bpy.data.objects.get(name)
    if ob: ob.hide_render=True
for ob in asset.all_objects:
    if ob and (ob.name.startswith("SouthHall_Level") and ob.name!="SouthHall_Level01_Terrazzo_Slab" or ob.name=="SouthHall_Roof_Slab"):
        ob.hide_render=True
# The nine learning labs and bedroom remain in the asset as schematic room modules;
# the ground-floor review frame focuses on connected public circulation instead.
for name in ["SouthHall_Schematic_DataMine_Lab_Glass_Partitions_01_09","SouthHall_Schematic_DataMine_Labs_Furniture_01_09","SouthHall_Schematic_Representative_Double_Room_Walls_Furnishings"]:
    ob=bpy.data.objects.get(name)
    if ob: ob.hide_render=True
cam.data.type="ORTHO"; cam.data.ortho_scale=110; cam.location=(-10,-18,100); aim(cam,(-10,-18,0))
scene.render.filepath=os.path.join(OUT,"south_hall_schematic_ground_floor_cutaway_r2.png")
bpy.ops.render.render(write_still=True)
print("RENDERS",mn,mx)

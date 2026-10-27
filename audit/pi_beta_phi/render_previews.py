import bpy, os, math
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET = os.path.join(ROOT, "modular", "buildings", "massing_house_301838781_891384f.blend")
OUT = os.path.join(ROOT, "audit", "pi_beta_phi")
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=1500
scene.render.resolution_y=1050
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.resolution_percentage=80
scene.view_settings.view_transform="AgX"
world=scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.34,0.42,0.54,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.38

def aim(obj, target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def area(name, location, power, size, color=(1.0,0.88,0.75)):
    data=bpy.data.lights.new(name,"AREA"); data.energy=power; data.shape="DISK"; data.size=size; data.color=color
    obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj); obj.location=location; aim(obj,(0,0,3.5)); return obj

area("Warm facade key",(-18,-32,30),6500,22)
area("Cool roof fill",(20,15,28),3800,20,(0.72,0.82,1.0))
area("Soft entry fill",(0,-22,8),1300,12)

camdata=bpy.data.cameras.new("PiPhi_preview_camera")
cam=bpy.data.objects.new("PiPhi_preview_camera",camdata); scene.collection.objects.link(cam); scene.camera=cam
camdata.lens=45

def render_view(name,location,target):
    cam.location=location; aim(cam,target)
    scene.render.filepath=os.path.join(OUT,name+".png")
    bpy.ops.render.render(write_still=True)

render_view("view_front",(0,-58,11),(0,-2,4.2))
render_view("view_three_quarter",(29,-43,17),(0,-2,4.0))

# Conceptual interior cutaway: shell and roof surfaces are hidden only for this
# review render. Room locations remain explicitly unverified.
for obj in bpy.data.objects:
    if obj.name in ("House_301838781", "PiPhi_white_perimeter_cornice", "PiPhi_flat_roof_surface_estimated", "PiPhi_roof_hatch") or obj.name.startswith(("PiPhi_roof_vent", "PiPhi_facade_", "PiPhi_attic_", "PiPhi_portico_", "PiPhi_column_", "PiPhi_balcony", "PiPhi_baluster", "PiPhi_entry_", "PiPhi_house_letters", "PiPhi_address")):
        obj.hide_render=True
    if obj.name in ("PiPhi_interior_floor_2", "PiPhi_interior_floor_3") or (obj.name.startswith(("PiPhi_hall_partition_", "PiPhi_room_partition_", "PiPhi_room_door_", "PiPhi_bed_", "PiPhi_headboard_")) and "_0_" not in obj.name):
        obj.hide_render=True
camdata.lens=44
render_view("view_interior_cutaway",(0,-32,11),(0,-2,1.6))
print("Rendered front, three-quarter and conceptual interior cutaway previews to",OUT)

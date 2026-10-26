"""Fresh R11 evidence renders from the saved candidate."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]
here=Path(__file__).resolve().parent
asset=root/"modular/buildings/rawls_hall.blend"
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
for obj in bpy.data.objects:
    if obj.type=="LIGHT": obj.hide_render=True
world=bpy.data.worlds.get("RAWL_R11_Review_World") or bpy.data.worlds.new("RAWL_R11_Review_World")
scene.world=world; world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.48,0.55,0.65,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.62
sun_data=bpy.data.lights.new("RAWL_R11_Review_Sun","SUN"); sun_data.energy=1.0
sun=bpy.data.objects.new("RAWL_R11_Review_Sun",sun_data); scene.collection.objects.link(sun)
sun.rotation_euler=(math.radians(31),math.radians(-26),math.radians(-22))
sun.visible_glossy=False
# Render-only diffuse fill keeps the schematic tiered desks and chair count
# readable through tinted glass. This is not a claimed installed room fixture.
fill_data=bpy.data.lights.new("RAWL_R11_RenderOnly_Classroom_Fill","AREA")
fill_data.energy=4200
fill_data.shape="RECTANGLE"; fill_data.size=8.0; fill_data.size_y=6.0
fill_data.color=(1.0,0.91,0.78)
fill_data.specular_factor=0.0
fill=bpy.data.objects.new("RAWL_R11_RenderOnly_Classroom_Fill",fill_data)
scene.collection.objects.link(fill)
fill.location=(33.0,2.0,4.2)
fill.rotation_euler=(Vector((32.6,1.68,0.55))-fill.location).to_track_quat("-Z","Y").to_euler()
fill.visible_glossy=False
scene.view_settings.view_transform="AgX"

def camera(name,loc,target,ortho=None,lens=45):
    data=bpy.data.cameras.new(name); obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj)
    obj.location=loc; obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    if ortho is not None: data.type="ORTHO"; data.ortho_scale=ortho
    else: data.type="PERSP"; data.lens=lens
    return obj

glass=bpy.data.objects["RAWL_SE_Diagonal_CurtainWall_Glass"]
poly=glass.data.polygons[2]
pane_pts=[glass.matrix_world@glass.data.vertices[i].co for i in poly.vertices]
pane_center=sum(pane_pts,Vector())/len(pane_pts)
normal=(glass.matrix_world.to_3x3()@poly.normal).normalized()
screens=[bpy.data.objects[n].matrix_world.translation.copy() for n in ["RAWL_1086_R10_Schematic_Projection_Surface_01","RAWL_1086_R10_Schematic_Projection_Surface_02"]]
screen_target=sum(screens,Vector())/len(screens)
screen_target.z += 0.20
view_dir=(screen_target-pane_center).normalized()
cam=camera("R11_SE_Through_Glass_Readability",pane_center-view_dir*5.2,screen_target,None,42)
scene.camera=cam
scene.render.resolution_x=1080; scene.render.resolution_y=810
scene.render.filepath=str(here/"se_curtainwall_through_glass_round11.png")
bpy.ops.render.render(write_still=True)

# Full facade comparison render; R11's changes are confined to the classroom and glazing shader.
pane_centers=[]
for p in glass.data.polygons:
    pane_centers.append(sum((glass.matrix_world@glass.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices))
facade_center=sum(pane_centers,Vector())/len(pane_centers)+Vector((0,0,3.5))
cam2=camera("R11_SE_Facade_Review",facade_center-normal*67+Vector((0,0,5)),facade_center,62)
scene.camera=cam2
scene.cycles.samples=16
scene.render.resolution_x=1200; scene.render.resolution_y=750
scene.render.filepath=str(here/"se_curtainwall_full_round11.png")
bpy.ops.render.render(write_still=True)
print(json.dumps({"asset":str(asset),"through_glass":"se_curtainwall_through_glass_round11.png","pane_index":2,"screen_target":[round(v,4) for v in screen_target],"render_engine":scene.render.engine},indent=2))

"""Render R10 Rawls SE elevation and through-glass room evidence."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
asset=Path(__file__).with_name('rawls_hall_r10_candidate.blend')
bpy.ops.wm.open_mainfile(filepath=str(asset)); scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=48; scene.cycles.use_denoising=True
scene.render.resolution_x=1440; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
for obj in bpy.data.objects:
 if obj.type=='LIGHT': obj.hide_render=True
world=bpy.data.worlds.get('RAWL_R10_Review_World') or bpy.data.worlds.new('RAWL_R10_Review_World')
scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.55,0.62,0.72,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.58
sun_data=bpy.data.lights.new('RAWL_R10_Review_Sun','SUN'); sun_data.energy=1.5
sun=bpy.data.objects.new('RAWL_R10_Review_Sun',sun_data); scene.collection.objects.link(sun)
sun.rotation_euler=(math.radians(28),math.radians(-34),math.radians(-35))
scene.view_settings.view_transform='AgX'
def camera(name,loc,target,ortho=None,lens=55):
 data=bpy.data.cameras.new(name); obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj)
 obj.location=loc; obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
 if ortho is not None: data.type='ORTHO'; data.ortho_scale=ortho
 else: data.type='PERSP'; data.lens=lens
 return obj
glass=bpy.data.objects['RAWL_SE_Diagonal_CurtainWall_Glass']; p=glass.data.polygons[0]
pts=[glass.matrix_world@glass.data.vertices[i].co for i in p.vertices]
normal=(glass.matrix_world.to_3x3()@p.normal).normalized()
centers=[sum((glass.matrix_world@glass.data.vertices[i].co for i in poly.vertices),Vector())/4 for poly in glass.data.polygons]
target=sum(centers,Vector())/len(centers)+Vector((0,0,3.5))
cam=camera('R10_SE_Facade_Review',target-normal*67+Vector((0,0,5)),target,62); scene.camera=cam
scene.render.filepath=str(Path(__file__).with_name('se_curtainwall_full_round10.png'))
bpy.ops.render.render(write_still=True)
pane_center=sum(pts,Vector())/len(pts)
cam2=camera('R10_SE_Through_Glass_Review',pane_center-normal*7+Vector((0,0,0.9)),pane_center+normal*3.5+Vector((0,0,0.1)),None,45)
# Small off-axis softbox; the R9 7 m disk generated an obvious semicircular reflection.
fill_data=bpy.data.lights.new('RAWL_R10_Interior_Fill','AREA'); fill_data.energy=3200
fill_data.specular_factor=0.0
fill_data.shape='RECTANGLE'; fill_data.size=0.8; fill_data.size_y=0.65
fill=bpy.data.objects.new('RAWL_R10_Interior_Fill',fill_data); scene.collection.objects.link(fill)
fill.visible_glossy=False
fill.location=pane_center+normal*8+Vector((0,4,2.8))
fill.rotation_euler=(pane_center+normal*2-fill.location).to_track_quat('-Z','Y').to_euler()
scene.camera=cam2; scene.render.resolution_x=1200; scene.render.resolution_y=900
scene.render.filepath=str(Path(__file__).with_name('se_curtainwall_through_glass_round10.png'))
bpy.ops.render.render(write_still=True)
print(json.dumps({'asset':str(asset),'full_view':str(Path(scene.render.filepath).name),'camera':'R10_SE_Through_Glass_Review','render_only_fill':'small off-axis rectangle at depth, not in building asset'},indent=2))






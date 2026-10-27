import bpy
from mathutils import Vector
from pathlib import Path

root=Path(__file__).resolve().parents[2]
evidence=root/'audit'/'alpha_gamma_rho'
scene=bpy.context.scene
asset=bpy.data.collections['Asset_massing_house_301841253_f0b3be3']
pts=[]
for o in asset.objects:
    if o.type=='MESH':
        for c in o.bound_box:
            pts.append(o.matrix_world @ Vector(c))
cx=(min(p.x for p in pts)+max(p.x for p in pts))/2
cy=(min(p.y for p in pts)+max(p.y for p in pts))/2
maxx=max(p.x for p in pts)

def aim(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
# Give the same materials a brighter review exposure and a soft facade fill.
if scene.world and scene.world.use_nodes:
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=1.15
scene.view_settings.exposure=0.55
for obj in bpy.data.objects:
    if obj.type=='LIGHT' and obj.name.startswith('AGR '): obj.data.energy*=1.75
light_data=bpy.data.lights.new('AGR facade softbox','AREA')
light=bpy.data.objects.new('AGR facade softbox',light_data); scene.collection.objects.link(light)
light.location=(maxx+32,cy-10,21); light_data.energy=12500; light_data.shape='DISK'; light_data.size=30; aim(light,(cx,cy,5))
scene.render.engine='CYCLES'; scene.cycles.samples=32
scene.render.resolution_percentage=100; scene.render.resolution_x=1600; scene.render.resolution_y=1100
scene.render.image_settings.file_format='PNG'
# Near frontal angle puts brick bays, blue shutters, and pediment/arched door at eye level.
data=bpy.data.cameras.new('AGR facade review camera'); cam=bpy.data.objects.new('AGR facade review camera',data); scene.collection.objects.link(cam)
cam.location=(maxx+63,cy-4,17); aim(cam,(cx,cy,5)); data.type='ORTHO'; data.ortho_scale=47; scene.camera=cam
scene.render.filepath=str(evidence/'renders'/'alpha_gamma_rho_facade.png'); bpy.ops.render.render(write_still=True)
# Lower oblique shows the portico, long south facade, roof silhouette, and site approach.
cam.location=(maxx+58,cy-31,24); aim(cam,(cx,cy,5)); data.ortho_scale=49
scene.render.filepath=str(evidence/'renders'/'alpha_gamma_rho_oblique.png'); bpy.ops.render.render(write_still=True)

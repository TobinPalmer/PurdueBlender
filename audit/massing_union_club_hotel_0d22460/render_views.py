import bpy, math, json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
asset=root/'modular/buildings/massing_union_club_hotel_0d22460.blend'
out=root/'audit/massing_union_club_hotel_0d22460/renders'
out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1440;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast'
scene.render.image_settings.color_depth='8'
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.48,0.48,0.48,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.8
# Non-building lighting only, generated for reproducible preview.
def area(name,loc,power,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
 o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((256,-225,10))-o.location).to_track_quat('-Z','Y').to_euler()
area('Preview_Key',(310,-180,115),180000,75)
area('Preview_Fill',(190,-325,70),90000,90)
area('Preview_Rim',(230,-100,90),100000,60)
camd=bpy.data.cameras.new('UCH_Preview_Camera');cam=bpy.data.objects.new('UCH_Preview_Camera',camd);scene.collection.objects.link(cam);scene.camera=cam
camd.type='ORTHO';camd.ortho_scale=145;camd.lens=50
focus=Vector((256,-225,11.5))
views={
 'east_oblique':(Vector((145,-25,52)),Vector((1,0,0))),
 'south_oblique':(Vector((35,-135,50)),Vector((0,1,0))),
 'northwest_oblique':(Vector((-105,95,48)),Vector((0,0,1))),
}
for name,(offset,up) in views.items():
 cam.location=focus+offset;cam.rotation_euler=(focus-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(out/(name+'.png'))
 bpy.ops.render.render(write_still=True)
# top orthographic footprint verification
cam.location=focus+Vector((0,0,185));cam.rotation_euler=(focus-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=145
scene.render.filepath=str(out/'top.png');bpy.ops.render.render(write_still=True)
print(json.dumps({'renders':[str(p) for p in sorted(out.glob('*.png'))]}))


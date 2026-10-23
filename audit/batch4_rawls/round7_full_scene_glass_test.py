import bpy, os
from mathutils import Vector
blend=os.path.abspath('modular/buildings/rawls_hall.blend');bpy.ops.wm.open_mainfile(filepath=blend)
s=bpy.context.scene; m=bpy.data.materials['RAWL_CurtainWall_Glass']; p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
# Test true Cycles transmission before saving any final material changes.
p.inputs['Base Color'].default_value=(.78,.87,.9,1);p.inputs['Transmission Weight'].default_value=1.0;p.inputs['Roughness'].default_value=.055;p.inputs['Metallic'].default_value=0
if 'IOR' in p.inputs:p.inputs['IOR'].default_value=1.45
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.cycles.max_bounces=18;s.cycles.transmission_bounces=12
s.render.resolution_x=1200;s.render.resolution_y=675;s.render.resolution_percentage=100
# Interior-only fill. Nothing on the building is hidden; existing north/south
# masonry, pane, frame, partitions, and shell remain in the full-scene render.
for i,(pos,power,size) in enumerate([((29,7,4.5),1900,5),((36,6,4.5),1500,5),((-10,-17,5),1500,4)]):
 ld=bpy.data.lights.new('R7_Interior_Test_'+str(i),'AREA');ld.energy=power;ld.shape='DISK';ld.size=size
 lo=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(lo);lo.location=pos
 lo.rotation_euler=(Vector((30,5,1))-lo.location).to_track_quat('-Z','Y').to_euler()
# Use the existing ordinary north elevation camera and sun; no camera cutaway.
s.camera=bpy.data.objects.get('Cam_RAWL_01_North_StateSt')
s.render.filepath=os.path.abspath('audit/batch4_rawls/full_scene_north_glass_cycles_test_round7.png')
bpy.ops.render.render(write_still=True)
print('Full-scene glass test: camera',s.camera.name,'engine',s.render.engine,'no building geometry hidden; unsaved trial.')

import bpy, os, json, math
from mathutils import Vector
blend=os.path.abspath('modular/buildings/rawls_hall.blend')
bpy.ops.wm.open_mainfile(filepath=blend);s=bpy.context.scene
print('REOPENED',bpy.data.filepath,'objects',len(s.objects),'meshes',sum(o.type=='MESH' for o in s.objects))
wall=bpy.data.objects['RAWL_Masonry_Exterior_Walls']; checks=[]
for name, coords, startaxis, direction in [
 ('south', [(-9.804,-24.8,2.35),(-5.994,-24.8,7.836),(-9.804,-24.8,12.927),(-5.994,-24.8,18.017)],'Y',(0,1,0)),
 ('north', [(-10.0,21.3,2.35),(0.0,21.3,7.836),(10.0,21.3,12.927),(20.0,21.3,18.017)],'Y',(0,-1,0))]:
 for i,origin in enumerate(coords):
  hit,loc,norm,fi,obj,mx=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector(origin),Vector(direction),distance=8)
  first=obj.name if hit else None; distance=(loc-Vector(origin)).length if hit else None
  # Continue from the first surface to identify whether the path reaches the modeled interior.
  second=None;seconddist=None
  if hit:
   h2,l2,n2,f2,o2,m2=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),loc+Vector(direction)*.015,Vector(direction),distance=8)
   second=o2.name if h2 else None;seconddist=(l2-loc).length if h2 else None
  checks.append({'facade':name,'sample':i,'origin':list(origin),'first_hit':first,'first_distance':distance,'next_hit':second,'next_distance':seconddist})
print('RAYS',json.dumps(checks))
os.makedirs('audit/batch4_rawls',exist_ok=True)
with open('audit/batch4_rawls/round5_aperture_ray_checks.json','w') as f:json.dump(checks,f,indent=2)
# Fresh south front, oblique and north glass/interior evidence renders.
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
world=bpy.data.worlds.get('RAWL_Batch4_World') or bpy.data.worlds.new('RAWL_Batch4_World');s.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.62,.69,.77,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.85
ld=bpy.data.lights.new('R5_Evidence_Sun','SUN');ld.energy=1.6;sun=bpy.data.objects.new('R5_Evidence_Sun',ld);s.collection.objects.link(sun);sun.rotation_euler=(math.radians(25),math.radians(-28),math.radians(-40))
ad=bpy.data.lights.new('R5_Evidence_Softbox','AREA');ad.energy=6500;ad.shape='DISK';ad.size=18;area=bpy.data.objects.new('R5_Evidence_Softbox',ad);s.collection.objects.link(area)
cd=bpy.data.cameras.new('R5_Evidence_Camera');cam=bpy.data.objects.new('R5_Evidence_Camera',cd);s.collection.objects.link(cam);s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.image_settings.file_format='PNG'
views=[('south_elevation_round5',(-8,-55,12),(-8,-24,12),50,'ORTHO',52),('south_glazing_closeup_round5',(-8,-35,10),(-8,-24,10),55,'PERSP',None),('north_glazing_interior_round5',(5,62,10),(5,20,10),55,'PERSP',None)]
for name,eye,target,lens,typ,scale in views:
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type=typ;cam.data.lens=lens
 if scale:cam.data.ortho_scale=scale
 area.location=(target[0]+5,target[1]+25,target[2]+12);area.rotation_euler=(Vector(target)-area.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=os.path.abspath('audit/batch4_rawls/'+name+'.png');bpy.ops.render.render(write_still=True);print('RENDERED',name,s.render.filepath)
# Save technical verification without saving temporary camera/light setup into the asset.
print('WALL_FACE_COUNT',len(wall.data.polygons),'SOUTH_FRAME_FACE_COUNT',len(bpy.data.objects['RAWL_South_Windows_South_BronzeMullions'].data.polygons))

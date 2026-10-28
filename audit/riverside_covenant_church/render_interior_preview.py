"""Temporary roof/front-wall cutaway render; the saved asset is not altered."""
import bpy, bmesh, json, math, os
from mathutils import Vector
folder=os.path.dirname(os.path.abspath(__file__))
cfg=json.load(open(os.path.join(folder,'build_config.json'),encoding='utf-8'))
snap=json.load(open(os.path.join(folder,'source_mesh_snapshot.json'),encoding='utf-8'))
obj=bpy.data.objects.get(cfg['object_name'])
if obj is None: raise RuntimeError('Riverside asset missing')
ring=[]
for raw in snap['vertices_local']:
 p=obj.matrix_world@Vector(raw)
 if abs(p.z)<1e-6 and not any((p-q).length<1e-5 for q in ring):ring.append(p)
end_a=(ring[0]+ring[1])*.5; end_b=(ring[2]+ring[3])*.5
axis=Vector((end_b.x-end_a.x,end_b.y-end_a.y,0)).normalized(); center=sum(ring,Vector((0,0,0)))/4
cross=Vector((-axis.y,axis.x,0))
if cross.dot((ring[1]+ring[2])*.5-center)<0:cross.negate()
width=abs(((ring[1]+ring[2])*.5-(ring[0]+ring[3])*.5).dot(cross)); y0=-width/2
preview=obj.copy(); preview.data=obj.data.copy(); preview.name='Riverside_InteriorCutawayPreview'; bpy.context.scene.collection.objects.link(preview)
obj.hide_render=True; preview.hide_render=False
bm=bmesh.new(); bm.from_mesh(preview.data); bm.faces.ensure_lookup_table()
remove=[]
for f in bm.faces:
 name=preview.data.materials[f.material_index].name.lower() if f.material_index<len(preview.data.materials) and preview.data.materials[f.material_index] else ''
 c=f.calc_center_median(); dy=(Vector(c)-center).dot(cross)
 # Hide roof/canopy surfaces and open the south entry wall to expose the interior plan.
 if 'charcoal_architectural_shingle' in name or 'dark_metal_canopies' in name:
  remove.append(f); continue
 if dy < y0+.30 and c.z < float(cfg['wall_eaves_m'])+.05:
  remove.append(f)
bmesh.ops.delete(bm,geom=remove,context='FACES')
bm.to_mesh(preview.data); bm.free(); preview.data.update()
pts=[preview.matrix_world@v.co for v in preview.data.vertices]
lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts))); hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
look=(lo+hi)/2; look.z=2.5
scene=bpy.context.scene
camdata=bpy.data.cameras.new('RiversideInteriorCutawayCamera'); cam=bpy.data.objects.new('RiversideInteriorCutawayCamera',camdata); scene.collection.objects.link(cam)
cam.location=look+Vector((-22,-29,40)); cam.rotation_euler=(look-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.type='ORTHO'; camdata.ortho_scale=40; scene.camera=cam
for n,off,power,size in [('InteriorKey',(-8,-10,34),2200,20),('InteriorFill',(18,-2,20),1100,16)]:
 ld=bpy.data.lights.new('Riverside_'+n,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=size
 ob=bpy.data.objects.new('Riverside_'+n,ld); scene.collection.objects.link(ob); ob.location=look+Vector(off); ob.rotation_euler=(look-ob.location).to_track_quat('-Z','Y').to_euler()
try: scene.render.engine='BLENDER_EEVEE_NEXT'
except TypeError: scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1440; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(folder,'preview_interior_cutaway.png')
scene.view_settings.view_transform='AgX'; scene.view_settings.exposure=0
bpy.ops.render.render(write_still=True)
print('RIVERSIDE_INTERIOR_PREVIEW='+scene.render.filepath)

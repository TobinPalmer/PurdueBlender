import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path.cwd(); O=R/'audit/mechanical_engineering/second_pass/review_r02_2026-11-03'; A=R/'modular/buildings/mechanical_engineering.blend'
coll=bpy.data.collections.get('Asset_mechanical_engineering')
objs=list(coll.all_objects) if coll else []
mesh=[o for o in objs if o.type=='MESH']
info={'asset_sha256':hashlib.sha256(A.read_bytes()).hexdigest(),'filepath':bpy.data.filepath,'collections':[c.name for c in bpy.data.collections],'objects':[{'name':o.name,'type':o.type,'dimensions':list(o.dimensions),'location':list(o.location),'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []} for o in objs],'images':[{'name':im.name,'packed':bool(im.packed_file),'path':im.filepath} for im in bpy.data.images]}
(O/'asset_inspection.json').write_text(json.dumps(info,indent=2))
pts=[o.matrix_world@Vector(c) for o in mesh for c in o.bound_box]
lo=Vector(tuple(min(p[i] for p in pts) for i in range(3))); hi=Vector(tuple(max(p[i] for p in pts) for i in range(3))); center=(lo+hi)/2; span=max(hi.x-lo.x,hi.y-lo.y)
scene=bpy.context.scene
for o in scene.objects:
    o.hide_render=o not in objs
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.background_type='WORLD';scene.world.color=(0.65,0.65,0.65)
scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
cam=bpy.data.objects.new('ReviewCamera',bpy.data.cameras.new('ReviewCamera'));scene.collection.objects.link(cam);scene.camera=cam;cam.hide_render=False;cam.data.type='ORTHO';cam.data.ortho_scale=span*1.28
for name,d in [('south',(0,-1,.05)),('north',(0,1,.05)),('east',(1,0,.05)),('west',(-1,0,.05)),('ne',(1,1,.65)),('sw',(-1,-1,.65)),('top',(0,0,1))]:
    cam.location=center+Vector(d).normalized()*span*2;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)

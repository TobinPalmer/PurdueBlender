import bpy, json
from mathutils import Vector
path=bpy.data.filepath
col=bpy.data.collections.get('Asset_massing_3rd_and_west_ffa3d05')
objs=list(col.all_objects) if col else []
out={'file':path,'collections':[c.name for c in bpy.data.collections],'asset_collection':col.name if col else None,'objects':[]}
for o in objs:
 b=[o.matrix_world @ Vector(c) for c in o.bound_box]
 out['objects'].append({'name':o.name,'type':o.type,'verts':len(o.data.vertices) if o.type=='MESH' else None,'faces':len(o.data.polygons) if o.type=='MESH' else None,'bounds':[[min(v[i] for v in b),max(v[i] for v in b)] for i in range(3)],'location':list(o.location),'dimensions':list(o.dimensions)})
open('audit/massing_3rd_and_west_ffa3d05/source_probe.json','w',encoding='utf8').write(json.dumps(out,indent=2))
# top orthographic camera
scene=bpy.context.scene
xs=[v.x for o in objs for v in [o.matrix_world@Vector(c) for c in o.bound_box]]
ys=[v.y for o in objs for v in [o.matrix_world@Vector(c) for c in o.bound_box]]
zs=[v.z for o in objs for v in [o.matrix_world@Vector(c) for c in o.bound_box]]
center=Vector(((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,(min(zs)+max(zs))/2))
camd=bpy.data.cameras.new('AuditCamera'); cam=bpy.data.objects.new('AuditCamera',camd); scene.collection.objects.link(cam); cam.location=(center.x,center.y,max(zs)+250);cam.rotation_euler=(0,0,0);cam.rotation_euler[0]=0; cam.rotation_euler[0]=0
# camera points down local -Z, orient top-down with Y-up world
cam.rotation_euler=(0,0,0); cam.rotation_euler[0]=0
# Blender camera default looks -Z; top-down no rotation works
camd.type='ORTHO'; camd.ortho_scale=max(max(xs)-min(xs),max(ys)-min(ys))*1.2; scene.camera=cam
scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=r'C:\\Users\\gotse\\Documents\\Codex\\2026-10-25\\github-plugin-github-openai-curated-remote\\outputs\\PurdueBlender\\audit\\massing_3rd_and_west_ffa3d05\\source_top.png';scene.render.film_transparent=False
scene.world.color=(0.15,0.15,0.15)
# hide audit camera from asset collection not issue, don't save source
bpy.ops.render.render(write_still=True)


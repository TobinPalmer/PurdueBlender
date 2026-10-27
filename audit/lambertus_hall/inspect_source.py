import bpy,json
from pathlib import Path
from mathutils import Vector
scene=bpy.context.scene
objs=[o for o in bpy.data.objects if o.type in {'MESH','CURVE','FONT'}]
rows=[]
for o in objs:
    bb=[o.matrix_world @ Vector(c) for c in o.bound_box]
    bounds=[[min(v[i] for v in bb),max(v[i] for v in bb)] for i in range(3)]
    rows.append({'name':o.name,'type':o.type,'verts':len(o.data.vertices) if o.type=='MESH' else None,'polygons':len(o.data.polygons) if o.type=='MESH' else None,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'bounds':bounds})
allv=[Vector((x,y,z)) for r in rows for x in (r['bounds'][0]) for y in (r['bounds'][1]) for z in (r['bounds'][2])]
all_bounds=[[min(v[i] for v in allv),max(v[i] for v in allv)] for i in range(3)] if allv else None
result={'file':bpy.data.filepath,'scene':scene.name,'collections':[{'name':c.name,'objects':[o.name for o in c.objects]} for c in bpy.data.collections],'objects':rows,'all_bounds':all_bounds,'materials':[{'name':m.name,'nodes':len(m.node_tree.nodes) if m.use_nodes and m.node_tree else 0} for m in bpy.data.materials]}
Path('audit/lambertus_hall/source_inspection.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
# camera uses overall geometry bounds, is saved only as evidence render
if allv:
    center=sum(allv,Vector())/len(allv); span=max(all_bounds[i][1]-all_bounds[i][0] for i in range(3))
    cam_data=bpy.data.cameras.new('EvidenceCamera'); cam=bpy.data.objects.new('EvidenceCamera',cam_data); scene.collection.objects.link(cam)
    cam.location=center+Vector((1.2,-1.5,1.1))*span; direction=center-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=span*1.8; scene.camera=cam
    light_data=bpy.data.lights.new('EvidenceKey','AREA'); light=bpy.data.objects.new('EvidenceKey',light_data); scene.collection.objects.link(light); light.location=center+Vector((0,-span,span*1.5)); light.data.energy=span*span*10; light.data.shape='DISK'; light.data.size=span*.8
    scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    if scene.world is None: scene.world=bpy.data.worlds.new('EvidenceWorld')
    scene.world.color=(.12,.12,.12); scene.view_settings.view_transform='Standard'; scene.render.image_settings.file_format='PNG'; scene.render.filepath='audit/lambertus_hall/source_preview.png'; bpy.ops.render.render(write_still=True)
print(json.dumps({'object_count':len(objs),'all_bounds':all_bounds}))



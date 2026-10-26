import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
p=Path(bpy.data.filepath)
h=hashlib.sha256(p.read_bytes()).hexdigest()
scenes=[]
for s in bpy.data.scenes:
    scenes.append({'name':s.name,'objects':len(s.objects),'camera':s.camera.name if s.camera else None,'render_engine':s.render.engine,'resolution':[s.render.resolution_x,s.render.resolution_y]})
col=bpy.data.collections.get('Asset_massing_first_street_towers_west_fstw_b6c3bbe')
wall=col.objects.get('FSTW | GIS perimeter walls, six levels') if col else None
wall_ring=[]
if wall:
    for poly in sorted(wall.data.polygons,key=lambda p:p.index):
        vids=list(poly.vertices); a=wall.data.vertices[vids[0]].co; b=wall.data.vertices[vids[1]].co
        wall_ring.append([float(a.x),float(a.y)])
objs=[]
for o in col.objects:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    mn=[min(v[i] for v in bb) for i in range(3)]; mx=[max(v[i] for v in bb) for i in range(3)]
    objs.append({'name':o.name,'type':o.type,'bounds':[mn,mx], 'verts':len(o.data.vertices) if o.type=='MESH' else None,'faces':len(o.data.polygons) if o.type=='MESH' else None,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'mods':[m.name+':'+m.type for m in o.modifiers]})
images=[{'name':i.name,'source':i.source,'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images]
report={'path':str(p),'sha256':h,'scenes':scenes,'collection_name':col.name if col else None,'collection_objects':objs,'candidate_wall_base_ring_xy':wall_ring,'images':images,'unit_settings':{'system':bpy.context.scene.unit_settings.system,'scale_length':bpy.context.scene.unit_settings.scale_length},'asset_props':{k:col[k] for k in col.keys()} if col else {}}
out=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\first_street_towers_west_fstw_independent_grade\fresh_open_inspection.json')
out.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({'sha256':h,'scene_count':len(scenes),'collection':col.name if col else None,'objects':len(objs),'images':images},indent=2))



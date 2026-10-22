import bpy,json,pathlib
from mathutils import Vector
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); out={}
m=json.loads((P/'modular/manifest.json').read_text()); refs=json.loads((P/'audit/official_building_references.json').read_text())
for id in ['hovde_hall','elliott_hall_of_music','bell_tower']:
 a=next(a for a in m['assets'] if a['id']==id);bpy.ops.wm.open_mainfile(filepath=str(P/'modular'/a['file'])); bpy.context.view_layer.update(); col=bpy.data.collections[a['collection']];rows=[]
 for o in col.all_objects:
  ps=[o.matrix_world@Vector(v) for v in o.bound_box] if o.type in ['MESH','FONT','CURVE'] else []
  rows.append({'name':o.name,'parent':o.parent.name if o.parent else None,'loc':list(o.location),'world_loc':list(o.matrix_world.translation),'bbox':[[min(p[i] for p in ps),max(p[i] for p in ps)]for i in range(3)] if ps else None})
 out[id]={'asset':a,'objects':rows}
(P/'audit/walc_north/inspection.json').write_text(json.dumps(out,indent=2))
print('INSPECT_DONE')

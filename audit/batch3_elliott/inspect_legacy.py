import bpy,json,pathlib
from mathutils import Vector
root=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
src=root/'modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=str(src))
rows=[]
for col in bpy.data.collections:
 if 'Legacy' not in col.name and 'ELLT' not in col.name: continue
 for ob in col.objects:
  row={'name':ob.name,'type':ob.type,'collections':[c.name for c in ob.users_collection],
       'loc':list(ob.location),'dim':list(ob.dimensions),'hide_viewport':ob.hide_viewport,
       'hide_render':ob.hide_render,'hide_get':ob.hide_get(),
       'materials':[m.name for m in getattr(ob.data,'materials',[]) if m],
       'props':{k:str(ob[k])[:250] for k in ob.keys() if not k.startswith('_')}}
  if ob.type=='MESH': row.update(vertices=len(ob.data.vertices),faces=len(ob.data.polygons))
  elif ob.type=='CURVE': row.update(splines=len(ob.data.splines),bevel_depth=ob.data.bevel_depth)
  rows.append(row)
(root/'audit/batch3_elliott/legacy_inventory.json').write_text(json.dumps(rows,indent=2))
print('objects',len(rows),'collections',[c.name for c in bpy.data.collections if 'Legacy' in c.name])

import bpy,json,pathlib
p=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
f=p/'modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=str(f))
c=bpy.data.collections['Asset_elliott_hall_of_music']
rows=[]
for o in c.all_objects:
 d={'name':o.name,'type':o.type,'loc':list(o.location),'dim':list(o.dimensions),'collection':o.users_collection[0].name if o.users_collection else None}
 if o.type=='MESH':
  d['verts']=len(o.data.vertices);d['faces']=len(o.data.polygons);d['materials']=[m.name for m in o.data.materials]
 rows.append(d)
(p/'audit/batch3_elliott/source_inventory.json').write_text(json.dumps(rows,indent=2))

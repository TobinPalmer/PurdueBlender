import bpy,json
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/krannert_building.blend'
bpy.ops.wm.open_mainfile(filepath=p)
res=[]
for o in bpy.data.collections['Asset_krannert_building'].all_objects:
 if o.type!='MESH':continue
 cs=[o.matrix_world@v.co for v in o.data.vertices]
 if not cs:continue
 mn=[min(c[i] for c in cs) for i in range(3)];mx=[max(c[i] for c in cs) for i in range(3)]
 if o.name.startswith('KRAN_') and ('Fac' in o.name or 'Window' in o.name or 'Pier' in o.name or 'Spandrel' in o.name or 'Mullion' in o.name):res.append((o.name,mn,mx,len(o.data.vertices),len(o.data.polygons)))
print(json.dumps(res,indent=2))

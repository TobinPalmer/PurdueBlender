import bpy, json
c=bpy.data.collections['Asset_walc']
def tree(col, depth=0):
 print('  '*depth + f'{col.name}: direct={len(col.objects)} total={len(col.all_objects)}')
 for child in sorted(col.children,key=lambda x:x.name): tree(child,depth+1)
tree(c)
keys=('interior','classroom','reading','atrium','stair','library','floor','basement','cafe','room','theater','theatre')
print('OBJECTS',json.dumps([o.name for o in c.all_objects if any(k in o.name.lower() for k in keys)][:160]))
print('CAMERAS',json.dumps([o.name for o in c.all_objects if o.type=='CAMERA']))
print('MATERIALS',json.dumps([m.name for m in sorted({s.material for o in c.all_objects for s in o.material_slots if s.material},key=lambda m:m.name)]))

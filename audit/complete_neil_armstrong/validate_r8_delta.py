import bpy,hashlib,json,math,os
root=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
r7=os.path.join(root,'modular','buildings','neil_armstrong_hall.blend1')
r8=os.path.join(root,'modular','buildings','neil_armstrong_hall.blend')
removed={'ARMS_East_Roof_Penthouse','ARMS_East_Penthouse_Louvers','ARMS_West_Roof_Penthouse','ARMS_West_Penthouse_Louvers'}
def snap(path):
 bpy.ops.wm.open_mainfile(filepath=path)
 col=bpy.data.collections['Asset_neil_armstrong_hall']; root_obj=bpy.data.objects['AssetRoot_neil_armstrong_hall']
 out={}
 for o in col.objects:
  data=None
  if o.type=='MESH':
   data=(tuple((round(v.co.x,6),round(v.co.y,6),round(v.co.z,6)) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons))
  out[o.name]={'type':o.type,'matrix':tuple(round(float(x),8) for row in o.matrix_basis for x in row),'data':data}
 return out,tuple(root_obj.location),len(col.objects)
s7,root7,n7=snap(r7)
s8,root8,n8=snap(r8)
missing=set(s7)-set(s8); added=set(s8)-set(s7)
changed=[name for name in set(s7)&set(s8) if s7[name]!=s8[name]]
if missing!=removed or added or changed or root7!=root8 or n7!=449 or n8!=445:
 raise RuntimeError(json.dumps({'missing':sorted(missing),'added':sorted(added),'changed':changed,'roots':[root7,root8],'counts':[n7,n8]}))
print(json.dumps({'r7_sha256':hashlib.sha256(open(r7,'rb').read()).hexdigest(),'r8_sha256':hashlib.sha256(open(r8,'rb').read()).hexdigest(),'removed_only':sorted(missing),'all_common_mesh_geometry_and_transforms_unchanged':True,'root_unchanged':root8,'counts':[n7,n8]},indent=2))

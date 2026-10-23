import bpy,json,bmesh
P='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_hicks/'
for name,d in json.load(open(P+'slab_plan.json')).items():
 o=bpy.data.objects[name];vs=[];fs=[];idx={}
 def vi(x,y,z):
  key=(round(x,5),round(y,5),z)
  if key not in idx:idx[key]=len(vs);vs.append(key)
  return idx[key]
 for tr in d['triangles']:
  fs.append([vi(x,y,d['z']) for x,y in tr]);fs.append([vi(x,y,d['z']-d['th']) for x,y in reversed(tr)])
 for ring in d['rings']:
  for (x,y),(a,b) in zip(ring,ring[1:]):fs.append([vi(x,y,d['z']),vi(a,b,d['z']),vi(a,b,d['z']-d['th']),vi(x,y,d['z']-d['th'])])
 me=bpy.data.meshes.new(name+'_ClosedSlab');me.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for m in o.data.materials:me.materials.append(m)
 o.data=me;o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1);o.parent=None;o['repair']='Constrained triangulation removes accidental fan gaps; perimeter and central opening retained'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

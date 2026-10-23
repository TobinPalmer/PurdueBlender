p='audit/complete_potter/build.py'
s=open(p).read();s=s.replace("bpy.ops.wm.open_mainfile(filepath=str(P));c=", "shutil.copy2(D/'before.blend',P)\nbpy.ops.wm.open_mainfile(filepath=str(P));c=",1)
s=s.replace('normal=Vector((tangent.y,-tangent.x,0));count=', 'normal=Vector((tangent.y,-tangent.x,0));normal *= (1 if sum(u.x*v.y-v.x*u.y for u,v in zip(pts,pts[1:]+pts[:1]))>0 else -1);count=')
s=s.replace('normal*.115','normal*.125')
s=s.replace("target=Vector((0,0,7));cam.rotation_euler", "target=sum((roof.matrix_world@Vector(v) for v in roof.bound_box),Vector())/8;cam.location=target+Vector((100,-125,90));cam.rotation_euler")
open(p,'w').write(s)

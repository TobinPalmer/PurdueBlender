p='audit/complete_potter/build.py';s=open(p).read();start=s.index('def box(');end=s.index('# Only long',start);s=s[:start]+'''def box(name,loc,scale,mat):
 x,y,z=[v/2 for v in scale];verts=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)];faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(mat);b=bpy.data.objects.new(name,me);c.objects.link(b);b.location=loc;return b
'''+s[end:];open(p,'w').write(s)

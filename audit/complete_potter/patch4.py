p='audit/complete_potter/build.py';s=open(p).read();pos=s.index('# Save portable node textures; no dependencies.');code='''# Iteration: construct real wall apertures directly, retaining the source XY perimeter.
for ob in list(c.objects):
 if ob.name.startswith(('POTR_Precast_Panel','POTR_Shaded_Window','POTR_406mm')):bpy.data.objects.remove(ob,do_unlink=True)
vs=[];fs=[];mis=[]
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=1
for j,(a,b) in enumerate(zip(pts,pts[1:]+pts[:1])):
 d=b-a;L=d.xy.length
 if L<.001:continue
 tangent=Vector((d.x/L,d.y/L,0));normal=Vector((tangent.y,-tangent.x,0));normal *= (1 if sum(u.x*v.y-v.x*u.y for u,v in zip(pts,pts[1:]+pts[:1]))>0 else -1)
 holes=[]
 if L>1.65:
  for k in range(max(1,int(L/1.6256))):
   u=(k+.5)*L/max(1,int(L/1.6256))
   for z in [6.1,10.3672]:holes.append((u-.355,u+.355,z-.3533,z+.3533))
 us=sorted(set([0,L]+[u for h in holes for u in h[:2]]));zs=sorted(set([-.0,4.4,13.5,z1]+[z for h in holes for z in h[2:]]))
 for u0,u1 in zip(us,us[1:]):
  for low,high in zip(zs,zs[1:]):
   if any(h[0]<(u0+u1)/2<h[1] and h[2]<(low+high)/2<h[3] for h in holes):continue
   base=len(vs)
   for u,z in [(u0,low),(u1,low),(u1,high),(u0,high)]:
    q=a+tangent*u;vs.append((q.x,q.y,z))
   fs.append((base,base+1,base+2,base+3));mis.append(int(L>1.65 and 4.4<=(low+high)/2<13.5))
 for h in holes:
  u=(h[0]+h[1])/2;z=(h[2]+h[3])/2;q=a+tangent*u-normal*.1
  ob=box('POTR_RealOpening_Glazing',(q.x,q.y,z),(.71,.025,.7066),glass);ob.rotation_euler.z=math.atan2(d.y,d.x)
  q=a+tangent*u+normal*.2032;ob=box('POTR_Precast_406mm_Overhang',(q.x,q.y,h[3]+.1),(.95,.4064,.16),concrete);ob.rotation_euler.z=math.atan2(d.y,d.x)
me=bpy.data.meshes.new('POTR_Perimeter_With_Real_Window_Openings');me.from_pydata(vs,[],fs);me.materials.append(brick);me.materials.append(concrete)
for face,mi in zip(me.polygons,mis):face.material_index=mi
o.data=me
''';s=s[:pos]+code+s[pos:];open(p,'w').write(s)

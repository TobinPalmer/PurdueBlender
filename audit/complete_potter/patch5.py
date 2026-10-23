p='audit/complete_potter/build.py';s=open(p).read();pos=s.index('# Save portable node textures; no dependencies.');code='''# Date-labelled historical interior tracing, with registration uncertainty retained.
white=material('POTR_Historic2016_Partition_Paint',(.7,.68,.61))
trace=json.loads((D/'historic_walls.json').read_text())
for page,base in [(51,-4.064),(53,.6096),(54,4.8768),(55,9.144)]:
 for idx,line in enumerate(trace[str(page)]['lines']):
  a=Vector((*line[0],0));b=Vector((*line[-1],0));d=b-a;L=d.length
  ob=box('POTR_Historic2016_Plan%d_Wall_%d'%(page,idx),((a.x+b.x)/2,(a.y+b.y)/2,base+1.35),(L,.12,2.7),white);ob.rotation_euler.z=math.atan2(d.y,d.x);ob['evidence']='Raster-traced existing 2016 plan; approximate affine registration, room layout may have changed';ob['registration_iou']=trace[str(page)]['registration_iou']
# Full basement perimeter documented by the existing structural assessment.
vs=[];fs=[]
for a,b in zip(pts,pts[1:]+pts[:1]):
 start=len(vs);vs.extend([(a.x,a.y,-4.064),(b.x,b.y,-4.064),(b.x,b.y,.6096),(a.x,a.y,.6096)]);fs.append((start,start+1,start+2,start+3))
me=bpy.data.meshes.new('POTR_Basement_Perimeter');me.from_pydata(vs,[],fs);me.materials.append(concrete);ob=bpy.data.objects.new('POTR_Full_Basement_Walls',me);c.objects.link(ob);m=ob.modifiers.new('Inward_Basement_280mm','SOLIDIFY');m.thickness=.28;m.offset=-1
''';s=s[:pos]+code+s[pos:];open(p,'w').write(s)

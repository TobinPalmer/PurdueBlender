import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
D=R/'audit/complete_me';c=bpy.data.collections['Asset_mechanical_engineering']
mat=bpy.data.materials.new('ME_PlanBased_Interior_Painted');mat.diffuse_color=(.64,.63,.58,1);mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.64,.63,.58,1)
def pt(x,y):return (128.998992+(x-179)/391*(96.012792-128.998992)+(y-224)/616*(86.567013-128.998992),92.123264+(x-179)/391*(65.063032-92.123264)+(y-224)/616*(144.401325-92.123264))
# Trace identifiable major corridor/room walls from slide12; portal breaks retained. Affine registration is estimated from three exterior anchors.
lines=[[(314,224),(314,670)],[(378,224),(378,670)],[(179,670),(280,670)],[(310,670),(818,670)],[(300,694),(300,745),(817,745)],[(350,770),(817,770)],[(230,354),(230,453)],[(250,480),(250,615)],[(270,480),(314,480)],[(263,520),(314,520)],[(263,555),(314,555)],[(263,610),(314,610)],[(482,283),(570,283)],[(482,341),(570,341)],[(482,390),(570,390)],[(482,445),(570,445)],[(482,502),(570,502)],[(482,556),(570,556)],[(482,612),(570,612)],[(482,359),(482,610)],[(397,681),(397,727)],[(467,681),(467,727)],[(562,681),(562,727)],[(654,681),(654,727)],[(721,681),(721,727)],[(487,780),(487,838)],[(598,780),(598,838)],[(711,780),(711,838)],[(760,440),(891,579)],[(816,515),(930,655)],[(890,451),(1013,585)],[(918,480),(953,449)],[(952,514),(985,485)],[(985,548),(1017,519)],[(1017,579),(1047,551)]]
count=0
for idx,line in enumerate(json.loads((D/'clipped_lines.json').read_text())):
 for vv in [line]:
  for a,b in zip(vv,vv[1:]):
   dx,dy=b[0]-a[0],b[1]-a[1];le=math.hypot(dx,dy)
   if le<.25:continue
   bpy.ops.mesh.primitive_cube_add(size=1,location=((a[0]+b[0])/2-66.3000011444,(a[1]+b[1])/2-86.5,1.9));o=bpy.context.object;o.name=f'ME_Slide12_Partition_{idx}_{count}';o.dimensions=(le,.15,3.8);o.rotation_euler.z=math.atan2(dy,dx);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
   for col in list(o.users_collection):col.objects.unlink(o)
   c.objects.link(o);o.data.materials.append(mat);o['source']='Purdue2025 Safety slide12';o['accuracy']='Approximate affine registered major walls; heights and thickness estimated; omitted minor rooms';count+=1
c['interior_status']='Major ground floor partitions traced2025 safety diagram; estimated registration and heights, incomplete furnishing'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'modular/buildings/mechanical_engineering.blend'));(D/'partitions.json').write_text(json.dumps({'count':count,'anchors_image':[[179,224],[570,224],[179,840]],'anchors_gis':[[86.567013,144.401325],[128.998992,92.123264],[32.635845,100.189118]],'uncertainty':'Unscaled safety diagram affine fit, no surveyed room dimensions; major walls only'},indent=2))

import bpy, json
src=bpy.data.filepath
assert src.lower().endswith('krach_leadership_center.blend')
col=bpy.data.collections['Schematic_Interior']
for o in list(bpy.data.objects):
 if o.name.startswith('KRCH | continuous stair handrails'):
  bpy.data.objects.remove(o,do_unlink=True)
mat=bpy.data.materials.get('KRCH | dark handrail cap') or bpy.data.materials.new('KRCH | dark handrail cap')
mat.diffuse_color=(0.12,0.15,0.16,1); mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF')
if bs: bs.inputs['Base Color'].default_value=(0.12,0.15,0.16,1); bs.inputs['Metallic'].default_value=0.65; bs.inputs['Roughness'].default_value=0.28
curve=bpy.data.curves.new('KRCH | dark metal rail cap over etched glass','CURVE'); curve.dimensions='3D'; curve.resolution_u=2; curve.bevel_depth=0.035; curve.bevel_resolution=3
levels=[-0.92,2.98,6.88,10.78,14.68]; x0=-23.35; xm=-19.45; xe=-15.55; ya=-10.55; yb=-8.05; width=1.75
ysA=[ya-width/2-0.10,ya+width/2+0.10]; ysB=[yb-width/2-0.10,yb+width/2+0.10]; n=11
for lo,hi in zip(levels[:-1],levels[1:]):
 mid=(lo+hi)/2
 lines=[]
 for y in ysA: lines.append(((x0,y,lo+1.02),(xm,y,mid+1.02)))
 for y in ysB: lines.append(((xe,y,mid+1.02),(xm,y,hi+1.02)))
 for y in [ysA[0],ysB[1]]:
  lines.append(((xm,y,mid+1.02),(xe,y,mid+1.02)))
  lines.append(((x0,y,hi+1.02),(xm,y,hi+1.02)))
 for a,b in lines:
  sp=curve.splines.new('POLY'); sp.points.add(1); sp.points[0].co=(*a,1); sp.points[1].co=(*b,1)
obj=bpy.data.objects.new('KRCH | continuous stair handrails over glass gallery guards',curve); col.objects.link(obj); curve.materials.append(mat)
obj['source_basis']='Purdue Stories stairwell photograph shows metal handrails over translucent stair guards; exact rail profile and dimensions are schematic.'
obj['continuity']='Each stair flight cap terminates at the matching landing cap; the landing cap continues the protected outer edge to the next stair run.'
obj['source_photo']='audit/krach_leadership_center/purdue_krach_stairwell_reference.jpg'
bpy.ops.wm.save_as_mainfile(filepath=src)
print(json.dumps({'saved':src,'rail_splines':len(curve.splines),'bevel_diameter_m':curve.bevel_depth*2},indent=2))

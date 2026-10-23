import bpy, math, os, json
from mathutils import Vector
BLEND=os.path.abspath('modular/buildings/rawls_hall.blend')
bpy.ops.wm.open_mainfile(filepath=BLEND)
col=bpy.data.collections['Asset_rawls_hall']
# Update facade glass to read as translucent architectural glazing in rendered light.
glass=bpy.data.materials['RAWL_CurtainWall_Glass']; glass.use_nodes=True
bs=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Base Color'].default_value=(0.30,0.39,0.43,1)
bs.inputs['Roughness'].default_value=0.18
bs.inputs['Metallic'].default_value=0.05
bs.inputs['Transmission Weight'].default_value=0.18
if 'Coat Weight' in bs.inputs:bs.inputs['Coat Weight'].default_value=0.25
if 'Coat Roughness' in bs.inputs:bs.inputs['Coat Roughness'].default_value=0.12
glass.diffuse_color=(0.30,0.39,0.43,1)
# Bronze mullions get enough separation from the panes to remain legible at facade scale.
bronze=bpy.data.materials.get('RAWL_Dark_Bronze_Metal')
if bronze and bronze.use_nodes:
 b=next(n for n in bronze.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 b.inputs['Base Color'].default_value=(0.20,0.15,0.095,1);b.inputs['Metallic'].default_value=0.78;b.inputs['Roughness'].default_value=0.28
 bronze.diffuse_color=(0.20,0.15,0.095,1)
# Historical atrium imagery (2003 archive and Purdue Business 2022 photo) shows ochre/yellow columns.
# This is a source-informed palette treatment; exact present finish is not verified.
column=bpy.data.materials.get('RAWL_Atrium_Ochre_HistoricReference') or bpy.data.materials.new('RAWL_Atrium_Ochre_HistoricReference')
column.use_nodes=True;column.diffuse_color=(0.54,0.27,0.085,1);column.node_tree.nodes.clear()
out=column.node_tree.nodes.new('ShaderNodeOutputMaterial');p=column.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Roughness'].default_value=0.62
p.inputs['Base Color'].default_value=(0.54,0.27,0.085,1)
tc=column.node_tree.nodes.new('ShaderNodeTexCoord');noise=column.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=0.55
ramp=column.node_tree.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=(.43,.19,.05,1);ramp.color_ramp.elements[1].position=.78;ramp.color_ramp.elements[1].color=(.58,.30,.10,1)
column.node_tree.links.new(tc.outputs['Object'],noise.inputs['Vector']);column.node_tree.links.new(noise.outputs['Fac'],ramp.inputs['Fac']);column.node_tree.links.new(ramp.outputs['Color'],p.inputs['Base Color']);column.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface'])
cols=bpy.data.objects['RAWL_Atrium_Structural_Columns'];cols.data.materials.clear();cols.data.materials.append(column)
# A quiet matte floor finish in the source-plan 1086 classroom; the plan does not specify finish,
# so this medium charcoal carpet is an explicitly estimated campus-interior finish.
carpet=bpy.data.materials.get('RAWL_1086_Floor_CharcoalCarpet_Estimated') or bpy.data.materials.new('RAWL_1086_Floor_CharcoalCarpet_Estimated')
carpet.use_nodes=True;carpet.diffuse_color=(.22,.23,.24,1);carpet.node_tree.nodes.clear()
out=carpet.node_tree.nodes.new('ShaderNodeOutputMaterial');p=carpet.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Roughness'].default_value=.92;p.inputs['Base Color'].default_value=(.22,.23,.24,1)
tc=carpet.node_tree.nodes.new('ShaderNodeTexCoord');mapping=carpet.node_tree.nodes.new('ShaderNodeMapping');mapping.inputs['Scale'].default_value=(30,30,30);noise=carpet.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.0;noise.inputs['Detail'].default_value=2.0
ramp=carpet.node_tree.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=(.13,.145,.16,1);ramp.color_ramp.elements[1].position=.78;ramp.color_ramp.elements[1].color=(.25,.26,.27,1)
bump=carpet.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.00018
links=carpet.node_tree.links;links.new(tc.outputs['Object'],mapping.inputs['Vector']);links.new(mapping.outputs['Vector'],noise.inputs['Vector']);links.new(noise.outputs['Fac'],ramp.inputs['Fac']);links.new(ramp.outputs['Color'],p.inputs['Base Color']);links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal']);links.new(p.outputs['BSDF'],out.inputs['Surface'])
fp=bpy.data.objects['RAWL_FloorSlab_L1_Ground']
room=[(127,318),(120,295),(245,256),(301,437),(176,475),(131,333)]
roomxy=[(399-.12*y-323.6582336425781,-384-.12*x+409.62242126464844) for x,y in room]
def inside(point,poly):
 x,y=point;c=False;j=len(poly)-1
 for i in range(len(poly)):
  xi,yi=poly[i];xj,yj=poly[j]
  if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi+1e-12)+xi:c=not c
  j=i
 return c
if carpet.name not in [m.name for m in fp.data.materials]:fp.data.materials.append(carpet)
carp_idx=next(i for i,m in enumerate(fp.data.materials) if m==carpet)
assigned=[]
for polyface in fp.data.polygons:
 c=fp.matrix_world@polyface.center
 if abs(c.z)<.02 and inside((c.x,c.y),roomxy):
  polyface.material_index=carp_idx;assigned.append({'face':polyface.index,'center':[round(c.x,3),round(c.y,3)],'area':round(polyface.area,2)})
# Metal top rails and vertical posts at current glazed atrium-balustrade extents/floors.
# Position follows existing panel mesh (approximate plan and unverified upper floor layout).
for o in list(bpy.data.objects):
 if o.name.startswith('RAWL_R2_Atrium_Railwork'):bpy.data.objects.remove(o,do_unlink=True)
railmat=bpy.data.materials.get('RAWL_Atrium_Rail_DarkBronze_R2') or bpy.data.materials.new('RAWL_Atrium_Rail_DarkBronze_R2')
railmat.use_nodes=True;railmat.diffuse_color=(.12,.11,.095,1);rbs=next(n for n in railmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');rbs.inputs['Base Color'].default_value=(.12,.11,.095,1);rbs.inputs['Metallic'].default_value=.74;rbs.inputs['Roughness'].default_value=.28
verts=[];faces=[]
def addbox(center,dims):
 x,y,z=center;dx,dy,dz=[v/2 for v in dims];base=len(verts)
 verts.extend([(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),(x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),(x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),(x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)])
 faces.extend([tuple(base+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
x0,x1=2.34,18.34;y0,y1=-4.38,1.62
levels=[(5.486,6.536),(10.577,11.627),(15.667,16.717),(20.33,21.38)]
for zbase,ztop in levels:
 zmid=(zbase+ztop)/2
 # cap rails along each existing glass-panel edge
 for y in [y0,y1]:addbox(((x0+x1)/2,y,ztop+.025),(x1-x0+.08,.055,.055))
 for x in [x0,x1]:addbox((x,(y0+y1)/2,ztop+.025),(.055,y1-y0+.08,.055))
 # glass-panel mullions/posts at approximately 2m spacing
 for y in [y0,y1]:
  for i in range(9):addbox((x0+(x1-x0)*i/8,y,zmid),(.045,.05,ztop-zbase))
 for x in [x0,x1]:
  for i in range(1,4):addbox((x,y0+(y1-y0)*i/4,zmid),(.05,.045,ztop-zbase))
mesh=bpy.data.meshes.new('RAWL_R2_Atrium_Railwork_Mesh');mesh.from_pydata(verts,[],faces);mesh.materials.append(railmat);mesh.update()
rail=bpy.data.objects.new('RAWL_R2_Atrium_Railwork_EvidenceInformed',mesh);col.objects.link(rail)
# Persist audit attributes to make finish/evidence status explicit.
rail['evidence_note']='Approximate dark bronze caps and posts added to the existing glass atrium guard panels. Historic 2003 archive photo and 2022 Purdue Business atrium image show glass guardrails; upper-floor layout is not plan-verified.'
cols['evidence_note']='Ochre column finish is informed by Purdue 2003 archive atrium photo and Purdue Business 2022 atrium photo; exact current finish is unverified.'
carpet['evidence_note']='Estimated classroom finish; the 2024 plan does not specify flooring. Chosen to provide a restrained matte commercial finish; not a verified current material.'
# Save only the standalone Rawls asset.
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
report={'saved':BLEND,'railwork_meshes':1,'railwork_cuboids':len(faces)//6,'atrium_columns_material':column.name,'glass':{'base_color':list(bs.inputs['Base Color'].default_value),'roughness':bs.inputs['Roughness'].default_value,'transmission':bs.inputs['Transmission Weight'].default_value},'classroom_floor_faces_assigned':assigned,'walls_left_unmoved_after_review':11}
with open('audit/batch4_rawls/round2_model_changes.json','w') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))

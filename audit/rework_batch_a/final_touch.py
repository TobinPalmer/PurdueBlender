import bpy,os,json
from mathutils import Vector
ROOT=os.path.abspath('.'); OUT=os.path.join(ROOT,'audit','rework_batch_a')
def box(col,name,loc,dim,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.data.materials.append(mat);return o
def concrete(m,color):
 m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear();g=n.new('ShaderNodeNewGeometry');g.location=(-500,80);noise=n.new('ShaderNodeTexNoise');noise.location=(-300,80);noise.inputs['Scale'].default_value=48;noise.inputs['Detail'].default_value=3;l.new(g.outputs['Position'],noise.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.location=(-70,120);r.color_ramp.elements[0].color=(color[0]*.72,color[1]*.72,color[2]*.72,1);r.color_ramp.elements[1].color=(color[0]*1.05,color[1]*1.05,color[2]*1.05,1);l.new(noise.outputs['Fac'],r.inputs['Fac']);p=n.new('ShaderNodeBsdfPrincipled');p.location=(200,80);p.inputs['Roughness'].default_value=.82;l.new(r.outputs['Color'],p.inputs['Base Color']);b=n.new('ShaderNodeBump');b.location=(0,-150);b.inputs['Strength'].default_value=.1;b.inputs['Distance'].default_value=.008;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs['Normal'],p.inputs['Normal']);out=n.new('ShaderNodeOutputMaterial');out.location=(460,80);l.new(p.outputs['BSDF'],out.inputs['Surface']);m.diffuse_color=(*color,1)
# MSEE: open schematic floors and truthful concrete finish
asset='materials_science_and_electrical_engineering_msee';path=os.path.join(ROOT,'modular','buildings',asset+'.blend');bpy.ops.wm.open_mainfile(filepath=path);col=next(c for c in bpy.data.collections if c.name=='Asset_'+asset)
for mat in bpy.data.materials:
 if mat.name.startswith(asset) and ('_facade' in mat.name or '_textured_masonry' in mat.name): concrete(mat,(.39,.41,.42))
mat=bpy.data.materials.get('MSEE_atrium_schematic_floor') or bpy.data.materials.new('MSEE_atrium_schematic_floor');mat.diffuse_color=(.24,.26,.27,1);mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.24,.26,.27,1)
for idx in range(1,4):
 found=[o for o in col.objects if o.name in (f'MSEE_schematic_floor_{idx}',f'MSEE_interior_floor_{idx}')]
 if not found: continue
 bounds=[]
 for o in found:
  p=[o.matrix_world@Vector(v) for v in o.bound_box];bounds.append(([min(q[i] for q in p) for i in range(3)],[max(q[i] for q in p) for i in range(3)]));bpy.data.objects.remove(o,do_unlink=True)
 lo,hi=bounds[0]; z=(lo[2]+hi[2])*.5; t=hi[2]-lo[2]
 # clear atrium spans x=-20.57:-6.49, y=-19.71:-2.53
 for name,y0,y1,x0,x1 in [(f'MSEE_atrium_gallery_south_{idx}',lo[1],-19.8,lo[0],hi[0]),(f'MSEE_atrium_gallery_east_{idx}',-19.8,-2.45,-6.35,hi[0]),(f'MSEE_atrium_gallery_north_{idx}',-2.45,hi[1],lo[0],hi[0])]:
  if y1-y0>.2:box(col,name,((x0+x1)/2,(y0+y1)/2,z),(x1-x0,y1-y0,t),mat)
sc=bpy.context.scene;sc.render.filepath=os.path.join(OUT,asset+'_revision_preview.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=path)
evpath=os.path.join(ROOT,'audit','build_batch_a2','materials_science_and_electrical_engineering_msee_evidence.json');ev=json.load(open(evpath,encoding='utf8'));ev.setdefault('revision_history',[]).append({'date':'2026-10-24','geometry_edits':['Removed the duplicate full-floor slabs at each schematic level and replaced them with south, east, and north gallery strips to keep the two-story atrium open.'],'materials':'Changed the MSEE facade to subtle concrete aggregate. Floor/origin/footprint dimensions remain unchanged.'});ev['validation']['revision_preview']=os.path.relpath(sc.render.filepath,ROOT).replace('/','\\');ev['validation']['atrium_floor_clearance']='Schematic floors cut around the full atrium glazing footprint';json.dump(ev,open(evpath,'w',encoding='utf8'),indent=2);print('MSEE patched',len(col.all_objects))
# Northwest Chiller concrete finish, same GIS shell and added rooftop plant remain.
asset='northwest_chiller_plant';path=os.path.join(ROOT,'modular','buildings',asset+'.blend');bpy.ops.wm.open_mainfile(filepath=path);col=next(c for c in bpy.data.collections if c.name=='Asset_'+asset)
for mat in bpy.data.materials:
 if mat.name.startswith(asset) and '_facade' in mat.name:concrete(mat,(.40,.42,.41))
sc=bpy.context.scene;sc.render.filepath=os.path.join(OUT,asset+'_revision_preview.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=path)
evpath=os.path.join(ROOT,'audit','build_batch_a2','northwest_chiller_plant_evidence.json');ev=json.load(open(evpath,encoding='utf8'));ev.setdefault('revision_history',[]).append({'date':'2026-10-24','geometry_edits':['Retained cooling-cell/fan/riser additions and fixed facade material to concrete utility-plant finish.'],'materials':'Fine aggregate concrete facade; dark painted-metal louvers and roof plant components.'});ev['validation']['revision_preview']=os.path.relpath(sc.render.filepath,ROOT).replace('/','\\');json.dump(ev,open(evpath,'w',encoding='utf8'),indent=2);print('NWCP patched',len(col.all_objects))

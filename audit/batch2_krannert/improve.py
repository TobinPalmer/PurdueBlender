import bpy, math, json, os
from mathutils import Vector
P=os.path.abspath('audit/batch2_krannert'); C=bpy.data.collections['Asset_krannert_building']; root=bpy.data.objects['AssetRoot_krannert_building']; origin=(234.5345001220703,-412.71900939941406)
before={o.name:[list(o.matrix_world@Vector(c)) for c in o.bound_box] for o in C.objects if o.type=='MESH'}
def material(n,c,rough=.7,noise=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=rough
 if noise:
  t=m.node_tree.nodes.new('ShaderNodeTexCoord'); q=m.node_tree.nodes.new('ShaderNodeTexNoise');q.inputs['Scale'].default_value=noise; m.node_tree.links.new(t.outputs['Geometry'] if 'Geometry' in t.outputs else t.outputs['Object'],q.inputs['Vector']); bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.0006;bump.inputs['Strength'].default_value=.25;m.node_tree.links.new(q.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],b.inputs['Normal'])
 return m
wood=material('KRAN_Photo_Oak',(0.43,.23,.075),.42,18);blue=material('KRAN_DrawingRoom_BlueFabric',(.055,.16,.29),.9,120);green=material('KRAN_DrawingRoom_LimeFabric',(.32,.43,.06),.9,120);steel=material('KRAN_Furniture_Chrome',(.43,.45,.46),.25);steel.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.8
carpet=material('KRAN_DrawingRoom_CharcoalCarpet',(.12,.13,.14),.95,100);paper=material('KRAN_BookPages',(.7,.68,.6));dark=material('KRAN_BookSpine_Blue',(.05,.11,.18));white=material('KRAN_Interior_WarmWhite',(.78,.76,.7))
def box(n,x,y,z,dx,dy,dz,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x-origin[0],y-origin[1],z));o=bpy.context.object;o.name='KRAN_New_'+n;o.dimensions=(dx,dy,dz);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection): c.objects.unlink(o)
 C.objects.link(o);o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.data.materials.append(m);o['layout_status']='inferred dimensions and XY; room identity and floor/photo furnishing types official tour PDF2026';return o
# Photo-supported furniture types on confirmed floor; XY remains explicitly inferred.
box('DrawingRoom_Carpet',220,-415,3.886,14,12,.025,carpet)
def chair(x,y,z,m):
 box('Seat',x,y,z+.46,.48,.48,.1,m);box('Back',x,y+.23,z+.8,.48,.08,.56,m)
 for a in [-.19,.19]:
  for b in [-.19,.19]:box('ChairLeg',x+a,y+b,z+.22,.025,.025,.44,steel)
for x in [215,219,223]:
 for y in [-418,-414]:
  box('DrawingRoom_OakTable',x,y,4.62,1.5,.85,.055,wood)
  for a in [-.62,.62]:box('TableLeg',x+a,y,4.24,.045,.6,.72,steel)
  chair(x-.4,y-.78,3.9,blue);chair(x+.4,y+.78,3.9,green)
  box('AcousticBlueDivider',x+1,y,4.6,.06,1.4,1.4,blue)
box('WindowStudyCounter',220,-420.4,4.93,12,.65,.07,white)
for x in [215,217,219,221,223,225]:chair(x,-419.6,4.2,blue)
# Low oak bookcases visible in official Parrish Library photo, floor2; inferred distribution.
for x in [215,220,225]:
 y=-416;z=8.55
 for a in [-1.2,1.2]:box('Parrish_OakUpright',x+a,y,z+.7,.06,.46,1.4,wood)
 for h in [0,.5,1,1.4]:box('Parrish_Shelf',x,y,z+h,2.46,.46,.035,wood)
 for h in [.03,.53]:
  for j in range(26):box('Parrish_Book',x-1.12+j*.086,y,z+h+.2,.065,.31,.38,dark if j%3 else green)
 for yy in [-418,-413]:
  box('Parrish_StudyDesk',x,yy,z+.74,1.6,.75,.05,wood);chair(x,yy-.65,z,blue)
# Fix the original material bug: existing bump distance default1m was excessive.
for m in bpy.data.materials:
 if not m.use_nodes:continue
 b=m.node_tree.nodes.get('Principled BSDF')
 if b:m.diffuse_color=b.inputs['Base Color'].default_value
 for nd in m.node_tree.nodes:
  if nd.type=='BUMP':nd.inputs['Distance'].default_value=.0006;nd.inputs['Strength'].default_value=.25
# limestone grain in local meter coordinates, no external image dependencies
m=bpy.data.materials.get('KRAN_Indiana_Limestone');m['texture_scale_status']='fine grain procedural approximation, not calibrated sample'
bpy.context.scene['interiors_status']='partial: Drawing Room F1 and Parrish F2 photo-supported furniture types; exact XY and dimensions inferred, remaining offices/classrooms unverified'
bpy.context.scene['batch2_source']='https://business.purdue.edu/undergraduate/visit/self-guided-tour.pdf retrieved2026-10-22'
assert all(k in bpy.data.objects for k in before)
json.dump({'before_objects':len(before),'after_objects':len(C.objects),'new_objects':len([o for o in C.objects if o.name.startswith('KRAN_New_')]),'missing_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not os.path.exists(bpy.path.abspath(i.filepath))]},open(P+'/checks.json','w'),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('modular/buildings/krannert_building.blend'))

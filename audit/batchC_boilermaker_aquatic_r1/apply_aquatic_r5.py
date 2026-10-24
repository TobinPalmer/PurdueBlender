import bpy
from pathlib import Path
from mathutils import Vector
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\morgan_j_burke_boilermaker_aquatic_center.blend')
bpy.ops.wm.open_mainfile(filepath=str(p)); asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']
old=bpy.data.collections.get('AQUA_R5_Context');
if old:
 for o in list(old.objects): bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.collections.remove(old)
ctx=bpy.data.collections.new('AQUA_R5_Context | approximate site dressing'); asset.children.link(ctx)
def material(name,color,rough=.8,metal=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;return m
concrete=bpy.data.materials.get('AQUA | cast concrete') or material('AQUA R5 | pale sidewalk concrete',(.43,.44,.42))
grass=material('AQUA R5 | campus grass context',(.095,.17,.065),.95)
asphalt=material('AQUA R5 | charcoal paved road context',(.105,.12,.12),.91)
leaf1=material('AQUA R5 | broadleaf canopy green',(.12,.23,.085),.9); leaf2=material('AQUA R5 | broadleaf canopy highlights',(.18,.29,.10),.92); trunk=material('AQUA R5 | tree bark',(.20,.105,.055),.95); shrubmat=material('AQUA R5 | low evergreen planting',(.105,.22,.075),.94)
def box(name,loc,dims,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 ctx.objects.link(o)
 if mat:o.data.materials.append(mat)
 return o
# Entry apron, front walk, and separate north-south approach path are modular schematic site context.
box('AQUA R5 | entry forecourt apron (schematic)',(0,57.4,-.07),(19,10,.18),concrete)
box('AQUA R5 | north sidewalk ribbon (schematic)',(0,63.6,-.11),(72,3.0,.18),concrete)
box('AQUA R5 | pedestrian approach path (schematic)',(0,73.4,-.12),(5.2,18.4,.16),concrete)
# Campus road edge as an approximate contextual strip, not a surveyed road alignment.
box('AQUA R5 | nearby campus roadway context (approximate)',(0,87.4,-.105),(120,10,.19),asphalt)
# Lawn beds anchor the approach without asserting planting positions or species.
box('AQUA R5 | north greenspace context',(0,72.0,-.17),(110,19,.06),grass)
for side in (-1,1):
 box('AQUA R5 | entry planting bed (schematic)',(side*23.5,58.5,-.10),(12,5.6,.14),grass)
# Two generic campus broadleaf trees sit at the outer ends of the rendered site context; individual species/placement are unverified.
for i,x in enumerate((-39,39),1):
 y=70.0
 bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.34,radius2=.21,depth=4.2,location=(x,y,1.9));o=bpy.context.object;o.name=f'AQUA R5 | generic context tree {i} trunk'
 for c in list(o.users_collection):c.objects.unlink(o)
 ctx.objects.link(o);o.data.materials.append(trunk)
 for j,(z,r,matleaf) in enumerate(((4.2,2.4,leaf1),(5.6,2.2,leaf2),(6.8,1.65,leaf1)),1):
  bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=(x+(j-2)*.45,y,z));crown=bpy.context.object;crown.name=f'AQUA R5 | generic context tree {i} crown {j}';crown.scale=(r,r*.88,r*.72);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  for c in list(crown.users_collection):c.objects.unlink(crown)
  ctx.objects.link(crown);crown.data.materials.append(matleaf)
# Low planted masses frame the paved forecourt; landscape layout is schematic.
for i,(x,y) in enumerate(((-28,59),(-22,59),(-16,59),(16,59),(22,59),(28,59)),1):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=1,location=(x,y,.42));o=bpy.context.object;o.name=f'AQUA R5 | generic low evergreen context shrub {i}';o.scale=(1.2,.72,.62);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 ctx.objects.link(o);o.data.materials.append(shrubmat)
bpy.ops.wm.save_as_mainfile(filepath=str(p));print('Saved optional approximate campus site context in dedicated collection:',len(ctx.objects),'objects')

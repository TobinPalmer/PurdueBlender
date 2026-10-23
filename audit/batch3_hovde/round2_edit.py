import bpy, math
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); f=P/'modular/buildings/hovde_hall.blend'; bpy.ops.wm.open_mainfile(filepath=str(f)); c=bpy.data.collections['Asset_hovde_hall']
# Triangle pediment, extruded through the portico depth. Existing front is +X.
o=bpy.data.objects['HOVD_Portico_Pediment_Base']; mat=o.data.materials[0]
verts=[]
for x in (-1.65,1.65): verts += [(x,-6.81,-1.6),(x,6.81,-1.6),(x,0,1.6)]
faces=[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
me=bpy.data.meshes.new('HOVD_Triangular_Pediment_Mesh'); me.from_pydata(verts,[],faces); me.materials.append(mat); me.update(); old=o.data;o.data=me
# modest limestone cornice ledges kept intact
# Replace visually weak rectangular shafts with round limestone shafts, bases and capitals, retaining the established six-column positions.
for i in range(1,7):
 old=bpy.data.objects.get(f'HOVD_Col_Shaft_{i}')
 if not old: continue
 x,y,z=old.location; h=old.dimensions.z; old.hide_render=True; old.hide_viewport=True
 def cyl(name, radius, depth, zc, verts=20):
  bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=(x,y,zc)); obj=bpy.context.object; obj.name=name; obj.data.materials.append(mat); 
  for coll in list(obj.users_collection): coll.objects.unlink(obj)
  c.objects.link(obj); return obj
 cyl(f'HOVD_Classical_Column_{i}',.63,h,z,24)
 cyl(f'HOVD_Column_Base_{i}',.92,.34,z-h/2+.17,24)
 cyl(f'HOVD_Column_Capital_{i}',.9,.42,z+h/2-.18,24)
# Red clay tile: verified in SAH campus design text, while noting it is contextual rather than a building-specific roof survey.
roof=bpy.data.objects['HOVD_Roof_Slab']; m=roof.data.materials[0]; m.diffuse_color=(.38,.075,.035,1); m.use_nodes=True
bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(.36,.055,.025,1); bs.inputs['Roughness'].default_value=.8
# understated staggered tile relief on the roof surface, spaced at broad overview scale
for row in range(1,9):
 y=-34+row*7.5
 for col in range(1,5):
  x=-9.5+col*3.8+(1.9 if row%2 else 0)
  if x>10: continue
  bpy.ops.mesh.primitive_cube_add(size=1, location=(x,y,16.78)); t=bpy.context.object;t.name=f'HOVD_Roof_TileHint_{row}_{col}';t.dimensions=(3.65,1.18,.055);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);t.data.materials.append(m)
  for coll in list(t.users_collection):coll.objects.unlink(t)
  c.objects.link(t)
# glazing readability: soften black pane by giving glass a blue-grey reflective, slightly transparent surface
for name in ['Solar_Ribbon_Glass']:
 m=bpy.data.materials.get(name)
 if m:
  m.diffuse_color=(.12,.22,.27,1)
  bs=m.node_tree.nodes.get('Principled BSDF') if m.node_tree else None
  if bs:
   bs.inputs['Base Color'].default_value=(.12,.22,.27,1);bs.inputs['Metallic'].default_value=.22;bs.inputs['Roughness'].default_value=.22;bs.inputs['IOR'].default_value=1.45
# Enclose named rooms with simple full-height inner walls; preserve openings on the public/circulation side.
wallmat=bpy.data.materials.get('Hovde_Plaster_Ivory')
def box(name,loc,dims,material):
 bpy.ops.mesh.primitive_cube_add(size=1, location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 for coll in list(o.users_collection):coll.objects.unlink(o)
 c.objects.link(o);return o
for tag,cy in [('Pres',-25),('Board',25)]:
 # walls approx 18m x 17m, 3.1m high, with broad opening across the camera side (south for pres, north for board)
 z=6.05; y0=cy-8.7; y1=cy+8.7
 box(f'HOVD_{tag}_Room_Wall_W',(-8.85,cy,z),(.22,17.2,3.3),wallmat)
 box(f'HOVD_{tag}_Room_Wall_E',(8.85,cy,z),(.22,17.2,3.3),wallmat)
 box(f'HOVD_{tag}_Room_Wall_Back',(0,y1,z),(17.5,.22,3.3),wallmat)
 # front wall two sections leave a 2.2m door centered
 box(f'HOVD_{tag}_Room_Wall_Front_L',(-5.9,y0,z),(5.8,.22,3.3),wallmat)
 box(f'HOVD_{tag}_Room_Wall_Front_R',(5.9,y0,z),(5.8,.22,3.3),wallmat)
 # doorway jambs, header and wood door leaf set open against the near jamb
 box(f'HOVD_{tag}_Room_Door_Header',(0,y0,7.45),(5.8,.24,.28),wallmat)
 box(f'HOVD_{tag}_Room_Door_Leaf',(-1.05,y0+.28,5.15),(.09,.06,2.3),bpy.data.materials.get('Hovde_Executive_Walnut'))
# Save and retain canonical scene/collection.
bpy.ops.wm.save_as_mainfile(filepath=str(f));print('saved',len(c.all_objects))

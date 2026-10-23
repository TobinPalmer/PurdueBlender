import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');f=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(f));c=bpy.data.collections['Asset_hovde_hall']
# Correct triangular pediment axis: facade width is local X; depth is local Y (object is rotated 90 degrees).
o=bpy.data.objects['HOVD_Portico_Pediment_Base'];m=o.data.materials[0]
verts=[]
for y in (-1.65,1.65): verts += [(-6.81,y,-1.6),(6.81,y,-1.6),(0,y,1.6)]
faces=[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
me=bpy.data.meshes.new('HOVD_Triangular_Pediment_Mesh');me.from_pydata(verts,[],faces);me.materials.append(m);me.update();o.data=me
# Reduce oversized office and boardroom shells and associated modeled furniture around their room centers.
for tag,cy in [('Pres',-25.0),('Board',25.0)]:
 for ob in c.all_objects:
  if not ob or not ob.name.startswith(f'HOVD_{tag}_'):continue
  fac=.72
  ob.location.x *= fac;ob.location.y=cy+(ob.location.y-cy)*fac;ob.location.z=4.4+(ob.location.z-4.4)*fac
  if ob.type=='MESH':ob.scale*=fac
  elif ob.type=='LIGHT':ob.data.energy*=.8
# Roof color moderately deeper red for clay tile treatment
roofmat=bpy.data.materials['Hovde_Roof_Membrane'];roofmat.diffuse_color=(.16,.016,.008,1);bs=roofmat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.16,.016,.008,1)
bpy.ops.wm.save_as_mainfile(filepath=str(f));print('corrected pediment orientation and room scale')

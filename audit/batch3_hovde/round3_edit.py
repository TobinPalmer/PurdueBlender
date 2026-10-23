import bpy, math
from mathutils import Vector, Matrix
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');f=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(f));c=bpy.data.collections['Asset_hovde_hall'];root=bpy.data.objects['HOVD_Root']
# Compact, deliberately conservative room-size pass (all related objects remain aligned to the existing asset root).
for tag,cy in [('Pres',-25.0),('Board',25.0)]:
 for o in c.all_objects:
  if not o:continue
  related=o.name.startswith(f'HOVD_{tag}_') or (tag=='Board' and o.name.startswith('HOVD_Chair_')) or (tag=='Pres' and o.name.startswith('HOVD_Chesterfield_Chair_'))
  if not related:continue
  fac=.70;o.location.x*=fac;o.location.y=cy+(o.location.y-cy)*fac;o.location.z=4.4+(o.location.z-4.4)*fac
  if o.type=='MESH':o.scale*=fac
  elif o.type=='LIGHT':o.data.energy*=.7
# Shrink and lower the rooftop access block. Positioning at the ridge remains a reconstruction estimate.
pent=bpy.data.objects['HOVD_Penthouse'];pent.location=(0,0,18.2);pent.scale=(.42,.35,.48)
louver=bpy.data.objects['HOVD_Penthouse_Louvers'];louver.location=(0,4.15,18.2);louver.scale=(.40,.4,.35)
# Remove the broad, floating rectangular course hints; use a fine tile shader across the roof instead.
for o in list(c.all_objects):
 if o and o.name.startswith('HOVD_Roof_TileHint_'):
  bpy.data.objects.remove(o,do_unlink=True)
# Build a low, restrained hipped roof overlay, supported by the red-clay campus palette but explicitly not a surveyed roof plan.
mat=bpy.data.materials['Hovde_Roof_Membrane'];mat.diffuse_color=(.20,.045,.018,1);mat.use_nodes=True
nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.20,.045,.018,1);bs.inputs['Roughness'].default_value=.76
tex=nodes.new('ShaderNodeTexCoord');brick=nodes.new('ShaderNodeTexBrick');brick.inputs['Color1'].default_value=(.24,.055,.022,1);brick.inputs['Color2'].default_value=(.16,.032,.013,1);brick.inputs['Mortar'].default_value=(.08,.045,.028,1);brick.inputs['Scale'].default_value=85;brick.inputs['Mortar Size'].default_value=.008;brick.inputs['Mortar Smooth'].default_value=.04;brick.inputs['Brick Width'].default_value=.55;brick.inputs['Row Height'].default_value=.24
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.035;links.new(tex.outputs['Generated'],brick.inputs['Vector']);links.new(brick.outputs['Color'],bs.inputs['Base Color']);links.new(brick.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
# Hipped planes: eaves at roof slab, low ridge along the long axis.
verts=[(-10.7,-35.4,16.72),(10.7,-35.4,16.72),(10.7,35.4,16.72),(-10.7,35.4,16.72),(0,-24.7,17.62),(0,24.7,17.62)]
faces=[(0,1,4),(3,5,2),(0,4,5,3),(1,2,5,4)]
mesh=bpy.data.meshes.new('HOVD_Inferred_Hipped_Roof_Mesh');mesh.from_pydata(verts,[],faces);mesh.materials.append(mat);mesh.update();obj=bpy.data.objects.new('HOVD_Inferred_Hipped_Roof',mesh);c.objects.link(obj);obj.parent=root;obj.matrix_parent_inverse.identity()

# Reduce glare/value mismatch: lower procedural limestone ramp and use consistent Principled base for brick.
stone=bpy.data.materials['Bedford_Indiana_Limestone'];stone.diffuse_color=(.62,.57,.47,1);sbs=stone.node_tree.nodes.get('Principled BSDF');sbs.inputs['Base Color'].default_value=(.62,.57,.47,1)
ramp=next((n for n in stone.node_tree.nodes if n.bl_idname=='ShaderNodeValToRGB'),None)
if ramp:
 ramp.color_ramp.elements[0].color=(.54,.50,.42,1);ramp.color_ramp.elements[1].color=(.64,.59,.49,1)
brickmat=bpy.data.materials['Purdue_Red_Brick'];brickmat.diffuse_color=(.30,.065,.027,1)
# Add a subtle but visible masonry/window frame detail: a single combined mesh of bronze sash rails/muntins.
frame=bpy.data.materials.get('Hovde_Bronze_Metal');verts=[];faces=[]
def append_box(center,dims,matx):
 start=len(verts);hx,hy,hz=[d*.5 for d in dims]
 pts=[(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),(-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
 for p in pts:verts.append(tuple(matx @ Vector(p)))
 for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:faces.append(tuple(start+i for i in q))
windows=[o for o in c.all_objects if o and o.name.startswith('HOVD_Win_') and o.type=='MESH']
for w in windows:
 # narrow the pane slightly so the frame is visible without shifting its opening
 w.scale.y*=.88;w.scale.z*=.90
 for yy,zz,dy,dz in [(0,0,.075,2.12),(0,0,1.95,.075),(-.96,0,.075,2.12),(.96,0,.075,2.12),(0,-1.02,1.92,.06),(0,1.02,1.92,.06)]:
  # local frame bar centered just proud of the glass plane
  mtx=w.matrix_local @ Matrix.Translation(Vector((-.13,yy,zz))) @ Matrix.Diagonal((1,1,1,1))
  append_box(Vector((0,0,0)),(.10,dy,dz),mtx)
frame_mesh=bpy.data.meshes.new('HOVD_Window_Sash_Detail_Mesh');frame_mesh.from_pydata(verts,[],faces);frame_mesh.materials.append(frame);frame_mesh.update();frame_obj=bpy.data.objects.new('HOVD_Window_Sash_Detail',frame_mesh);c.objects.link(frame_obj);frame_obj.parent=root;frame_obj.matrix_parent_inverse.identity()
# Ensure key scene/collection survives and save only the assigned building asset.
bpy.ops.wm.save_as_mainfile(filepath=str(f));print('saved round3',len(c.all_objects),'windows',len(windows))


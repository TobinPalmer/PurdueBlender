"""Add a qualitative rooftop service-equipment cluster where overhead imagery shows equipment.
Unit type/count/placement are illustrative; no as-built mechanical plan was found.
"""
import bpy, math
from pathlib import Path
ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); blend=ROOT/'modular/buildings/niswonger_aviation_tech.blend'
asset=bpy.data.collections['Asset_niswonger_aviation_tech']
# Clear an earlier R4 trial, preserving the one-object asset boundary.
for ob in list(asset.objects):
 if ob.name=='NISW_R4_Roof_HVAC_Cluster':bpy.data.objects.remove(ob,do_unlink=True)
def mat(name,color,metal,rough):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;return m
pad=mat('NISW_R4_Mechanical_Curb',(.29,.31,.32),.22,.58)
casing=mat('NISW_R4_Mechanical_Casing',(.48,.50,.49),.28,.42)
louver=mat('NISW_R4_Mechanical_Louver',(.13,.16,.17),.35,.5)
fanmat=mat('NISW_R4_Mechanical_Fan',(.21,.24,.25),.48,.38)
for m in (pad,casing,louver,fanmat):m['source_basis']='Generic equipment details qualitatively placed from the visible rooftop equipment cluster in Esri World Imagery z20; equipment models, count, dimensions, and exact local placement are illustrative and unverified.'
parts=[]
# The flat classroom plate slopes 0.12 m across its 36.54 m x span.
def roof_z(x):return 7.84-.12*(x+31.7)/(4.84+31.7)
def box(name, loc, dims, material, bevel=0.04):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:
  b=o.modifiers.new('Manufactured corner radius','BEVEL');b.width=bevel;b.segments=3;n=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');n.keep_sharp=True
 parts.append(o);return o
# Three compact rooftop AHU-like housings in a single eastern service zone.
# Keep them inside the approximate classroom roof plate. The orthophoto shows a dense equipment group near this side.
centers=[-3.25,-.15,2.95]; cy=37.6
for i,cx in enumerate(centers,1):
 z=roof_z(cx)
 box(f'R4_AHU_{i}_Curb',(cx,cy,z+.11),(2.55,3.15,.20),pad,.035)
 base=z+.20
 box(f'R4_AHU_{i}_Casing',(cx,cy,base+.69),(2.24,2.82,1.18),casing,.09)
 # South-facing intake louvers: eight narrow horizontal vanes per unit.
 for j in range(8):
  zz=base+.19+j*.105
  box(f'R4_AHU_{i}_IntakeVane_{j+1}',(cx,cy-1.425,zz),(1.64,.035,.035),louver,.008)
 # Two low fan housings on top, each with a dark protective grille/central hub.
 for k,dy in enumerate((-.64,.64),1):
  fz=base+1.31
  bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.37,depth=.16,location=(cx,cy+dy,fz)); fan=bpy.context.object;fan.name=f'R4_AHU_{i}_FanHousing_{k}';fan.data.materials.append(fanmat)
  b=fan.modifiers.new('Rounded fan housing','BEVEL');b.width=.025;b.segments=2;n=fan.modifiers.new('Weighted normals','WEIGHTED_NORMAL');n.keep_sharp=True;parts.append(fan)
  bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.07,depth=.025,location=(cx,cy+dy,fz+.09));hub=bpy.context.object;hub.name=f'R4_AHU_{i}_FanHub_{k}';hub.data.materials.append(casing);parts.append(hub)
  # Four grille bars per fan, simple flat stainless rails that read from the aerial/high view.
  for q,angle in enumerate((0,math.pi/4,math.pi/2,3*math.pi/4)):
   bpy.ops.mesh.primitive_cube_add(size=1,location=(cx,cy+dy,fz+.104));g=bpy.context.object;g.name=f'R4_AHU_{i}_FanGrille_{k}_{q}';g.dimensions=(.66,.022,.018) if q%2==0 else (.022,.66,.018);g.rotation_euler[2]=angle if q%2==1 else 0;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);g.data.materials.append(louver);parts.append(g)
# A small shared supply duct / transition box along the north side of the array.
box('R4_AHU_Shared_Duct',(0.0,40.0,roof_z(0.0)+.32),(7.5,.48,.48),pad,.05)
# Join all added parts into one named building-local export mesh to keep the manifest delta minimal.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:
 o.select_set(True);bpy.context.view_layer.objects.active=o
 # Apply bevel modifiers to make one portable mesh with explicit rounded geometry.
 for mod in list(o.modifiers):
  try:bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
  except:pass
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
cluster=bpy.context.object;cluster.name='NISW_R4_Roof_HVAC_Cluster'
for c in list(cluster.users_collection):c.objects.unlink(cluster)
asset.objects.link(cluster)
cluster['source_basis']='Esri World Imagery z20 shows a clustered rooftop service/equipment zone on the east/northeast side of the classroom addition. Purdue 2019 airport project record confirms HVAC work at Niswonger, without locating specific units.'
cluster['extent_status']='Illustrative cluster footprint placed in the approximate northeast zone; exact coordinates/count/dimensions/type unverified because the orthophoto cannot be precisely registered to the asset-local XY axes and no mechanical roof plan was found.'
cluster['detail_status']='Generic curb-mounted AHU-like boxes, louver faces, two fan housings each; not asserted as actual equipment model or as-built count.'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
print('Added one joined HVAC cluster object with',len(parts),'source parts to',cluster.name)

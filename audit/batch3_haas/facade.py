import bpy,math,json
from pathlib import Path
from mathutils import Vector
fp=bpy.data.filepath;c=bpy.data.collections['Asset_felix_haas_hall'];D=Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas');added=[]
def mat(n,col):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*col,1);return m
stone=mat('HAAS_Photo_Limestone',(.54,.50,.41));glass=mat('HAAS_Photo_BlueGlass',(.035,.09,.14));g=glass.node_tree.nodes.get('Principled BSDF');g.inputs['Metallic'].default_value=.25;g.inputs['Roughness'].default_value=.17
roof=mat('HAAS_Photo_DarkRoof_estimated',(.07,.065,.055));bpy.data.objects['HAAS_Corrected_GIS_Roof_Slab'].data.materials.clear();bpy.data.objects['HAAS_Corrected_GIS_Roof_Slab'].data.materials.append(roof)
def box(n,loc,sz,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='HAAS_Photo_'+n;o.dimensions=sz;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(m);added.append(o.name);return o
# Registered east entrance wing; dimensions estimated from qualitative official photo.
for yy in [-11.1,-4.5,4.5,11.1]:
 box('Pier_'+str(yy),(13.04,yy,5.95),(.3,.88,9.6),stone)
 for z in [1.3,4.3,9.9]:box('Capital_'+str(yy)+'_'+str(z),(13.15,yy,z),(.42,1.1,.28),stone)
for z in [1.15,4.3,9.9,10.2]:box('Band_'+str(z),(13.05,0,z),(.24,23.8,.24 if z!=1.15 else .7),stone)
# Real recess openings through existing shell. Arched trim carries curve rather than a rectangular patch.
for yy in [-7.65,0,7.65]:
 for zz,hh,ww in [(7.7,1.6,3.2),(3.1,3.2,3.0)]:
  if yy==0 and zz==3.1:ww=2
  cutter=box('Cut',(12.9,yy,zz),(1.5,ww,hh),stone)
  for target in [bpy.data.objects.get('HAAS_Corrected_GIS_Wall_Envelope'),bpy.data.objects.get('HAAS_Brick_Wall_East')]:
   if target:
    bpy.context.view_layer.objects.active=target;mod=target.modifiers.new('Photo_window_recess','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
    try:bpy.ops.object.modifier_apply(modifier=mod.name)
    except:pass
  bpy.data.objects.remove(cutter,do_unlink=True)
  box('Glazing_'+str(yy)+'_'+str(zz),(12.79,yy,zz),(.06,ww-.12,hh-.12),glass)
  for y in [yy-ww/2-.09,yy+ww/2+.09]:box('Jamb',(13.12,y,zz),(.26,.18,hh+.2),stone)
  for z in [zz-hh/2-.08,zz+hh/2+.08]:box('LintelSill',(13.12,yy,z),(.26,ww+.36,.18),stone)
  for y in [yy-ww/6,yy+ww/6]:box('Mullion',(12.88,y,zz),(.09,.05,hh),stone)
  box('Transom',(12.88,yy,zz+.2),(.09,ww,.06),stone)
  if zz==3.1:
   curve=bpy.data.curves.new('Arch','CURVE');curve.dimensions='3D';curve.bevel_depth=.11;curve.bevel_resolution=3;s=curve.splines.new('POLY');s.points.add(24)
   for i,p in enumerate(s.points):
    t=math.pi*i/24;p.co=(13.14,yy+ww/2*math.cos(t),zz+hh/2-.18+.65*math.sin(t),1)
   o=bpy.data.objects.new('HAAS_Photo_ArchedTrim',curve);c.objects.link(o);curve.materials.append(stone)
bpy.ops.wm.save_as_mainfile(filepath=fp)
(D/'facade_changes.json').write_text(json.dumps({'added':added,'source':'https://events.purdue.edu/felix_haas_hall','limits':'East entrance qualitative photo reconstruction, estimated dimensions; remaining facades unverified'},indent=2))

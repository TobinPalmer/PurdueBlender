import bpy, math, shutil, json
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter');shutil.copy2(P,D/'round7_before_rail_rebuild.blend');bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];col=bpy.data.collections['POTR_Historic2016_StairRails_Estimate']
for ob in list(bpy.data.objects):
 if ob.name.endswith('_Handrails'):bpy.data.objects.remove(ob,do_unlink=True)
mat=bpy.data.materials.get('POTR_Stair_Rail_Metal') or bpy.data.materials.new('POTR_Stair_Rail_Metal');mat.diffuse_color=(.065,.075,.085,1);mat.use_nodes=True;bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.065,.075,.085,1);bs.inputs['Metallic'].default_value=.68;bs.inputs['Roughness'].default_value=.36
centers=[(49.8,1.5),(49.9,53.4),(10.5,35.2)];levels=[(-3.914,.7596),(.7596,5.0268),(5.0268,9.294),(9.294,13.4112)];stats=[]
for ci,(x,y) in enumerate(centers,1):
 for li,(z0,z1) in enumerate(levels):
  if ci<3 and li==3:continue
  cu=bpy.data.curves.new(f'POTR_R7_Core{ci}_Level{li}_Refined_Rails','CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=.018;cu.bevel_resolution=3
  run=2.7;width=1.05;half=(z1-z0)/2
  def add_line(points):
   sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
   for p,co in zip(sp.points,points):p.co=(*co,1)
  for f in range(2):
   if f==0:x0,x1=x-run/2,x+run/2;za,zb=z0,z0+half;yc=y-width/2
   else:x0,x1=x+run/2,x-run/2;za,zb=z0+half,z1;yc=y+width/2
   for yy in [yc-width/2,yc+width/2]:
    # Short, independent handrail segments terminate over the landing; they no longer sweep diagonally across the adjacent flight.
    add_line([(x0,yy,za+.98),(x1,yy,zb+.98)])
    for idx in [0,3,7,11]:
     frac=(idx+.5)/12;xx=x0+(x1-x0)*frac;zz=za+(zb-za)*frac+((zb-za)/12)*.5
     add_line([(xx,yy,zz+.04),(xx,yy,zz+.98)])
  ob=bpy.data.objects.new(f'POTR_2016_StairCore{ci}_Level{li}_Handrails',cu);col.objects.link(ob);ob.data.materials.append(mat);ob['source']='Estimated rail positions derived from modeled 2016-core stair treads; individual flights terminate at the landing, with no unsupported cross-flight sweep.';ob['clear_flight_width_m']=round(width-2*.018,3);stats.append(ob.name)
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));print(json.dumps({'reopened':True,'handrail_objects':len(stats),'names':stats,'material_base_color':list(bs.inputs['Base Color'].default_value)},indent=2))

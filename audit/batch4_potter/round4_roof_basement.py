import bpy,math,shutil,bmesh,json
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter');BASE=D/'round2.blend'
shutil.copy2(P,D/'round3.blend');bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering']
# Restore the documented full roof deck, then keep the upper stair opening only at 4S04/S03, which is the core shown at the penthouse level on the existing plan.
with bpy.data.libraries.load(str(BASE),link=False) as (src,dst): dst.meshes=['POTR_Official_864_Roof']
base_mesh=dst.meshes[0];roof=c.objects['POTR_Official_864_Roof'];roof.data=base_mesh
mem=bpy.data.materials.get('POTR_Current_Roof_Membrane_Estimate')
if mem and mem.name not in [m.name for m in roof.data.materials if m]:roof.data.materials.append(mem)
# Difference only the 3S03/4S04 core aperture at the penthouse floor; no unsupported upper stairs at S01/S02.
x,y=10.5,35.2
bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,14.5));cut=bpy.context.object;cut.name='TEMP_4S04_Roof_Aperture';cut.dimensions=(4.6,3.6,2.2);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
mod=roof.modifiers.new('Historic 4S04 penthouse stair opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=roof;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
roof['stair_openings']='Only 4S04/S03 core opening retained at penthouse level per 2016 Existing Penthouse plan; dimensions approximate.'
# Remove unsupported transitions at S01/S02 into the penthouse: the 2016 plan only shows a stair label at 4S04.
for ci in (1,2):
 for suffix in ('Flight','UpperLanding','Handrails'):
  name=f'POTR_2016_StairCore{ci}_Level3_{suffix}';o=bpy.data.objects.get(name)
  if o:bpy.data.objects.remove(o,do_unlink=True)
# Add separate, clearly tagged 4S04 stair enclosure adjoining Room 401. The 2016 plan labels the core but not dimensions; size/door clear width are illustrative.
col4=bpy.data.collections.get('POTR_Historic2016_4S04_Enclosure_Estimate')
if not col4:col4=bpy.data.collections.new('POTR_Historic2016_4S04_Enclosure_Estimate');c.children.link(col4)
paint=bpy.data.materials.get('POTR_Interior_Warm_OffWhite') or bpy.data.materials.get('POTR_2016_Lab205_Enamel')
if not paint:paint=bpy.data.materials.new('POTR_Interior_Warm_OffWhite');paint.diffuse_color=(.76,.75,.70,1);paint.use_nodes=True;next(n for n in paint.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(.76,.75,.70,1)
def make_box(name,loc,dim):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for cc in list(o.users_collection):cc.objects.unlink(o)
 col4.objects.link(o);o.data.materials.append(paint);o['source']='2016 Potter renovation study, Existing Penthouse plan (printed p.45), label 4S04; dimensions and access opening estimated.';return o
# enclosure interior 5.5m x 6.7m, rising from estimated penthouse floor to roof; doorway faces Room 401 toward +X.
cx,cy=12.45,35.3;z0=13.4112;z1=15.50;th=.18;wx=5.5;wy=6.7;h=z1-z0;zc=(z0+z1)/2
make_box('POTR_4S04_Wall_West',(cx-wx/2,cy,zc),(th,wy,h))
make_box('POTR_4S04_Wall_North',(cx,cy+wy/2,zc),(wx,th,h))
make_box('POTR_4S04_Wall_South',(cx,cy-wy/2,zc),(wx,th,h))
# east wall lintel and side returns leave a 0.9 m estimated doorway toward the Room401 mass.
make_box('POTR_4S04_EastWall_North',(cx+wx/2,cy+1.3,zc),(th,4.1,h))
make_box('POTR_4S04_EastWall_South',(cx+wx/2,cy-1.3,zc),(th,4.1,h))
make_box('POTR_4S04_EastDoor_Lintel',(cx+wx/2,cy,z1-.12),(th,.9,.24))
# Bottom landings at the modeled basement-floor start for all three stair runs; they rest on the basement slab, rather than cutting through it.
landingmat=bpy.data.materials['POTR_Interior_Concrete_Stairs']
for ci,(sx,sy) in enumerate([(49.8,1.5),(49.9,53.4),(10.5,35.2)],1):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(sx-2.05,sy,-3.984));o=bpy.context.object;o.name=f'POTR_2016_StairCore{ci}_Basement_Landing_Estimate';o.dimensions=(.7,2.1,.16);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(landingmat);o['source']='Landing at estimated lower-level stair termination inferred from 2016 lower-level plan; exact BS-core registration unverified.'
# Give the T-shaped penthouse roof plate a modest thickness rather than leaving a zero-thickness plane.
plate=c.objects['POTR_Historic2016_Room401_Penthouse_Roof'];mod=plate.modifiers.new('Estimated 150mm roof build-up','SOLIDIFY');mod.thickness=.15;mod.offset=-1;bpy.context.view_layer.objects.active=plate;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering']
print(json.dumps({'objects':len(c.all_objects),'root':list(c.objects['AssetRoot_potter_engineering'].location),'shell_xy':list(c.objects['POTR_Official_864_Structural_Envelope'].dimensions[:2]),'roof_openings':3,'removed_upper_stairs_12':True,'4S04_enclosure':len(c.children['POTR_Historic2016_4S04_Enclosure_Estimate'].objects),'bottom_landings':len([o for o in c.objects if 'Basement_Landing' in o.name]),'penthouse_roof_thickness':list(c.objects['POTR_Historic2016_Room401_Penthouse_Roof'].dimensions)},indent=2))

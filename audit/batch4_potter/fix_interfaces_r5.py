import bpy,json
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering']
# Correct the 4S04 doorway returns so neither wall overlaps its 0.9m opening.
for name,y,depth in [('POTR_4S04_EastWall_North',37.2,2.9),('POTR_4S04_EastWall_South',33.4,2.9)]:
 o=bpy.data.objects[name];o.location.y=y;o.dimensions.y=depth;bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
# Lift integrated mid-landings 20 mm into the second flight so the last first-flight and first return-flight treads overlap the platform.
centers=[(49.8,1.5),(49.9,53.4),(10.5,35.2)]
for i,(x,y) in enumerate(centers,1):
 for level in range(4):
  o=c.objects.get(f'POTR_2016_StairCore{i}_Level{level}_Flight')
  if not o:continue
  for v in o.data.vertices[-8:]:v.co.z+=.02
  o.data.update();o['mid_landing_interface']='Plate widened to overlap both flights and raised 20mm into return-flight first tread.'
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];mass=c.objects['POTR_Historic2016_Room401_Penthouse_Massing'];checks=[]
for y in [35.3,34.7,35.9]:
 hit,loc,no,idx=mass.ray_cast(Vector((14.5,y,14.4)),Vector((1,0,0)),distance=1.5);checks.append({'y':y,'room401_boundary_blocks_ray':bool(hit)})
print(json.dumps({'objects':len(c.all_objects),'door_center_open':not checks[0]['room401_boundary_blocks_ray'],'door_sides_have_wall':checks[1:],'root':list(c.objects['AssetRoot_potter_engineering'].location)},indent=2))

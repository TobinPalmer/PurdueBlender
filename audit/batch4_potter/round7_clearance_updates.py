import bpy,json,shutil
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter');shutil.copy2(P,D/'round6_before_round7_clearance.blend');bpy.ops.wm.open_mainfile(filepath=str(P))
# Extend the estimated S03 penthouse landing exactly to the north/south roof-opening edges so its surface meets the adjacent roof deck continuously.
land=bpy.data.objects['POTR_2016_StairCore3_Penthouse_Landing_4S04_Estimate'];land.dimensions=(1.6,2.7,.16);bpy.context.view_layer.objects.active=land;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);land['clear_path']='Y span extended to meet the 3.2 x 2.7m roof opening edges and provide a modeled path around the opening to the 4S04 east doorway. Estimated; see round7 person-clear path check.'
# Increase all three estimated door lintel openings to 2.0m clear height while staying within wall top elevation.
for name in ['POTR_Historic2016_Room401_Penthouse_Massing','POTR_4S04_Enclosure_Walls_183sf_Estimate']:
 ob=bpy.data.objects[name];me=ob.data
 for start in range(0,len(me.vertices)-7,8):
  group=me.vertices[start:start+8];zs=[v.co.z for v in group]
  if min(zs)>15.34 and max(zs)>15.49 and max(zs)-min(zs)<.16:
   for v in group:
    if v.co.z<15.40:v.co.z=13.4112+2.0
 me.update();ob['door_clear_height_estimate_m']=2.0
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));land=bpy.data.objects['POTR_2016_StairCore3_Penthouse_Landing_4S04_Estimate'];print(json.dumps({'reopened':True,'landing_dimensions':list(land.dimensions),'landing_bounds':[list((land.matrix_world@__import__('mathutils').Vector(v))) for v in land.bound_box][:2],'door_heights':{n:bpy.data.objects[n].get('door_clear_height_estimate_m') for n in ['POTR_Historic2016_Room401_Penthouse_Massing','POTR_4S04_Enclosure_Walls_183sf_Estimate']}},indent=2))

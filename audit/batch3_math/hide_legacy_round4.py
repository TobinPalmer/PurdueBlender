import bpy,json
from pathlib import Path
src=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/math_sciences.blend')
c=bpy.data.collections['Asset_math_sciences']; keep={'MATH_Lib_Floor_Terrazzo','MATH_Lib_Border_Terrazzo','MATH_Lib_Wall_East','MATH_Lib_Wall_South','MATH_Lib_Wall_North','MATH_Lib_Ceiling'}
hidden=[]
for o in c.all_objects:
 if o and o.name.startswith('MATH_Lib_') and o.name not in keep:
  o.hide_render=True; o.hide_viewport=True
  o['source_status']='Legacy illustrative interior duplicate hidden after replacement by the 2026 reviewed library furniture/partition set.'
  hidden.append(o.name)
bpy.ops.wm.save_as_mainfile(filepath=str(src))
Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_math/legacy_interior_visibility_round4.json').write_text(json.dumps({'hidden_legacy_duplicate_count':len(hidden),'hidden_objects':hidden,'retained':sorted(keep)},indent=2))
print('ROUND4_HIDDEN',len(hidden))

import bpy, json
from pathlib import Path
p=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/math_sciences.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
print(json.dumps({'reopened':True,'sign_present':bool(bpy.data.objects.get('MATH_Signage_East')),'asset_collection':bool(bpy.data.collections.get('Asset_math_sciences')),'direct_objects':len(bpy.data.collections['Asset_math_sciences'].all_objects)}))

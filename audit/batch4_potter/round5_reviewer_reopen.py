import bpy,json,os
from pathlib import Path
from mathutils import Vector
p=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter');bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;c=bpy.data.collections['Asset_potter_engineering'];
scene_only=[o.name for o in s.objects if o.name not in c.all_objects and o.name.startswith('POTR_')]
out={'scene_only_potr_named_objects':scene_only,'exterior_time':os.path.getmtime(D/'exterior_current.png'),'cutaway_time':os.path.getmtime(D/'stairwell_cutaway.png'),'blend_time':os.path.getmtime(p),'current_scene_object_count':len(s.objects),'collection_object_count':len(c.all_objects),'root_location':list(c.objects['AssetRoot_potter_engineering'].location),'external_unpacked_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file]}
for i in range(1,4):
 f=c.objects[f'POTR_2016_StairCore{i}_Level0_Flight'];l=c.objects[f'POTR_2016_StairCore{i}_Basement_Landing_Estimate'];out.setdefault('basement_landing_checks',[]).append({'core':i,'flight_bounds':[[round(min((f.matrix_world@v.co)[j] for v in f.data.vertices),3) for j in range(3)],[round(max((f.matrix_world@v.co)[j] for v in f.data.vertices),3) for j in range(3)]],'landing_bounds':[[round(min((l.matrix_world@v.co)[j] for v in l.data.vertices),3) for j in range(3)],[round(max((l.matrix_world@v.co)[j] for v in l.data.vertices),3) for j in range(3)]],'note':'AABB overlap does not establish clear walking surface or corridor connection'})
(D/'round5_reviewer_reopen_checks.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

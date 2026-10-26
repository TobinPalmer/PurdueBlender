import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=str(Path('modular/buildings/massing_purdue_graduate_student_center_af9c5c7.blend').resolve()))
c=bpy.data.collections['Asset_massing_purdue_graduate_student_center_af9c5c7'];objects=list(c.all_objects);used={m.name for o in objects for m in getattr(o.data,'materials',[]) if m};out={'object_count':len(objects),'mesh_count':sum(o.type=='MESH' for o in objects),'used_materials':sorted(used),'external_unpacked_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and i.packed_file is None]};Path('audit/purdue_graduate_student_center/independent_grade_master/asset_material_probe.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))

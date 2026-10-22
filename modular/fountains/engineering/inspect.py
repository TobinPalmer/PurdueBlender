import bpy,json
from pathlib import Path
p=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
bpy.ops.wm.open_mainfile(filepath=str(p/'modular_source_snapshot.blend'))
c=bpy.data.collections['08_Engineering_Fountain_and_Mall']
rows=[{'name':o.name,'location':list(o.location),'dimensions':list(o.dimensions)} for o in c.all_objects]
(p/'modular/fountains/engineering/source_inventory.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows))

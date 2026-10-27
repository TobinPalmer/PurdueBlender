import bpy, json
from pathlib import Path
p=Path(bpy.data.filepath).resolve()
names=['Placement_flex_lab','Placement_flex_lab']
items=[]
for name in names:
 o=bpy.data.objects.get(name)
 if o: items.append({'name':o.name,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'matrix_world':[list(r) for r in o.matrix_world]})
print(json.dumps({'blend':str(p),'scene':bpy.context.scene.name,'marker':items},indent=2))
Path('audit/flex_lab/independent_grade_r2/master_placement_probe.json').write_text(json.dumps({'blend':str(p),'scene':bpy.context.scene.name,'marker':items},indent=2)+'\n')

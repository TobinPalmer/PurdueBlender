import bpy,json
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');m=json.loads((P/'modular/manifest.json').read_text());d=P/'audit/walc_south/corrections.json';r=json.loads(d.read_text())
for a in m['assets']:
 if a['id'] not in ['math_sciences','felix_haas_hall','stanley_coulter_hall']:continue
 fp=P/'modular'/a['file'];bpy.ops.wm.open_mainfile(filepath=str(fp));ref=bpy.data.collections.get('Reference_Incompatible_Geometry_'+a['id']);dest=bpy.data.collections[a['collection']];restored=[]
 for ob in list(ref.objects):
  if any(s in ob.name for s in ['Algorithm','Equation','SC_Portico_3D_Text']):ref.objects.unlink(ob);dest.objects.link(ob);restored.append(ob.name)
 for row in r:
  if row['id']==a['id']:
   for field in ['additional_hidden_floating_labels','removed_unsupported_site_overlay']:
    if field in row:row[field]=[x for x in row[field] if x not in restored]
 bpy.ops.wm.save_as_mainfile(filepath=str(fp))
d.write_text(json.dumps(r,indent=2))

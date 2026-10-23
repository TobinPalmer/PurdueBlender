import bpy,json,bmesh
from pathlib import Path
P=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend'
bpy.ops.wm.open_mainfile(filepath=P)
c=bpy.data.collections['Asset_potter_engineering']
items=[]
for o in c.all_objects:
 if any(s in o.name for s in ['Room401','4S04','Official_864_Roof','StairCore3','Basement_Landing']):
  items.append({'name':o.name,'type':o.type,'loc':list(o.location),'dim':list(o.dimensions),'bbox':[[min(v[i] for v in o.bound_box) for i in range(3)],[max(v[i] for v in o.bound_box) for i in range(3)]],'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'props':{k:o[k] for k in o.keys() if k not in ['_RNA_UI']}})
print(json.dumps({'version':bpy.app.version_string,'root':list(c.objects['AssetRoot_potter_engineering'].location),'shell':list(c.objects['POTR_Official_864_Structural_Envelope'].dimensions),'selected':items},indent=2))

import bpy,json
from pathlib import Path
out=[]
for name in ['LAMB | schematic overhead linear luminaires','LAMB | GIS-registered archival-dimension fieldhouse roof (R7 hypothesis)','LAMB | round6 fieldhouse arch purlins','LAMB | round6 trusses fitted to archival fieldhouse span','LAMB | Stadium sidewalk round4','LAMB | Stadium curb round4','LAMB | Stadium Avenue roadway round4','LAMB | R8 event detail review camera','LAMB | interior review camera']:
 o=bpy.data.objects.get(name);out.append({'name':name,'exists':bool(o),'type':o.type if o else None,'loc':list(o.location) if o else None,'dims':list(o.dimensions) if o else None,'hide_render':o.hide_render if o else None,'hide_viewport':o.hide_viewport if o else None,'hide_get':o.hide_get() if o else None,'collections':[c.name for c in o.users_collection] if o else [],'mat_details':[]})
 if o and getattr(o.data,'materials',None):
  for m in o.data.materials:
   if not m:continue
   d={'mat':m.name,'blend_method':getattr(m,'blend_method',None)}
   if m.use_nodes:
    for n in m.node_tree.nodes:
     if n.type=='BSDF_PRINCIPLED':d['inputs']={x.identifier: list(x.default_value) if hasattr(x.default_value,'__len__') and not isinstance(x.default_value,str) else x.default_value for x in n.inputs if x.identifier in ['Alpha','Base Color','Metallic','Roughness','Emission Color','Emission Strength']}
   out[-1]['mat_details'].append(d)
Path('audit/lambert_fieldhouse/inspect_r8_render.json').write_text(json.dumps(out,indent=2),encoding='utf-8'); print(json.dumps(out,indent=2))

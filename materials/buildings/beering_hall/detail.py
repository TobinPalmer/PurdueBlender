import bpy
from collections import Counter
c=bpy.data.collections['Asset_beering_hall']
for m in bpy.data.materials:
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); print(m.name, list(p.inputs['Base Color'].default_value),p.inputs['Roughness'].default_value, p.inputs['Metallic'].default_value, sum(1 for o in c.all_objects if o.type=='MESH' and m in list(o.data.materials)))
for o in c.all_objects:
 if o.type=='MESH' and ('Masonry' in o.name or 'Dome' in o.name or 'Plaza' in o.name):print(o.name,list(o.location),list(o.dimensions),list(o.scale))

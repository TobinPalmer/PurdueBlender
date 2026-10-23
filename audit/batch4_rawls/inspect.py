import bpy, json
from mathutils import Vector
out=[]
for o in bpy.data.collections['Asset_rawls_hall'].all_objects:
    if o.name.startswith('RAWL_2026_'):
        out.append({'n':o.name,'loc':[round(x,3) for x in o.location], 'dim':[round(x,3) for x in o.dimensions], 'rot':round(o.rotation_euler.z,3), 'mat':[m.name for m in o.data.materials] if o.type=='MESH' else []})
print('N2026',len(out))
print(json.dumps(out,indent=2))
for name in ['RAWL_Footprint_Reference_Wire','RAWL_FloorSlab_L1_Ground','RAWL_Site_Sidewalk_Apron','RAWL_Masonry_Exterior_Walls']:
 o=bpy.data.objects.get(name);print('SPECIAL',name, o.type if o else None, len(o.data.vertices) if o and o.type=='MESH' else 0, len(o.data.polygons) if o and o.type=='MESH' else 0)

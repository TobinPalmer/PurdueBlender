import bpy, json
from mathutils import Vector

names=["ARMS_Cantilever_Canopy_Deck","ARMS_Canopy_Fascia_Trim","ARMS_East_Roof_Slab","ARMS_West_Roof_Slab","ARMS_R5_Coarse_LiDAR_roof_high"]
out=[]
for name in names:
    o=bpy.data.objects[name]
    mats=[m.name if m else None for m in o.data.materials]
    cnt={}
    for p in o.data.polygons: cnt[str(p.material_index)]=cnt.get(str(p.material_index),0)+1
    vs=[o.matrix_world @ v.co for v in o.data.vertices]
    item={"name":name,"materials":mats,"polygon_material_counts":cnt,"verts":len(vs),"polygons":len(o.data.polygons),"vertices":[[round(v.x,3),round(v.y,3),round(v.z,3)] for v in vs[:40]]}
    out.append(item)
print(json.dumps(out,indent=2))

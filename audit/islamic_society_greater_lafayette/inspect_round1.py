import bpy, json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
asset=root/'modular/buildings/massing_islamic_societyof_greater_lafayette_0130012.blend'
bpy.ops.wm.open_mainfile(filepath=str(asset))
mesh=bpy.data.objects['Islamic Society of Greater Lafayette'].data
counts={}
for p in mesh.polygons:
    m=mesh.materials[p.material_index] if p.material_index<len(mesh.materials) else None
    name=m.name if m else 'NONE'
    coords=[mesh.vertices[i].co for i in p.vertices]
    z=sum(v.z for v in coords)/len(coords)
    counts.setdefault(name,[]).append(z)
out={name:{'count':len(zs),'min_z':min(zs),'max_z':max(zs),'mean_z':sum(zs)/len(zs)} for name,zs in counts.items()}
(root/'audit/islamic_society_greater_lafayette/material_face_z_inventory.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))

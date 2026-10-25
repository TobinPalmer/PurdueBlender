import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
path=ROOT/'modular/buildings/physics_building_phys_3bf42f3.blend'
bpy.ops.wm.open_mainfile(filepath=str(path))
asset=bpy.data.collections['Asset_physics_building']
for name in ('PHYS | long clay ridge cap','PHYS | secondary hip ridge','PHYS | secondary hip ridge.001'):
    ob=bpy.data.objects.get(name)
    if ob: bpy.data.objects.remove(ob,do_unlink=True)
shell=bpy.data.objects['PHYS | GIS footprint brick envelope']
base=[v.co.copy() for v in shell.data.vertices if abs(v.co.z)<1e-5]
a,b=base[0],base[2]
axis=(b-a).normalized(); axis.z=0; axis.normalize()
roof=bpy.data.objects['PHYS | estimated sloped red tile roof']
# Ridge endpoints exactly follow the same source-derived projection axis as the roof surfaces.
proj=[p.x*axis.x+p.y*axis.y for p in base]
s0,s1=min(proj),max(proj)
length=s1-s0
mid=(s0+s1)*.5
center=axis*mid; center.z=15.99
mat=bpy.data.materials.get('PHYSICS_BUILDING | evidence palette roof')
bpy.ops.mesh.primitive_cube_add(size=1, location=center)
cap=bpy.context.object; cap.name='PHYS | GIS-aligned main clay ridge cap'
cap.dimensions=(length,.30,.20)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
cap.rotation_euler.z=math.atan2(axis.y,axis.x)
for c in list(cap.users_collection): c.objects.unlink(cap)
asset.objects.link(cap)
cap.data.materials.append(mat)
cap['source_note']='Single ridge cap aligned to the longest GIS-derived roof axis; original offset bars removed.'
roof['roof_profile_note']='Pitched hipped roof relief from the exact GIS perimeter; one ridge cap follows the GIS long axis, former displaced caps removed.'
asset['roof_cleanup_revision']='Removed three displaced ridge bars; added single ridge cap aligned to GIS footprint axis without changing footprint or wall geometry.'
bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
print(json.dumps({'ridge_length_m':length,'ridge_axis_xy':[axis.x,axis.y],'roof_dimensions':list(roof.dimensions),'objects':len(asset.all_objects)}))

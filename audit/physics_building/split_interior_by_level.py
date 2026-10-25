import bpy
from pathlib import Path
p=Path.cwd()/'modular/buildings/physics_building_phys_3bf42f3.blend'; bpy.ops.wm.open_mainfile(filepath=str(p)); asset=bpy.data.collections['Asset_physics_building']
old=bpy.data.objects['PHYS R2 | floor-plan corridor and room partitions']; mat=old.data.materials[0]; coords=[v.co.copy() for v in old.data.vertices]
levels=[('ground',1.7),('first',5.56),('second',9.86)]
objs={}
for label,zcenter in levels:
    verts=[]; faces=[]
    for start in range(0,len(coords),8):
        group=coords[start:start+8]
        if len(group)<8: continue
        center_z=sum(v.z for v in group)/8
        if abs(center_z-zcenter)>.30: continue
        offset=len(verts); verts.extend([tuple(v) for v in group]); faces.extend([(offset+0,offset+1,offset+3,offset+2),(offset+4,offset+6,offset+7,offset+5),(offset+0,offset+4,offset+5,offset+1),(offset+2,offset+3,offset+7,offset+6),(offset+0,offset+2,offset+6,offset+4),(offset+1,offset+5,offset+7,offset+3)])
    me=bpy.data.meshes.new(f'R2 | {label} floor-plan circulation walls'); me.from_pydata(verts,[],faces); me.materials.append(mat); me.update()
    ob=bpy.data.objects.new(f'PHYS R2 | {label} floor-plan partitions',me); asset.objects.link(ob); ob['source_note']='Purdue Physics evacuation plans identify circulation, labs, commons, and vertical cores on this floor; exact dimensions and positions are illustrative.'; objs[label]=len(verts)//8
bpy.data.objects.remove(old,do_unlink=True)
asset['r2_interior_partitions']='Partition walls are organized into ground, first, and second floor objects for inspectable level-by-level cutaway; layout dimensions remain schematic.'
bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True)
print('Split partitions by floor level:',objs,'objects',len(asset.all_objects))

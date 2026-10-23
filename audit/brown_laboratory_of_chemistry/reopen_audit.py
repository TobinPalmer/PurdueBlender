import bpy, json, os
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\brown_laboratory_of_chemistry.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
scene=bpy.context.scene
col=bpy.data.collections.get('Asset_brown_laboratory_of_chemistry')
root=bpy.data.objects.get('AssetRoot_brown_laboratory_of_chemistry')
assert scene.name=='Building_brown_laboratory_of_chemistry'
assert col is not None and root is not None
assert tuple(round(v,6) for v in root.location)==(0,0,0)
assert tuple(round(v,6) for v in root.scale)==(1,1,1)
objs=list(col.objects); meshes=[o for o in objs if o.type=='MESH']
missing=[]; unrooted=[]
for o in objs:
    if o is not root and o.parent is not root: unrooted.append(o.name)
    if o.type=='MESH' and (not o.data.materials or any(m is None for m in o.data.materials)): missing.append(o.name)
assert not missing, missing
assert not unrooted, unrooted
assert not any(o.library for o in bpy.data.objects)
assert not any(m.library for m in bpy.data.materials)
external=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]
polygon=json.loads(col.get('source_footprint_local_xy_json','[]'))
assert len(polygon)>=4, 'missing local source footprint polygon'
def inside_or_on(x,y):
    inside=False
    for (ax,ay),(bx,by) in zip(polygon,polygon[1:]+polygon[:1]):
        dx,dy=bx-ax,by-ay; den=dx*dx+dy*dy
        if den:
            t=max(0.0,min(1.0,((x-ax)*dx+(y-ay)*dy)/den))
            if ((x-(ax+t*dx))**2+(y-(ay+t*dy))**2)**.5<=1e-5: return True
        if ((ay>y)!=(by>y)) and x < (bx-ax)*(y-ay)/(by-ay)+ax: inside=not inside
    return inside
exterior_mesh_names={'Exterior_Brickwork_EW','Exterior_Brickwork_NS','Exterior_Concrete_Piers_and_Coping','Exterior_Glazing','Exterior_Window_Frames'}
intentional_exemptions={}
tested_interior_meshes=[]; outside_by_object={}
for ob in meshes:
    if ob.name in exterior_mesh_names: continue
    if ob.get('containment_exemption'):
        intentional_exemptions[ob.name]=ob['containment_exemption']
        continue
    tested_interior_meshes.append(ob)
    out=[v.co for v in ob.data.vertices if not inside_or_on(v.co.x,v.co.y)]
    if out: outside_by_object[ob.name]=len(out)
assert not outside_by_object, f'interior meshes outside the source polygon: {outside_by_object}'
wall_obj=bpy.data.objects.get('Interior_Partitions')
assert wall_obj is not None
story_bands={'basement':(-3.30,-.40),'floor_01':(0.00,3.10),'floor_02':(3.20,6.30),'floor_03':(6.40,9.50),'floor_04':(9.60,12.70),'floor_05':(12.80,15.90)}
containment_by_story={}
for story,(zlo,zhi) in story_bands.items():
    verts=[v.co for v in wall_obj.data.vertices if zlo-1e-6<=v.co.z<=zhi+1e-6]
    outside=sum(not inside_or_on(v.x,v.y) for v in verts)
    containment_by_story[story]={'vertices_checked':len(verts),'outside':outside}
    assert outside==0, f'{story}: {outside} partition vertices beyond source polygon'
audit_dir=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\brown_laboratory_of_chemistry')
renders=['brown_exterior.png','brown_interior_lab.png','brown_cutaway.png','brown_basement_cutaway.png']+[f'brown_floor_{i:02d}_cutaway.png' for i in range(1,6)]
missing_renders=[name for name in renders if not (audit_dir/name).is_file()]
assert not missing_renders, missing_renders
# Local extents of asset geometry
bb=[]
for o in objs:
    if o.type=='MESH':
        for c in o.bound_box: bb.append(o.matrix_world @ __import__('mathutils').Vector(c))
mins=[min(v[k] for v in bb) for k in range(3)]; maxs=[max(v[k] for v in bb) for k in range(3)]
report={'scene':scene.name,'collection':col.name,'object_count':len(objs),'mesh_count':len(meshes),'material_count':len([m for m in bpy.data.materials if m.users>0]),'missing_mesh_materials':missing,'non_rooted_objects':unrooted,'linked_libraries':sum(bool(o.library) for o in bpy.data.objects),'unpacked_external_images':external,'root_location':list(root.location),'root_scale':list(root.scale),'local_bounds_min_m':mins,'local_bounds_max_m':maxs,'placement_origin_xy_m':list(col.get('placement_origin_xy_m')),'source_massing_id':col.get('source_massing_id'),'source_polygon_vertex_count':len(polygon),'interior_mesh_objects_checked':len(tested_interior_meshes),'interior_mesh_vertices_checked':sum(len(o.data.vertices) for o in tested_interior_meshes),'interior_meshes_outside':outside_by_object,'intentional_exterior_exemptions':intentional_exemptions,'interior_wall_vertices_checked':len(wall_obj.data.vertices),'partition_containment_by_story':containment_by_story,'render_count':len(renders),'missing_renders':missing_renders}
print(json.dumps(report,indent=2))

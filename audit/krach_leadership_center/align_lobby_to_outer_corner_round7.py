import bpy, bmesh, json
from mathutils import Vector

src=bpy.data.filepath
assert src.lower().endswith('krach_leadership_center.blend'), src
start=Vector((-35.13066864,-13.89586353))
end=Vector((-16.32078934,-14.05729580))
edge=end-start
bay_width=8.66856878
bay_mid=start+edge*(bay_width/edge.length*.5)
new_x=bay_mid.x
old_x=-11.9923117
stair=bpy.data.objects['KRCH | four-story visible switchback stair and etched glass guard']
assert not stair.get('facade_alignment_round7')
for v in stair.data.vertices:
    v.co.x += new_x-old_x
stair['facade_alignment_round7']='Moved the schematic multilevel lobby stair behind the southwest outside-corner glazed bay. Centered on bay midpoint; exact interior plan remains schematic.'

rails=bpy.data.objects.get('KRCH | continuous stair handrails over glass gallery guards')
if rails and rails.type=='CURVE':
    for spline in rails.data.splines:
        points=spline.points if spline.type=='POLY' else spline.bezier_points
        for point in points: point.co.x += new_x-old_x
    rails['facade_alignment_round7']='Moved with the schematic stair to remain visible through the southwest corner lobby glazing.'

shell=bpy.data.objects['KRCH structural shell | GIS outline']
base=next(p for p in shell.data.polygons if all(abs(shell.data.vertices[i].co.z+1.0)<1e-4 for i in p.vertices))
ring=[shell.data.vertices[i].co.copy() for i in base.vertices]
for obj in list(bpy.data.objects):
    if obj.name.startswith('KRCH | schematic level slab'): bpy.data.objects.remove(obj,do_unlink=True)
interior=bpy.data.collections['Schematic_Interior']
floor_mat=bpy.data.materials.get('KRCH | pale terrazzo gallery floor') or bpy.data.materials.get('KRCH | pale terrazzo upper-floor')
levels=[-.92,2.98,6.88,10.78,14.68]
for idx,z in enumerate(levels):
    n=len(ring)
    vv=[(v.x*.985,v.y*.985,z-.18) for v in ring]+[(v.x*.985,v.y*.985,z) for v in ring]
    ff=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n): ff.append((i,(i+1)%n,(i+1)%n+n,i+n))
    mesh=bpy.data.meshes.new('KRCH level slab with southwest corner lobby void'); mesh.from_pydata(vv,[],ff)
    if floor_mat: mesh.materials.append(floor_mat)
    mesh.update(); bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(mesh); bm.free()
    slab=bpy.data.objects.new('KRCH | schematic level slab %02d'%(idx+1),mesh); interior.objects.link(slab)
    slab['level_top_m']=z; slab['atrium_void']='Schematic void centered under the southwest glazed corner bay; dimensions and exact plan remain unverified.'
    bpy.ops.mesh.primitive_cube_add(size=1,location=(new_x,-9.3,z-.09))
    cutter=bpy.context.object; cutter.name='TEMP | round7 lobby void cutter'; cutter.dimensions=(8.8,7.2,.4)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.ops.object.select_all(action='DESELECT'); slab.select_set(True); bpy.context.view_layer.objects.active=slab
    modifier=slab.modifiers.new('Southwest corner lobby opening','BOOLEAN'); modifier.operation='DIFFERENCE'; modifier.solver='EXACT'; modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name); bpy.data.objects.remove(cutter,do_unlink=True)

bpy.ops.wm.save_as_mainfile(filepath=src)
print(json.dumps({'saved':src,'outer_corner_bay_center_m':[new_x,bay_mid.y],'stair_center_x_m':new_x,'floor_void_center_xy_m':[new_x,-9.3],'floor_void_size_m':[8.8,7.2],'story_levels_m':levels},indent=2))

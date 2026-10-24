import bpy, bmesh, json
from mathutils import Vector

src=bpy.data.filepath
assert src.lower().endswith('krach_leadership_center.blend')
shell=bpy.data.objects['KRCH structural shell | GIS outline']
base=next(p for p in shell.data.polygons if all(abs(shell.data.vertices[i].co.z+1.0)<1e-4 for i in p.vertices))
ring=[shell.data.vertices[i].co.copy() for i in base.vertices]
dx=11.75
old_center=(-19.45,-9.3); new_center=(-7.70,-9.3)

# The revised glass bay is now on the actual diagonal GIS connector. Bring the
# already documented schematic stair and floor voids behind that bay, preserving
# their full geometry, floor elevations, stair-flight relationships, and widths.
stair=bpy.data.objects['KRCH | four-story visible switchback stair and etched glass guard']
if not stair.get('facade_alignment_round4'):
    for v in stair.data.vertices: v.co.x+=dx
stair['facade_alignment_round4']='Translated 11.75 m east within the same local coordinate frame so the existing schematic stair lies behind the GIS-aligned south glass bay; floor heights/flight geometry unchanged.'
rails=bpy.data.objects.get('KRCH | continuous stair handrails over glass gallery guards')
if rails and rails.type=='CURVE' and not rails.get('facade_alignment_round4'):
    for spl in rails.data.splines:
        for p in (spl.points if spl.type=='POLY' else spl.bezier_points): p.co.x+=dx
    rails['facade_alignment_round4']='Translated 11.75 m east with the schematic lobby stair, so handrail splines remain aligned.'

# Rebuild only the five schematic plates, preserving the same footprint and levels,
# with the same-size lobby void relocated to the stair's new center.
for o in list(bpy.data.objects):
    if o.name.startswith('KRCH | schematic level slab'):
        bpy.data.objects.remove(o,do_unlink=True)
interior=bpy.data.collections['Schematic_Interior']
floor_mat=bpy.data.materials.get('KRCH | pale terrazzo gallery floor') or bpy.data.materials.get('KRCH | pale terrazzo upper-floor')
if floor_mat is None:
    floor_mat=bpy.data.materials.new('KRCH | pale terrazzo gallery floor'); floor_mat.diffuse_color=(.53,.50,.44,1)
levels=[-0.92,2.98,6.88,10.78,14.68]
for idx,z in enumerate(levels):
    n=len(ring); vv=[(v.x*.985,v.y*.985,z-.18) for v in ring]+[(v.x*.985,v.y*.985,z) for v in ring]
    ff=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n): ff.append((i,(i+1)%n,(i+1)%n+n,i+n))
    me=bpy.data.meshes.new('KRCH level slab with corner bay lobby void | GIS ring'); me.from_pydata(vv,[],ff); me.materials.append(floor_mat); me.update()
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new('KRCH | schematic level slab %02d'%(idx+1),me); interior.objects.link(ob)
    ob['level_top_m']=z; ob['atrium_void']='Schematic open rectangle aligned to the multilevel lobby stair behind the photo-matched diagonal corner bay; exact floor plan and opening dimensions are not surveyed.'
    bpy.ops.mesh.primitive_cube_add(size=1,location=(new_center[0],new_center[1],z-.09)); cut=bpy.context.object
    cut.name='TEMP | aligned lobby void cutter'; cut.dimensions=(11.7,7.2,.4); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('Corner glass bay aligned lobby opening','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cut
    bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cut,do_unlink=True)

bpy.ops.wm.save_as_mainfile(filepath=src)
print(json.dumps({'saved':src,'stair_x_shift_m':dx,'stair_new_bounds_x_m':[min(v.co.x for v in stair.data.vertices),max(v.co.x for v in stair.data.vertices)],'void_center_xy_m':new_center,'void_size_xy_m':[11.7,7.2],'story_levels_m':levels},indent=2))

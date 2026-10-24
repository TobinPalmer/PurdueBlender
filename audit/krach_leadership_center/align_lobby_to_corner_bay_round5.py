import bpy, bmesh, json
from mathutils import Vector

src=bpy.data.filepath
assert src.lower().endswith('krach_leadership_center.blend')
shell=bpy.data.objects['KRCH structural shell | GIS outline']
base=next(p for p in shell.data.polygons if all(abs(shell.data.vertices[i].co.z+1.0)<1e-4 for i in p.vertices))
ring=[shell.data.vertices[i].co.copy() for i in base.vertices]

# Match the tighter source-matched bay on the west half of the GIS diagonal.
edge_a=Vector((-16.3207893372,-14.0572958)); edge_b=Vector((0.9931200743,-13.1601419449))
bay_center=edge_a+(edge_b-edge_a)*.25
old_center_x=-7.70; old_width_center=-8.245
new_center_x=bay_center.x
dx=new_center_x-old_width_center; x_scale=.92

stair=bpy.data.objects['KRCH | four-story visible switchback stair and etched glass guard']
if not stair.get('facade_alignment_round5'):
    for v in stair.data.vertices: v.co.x=(v.co.x-old_width_center)*x_scale+new_center_x
    stair['facade_alignment_round5']='Shifted to the narrow source-matched corner bay and scaled 0.92 in X so the schematic stair fits behind its glazing; exact plan remains estimated.'

rails=bpy.data.objects.get('KRCH | continuous stair handrails over glass gallery guards')
if rails and rails.type=='CURVE' and not rails.get('facade_alignment_round5'):
    for spl in rails.data.splines:
        points=spl.points if spl.type=='POLY' else spl.bezier_points
        for p in points: p.co.x=(p.co.x-old_width_center)*x_scale+new_center_x
    rails['facade_alignment_round5']='Aligned and scaled with the schematic stair for the narrower corner bay.'

# Rebuild the five schematic slabs with the same footprint, inset, and story levels;
# the opening stays oversized enough to represent unresolved circulation clearance.
for o in list(bpy.data.objects):
    if o.name.startswith('KRCH | schematic level slab'): bpy.data.objects.remove(o,do_unlink=True)
interior=bpy.data.collections['Schematic_Interior']
floor_mat=bpy.data.materials.get('KRCH | pale terrazzo gallery floor') or bpy.data.materials.get('KRCH | pale terrazzo upper-floor')
if floor_mat is None:
    floor_mat=bpy.data.materials.new('KRCH | pale terrazzo gallery floor'); floor_mat.diffuse_color=(.53,.50,.44,1)
levels=[-.92,2.98,6.88,10.78,14.68]
for idx,z in enumerate(levels):
    n=len(ring); vv=[(v.x*.985,v.y*.985,z-.18) for v in ring]+[(v.x*.985,v.y*.985,z) for v in ring]
    ff=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n): ff.append((i,(i+1)%n,(i+1)%n+n,i+n))
    me=bpy.data.meshes.new('KRCH level slab with corner lobby void | GIS ring'); me.from_pydata(vv,[],ff)
    me.materials.append(floor_mat); me.update()
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new('KRCH | schematic level slab %02d'%(idx+1),me); interior.objects.link(ob)
    ob['level_top_m']=z; ob['atrium_void']='Schematic opening around the corner-bay lobby stair; dimensions and exact floor plan are unverified.'
    bpy.ops.mesh.primitive_cube_add(size=1,location=(new_center_x,-9.3,z-.09)); cut=bpy.context.object
    cut.name='TEMP | round5 lobby void cutter'; cut.dimensions=(11.7,7.2,.4); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('Corner lobby opening','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cut
    bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cut,do_unlink=True)

bpy.ops.wm.save_as_mainfile(filepath=src)
print(json.dumps({'saved':src,'bay_center_x_m':new_center_x,'stair_center_x_m':new_center_x,'stair_x_scale':x_scale,'opening_center_xy_m':[new_center_x,-9.3],'story_levels_m':levels},indent=2))

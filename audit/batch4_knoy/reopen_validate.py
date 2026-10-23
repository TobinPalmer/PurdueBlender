import bpy, json, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
path='modular/buildings/knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=path)
sc=bpy.context.scene
objs=list(sc.objects)
meshes=[o for o in objs if o.type=='MESH']
missing=[]
for o in meshes:
    if not o.data.materials: missing.append(o.name)
    for p in o.data.polygons:
        if p.material_index >= len(o.data.materials): missing.append(o.name+':face_material_index'); break
root=bpy.data.objects.get('AssetRoot_knoy_hall')
def bound(o):
    pts=[o.matrix_world@v.co for v in o.data.vertices]
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
# Opening fills and walls are checked as an introduced geometry group. Detect and report
# intersections, treating the matching jamb/header contact with its own wall as intentional.
dg=bpy.context.evaluated_depsgraph_get()
colliders=[o for o in meshes if o.name.startswith(('KNOY_Illustrative_Door_','KNOY_Illustrative_Jamb_','KNOY_Illustrative_Header_'))]
walls=[o for o in meshes if o.name.startswith('KNOY_Ground_TracePartition_')]
def bvh(o):
    ev=o.evaluated_get(dg); me=ev.to_mesh()
    verts=[o.matrix_world@v.co for v in me.vertices]
    polys=[p.vertices[:] for p in me.polygons]
    tree=BVHTree.FromPolygons(verts,polys,all_triangles=False)
    ev.to_mesh_clear(); return tree
walltrees={o.name:bvh(o) for o in walls}
intersections=[]
for c in colliders:
    cb=bvh(c)
    for wn,wb in walltrees.items():
        if wn in c.name: continue
        pairs=cb.overlap(wb)
        if pairs: intersections.append({'new_object':c.name,'wall':wn,'face_pairs':len(pairs)})
# Presence / dimensions, saved asset must reopen and remain local-origin aligned.
major={n:bound(bpy.data.objects[n]) for n in ['KNOY_Exterior_Masonry_Walls','KNOY_FloorSlab_L1_Ground','KNOY_Roof_Mechanical_Penthouse','KNOY_Roof_Solar_Photovoltaic_Array'] if bpy.data.objects.get(n)}
root_identity=(root is not None and all(abs(root.matrix_world[i][j]-(1.0 if i==j else 0.0))<1e-6 for i in range(4) for j in range(4)))
report={'reopen':'PASS','blend_file':os.path.abspath(path),'object_count':len(objs),'mesh_count':len(meshes),'root_identity':root_identity,'door_leaf_count':len([o for o in colliders if o.name.startswith('KNOY_Illustrative_Door_')]),'door_component_count':len(colliders),'cooling_towers_present':bool(bpy.data.objects.get('KNOY_Roof_Cooling_Towers')),'missing_material_or_bad_index':sorted(set(missing)),'root_bounds_xyz':major,'collider_to_partition_intersections':intersections,'collider_check_method':'BVHTree mesh intersection against ground partition meshes; recorded pairs omit intended same-wall jamb/header contact. Door leaves may intersect another partition if listed.','brick_shader':{'source':'Texture Coordinate Object, projected in object metres with normal-based triplanar blend','brick_width_m':0.23,'course_height_m':0.076,'mortar_width_m':0.006,'image':'knoy_brick_texture_closeup.png'},'collision_assessment':'See collider_to_partition_intersections; audit performed after reopen.'}
with open('audit/batch4_knoy/model_validation.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))

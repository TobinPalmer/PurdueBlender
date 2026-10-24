import bpy, os, json, bmesh
from mathutils import Vector

ROOT=os.path.abspath('.')
ASSET=os.path.join(ROOT,'modular','buildings','materials_science_and_electrical_engineering_msee.blend')
ID='materials_science_and_electrical_engineering_msee'
bpy.ops.wm.open_mainfile(filepath=ASSET)
col=bpy.data.collections.get('Asset_'+ID)
shell=bpy.data.objects.get(ID+'_official_GIS_shell')
screen=bpy.data.objects.get('MSEE_Max_W_Brown_two_story_glazed_atrium')
assert col and shell and screen
dg=bpy.context.evaluated_depsgraph_get(); ev=shell.evaluated_get(dg); mesh=ev.to_mesh()
pts=[ev.matrix_world@v.co for v in mesh.vertices]
bounds=[[round(min(p[i] for p in pts),4),round(max(p[i] for p in pts),4)] for i in range(3)]
expected_bounds=[[-37.0934,37.0881],[-40.0671,40.0597],[.3,15.]]
bm=bmesh.new(); bm.from_mesh(mesh)
nonmanifold=sum(not e.is_manifold for e in bm.edges); volume=round(bm.calc_volume(signed=True),3)
verts=len(mesh.vertices); faces=len(mesh.polygons); bm.free(); ev.to_mesh_clear()
screen_pts=[screen.matrix_world@v.co for v in screen.data.vertices]
screen_z=[min(p.z for p in screen_pts),max(p.z for p in screen_pts)]
entry=[o for o in col.all_objects if o.name.startswith(('R6_MSEE_entry_','R6_MSEE_fanlight_spoke_'))]
old_fragments=[o.name for o in col.all_objects if o.name=='R5_MSEE_arch_head' or o.name.startswith('R5_MSEE_fanlight_spoke_')]
top=[o for o in col.all_objects if o.name.startswith('MSEE_window_') and o.name.split('_')[3]=='3']
top_dims=[]
for o in top:
    p=[o.matrix_world@Vector(c) for c in o.bound_box]
    top_dims.append(round(max(x.z for x in p)-min(x.z for x in p),3))
external=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file:
        fp=bpy.path.abspath(im.filepath); external.append({'path':im.filepath,'exists':os.path.exists(fp)})
report={'asset':ID,'path':'modular/buildings/'+ID+'.blend','reopened':True,
        'collection':col.name,'object_count':len(col.all_objects),'mesh_objects':sum(o.type=='MESH' for o in col.all_objects),
        'shell_bounds_local_m':bounds,'bounds_match_R5_within_0_001m':all(abs(a-b)<.001 for ar,br in zip(bounds,expected_bounds) for a,b in zip(ar,br)),
        'shell_mesh_vertices':verts,'shell_mesh_faces':faces,'shell_nonmanifold_edges':nonmanifold,
        'shell_signed_volume_m3':volume,'screen_z_bounds_m':[round(v,3) for v in screen_z],
        'entry_object_count':len(entry),'entry_base_z_m':round(min((o.matrix_world@Vector(c)).z for o in entry for c in o.bound_box),3),
        'entry_arch_top_z_m':round(max((o.matrix_world@Vector(c)).z for o in entry if o.name=='R6_MSEE_entry_arched_head' for c in o.bound_box),3),
        'top_course_window_count':len(top),'top_course_window_height_range_m':[min(top_dims),max(top_dims)],
        'obsolete_R5_arch_objects_remaining':old_fragments,'unpacked_external_images':external,
        'preview':'audit/rework_batch_a/'+ID+'_revision6_preview.png',
        'entry_detail_preview':'audit/rework_batch_a/'+ID+'_revision6_entry_detail.png',
        'pass':len(entry)==14 and not old_fragments and nonmanifold==0 and volume>0 and
               all(abs(a-b)<.001 for a,b in zip(bounds[0],[-37.0934,37.0881])) and
               all(abs(a-b)<.001 for a,b in zip(bounds[1],[-40.0671,40.0597])) and
               all(abs(a-b)<.001 for a,b in zip(bounds[2],[.3,15.])) and
               .4<=min((o.matrix_world@Vector(c)).z for o in entry for c in o.bound_box)<=.8 and
               all(x['exists'] for x in external)}
out=os.path.join(ROOT,'audit','rework_batch_a',ID+'_R6_validation.json')
with open(out,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))

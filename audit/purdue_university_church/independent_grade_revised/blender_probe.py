import bpy, json, os, math, hashlib
from mathutils import Vector
asset=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_university_church_84b2a1b.blend'
out=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\purdue_university_church\independent_grade_revised\fresh_open_probe.json'
gis=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\purdue_university_church\sources\purdue_gis_fid797.geojson'
scene_name='Building_massing_university_church_84b2a1b'; coll_name='Asset_massing_university_church_84b2a1b'
scene=bpy.context.scene
coll=bpy.data.collections.get(coll_name)
objs=list(coll.all_objects) if coll else []
meshobjs=[o for o in objs if o.type=='MESH']

def world_bbox(obj):
    pts=[obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]

def world_curve_points(obj):
    pts=[]
    if obj.type=='CURVE':
        for spl in obj.data.splines:
            for p in spl.points: pts.append(obj.matrix_world @ Vector(p.co[:3]))
    return pts

shell=bpy.data.objects.get('University Church | GIS brick envelope')
basepts=[]
if shell:
    for v in shell.data.vertices:
        p=shell.matrix_world @ v.co
        if abs(p.z)<1e-4: basepts.append([float(p.x),float(p.y)])
# Deduplicate exact-ish lower shell vertices.
basepts=sorted({(round(x,7),round(y,7)) for x,y in basepts})
with open(gis,encoding='utf-8') as f: src=json.load(f)
record_path=os.path.join(os.path.dirname(os.path.dirname(gis)),'build_evidence.json')
with open(record_path,encoding='utf-8') as f: evidence_record=json.load(f)
feature=src['features'][0]
props=feature['properties']
ring=feature['geometry']['coordinates'][0][:-1]
origin=(40.4274,-86.9137); m_lon=111412.84*math.cos(math.radians(origin[0])); m_lat=111040.0
srcpts=[((lon-origin[1])*m_lon,(lat-origin[0])*m_lat) for lon,lat in ring]
def directed(a,b): return max(min(math.dist(p,q) for q in b) for p in a) if a and b else None
haus=max(directed(srcpts,basepts),directed(basepts,srcpts))
arch=[o for o in objs if 'arched side window head' in o.name]
arch_stats=[]
for o in arch:
    pts=world_curve_points(o)
    if pts:
        xs=[p.x for p in pts]; ys=[p.y for p in pts]
        arch_stats.append({'name':o.name,'x_bounds':[min(xs),max(xs)],'y_bounds':[min(ys),max(ys)],'z_range':[min(p.z for p in pts),max(p.z for p in pts)]})
maxx=max(p[0] for p in srcpts); minx=min(p[0] for p in srcpts); maxy=max(p[1] for p in srcpts); miny=min(p[1] for p in srcpts)
east_arch=[d for d in arch_stats if d['x_bounds'][0] >= maxx-0.65 and d['x_bounds'][1]<=maxx+0.65]
# Count window reveals/lintels on the east wall using independently transformed world coordinates.
east_reveals=[]; east_lintels=[]; portico_columns=[]
for o in objs:
    if o.name.startswith('UC | window reveal') or o.name.startswith('UC | stone lintel'):
        bb=world_bbox(o); x=(bb[0][0]+bb[0][1])*0.5
        if x>=maxx-0.65:
            (east_reveals if o.name.startswith('UC | window reveal') else east_lintels).append(o.name)
    if o.name.startswith('UC | portico column shaft'):
        portico_columns.append(o)
images=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath:
        exists=os.path.exists(bpy.path.abspath(im.filepath))
        packed=bool(im.packed_file)
        if not exists and not packed: images.append({'path':im.filepath,'exists':exists,'packed':packed})
missing_lib=[]
for lib in bpy.data.libraries:
    if lib.filepath and not os.path.exists(bpy.path.abspath(lib.filepath)): missing_lib.append(lib.filepath)
materialless=[o.name for o in meshobjs if len(o.data.materials)==0]
invalid_face_materials=[{'object':o.name,'face_indices':[poly.index for poly in o.data.polygons if poly.material_index>=len(o.data.materials)]} for o in meshobjs if any(poly.material_index>=len(o.data.materials) for poly in o.data.polygons)]
used_mats={m.name:m for o in meshobjs for m in o.data.materials if m is not None}
material_stats={'used_material_count':len(used_mats),'node_material_count':sum(1 for m in used_mats.values() if m.use_nodes and m.node_tree),'principled_material_count':sum(1 for m in used_mats.values() if m.use_nodes and m.node_tree and any(n.type=='BSDF_PRINCIPLED' for n in m.node_tree.nodes)),'material_names':sorted(used_mats)}
reveal_count=sum(o.name.startswith('UC | window reveal') for o in objs)
scene_ok=scene_name in bpy.data.scenes
report={
 'asset_path':asset,'asset_sha256':hashlib.sha256(open(asset,'rb').read()).hexdigest(),'fresh_open':True,
 'blender_version':bpy.app.version_string,'expected_scene_present':scene_ok,'active_scene':scene.name,
 'expected_collection_present':coll is not None,'collection_object_count':len(objs),'mesh_count':len(meshobjs),
 'mesh_shell_name_present':shell is not None,'shell_bottom_vertex_count':len(basepts),'shell_hausdorff_error_m':haus,
 'gis_feature_properties':{k:props.get(k) for k in ['FID','BLDG_ABBR','BUILDING_N','Level_','NUM_LEVELS','CountOfFLO','Extrution']},
 'gis_shell_bounds_m':[[min(x for x,y in srcpts),max(x for x,y in srcpts)],[min(y for x,y in srcpts),max(y for x,y in srcpts)]],
 'saved_shell_bounds_m':world_bbox(shell)[:2] if shell else None,
 'window_reveals_total':reveal_count,'arched_window_head_objects':len(arch),'east_portico_arch_heads':len(east_arch),
 'perpendicular_arch_heads':len(arch)-len(east_arch),'east_portico_window_reveals':len(east_reveals),'east_portico_square_lintels':len(east_lintels),
 'east_arch_examples':east_arch[:5], 'perpendicular_arch_examples':arch_stats[:3],
 'oculus_present':any('pediment circular oculus glazing' in o.name for o in objs),
 'oculus_ring_present':any('pediment oculus limestone ring' in o.name for o in objs),
 'portico_shaft_count':len(portico_columns),'tower_present':any('bell tower shaft' in o.name for o in objs),
 'spire_present':any('spire' in o.name.lower() for o in objs),
 'main_door_count':sum(o.name.startswith('UC | timber double door ') for o in objs),
 'door_component_names':[o.name for o in objs if o.name.startswith('UC | timber double door ')],
 'materialless_meshes':materialless,'invalid_face_materials':invalid_face_materials,'materials':material_stats,'unresolved_external_images':images,'file_images':[{'path':im.filepath,'exists':os.path.exists(bpy.path.abspath(im.filepath)),'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE' and im.filepath],'missing_library_paths':missing_lib,
 'source_snapshots':[{'path':s.get('snapshot_path'),'exists':os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(gis)))),s.get('snapshot_path','')))} for s in evidence_record.get('sources',[])],
 'source_previews':[{'path':f,'exists':os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(gis)))),f))} for f in evidence_record.get('validation',{}).get('previews',[])],
 'shell_bottom_xy':basepts
}
with open(out,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='shell_bottom_xy'},indent=2))

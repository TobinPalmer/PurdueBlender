import bpy, bmesh, hashlib, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / 'modular/buildings/massing_west_lafayette_intermediate_school_d72f0fa.blend'
OUT = ROOT / 'audit/west_lafayette_intermediate_school/independent_grade_r2/fresh_open_findings.json'
SCENE = 'Building_massing_west_lafayette_intermediate_school_d72f0fa'
COLL = 'Asset_massing_west_lafayette_intermediate_school_d72f0fa'
scene = bpy.data.scenes.get(SCENE)
coll = bpy.data.collections.get(COLL)
assert scene and coll
objects = list(coll.all_objects)
meshes = [o for o in objects if o.type == 'MESH']
def bb(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)] if pts else None
verts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
bounds = [[min(p[i] for p in verts), max(p[i] for p in verts)] for i in range(3)]
shell = bpy.data.objects['GIS 772742586 | exact connected school footprint']
base = []
for v in shell.data.vertices:
    p = shell.matrix_world @ v.co
    if abs(p.z) < 1e-5: base.append((p.x, p.y))
base = list(dict.fromkeys((round(x, 7), round(y, 7)) for x, y in base))
osm = json.loads((ROOT/'audit/west_lafayette_intermediate_school/sources/osm_way_772742586_full.json').read_text())
way = next(e for e in osm['elements'] if e.get('type')=='way' and e.get('id')==772742586)
nodes = {e['id']:(e['lon'],e['lat']) for e in osm['elements'] if e.get('type')=='node'}
source=[]
for i in way['nodes']:
    lon,lat=nodes[i]
    source.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0))
if source[0]==source[-1]: source.pop()
err=[min(math.hypot(x-a,y-b) for a,b in base) for x,y in source]
def inside(pt, poly):
    x,y=pt; c=False
    for i,(ax,ay) in enumerate(poly):
        bx,by=poly[(i+1)%len(poly)]
        if ((ay>y)!=(by>y)) and x<(bx-ax)*(y-ay)/(by-ay)+ax: c=not c
    return c
ring=[nodes[i] for i in way['nodes']]
ring_xy=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring]
if ring_xy[0]==ring_xy[-1]: ring_xy.pop()
hub=((min(x for x,y in ring_xy)+max(x for x,y in ring_xy))*0.5,(min(y for x,y in ring_xy)+max(y for x,y in ring_xy))*0.5)
# Recreate the builder's schematic classroom centroid locations and test them
# against the OSM polygon. This reveals whether rooms remain inside its shell.
classroom_centers=[]
classroom_inside_ids=[]; classroom_outside_ids=[]
rays=[(-0.70,0.68),(0.78,0.62),(-0.80,-0.52)]
room_num=0
for rx,ry in rays:
    mag=math.hypot(rx,ry); rx/=mag; ry/=mag
    px,py=-ry,rx
    for k in range(6):
        along=14.0+k*6.1; center=(hub[0]+rx*along,hub[1]+ry*along)
        for side in (-1,1):
            room_num+=1
            p=(center[0]+px*side*5.25,center[1]+py*side*5.25)
            classroom_centers.append(p)
            (classroom_inside_ids if inside(p,ring_xy) else classroom_outside_ids).append(room_num)
classroom_inside_count=sum(inside(p,ring_xy) for p in classroom_centers)
mat_info=[]
for m in sorted({s.material for o in meshes for s in o.material_slots if s.material},key=lambda m:m.name):
    nodes=[n.type for n in m.node_tree.nodes] if m.use_nodes and m.node_tree else []
    img_nodes=[n for n in m.node_tree.nodes if n.type=='TEX_IMAGE'] if m.use_nodes and m.node_tree else []
    mat_info.append({'name':m.name,'nodes':nodes,'image_nodes':[n.image.name if n.image else None for n in img_nodes]})
groups={c.name:len(c.all_objects) for c in coll.children}
classroom=[o for o in objects if 'Classroom ' in o.name and ('corridor partition' in o.name or 'student table' in o.name)]
classroom_bounds=[bb(o) for o in classroom if o.type=='MESH']
vol=bmesh.new();vol.from_mesh(shell.data);vol.normal_update()
topology={'verts':len(vol.verts),'edges':len(vol.edges),'faces':len(vol.faces),'boundary':sum(e.is_boundary for e in vol.edges),'nonmanifold':sum(not e.is_manifold for e in vol.edges),'zero_area':sum(f.calc_area()<1e-10 for f in vol.faces),'volume':vol.calc_volume(signed=True) if all(e.is_manifold for e in vol.edges) else None}
vol.free()
result={'fresh_open':True,'blender_version':bpy.app.version_string,'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'asset_size_bytes':ASSET.stat().st_size,'scene':scene.name,'collection':coll.name,'objects':len(objects),'meshes':len(meshes),'mesh_vertices':sum(len(o.data.vertices) for o in meshes),'mesh_polygons':sum(len(o.data.polygons) for o in meshes),'bounds_world_m':bounds,'osm_way_id':way['id'],'osm_name':way.get('tags',{}).get('name'),'osm_unique_nodes':len(source),'shell_base_unique_vertices':len(base),'footprint_max_nearest_error_m':max(err),'footprint_rms_nearest_error_m':math.sqrt(sum(e*e for e in err)/len(err)),'shell_topology':topology,'subcollections':groups,'materials':mat_info,'external_file_images':[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE'],'classroom_object_count':len(classroom),'classroom_centers_within_osm_footprint':classroom_inside_count,'classroom_centers_total':len(classroom_centers),'classroom_inside_ids':classroom_inside_ids,'classroom_outside_ids':classroom_outside_ids,'classroom_component_bounds':classroom_bounds[:80]}
OUT.write_text(json.dumps(result,indent=2)+'\n')
print('INDEPENDENT_WLIS_R2 '+json.dumps(result))

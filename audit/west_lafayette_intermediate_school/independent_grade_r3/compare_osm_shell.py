import bpy,json,math,hashlib,os
from mathutils import Vector
base='C:/Users/Tobin/Documents/Blender/PurdueMap/'
source=json.load(open(base+'audit/west_lafayette_intermediate_school/sources/osm_way_772742586_full.json',encoding='utf-8'))
way=next(e for e in source['elements'] if e['type']=='way' and e['id']==772742586)
nodes={e['id']:e for e in source['elements'] if e['type']=='node'}
lat0=40.4274; lon0=-86.9137; lonm=111412.84*math.cos(math.radians(lat0)); latm=111040.0
ring=[]
for nid in way['nodes'][:-1]:
 n=nodes[nid]; ring.append(((n['lon']-lon0)*lonm,(n['lat']-lat0)*latm))
o=bpy.data.objects['GIS 772742586 | exact connected school footprint']
world=[o.matrix_world @ v.co for v in o.data.vertices]
basev=[]
for v in world:
 if abs(v.z)<1e-6 and not any((v.xy-w.xy).length<1e-7 for w in basev): basev.append(v)
errs=[min(math.hypot(v.x-x,v.y-y) for v in basev) for x,y in ring]
# shoelace areas, signs
area=lambda pts: sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))/2
classes=sorted({o.name.split(' | ')[0] for o in bpy.data.objects if o.name.startswith('Classroom ')})
# Use actual classroom mesh bounds center to estimate each classroom footprint location, no claim that floorplan is authoritative.
class_mesh=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Classroom ') and '| corridor partition' in o.name]
res={'asset_sha256':hashlib.sha256(open(bpy.data.filepath,'rb').read()).hexdigest(),'osm_node_count':len(ring),'shell_base_unique_vertex_count':len(basev),'osm_to_shell_max_nearest_vertex_error_m':max(errs),'osm_to_shell_rms_nearest_vertex_error_m':math.sqrt(sum(e*e for e in errs)/len(errs)),'osm_polygon_area_m2':area(ring),'shell_ordered_xy_area_m2':area([(v.x,v.y) for v in basev]),'classroom_number_prefix_count':len(classes),'classroom_corridor_partition_meshes':len(class_mesh),'source_way_tags':way['tags']}
print('GEOMETRY_CHECK_JSON='+json.dumps(res,separators=(',',':')))
open(os.environ['WLI_GEOMETRY_OUT'],'w',encoding='utf-8').write(json.dumps(res,indent=2))

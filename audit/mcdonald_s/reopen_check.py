import bpy, json, math, xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
blend=root/'modular/buildings/massing_mcdonald_s_ab77b70.blend'
xml=root/'audit/mcdonald_s/sources/osm_way_256640455_full.xml'
obj=bpy.data.objects.get("McDonald's")
assert obj is not None and obj.type=='MESH', 'assigned mesh missing'
assert len(obj.users_collection)==1 and obj.users_collection[0].name=='Asset_massing_mcdonald_s_ab77b70'
assert tuple(round(float(v),6) for v in obj.location)==(0.0,0.0,0.0)
assert tuple(round(float(v),6) for v in obj.rotation_euler)==(0.0,0.0,0.0)
assert tuple(round(float(v),6) for v in obj.scale)==(1.0,1.0,1.0)
assert len(obj.modifiers)==0
root_xml=ET.parse(xml).getroot(); way=root_xml.find('way'); nodes={n.get('id'):(float(n.get('lon')),float(n.get('lat'))) for n in root_xml.findall('node')}
ring=[nodes[n.get('ref')] for n in way.findall('nd')]
if ring[0]==ring[-1]: ring.pop()
lon_m=111412.84*math.cos(math.radians(40.4274)); lat_m=111040.0
source=[((lon+86.9137)*lon_m,(lat-40.4274)*lat_m) for lon,lat in ring]
world=[obj.matrix_world @ v.co for v in obj.data.vertices]
bottom=[v for v in world if abs(v.z)<1e-6]
errs=[]
for p in source:
    errs.append(min(math.hypot(v.x-p[0],v.y-p[1]) for v in bottom))
xs=[v.x for v in world];ys=[v.y for v in world];zs=[v.z for v in world]
external=[{'name':i.name,'filepath':i.filepath} for i in bpy.data.images if i.source=='FILE' and i.filepath]
collection=bpy.data.collections['Asset_massing_mcdonald_s_ab77b70']
res={'blend_path':str(blend),'saved_file_reopened':True,'object':obj.name,'collection':collection.name,'collection_object_count':len(collection.objects),'object_type':obj.type,'mesh_vertices':len(obj.data.vertices),'mesh_edges':len(obj.data.edges),'mesh_faces':len(obj.data.polygons),'modifiers':[m.name for m in obj.modifiers],'identity_transform':True,'source_osm_way':256640455,'source_outline_vertices':len(source),'wall_footprint_vertex_error_max_m':max(errs),'all_source_vertices_present':max(errs)<0.0002,'bounds_world_m':{'min':[min(xs),min(ys),min(zs)],'max':[max(xs),max(ys),max(zs)],'dimensions':[max(xs)-min(xs),max(ys)-min(ys),max(zs)-min(zs)]},'external_file_images':external,'portable_no_external_images':len(external)==0}
assert res['collection_object_count']==1 and res['all_source_vertices_present'] and not external
out=root/'audit/mcdonald_s/reopen_check.json'; out.write_text(json.dumps(res,indent=2)+'\n',encoding='utf-8')
print(json.dumps(res,indent=2))

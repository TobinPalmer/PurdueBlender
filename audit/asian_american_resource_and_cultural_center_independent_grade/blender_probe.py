import bpy, json, math, hashlib, os
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ASSET=ROOT/'modular/buildings/asian_american_resource_and_cultural_center.blend'
MASTER=ROOT/'purdue_campus_master.blend'
GIS=HERE/'sources/aaarcc_gis_feature_926.json'
MANIFEST=HERE/'sources/manifest_snapshot.json'

def bounds(objs):
    deps=bpy.context.evaluated_depsgraph_get(); pts=[]
    for obj in objs:
        if obj.type not in {'MESH','CURVE','FONT','SURFACE','META'}: continue
        ob=obj.evaluated_get(deps)
        pts.extend(ob.matrix_world @ Vector(c) for c in ob.bound_box)
    if not pts: return None
    return [[float(min(p[i] for p in pts)),float(max(p[i] for p in pts))] for i in range(3)]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads(MANIFEST.read_text(encoding='utf-8-sig'))
entry=next(a for a in manifest['assets'] if a.get('id')=='asian_american_resource_and_cultural_center')
payload=json.loads(GIS.read_text(encoding='utf-8-sig')); feature=payload[0] if isinstance(payload,list) else payload
attrs=feature['attributes']; ring=feature['geometry']['rings'][0]
lon_scale=111412.84*math.cos(math.radians(40.4274)); lat_scale=111040.0
campus=[((p[0]+86.9137)*lon_scale,(p[1]-40.4274)*lat_scale) for p in ring]
source_center=((min(p[0] for p in campus)+max(p[0] for p in campus))/2,(min(p[1] for p in campus)+max(p[1] for p in campus))/2)
source_local=[(p[0]-source_center[0],p[1]-source_center[1]) for p in campus]
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.data.scenes.get(entry['scene']); collection=bpy.data.collections.get(entry['collection']); assert scene and collection
objects=list(collection.all_objects)
types={}
for obj in objects: types[obj.type]=types.get(obj.type,0)+1
plinth=bpy.data.objects.get('AAARCC exact GIS perimeter | stone plinth')
base_xy=[]
if plinth:
  base_xy=[(float(v.co.x),float(v.co.y)) for v in plinth.data.vertices]
def near(a,pts): return min(math.hypot(a[0]-b[0],a[1]-b[1]) for b in pts)
source_to_model=[near(p,base_xy) for p in source_local] if base_xy else []
model_to_source=[near(p,source_local) for p in base_xy] if base_xy else []
unmaterialed=[o.name for o in objects if o.type=='MESH' and (not o.data.materials or all(m is None for m in o.data.materials))]
external_libraries=[{'path':l.filepath,'absolute':bpy.path.abspath(l.filepath)} for l in bpy.data.libraries]
external_images=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath and not im.packed_file: external_images.append({'name':im.name,'filepath':im.filepath,'resolved':bpy.path.abspath(im.filepath)})
asset_probe={'asset_path':str(ASSET.relative_to(ROOT)),'sha256':sha(ASSET),'bytes':ASSET.stat().st_size,'blender_version':bpy.app.version_string,'scene':scene.name,'render_engine':scene.render.engine,'collection':collection.name,'object_count':len(objects),'type_counts':types,'object_names':sorted(o.name for o in objects),'object_names_match_manifest':sorted(o.name for o in objects)==sorted(entry.get('objects',[])),'manifest_object_count':entry.get('object_count'),'object_count_matches_manifest':len(objects)==entry.get('object_count'),'bounds_local_m':bounds(objects),'manifest_local_bounds_m':entry.get('local_bounds_m'),'root_empty':[o.name for o in objects if o.type=='EMPTY'],'plinth':plinth.name if plinth else None,'plinth_vertex_count':len(base_xy),'gis_feature_id':attrs.get('FID'),'gis_building_code':attrs.get('BLDG_ABBR'),'gis_building_name':attrs.get('BUILDING_N'),'gis_ring_vertex_count_including_closure':len(ring),'source_ring_vertex_count':len(source_local)-1 if source_local and source_local[0]==source_local[-1] else len(source_local),'source_local_center_xy_m':list(source_center),'source_local_bounds_m':[[min(p[i] for p in source_local),max(p[i] for p in source_local)] for i in (0,1)],'gis_to_plinth_nearest_avg_m':sum(source_to_model)/len(source_to_model) if source_to_model else None,'gis_to_plinth_nearest_max_m':max(source_to_model) if source_to_model else None,'plinth_to_gis_nearest_avg_m':sum(model_to_source)/len(model_to_source) if model_to_source else None,'plinth_to_gis_nearest_max_m':max(model_to_source) if model_to_source else None,'unmaterialed_mesh_count':len(unmaterialed),'unmaterialed_meshes':unmaterialed,'external_libraries':external_libraries,'unpacked_file_images':external_images,'modifier_count':sum(len(o.modifiers) for o in objects),'has_preview_sibling':bpy.data.collections.get('Preview_only') is not None}
(HERE/'blender_asset_probe.json').write_text(json.dumps(asset_probe,indent=2)+'\n',encoding='utf-8')
# Read-only placement/link probe in the master.
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
markers=[o for o in bpy.data.objects if o.name=='Placement_asian_american_resource_and_cultural_center']
master={'master_path':str(MASTER.relative_to(ROOT)),'marker_count':len(markers),'markers':[]}
for m in markers:
 master['markers'].append({'name':m.name,'location':[float(v) for v in m.location],'rotation_degrees':[math.degrees(float(v)) for v in m.rotation_euler],'scale':[float(v) for v in m.scale],'instance_collection':m.instance_collection.name if m.instance_collection else None,'library_path':m.instance_collection.library.filepath if m.instance_collection and m.instance_collection.library else None})
(HERE/'master_placement_probe.json').write_text(json.dumps(master,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'asset':{k:v for k,v in asset_probe.items() if k not in ('object_names',)},'master':master},indent=2))

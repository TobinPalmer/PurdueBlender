import bpy, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/massing_crosswalk_commons_7c01ecd.blend'
EVIDENCE=ROOT/'audit/crosswalk_commons'
SOURCE=json.loads((EVIDENCE/'sources/osm_way_231217849_full.json').read_text(encoding='utf-8-sig'))
WAY=next(e for e in SOURCE['elements'] if e['type']=='way' and e['id']==231217849)
NODES={e['id']:e for e in SOURCE['elements'] if e['type']=='node'}
ring=[]
for node_id in WAY['nodes'][:-1]:
    n=NODES[node_id]
    ring.append(((n['lon']+86.9137)*111412.84*math.cos(math.radians(40.4274)),(n['lat']-40.4274)*111040.0))
scene=bpy.data.scenes.get('Building_massing_crosswalk_commons_7c01ecd')
collection=bpy.data.collections.get('Asset_massing_crosswalk_commons_7c01ecd')
objects=list(collection.objects) if collection else []
obj=next((o for o in objects if o.name=='Crosswalk Commons'),None)
verts=[obj.matrix_world @ v.co for v in obj.data.vertices] if obj and obj.type=='MESH' else []
bottom=[v for v in verts if abs(v.z)<1e-5]
nearest=[]
for x,y in ring:
    nearest.append(min((math.hypot(v.x-x,v.y-y) for v in bottom),default=float('inf')))
materials=[m.name if m else None for m in obj.data.materials] if obj else []
image_paths=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath]
report={
  'blender_version':bpy.app.version_string,
  'asset_reopened':bpy.data.filepath.lower()==str(ASSET).lower(),
  'asset_path':str(ASSET.relative_to(ROOT)).replace('\\','/'),
  'scene_name':scene.name if scene else None,
  'collection_name':collection.name if collection else None,
  'collection_object_names':[o.name for o in objects],
  'expected_single_mesh_object':len(objects)==1 and obj is not None and obj.type=='MESH',
  'dimensions_m':list(obj.dimensions) if obj else None,
  'world_bounds_m':[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)] if verts else None,
  'material_slots':materials,
  'modifiers':[{ 'name':m.name,'type':m.type } for m in obj.modifiers] if obj else None,
  'external_image_dependencies':image_paths,
  'osm_footprint_vertices_represented_at_ground':len(bottom)>=len(ring) and max(nearest,default=0)<1e-4,
  'max_osm_ring_vertex_error_m':max(nearest,default=None),
  'mesh_vertex_count':len(verts),
  'result':'PASS' if scene and collection and len(objects)==1 and obj and obj.type=='MESH' and len(bottom)>=len(ring) and max(nearest,default=1)<1e-4 and not image_paths else 'FAIL'
}
(EVIDENCE/'validation_report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))

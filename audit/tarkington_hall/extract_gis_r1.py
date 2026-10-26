import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path.cwd()
out=root/'audit'/'tarkington_hall'
source=json.load(open(root/'audit'/'official_purdue_buildings_wgs84.json',encoding='utf-8'))
feature=next(f for f in source['features'] if f.get('attributes',{}).get('FID')==662)
meta={'provider':'Purdue University campus GIS BuildingShapesZip4 FeatureServer layer 0','source_url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','query_url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D662&outFields=*&returnGeometry=true&outSR=4326&f=pjson','feature_id':662,'building_code':'TARK','snapshot_retrieved_date':'2026-10-22','packaged_date':'2026-10-25','source_crs':source.get('spatialReference'),'source_snapshot':'audit/official_purdue_buildings_wgs84.json'}
json.dump({'metadata':meta,'feature':feature},open(out/'gis_feature_662.json','w',encoding='utf-8'),indent=2)
# Structural shell object set from existing building-specific audit selection ledger
ledger=json.load(open(root/'audit'/'master_building_audit.json',encoding='utf-8'))
records=ledger['records']
rec=next(r for r in records if r.get('id')=='tarkington_hall')
names=set(rec['shell_candidates'])
objects=[]
for o in bpy.data.objects:
    if o.name not in names or o.type!='MESH': continue
    verts=[o.matrix_world @ v.co for v in o.data.vertices]
    objects.append({'name':o.name,'vertices_xy':[[float(v.x),float(v.y)] for v in verts]})
json.dump({'asset':bpy.data.filepath,'asset_root':'AssetRoot_tarkington_hall','asset_local_xy_origin_m':[-591.6124877929688,348.0],'object_count':len(objects),'objects':objects,'selection_source':'audit/master_building_audit.json shell_candidates for id=tarkington_hall','coordinates':'evaluated object matrix_world in modular asset local coordinates; X east, Y north, meters'},open(out/'shell_vertices_r1.json','w',encoding='utf-8'),indent=2)
print('saved source feature',feature['attributes']['BUILDING_N'],'rings',len(feature['geometry']['rings']))
print('shell objects extracted',len(objects),[x['name'] for x in objects])


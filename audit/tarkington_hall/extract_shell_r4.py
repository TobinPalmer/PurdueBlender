import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path.cwd(); out=root/'audit'/'tarkington_hall'
ledger=json.load(open(root/'audit'/'master_building_audit.json',encoding='utf-8'))
rec=next(r for r in ledger['records'] if r.get('id')=='tarkington_hall')
names=set(rec['shell_candidates']); objects=[]
asset=bpy.data.collections.get('Asset_tarkington_hall')
if asset is None: raise RuntimeError('Missing Asset_tarkington_hall')
for o in asset.objects:
 connector_shell = o.name.startswith(('Tark_West_Connector_Limestone_Base','Tark_West_Connector_Brick_Shaft','Tark_West_Connector_Limestone_Belt_','Tark_West_Connector_Roof_Membrane','Tark_West_Connector_Roof_Parapet','Tark_East_Connector_Limestone_Base','Tark_East_Connector_Brick_Shaft','Tark_East_Connector_Limestone_Belt_','Tark_East_Connector_Roof_Membrane','Tark_East_Connector_Roof_Parapet','Tark_West_Core_Connector_Limestone_Base','Tark_West_Core_Connector_Brick_Shaft','Tark_West_Core_Connector_Limestone_Belt_','Tark_West_Core_Connector_Roof_Membrane','Tark_West_Core_Connector_Roof_Parapet','Tark_East_Core_Connector_Limestone_Base','Tark_East_Core_Connector_Brick_Shaft','Tark_East_Core_Connector_Limestone_Belt_','Tark_East_Core_Connector_Roof_Membrane','Tark_East_Core_Connector_Roof_Parapet','Tark_South_Lobby_Core_Limestone_Base','Tark_South_Lobby_Core_Brick_Shaft','Tark_South_Lobby_Core_Limestone_Belt_','Tark_South_Lobby_Core_Roof_Membrane','Tark_South_Lobby_Core_Roof_Parapet'))
 if (o.name in names or connector_shell) and o.type=='MESH':
  verts=[o.matrix_world@v.co for v in o.data.vertices]
  objects.append({'name':o.name,'vertices_xy':[[float(v.x),float(v.y)] for v in verts]})
json.dump({'asset':bpy.data.filepath,'asset_root':'AssetRoot_tarkington_hall','export_collection':'Asset_tarkington_hall','asset_local_xy_origin_m':[-591.6124877929688,348.0],'object_count':len(objects),'objects':objects,'selection_source':'shell_candidates for id=tarkington_hall from read-only audit/master_building_audit.json plus structural connector objects; extracted strictly from Asset_tarkington_hall','coordinates':'object matrix_world; X east, Y north, meters'},open(out/'shell_vertices_r4.json','w',encoding='utf-8'),indent=2)
print('shell objects',len(objects))


import bpy,json,hashlib,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
paths=[ROOT/'modular/buildings/black_cultural_center.blend',HERE/'builder_smoke_project/modular/buildings/black_cultural_center.blend']
def summary(p):
 bpy.ops.wm.open_mainfile(filepath=str(p)); c=bpy.data.collections.get('Asset_black_cultural_center'); assert c
 rows=[]
 for o in sorted(c.all_objects,key=lambda x:x.name):
  row={'name':o.name,'type':o.type,'location':[round(float(v),8) for v in o.location],'rotation':[round(float(v),8) for v in o.rotation_euler],'scale':[round(float(v),8) for v in o.scale]}
  if o.type=='MESH':
   h=hashlib.sha256()
   for v in o.data.vertices: h.update(struct.pack('<3f',*v.co))
   row.update({'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'mesh_xyz_sha256':h.hexdigest(),'materials':[m.name if m else None for m in o.data.materials]})
  elif o.type=='FONT': row.update({'body':o.data.body,'size':float(o.data.size),'materials':[m.name if m else None for m in o.data.materials]})
  rows.append(row)
 return {'path':str(p.relative_to(ROOT)) if ROOT in p.parents else str(p),'count':len(rows),'rows':rows}
a=summary(paths[0]); b=summary(paths[1]); amap={x['name']:x for x in a['rows']}; bmap={x['name']:x for x in b['rows']}
common=set(amap)&set(bmap)
report={'current_asset':a['path'],'rebuild_asset':b['path'],'current_count':a['count'],'rebuild_count':b['count'],'same_object_name_set':set(amap)==set(bmap),'same_transforms_and_mesh_data':all(amap[n]==bmap[n] for n in common),'differing_object_count':sum(amap[n]!=bmap[n] for n in common),'different_object_names':sorted(set(amap)^set(bmap))}
(HERE/'builder_rebuild_geometry_comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,indent=2)); assert report['same_object_name_set'] and report['same_transforms_and_mesh_data']

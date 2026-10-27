import bpy, json, math, hashlib
from pathlib import Path
asset=Path(bpy.data.filepath); root=asset.parents[2]; d=root/'audit'/'convergence_center'/'independent_grade_r1'; c=bpy.data.collections.get('Asset_convergence_center'); objs=list(c.all_objects) if c else []
interesting=[]
for o in objs:
 n=o.name.casefold()
 if any(k in n for k in ('lobby','reception','mezz','interior','atrium','monument','portal','window','cladding','sign','floor_')):
  dim=[float(x) for x in o.dimensions] if o.type=='MESH' else []
  interesting.append({'name':o.name,'type':o.type,'location':[float(x) for x in o.location],'dimensions':dim,'material_names':[m.name for m in o.data.materials if m] if o.type=='MESH' else []})
imgs=[]; missing=[]
for image in bpy.data.images:
 if image.name in ('Render Result','Viewer Node'): continue
 imgs.append({'name':image.name,'packed':bool(image.packed_file),'path':image.filepath})
for mat in bpy.data.materials:
 if not mat.use_nodes or not mat.node_tree: continue
 for node in mat.node_tree.nodes:
  if node.type=='TEX_IMAGE':
   if not node.image: missing.append({'material':mat.name,'node':node.name})
   elif node.image.filepath and not node.image.packed_file:
    path=bpy.path.abspath(node.image.filepath)
    if not Path(path).exists(): missing.append({'material':mat.name,'path':path})
props={}
if c:
 for k in ('building_id','source_feature_id','placement_origin_xy_m','local_coordinates'):
  v=c.get(k); props[k]=list(v) if hasattr(v,'__iter__') and not isinstance(v,(str,bytes)) else v
probe={'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'collection':c.name if c else None,'custom_properties':props,'object_count':len(objs),'mesh_count':sum(o.type=='MESH' for o in objs),'interesting_objects':interesting,'images':imgs,'missing_images_or_nodes':missing}
(d/'direct_asset_probe.json').write_text(json.dumps(probe,indent=2,default=str),encoding='utf-8');print(json.dumps(probe,indent=2,default=str))


import bpy, json, hashlib
from pathlib import Path
asset=Path(bpy.data.filepath)
record={'file':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'scene':bpy.context.scene.name,'scenes':[],'collections':[],'objects':[],'materials':[]}
for scene in bpy.data.scenes:
 record['scenes'].append({'name':scene.name,'objects':len(scene.objects),'camera':scene.camera.name if scene.camera else None})
for c in bpy.data.collections:
 if c.name.startswith('Asset_') or c.name.startswith('Building_'):
  record['collections'].append({'name':c.name,'objects':[o.name for o in c.all_objects],'library':c.library.filepath if c.library else None})
for o in bpy.data.objects:
 if o.type=='MESH':
  dims=[round(float(v),4) for v in o.dimensions]
  mw=o.matrix_world
  coords=[mw @ v.co for v in o.data.vertices]
  if coords:
   bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
  else: bounds=None
  record['objects'].append({'name':o.name,'type':o.type,'dims':dims,'loc':[round(float(v),6) for v in o.location],'rot':[round(float(v),6) for v in o.rotation_euler],'scale':[round(float(v),6) for v in o.scale],'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'bounds_world':bounds,'materials':[m.name if m else None for m in o.data.materials]})
for m in bpy.data.materials:
 record['materials'].append({'name':m.name,'nodes':m.use_nodes,'base_color':list(m.diffuse_color),'image_nodes':[n.image.filepath if n.image else None for n in m.node_tree.nodes if n.type=='TEX_IMAGE'] if m.use_nodes and m.node_tree else []})
out=Path(__file__).with_name('initial_asset_inventory.json')
out.write_text(json.dumps(record,indent=2))
print(out)
print(json.dumps({'sha256':record['sha256'],'scenes':record['scenes'],'collections':record['collections'],'objects':record['objects'],'materials':record['materials']},indent=2))

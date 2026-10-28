import bpy, json
p=r'modular/buildings/massing_house_301836574_fff1661.blend'
bpy.ops.wm.open_mainfile(filepath=p)
out={'scene':bpy.context.scene.name,'objects':[],'collections':[]}
for c in bpy.data.collections:
 if 'Asset_massing_house_301836574_fff1661' in c.name or c.name=='Scene Collection': out['collections'].append(c.name)
for o in bpy.data.objects:
 if o.type=='MESH':
  me=o.data
  out['objects'].append({'name':o.name,'collection':[c.name for c in o.users_collection],'verts':len(me.vertices),'faces':len(me.polygons),'dims':list(o.dimensions),'loc':list(o.location),'materials':[m.name if m else None for m in me.materials],'bounds':[[min(v.co[i] for v in me.vertices) for i in range(3)],[max(v.co[i] for v in me.vertices) for i in range(3)]]})
open(r'audit/phi_mu_fid772/base_asset_inspection.json','w').write(json.dumps(out,indent=2))

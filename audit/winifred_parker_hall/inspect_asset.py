import bpy, json, hashlib, os
from pathlib import Path
from mathutils import Vector
blend = Path(bpy.data.filepath)
coll = bpy.data.collections.get('Asset_winifred_parker_hall')
if not coll: raise RuntimeError('Expected export collection missing')
def box(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    corners=[ev.matrix_world @ Vector(c) for c in ev.bound_box]
    return [[min(v[i] for v in corners),max(v[i] for v in corners)] for i in range(3)]
objs=list(coll.all_objects)
items=[]
for o in objs:
    items.append({'name':o.name,'type':o.type,'loc':list(o.location),'dim':list(o.dimensions),'bounds':box(o),'parent':o.parent.name if o.parent else None,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'verts':len(o.data.vertices) if o.type=='MESH' else None,'faces':len(o.data.polygons) if o.type=='MESH' else None})
# pairwise overlap candidate exact duplicates among named main masses
main=[x for x in items if 'MainMass' in x['name']]
checks=[]
for i,a in enumerate(main):
 for b in main[i+1:]:
  widths=[max(0,min(a['bounds'][d][1],b['bounds'][d][1])-max(a['bounds'][d][0],b['bounds'][d][0])) for d in range(3)]
  overlap=widths[0]*widths[1]*widths[2]
  minvol=min(max(0,a['dim'][0]*a['dim'][1]*a['dim'][2]),max(0,b['dim'][0]*b['dim'][1]*b['dim'][2]))
  if minvol>0 and overlap/minvol>.8: checks.append({'a':a['name'],'b':b['name'],'overlap_ratio_min_vol':overlap/minvol,'overlap_volume':overlap})
materials=[]
used={m for o in objs if o.type=='MESH' for m in o.data.materials if m}
for m in sorted(used,key=lambda m:m.name):
 nt=m.node_tree
 materials.append({'name':m.name,'nodes':[n.type for n in nt.nodes] if nt else [],'image_nodes':[n.image.filepath for n in nt.nodes if n.type=='TEX_IMAGE' and n.image] if nt else []})
report={'file':str(blend),'sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'scene':bpy.context.scene.name,'scene_object_count':len(bpy.context.scene.objects),'collection_object_count':len(objs),'collection_mesh_count':sum(o.type=='MESH' for o in objs),'collection_bounds':[[min(box(o)[i][0] for o in objs if o.type=='MESH'),max(box(o)[i][1] for o in objs if o.type=='MESH')] for i in range(3)],'scene_camera':bpy.context.scene.camera.name if bpy.context.scene.camera else None,'cameras':[o.name for o in bpy.data.objects if o.type=='CAMERA'],'material_count':len(used),'materialless_mesh_count':sum(o.type=='MESH' and not any(o.data.materials) for o in objs),'invalid_material_index_polys':sum(sum(p.material_index>=len(o.data.materials) for p in o.data.polygons) for o in objs if o.type=='MESH'),'main_mass_candidates':main,'main_mass_high_overlap':checks,'materials':materials,'objects':items}
out=blend.parent.parent.parent/'audit'/'winifred_parker_hall'/'baseline_asset_inspection.json'
out.write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['objects','materials']},indent=2))
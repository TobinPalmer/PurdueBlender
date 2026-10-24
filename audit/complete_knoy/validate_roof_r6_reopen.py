import bpy, json, os
from mathutils import Vector
ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET_PATH=ROOT+r'/modular/buildings/knoy_hall.blend'
OUT=ROOT+r'/audit/complete_knoy/roof_equipment_validation_r6.json'
bpy.ops.wm.open_mainfile(filepath=ASSET_PATH)
asset=bpy.data.collections.get('Asset_knoy_hall')
root=bpy.data.objects.get('AssetRoot_knoy_hall')
pv=bpy.data.objects.get('KNOY_Roof_PV_28Panel_Array_R6')
rack=bpy.data.objects.get('KNOY_Roof_PV_Racking_R6')
pent=bpy.data.objects.get('KNOY_Roof_Mechanical_Penthouse')
assert asset and root and pv and rack and pent
objs=list(asset.all_objects); meshes=[o for o in objs if o.type=='MESH']
issues=[]
root_ident=all(abs(root.matrix_world[i][j]-(1 if i==j else 0))<1e-6 for i in range(4) for j in range(4))
if not root_ident: issues.append('Asset root transform changed')
if pv['modeled_panel_count']!=28 or len(pv.data.polygons)!=168: issues.append('PV module count/mesh check failed')
if pv.name not in asset.objects or rack.name not in asset.objects: issues.append('PV or rack missing from asset collection')
if pv.parent is None: issues.append('PV parent relationship lost')
if any('cooling' in o.name.lower() or 'tower' in o.name.lower() for o in objs): issues.append('Unsupported cooling-tower geometry present')
if 'Unverified schematic placeholder' not in pent.get('evidence_status',''): issues.append('Penthouse uncertainty metadata missing')
unmat=[o.name for o in meshes if len(o.data.materials)==0]
bad=[]
for o in meshes:
 for m in o.data.materials:
  if m is None or not m.node_tree or not any(n.type=='OUTPUT_MATERIAL' for n in m.node_tree.nodes): bad.append(o.name)
if unmat: issues.append('Unmaterialed mesh found')
if bad: issues.append('Material output issue found')
pts=[pv.matrix_world@v.co for v in pv.data.vertices]
report=json.load(open(OUT,encoding='utf-8'))
report['asset_file']='modular/buildings/knoy_hall.blend'
report.pop('candidate_saved_as',None)
report['saved_main_asset_reopened']=True
report['asset_root_identity']=root_ident
report['source_mesh_count']=len(meshes)
report['source_unmaterialed_mesh_count']=len(unmat)
report['source_material_output_issue_count']=len(set(bad))
report['pv_parent_relationship_preserved']=pv.parent is not None
report['pv_bounds_asset_local_xy_m']=[round(min(p.x for p in pts),3),round(max(p.x for p in pts),3),round(min(p.y for p in pts),3),round(max(p.y for p in pts),3)]
report['issues']=issues
with open(OUT,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
assert not issues, issues

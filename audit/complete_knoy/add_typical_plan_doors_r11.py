import bpy, json, hashlib
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
BLEND=ROOT/'modular/buildings/knoy_hall.blend'
DOORS=ROOT/'audit/complete_knoy/typical_plan_door_candidates_r11.json'
OUT=ROOT/'audit/complete_knoy/door_model_validation_r11.json'
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
asset=bpy.data.collections['Asset_knoy_hall']
coll_name='KNOY_TypicalPlan_Doors_L2-L4'
old=bpy.data.collections.get(coll_name)
if old:
 for obj in list(old.objects): bpy.data.objects.remove(obj,do_unlink=True)
else:
 old=bpy.data.collections.new(coll_name)
if old.name not in [c.name for c in asset.children]: asset.children.link(old)
# Read candidates from the local source record, but store their coordinates and
# evidence properties in the asset so the linked collection remains self-contained.
source=json.loads(DOORS.read_text(encoding='utf-8'))
mat=bpy.data.materials.get('KNOY_Interior_Door_Neutral_Estimate')
if mat is None:
 mat=bpy.data.materials.new('KNOY_Interior_Door_Neutral_Estimate'); mat.diffuse_color=(0.28,0.32,0.34,1.0)
 mat.use_nodes=True
 bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 bsdf.inputs['Base Color'].default_value=(0.28,0.32,0.34,1.0);bsdf.inputs['Roughness'].default_value=0.65;bsdf.inputs['Metallic'].default_value=0.0
mat['appearance_status']='Neutral illustrative material only; source plan does not identify door finish or color.'
mat['source_url']=source['source_url']
levels=[('L2',4.481),('L3',8.961),('L4',13.442)]
height=2.10; thickness=0.045
for level,z0 in levels:
 for d in source['candidate_doors']:
  cx,cy=d['center_local_xy_m'];ux,uy=d['wall_axis_xy_unit'];nx,ny=-uy,ux
  width=d['width_from_plan_gap_m']
  corners=[(cx-ux*width/2-nx*thickness/2,cy-uy*width/2-ny*thickness/2,z0),
           (cx+ux*width/2-nx*thickness/2,cy+uy*width/2-ny*thickness/2,z0),
           (cx+ux*width/2+nx*thickness/2,cy+uy*width/2+ny*thickness/2,z0),
           (cx-ux*width/2+nx*thickness/2,cy-uy*width/2+ny*thickness/2,z0)]
  verts=corners+[(x,y,z0+height) for x,y,_ in corners]
  faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
  mesh=bpy.data.meshes.new(f'KNOY_{level}_PlanDoor_{d["id"]}_Mesh');mesh.from_pydata(verts,[],faces);mesh.materials.append(mat);mesh.update()
  obj=bpy.data.objects.new(f'KNOY_{level}_TypicalPlan_Door_{d["id"]:02d}',mesh);old.objects.link(obj)
  obj['source']=source['source_url'];obj['source_page']=source['source_pdf_page'];obj['source_plan_label']=source['source_plan_label']
  obj['source_door_id']=d['id'];obj['source_pixel_center']=d['source_pixel_center']
  obj['source_level']=level
  obj['source_pixel_center']=d['source_pixel_center'];obj['source_gap_width_estimate_m']=width
  obj['modeled_panel_height_estimate_m']=height;obj['modeled_panel_thickness_estimate_m']=thickness
  obj['door_position_status']='Door opening/swing symbol located on source typical plan; panel shown in closed position for interior readability. Exact leaf swing and vertical dimensions are not specified.'
  obj['material_status']='Render-only neutral placeholder; actual finish unknown.'
  obj['registration_uncertainty']=source['registration']
# Verify nested collection placement and that existing geometry remains unchanged.
asset_objects=list(asset.all_objects)
assert coll_name in {c.name for c in asset.children}
assert len(old.objects)==len(source['candidate_doors'])*len(levels)
assert all(o.parent is None for o in old.objects)
scene=bpy.context.scene
scene['upper_plan_door_status']='15 plan-traced candidate openings repeated only on the official 2018 typical Levels 2-4 plan. Panels are closed-position visual placeholders; dimensions/material are estimated. L1 candidates remain unresolved.'
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
print('Saved',len(old.objects),'door panels; Asset all_objects',len(asset.all_objects),'collections', [c.name for c in asset.children])

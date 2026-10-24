import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
BLEND=ROOT/'modular/buildings/knoy_hall.blend'
TRACE=ROOT/'audit/complete_knoy/upper_plan_wall_trace.json'
CAND=ROOT/'audit/complete_knoy/typical_plan_fixture_candidates_r12.json'
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
asset=bpy.data.collections['Asset_knoy_hall'];name='KNOY_TypicalPlan_WashroomFixtures_L2-L4'
old=bpy.data.collections.get(name)
if old:
 for o in list(old.objects):bpy.data.objects.remove(o,do_unlink=True)
else:
 old=bpy.data.collections.new(name)
if name not in {c.name for c in asset.children}:asset.children.link(old)
trace=json.loads(TRACE.read_text(encoding='utf-8'));aff=trace['pixel_to_local_xy_affine'];data=json.loads(CAND.read_text(encoding='utf-8'))
def xy(u,v):return (aff['x'][0]*u+aff['x'][1]*v+aff['x'][2],aff['y'][0]*u+aff['y'][1]*v+aff['y'][2])
mat=bpy.data.materials.get('KNOY_Washroom_Fixture_Neutral_Estimate')
if not mat:
 mat=bpy.data.materials.new('KNOY_Washroom_Fixture_Neutral_Estimate');mat.diffuse_color=(0.78,0.80,0.79,1);mat.use_nodes=True
 bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bsdf.inputs['Base Color'].default_value=(0.78,0.80,0.79,1);bsdf.inputs['Roughness'].default_value=.42;bsdf.inputs['Metallic'].default_value=0
mat['evidence_source']=data['source_url'];mat['appearance_status']='Neutral display placeholder only; source plan gives no fixture material/finish.'
levels=[('L2',4.481),('L3',8.961),('L4',13.442)]
def add_sphere(bm,center,scale,segments=12,rings=8):
 res=bmesh.ops.create_uvsphere(bm,u_segments=segments,v_segments=rings,radius=1)
 vs=res['verts'];bmesh.ops.scale(bm,verts=vs,vec=Vector(scale));bmesh.ops.translate(bm,verts=vs,vec=Vector(center))
def add_box(bm,center,scale):
 res=bmesh.ops.create_cube(bm,size=1);vs=res['verts'];bmesh.ops.scale(bm,verts=vs,vec=Vector(scale));bmesh.ops.translate(bm,verts=vs,vec=Vector(center))
def save_fixture(name,objtype,candidate,level,zbase):
 u,v=candidate['center_pixel'];cx,cy=xy(u,v);bm=bmesh.new()
 if objtype=='toilet':
  # Bowl is directed toward the room (west); tank sits against the east partition.
  add_sphere(bm,(cx-.15,cy,zbase+.43),(.22,.29,.22),16,10)
  add_box(bm,(cx+.18,cy,zbase+.63),(.40,.22,.48))
  width=.44;depth=.72;height=.87
 else:
  # Compact wall-side basin/counter symbol; plumbing and exact pedestal type are unknown.
  add_box(bm,(cx+.10,cy,zbase+.82),(.50,.42,.10))
  add_sphere(bm,(cx+.08,cy,zbase+.91),(.20,.25,.08),14,8)
  width=.50;depth=.50;height=.99
 mesh=bpy.data.meshes.new(name+'_Mesh');bm.to_mesh(mesh);bm.free();mesh.materials.append(mat);mesh.update()
 obj=bpy.data.objects.new(name,mesh);old.objects.link(obj)
 obj['source_url']=data['source_url'];obj['source_plan_page']=24;obj['source_level_basis']='Typical Plan Levels 2-4; repeated on modeled Levels 2, 3, and 4.'
 obj['source_feature_id']=candidate['id'];obj['source_feature_pixel_center']=candidate['center_pixel'];obj['interpreted_fixture_type']=objtype
 obj['registration_uncertainty']=data['registration'];obj['estimated_model_size_m']=[width,depth,height]
 obj['geometry_status']='Simplified 3D stand-in for a plan symbol. Fixture type/count interpretation is moderate confidence; exact size, height, plumbing, material, and current condition are not specified by source.'
for level,zbase in levels:
 for cand in data['candidates']:
  code=cand['type'];label='WC' if code=='toilet' else 'Basin'
  save_fixture(f'KNOY_{level}_PlanFixture_{label}_{cand["id"]}',code,cand,level,zbase)
scene=bpy.context.scene
scene['washroom_fixture_status']='Two plan-visible fixture banks represented with simplified placeholders on L2-L4. Type/count are visual interpretations from the 2018 raster; dimensions/materials are estimated. No current room use/condition is asserted.'
assert len(old.objects)==len(data['candidates'])*len(levels)==39
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
print('Saved',len(old.objects),'plan-derived washroom fixture objects; total asset hierarchy',len(asset.all_objects))

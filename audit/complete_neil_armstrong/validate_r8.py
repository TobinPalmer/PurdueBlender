"""Reopen and validate Neil R8; writes only its dedicated audit record."""
import bpy, json, os, hashlib
from mathutils import Vector, Matrix
ROOT=r'C:\\Users\\Tobin\\Documents\\Blender\\PurdueMap'
BASE=os.path.join(ROOT,'audit','complete_neil_armstrong')
ASSET=os.path.join(ROOT,'modular','buildings','neil_armstrong_hall.blend')
R7=os.path.join(ROOT,'modular','buildings','neil_armstrong_hall.blend1')
REMOVED={'ARMS_East_Roof_Penthouse','ARMS_East_Penthouse_Louvers','ARMS_West_Roof_Penthouse','ARMS_West_Penthouse_Louvers'}
def asset_snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    col=bpy.data.collections['Asset_neil_armstrong_hall']; root=bpy.data.objects['AssetRoot_neil_armstrong_hall']
    items={}
    for o in col.objects:
        mesh=None
        if o.type=='MESH':
            mesh=(tuple((round(v.co.x,6),round(v.co.y,6),round(v.co.z,6)) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons))
        items[o.name]={'type':o.type,'matrix':tuple(round(float(x),8) for row in o.matrix_basis for x in row),'mesh':mesh}
    return items,tuple(float(x) for x in root.location),len(col.objects),bpy.context.scene.name
r7_hash=hashlib.sha256(open(R7,'rb').read()).hexdigest()
with open(os.path.join(BASE,'validation_r7.json'),encoding='utf-8') as f:r7_validation=json.load(f)
assert r7_hash==r7_validation['source_hash']
r7,root7,n7,scene7=asset_snapshot(R7)
r8_hash=hashlib.sha256(open(ASSET,'rb').read()).hexdigest()
r8,root8,n8,scene8=asset_snapshot(ASSET)
assert scene7==scene8=='Building_neil_armstrong_hall'
assert root7==root8==(0.0,0.0,0.0) and n7==449 and n8==445
assert set(r7)-set(r8)==REMOVED and not (set(r8)-set(r7))
changed=[k for k in set(r7)&set(r8) if r7[k]!=r8[k]]
assert not changed, changed
col=bpy.data.collections['Asset_neil_armstrong_hall']; root=bpy.data.objects['AssetRoot_neil_armstrong_hall']
def bounds(objects):
    pts=[o.matrix_world@Vector(c) for o in objects if o.type=='MESH' for c in o.bound_box]
    return [[float(min(p[i] for p in pts)),float(max(p[i] for p in pts))] for i in range(3)]
shell=[o for o in col.objects if o.type=='MESH' and 'Wall' in o.name and not o.name.startswith('ARMS_R5')]
shell_bounds=bounds(shell); old=r7_validation['original_shell_bounds_m']
assert len(shell)==r7_validation.get('shell_wall_count',len(shell))
assert all(abs(shell_bounds[a][b]-old[a][b])<1e-5 for a in range(3) for b in range(2))
for name in REMOVED: assert bpy.data.objects.get(name) is None
for name in ['ARMS_R6_North_Clerestory_Glass','ARMS_R6_North_Clerestory_Mullions']:
    assert bpy.data.objects[name].parent==root
with open(os.path.join(BASE,'roof_height_reconciliation_r8.json'),encoding='utf-8') as f:roof_check=json.load(f)
assert roof_check['high_cell_count_inside_fid_642']==2 and len(roof_check['cells'])==2
with open(os.path.join(ROOT,'audit','batch3_master','placement_check.json'),encoding='utf-8') as f:placement=json.load(f)
marker=next(row for row in placement['rows'] if row['id']=='neil_armstrong_hall')
assert marker['actual_xyz']==[-109.0,400.1893310546875,0.0] and marker['position_error_m']==0.0
renders={name:os.path.getsize(os.path.join(BASE,'renders_r8',name)) for name in ['exterior_lidar_silhouette_r8.png','roof_registered_plan_r8.png','atrium_bridges_enclosure_r8.png']}
assert all(size>100000 for size in renders.values())
result={'building_id':'neil_armstrong_hall','revision':'R8','asset_path':'modular/buildings/neil_armstrong_hall.blend','saved_then_reopened_read_only':True,'scene':scene8,'collection':'Asset_neil_armstrong_hall','object_count':n8,'source_hash':r8_hash,'r7_backup_hash_verified':r7_hash,'r7_to_r8_delta':'Exactly four rooftop penthouse/louver objects removed; every common object transform and mesh vertex/face list is unchanged.','removed_objects':sorted(REMOVED),'all_common_geometry_unchanged':True,'root_location_m':list(root8),'existing_shell_wall_bounds_m':shell_bounds,'r5_r7_gis_lidar_envelopes_preserved':True,'r6_facade_objects_preserved':['ARMS_R6_North_Clerestory_Glass','ARMS_R6_North_Clerestory_Mullions'],'lidar_roof_reconciliation':'roof_height_reconciliation_r8.json; two >22m cells inside FID 642 only, localized at X≈-13.53m, Y≈5.75–7.27m; does not identify penthouse footprint.','placement_marker_read_only':{'xy':marker['actual_xyz'],'error_m':marker['position_error_m'],'rotation':marker['rotation'],'scale':marker['scale']},'renders_r8_png_bytes':renders,'asset_size_bytes':os.path.getsize(ASSET)}
with open(os.path.join(BASE,'validation_r8.json'),'w',encoding='utf-8') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))

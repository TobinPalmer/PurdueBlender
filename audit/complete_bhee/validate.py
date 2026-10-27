import bpy, hashlib, json
from pathlib import Path
from mathutils import Vector

root=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
blend=root/'modular/buildings/electrical_engineering.blend'
report=root/'audit/complete_bhee/check.json'
bpy.ops.wm.open_mainfile(filepath=str(blend))
scene=bpy.context.scene
collection=bpy.data.collections.get('Asset_electrical_engineering')
errors=[]
if scene.name!='Building_electrical_engineering':errors.append('Unexpected scene name')
if collection is None:errors.append('Expected asset collection missing')
objects=list(collection.all_objects) if collection else []
meshes=[o for o in objects if o.type=='MESH']
geometry=json.loads((root/'audit/official_building_references.json').read_text())
source={f['fid']:f for f in geometry['buildings'] if f['fid'] in (292,109)}
component_checks={}
for fid,f in source.items():
 ob=next((o for o in meshes if o.name.startswith('BHEE_ClippedSlabFID'+str(fid))),None)
 if ob is None:
  errors.append(f'Missing footprint plate for feature {fid}')
  continue
 pts=[(x-143.8499984741211,y-135.0) for x,y in f['rings_xy_m'][0]]
 expected=[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]
 actual=[min((ob.matrix_world@v.co).x for v in ob.data.vertices),min((ob.matrix_world@v.co).y for v in ob.data.vertices),max((ob.matrix_world@v.co).x for v in ob.data.vertices),max((ob.matrix_world@v.co).y for v in ob.data.vertices)]
 delta=[actual[i]-expected[i] for i in range(4)]
 component_checks[str(fid)]={'source_bbox_local_m':[round(v,5) for v in expected],'asset_plate_bbox_local_m':[round(v,5) for v in actual],'bbox_error_m':[round(v,6) for v in delta],'matches_source_bbox_within_0_01m':max(map(abs,delta))<.01}
 if max(map(abs,delta))>=.01:errors.append(f'FID {fid} slab bounds disagree with source')
images=[{'name':im.name,'path':im.filepath} for im in bpy.data.images if im.source=='FILE']
external=[im for im in images if im['path'] and not im['path'].startswith('//')]
if external:errors.append('External image path present')
materials={m.name for o in objects if o.type in {'MESH','FONT'} for m in o.data.materials if m}
if not materials:errors.append('No assigned materials found')
bounds=[]
for axis in range(3):
 vals=[(o.matrix_world@Vector(corner))[axis] for o in objects if o.type=='MESH' for corner in o.bound_box]
 bounds.append([round(min(vals),5),round(max(vals),5)] if vals else None)
sha=hashlib.sha256(blend.read_bytes()).hexdigest()
data={'asset':str(blend.relative_to(root)).replace('\\','/'),'sha256':sha,'fresh_open':True,'scene':scene.name,'collection':collection.name if collection else None,'objects':len(objects),'mesh_objects':len(meshes),'materials_used':sorted(materials),'external_images':images,'local_bounds_xyz_m':bounds,'footprint_components':component_checks,'checks_passed':not errors,'errors':errors}
report.write_text(json.dumps(data,indent=2))
print(json.dumps(data,indent=2))
if errors:raise RuntimeError('; '.join(errors))

import bpy, hashlib, json
from pathlib import Path

ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/knoy_hall.blend'
VALIDATION=ROOT/'audit/complete_knoy/validation_round18.json'
OUT=ROOT/'audit/complete_knoy/independent_review_round18_reopen.json'
def fingerprint(obj):
    payload={'verts':[tuple(round(v,7) for v in p.co) for p in obj.data.vertices],
             'faces':[tuple(p.vertices) for p in obj.data.polygons],
             'world':[tuple(round(v,7) for v in row) for row in obj.matrix_world]}
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.context.scene
names=['KNOY_Fenestration_Ribbon_Glass','KNOY_Fenestration_Bronze_Mullions',
       'KNOY_Facade_Brick_Spandrels_R17','KNOY_Exterior_Masonry_Walls']
objs={n:bpy.data.objects.get(n) for n in names}
assert all(objs.values())
stored=json.loads(VALIDATION.read_text(encoding='utf-8'))
current={n:fingerprint(o) for n,o in objs.items()}
assert current==stored['fingerprints'], 'Saved R18 geometry differs from its validation fingerprints.'
assert scene.get('knoy_r18_review_status')=='Evidence and uncertainty pass; no geometric changes.'
assert 'not a measured dimension' in objs['KNOY_Fenestration_Ribbon_Glass']['r18_facade_status']
assert all(len(o.data.materials) for o in objs.values())
unpacked=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]
result={'asset_reopened':True,'blender_version':bpy.app.version_string,
 'scene':scene.name,'scene_objects':len(bpy.data.objects),
 'mesh_objects':sum(o.type=='MESH' for o in bpy.data.objects),
 'r18_recorded_geometry_fingerprints_match':True,'objects_checked':names,
 'unpacked_external_images':unpacked,'geometry_change_in_r18':False,
 'method':'Reopened current R18 source, independently recomputed fingerprints for the four R18 validation objects, compared to validation_round18.json. The update script was inspected and only writes custom properties and a text datablock.'}
OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))

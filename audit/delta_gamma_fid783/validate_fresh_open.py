import bpy, json, os, hashlib, math
from mathutils import Vector

HERE=os.path.dirname(__file__)
ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301840872_582df9d.blend')
CFG=json.load(open(os.path.join(HERE,'build_config.json'),encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.data.scenes.get(CFG['scene_name'])
coll=bpy.data.collections.get(CFG['collection_name'])
obj=bpy.data.objects.get(CFG['object_name'])
assert scene and coll and obj and obj.type=='MESH'
assert list(coll.objects)==[obj], [o.name for o in coll.objects]
assert obj.data and len(obj.data.vertices)>1000 and len(obj.data.polygons)>500
assert obj.location.length < 1e-8 and all(abs(v-1)<1e-8 for v in obj.scale)
coords=[v.co for v in obj.data.vertices]
zmin=min(v.z for v in coords); zmax=max(v.z for v in coords)
materials=[m.name for m in obj.data.materials if m]
assert any('Interpretive_Red_Brick' in n for n in materials)
assert any('Estimated_Slate_Roof' in n for n in materials)
assert any('Schematic_Bedding' in n for n in materials)
sha=hashlib.sha256(open(ASSET,'rb').read()).hexdigest().upper()
report={
 'validation':'PASS fresh-opened individual library',
 'blender_version':bpy.app.version_string,
 'asset_path':'modular/buildings/massing_house_301840872_582df9d.blend',
 'asset_sha256':sha,
 'scene_name':scene.name,'collection_name':coll.name,'collection_object_count':len(coll.objects),
 'object_name':obj.name,'object_type':obj.type,
 'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),
 'bounds_xyz_m':[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)],
 'materials':materials,
 'raw_geometry_only':True,
 'limitations':'Fresh-open validates the single-object library, not appearance accuracy, GIS vertical accuracy, facade, height, roof, or current interior.'
}
out=os.path.join(HERE,'fresh_open_validation.json')
json.dump(report,open(out,'w',encoding='utf-8'),indent=2)
print('FRESH_OPEN_VALIDATION='+json.dumps(report))

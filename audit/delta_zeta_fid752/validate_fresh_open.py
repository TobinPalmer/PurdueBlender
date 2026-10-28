import bpy,json,os,hashlib
HERE=os.path.dirname(__file__);ROOT=os.path.abspath(os.path.join(HERE,'..','..'));cfg=json.load(open(os.path.join(HERE,'build_config.json'),encoding='utf-8'))
ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301841601_7ae6159.blend');bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.data.scenes.get(cfg['scene_name']);coll=bpy.data.collections.get(cfg['collection_name']);obj=bpy.data.objects.get(cfg['object_name'])
assert scene and coll and obj and obj.type=='MESH';assert list(coll.objects)==[obj];assert len(obj.data.vertices)>1500 and len(obj.data.polygons)>1000
assert obj.location.length<1e-8 and all(abs(x-1)<1e-8 for x in obj.scale)
coords=[v.co for v in obj.data.vertices];mats=[m.name for m in obj.data.materials if m]
assert any('Interpretive_Brick' in n for n in mats) and any('Estimated_Roof_Cap' in n for n in mats)
sha=hashlib.sha256(open(ASSET,'rb').read()).hexdigest().upper()
report={'validation':'PASS fresh-opened individual library','blender_version':bpy.app.version_string,'asset_path':'modular/buildings/massing_house_301841601_7ae6159.blend','asset_sha256':sha,'scene_name':scene.name,'collection_name':coll.name,'collection_object_count':len(coll.objects),'object_name':obj.name,'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),'bounds_xyz_m':[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)],'materials':mats,'saved_cameras_or_lights':sum(o.type in {'CAMERA','LIGHT'} for o in bpy.data.objects),'external_image_datablocks':len(bpy.data.images),'limitations':'Fresh-open validates the individual library and stable identity only; does not establish building height, roof profile, facade dimensions, or an as-built interior.'}
json.dump(report,open(os.path.join(HERE,'fresh_open_validation.json'),'w',encoding='utf-8'),indent=2);print('DZ_FRESH_OPEN='+json.dumps(report))

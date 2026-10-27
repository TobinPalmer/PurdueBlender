import bpy, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
BLEND=ROOT/'modular/buildings/massing_house_301836574_fff1661.blend'
OUT=ROOT/'audit/phi_mu'
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
col=bpy.data.collections.get('Asset_massing_house_301836574_fff1661')
assert col and len(col.objects)==1
obj=col.objects[0]; assert obj.name=='House_301836574' and obj.type=='MESH'
assert tuple(round(v,6) for v in obj.location)==(0.0,0.0,0.0)
assert tuple(round(v,6) for v in obj.rotation_euler)==(0.0,0.0,0.0)
assert tuple(round(v,6) for v in obj.scale)==(1.0,1.0,1.0)
raw=json.load(open(OUT/'sources/purdue_gis_fid772_raw.json',encoding='utf8'))
ring=raw['features'][0]['geometry']['rings'][0][:-1]
lat0=40.4274; lon0=-86.9137
expected=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in ring]
base={(round(v.co.x,4),round(v.co.y,4)) for v in obj.data.vertices if abs(v.co.z)<1e-5}
missing=[p for p in expected if (round(p[0],4),round(p[1],4)) not in base]
assert not missing,missing
# evaluated mesh dimensions
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(dg); me=ev.to_mesh()
coords=[ev.matrix_world@v.co for v in me.vertices]
bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
evid={'reopened':True,'asset_path':'modular/buildings/massing_house_301836574_fff1661.blend','collection':'Asset_massing_house_301836574_fff1661','collection_object_count':len(col.objects),'object':'House_301836574','object_type':obj.type,'location':list(obj.location),'rotation_euler':list(obj.rotation_euler),'scale':list(obj.scale),'mesh_vertices':len(me.vertices),'mesh_faces':len(me.polygons),'evaluated_bounds_xyz_m':bounds,'gis_ring_vertices':len(expected),'gis_ring_missing_at_base':len(missing),'gis_ring_comparison_tolerance_m':0.0001,'external_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath], 'checks':{'expected_identity':True,'expected_collection':True,'identity_transform':True,'footprint_vertices_present':True}}
ev.to_mesh_clear()
assert not evid['external_images']
(OUT/'reopen_validation.json').write_text(json.dumps(evid,indent=2)+'\n',encoding='utf8')
# Create an inspection camera looking from south-west at front and side elevations.
scene=bpy.context.scene
for o in list(scene.objects):
    if o.type in {'CAMERA','LIGHT'}: bpy.data.objects.remove(o,do_unlink=True)
center=Vector(((bounds[0][0]+bounds[0][1])/2,(bounds[1][0]+bounds[1][1])/2,6.2))
def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
camdat=bpy.data.cameras.new('Phi Mu inspection camera'); cam=bpy.data.objects.new('Phi Mu inspection camera',camdat); scene.collection.objects.link(cam)
cam.location=center+Vector((55,-68,38)); aim(cam,center); camdat.lens=56; scene.camera=cam
ld=bpy.data.lights.new('Large soft key','AREA'); lo=bpy.data.objects.new('Large soft key',ld); scene.collection.objects.link(lo); lo.location=center+Vector((5,-30,55)); ld.energy=18000; ld.shape='DISK'; ld.size=38; aim(lo,center)
ld2=bpy.data.lights.new('Fill','AREA'); lo2=bpy.data.objects.new('Fill',ld2); scene.collection.objects.link(lo2); lo2.location=center+Vector((-35,25,28)); ld2.energy=8000; ld2.size=35; aim(lo2,center)
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1100; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(OUT/'preview.png'); scene.render.film_transparent=False
scene.world.color=(.19,.19,.19)
scene.view_settings.view_transform='AgX'
bpy.ops.render.render(write_still=True)
print(json.dumps(evid))

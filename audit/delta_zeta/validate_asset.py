import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'audit/delta_zeta';BLEND=ROOT/'modular/buildings/massing_house_301841601_7ae6159.blend'
bpy.ops.wm.open_mainfile(filepath=str(BLEND));col=bpy.data.collections.get('Asset_massing_house_301841601_7ae6159');assert col and len(col.objects)==1
obj=col.objects[0];assert obj.name=='House_301841601' and obj.type=='MESH';assert tuple(round(v,6) for v in obj.location)==(0.,0.,0.);assert tuple(round(v,6) for v in obj.rotation_euler)==(0.,0.,0.);assert tuple(round(v,6) for v in obj.scale)==(1.,1.,1.)
raw=json.load(open(OUT/'sources/purdue_gis_fid752_raw.json',encoding='utf8'));ring=raw['features'][0]['geometry']['rings'][0][:-1];lat0=40.4274;lon0=-86.9137;expected=[((x-lon0)*111412.84*math.cos(math.radians(lat0)),(y-lat0)*111040.) for x,y in ring]
base=[(v.co.x,v.co.y) for v in obj.data.vertices if abs(v.co.z)<1e-5];missing=[p for p in expected if min((x-p[0])**2+(y-p[1])**2 for x,y in base)>(.0001**2)];assert not missing,missing
bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();coords=[ev.matrix_world@v.co for v in me.vertices];bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
report={'reopened':True,'asset_path':'modular/buildings/massing_house_301841601_7ae6159.blend','collection':'Asset_massing_house_301841601_7ae6159','collection_object_count':len(col.objects),'object':'House_301841601','object_type':obj.type,'location':list(obj.location),'rotation_euler':list(obj.rotation_euler),'scale':list(obj.scale),'mesh_vertices':len(me.vertices),'mesh_faces':len(me.polygons),'evaluated_bounds_xyz_m':bounds,'gis_ring_vertices':len(expected),'gis_ring_missing_at_base':len(missing),'gis_ring_comparison_tolerance_m':.0001,'external_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath],'checks':{'expected_identity':True,'expected_collection':True,'identity_transform':True,'footprint_vertices_present':True}}
ev.to_mesh_clear();assert not report['external_images'];(OUT/'reopen_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
# Match inspection camera to GIS-selected facade edge using local u/inward transform.
pts=expected;p0=pts[0];p1=pts[1];dx=p1[0]-p0[0];dy=p1[1]-p0[1];L=math.hypot(dx,dy);u=(dx/L,dy/L);n=(dy/L,-dx/L)
local=[((x-p0[0])*u[0]+(y-p0[1])*u[1],(x-p0[0])*n[0]+(y-p0[1])*n[1]) for x,y in pts]
smin,smax=min(s for s,t in local),max(s for s,t in local);tmax=max(t for s,t in local)
def world(s,t,z):return Vector((p0[0]+u[0]*s+n[0]*t,p0[1]+u[1]*s+n[1]*t,z))
scene=bpy.context.scene
for o in list(scene.objects):
 if o.type in {'CAMERA','LIGHT'}:bpy.data.objects.remove(o,do_unlink=True)
target=world((smin+smax)/2,tmax*.45,6.8)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
camdat=bpy.data.cameras.new('Delta Zeta inspection camera');cam=bpy.data.objects.new('Delta Zeta inspection camera',camdat);scene.collection.objects.link(cam);cam.location=world((smin+smax)/2,-54,19);aim(cam,target);camdat.lens=52;scene.camera=cam
for name,offset,energy,size in [('Key',(22,-22,42),18000,30),('Fill',(-35,23,27),8500,30)]:
 ld=bpy.data.lights.new(name,'AREA');lo=bpy.data.objects.new(name,ld);scene.collection.objects.link(lo);lo.location=target+Vector(offset);ld.energy=energy;ld.size=size;aim(lo,target)
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1200;scene.render.resolution_y=850;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'preview.png');scene.world.color=(.19,.19,.19);scene.view_settings.view_transform='AgX';bpy.ops.render.render(write_still=True);print(json.dumps(report))

import bpy,json,math,pathlib
from mathutils import Vector
ROOT=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');A=ROOT/'audit/batch3_elliott'
meta=json.loads((A/'building_shapes_layer_metadata_raw.json').read_text());raw=json.loads((A/'building_shapes_fid_617_raw.json').read_text())['feature'];near=json.loads((A/'building_shapes_neighborhood_raw.json').read_text());poly=json.loads((A/'polygon.json').read_text());manifest=json.loads((ROOT/'modular/manifest.json').read_text());rec=next(x for x in manifest['assets'] if x['id']=='elliott_hall_of_music');ox,oy=rec['placement_origin_xy_m']
lat=math.radians(40.4274);lon=math.radians(-86.9137);R=6378137.;x0=R*lon;y0=R*math.log(math.tan(math.pi/4+lat/2));k=math.cos(lat)
def xy(pt):return ((pt[0]-x0)*k,(pt[1]-y0)*k)
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
neutral=material('Neighbor GIS Footprints',(.26,.31,.34));source_mat=material('Feature 617 Source',(.84,.45,.16));model_line=material('Asset Footprint',(.18,.85,.50));line_red=material('GIS Boundary',(.98,.36,.08));white=material('Map Labels',(.92,.94,.96));muted=material('Secondary Labels',(.63,.69,.73))
def mesh_poly(name,coords,z,ma):
 vs=[(x,y,z) for x,y in coords];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[tuple(range(len(vs)))]);me.materials.append(ma);me.update();o=bpy.data.objects.new(name,me);scene.collection.objects.link(o);return o
def polyline(name,coords,z,ma,width=.18):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=width;cu.bevel_resolution=2
 sp=cu.splines.new('POLY');sp.points.add(len(coords)-1)
 for pt,(x,y) in zip(sp.points,coords):pt.co=(x,y,z,1)
 sp.use_cyclic_u=True;ob=bpy.data.objects.new(name,cu);scene.collection.objects.link(ob);cu.materials.append(ma);return ob
def txt(name,body,loc,size,ma):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.extrude=.01;ob=bpy.data.objects.new(name,cu);scene.collection.objects.link(ob);ob.location=loc;cu.materials.append(ma);return ob
# Neighboring building footprints from the same FeatureServer query provide local context.
labels={'HOVD','WALC','WTHR','AR','BELL','MATH','CL50','FRNY'}
for f in near['features']:
 rings=f['geometry'].get('rings',[])
 if not rings:continue
 coords=[xy(p) for p in rings[0]]
 mesh_poly('GIS_'+str(f['attributes'].get('FID'))+'_footprint',coords,-.8,neutral)
 abbr=(f['attributes'].get('BLDG_ABBR') or '').strip()
 if abbr in labels:
  cx=sum(x for x,y in coords)/len(coords);cy=sum(y for x,y in coords)/len(coords)
  txt('label_'+abbr,abbr,(cx,cy,1.1),3.5,white)
# Highlight FID 617 footprint and overlay the placed asset outline.
src=[xy(pt) for pt in raw['geometry']['rings'][0][:-1]]
mesh_poly('FID_617_GIS_source_fill',src,.05,source_mat);polyline('FID_617_source_boundary',src,.35,line_red,.22)
asset=[(x+ox,y+oy) for x,y in poly];polyline('Asset_elliott_plus_manifest_outline',asset,.65,model_line,.15)
cx=sum(x for x,y in src)/len(src);cy=sum(y for x,y in src)/len(src)
txt('Elliott_label','ELLIOTT  /  FID 617',(cx-25,cy-1,1.2),4.5,white)
# Placement origin marker (the manifest/master translation, not the footprint centroid).
bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=(ox,oy,1.4));mark=bpy.context.object;mark.name='Manifest placement origin';mark.scale=(1.4,1.4,.3);mark.data.materials.append(white)
txt('Origin_label','manifest origin',(ox+3,oy+2,1.2),2.8,white)
# North arrow and map-scale bar, both in ground metres.
txt('north','N',(25,190,1),5,white);polyline('north_arrow',[(27,180),(27,198)],1,white,.45);polyline('north_arrow_head',[(24,194),(27,199),(30,194)],1,white,.45)
polyline('scale_bar', [(-250,-85),(-200,-85)],1,white,.45);polyline('scale_tick_left',[(-250,-88),(-250,-82)],1,white,.35);polyline('scale_tick_right',[(-200,-88),(-200,-82)],1,white,.35);txt('scale_label','50 m',(-238,-96,1),3,white)
# Legend.
txt('legend_title','PURDUE BUILDINGSHAPES — NORTH-UP PLACEMENT OVERLAY',(-315,204,1),5.0,white)
polyline('legend_gis', [(-315,193),(-305,193)],1,line_red,.5);txt('legend_gis_text','FID 617 source outline',(-302,191,1),3.2,white)
polyline('legend_asset', [(-315,185),(-305,185)],1,model_line,.5);txt('legend_asset_text','Asset footprint + manifest translation',(-302,183,1),3.2,white)
# World/camera setup. Map coordinates are local campus ground metres, north-up.
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1800;scene.render.resolution_y=1350;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=False;scene.display.shading.background_type='WORLD';scene.display.shading.background_color=(.055,.07,.085)
camdata=bpy.data.cameras.new('North-up evidence camera');camdata.type='ORTHO';camdata.ortho_scale=460;cam=bpy.data.objects.new('North-up evidence camera',camdata);scene.collection.objects.link(cam);cam.location=(-135,55,500);cam.rotation_euler=(0,0,0);scene.camera=cam
scene.render.filepath=str(A/'footprint_neighborhood_overlay_round9.png');bpy.ops.render.render(write_still=True)
print(json.dumps({'neighbor_feature_count':len(near['features']),'highlight_fid':raw['attributes']['FID'],'placement_origin':[ox,oy],'output':str(A/'footprint_neighborhood_overlay_round9.png')}))

import bpy,json,math,os
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); audit=P/'audit/batch3_hovde'; source=P/'modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(source)); scene=bpy.context.scene; col=bpy.data.collections['Asset_hovde_hall'];root=bpy.data.objects['HOVD_Root']
snap=json.loads((audit/'gis_feature_618_snapshot_20261024.json').read_text())
R=6378137.0;lat0=40.4274;lon0=-86.9137

def xymerc_to_local(x,y):
 lon=(x/R)*180/math.pi;lat=(2*math.atan(math.exp(y/R))-math.pi/2)*180/math.pi
 return ((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0)
# The HOVD_Root parent inverse removes the master collection-instance marker
# from the source library. GIS campus coordinates therefore need that same
# inverse-marker translation to enter this saved source-local frame.
frame_shift=(root.matrix_parent_inverse[0][3],root.matrix_parent_inverse[1][3])
gis=[tuple(a+b for a,b in zip(xymerc_to_local(x,y),frame_shift)) for x,y in snap['feature']['geometry']['rings'][0]]
def convex_hull(points):
 pts=sorted(set((float(x),float(y)) for x,y in points))
 if len(pts)<3:return pts
 def cr(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[]
 for q in pts:
  while len(lo)>=2 and cr(lo[-2],lo[-1],q)<=0:lo.pop()
  lo.append(q)
 up=[]
 for q in reversed(pts):
  while len(up)>=2 and cr(up[-2],up[-1],q)<=0:up.pop()
  up.append(q)
 return lo[:-1]+up[:-1]
wallnames=['HOVD_Wall_South_West','HOVD_Wall_South_East','HOVD_Wall_South_Center_Upper','HOVD_Wall_North','HOVD_Wall_East','HOVD_Wall_West']
# Compare filled footprints, not the thin wall-solid union (which would
# artificially score poorly against a filled GIS polygon). The saved source
# roof slab is the continuous structural footprint proxy; keep the wall bounds
# as a separate measurement so the scope stays explicit.
roof_slab=bpy.data.objects['HOVD_Roof_Slab']
model_hull=convex_hull([(q.x,q.y) for q in (roof_slab.matrix_world@v.co for v in roof_slab.data.vertices)])
wall=[]
for name in wallnames:
 o=bpy.data.objects[name]
 pts=[(q.x,q.y) for q in (o.matrix_world@Vector(c) for c in o.bound_box)]
 wall.append(convex_hull(pts))

def signed_area(p):return .5*sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))
def pip(x,y,poly):
 inside=False;j=len(poly)-1
 for i,(xi,yi) in enumerate(poly):
  xj,yj=poly[j]
  if ((yi>y)!=(yj>y)) and (x<(xj-xi)*(y-yi)/(yj-yi+1e-30)+xi):inside=not inside
  j=i
 return inside

gis_bounds=[[min(q[i] for q in gis),max(q[i] for q in gis)] for i in range(2)]
model_bounds=[[min(q[i] for q in model_hull),max(q[i] for q in model_hull)] for i in range(2)]
step=.25;xmin=min(gis_bounds[0][0],model_bounds[0][0]);xmax=max(gis_bounds[0][1],model_bounds[0][1]);ymin=min(gis_bounds[1][0],model_bounds[1][0]);ymax=max(gis_bounds[1][1],model_bounds[1][1])
ng=nm=ni=0;ny=int(math.ceil((ymax-ymin)/step));nx=int(math.ceil((xmax-xmin)/step))
for iy in range(ny):
 y=ymin+(iy+.5)*step
 for ix in range(nx):
  x=xmin+(ix+.5)*step;g=pip(x,y,gis);m=pip(x,y,model_hull)
  ng+=g;nm+=m;ni+=(g and m)
union=ng+nm-ni
# Estimate the GIS major-axis orientation from the longest straight ring edges;
# express both the source's local +Y axis and GIS axis counter-clockwise from north.
major=[]
for a,b in zip(gis,gis[1:]+gis[:1]):
 dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
 if length>8.0: major.append((length,math.degrees(math.atan2(dy,dx))%180.0))
gis_long_east=sum(length*deg for length,deg in major)/sum(length for length,deg in major)
gis_long_north_ccw=(gis_long_east-90.0)%180.0
angle=math.degrees(root.rotation_euler.z)
source_long_north_ccw=angle%180.0
axis_delta=min(abs(source_long_north_ccw-gis_long_north_ccw),180-abs(source_long_north_ccw-gis_long_north_ccw))
metrics={'gis_feature':618,'crs_input':'EPSG:3857 (ArcGIS wkid102100/latestWkid3857)','projection':'Inverse Web Mercator to lon/lat; project local campus XY approximation (X=(lon+86.9137)*111412.84*cos(40.4274deg), Y=(lat-40.4274)*111040); then add HOVD_Root.matrix_parent_inverse XY translation to enter source-library frame. Approximate meters.','source_frame_shift_xy_m':list(frame_shift),'gis_ring_vertices':len(gis),'gis_bounds_xy_ranges_local_m':gis_bounds,'gis_polygon_area_m2_local_projected':abs(signed_area(gis)),'source_structural_members':wallnames,'model_footprint_proxy':'HOVD_Roof_Slab convex hull projected to XY; roof-slab perimeter is a source-model structural proxy, not an as-built survey.','model_xy_ranges_local_m':model_bounds,'structural_wall_union_bounds_xy_ranges_local_m':[[min(q[i] for hull in wall for q in hull),max(q[i] for hull in wall for q in hull)] for i in range(2)],'source_long_axis_orientation_deg_from_north_ccw':round(source_long_north_ccw,3),'gis_major_edge_orientation_deg_from_north_ccw':round(gis_long_north_ccw,3),'axis_delta_deg':round(axis_delta,3),'major_gis_edge_count_over_8m':len(major),'raster_step_m':step,'gis_area_raster_m2':round(ng*step*step,2),'source_roof_slab_proxy_area_raster_m2':round(nm*step*step,2),'overlap_area_raster_m2':round(ni*step*step,2),'intersection_over_union':round(ni/union,4),'gis_coverage':round(ni/ng,4),'source_proxy_coverage':round(ni/nm,4),'root_transform_preserved':True,'interpretation':'Overlay compares filled official GIS FID 618 footprint with the current source HOVD_Roof_Slab XY convex-hull proxy. The six structural wall meshes are separately bounded; portico, stairs, landscaping, height and master placement are not part of this source-library overlay. The project conversion is approximate, not a surveyed CRS; the parent agent separately checked the master placement marker against the manifest.'}
(audit/'footprint_overlay_round13.json').write_text(json.dumps(metrics,indent=2)+'\n')
# Render an explanatory plan overlay from temporary emissive objects; do not save any source-model changes.
for o in list(scene.objects):o.hide_render=True
# use standalone temporary collection for diagram geometry
T=bpy.data.collections.new('TEMP_R13_footprint_overlay');scene.collection.children.link(T)
def emission(name,color,alpha=1):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,alpha);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*color,alpha);nt.links.new(e.outputs[0],out.inputs['Surface']);return m
mgis=emission('R13 GIS outline',(.96,.035,.015));mmod=emission('R13 source footprint proxy',(.08,.38,.72));mbg=emission('R13 background',(.96,.96,.93));mtext=emission('R13 diagram text',(.07,.08,.09))
def objmesh(name,vertices,faces,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);me.update();o=bpy.data.objects.new(name,me);T.objects.link(o);o.data.materials.append(mat);return o
# GIS transparent fill is deliberately omitted; red line shows surveyed wall/footprint outline.
def polyline(name,points,z,mat,width=.07):
 cv=bpy.data.curves.new(name,'CURVE');cv.dimensions='3D';cv.resolution_u=1;cv.bevel_depth=width/2;cv.bevel_resolution=2;s=cv.splines.new('POLY');s.points.add(len(points)-1)
 for pt,q in zip(s.points,points):pt.co=(q[0],q[1],z,1)
 s.use_cyclic_u=True;o=bpy.data.objects.new(name,cv);T.objects.link(o);o.data.materials.append(mat);return o
polyline('Official GIS FID618 outline',gis,.3,mgis,.28)
verts=[];faces=[]
verts.extend([(x,y,.05) for x,y in model_hull]);faces.append(tuple(range(len(verts))))
objmesh('Current source roof slab footprint proxy',verts,faces,mmod)
polyline('Source roof slab proxy perimeter',model_hull,.36,mmod,.12)
for i,hull in enumerate(wall):polyline('Structural wall mesh bounds '+str(i+1),hull,.25,mmod,.035)
# Camera/background and a compact legend.
cx=(xmin+xmax)/2;cy=(ymin+ymax)/2;span=max(xmax-xmin,ymax-ymin)+16
objmesh('Diagram background',[(xmin-8,ymin-8,-.15),(xmax+8,ymin-8,-.15),(xmax+8,ymax+8,-.15),(xmin-8,ymax+8,-.15)],[(0,1,2,3)],mbg)
for textval,loc in [(f'FID 618 GIS outline (red) / source roof-slab footprint proxy (blue)',(xmin, ymax+4,.4)),(f'IoU {metrics["intersection_over_union"]:.3f} | GIS coverage {metrics["gis_coverage"]:.3f} | source proxy coverage {metrics["source_proxy_coverage"]:.3f}',(xmin,ymin-5,.4))]:
 cu=bpy.data.curves.new('R13 overlay label','FONT');cu.body=textval;cu.size=1.25;cu.extrude=0;ob=bpy.data.objects.new('R13 overlay label',cu);T.objects.link(ob);ob.location=loc;ob.data.materials.append(mtext)
camdat=bpy.data.cameras.new('R13 footprint top camera');cam=bpy.data.objects.new('R13 footprint top camera',camdat);T.objects.link(cam);cam.location=(cx,cy,180);camdat.type='ORTHO';camdat.ortho_scale=span;cam.rotation_euler=(0,0,0);scene.camera=cam
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=16;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(audit/'footprint_overlay_round13.png');scene.world.color=(1,1,1)
bpy.ops.render.render(write_still=True)
print(json.dumps(metrics,indent=2))

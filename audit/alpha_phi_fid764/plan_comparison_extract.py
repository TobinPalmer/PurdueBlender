import bpy, json, math, os
HERE=os.path.dirname(__file__)
ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301841331_735e92f.blend')
with open(os.path.join(HERE,'build_config.json'),encoding='utf8') as f: cfg=json.load(f)
with open(os.path.join(HERE,cfg['source_feature_file']),encoding='utf8') as f: raw=json.load(f)
bpy.ops.wm.open_mainfile(filepath=ASSET)
obj=bpy.data.objects[cfg['object_name']]; mesh=obj.data
R=6378137.0; lat0=cfg['coordinate_origin']['latitude']; lon0=cfg['coordinate_origin']['longitude']
source=[]
for mx,my in raw['features'][0]['geometry']['rings'][0]:
    lon=mx/R*180/math.pi; lat=(2*math.atan(math.exp(my/R))-math.pi/2)*180/math.pi
    source.append(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0))
if len(source)>1 and source[0]==source[-1]: source.pop()
wall_segments=[]
for p in mesh.polygons:
    ma=mesh.materials[p.material_index] if p.material_index<len(mesh.materials) else None
    if not ma or not ma.name.startswith('ALPHAPHI_Limestone'): continue
    co=[mesh.vertices[i].co for i in p.vertices]
    if not (abs(min(v.z for v in co))<1e-5 and abs(max(v.z for v in co)-0.58)<1e-4): continue
    low=[(v.x,v.y) for v in co if abs(v.z)<1e-5]
    if len(low)==2: wall_segments.append(low)
assert len(wall_segments)==len(source), (len(wall_segments),len(source))
def dist(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
errors=[]
for a,b in zip(source,source[1:]+source[:1]):
    match=min(wall_segments,key=lambda s:min(dist(a,s[0])+dist(b,s[1]),dist(a,s[1])+dist(b,s[0])))
    errors.extend((min(dist(a,match[0]),dist(a,match[1])),min(dist(b,match[0]),dist(b,match[1]))))
area2=sum(source[i][0]*source[(i+1)%len(source)][1]-source[(i+1)%len(source)][0]*source[i][1] for i in range(len(source)))
area=area2/2
cx=sum((source[i][0]+source[(i+1)%len(source)][0])*(source[i][0]*source[(i+1)%len(source)][1]-source[(i+1)%len(source)][0]*source[i][1]) for i in range(len(source)))/(6*area)
cy=sum((source[i][1]+source[(i+1)%len(source)][1])*(source[i][0]*source[(i+1)%len(source)][1]-source[(i+1)%len(source)][0]*source[i][1]) for i in range(len(source)))/(6*area)
xs=[p[0] for p in source]; ys=[p[1] for p in source]
mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
cov_xx=sum((x-mx)**2 for x,y in source); cov_xy=sum((x-mx)*(y-my) for x,y in source); cov_yy=sum((y-my)**2 for x,y in source)
pca_axis=math.degrees(0.5*math.atan2(2*cov_xy,cov_xx-cov_yy))%180
roof_axis=math.degrees(math.atan2(cfg['principal_axis_xy'][1],cfg['principal_axis_xy'][0]))%180
roof_axis_delta=abs((pca_axis-roof_axis+90)%180-90)
report={
 'asset_id':cfg['asset_id'],'feature_id':raw['features'][0]['attributes']['FID'],
 'comparison':'Raw FID 764 ring after documented transform vs. saved mesh base wall-plinth segments extracted at z=0.0 to 0.58 m.',
 'source_ring_xy_m':source,'model_wall_segments_xy_m':wall_segments,
 'bounds_xy_m':[[min(xs),max(xs)],[min(ys),max(ys)]],
 'axis_aligned_dimensions_m':[max(xs)-min(xs),max(ys)-min(ys)],
 'transformed_polygon_area_m2':abs(area),'transformed_polygon_centroid_xy_m':[cx,cy],
 'source_ring_pca_major_axis_degrees_from_east':pca_axis,
 'estimated_roof_ridge_axis_degrees_from_east':roof_axis,
 'estimated_roof_vs_footprint_pca_axis_difference_degrees':roof_axis_delta,
 'source_vs_model_max_boundary_vertex_error_m':max(errors) if errors else None,
 'source_vs_model_rms_boundary_vertex_error_m':math.sqrt(sum(e*e for e in errors)/len(errors)) if errors else None,
 'translation_correction_m':[0.0,0.0],
 'rotation_correction_degrees':0.0,
 'orientation_note':'The wall base is generated from the same transformed ring vertices in the same order. The 0 m translation and 0 degree wall-footprint rotation are by-construction checks, not independent ground-control validation. The estimated roof ridge axis differs from the footprint ring PCA axis; no roof evidence resolves that interpretation.',
 'evidence_limits':'No georeferenced orthophoto or survey/CAD plan was available in the retained packet. The overlay verifies faithful mesh construction from the retained ring, not whether the ring is a current wall footprint.'
}
with open(os.path.join(HERE,'plan_comparison.json'),'w',encoding='utf8') as f: json.dump(report,f,indent=2)
print('PLAN_COMPARISON='+json.dumps({k:v for k,v in report.items() if k not in {'source_ring_xy_m','model_wall_segments_xy_m'}}))

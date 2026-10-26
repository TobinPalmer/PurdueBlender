"""Compare the full FID 213 GIS ring with the existing University Hall wall shell.

The project coordinate conversion is the approximate local-meter formula in
modular/AGENTS.md. It is not a certified projected CRS or a building survey.
"""
import json, math
from pathlib import Path
base=Path(__file__).resolve().parent
feature=json.loads((base/'gis_fid213_20261025.geojson').read_text())['features'][0]
ring_ll=feature['geometry']['coordinates'][0]
lat0=40.4274;lon0=-86.9137
xscale=111412.84*math.cos(math.radians(lat0));yscale=111040.0
gis=[((lon-lon0)*xscale,(lat-lat0)*yscale) for lon,lat,*_ in ring_ll]
if gis[0]==gis[-1]:gis=gis[:-1]

# Wall-shell extrema reconstructed from the actual exterior wall object faces.
# Campus placement marker is [-119.09500122070312, -236.52999877929688].
# East/west wall centerlines and north/south wall centerlines in the source
# asset are specified by build_university_hall_photorealistic.py.
model_campus=[(-137.57000732421875,-258.1499938964844),
              (-115.66000366210938,-258.1499938964844),
              (-115.66000366210938,-214.91000366210938),
              (-137.57000732421875,-214.91000366210938)]
model=model_campus[:]

def area(poly):
    return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
def signed_area(poly):
    return sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2
def clip(poly, xmin,xmax,ymin,ymax):
    out=poly
    for axis,bound,keep_ge in ((0,xmin,True),(0,xmax,False),(1,ymin,True),(1,ymax,False)):
        inp=out;out=[]
        if not inp:break
        def inside(p): return p[axis]>=bound-1e-10 if keep_ge else p[axis]<=bound+1e-10
        def cross(a,b):
            d=b[axis]-a[axis]
            t=0 if abs(d)<1e-12 else (bound-a[axis])/d
            return (a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]))
        prev=inp[-1];pin=inside(prev)
        for cur in inp:
            cin=inside(cur)
            if cin:
                if not pin:out.append(cross(prev,cur))
                out.append(cur)
            elif pin:out.append(cross(prev,cur))
            prev,pin=cur,cin
    return out
def point_seg(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    if dx*dx+dy*dy<1e-20:return math.hypot(p[0]-a[0],p[1]-a[1])
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def boundary_distance_samples(src,dst,step=0.25):
    samples=[]
    for i,a in enumerate(src):
        b=src[(i+1)%len(src)];length=math.dist(a,b);n=max(1,math.ceil(length/step))
        for j in range(n):
            t=j/n;p=(a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]))
            samples.append(min(point_seg(p,dst[k],dst[(k+1)%len(dst)]) for k in range(len(dst))))
    return samples

minx,maxx=min(p[0] for p in model),max(p[0] for p in model)
miny,maxy=min(p[1] for p in model),max(p[1] for p in model)
intersection=clip(gis,minx,maxx,miny,maxy)
ag,am,ai=area(gis),area(model),area(intersection)
dg=boundary_distance_samples(gis,model);dm=boundary_distance_samples(model,gis);d=dg+dm
sorted_d=sorted(d)
q95=sorted_d[min(len(sorted_d)-1,math.ceil(.95*len(sorted_d))-1)]
gbox=[min(x for x,y in gis),min(y for x,y in gis),max(x for x,y in gis),max(y for x,y in gis)]
m_box=[minx,miny,maxx,maxy]
report={
 'source_url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D213&outFields=*&returnGeometry=true&outSR=4326&f=geojson',
 'provider':'Purdue University ArcGIS BuildingShapesZip4', 'feature_id':213,'building_code':'UNIV','building_name':'University Hall',
 'retrieved':'2026-10-25','source_crs':'EPSG:4326','project_frame':'Approximate local meters: X=(longitude+86.9137)*111412.84*cos(radians(40.4274)); Y=(latitude-40.4274)*111040.0; not a certified CRS.',
 'model_source':'Existing structural wall rectangle reconstructed from the four wall centerlines/thickness in build_university_hall_photorealistic.py and checked against current shell bounds in R2 independent_grade_r2.json.',
 'model_placement_origin_xy_m':[-119.09500122070312,-236.52999877929688],
 'gis_ring_vertex_count_excluding_closure':len(gis),'model_ring_vertices_m':model,'gis_ring_m':gis,'intersection_ring_m':intersection,
 'model_bounds_m':m_box,'gis_bounds_m':gbox,
 'model_area_m2':am,'gis_area_m2':ag,'intersection_area_m2':ai,'intersection_over_union':ai/(am+ag-ai),
 'symmetric_difference_area_m2':am+ag-2*ai,
 'boundary_residual_sampling_step_m':0.25,
 'model_to_gis_boundary_mean_sampled_m':sum(dm)/len(dm),'gis_to_model_boundary_mean_sampled_m':sum(dg)/len(dg),
 'symmetric_mean_boundary_residual_m':sum(d)/len(d),
 'symmetric_95th_percentile_boundary_residual_m':q95,'symmetric_sampled_hausdorff_m':max(d),
 'limitations':['Model shell perimeter was reconstructed as its existing axis-aligned exterior wall ring; east entry wall is locally interrupted at ground but above-door shell is continuous.','GIS polygon is a Purdue campus-map polygon and not a certified as-built survey.','Approximate local projection can contribute small meter-scale errors; no CRS conversion or geodetic datum adjustment beyond project formula was applied.','This does not verify height, roof, facade, or interior.']}
(base/'fid213_polygon_comparison_r3.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

# Write a small review SVG: source GIS ring (red), model shell (blue), overlap fill.
allpts=gis+model
loX,hiX=min(p[0] for p in allpts),max(p[0] for p in allpts);loY,hiY=min(p[1] for p in allpts),max(p[1] for p in allpts)
W,H=900,850;pad=50;scale=min((W-2*pad)/(hiX-loX),(H-2*pad)/(hiY-loY))
def xy(p):return (pad+(p[0]-loX)*scale,H-pad-(p[1]-loY)*scale)
def pointlist(poly):return ' '.join(f'{xy(p)[0]:.1f},{xy(p)[1]:.1f}' for p in poly)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<rect width="100%" height="100%" fill="#f7f6f1"/>']
svg.append(f'<polygon points="{pointlist(gis)}" fill="#dc7666" fill-opacity=".35" stroke="#af302a" stroke-width="2"/>')
svg.append(f'<polygon points="{pointlist(model)}" fill="#5b89c6" fill-opacity=".40" stroke="#174f9d" stroke-width="2"/>')
for i,p in enumerate(gis):
    x,y=xy(p);svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#af302a"/><text x="{x+5:.1f}" y="{y-5:.1f}" font-size="12" fill="#84221c">{i}</text>')
svg.append('<text x="35" y="30" font-family="sans-serif" font-size="18" fill="#222">University Hall shell vs Purdue GIS FID 213 (project approximate meters)</text>')
svg.append(f'<text x="35" y="{H-18}" font-family="sans-serif" font-size="13" fill="#333">Red: GIS polygon · Blue: reconstructed structural wall ring · IoU {ai/(am+ag-ai):.4f} · symmetric sampled boundary Hausdorff {max(d):.3f} m</text>')
svg.append('</svg>')
(base/'fid213_polygon_overlay_r3.svg').write_text('\n'.join(svg),encoding='utf-8')
print(json.dumps({k:report[k] for k in ('gis_ring_vertex_count_excluding_closure','model_bounds_m','gis_bounds_m','model_area_m2','gis_area_m2','intersection_area_m2','intersection_over_union','symmetric_difference_area_m2','symmetric_mean_boundary_residual_m','symmetric_95th_percentile_boundary_residual_m','symmetric_sampled_hausdorff_m')},indent=2))

import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

A=Path(__file__).parent
feat=json.loads((A/'purdue_gis_fid772_2026-10-28_4326.json').read_text())['features'][0]
ring_ll=feat['geometry']['rings'][0][:-1]
def project(lon,lat):
    return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.)
gis=[project(lon,lat) for lon,lat in ring_ll]
old_data=json.loads((A/'base_mesh.json').read_text())['verts'][:15]
old=[(p[0],p[1]) for p in old_data]
def area(poly):
    return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
def perimeter(poly):
    return sum(math.dist(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly)))
def pd(p,a,b):
    dx=b[0]-a[0]; dy=b[1]-a[1]
    if dx==dy==0: return math.dist(p,a)
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
    return math.dist(p,(a[0]+t*dx,a[1]+t*dy))
def vertex_to_line(poly,other):
    return max(min(pd(p,other[i],other[(i+1)%len(other)]) for i in range(len(other))) for p in poly)
def haus(a,b): return max(vertex_to_line(a,b),vertex_to_line(b,a))
def bbox(poly):
    return [min(p[0] for p in poly),min(p[1] for p in poly),max(p[0] for p in poly),max(p[1] for p in poly)]
def size(poly):
    b=bbox(poly); return [b[2]-b[0],b[3]-b[1]]
prj=json.loads((A/'purdue_gis_fid772_2026-10-28_3857.json').read_text())['features'][0]
native=prj['geometry']['rings'][0]
def raw_area(poly):
    return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
def raw_per(poly): return sum(math.dist(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly)))
metrics={
 'feature_id':772,'geometry_vertex_count_excluding_close':len(gis),
 'project_conversion':'README local approximation from EPSG:4326, origin lon -86.9137 / lat 40.4274; X=delta lon*111412.84*cos(40.4274deg), Y=delta lat*111040.',
 'native_epsg3857':{'area_m2':raw_area(native),'perimeter_m':raw_per(native),'Shape__Area':prj['attributes']['Shape__Area'],'Shape__Length':prj['attributes']['Shape__Length']},
 'project_local_geometry':{'area_m2':area(gis),'perimeter_m':perimeter(gis),'width_m':size(gis)[0],'depth_m':size(gis)[1],'bbox_xy_m':bbox(gis)},
 'starter_geometry':{'bottom_ring_vertex_count':len(old),'area_m2':area(old),'perimeter_m':perimeter(old),'width_m':size(old)[0],'depth_m':size(old)[1],'bbox_xy_m':bbox(old),'symmetric_boundary_hausdorff_m':haus(gis,old)},
 'revised_geometry':{'outline':'source FID 772 ring converted to project local coordinates; 18 distinct points'},
 'native_to_local_area_ratio':raw_area(native)/area(gis),'native_to_local_perimeter_ratio':raw_per(native)/perimeter(gis),
 'height':{'revised_ridge_m_estimate':9.4,'source_NUM_LEVELS':feat['attributes']['NUM_LEVELS'],'source_Extrution':feat['attributes']['Extrution'],'unit_for_Extrution':'undocumented; not treated as verified meters or feet'},
 'qualifications':['Geometry derives from source polygon only, using the project approximate local transform.','This does not independently verify campus placement relative to roads or adjacent buildings.','The new two-level facade reading conflicts with GIS NUM_LEVELS=1 and is interpretative; the photo clearly documents only the lower level.','Extrusion/height, facade orientation, detailed roof breaks, unseen facade openings and interior are not surveyed or verified.']}
fresh=json.loads((A/'fresh_open_validation.json').read_text())
metrics['revised_geometry'].update({'max_vertex_error_to_source_m':fresh['max_source_to_saved_mesh_outline_vertex_error_m'],
 'area_difference_from_converted_source_m2':fresh['saved_outline_area_difference_m2'],
 'perimeter_difference_from_converted_source_m':fresh['saved_outline_perimeter_difference_m']})
(A/'geometry_reconciliation.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')

# Overlay: green source fill, blue exact revised boundary, dashed red starter boundary.
w,h,pad=1500,1250,120
b=bbox(gis); scale=min((w-2*pad)/(b[2]-b[0]),(h-2*pad)/(b[3]-b[1]))
def xy(p): return (int(pad+(p[0]-b[0])*scale),int(h-pad-(p[1]-b[1])*scale))
im=Image.new('RGB',(w,h),(250,250,247)); d=ImageDraw.Draw(im)
srcpx=[xy(p) for p in gis]; oldpx=[xy(p) for p in old]
d.polygon(srcpx,fill=(218,235,221),outline=(49,105,72),width=5)
d.line(srcpx+[srcpx[0]],fill=(27,75,134),width=8)
for i,p1 in enumerate(oldpx):
    p2=oldpx[(i+1)%len(oldpx)]
    for j in range(0,20,2):
        a=j/20;c=(j+1)/20
        d.line((p1[0]+(p2[0]-p1[0])*a,p1[1]+(p2[1]-p1[1])*a,p1[0]+(p2[0]-p1[0])*c,p1[1]+(p2[1]-p1[1])*c),fill=(198,74,62),width=5)
try:
    font=ImageFont.truetype('arial.ttf',30); small=ImageFont.truetype('arial.ttf',23)
except OSError:
    font=small=ImageFont.load_default()
d.text((55,35),'Phi Mu FID 772 — source footprint / model comparison',font=font,fill=(30,35,40))
d.text((55,82),'Blue: revised model; green: GIS FID 772; red dashed: starter mesh boundary',font=small,fill=(50,55,60))
d.text((55,h-70),f"18 source vertices | local area {area(gis):.1f} m² | starter boundary error {haus(gis,old):.2f} m",font=small,fill=(50,55,60))
im.save(A/'footprint_overlay.png')
print(json.dumps(metrics,indent=2))

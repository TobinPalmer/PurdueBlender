import bpy, json, math
from pathlib import Path
from mathutils import Vector
out=Path(r'audit/alpha_xi_delta_fid788')
with (out/'source_fid788.json').open(encoding='utf-8-sig') as f: packet=json.load(f)
ring=packet['features'][0]['geometry']['rings'][0][:-1]
source=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring]
mesh=bpy.data.meshes.new('AXiD_Overlay_Audit_Temp')
# Fresh open is done separately by validator; here read root from current saved asset.
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/massing_house_301841248_fe939c7.blend')
root=bpy.data.objects['House_301841248']
model=[(root.matrix_world@root.data.vertices[i].co).xy[:] for i in range(24)]
def perimeter(p): return sum(math.dist(p[i],p[(i+1)%len(p)]) for i in range(len(p)))
def area(p): return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))/2)
def centroid(p):
    a2=sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))
    return [sum((p[i][0]+p[(i+1)%len(p)][0])*(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1]) for i in range(len(p)))/(3*a2),sum((p[i][1]+p[(i+1)%len(p)][1])*(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1]) for i in range(len(p)))/(3*a2)]
def dims(p): return [max(x for x,y in p)-min(x for x,y in p),max(y for x,y in p)-min(y for x,y in p)]
def nearest(a,b): return max(min(math.dist(p,q) for q in b) for p in a)
# PCA major axis from covariance of outline vertices (descriptive only; candidate copied from GIS)
def pca_angle(p):
    mx=sum(x for x,y in p)/len(p); my=sum(y for x,y in p)/len(p)
    xx=sum((x-mx)**2 for x,y in p)/len(p); yy=sum((y-my)**2 for x,y in p)/len(p); xy=sum((x-mx)*(y-my) for x,y in p)/len(p)
    return (0.5*math.degrees(math.atan2(2*xy,xx-yy)))%180
metrics={
 'building':'Alpha Xi Delta','fid':788,'asset':'modular/buildings/massing_house_301841248_fe939c7.blend',
 'method':'Purdue GIS FID 788 ring transformed to project local approximate XY; candidate lower-shell first 24 vertices compared after save/reopen.',
 'transform':'X=(longitude+86.9137)*111412.84*cos(radians(40.4274)); Y=(latitude-40.4274)*111040.0',
 'source_vertices':len(source),'candidate_vertices':len(model),
 'source_area_m2':area(source),'candidate_area_m2':area(model),'source_perimeter_m':perimeter(source),'candidate_perimeter_m':perimeter(model),
 'source_dimensions_xy_m':dims(source),'candidate_dimensions_xy_m':dims(model),
 'source_centroid_xy_m':centroid(source),'candidate_centroid_xy_m':centroid(model),
 'source_vertex_pca_axis_deg_from_east':pca_angle(source),'candidate_vertex_pca_axis_deg_from_east':pca_angle(model),
 'source_to_candidate_hausdorff_vertices_m':max(nearest(source,model),nearest(model,source)),
 'comparison_caveat':'Exact boundary coincidence is by construction because candidate vertices were directly transformed from this same GIS ring; this is not independent validation. Projection is local approximate, not surveyed; outline describes GIS footprint and is not proof of all structural wall positions.'}
(out/'footprint_comparison.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
# SVG plan overlay. Identical outlines show both data series with a thick GIS blue stroke and coral model centerline.
W,H=1200,850; margin=110
xs=[x for x,y in source+model]; ys=[y for x,y in source+model]
scale=min((W-2*margin)/(max(xs)-min(xs)),(H-2*margin-70)/(max(ys)-min(ys)))
def xy(p): return (W/2+(p[0]-(min(xs)+max(xs))/2)*scale,H/2+20- (p[1]-(min(ys)+max(ys))/2)*scale)
def path(points):
    coords=[xy(p) for p in points]
    return 'M '+' L '.join(f'{x:.2f},{y:.2f}' for x,y in coords)+' Z'
coords=[xy(p) for p in source]
northx=W-90; northy=H-110
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="100%" height="100%" fill="#f6f5f1"/>
<text x="55" y="55" font-family="Arial" font-size="30" font-weight="bold" fill="#202b39">Alpha Xi Delta — GIS / model footprint overlay</text>
<text x="55" y="88" font-family="Arial" font-size="17" fill="#4d5968">FID 788 · exact coincident outline by construction · local approximate XY, not surveyed</text>
<path d="{path(source)}" fill="#dbeafe" fill-opacity="0.35" stroke="#1673b8" stroke-width="9" stroke-dasharray="18 10" stroke-linejoin="round"/>
<path d="{path(model)}" fill="none" stroke="#e65d4f" stroke-width="3.5" stroke-linejoin="round"/>
<rect x="55" y="{H-72}" width="23" height="11" fill="none" stroke="#1673b8" stroke-width="5" stroke-dasharray="8 5"/><text x="90" y="{H-61}" font-family="Arial" font-size="16" fill="#202b39">GIS FID 788 ring</text>
<path d="M 305,{H-67} h 32" stroke="#e65d4f" stroke-width="4"/><text x="350" y="{H-61}" font-family="Arial" font-size="16" fill="#202b39">Saved House_301841248 lower shell</text>
<text x="55" y="{H-30}" font-family="Arial" font-size="14" fill="#4d5968">Area {metrics['source_area_m2']:.2f} m² · perimeter {metrics['source_perimeter_m']:.2f} m · boundary distance {metrics['source_to_candidate_hausdorff_vertices_m']:.5f} m by construction</text>
<path d="M {northx} {northy+35} L {northx} {northy-28} M {northx} {northy-28} L {northx-10} {northy-8} M {northx} {northy-28} L {northx+10} {northy-8}" stroke="#202b39" stroke-width="4" fill="none"/><text x="{northx-9}" y="{northy-43}" font-family="Arial" font-size="21" font-weight="bold" fill="#202b39">N</text>
</svg>'''
(out/'footprint_overlay.svg').write_text(svg,encoding='utf-8')
print(json.dumps(metrics,indent=2))

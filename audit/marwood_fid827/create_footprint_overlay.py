import json, math
from pathlib import Path

ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
AUD=ROOT/'audit/marwood_fid827'; SRC=AUD/'sources'
raw=json.loads((SRC/'purdue_gis_fid827_2026-10-28_4326.json').read_text(encoding='utf-8'))
attrs=raw['features'][0]['attributes']
validation=json.loads((AUD/'fresh_open_validation.json').read_text(encoding='utf-8'))
source=[tuple(p) for p in validation['source_outline_vertices_xy_m']]
model=[tuple(p) for p in validation['model_outline_nearest_vertices_xy_m']]

minx=min(x for x,y in source+model); maxx=max(x for x,y in source+model)
miny=min(y for x,y in source+model); maxy=max(y for x,y in source+model)
W,H=1200,860; left,top,plotw,ploth=100,155,780,570
scale=min(plotw/(maxx-minx),ploth/(maxy-miny))
draww=(maxx-minx)*scale; drawh=(maxy-miny)*scale
ox=left+(plotw-draww)/2; oy=top+(ploth-drawh)/2
def xy(pt):
    x,y=pt
    return (ox+(x-minx)*scale,oy+(maxy-y)*scale)
def path(points):
    xypts=[xy(p) for p in points]
    return 'M '+' L '.join(f'{x:.3f},{y:.3f}' for x,y in xypts)+' Z'

source_area=abs(sum(source[i][0]*source[(i+1)%len(source)][1]-source[(i+1)%len(source)][0]*source[i][1] for i in range(len(source)))/2)
model_area=abs(sum(model[i][0]*model[(i+1)%len(model)][1]-model[(i+1)%len(model)][0]*model[i][1] for i in range(len(model)))/2)
source_perimeter=sum(math.hypot(source[(i+1)%len(source)][0]-source[i][0],source[(i+1)%len(source)][1]-source[i][1]) for i in range(len(source)))
model_perimeter=sum(math.hypot(model[(i+1)%len(model)][0]-model[i][0],model[(i+1)%len(model)][1]-model[i][1]) for i in range(len(model)))
metrics={
 'building':'Marwood Cooperative','fid':827,'asset':'modular/buildings/massing_marwood_cooperative_fid827.blend',
 'source_vertex_count':len(source),'model_vertex_count':len(model),'max_source_model_vertex_error_m':validation['max_source_outline_vertex_error_m'],
 'source_bounds_xy_m':[[minx,miny],[maxx,maxy]],'source_dimensions_xy_m':[maxx-minx,maxy-miny],
 'source_area_project_local_m2':source_area,'model_area_project_local_m2':model_area,'source_perimeter_project_local_m':source_perimeter,'model_perimeter_project_local_m':model_perimeter,
 'gis_shape_area_field':attrs['Shape__Area'],'gis_shape_length_field':attrs['Shape__Length'],
 'comparison_method':'Transformed FID 827 ring is the wall-base perimeter by construction; model vertices were extracted from the saved root mesh after fresh-open.',
 'caveat':'Coincidence is by construction and is not independent geodetic placement, survey, or structural wall verification. Project XY uses the approximate local compatibility transform in modular/AGENTS.md.'
}
(AUD/'footprint_comparison.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')

svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="100%" height="100%" fill="#f7f8f6"/>
<text x="60" y="58" font-family="Arial,sans-serif" font-size="34" font-weight="700" fill="#172b37">MARWOOD COOPERATIVE · FID 827</text>
<text x="60" y="96" font-family="Arial,sans-serif" font-size="18" fill="#53606a">Purdue BuildingShapesZip4 source ring and saved mesh base outline</text>
<rect x="{left}" y="{top}" width="{plotw}" height="{ploth}" rx="4" fill="#fff" stroke="#d9dfdc"/>
<path d="{path(source)}" fill="#82b7d8" fill-opacity=".28" stroke="#216b9a" stroke-width="5" stroke-linejoin="round"/>
<path d="{path(model)}" fill="none" stroke="#bd553f" stroke-width="2.6" stroke-dasharray="9 5" stroke-linejoin="round"/>
<text x="{left+16}" y="{top+28}" font-family="Arial,sans-serif" font-size="17" fill="#56616a">North ↑ · approximate campus XY (m)</text>
<line x1="910" y1="190" x2="970" y2="190" stroke="#216b9a" stroke-width="5"/>
<text x="990" y="196" font-family="Arial,sans-serif" font-size="18" fill="#263642">GIS FID 827 ring</text>
<line x1="910" y1="230" x2="970" y2="230" stroke="#bd553f" stroke-width="3" stroke-dasharray="9 5"/>
<text x="990" y="236" font-family="Arial,sans-serif" font-size="18" fill="#263642">Model base outline</text>
<text x="910" y="300" font-family="Arial,sans-serif" font-size="20" font-weight="700" fill="#263642">Measurements</text>
<text x="910" y="335" font-family="Arial,sans-serif" font-size="16" fill="#40515c">Source ring: {len(source)} points</text>
<text x="910" y="365" font-family="Arial,sans-serif" font-size="16" fill="#40515c">Bounds: {maxx-minx:.2f} × {maxy-miny:.2f} m</text>
<text x="910" y="395" font-family="Arial,sans-serif" font-size="16" fill="#40515c">Local polygon area: {source_area:.2f} m²</text>
<text x="910" y="425" font-family="Arial,sans-serif" font-size="16" fill="#40515c">Vertex error: {validation['max_source_outline_vertex_error_m']:.8f} m</text>
<rect x="60" y="755" width="1080" height="66" rx="4" fill="#e9edf0"/>
<text x="82" y="784" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#263642">Caveat:</text>
<text x="153" y="784" font-family="Arial,sans-serif" font-size="16" fill="#40515c">The GIS ring was used to build the base wall outline, so this overlap is by construction.</text>
<text x="82" y="808" font-family="Arial,sans-serif" font-size="16" fill="#40515c">It is not an independent placement or survey check; facade bearing and structural wall positions remain unverified.</text>
</svg>'''
(AUD/'footprint_overlay.svg').write_text(svg,encoding='utf-8')
print('Wrote footprint_overlay.svg and footprint_comparison.json')

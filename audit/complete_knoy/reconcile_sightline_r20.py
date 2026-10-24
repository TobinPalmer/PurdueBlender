import ast, json, math, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
EVIDENCE_R19 = ROOT / 'audit/complete_knoy/evidence_round19.json'
MANIFEST = ROOT / 'modular/manifest.json'
BUILDER = ROOT / 'modular/buildings/build_knoy_hall.py'
OUT_EVIDENCE = ROOT / 'audit/complete_knoy/evidence_round20.json'
OUT_SVG = ROOT / 'audit/complete_knoy/facade_glazing_assignment_r20.svg'
OUT_PNG = ROOT / 'audit/complete_knoy/facade_glazing_assignment_r20.png'

evidence = json.loads(EVIDENCE_R19.read_text(encoding='utf-8'))
manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
origin = manifest['origin']
text = BUILDER.read_text(encoding='utf-8')
tree = ast.parse(text)
gis_polygon = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'GIS_POLYGON' for t in node.targets):
        gis_polygon = ast.literal_eval(node.value)
        break
if gis_polygon is None:
    raise RuntimeError('GIS_POLYGON was not found in Knoy builder')
boundary = [tuple(p) for p in gis_polygon[:-1]]

def xy_from_lat_lon(lat, lon):
    x = (lon - origin['lon']) * origin['longitude_to_meters']
    y = (lat - origin['lat']) * origin['latitude_to_meters']
    return [x, y]

def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]

def ray_hits(camera_xy, heading_deg):
    a = math.radians(heading_deg)
    direction = [math.sin(a), math.cos(a)]
    hits = []
    for i, p0 in enumerate(boundary):
        p1 = boundary[(i + 1) % len(boundary)]
        edge = [p1[0] - p0[0], p1[1] - p0[1]]
        w = [p0[0] - camera_xy[0], p0[1] - camera_xy[1]]
        den = cross(direction, edge)
        if abs(den) < 1e-10:
            continue
        t = cross(w, edge) / den
        u = cross(w, direction) / den
        if t > 0 and -1e-10 <= u <= 1 + 1e-10:
            hit_xy = [camera_xy[0] + t * direction[0], camera_xy[1] + t * direction[1]]
            hits.append({'segment_index_zero_based': i, 'distance_m': t, 'edge_parameter_u': u, 'intersection_xy_m': hit_xy})
    return sorted(hits, key=lambda h: h['distance_m'])

view = evidence['facade_sightline']
lat, lon = view['camera_lat_lon']
camera_xy = xy_from_lat_lon(lat, lon)
primary = ray_hits(camera_xy, view['heading_degrees_true_north'])[0]
assert primary['segment_index_zero_based'] == 18, primary

historic = []
historic_inputs = [
    {'date': '2017-09', 'pano_id': 'D6_nILpQqNtb2fZJUbaPJQ', 'lat_lon': [40.4281078, -86.9106299]},
    {'date': '2009-06', 'pano_id': 'HBWd-zKUSYl9fdHHvzm21w', 'lat_lon': [40.4280957, -86.9106154]},
]
for item in historic_inputs:
    xy = xy_from_lat_lon(*item['lat_lon'])
    hit = ray_hits(xy, view['heading_degrees_true_north'])[0]
    historic.append({
        'date': item['date'], 'pano_id': item['pano_id'], 'camera_lat_lon': item['lat_lon'],
        'camera_xy_m': xy, 'heading_degrees_true_north': view['heading_degrees_true_north'],
        'ray_hit': hit,
        'observation': 'Historical pano has the same broad view; vegetation and perspective do not resolve window count or spacing.'
    })

view['project_xy_m'] = camera_xy
view['ray_hit'] = primary
view['historical_views_checked'] = historic
view['r19_discrepancy_correction'] = (
    'The R19 JSON camera/ray values came from the Aug 2025 pano. Its SVG accidentally plotted the June 2009 pano camera/ray while labeling it Aug 2025. '
    'The two Google pano positions differ by about 1.82 m and their ray intersections by about 1.91 m. R20 keeps them as separate views and regenerates its diagram from the primary 2025 JSON camera position.'
)
view['geometry_decision'] = (
    'The corrected 2025 sightline intersects GIS edge 18. This candidate-face match is approximate and does not resolve exact slit count, window widths, interruption positions, or cadence elsewhere. '
    'No modeled window segmentation is changed; the historic photo and Street View remain occluded/perspective imagery rather than a measured elevation.'
)
view['diagram'] = 'audit/complete_knoy/facade_glazing_assignment_r20.svg'
view['diagram_preview_png'] = 'audit/complete_knoy/facade_glazing_assignment_r20.png'
evidence['revision'] = 20
evidence['scope'] = 'R20 corrects a sightline diagram/source-coordinate mismatch and records separate panorama positions. No building geometry, materials, transforms, or placement changed.'
evidence['r19_superseded_artifact'] = {
    'file': 'audit/complete_knoy/facade_glazing_assignment_r19.svg',
    'status': 'Superseded. It plotted the June 2009 camera/ray coordinates but labeled them as the Aug 2025 pano. The JSON primary Aug 2025 coordinates were correct.'
}
evidence['new_source_search_r20'] = {
    'review_date': '2026-10-24',
    'result': 'No newly found public source provides a calibrated, face-registered Knoy elevation or window interruption schedule. Geometry remains unchanged.',
    'leads': [
        {
            'title': 'UA 62 Purdue University Office of Marketing and Media photographs, Series 3 finding aid',
            'provider': 'Purdue University Archives and Special Collections',
            'url': 'https://archives.lib.purdue.edu/fa/UA62_Series3.pdf',
            'source_date': 'Finding aid describes 1985 construction photos and a rendering for the New Technology Building (Knoy); opened-building photos from 1989 are also listed.',
            'crs': 'Not georeferenced; physical/archival photograph holdings.',
            'finding': 'The record identifies potentially useful historical images, but the catalog result does not expose calibrated, face-identified image files suitable for window-to-model assignment.',
            'use': 'Follow-up archive lead only; no geometry inference.'
        },
        {
            'title': 'Engineering and Polytechnic Gateway Formation Study, Existing Knoy Elevations',
            'provider': 'Purdue Engineering',
            'url': 'https://engineering.purdue.edu/~frosch/Renderings/Gateway/2018-05-31%20MASSING%20STUDIES%20DRAFT%20INCLUDING%20LANDSCAPE.pdf',
            'source_date': '2018-05-31 draft',
            'crs': 'Diagrammatic elevations, not a registered survey/elevation set.',
            'finding': 'Text describes alternating brick panels punctuated by stone or precast concrete and gives floor-to-floor height marks; it does not supply identifiable facade opening coordinates or exact glazing interruptions.',
            'use': 'Material and broad rhythm context only; insufficient to alter window segmentation.'
        }
    ]
}
evidence['geometry_change'] = False
OUT_EVIDENCE.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')

edge0, edge1 = boundary[18], boundary[19]
hit = primary['intersection_xy_m']
distance = primary['distance_m']
u = primary['edge_parameter_u']
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="720" viewBox="0 0 960 720">
<rect width="960" height="720" fill="#fafafa"/>
<text x="36" y="42" font-family="Arial,sans-serif" font-size="25" font-weight="700" fill="#222">Knoy Hall — Street View sightline check (R20)</text>
<text x="36" y="70" font-family="Arial,sans-serif" font-size="15" fill="#555">Both plotted points are recomputed from the same 2025 pano record in evidence_round20.json.</text>
<g transform="translate(-1178 715) scale(7 -7)">
 <polygon points="{' '.join(f'{x:.3f},{y:.3f}' for x,y in boundary)}" fill="#e8dfd2" stroke="#39414a" stroke-width="0.28"/>
 <line x1="{edge0[0]}" y1="{edge0[1]}" x2="{edge1[0]}" y2="{edge1[1]}" stroke="#c43129" stroke-width="0.8"/>
 <line x1="{camera_xy[0]}" y1="{camera_xy[1]}" x2="{hit[0]}" y2="{hit[1]}" stroke="#2869a8" stroke-width="0.55" stroke-dasharray="1.4,0.9"/>
 <circle cx="{camera_xy[0]}" cy="{camera_xy[1]}" r="0.85" fill="#2869a8" stroke="#fff" stroke-width="0.22"/>
 <circle cx="{hit[0]}" cy="{hit[1]}" r="0.65" fill="#c43129" stroke="#fff" stroke-width="0.2"/>
</g>
<text x="430" y="247" font-family="Arial,sans-serif" font-size="14" fill="#8e1f1a">GIS segment 18</text>
<text x="653" y="178" font-family="Arial,sans-serif" font-size="14" fill="#1e4e7c">2025 pano camera</text>
<text x="485" y="270" font-family="Arial,sans-serif" font-size="13" fill="#8e1f1a">ray hits segment</text>
<g transform="translate(72 125)" font-family="Arial,sans-serif" font-size="14" fill="#333">
 <line x1="0" y1="0" x2="38" y2="0" stroke="#c43129" stroke-width="5"/><text x="48" y="5">GIS exterior segment 18 (candidate photographed facade)</text>
 <line x1="0" y1="30" x2="38" y2="30" stroke="#2869a8" stroke-width="3" stroke-dasharray="8,5"/><text x="48" y="35">Street View camera ray; heading {view['heading_degrees_true_north']:.3f}° true north</text>
 <text x="0" y="69">Pano: 417 Northwestern Ave, Aug 2025; camera XY = ({camera_xy[0]:.2f}, {camera_xy[1]:.2f}) m.</text>
 <text x="0" y="91">Ray hit: ({hit[0]:.2f}, {hit[1]:.2f}) m; range = {distance:.2f} m; edge parameter u = {u:.3f}.</text>
 <text x="0" y="113">Approximate local conversion. Trees and perspective obscure slit count, dimensions and spacing.</text>
</g>
</svg>'''
OUT_SVG.write_text(svg, encoding='utf-8')

im = Image.new('RGB', (960, 720), '#fafafa')
draw = ImageDraw.Draw(im)
try:
    font = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 18)
    small = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 15)
    title = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 25)
except OSError:
    font = small = title = ImageFont.load_default()
draw.text((36, 24), 'Knoy Hall — Street View sightline check (R20)', font=title, fill='#222222')
draw.text((36, 58), 'Both plotted points use the same Aug 2025 pano record in evidence_round20.json.', font=small, fill='#555555')
def px(x, y):
    return (80 + (x - 190) * 8.4, 670 - (y + 5) * 5.8)
poly_pixels = [px(x, y) for x, y in boundary]
draw.polygon(poly_pixels, fill='#e8dfd2', outline='#39414a', width=3)
draw.line([px(*boundary[18]), px(*boundary[19])], fill='#c43129', width=8)
draw.line([px(*camera_xy), px(*hit)], fill='#2869a8', width=5)
cx, cy = px(*camera_xy)
hx, hy = px(*hit)
draw.ellipse((cx-8,cy-8,cx+8,cy+8), fill='#2869a8', outline='white', width=2)
draw.ellipse((hx-7,hy-7,hx+7,hy+7), fill='#c43129', outline='white', width=2)
draw.text((hx-65,hy+12), 'GIS segment 18', font=small, fill='#8e1f1a')
draw.text((cx-120,cy-28), '2025 pano camera', font=small, fill='#1e4e7c')
draw.text((40, 120), f'Camera ray, heading {view["heading_degrees_true_north"]:.3f}° true north', font=font, fill='#2869a8')
draw.line((40, 155, 88, 155), fill='#2869a8', width=5)
draw.line((40, 190, 88, 190), fill='#c43129', width=8)
draw.text((100, 178), f'Intersection: ({hit[0]:.2f}, {hit[1]:.2f}) m; range {distance:.2f} m; u={u:.3f}', font=small, fill='#333333')
draw.text((100, 143), f'Camera XY: ({camera_xy[0]:.2f}, {camera_xy[1]:.2f}) m', font=small, fill='#333333')
draw.text((40, 700), 'Approximate tangent-plane conversion; perspective/trees prevent window-count or spacing measurement.', font=small, fill='#555555')
im.save(OUT_PNG)
print(json.dumps({'camera_xy_m': camera_xy, 'primary_hit': primary, 'historical': historic,
                  'evidence': str(OUT_EVIDENCE), 'diagram': str(OUT_SVG), 'preview': str(OUT_PNG)}, indent=2))

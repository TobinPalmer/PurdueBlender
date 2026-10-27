import bpy, json, math, xml.etree.ElementTree as ET, os
from pathlib import Path
asset_id='massing_house_970455277_a3fb72a'
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
xml_path=root/'audit/alpha_omicron_pi/osm_way_970455277.xml'
source=json.loads((root/'audit/alpha_omicron_pi/source_register.json').read_text(encoding='utf-8'))
origin=source['model']['placement_origin_world_xy_m'] if 'placement_origin_world_xy_m' in source['model'] else source['model']['origin_world_xy_m']
# Read OSM ring and project vertices into local project coordinates independently.
tree=ET.parse(xml_path); osm=tree.getroot(); nodes={n.attrib['id']:(float(n.attrib['lon']),float(n.attrib['lat'])) for n in osm.findall('node')}
way=next(w for w in osm.findall('way') if w.attrib.get('id')=='970455277')
refs=[nd.attrib['ref'] for nd in way.findall('nd')]
ref_ring=[]
for rid in refs:
 lon,lat=nodes[rid]; x=(lon+86.9137)*111412.84*math.cos(math.radians(40.4274)); y=(lat-40.4274)*111040.0; ref_ring.append((x-origin[0],y-origin[1]))
# Actual structural perimeter is derived from the fresh-opened floor slab mesh.
obj=bpy.data.objects.get('AOII_Level_1_Slab')
assert obj is not None
actual=[]
for v in obj.data.vertices:
 if abs(v.co.z-2.98)<1e-4: actual.append((v.co.x,v.co.y))
# de-duplicate and remove closing point if present.
actual=list(dict.fromkeys((round(x,6),round(y,6)) for x,y in actual))
ref_ring=list(dict.fromkeys((round(x,6),round(y,6)) for x,y in ref_ring))
def area(poly):
 return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
def directed_hausdorff(a,b):
 return max(min(math.dist(p,q) for q in b) for p in a)
# vertex Hausdorff is sufficient here because both boundaries are linear rings with corresponding vertices.
haus=max(directed_hausdorff(actual,ref_ring),directed_hausdorff(ref_ring,actual))
report={'source':'audit/alpha_omicron_pi/osm_way_970455277.xml (WGS84, source way 970455277)','transform':'X=(lon+86.9137)*111412.84*cos(40.4274deg); Y=(lat-40.4274)*111040; then subtract the asset origin','asset_id':asset_id,'asset_file':bpy.data.filepath,'footprint_object':'AOII_Level_1_Slab lower structural ring at z=2.98 m','source_vertex_count':len(ref_ring),'asset_vertex_count':len(actual),'source_area_m2':area(ref_ring),'asset_area_m2':area(actual),'symmetric_vertex_hausdorff_m':haus,'source_vertices_local_m':ref_ring,'asset_vertices_local_m':actual,'interpretation':'Polygon vertices independently transformed from OSM and compared against the fresh-opened model footprint.'}
out=root/'audit/alpha_omicron_pi/independent_grade_r1/footprint_comparison.json'; out.write_text(json.dumps(report,indent=2),encoding='utf-8'); print(json.dumps(report,indent=2))

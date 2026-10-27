import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
asset_path=ROOT/'modular/buildings/kappa_delta.blend'
source=ROOT/'audit/kappa_delta/sources/osm_kappa_delta_building_860903232_2026-10-27.osm'
summary=json.loads((ROOT/'audit/kappa_delta/build_summary.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
collection=bpy.data.collections.get('Asset_kappa_delta')
assert collection is not None
objs=list(collection.all_objects)
meshes=[o for o in objs if o.type=='MESH']
assert bpy.context.scene.name=='Building_kappa_delta'
assert len(objs)==1216 and len(meshes)==1215
external=[i.filepath for i in bpy.data.images if i.users and i.source=='FILE']
mat_names=sorted({m.name for o in meshes for m in o.data.materials if m})
# Compute the exact official OSM ring in project campus coordinates and compare
# it to the bottom vertices of the saved foundation mesh after local origin shift.
import xml.etree.ElementTree as ET
xml=ET.parse(source).getroot()
nodes={n.attrib['id']:(float(n.attrib['lon']),float(n.attrib['lat'])) for n in xml.findall('node')}
way=next(w for w in xml.findall('way') if w.attrib.get('id')=='860903232')
ring=[nodes[n.attrib['ref']] for n in way.findall('nd')]
if ring[0]==ring[-1]: ring=ring[:-1]
origin=summary['placement_origin_xy_m']
world=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring]
expected=[(p[0]-origin[0],p[1]-origin[1]) for p in world]
base=bpy.data.objects.get('KappaDelta_OSM_Footprint_Foundation')
assert base is not None
actual=[(v.co.x,v.co.y) for v in base.data.vertices if abs(v.co.z-(-.12))<1e-5]
errs=[min(math.hypot(x-ex,y-ey) for x,y in actual) for ex,ey in expected]
probe={'sha256':hashlib.sha256(asset_path.read_bytes()).hexdigest(),'scene':bpy.context.scene.name,'collection':collection.name,'object_count':len(objs),'mesh_count':len(meshes),'material_count':len(mat_names),'materials':mat_names,'external_images':external,'foundation_ring_vertices':len(actual),'osm_ring_vertices':len(expected),'max_nearest_vertex_error_m':max(errs),'fresh_open':True}
(ROOT/'audit/kappa_delta/independent_grade_r2/fresh_open_probe.json').write_text(json.dumps(probe,indent=2)+'\n',encoding='utf8')
print(json.dumps(probe))

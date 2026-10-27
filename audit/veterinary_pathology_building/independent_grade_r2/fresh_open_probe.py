import bpy, json, hashlib, math, os
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular'/'buildings'/'massing_veterinary_pathology_building_48b5a5b.blend'
GEO=ROOT/'audit'/'veterinary_pathology_building'/'purdue_campus_building_vpth_raw.geojson'
OUT=ROOT/'audit'/'veterinary_pathology_building'/'independent_grade_r2'/'fresh_open_probe.json'
scene=bpy.data.scenes.get('Building_massing_veterinary_pathology_building_48b5a5b')
collection=bpy.data.collections.get('Asset_massing_veterinary_pathology_building_48b5a5b')
assert scene and collection, 'expected scene or collection missing'
objects=list(collection.objects)
assert len(objects)==1, f'expected exactly one building object, got {len(objects)}'
obj=objects[0]
assert obj.type=='MESH'
# Keep the source mesh local and apply only its own object matrix for local bounds.
local_verts=[obj.matrix_local @ v.co for v in obj.data.vertices]
local_bounds=[[min(float(v[i]) for v in local_verts),max(float(v[i]) for v in local_verts)] for i in range(3)]
# Source ring transformed into documented project campus frame then rebased around the recorded centroid.
feature=json.loads(GEO.read_text(encoding='utf-8'))['features'][0]
ring=feature['geometry']['coordinates'][0]
lat0,lon0=40.4274,-86.9137
coslat=math.cos(math.radians(lat0))
xy=[((lon-lon0)*111412.84*coslat,(lat-lat0)*111040.0) for lon,lat in ring]
anchor=(-162.82127231466023,-816.2568072720078)
gislocal=[(x-anchor[0],y-anchor[1]) for x,y in xy]
gisbounds=[[min(p[i] for p in gislocal),max(p[i] for p in gislocal)] for i in range(2)]
bottom=[(float((obj.matrix_local@v.co).x),float((obj.matrix_local@v.co).y)) for v in obj.data.vertices if abs(float((obj.matrix_local@v.co).z))<1e-5]
hgis=max(min(math.hypot(x-u,y-v) for u,v in bottom) for x,y in gislocal)
hmesh=max(min(math.hypot(x-u,y-v) for u,v in gislocal) for x,y in bottom)
materials=[]
for i,mat in enumerate(obj.data.materials):
 used=sum(1 for poly in obj.data.polygons if poly.material_index==i)
 node_types=[]
 if mat and mat.use_nodes and mat.node_tree: node_types=[n.type for n in mat.node_tree.nodes]
 materials.append({'slot':i,'name':mat.name if mat else None,'polygons_using_slot':used,'node_types':node_types})
images=[{'name':im.name,'path':bpy.path.abspath(im.filepath)} for im in bpy.data.images if im.source=='FILE']
libraries=[bpy.path.abspath(lib.filepath) for lib in bpy.data.libraries if lib.filepath]
report={
 'readback_fresh_process':True,
 'blender_version':bpy.app.version_string,
 'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),
 'scene':scene.name,'collection':collection.name,'collection_object_count':len(objects),
 'object_name':obj.name,'stable_asset_id':obj.get('stable_asset_id'),'object_type':obj.type,
 'object_location_m':[float(x) for x in obj.location],
 'local_bounds_m':local_bounds,'GIS_local_bounds_xy_m':gisbounds,
 'GIS_to_mesh_base_hausdorff_m':hgis,'mesh_base_to_GIS_ring_hausdorff_m':hmesh,
 'vertex_count':len(obj.data.vertices),'polygon_count':len(obj.data.polygons),
 'material_slot_count':len(obj.data.materials),'materials':materials,
 'unused_material_slots':[m['name'] for m in materials if m['polygons_using_slot']==0],
 'file_image_dependencies':images,'external_libraries':libraries,
 'scene_object_types':{t:sum(1 for o in scene.objects if o.type==t) for t in sorted(set(o.type for o in scene.objects))},
 'GIS_properties':feature['properties']
}
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

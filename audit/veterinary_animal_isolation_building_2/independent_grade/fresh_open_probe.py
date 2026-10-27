import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
folder=root/'audit/veterinary_animal_isolation_building_2'
asset=root/'modular/buildings/massing_veterinary_animal_isolation_building_2_ebb4142.blend'
out=folder/'independent_grade/fresh_open_probe.json'
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.context.scene
collection=bpy.data.collections.get('Asset_massing_veterinary_animal_isolation_building_2_ebb4142')
assert collection
meshes=[o for o in collection.objects if o.type=='MESH']
verts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
lo=[min(v[i] for v in verts) for i in range(3)]; hi=[max(v[i] for v in verts) for i in range(3)]
found=next(o for o in meshes if o.name=='VA2 GIS footprint foundation')
fbb=[found.matrix_world@Vector(c) for c in found.bound_box]
fmin=[min(p[i] for p in fbb) for i in range(3)]; fmax=[max(p[i] for p in fbb) for i in range(3)]
source=json.loads((folder/'sources/purdue_va2_fid942.geojson').read_text(encoding='utf-8'))
ring=source['features'][0]['geometry']['coordinates'][0]
lat0,lon0=40.4274,-86.9137
cx=111412.84*math.cos(math.radians(lat0)); cy=111040.0
anchor=[-201.17001685170442,-948.4519000771968]
xy=[((p[0]-lon0)*cx-anchor[0],(p[1]-lat0)*cy-anchor[1]) for p in ring]
gis_min=[min(p[i] for p in xy) for i in range(2)]; gis_max=[max(p[i] for p in xy) for i in range(2)]
found_min=fmin[:2]; found_max=fmax[:2]
edge_diffs=[max(abs(gis_min[i]-found_min[i]),abs(gis_max[i]-found_max[i])) for i in range(2)]
# Check that major roof units rest on the roof plane. Bounds for a small sample are enough to expose stray objects.
roof_samples=[]
for o in meshes:
    if o.name in ('VA2 central rooftop service strip','VA2 rooftop unit 1 body','VA2 roof exhaust curb 1','VA2 roof perimeter parapet'):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        roof_samples.append({'name':o.name,'z_min':round(min(p.z for p in bb),3),'z_max':round(max(p.z for p in bb),3)})
report={'readback_fresh_process':True,'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'scene':scene.name,'building_id':scene.get('building_id'),'collection':collection.name,'objects':len(collection.objects),'object_types':{t:sum(o.type==t for o in collection.objects) for t in sorted({o.type for o in collection.objects})},'materials':len({m.name for o in meshes for m in o.data.materials if m}),'bounds_local':{'min':lo,'max':hi,'size':[hi[i]-lo[i] for i in range(3)]},'foundation_bounds_xy':{'min':found_min,'max':found_max},'gis_footprint_xy':{'min':gis_min,'max':gis_max},'max_foundation_bbox_error_m':max(edge_diffs),'scene_origin_xy':list(scene.get('origin_xy_m')),'file_image_dependencies':[i.name for i in bpy.data.images if i.source=='FILE'],'external_libraries':[l.filepath for l in bpy.data.libraries],'roof_component_sample':roof_samples}
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

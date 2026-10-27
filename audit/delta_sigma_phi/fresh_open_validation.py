import bpy, os, json, math, hashlib
from mathutils import Vector
path=bpy.data.filepath
asset_id='massing_house_860826641_2c90f97'
expected_scene='Building_'+asset_id
expected_collection='Asset_'+asset_id
col=bpy.data.collections.get(expected_collection)
assert bpy.context.scene.name==expected_scene, (bpy.context.scene.name,expected_scene)
assert col is not None, expected_collection
objects=list(col.objects)
meshes=[o for o in objects if o.type=='MESH']
materials=sorted({m.name for o in meshes for m in o.data.materials if m})
verts=[]
for o in meshes:
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); me=e.to_mesh()
    verts.extend([e.matrix_world @ v.co for v in me.vertices]); e.to_mesh_clear()
bounds=[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)]
# Recheck the saved structural wall vertices against the official FID 798 ring in the documented local frame.
root=bpy.data.objects.get('AssetRoot_'+asset_id)
assert root is not None and tuple(round(v,9) for v in root.location)==(0.0,0.0,0.0)
G=json.load(open('audit/delta_sigma_phi/sources/purdue_gis_fid798_delta_sigma_phi_2026-10-26_wgs84.json',encoding='utf-8-sig'))['features'][0]
ring=G['geometry']['rings'][0][:-1]
origin=(-86.9137,40.4274); mx=84810.60416539927; my=111040.0; theta=math.radians(129.44405524991802); cx,cy=(357.7400581596961,-73.82974158000164)
def expected(lon,lat):
    x=(lon-origin[0])*mx-cx; y=(lat-origin[1])*my-cy
    u=x*math.cos(theta)+y*math.sin(theta); v=-x*math.sin(theta)+y*math.cos(theta)
    return (u*math.cos(theta)-v*math.sin(theta),u*math.sin(theta)+v*math.cos(theta))
max_error=0.0
for i,(lon,lat) in enumerate(ring):
    ob=bpy.data.objects.get('DSP_Exterior_Wall_%02d'%i)
    assert ob is not None, 'missing GIS edge '+str(i)
    p=ob.matrix_world @ ob.data.vertices[0].co
    e=expected(lon,lat)
    max_error=max(max_error,math.hypot(p.x-e[0],p.y-e[1]))
# No hidden floorplan/interior objects were created; no external images or linked libraries.
interior_names=[o.name for o in objects if 'interior' in o.name.lower() or 'floorplan' in o.name.lower()]
external_images=[im.filepath for im in bpy.data.images if im.source=='FILE']
linked_libraries=[lib.filepath for lib in bpy.data.libraries]
source_hash=hashlib.sha256(open(path,'rb').read()).hexdigest()
report={
 'fresh_open':'PASS', 'blender_version':bpy.app.version_string, 'file':path, 'sha256':source_hash,
 'scene':bpy.context.scene.name,'expected_scene':expected_scene,'collection':col.name,'expected_collection':expected_collection,
 'asset_object_count':len(objects),'mesh_object_count':len(meshes),'mesh_vertex_count':sum(len(o.data.vertices) for o in meshes),'mesh_polygon_count':sum(len(o.data.polygons) for o in meshes),'unique_material_count':len(materials),'materials':materials,
 'local_bounds_m':bounds,'gis_footprint_edge_count':len(ring),'max_wall_vertex_xy_error_vs_gis_m':max_error,
 'external_image_dependencies':external_images,'linked_library_dependencies':linked_libraries,'interior_or_floorplan_objects':interior_names,
 'placement_origin_xy_m':[cx,cy], 'notes':'Preview rig was excluded from saved asset; all shader textures are procedural. Geometry remains local and the shared manifest/master marker still require coordinator integration.'
}
os.makedirs('audit/delta_sigma_phi',exist_ok=True)
json.dump(report,open('audit/delta_sigma_phi/fresh_open_validation.json','w',encoding='utf8'),indent=2)
print(json.dumps(report,indent=2))

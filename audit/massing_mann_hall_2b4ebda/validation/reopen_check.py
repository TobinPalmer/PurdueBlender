import bpy, json, math
from pathlib import Path
root=Path(__file__).resolve().parents[3]
asset=root/'modular/buildings/massing_mann_hall_2b4ebda.blend'
src=root/'audit/massing_mann_hall_2b4ebda/sources/purdue_building_gis_fid_635.json'
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.data.scenes.get('Building_massing_mann_hall_2b4ebda')
col=bpy.data.collections.get('Asset_massing_mann_hall_2b4ebda')
assert scene is not None and col is not None
assert len(col.objects)==1, f'Expected one exported object; found {len(col.objects)}'
obj=col.objects[0]; assert obj.name=='Mann Hall' and obj.type=='MESH'
assert not obj.modifiers, f'Unexpected modifiers: {[m.name for m in obj.modifiers]}'
assert not list(bpy.data.libraries), f'External Blender libraries: {[x.filepath for x in bpy.data.libraries]}'
dg=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(dg); mesh=ev.to_mesh()
pts=[obj.matrix_world@v.co for v in mesh.vertices]
bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
feature=json.loads(src.read_text(encoding='utf-8'))['features'][0]
coords=feature['geometry']['rings'][0]
def proj(lon,lat): return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)
ring=[proj(*p) for p in coords]
if math.dist(ring[0],ring[-1])<0.02: ring.pop()
clean=[]
for p in ring:
 if not clean or math.dist(clean[-1],p)>0.12: clean.append(p)
if math.dist(clean[0],clean[-1])<0.12: clean.pop()
base=[(p.x,p.y) for p in pts if abs(p.z)<1e-5]
nearest=[]
for x,y in clean:
 nearest.append(min(math.hypot(x-a,y-b) for a,b in base))
report={
 'validated_in_blender':bpy.app.version_string,'asset':str(asset.relative_to(root)),
 'scene':scene.name,'collection':col.name,'collection_objects':[o.name for o in col.objects],
 'mesh_vertices':len(mesh.vertices),'mesh_faces':len(mesh.polygons),'modifiers':[m.type for m in obj.modifiers],
 'external_libraries':[x.filepath for x in bpy.data.libraries],
 'evaluated_world_bounds_m':bounds,'evaluated_height_m':bounds[2][1]-bounds[2][0],
 'source_feature':'Purdue ArcGIS FID 635 / MANN','source_ring_points':len(clean),
 'max_source_vertex_to_shell_base_m':max(nearest),'mean_source_vertex_to_shell_base_m':sum(nearest)/len(nearest),
 'mesh_materials':[m.name for m in mesh.materials],
 'custom_properties':{k:obj[k] for k in obj.keys()}
}
ev.to_mesh_clear()
out=root/'audit/massing_mann_hall_2b4ebda/validation/reopen_validation.json'
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('REOPEN_VALIDATION',json.dumps(report))

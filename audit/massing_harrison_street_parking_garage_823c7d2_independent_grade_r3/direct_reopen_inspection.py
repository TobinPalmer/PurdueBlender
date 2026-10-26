import bpy, json, os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/massing_harrison_street_parking_garage_823c7d2.blend'
OUT=Path(__file__).with_name('direct_reopen_inspection.json')
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
coll=bpy.data.collections.get('Asset_massing_harrison_street_parking_garage_823c7d2')
assert coll is not None
deps=bpy.context.evaluated_depsgraph_get()
pts=[]; objects=[]
for ob in coll.objects:
    ev=ob.evaluated_get(deps); mesh=ev.to_mesh()
    vv=[ev.matrix_world@v.co for v in mesh.vertices]
    if vv: pts.extend(vv)
    bounds=[[min(v[i] for v in vv),max(v[i] for v in vv)] for i in range(3)] if vv else None
    objects.append({'name':ob.name,'type':ob.type,'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'bounds':bounds,'materials':[m.name for m in mesh.materials]})
    ev.to_mesh_clear()
all_bounds=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
images=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath:
        images.append({'path':im.filepath,'packed':bool(im.packed_file),'exists':os.path.exists(bpy.path.abspath(im.filepath))})
data={'asset':str(ASSET.relative_to(ROOT)).replace('\\','/'),'scene_names':[s.name for s in bpy.data.scenes],'expected_collection':coll.name,'object_count':len(coll.objects),'mesh_objects':sum(o.type=='MESH' for o in coll.objects),'bounds_xyz':all_bounds,'objects':objects,'images':images,'linked_libraries':[lib.filepath for lib in bpy.data.libraries],'evaluated_after_reopen':True}
OUT.write_text(json.dumps(data,indent=2),encoding='utf-8')
print('INDEPENDENT_REOPEN',json.dumps(data))

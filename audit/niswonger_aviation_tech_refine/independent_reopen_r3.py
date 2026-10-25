import bpy, json, hashlib, os
from pathlib import Path
from mathutils import Vector

ROOT = Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
ASSET_PATH = ROOT/'modular/buildings/niswonger_aviation_tech.blend'
MASTER_PATH = ROOT/'purdue_campus_master.blend'
MANIFEST_PATH = ROOT/'modular/manifest.json'
OUT = ROOT/'audit/niswonger_aviation_tech_refine/independent_reopen_r3.json'
manifest=json.loads(MANIFEST_PATH.read_text(encoding='utf8'))
record=next(a for a in manifest['assets'] if a['id']=='niswonger_aviation_tech')
expected=set(record['objects'])
asset_hash=hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))
coll=bpy.data.collections.get(record['collection'])
assert coll
objects=list(coll.all_objects)
actual=set(o.name for o in objects)
mesh_objects=[o for o in objects if o.type=='MESH']
lo=[float('inf')]*3; hi=[float('-inf')]*3
for o in objects:
    for c in o.bound_box:
        p=o.matrix_world@Vector(c)
        for i in range(3): lo[i]=min(lo[i],p[i]);hi[i]=max(hi[i],p[i])
materialed=[o.name for o in mesh_objects if not o.data.materials or all(m is None for m in o.data.materials)]
images=[]
for image in bpy.data.images:
    if image.source=='FILE':
        images.append({'name':image.name,'filepath':bpy.path.abspath(image.filepath),'packed':bool(image.packed_file),'exists':os.path.exists(bpy.path.abspath(image.filepath))})
named={k:[o.name for o in objects if k in o.name.lower()] for k in ('hangar','connector','sloping_roof','roof')}
roof_info=[]
for name in ('NISW_R2_Roof_Brick_Wing','NISW_R2_Roof_Classroom_Wing','NISW_Photographic_Sloping_Roof'):
    o=bpy.data.objects.get(name)
    if o:
        pts=[o.matrix_world@Vector(c) for c in o.bound_box]
        roof_info.append({'name':name,'type':o.type,'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'vertices':len(o.data.vertices) if o.type=='MESH' else None,'faces':len(o.data.polygons) if o.type=='MESH' else None})
asset_result={'path':str(ASSET_PATH),'sha256':asset_hash,'fresh_reopen':True,'scene':bpy.context.scene.name,'collection':coll.name,'object_count':len(objects),'expected_object_count':record['object_count'],'mesh_count':len(mesh_objects),'missing_manifest_names':sorted(expected-actual),'extra_names':sorted(actual-expected),'actual_local_bounds':[lo,hi], 'expected_local_bounds_m':record['local_bounds_m'],'root':{'name':record['objects'][0],'location':list(bpy.data.objects[record['objects'][0]].location)},'materialless_meshes':materialed,'file_images':images,'roof_objects':roof_info,'named_inventory':named}
# Verify the master still has an instance/linked collection sourced from this asset.
bpy.ops.wm.open_mainfile(filepath=str(MASTER_PATH))
links=[]
for o in bpy.data.objects:
    if o.instance_type=='COLLECTION' and o.instance_collection and 'niswonger' in o.instance_collection.name.lower():
        links.append({'object':o.name,'collection':o.instance_collection.name,'location':list(o.location),'rotation_euler':list(o.rotation_euler),'scale':list(o.scale),'library_filepath':o.instance_collection.library.filepath if o.instance_collection.library else None})
for c in bpy.data.collections:
    if 'niswonger' in c.name.lower() and c.library:
        links.append({'collection':c.name,'library_filepath':c.library.filepath,'objects':len(c.all_objects)})
result={'asset':asset_result,'master':{'path':str(MASTER_PATH),'niswonger_references':links}}
OUT.write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))

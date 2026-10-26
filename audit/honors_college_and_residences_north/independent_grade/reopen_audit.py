import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
asset=Path(bpy.data.filepath)
asset_id='massing_honors_college_and_residences_north_3de3b7c'
coll=bpy.data.collections.get('Asset_'+asset_id)
scene=bpy.data.scenes.get('Building_'+asset_id)
assert coll and scene
shell=bpy.data.objects.get('LeesSuch_GIS_Footprint_SixFloor_Shell')
assert shell and shell.type=='MESH'
verts=[list(shell.matrix_world @ v.co) for v in shell.data.vertices]
n=len(verts)//2
records=[]
for o in coll.objects:
 if o.type=='MESH':
  w=[o.matrix_world @ Vector(c) for c in o.bound_box]
  records.append({'name':o.name,'bounds':[[min(v[i] for v in w) for i in range(3)],[max(v[i] for v in w) for i in range(3)]],'verts':len(o.data.vertices),'faces':len(o.data.polygons),'materials':[m.name if m else None for m in o.data.materials]})
images=[im.filepath for im in bpy.data.images]
materials=[]
for m in bpy.data.materials:
 if m.users:
  materials.append({'name':m.name,'users':m.users,'nodes':[n.type for n in m.node_tree.nodes] if m.use_nodes else [],'images':[n.image.filepath for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.use_nodes else []})
report={'asset_path':str(asset),'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'scene':scene.name,'collection':coll.name,'collection_object_count':len(coll.objects),'mesh_object_count':len(records),'shell_name':shell.name,'shell_vertex_count':len(shell.data.vertices),'bottom_ring_xyz':verts[:n],'top_ring_z_range':[min(v[2] for v in verts[n:]),max(v[2] for v in verts[n:])],'schematic_scene_exists':bpy.data.scenes.get('Building_'+asset_id+'_SchematicInterior_NOT_AS_BUILT') is not None,'images':images,'materials':materials,'objects':records}
out=Path(__file__).resolve().parent/'reopen_audit.json'
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('objects','materials','bottom_ring_xyz')},indent=2))

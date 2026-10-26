import bpy,json,sys,hashlib
from pathlib import Path
root=Path(r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender')
out=root/'audit/beering_hall_independent_grade'
asset=root/'modular/buildings/beering_hall.blend'
probe=out/'blender_probe.json'
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.context.scene
coll=bpy.data.collections.get('Asset_beering_hall')
assert scene and scene.name=='Building_beering_hall'
assert coll is not None
objs=[]; coords=[]; mesh_count=0; external=[]
deps=bpy.context.evaluated_depsgraph_get()
for obj in sorted(coll.all_objects,key=lambda o:o.name):
    rec={'name':obj.name,'type':obj.type,'location_local':list(obj.location),'dimensions_local':list(obj.dimensions),'bound_box_world_local':[[min((obj.matrix_world @ __import__('mathutils').Vector(c))[i] for c in obj.bound_box),max((obj.matrix_world @ __import__('mathutils').Vector(c))[i] for c in obj.bound_box)] for i in range(3)]}
    objs.append(rec)
    if obj.type=='MESH':
      mesh_count+=1
      ev=obj.evaluated_get(deps); mesh=ev.to_mesh()
      try:
       pts=[ev.matrix_world @ v.co for v in mesh.vertices]
       coords.extend(pts)
       rec['evaluated_vertices']=len(pts)
      finally: ev.to_mesh_clear()
    for slot in obj.material_slots:
     mat=slot.material
     if mat and mat.use_nodes:
      for node in mat.node_tree.nodes:
       if node.type=='TEX_IMAGE' and node.image and node.image.filepath:
        fp=node.image.filepath
        external.append({'object':obj.name,'image':node.image.name,'filepath':fp,'packed':bool(node.image.packed_file)})
allbounds=[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)]
structural={}
for obj_name in ['BRNG_Classroom_Wing_Masonry','BRNG_Office_Tower_Masonry','BRNG_Rotunda_Masonry_Drum_Core']:
    obj=bpy.data.objects.get(obj_name)
    assert obj is not None and obj.name in coll.objects
    ev=obj.evaluated_get(deps); mesh=ev.to_mesh()
    try:
      points=[ev.matrix_world @ v.co for v in mesh.vertices]
      floor=[(round(v.x,6),round(v.y,6)) for v in points if abs(v.z)<0.005]
      structural[obj_name]={'bounds':[[min(v[i] for v in points),max(v[i] for v in points)] for i in range(3)],'bottom_vertices_xy':sorted(set(floor))}
    finally: ev.to_mesh_clear()
export_probe=out/'collection_export_probe.blend'
bpy.data.libraries.write(str(export_probe),{coll},path_remap='RELATIVE_ALL',fake_user=True)
report={'asset':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'scene':scene.name,'collection':coll.name,'object_count':len(coll.all_objects),'mesh_object_count':mesh_count,'object_names':sorted(o.name for o in coll.all_objects),'objects':objs,'evaluated_bounds_local_m':allbounds,'external_image_paths':external,'linked_libraries':[{'filepath':lib.filepath,'absolute':bpy.path.abspath(lib.filepath)} for lib in bpy.data.libraries if lib.filepath], 'scene_cameras_lights':sorted(o.name for o in scene.objects if o.type in {'CAMERA','LIGHT'}),'structural_objects':structural,'export_probe_file':str(export_probe),'candidates':[o for o in objs if any(t in o['name'].lower() for t in ['masonry','wall','shell','roof','tower','classroom_wing'])]}
probe.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['blender_version','scene','collection','object_count','mesh_object_count','evaluated_bounds_local_m','external_image_paths','linked_libraries','scene_cameras_lights']},indent=2))
print('structural objects:',{n:{'bounds':v['bounds'],'bottom_vertex_count':len(v['bottom_vertices_xy'])} for n,v in structural.items()})
print('export probe:',export_probe)

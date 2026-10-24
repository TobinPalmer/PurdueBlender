import bpy, json, os, math
from mathutils import Vector
p=r'modular/buildings/birck_nanotechnology_center.blend'
bpy.ops.wm.open_mainfile(filepath=p)
collection=bpy.data.collections.get('Asset_birck_nanotechnology_center')
if not collection: raise RuntimeError('Expected exported collection missing')
objs=list(collection.objects)
mesh_objs=[o for o in objs if o.type=='MESH']
coords=[]
for o in mesh_objs:
    for c in o.bound_box: coords.append(o.matrix_world @ Vector(c))
mins=[min(v[i] for v in coords) for i in range(3)]; maxs=[max(v[i] for v in coords) for i in range(3)]
materials=[]
for m in bpy.data.materials:
    if m.name.startswith('BIRCK'):
        principled=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
        links=[]
        if principled:
            for socket in [principled.inputs.get('Base Color'),principled.inputs.get('Normal')]:
                if socket and socket.is_linked: links.extend(link.from_node.type for link in socket.links)
        materials.append({'name':m.name,'node_types_linked_to_principled':links})
scene=bpy.context.scene
cam=scene.camera
if not cam: raise RuntimeError('Saved preview camera missing')
print(json.dumps({'file':bpy.data.filepath,'collection':collection.name,'object_count':len(objs),'mesh_count':len(mesh_objs),'bounds_local_m':{'min':mins,'max':maxs},'camera':cam.name,'materials':materials,'linked_library_paths':[l.filepath for l in bpy.data.libraries if l.filepath]},indent=2))
scene.render.resolution_x=960; scene.render.resolution_y=746; scene.render.resolution_percentage=100; scene.cycles.samples=8
scene.render.filepath=r'C:\\Users\\Tobin\\Documents\\Blender\\PurdueMap\\audit\\birck_nanotechnology_center\\reopened_validation.png'
bpy.ops.render.render(write_still=True)
print('REOPEN_RENDER_OK',os.path.getsize(scene.render.filepath))


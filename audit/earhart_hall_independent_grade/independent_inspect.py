import bpy, json, hashlib, math, os
from mathutils import Vector
p = r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_earhart_hall_0f14209.blend'
out = r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\earhart_hall_independent_grade'
with open(p,'rb') as f: digest=hashlib.sha256(f.read()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=p)
scene=bpy.context.scene
colls=[c.name for c in bpy.data.collections]
asset=next((c for c in bpy.data.collections if c.name=='Asset_massing_earhart_hall_0f14209'),None)
objs=list(asset.all_objects) if asset else list(scene.objects)
mins=[1e30]*3; maxs=[-1e30]*3; meshes=[]; images=[]
for ob in objs:
    if ob.type=='MESH':
        deps=bpy.context.evaluated_depsgraph_get(); ev=ob.evaluated_get(deps); me=ev.to_mesh()
        meshes.append({'name':ob.name,'verts':len(me.vertices),'polys':len(me.polygons),'materials':[m.name for m in ob.data.materials if m], 'dims':list(ob.dimensions)})
        for v in me.vertices:
            w=ev.matrix_world @ v.co
            for i in range(3): mins[i]=min(mins[i],w[i]); maxs[i]=max(maxs[i],w[i])
        ev.to_mesh_clear()
for im in bpy.data.images:
    if im.source not in {'GENERATED','VIEWER'}: images.append({'name':im.name,'filepath':im.filepath,'packed':bool(im.packed_file)})
materials=[]
for m in bpy.data.materials:
    if m.name.startswith('ERHT_'):
        materials.append({'name':m.name,'nodes':[(n.bl_idname, n.name) for n in m.node_tree.nodes] if m.use_nodes else []})
# Fresh process inspection, generate reproducible orthographic review render using saved asset camera-independent.
# don't save changes to candidate file.
cam_data=bpy.data.cameras.new('IndependentReviewCamera'); cam=bpy.data.objects.new('IndependentReviewCamera',cam_data); scene.collection.objects.link(cam)
cam.location=(-878,-120,92); target=Vector((-954,-174,12)); direction=target-Vector(cam.location); cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=170; scene.camera=cam
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1500; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(out,'fresh_open_overview.png'); scene.render.film_transparent=False
scene.view_settings.view_transform='Standard'
bpy.ops.render.render(write_still=True)
report={'sha256':digest,'fresh_process_opened':True,'scene':scene.name,'collections':colls,'asset_collection_found':bool(asset),'object_count':len(objs),'mesh_objects':meshes,'materials':materials,'images':images,'bounds_world_m':[mins,maxs],'render':scene.render.filepath}
with open(os.path.join(out,'independent_fresh_open.json'),'w') as f: json.dump(report,f,indent=2)

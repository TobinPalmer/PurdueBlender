"""Freshly reopen the candidate PAO asset and produce an audit-only exterior view."""
import bpy, os, json, hashlib, math
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
path=os.path.join(root,'modular','buildings','massing_yue_kong_pao_hall_a3cb766.blend')
bpy.ops.wm.open_mainfile(filepath=path)
scene=bpy.context.scene
col=bpy.data.collections.get('Asset_massing_yue_kong_pao_hall_a3cb766')
assert col and len(col.objects)==363, ('asset collection missing/unexpected object count',len(col.objects) if col else None)
assert bpy.data.scenes.get('Building_massing_yue_kong_pao_hall_a3cb766')
mesh=[o for o in col.objects if o.type=='MESH']
assert len(mesh)>=300
assert all(len(o.data.materials)>0 for o in mesh), [o.name for o in mesh if not o.data.materials]
assert all(im.packed_file is not None for im in bpy.data.images if im.source=='FILE'),[(im.name,im.filepath) for im in bpy.data.images if im.source=='FILE' and im.packed_file is None]
deps=[]
for im in bpy.data.images:
    if im.source=='FILE': deps.append({'name':im.name,'packed':bool(im.packed_file),'path':im.filepath})
for o in bpy.context.scene.objects: o.select_set(False)
# Audit-only camera, world, and lights are created in memory and never saved into the asset.
world=scene.world or bpy.data.worlds.new('PAO audit world'); scene.world=world; world.use_nodes=True
world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.30,.38,.49,1)
world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.4
def aim(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('Audit south facade camera'); cam=bpy.data.objects.new('Audit south facade camera',data); scene.collection.objects.link(cam)
cam.location=(40,-660,23); aim(cam,(63,-550,8.5)); data.lens=45; scene.camera=cam
ld=bpy.data.lights.new('Audit sun','SUN'); lo=bpy.data.objects.new('Audit sun',ld); scene.collection.objects.link(lo); lo.rotation_euler=(math.radians(28),0,math.radians(-24)); ld.energy=1.25
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1800; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(os.path.dirname(__file__),'south_facade_candidate.png'); scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'
bpy.ops.render.render(write_still=True)
sha=hashlib.sha256(open(path,'rb').read()).hexdigest()
bounds=[]
for axis in range(3):
    vals=[o.matrix_world @ v.co for o in mesh for v in o.data.vertices]
    bounds.append([round(min(v[axis] for v in vals),3),round(max(v[axis] for v in vals),3)])
info={'asset':path,'sha256':sha,'scene':'Building_massing_yue_kong_pao_hall_a3cb766','collection':col.name,'object_count':len(col.objects),'mesh_count':len(mesh),'mesh_vertices':sum(len(o.data.vertices) for o in mesh),'mesh_faces':sum(len(o.data.polygons) for o in mesh),'all_meshes_have_materials':True,'images':deps,'campus_bounds_xyz_m':bounds,'render':scene.render.filepath,'fresh_reopen':True,'isolation':'audit camera/light/world are memory-only and not saved'}
with open(os.path.join(os.path.dirname(__file__),'fresh_reopen_validation.json'),'w') as f: json.dump(info,f,indent=2)
print('FRESH_REOPEN_VALIDATION',json.dumps(info))

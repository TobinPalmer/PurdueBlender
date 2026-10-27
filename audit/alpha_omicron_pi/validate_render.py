import bpy, json, math, os
from mathutils import Vector
p=bpy.data.filepath
asset_id='massing_house_970455277_a3fb72a'
coll=bpy.data.collections.get('Asset_'+asset_id)
scene=bpy.data.scenes.get('Building_'+asset_id)
assert coll and scene, 'required collection or scene missing'
objs=list(coll.all_objects)
assert len(objs)>=500, f'geometry count unexpectedly low: {len(objs)}'
assert all(o.type=='MESH' for o in objs), 'non-mesh object found'
materials={m.name for m in bpy.data.materials}
assert len(materials)>=10, f'materials missing: {len(materials)}'
for o in objs:
    assert len(o.data.polygons)>0, f'empty mesh {o.name}'
# set up temporary inspection scene data in memory for fresh-file renders
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.render.resolution_percentage=65
scene.world.color=(0.18,0.18,0.18)
# ensure world has a light background for material preview-like output
if scene.world and scene.world.use_nodes:
    bg=scene.world.node_tree.nodes.get('Background')
    if bg: bg.inputs['Color'].default_value=(.35,.38,.42,1); bg.inputs['Strength'].default_value=.7
ld=bpy.data.lights.new('Inspection_Key','AREA'); lo=bpy.data.objects.new('Inspection_Key',ld); scene.collection.objects.link(lo); lo.location=(-22,-26,35); ld.energy=1500; ld.shape='DISK'; ld.size=24
ld2=bpy.data.lights.new('Inspection_Fill','AREA'); lo2=bpy.data.objects.new('Inspection_Fill',ld2); scene.collection.objects.link(lo2); lo2.location=(24,12,22); ld2.energy=850; ld2.size=18
center=Vector((0,0,4.8))
def camera(name,loc,scale):
    cd=bpy.data.cameras.new(name); co=bpy.data.objects.new(name,cd); scene.collection.objects.link(co); co.location=loc; co.rotation_euler=(center-co.location).to_track_quat('-Z','Y').to_euler(); cd.type='ORTHO'; cd.ortho_scale=scale; scene.camera=co; return co
out=r'audit/alpha_omicron_pi'
for name,loc,scale in [('front_west',(-31,-1,15),34),('entry_isometric',(-28,-32,23),39),('terrace_aerial',(21,27,38),39)]:
    camera('Inspection_'+name,loc,scale)
    scene.render.filepath=os.path.abspath(os.path.join(out,'preview_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
coords=[o.matrix_world @ v.co for o in objs for v in o.data.vertices]
bounds_local_m=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
report={'file':p,'scene':scene.name,'collection':coll.name,'object_count':len(objs),'mesh_count':sum(o.type=='MESH' for o in objs),'material_count':len(materials),'bounds_local_m':bounds_local_m,'origin_world_xy_m':list(scene['local_origin_world_xy_m']),'saved':True,'renders':[os.path.abspath(os.path.join(out,'preview_'+n+'.png')) for n in ['front_west','entry_isometric','terrace_aerial']]}
with open(os.path.join(out,'fresh_open_validation.json'),'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
import bpy, os, math
from mathutils import Vector

ROOT = r'C:\Users\Tobin\Documents\Blender\PurdueMap'
NAMES = ['armory','beering_hall','american_railway_building','brown_laboratory_of_chemistry','peirce_hall']
OUT = os.path.join(ROOT, 'audit', 'texture_batch_1')
os.makedirs(OUT, exist_ok=True)

def setup_render():
    scene=bpy.context.scene
    objs=[o for o in bpy.data.objects if o.type=='MESH']
    pts=[o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    if not pts: return
    lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    center=(lo+hi)/2
    dims=hi-lo
    diag=max(dims.length, 10)
    # Broad front-left three-quarter view, camera fitted to full asset.
    direction=Vector((1,-1,0.58)).normalized()
    cam_data=bpy.data.cameras.new('TextureAuditCamera')
    cam=bpy.data.objects.new('TextureAuditCamera',cam_data); scene.collection.objects.link(cam)
    cam.location=center+direction*diag*1.7
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    cam_data.lens=48
    scene.camera=cam
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.film_transparent=False
    world=scene.world or bpy.data.worlds.new('TextureAuditWorld'); scene.world=world; world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.22,0.28,0.38,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.7
    # Soft studio key and fill.
    for name, offset, power, size, color in [('Key',Vector((-1,-1,1.5)),18000,50,(1.0,.84,.68)),('Fill',Vector((1,1,1)),9000,42,(.65,.78,1.0))]:
        ld=bpy.data.lights.new(name,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=size; ld.color=color
        lo_obj=bpy.data.objects.new(name,ld); scene.collection.objects.link(lo_obj); lo_obj.location=center+offset*diag*1.2; lo_obj.rotation_euler=(center-lo_obj.location).to_track_quat('-Z','Y').to_euler()
    scene.view_settings.view_transform='AgX'
    scene.render.filepath=os.path.join(OUT, NAMES[NAMES.index(os.path.basename(bpy.data.filepath).replace('.blend',''))]+'.png')
    return objs,lo,hi

for name in NAMES:
    path=os.path.join(ROOT,'modular','buildings',name+'.blend')
    bpy.ops.wm.open_mainfile(filepath=path)
    summary=[]
    mats={m for o in bpy.data.objects if o.type=='MESH' for m in o.data.materials if m}
    for mat in sorted(mats,key=lambda m:m.name):
        nt=mat.node_tree
        if not nt: continue
        surf=next((l.from_node for l in nt.links if l.to_node.type=='OUTPUT_MATERIAL' and l.to_socket.name=='Surface'),None)
        principled=surf if surf and surf.type=='BSDF_PRINCIPLED' else None
        def inp(key,default=None):
            try: return tuple(round(float(x),3) for x in principled.inputs[key].default_value)
            except: return default
        node_desc=[]
        for n in nt.nodes:
            if n.type in {'TEX_NOISE','TEX_IMAGE','TEX_COORD','BUMP','TEX_VORONOI'}:
                links=[(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name) for l in nt.links if l.to_node==n or l.from_node==n]
                node_desc.append((n.name,n.type,[(x[0],x[1],x[3],x[4]) for x in links]))
        summary.append({'mat':mat.name,'base':inp('Base Color'),'roughness':inp('Roughness'),'metallic':inp('Metallic'),'surface':principled.name if principled else (surf.type if surf else 'none'),'tex':node_desc})
    log=os.path.join(OUT,name+'_materials.txt')
    with open(log,'w',encoding='utf-8') as f:
        f.write(f'file={path}\nmeshobjects={sum(o.type=="MESH" for o in bpy.data.objects)} materials={len(mats)}\n')
        for row in summary: f.write(repr(row)+'\n')
    setup=setup_render()
    if setup:
        bpy.ops.render.render(write_still=True)
    print('DONE',name,log)

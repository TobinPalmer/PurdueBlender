import bpy
from mathutils import Vector
from pathlib import Path

P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'))
s=bpy.context.scene; c=bpy.data.collections['Asset_hovde_hall']
s.render.engine='BLENDER_EEVEE'; s.eevee.taa_render_samples=96
s.render.resolution_x=1600; s.render.resolution_y=1000; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast'; s.view_settings.exposure=.55
root=bpy.data.objects['HOVD_Root']
port=bpy.data.objects['HOVD_Portico_Entablature'].matrix_world.translation.copy()
side=(root.matrix_world.to_3x3() @ Vector((1,0,0))).normalized()
along=(root.matrix_world.to_3x3() @ Vector((0,1,0))).normalized()
def aim(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def light(name,loc,target,power,size):
    d=bpy.data.lights.new(name,'AREA'); o=bpy.data.objects.new(name,d); s.collection.objects.link(o)
    o.location=loc; d.energy=power; d.shape='DISK'; d.size=size; aim(o,target)
    return o,d
def camera(name,loc,target,scale):
    d=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,d); s.collection.objects.link(o)
    o.location=loc; aim(o,target); d.type='ORTHO'; d.ortho_scale=scale; s.camera=o
    return o

target=port+Vector((0,0,-.3))
for args in [('R4V_Key',target+side*38+along*12+Vector((0,0,48)),target,2600,48),
             ('R4V_Fill',target-side*30-along*9+Vector((0,0,30)),target,2100,50),
             ('R4V_Rim',target+along*48+Vector((0,0,35)),target,1400,45)]: light(*args)
cam=camera('R4V_Exterior',target+side*76+along*14+Vector((0,0,26)),target,96)
s.render.filepath=str(P/'audit/batch3_hovde/exterior_round6.png'); bpy.ops.render.render(write_still=True)
# Lower and widen the facade detail shot so the complete pediment, all capitals, and stair relationship are visible.
target=port+Vector((0,0,-2.0)); cam.location=target+side*38+along*4+Vector((0,0,6)); aim(cam,target); cam.data.ortho_scale=32
s.view_settings.exposure=.65
s.render.filepath=str(P/'audit/batch3_hovde/portico_detail_round6.png'); bpy.ops.render.render(write_still=True)

# Render the interpretive office and boardroom as clean plan cutaways. Only room floor and furnishings are visible.
s.view_settings.exposure=.25
for tag,floorname in [('Pres','HOVD_Pres_Floor'),('Board','HOVD_Board_Floor')]:
    floor=bpy.data.objects[floorname]; center=floor.matrix_world.translation.copy()
    for o in c.all_objects:
        if o: o.hide_render=True
    # The imported shell also has linked scene objects outside this asset collection.
    # Hide those globally for the interior evidence, then selectively reveal the room set.
    for o in s.objects:
        if o.type not in {'CAMERA','LIGHT'}: o.hide_render=True
    for o in c.all_objects:
        if not o: continue
        n=o.name
        tokens=('Desk_','Chair_','Guest_','Chesterfield_','Interpretive_Bookcase','Bookcase_Shelf_','Book_Spine_',
                'Interpretive_Records_Credenza','Credenza_Drawer_','Fireplace_','Mantel_Clock','Rug')
        selected=(n.startswith(f'HOVD_{tag}_') and any(t in n for t in tokens))
        if tag=='Board': selected=(n==floorname or n.startswith('HOVD_Board_') and any(t in n for t in ('Table','Chair','Credenza','Book_','Wayfinding')) or n.startswith('HOVD_Chair_'))
        if selected: o.hide_render=False
        if 'Room_Wall' in n or n.endswith('_Ceiling') or 'Window' in n: o.hide_render=True
    # Some chair and room props are linked through sibling collections; reveal matching
    # named furniture across the scene as well.
    for o in s.objects:
        n=o.name
        if tag=='Pres':
            selected=(n.startswith('HOVD_Pres_') and any(t in n for t in tokens)) or n.startswith('HOVD_Chesterfield_')
        else:
            selected=(n.startswith('HOVD_Board_') and any(t in n for t in ('Table','Chair','Credenza','Book_','Wayfinding'))) or n.startswith('HOVD_Chair_')
        if selected and 'Room_Wall' not in n and not n.endswith('_Ceiling'):
            o.hide_render=False
    for o in s.objects:
        if o.type=='LIGHT': o.hide_render=True
    # Substitute a neutral temporary floor; the saved floor material is not legible in a top-down cutaway.
    mesh=bpy.data.meshes.new(f'R4V_{tag}_FloorMesh')
    verts=[(-5,-5,0),(5,-5,0),(5,5,0),(-5,5,0)]
    mesh.from_pydata(verts,[],[(0,1,2,3)]); mesh.update()
    plane=bpy.data.objects.new(f'R4V_{tag}_TemporaryFloor',mesh); s.collection.objects.link(plane)
    plane.location=center+Vector((0,0,.02))
    mat=bpy.data.materials.new(f'R4V_{tag}_TemporaryWalnut'); mat.diffuse_color=(.30,.19,.10,1)
    mat.use_nodes=True; mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.30,.19,.10,1)
    plane.data.materials.append(mat)
    d=bpy.data.lights.new('R4V_Interior_Fill','AREA'); lo=bpy.data.objects.new('R4V_Interior_Fill',d); s.collection.objects.link(lo)
    lo.location=center+Vector((1,-3,14)); d.energy=1600; d.shape='DISK'; d.size=9; aim(lo,center)
    # Top-down plan view avoids facade/wall occlusion while showing circulation and furniture placement.
    cam.location=center+Vector((0,-.5,22)); aim(cam,center); cam.data.ortho_scale=12.5
    name='presidential_office_round6.png' if tag=='Pres' else 'trustees_boardroom_round6.png'
    s.render.filepath=str(P/'audit/batch3_hovde'/name); bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(lo,do_unlink=True); bpy.data.lights.remove(d)
    bpy.data.objects.remove(plane,do_unlink=True); bpy.data.meshes.remove(mesh); bpy.data.materials.remove(mat)
print('Rendered from reopened saved asset: exterior, portico detail, office and boardroom cutaways.')




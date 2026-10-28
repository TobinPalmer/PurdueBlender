import bpy, bmesh, json, math, os
from mathutils import Vector

here=os.path.dirname(__file__)
cfg=json.load(open(os.path.join(here,'build_config.json'),encoding='utf8'))
obj=bpy.data.objects.get(cfg['object_name'])
if obj is None: raise RuntimeError('Target asset missing')
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'; scene.eevee.taa_render_samples=32
scene.render.resolution_x=1120; scene.render.resolution_y=840; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=-0.25
scene.world.color=(0.035,0.035,0.035)
verts=[obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
lo=Vector(tuple(min(v[i] for v in verts) for i in range(3)))
hi=Vector(tuple(max(v[i] for v in verts) for i in range(3)))
center=(lo+hi)*0.5; size=max(hi-lo)
cam_data=bpy.data.cameras.new('Shealy preview camera'); cam=bpy.data.objects.new('Shealy preview camera',cam_data); scene.collection.objects.link(cam)
cam_data.type='ORTHO'; cam_data.ortho_scale=size*1.46; scene.camera=cam
cam.location=center+Vector((-size*1.45,-size*1.65,size*1.05)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,area in [('Key',center+Vector((-size,-size,size*2)),size*size*0.27,size*1.2),('Fill',center+Vector((size,size*0.6,size)),size*size*0.10,size*1.5)]:
    ld=bpy.data.lights.new(name,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=area
    lo_obj=bpy.data.objects.new(name,ld); scene.collection.objects.link(lo_obj); lo_obj.location=loc
    lo_obj.rotation_euler=(center-lo_obj.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=os.path.join(here,'preview_detail.png'); bpy.ops.render.render(write_still=True)

# Supplemental roof-plan view makes the three roof wings and the flat EPDM field
# readable together where the oblique exterior view partly hides the far wing.
roof_target=Vector((center.x,center.y,hi.z-1.0))
cam.location=roof_target+Vector((0,0,size*2.2)); cam.rotation_euler=(roof_target-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.ortho_scale=size*1.23
scene.render.filepath=os.path.join(here,'preview_roof_plan.png'); bpy.ops.render.render(write_still=True)

# Find the courtyard-facing central entry edge in the source footprint, not a guessed west edge.
feature=json.load(open(os.path.join(here,cfg['source_feature_file']),encoding='utf8'))
ring=feature['geometry']['rings'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
origin_lat=40.4274; origin_lon=-86.9137
pts=[Vector(((lon-origin_lon)*111412.84*math.cos(math.radians(origin_lat)),(lat-origin_lat)*111040.0,0)) for lon,lat in ring]
area2=sum(pts[i].x*pts[(i+1)%len(pts)].y-pts[(i+1)%len(pts)].x*pts[i].y for i in range(len(pts)))
sign=1.0 if area2>0 else -1.0; edges=[]
for i,a in enumerate(pts):
    b=pts[(i+1)%len(pts)]; delta=b-a; length=delta.length
    if length>5.5:
        tangent=Vector((delta.x/length,delta.y/length,0)); normal=Vector((tangent.y,-tangent.x,0))*sign
        if normal.y < -0.9: edges.append((length,a,b,tangent,normal))
if edges:
    length,a,b,tangent,normal=max(edges,key=lambda e:e[0]); midpoint=(a+b)*0.5
    target=Vector((midpoint.x,midpoint.y,4.9))+normal*0.45
    cam.location=target+normal*12+Vector((0,0,2.6)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.ortho_scale=7.7
    scene.render.filepath=os.path.join(here,'preview_entrance.png'); bpy.ops.render.render(write_still=True)

# Roof-open cutaway: temporary copy and roof deletion; the saved library remains intact.
cut=obj.copy(); cut.data=obj.data.copy(); cut.name='Shealy interior review cutaway'; scene.collection.objects.link(cut)
bm=bmesh.new(); bm.from_mesh(cut.data)
roof_ids={i for i,m in enumerate(cut.data.materials) if m and ('EPDM_Flat_Roof' in m.name or 'Clay_Tile_Roof' in m.name)}
remove=[f for f in bm.faces if f.material_index in roof_ids]
if remove: bmesh.ops.delete(bm,geom=remove,context='FACES')
bm.to_mesh(cut.data); bm.free(); cut.data.update()
obj.hide_render=True; cut.hide_render=False
top=Vector((center.x,center.y,0)); cam.location=top+Vector((0,0,size*1.45)); cam.rotation_euler=(top-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.ortho_scale=size*1.26
scene.render.filepath=os.path.join(here,'preview_interior.png'); bpy.ops.render.render(write_still=True)

# Local interior detail view: crop one published-size room module from the unified
# asset mesh so its furniture can be inspected without implying a full floor plan.
bm=bmesh.new(); bm.from_mesh(cut.data)
tc=Vector((0.7071,0.7071,0)).normalized(); nc=Vector((-0.7071,0.7071,0)).normalized()
room=Vector((-610.0,-152.0,0)); keep=[]
for f in bm.faces:
    # Requiring every vertex to fall inside the crop avoids retaining huge triangulated
    # floor/roof polygons merely because their center happens to lie over this room.
    mat_name=cut.data.materials[f.material_index].name if f.material_index<len(cut.data.materials) else ''
    interior_detail=any(key in mat_name for key in ('Interior_Plaster','Interior_Slate_and_Tile','Quarter_Sawn_Oak','Dorm_Bed_Linen','Dorm_Furniture','Interior_Accent','Room_Carpet'))
    in_module=interior_detail
    # Open the far wall for a readable cutaway while retaining the side walls and door.
    for v in f.verts:
        rel=Vector((v.co.x-room.x,v.co.y-room.y,0))
        if not (abs(rel.dot(tc))<3.35 and abs(rel.dot(nc))<3.55 and 2.90<v.co.z<5.95):
            in_module=False; break
    if in_module and 'Interior_Plaster' in mat_name:
        c=f.calc_center_median(); rel=Vector((c.x-room.x,c.y-room.y,0))
        if rel.dot(nc)>2.2: in_module=False
    if not in_module: keep.append(f)
if keep: bmesh.ops.delete(bm,geom=keep,context='FACES')
bm.to_mesh(cut.data); bm.free(); cut.data.update()
target=room+Vector((0,0,4.35)); cam.location=target+nc*8.0+tc*1.6+Vector((0,0,5.6)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.ortho_scale=8.0
# Preview-only color/lighting boost makes the schematic furniture legible; it does not
# replace or modify the materials stored in the exported library.
preview_colors={
    'Room_Carpet':(0.025,0.04,0.045,1), 'Dorm_Bed_Linen':(0.92,0.84,0.64,1),
    'Dorm_Furniture':(0.13,0.055,0.02,1), 'Quarter_Sawn_Oak':(0.25,0.075,0.018,1),
    'Interior_Plaster':(0.66,0.57,0.42,1), 'Interior_Slate_and_Tile':(0.08,0.14,0.16,1),
    'Interior_Accent':(0.015,0.26,0.32,1)
}
for i,m in enumerate(cut.data.materials):
    if not m: continue
    color=next((v for k,v in preview_colors.items() if k in m.name),None)
    if color:
        pm=m.copy(); pm.name='Preview_'+m.name; pm.diffuse_color=color; pm.use_nodes=True
        bs=next((n for n in pm.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if bs: bs.inputs['Base Color'].default_value=color
        cut.data.materials[i]=pm
scene.world.color=(0.012,0.016,0.022)
for name,loc,power,area in [
    ('Room key',target+Vector((2.0,-3.0,7.0)),220,4.5),
    ('Room fill',target+Vector((-3.0,2.0,4.0)),85,3.5)]:
    ld=bpy.data.lights.new(name,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=area
    light=bpy.data.objects.new(name,ld); scene.collection.objects.link(light); light.location=loc
    light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
scene.view_settings.exposure=-0.4
scene.render.resolution_x=1120; scene.render.resolution_y=840
scene.render.filepath=os.path.join(here,'preview_single_room.png'); bpy.ops.render.render(write_still=True)
print('PREVIEW_RENDER='+os.path.join(here,'preview_detail.png'))

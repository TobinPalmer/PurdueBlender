import bpy, math, json, os
from mathutils import Vector

HERE=os.path.dirname(__file__)
ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301841331_735e92f.blend')
with open(os.path.join(HERE,'build_config.json'),encoding='utf8') as f: cfg=json.load(f)
bpy.ops.wm.open_mainfile(filepath=ASSET)
obj=bpy.data.objects[cfg['object_name']]
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'
world=bpy.data.worlds.new('AlphaPhi Preview World') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.58,0.64,0.72,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.55
for ob in list(scene.objects):
    if ob.type in {'CAMERA','LIGHT'}: bpy.data.objects.remove(ob,do_unlink=True)
def aim(camera,target): camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,target):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=loc; aim(ob,target)
def camera(name,loc,target,scale):
    data=bpy.data.cameras.new(name); data.type='ORTHO'; data.ortho_scale=scale
    ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=loc; aim(ob,target); scene.camera=ob
ring=json.load(open(os.path.join(HERE,cfg['source_feature_file']),encoding='utf8'))['features'][0]['geometry']['rings'][0][:-1]
R=6378137.0; lat0=cfg['coordinate_origin']['latitude']; lon0=cfg['coordinate_origin']['longitude']
pts=[]
for mx,my in ring:
    lon=mx/R*180/math.pi; lat=(2*math.atan(math.exp(my/R))-math.pi/2)*180/math.pi
    pts.append(Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0,0)))
center=sum(pts,Vector((0,0,0)))/len(pts)
target=center+Vector((0,0,4.2))
area('Large soft key',center+Vector((26,-34,45)),26000,30,target)
area('Cool fill',center+Vector((-35,-5,22)),16000,26,target)
area('Roof rim',center+Vector((5,36,32)),18000,24,target)
camera('Exterior Three Quarter',center+Vector((32,-42,27)),target,53)
scene.render.filepath=os.path.join(HERE,'exterior_three_quarter.png'); bpy.ops.render.render(write_still=True)

# Render-only full-footprint upper cutaway; this temporary object is not saved in
# the one-object building library and does not claim an as-built floor plan.
src=obj.data
interior_names={'ALPHAPHI_Interior_Bordeaux_Carpet','ALPHAPHI_Interior_Furniture','ALPHAPHI_Bed_Linen'}
preview_colors={'ALPHAPHI_Interior_Bordeaux_Carpet':(0.52,0.12,0.20,1),'ALPHAPHI_Interior_Furniture':(0.52,0.31,0.17,1),'ALPHAPHI_Bed_Linen':(1.0,0.97,0.86,1)}
for m in src.materials:
    if m and m.name in preview_colors: m.diffuse_color=preview_colors[m.name]
keep_ids={i for i,m in enumerate(src.materials) if m and m.name in interior_names}
story=cfg['estimated_wall_height_m']/2
verts=[]; faces=[]; mids=[]
for p in src.polygons:
    mat=src.materials[p.material_index] if p.material_index<len(src.materials) else None
    name=mat.name if mat else ''
    if name.startswith('ALPHAPHI_Mottled_Clay_Composite_Shingle'): continue
    if name=='ALPHAPHI_Interior_Oak_Floor': continue
    coords=[src.vertices[i].co for i in p.vertices]
    if p.material_index not in keep_ids:
        clipped=[]
        for i,v in enumerate(coords):
            w=coords[(i+1)%len(coords)]
            vin=v.z<=story; win=w.z<=story
            if vin: clipped.append(v.copy())
            if vin!=win:
                alpha=(story-v.z)/(w.z-v.z)
                clipped.append(v.lerp(w,alpha))
        coords=clipped
    if len(coords)<3: continue
    base=len(verts); verts.extend(tuple(v) for v in coords); faces.append(tuple(range(base,base+len(coords)))); mids.append(p.material_index)
preview=bpy.data.meshes.new('AlphaPhi_Full_Context_Schematic_Cutaway'); preview.from_pydata(verts,[],faces)
for m in src.materials: preview.materials.append(m)
for poly,mi in zip(preview.polygons,mids): poly.material_index=mi
preview.update(); cut=bpy.data.objects.new('Preview only — full-footprint schematic upper cutaway',preview); scene.collection.objects.link(cut)
obj.hide_render=True
for ob in list(scene.objects):
    if ob.type=='LIGHT': bpy.data.objects.remove(ob,do_unlink=True)
area('Cutaway key',center+Vector((16,-20,46)),30000,30,center+Vector((0,0,3.8)))
area('Cutaway fill',center+Vector((-28,16,34)),22000,26,center+Vector((0,0,3.8)))
camera('Full Footprint Upper Cutaway',center+Vector((26,-30,52)),center+Vector((0,0,3.6)),54)
scene.render.filepath=os.path.join(HERE,'schematic_upper_rooms.png'); bpy.ops.render.render(write_still=True)

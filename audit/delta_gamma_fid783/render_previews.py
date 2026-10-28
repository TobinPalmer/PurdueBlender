import bpy, json, math, os
from mathutils import Vector
HERE=os.path.dirname(__file__); ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301840872_582df9d.blend')
cfg=json.load(open(os.path.join(HERE,'build_config.json'),encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=ASSET)
obj=bpy.data.objects[cfg['object_name']]; scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'
world=bpy.data.worlds.new('DeltaGamma Preview World') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.52,0.59,0.67,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.62
for ob in list(scene.objects):
    if ob.type in {'CAMERA','LIGHT'}: bpy.data.objects.remove(ob,do_unlink=True)
ring=json.load(open(os.path.join(HERE,cfg['source_feature_file']),encoding='utf-8'))['features'][0]['geometry']['rings'][0][:-1]
R=6378137.0; lat0=cfg['coordinate_origin']['latitude']; lon0=cfg['coordinate_origin']['longitude']
pts=[]
for mx,my in ring:
    lon=mx/R*180/math.pi; lat=(2*math.atan(math.exp(my/R))-math.pi/2)*180/math.pi
    pts.append(Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0,0)))
center=sum(pts,Vector((0,0,0)))/len(pts)
def aim(cam,target): cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,target):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=loc; aim(ob,target)
def camera(name,loc,target,scale):
    data=bpy.data.cameras.new(name); data.type='ORTHO'; data.ortho_scale=scale
    ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=loc; aim(ob,target); scene.camera=ob
target=center+Vector((0,0,5.0))
area('Exterior soft key',center+Vector((22,-34,42)),28000,28,target)
area('Exterior fill',center+Vector((-32,-5,24)),18000,24,target)
area('Exterior rim',center+Vector((4,35,32)),18000,22,target)
camera('Delta Gamma Exterior',center+Vector((28,-42,27)),target,48)
scene.render.filepath=os.path.join(HERE,'exterior_three_quarter.png'); bpy.ops.render.render(write_still=True)

# Temporary roof-open cutaway preview: retain the full footprint perimeter,
# clip upper facade at the estimated story midpoint, and show schematic inserts.
src=obj.data; interior_names={'DELTAGAMMA_Schematic_Bordeaux_Carpet','DELTAGAMMA_Schematic_Bedding','DELTAGAMMA_Schematic_Wood_Furniture'}
keep_ids={i for i,m in enumerate(src.materials) if m and m.name in interior_names}
story=float(cfg['estimated_story_height_m']); verts=[]; faces=[]; mids=[]
for p in src.polygons:
    mat=src.materials[p.material_index] if p.material_index<len(src.materials) else None
    name=mat.name if mat else ''
    coords=[src.vertices[i].co for i in p.vertices]
    # Show the estimated upper-story floor as a useful plan surface. The
    # lower slab and roof slab are omitted from this render-only cutaway.
    if name.startswith('DELTAGAMMA_Estimated_Slate_Roof'): continue
    if name=='DELTAGAMMA_Interior_Wood_Floor':
        if abs(sum(v.z for v in coords)/len(coords)-story)>0.08: continue
        verts.extend(tuple(v) for v in coords); faces.append(tuple(range(len(verts)-len(coords),len(verts)))); mids.append(p.material_index)
        continue
    if p.material_index not in keep_ids:
        clipped=[]
        for i,v in enumerate(coords):
            w=coords[(i+1)%len(coords)]; vin=v.z<=story; win=w.z<=story
            if vin: clipped.append(v.copy())
            if vin!=win: clipped.append(v.lerp(w,(story-v.z)/(w.z-v.z)))
        coords=clipped
    if len(coords)<3: continue
    base=len(verts); verts.extend(tuple(v) for v in coords); faces.append(tuple(range(base,base+len(coords)))); mids.append(p.material_index)
preview=bpy.data.meshes.new('DeltaGamma_FullContext_Cutaway_Preview'); preview.from_pydata(verts,[],faces)
for m in src.materials: preview.materials.append(m)
for poly,mi in zip(preview.polygons,mids): poly.material_index=mi
preview.update(); cut=bpy.data.objects.new('Preview only — roof-open schematic cutaway',preview); scene.collection.objects.link(cut); obj.hide_render=True
for ob in list(scene.objects):
    if ob.type=='LIGHT': bpy.data.objects.remove(ob,do_unlink=True)
area('Cutaway key',center+Vector((16,-20,46)),29000,30,center+Vector((0,0,3.6)))
area('Cutaway fill',center+Vector((-28,16,34)),21000,26,center+Vector((0,0,3.6)))
camera('Full Footprint Cutaway',center+Vector((22,-30,54)),center+Vector((0,0,3.0)),48)
scene.render.filepath=os.path.join(HERE,'schematic_interior_cutaway.png'); bpy.ops.render.render(write_still=True)

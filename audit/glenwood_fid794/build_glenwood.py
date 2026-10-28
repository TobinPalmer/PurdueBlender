import bpy, json, math, hashlib, bmesh
from pathlib import Path
from mathutils import Vector, geometry

ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
AUD=ROOT/'audit/glenwood_fid794'
SRC=AUD/'sources'
ASSET=ROOT/'modular/buildings/massing_house_301841249_f827941.blend'
GIS=SRC/'purdue_gis_fid794_2026-10-28_4326.json'

data=json.loads(GIS.read_text(encoding='utf-8'))
feat=data['features'][0]
ring_ll=feat['geometry']['rings'][0][:-1]
ring=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring_ll]

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.context.scene
col=bpy.data.collections.get('Asset_massing_house_301841249_f827941')
if scene.name!='Building_massing_house_301841249_f827941' or col is None:
    raise RuntimeError('Expected stable scene/collection not present')
for obj in list(col.objects): bpy.data.objects.remove(obj,do_unlink=True)

xmin=min(x for x,y in ring); xmax=max(x for x,y in ring)
ymin=min(y for x,y in ring); ymax=max(y for x,y in ring)
cx=sum(x for x,y in ring)/len(ring); cy=sum(y for x,y in ring)/len(ring)

# Materials are all procedural/native. Siding gets a restrained horizontal clapboard cue.
def mat(name,color,rough=0.78,metal=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial'); p=nt.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    nt.links.new(p.outputs['BSDF'],out.inputs['Surface'])
    return m
siding=mat('Glenwood_White_Horizontal_Siding',(0.84,0.82,0.75))
nt=siding.node_tree; p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
tex=nt.nodes.new('ShaderNodeTexCoord'); wave=nt.nodes.new('ShaderNodeTexWave'); ramp=nt.nodes.new('ShaderNodeValToRGB'); bump=nt.nodes.new('ShaderNodeBump')
wave.wave_type='BANDS'; wave.bands_direction='Z'; wave.inputs['Scale'].default_value=88; wave.inputs['Distortion'].default_value=0
nt.links.new(tex.outputs['Generated'],wave.inputs['Vector'])
ramp.color_ramp.elements[0].position=0.47; ramp.color_ramp.elements[0].color=(0.77,0.76,0.71,1)
ramp.color_ramp.elements[1].position=0.56; ramp.color_ramp.elements[1].color=(0.91,0.89,0.83,1)
nt.links.new(wave.outputs['Fac'],ramp.inputs[0]); nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
bump.inputs['Strength'].default_value=0.08; bump.inputs['Distance'].default_value=0.035; nt.links.new(wave.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
white=mat('Glenwood_White_Trim',(0.94,0.92,0.86))
black=mat('Glenwood_Black_Shutters',(0.035,0.045,0.055))
brick=mat('Glenwood_Red_Brown_Foundation_Brick',(0.24,0.075,0.045))
roofmat=mat('Glenwood_Dark_Charcoal_Shingle_Roof',(0.07,0.075,0.08))
glass=mat('Glenwood_BlueGray_Window_Glass',(0.07,0.16,0.21),0.2)
purple=mat('Glenwood_Purple_Sign',(0.29,0.055,0.25),0.55)
door=mat('Glenwood_Dark_Entry_Door',(0.11,0.07,0.055))
wood=mat('Glenwood_Interior_Wood_Schematic',(0.34,0.22,0.12))
floor=mat('Glenwood_Interior_Floor_Schematic',(0.30,0.27,0.23))
partition=mat('Glenwood_Interior_Partition_Schematic',(0.74,0.68,0.58))
blue=mat('Glenwood_Interior_Furnishing_Schematic',(0.17,0.27,0.38))

created=[]
def mesh_obj(name,verts,faces,material):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.materials.append(material); me.validate(verbose=False); me.update()
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); created.append(ob); return ob
def cube(name,center,size,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    ob=bpy.context.object; ob.name=name; ob.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    col.objects.link(ob); ob.data.materials.append(material)
    if bevel:
        mod=ob.modifiers.new('Small_edge_rounding','BEVEL'); mod.width=bevel; mod.segments=2
        bpy.context.view_layer.objects.active=ob; bpy.ops.object.modifier_apply(modifier=mod.name)
    created.append(ob); return ob
def cylinder(name,center,radius,depth,material,vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=center)
    ob=bpy.context.object; ob.name=name
    for c in list(ob.users_collection): c.objects.unlink(ob)
    col.objects.link(ob); ob.data.materials.append(material); created.append(ob); return ob

# Exact source ring for the wall base; 8 unique vertices from the current FID response.
wall_h=6.35; foundation_h=0.72; eave=6.45; ridge=9.15
n=len(ring)
# Base course and upper wall masses are extrusions of the same GIS footprint.
baseverts=[(x,y,z) for x,y in ring for z in (0.0,foundation_h)]
basefaces=[tuple(range(n)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh_obj('Foundation_Brick_Course',baseverts,basefaces,brick)
wallverts=[(x,y,z) for x,y in ring for z in (foundation_h,wall_h)]
wallfaces=[tuple(range(n)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh_obj('Siding_Wall_Mass',wallverts,wallfaces,siding)

# Main gable roof over the broad house body, ridgeline along the long GIS axis.
rx0=xmin-0.45; rx1=xmax+0.25; ry0=ymin-0.35; ry1=ymax+0.08; midy=(ymin+ymax)/2
verts=[(rx0,ry0,eave),(rx1,ry0,eave),(rx1,midy,ridge),(rx0,midy,ridge),
       (rx0,midy,ridge),(rx1,midy,ridge),(rx1,ry1,eave),(rx0,ry1,eave)]
mesh_obj('Main_Gabled_Roof',verts,[(0,1,2,3),(4,5,6,7)],roofmat)
# Gable end caps are white siding over the walls, only at the two main ends.
for x,tag in [(rx0,'West'),(rx1,'East')]:
    mesh_obj('Gable_End_'+tag,[(x,ry0,wall_h),(x,ry1,wall_h),(x,midy,ridge-0.15)],[(0,1,2)],siding)

# White fascia on the two eaves and ridge, plus restrained gutters.
for tag,y in [('North',ry1),('South',ry0)]:
    cube('Roof_Fascia_'+tag,((rx0+rx1)/2,y,eave-0.06),(rx1-rx0,0.16,0.24),white,0.025)
    cube('Gutter_'+tag,((rx0+rx1)/2,y+(-0.11 if tag=='North' else 0.11),eave-0.18),(rx1-rx0,0.10,0.12),black,0.025)

# Facade presentation side is chosen for readability; compass orientation is not verified.
front_y=ymax+0.14; facade_x=(xmin+xmax)/2; mainwidth=xmax-xmin
# Vertical stacked, white-trim sash window assemblies, with black louver-like shutters.
def window(name,x,y,z,w=1.55,h=1.65,shutters=True):
    cube(name+'_Glass',(x,y,z),(w,0.09,h),glass,0.025)
    for sx in (-1,1): cube(name+'_FrameV_'+str(sx),(x+sx*(w/2+0.07),y-0.07,z),(0.13,0.14,h+0.22),white,0.015)
    for sz in (-1,1): cube(name+'_FrameH_'+str(sz),(x,y-0.07,z+sz*(h/2+0.07)),(w+0.24,0.14,0.13),white,0.015)
    cube(name+'_MullionV',(x,y-0.10,z),(0.07,0.10,h),white)
    cube(name+'_MullionH',(x,y-0.10,z),(w,0.10,0.07),white)
    if shutters:
        sw=0.38
        for sx in (-1,1):
            xx=x+sx*(w/2+0.34)
            cube(name+'_Shutter_'+str(sx),(xx,y-0.02,z),(sw,0.12,h+0.18),black,0.02)
            for k in range(5): cube(name+'_ShutterSlat_'+str(sx)+'_'+str(k),(xx,y-0.095,z-h*0.40+k*h*0.20),(sw*0.86,0.04,0.055),black)

# Seven repeated bays across the long facade on both stories, plus smaller end windows.
for floor_index,z in enumerate((1.8,4.75)):
    for i in range(7):
        x=xmin+2.3+i*(mainwidth-4.6)/6
        window('Front_Window_%d_%d'%(floor_index,i),x,front_y,z,1.45 if floor_index else 1.40,1.65 if floor_index else 1.55)
# Side elevations use a quieter two-story rhythm; positions are illustrative.
for side_x,tag in [(xmin-0.12,'West'),(xmax+0.12,'East')]:
    for floor_index,z in enumerate((1.8,4.75)):
        for j in range(3):
            y=ymin+1.8+j*(ymax-ymin-3.6)/2
            # windows are on side walls; local geometry orientation rotates 90 degrees
            ob=cube('Side_Window_'+tag+'_%d_%d'%(floor_index,j),(side_x,y,z),(0.10,1.45,1.55),glass,0.02)
            for sy in (-1,1): cube('Side_Window_Frame_Y_'+tag+'_%d_%d_%d'%(floor_index,j,sy),(side_x+(-0.08 if tag=='West' else 0.08),y+sy*0.78,z),(0.13,0.12,1.76),white,0.015)
            for sz in (-1,1): cube('Side_Window_Frame_Z_'+tag+'_%d_%d_%d'%(floor_index,j,sz),(side_x+(-0.08 if tag=='West' else 0.08),y,z+sz*0.78),(0.13,1.7,0.12),white,0.015)

# Three dormers on the photographed long elevation; their count and dimensions remain approximate.
for i,x in enumerate((xmin+5.2,xmin+13.3,xmin+21.4)):
    dy=ymax-2.0; bottom=6.70; top=8.60; width=2.75; depth=2.10
    # Front face with a triangular top and a short white dormer body.
    dfront=ymax+0.22; dback=dy-depth
    mesh_obj('Dormer_Front_%d'%i,[(x-width/2,dfront,bottom),(x+width/2,dfront,bottom),(x+width/2,dfront,7.95),(x,dfront,top),(x-width/2,dfront,7.95)],[(0,1,2,3,4)],siding)
    cube('Dormer_Sill_%d'%i,(x,dfront+0.06,bottom+0.1),(width+0.12,0.12,0.16),white,0.015)
    # Camera-facing wall is at dfront; place all window pieces fully in front
    # of the siding plane so the glazing is not occluded by the dormer face.
    window('Dormer_Window_%d'%i,x,dfront+0.34,7.44,1.22,1.10,True)
    # Two shed-like roof planes frame the modest dormer head.
    mesh_obj('Dormer_Roof_%d'%i,[(x-width/2,dfront,7.98),(x,dfront,top),(x,dback,top-0.12),(x-width/2,dback,7.98)],[(0,1,2,3)],roofmat)
    mesh_obj('Dormer_Roof_R_%d'%i,[(x,dfront,top),(x+width/2,dfront,7.98),(x+width/2,dback,7.98),(x,dback,top-0.12)],[(0,1,2,3)],roofmat)

# Main entrance portico: centered on the documented presentation facade; form based on current photo.
doorz=2.15; entry_y=front_y+0.03
cube('Front_Entry_Door',(facade_x,entry_y,doorz),(1.45,0.20,2.65),door,0.04)
for sx in (-1,1):
    x=facade_x+sx*0.98
    cube('Entry_Sidelight_'+str(sx),(x,entry_y-0.11,2.15),(0.28,0.06,2.0),glass,0.015)
# Portico columns with simple capitals, bases and entablature.
porch_y=front_y+2.15
for i,x in enumerate((facade_x-1.85,facade_x+1.85)):
    cylinder('Portico_Column_%d'%i,(x,porch_y,3.15),0.22,5.65,white,24)
    cylinder('Portico_Column_Base_%d'%i,(x,porch_y,0.38),0.34,0.25,white,24)
    cylinder('Portico_Column_Capital_%d'%i,(x,porch_y,5.95),0.34,0.25,white,24)
cube('Portico_Entablature',(facade_x,porch_y,6.12),(5.3,0.55,0.32),white,0.04)
mesh_obj('Portico_Pediment',[(facade_x-2.65,porch_y,6.24),(facade_x+2.65,porch_y,6.24),(facade_x,porch_y,7.55)],[(0,1,2)],white)
cube('Glenwood_Sign_Plaque',(facade_x,porch_y+0.72,6.72),(2.65,0.12,0.66),purple,0.045)
# Native text is converted to mesh before joining; no external font dependency.
text=bpy.data.curves.new('Glenwood_Sign_Text_Curve','FONT'); text.body='Glenwood'; text.size=0.40; text.align_x='CENTER'; text.extrude=0.008
textob=bpy.data.objects.new('Glenwood_Sign_Text',text); col.objects.link(textob); textob.location=(facade_x,porch_y+0.80,6.58); textob.rotation_euler=(math.pi/2,0,math.pi); textob.data.materials.append(white); created.append(textob)
bpy.ops.object.select_all(action='DESELECT'); textob.select_set(True); bpy.context.view_layer.objects.active=textob
bpy.ops.object.convert(target='MESH'); textob=bpy.context.view_layer.objects.active; textob.name='Glenwood_Sign_Text_Mesh'; textob.select_set(False)
# Entry landing and steps extend toward the presentation side as shown in the official image.
cube('Entry_Landing',(facade_x,front_y+3.0,0.36),(5.4,2.6,0.5),white,0.05)
for i in range(4):
    cube('Entry_Step_%d'%i,(facade_x,front_y+4.5+i*0.58,0.25-i*0.055),(5.0-i*0.45,0.62,0.25-i*0.03),white,0.025)
for sx in (-1,1):
    cube('Entry_Railing_Post_'+str(sx),(facade_x+sx*2.35,front_y+3.9,0.95),(0.10,0.10,1.35),black,0.015)
    cube('Entry_Railing_'+str(sx),(facade_x+sx*2.35,front_y+4.7,1.12),(0.10,1.8,0.10),black,0.015)

# Schematic interior floor areas, generic partitions, stairs and modest furniture.
def inset_plate(name,z,scale,material):
    mx=sum(x for x,y in ring)/n; my=sum(y for x,y in ring)/n
    pts=[Vector((mx+(x-mx)*scale,my+(y-my)*scale,0)) for x,y in ring]
    tris=geometry.tessellate_polygon([pts])
    faces=[tuple(int(i) for i in tri) for tri in tris]
    mesh_obj(name,[(p.x,p.y,z) for p in pts],faces,material)
inset_plate('Schematic_Ground_Floor',0.22,0.965,floor)
inset_plate('Schematic_Second_Floor',3.28,0.94,floor)
# Main body interior segments; elevations and room uses are not sourced.
for i,(a,b,z) in enumerate([
    ((xmin+2,ymin+3),(xmin+2,ymax-3),1.7),((xmin+8,ymin+2),(xmin+8,ymax-2),1.7),
    ((xmin+15,ymin+2),(xmin+15,ymax-2),1.7),((xmin+22,ymin+2),(xmin+22,ymax-2),1.7),
    ((xmin+1,ymin+4),(xmax-2,ymin+4),1.7),((xmin+2,ymax-4),(xmax-2,ymax-4),1.7),
    ((xmin+5,ymin+3),(xmin+5,ymax-3),4.75),((xmin+14,ymin+3),(xmin+14,ymax-3),4.75),
    ((xmin+22,ymin+3),(xmin+22,ymax-3),4.75),((xmin+2,ymin+4),(xmax-2,ymin+4),4.75)]):
    (ax,ay),(bx,by)=a,b
    length=math.hypot(bx-ax,by-ay)
    cube('Schematic_Interior_Partition_%02d'%i,((ax+bx)/2,(ay+by)/2,z),(length,0.15,2.65),partition,0.01)
# Stair treads and rails sit near the junction of the main volume and east wing.
stair_x=xmax-6.2
for i in range(11):
    cube('Schematic_Stair_Tread_%02d'%i,(stair_x,ymin+2.0+i*0.45,0.35+i*0.255),(2.2,0.52,0.13),white,0.01)
for sx in (-1,1): cube('Schematic_Stair_Rail_'+str(sx),(stair_x+sx*1.0,ymin+4.2,1.7),(0.07,5.5,0.12),wood,0.015)
# Generic tables, chairs and sleeping blocks, deliberately modest.
for name,loc,size,material in [
 ('Dining_Table',(xmin+6,ymin+5,0.82),(3.2,1.25,0.18),wood),
 ('Common_Room_Table',(xmin+18,ymin+6,0.82),(2.6,1.3,0.18),wood),
 ('Upper_Table',(xmin+10,ymax-6,3.88),(2.4,1.2,0.18),wood),
 ('Bed_A',(xmin+5,ymax-7,3.58),(2.1,1.0,0.25),blue),
 ('Bed_B',(xmin+18,ymax-7,3.58),(2.1,1.0,0.25),blue),
 ('Kitchen_Counter',(xmin+1.2,ymin+6,0.72),(0.65,5.0,0.9),partition)]:
    cube('Schematic_'+name,loc,size,material,0.035)
for i,(x,y,z) in enumerate([(xmin+4,ymin+5,0.48),(xmin+8,ymin+5,0.48),(xmin+16,ymin+6,0.48),(xmin+20,ymin+6,0.48),(xmin+8,ymax-6,3.48),(xmin+12,ymax-6,3.48)]):
    cube('Schematic_Chair_%02d'%i,(x,y,z),(0.48,0.48,0.72),blue,0.03)

# Merge every architectural piece into the stable one-mesh interface expected by the manifest.
bpy.ops.object.select_all(action='DESELECT')
for ob in list(col.objects):
    if ob.type!='MESH': raise RuntimeError('Non-mesh component remains before join: '+ob.name)
    ob.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in col.objects if o.select_get())
bpy.ops.object.join()
house=bpy.context.object; house.name='House_301841249'; house.data.name='Glenwood_503University_GIS_Footprint_Illustrative_Details'; house.select_set(False)

# Render previews with temporary cameras/lights, then remove those helpers before saving.
rcol=bpy.data.collections.new('Temporary_Render_Setup'); scene.collection.children.link(rcol)
def aim(ob,target): ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
def camera(name,loc,target,scale):
    d=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,d); rcol.objects.link(o); o.location=loc; d.type='ORTHO'; d.ortho_scale=scale; aim(o,target); scene.camera=o; return o
def light(name,loc,power,size,target):
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; o=bpy.data.objects.new(name,d); rcol.objects.link(o); o.location=loc; aim(o,target)
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=80; scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'; scene.view_settings.view_transform='AgX'
world=scene.world or bpy.data.worlds.new('Glenwood_Studio_World'); world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.22,0.25,0.29,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.30
center=(cx,cy,4.3)
light('Glenwood_Key',(cx-25,cy+30,35),1500,18,center); light('Glenwood_Fill',(cx+32,cy-15,26),500,16,center); light('Glenwood_Rim',(cx+8,cy-35,28),350,16,center)
scene.camera=camera('Glenwood_Exterior_Camera',(cx-10,ymax+35,14),center,40)
scene.render.filepath=str(AUD/'exterior_preview.png'); bpy.ops.render.render(write_still=True)
scene.camera=camera('Glenwood_Roof_Oblique_Camera',(cx-20,ymax+43,24),center,50)
scene.render.filepath=str(AUD/'roof_oblique_preview.png'); bpy.ops.render.render(write_still=True)
scene.camera=camera('Glenwood_Top_Camera',(cx,cy,76),(cx,cy,0),49)
scene.render.filepath=str(AUD/'top_preview.png'); bpy.ops.render.render(write_still=True)
# Filtered interior-only cutaway from a temporary duplicate; retain full floor plate outline.
cut=house.copy(); cut.data=house.data.copy(); cut.name='Temporary_Interior_Cutaway'; rcol.objects.link(cut)
interior_names={'Glenwood_Interior_Floor_Schematic','Glenwood_Interior_Partition_Schematic','Glenwood_Interior_Wood_Schematic','Glenwood_Interior_Furnishing_Schematic'}
allowed={i for i,m in enumerate(cut.data.materials) if m and any(s in m.name for s in interior_names)}
# Floor, divider, furniture and stair materials remain visible; exterior and roof are removed from this evidence pass.
bm=bmesh.new(); bm.from_mesh(cut.data); bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index not in allowed],context='FACES'); bm.to_mesh(cut.data); bm.free(); cut.data.update()
house.hide_render=True
old_energy=[(o,o.data.energy) for o in rcol.objects if o.type=='LIGHT']
for o,e in old_energy: o.data.energy=e*0.45
old_world_strength=world.node_tree.nodes['Background'].inputs['Strength'].default_value
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.18
scene.camera=camera('Glenwood_Interior_Cutaway_Camera',(cx-21,ymax+34,30),(cx,cy,1.6),45)
scene.render.filepath=str(AUD/'schematic_interior_cutaway.png'); bpy.ops.render.render(write_still=True)
for o,e in old_energy: o.data.energy=e
world.node_tree.nodes['Background'].inputs['Strength'].default_value=old_world_strength
house.hide_render=False; bpy.data.objects.remove(cut,do_unlink=True)
for ob in list(rcol.objects): bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.collections.remove(rcol); scene.camera=None; scene.render.filepath='//'
# Remove unused preview image datablocks; all model materials are procedural.
for im in list(bpy.data.images):
    if im.users==0: bpy.data.images.remove(im)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('SAVED',ASSET)
print('RING_VERTICES',n,'WORLD_BOUNDS',xmin,xmax,ymin,ymax,'HEIGHT',ridge,'OBJECTS',len(col.objects))

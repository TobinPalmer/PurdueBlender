import bpy, math, json, os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

BLEND=r'modular/buildings/massing_house_301841248_fe939c7.blend'
OUT=r'audit/alpha_xi_delta_fid788'
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene=bpy.context.scene
root=bpy.data.collections.get('Asset_massing_house_301841248_fe939c7')
house=bpy.data.objects['House_301841248']
# Build from the official FID 788 ring using the project local approximation.
with open(OUT+'/source_fid788.json','r',encoding='utf-8-sig') as f: source_packet=json.load(f)
source_ring=source_packet['features'][0]['geometry']['rings'][0][:-1]
pts=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in source_ring]
n=len(pts); xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
x0,x1=min(xs),max(xs); y0,y1=min(ys),max(ys); cx,cy=(x0+x1)/2,(y0+y1)/2
signed_area=sum(pts[i][0]*pts[(i+1)%n][1]-pts[(i+1)%n][0]*pts[i][1] for i in range(n))/2

# clear all objects from the one-building asset except its stable root object
for ob in list(root.objects):
    if ob!=house:
        bpy.data.objects.remove(ob,do_unlink=True)
# remove stray scene objects if any, while leaving other data blocks untouched
for ob in list(scene.objects):
    if ob!=house:
        bpy.data.objects.remove(ob,do_unlink=True)

def mat(name, color, rough=.78, metallic=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metallic
    return m
brick=mat('AXiD • warm red-brown brick',(0.30,.12,.075))
cream=mat('AXiD • ivory plaster',(0.79,.73,.62))
timber=mat('AXiD • dark Tudor timber',(.085,.042,.02))
roofmat=mat('AXiD • charcoal slate',(.035,.045,.065),.7)
glass=mat('AXiD • blue-gray glass',(.12,.27,.38),.26)
frame=mat('AXiD • cream window trim',(.88,.83,.72))
wood=mat('AXiD • warm interior wood',(.38,.22,.12))
lightwood=mat('AXiD • floor and stair wood',(.58,.39,.22))
wallmat=mat('AXiD • interior plaster',(.59,.54,.46))
stone=mat('AXiD • limestone',(.65,.59,.49))
blue=mat('AXiD • chapter blue',(.04,.16,.34),.4)
gold=mat('AXiD • chapter gold',(.83,.63,.16),.45,.15)
white=mat('AXiD • warm white',(.91,.87,.79))

# helper build mesh from verts/faces, coords in campus frame
def mesh_obj(name, verts, faces, material, coll=root):
    me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(name,me); coll.objects.link(ob)
    return ob

def box(name, loc, scale, material, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob=bpy.context.object; ob.name=name; ob.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if ob.name not in root.objects: root.objects.link(ob)
    for c in list(ob.users_collection):
        if c!=root: c.objects.unlink(ob)
    ob.data.materials.append(material)
    if bevel:
        mod=ob.modifiers.new('Soft architectural edges','BEVEL'); mod.width=bevel; mod.segments=2
        ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return ob

def extruded(name,zlo,zhi,material):
    verts=[(x,y,zlo) for x,y in pts]+[(x,y,zhi) for x,y in pts]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh_obj(name,verts,faces,material)

# Remodel the stable base object as the lower brick story, leaving stable collection and object ID intact.
oldmat=house.data.materials[:]
me=bpy.data.meshes.new('House_301841248_LowerBrickMesh')
verts=[(x,y,z) for z in (0,3.75) for x,y in pts]
faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
me.from_pydata(verts,[],faces); me.materials.append(brick); me.update()
house.data=me; house.name='House_301841248'; house['building_id']='massing_house_301841248_fe939c7'; house['role']='Source-footprint lower brick story'; house['outline_source']='Purdue GIS BuildingShapesZip4 FID 788; 24 unique GIS vertices transformed with project local approximation.';
upper=extruded('AXiD_Upper_Tudor_Story',3.75,7.35,cream); upper['role']='Upper story massing inferred from exterior photography';
# Main interior floors visible in cutaway
for z in (0.12,3.72,7.28):
    ob=extruded('AXiD_FloorSlab_'+str(z).replace('.','_'),z,z+.12,lightwood if z>0 else stone)
    ob['role']='Schematic floor plate; internal plan is not documented'
# Estimated roof wings follow the source outline's articulated plan. Heights and pitches are inferred.
def gable_wing(name,xa,xb,ya,yb,eave,ridge,axis='X'):
    if axis=='X':
        v=[(xa,ya,eave),(xb,ya,eave),(xb,yb,eave),(xa,yb,eave),(xa,(ya+yb)/2,ridge),(xb,(ya+yb)/2,ridge)]
        f=[(0,1,5,4),(4,5,2,3),(0,4,3),(1,2,5),(0,3,2,1)]
    else:
        v=[(xa,ya,eave),(xb,ya,eave),(xb,yb,eave),(xa,yb,eave),((xa+xb)/2,ya,ridge),((xa+xb)/2,yb,ridge)]
        f=[(0,1,4),(1,2,5,4),(4,5,3),(0,4,5,3),(0,3,2,1)]
    ob=mesh_obj(name,v,f,roofmat); ob.modifiers.new('Slate thickness','SOLIDIFY').thickness=.18; return ob
roof=mesh_obj('AXiD_DarkSlate_GabledRoof',[],[],roofmat)
# Main south wing, north return and east return create a stepped roofline.
roof_parts=[gable_wing('AXiD_RoofWing_Front',x0,x1,y0,y0+12.0,7.35,9.65,'X'),gable_wing('AXiD_RoofWing_North',x0+5.0,x1,y1-6.0,y1,7.35,9.70,'X'),gable_wing('AXiD_RoofWing_East',x1-6.0,x1,y0+10.0,y1-5.5,7.35,9.50,'Y'),gable_wing('AXiD_RoofWing_Northwest',x0,x0+5.6,y1-4.3,y1,7.35,9.20,'X')]
bpy.data.objects.remove(roof,do_unlink=True)

# Continuous dark roof field closes the unsupported central roof gap while the articulated wings remain visible above it.
cover_verts=[(x0-.9,y0-.9,7.43),(x1+.9,y0-.9,7.43),(x1+.9,y1+.9,7.43),(x0-.9,y1+.9,7.43)]
roof_cover=mesh_obj('AXiD_Roof_Continuity_Cover',cover_verts,[(0,1,2,3)],roofmat); roof_cover['role']='Continuous estimated roof deck beneath the articulated gabled wings; closes the prior unsupported open roof gap'

# Nearly flush windows are placed on real straight GIS boundary segments.
def window_edge(name,center,z,width,height,angle,outward):
    nrm=Vector((outward[0],outward[1],0)); tangent=Vector((math.cos(angle),math.sin(angle),0)); c=Vector((center[0],center[1],z))
    def fitted(label,pos,dims,material):
        ob=box(name+'_'+label,(pos.x,pos.y,pos.z),dims,material,.01); ob.rotation_euler[2]=angle
    fitted('Glass',c+nrm*.005,(width,.04,height),glass)
    for side in (-1,1): fitted('Jamb',c+nrm*.024+tangent*side*(width/2+.06),(.12,.06,height+.18),frame)
    for dz in (-height/2-.07,height/2+.07): fitted('SillHead',c+nrm*.024+Vector((0,0,dz)),(width+.23,.06,.12),frame)
    fitted('Mullion',c+nrm*.035,(.055,.06,height),frame); fitted('Crossbar',c+nrm*.035,(width,.06,.055),frame)
edges=[]
for i,a in enumerate(pts):
    b=pts[(i+1)%n]; edges.append((math.hypot(b[0]-a[0],b[1]-a[1]),a,b,math.atan2(b[1]-a[1],b[0]-a[0])))
front_edge=max((e for e in edges if abs(e[2][1]-e[1][1])<.25),key=lambda e:e[0]); front_length,front_a,front_b,front_angle=front_edge
entry_point=((front_a[0]+front_b[0])/2,(front_a[1]+front_b[1])/2); front_out=(0,-1) if signed_area<0 else (0,1)
for ei,(length,a,b,angle) in enumerate(edges):
    if length<5.2: continue
    count=max(1,int(length//4.8)); tangent=(math.cos(angle),math.sin(angle)); left=(-tangent[1],tangent[0]); outward=left if signed_area<0 else (-left[0],-left[1])
    for j in range(count):
        t=(j+1)/(count+1); center=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
        if ei==edges.index(front_edge) and math.dist(center,entry_point)<2.0: continue
        window_edge('AXiD_Window_L%02d_%02d'%(ei,j),center,2.15,1.42,1.52,angle,outward)
        window_edge('AXiD_Window_U%02d_%02d'%(ei,j),center,5.35,1.42,1.52,angle,outward)
# Tudor framing follows the actual south/front wall segment, not the whole bounding box.
normal=Vector((front_out[0],front_out[1],0)); facade_tangent=Vector((math.cos(front_angle),math.sin(front_angle),0))
def front_bar(name,t,z,w,h,d=.17):
    p=Vector((front_a[0]+(front_b[0]-front_a[0])*t,front_a[1]+(front_b[1]-front_a[1])*t,z))+normal*.04
    ob=box(name,(p.x,p.y,p.z),(w,d,h),timber,.025); ob.rotation_euler[2]=front_angle; return ob
for z in (3.8,4.02,7.22): front_bar('Tudor_Front_Band',.5,z,front_length,.18,.22)
for j in range(6): front_bar('Tudor_Front_Post_%02d'%j,.03+j*.94/5,5.5,.18,3.35,.22)
for t in (.18,.38,.62,.82):
    ob=front_bar('Tudor_Front_Diagonal',t,5.45,.15,1.3,.22); ob.rotation_euler[0]=math.radians(45)

# Entry, stone surround, signage and steps center on the long south/front wall.
entry_x,entry_y=entry_point; porch=Vector((entry_x,entry_y,0))+normal*1.0
box('AXiD_EntryPorchRoof',(porch.x,porch.y,4.05),(4.7,2.25,.28),timber,.06)
for side in (-1,1):
    p=Vector((entry_x,entry_y,2.0))+normal*.95+facade_tangent*side*1.95; box('AXiD_PorticoPost',(p.x,p.y,p.z),(.28,.28,4.0),stone,.04)
p=Vector((entry_x,entry_y,1.55))+normal*.04
door=box('AXiD_EntryDoor',(p.x,p.y,p.z),(1.55,.16,2.65),wood,.04); door.rotation_euler[2]=front_angle
panel=box('AXiD_EntryDoorPanel',(p.x+normal.x*.08,p.y+normal.y*.08,p.z),(1.12,.06,2.15),timber,.03); panel.rotation_euler[2]=front_angle
for side in (-1,1):
    p=Vector((entry_x,entry_y,1.8))+normal*.07+facade_tangent*side*.9; ob=box('AXiD_StoneJamb',(p.x,p.y,p.z),(.22,.30,3.05),stone,.04); ob.rotation_euler[2]=front_angle
p=Vector((entry_x,entry_y,3.32))+normal*.07; ob=box('AXiD_StoneLintel',(p.x,p.y,p.z),(2.02,.30,.28),stone,.04); ob.rotation_euler[2]=front_angle
for i in range(6):
    z=.25+i*.28; d=(i+1)*.48; p=Vector((entry_x,entry_y,0))+normal*(1.1+d/2); ob=box('AXiD_EntryStep_%02d'%i,(p.x,p.y,z),(3.2,d,.25),stone,.04); ob.rotation_euler[2]=front_angle
bpy.ops.object.text_add(location=(entry_x-2.2,entry_y+normal.y*.13,3.78),rotation=(math.radians(90),0,front_angle))
t=bpy.context.object; t.name='AXiD_ChapterSign_Text'; t.data.body='ALPHA XI DELTA  •  ALPHA ETA'; t.data.size=.36; t.data.extrude=.012; t.data.materials.append(blue); root.objects.link(t)
for c in list(t.users_collection):
    if c!=root: c.objects.unlink(t)
t['role']='Official chapter text; exact sign dimensions/position are illustrative'
bpy.ops.object.text_add(location=(entry_x+3.6,entry_y+normal.y*.14,5.6),rotation=(math.radians(90),0,front_angle))
g=bpy.context.object; g.name='AXiD_GreekLetters'; g.data.body='ΑΞΔ'; g.data.size=.85; g.data.extrude=.018; g.data.materials.append(gold); root.objects.link(g)
for c in list(g.users_collection):
    if c!=root: c.objects.unlink(g)
for j,x in enumerate((x0+5.2,cx,x1-5.2)):
    yf=y0+2.05; yb=y0+3.75; zb=7.42; ze=8.72; zr=9.55
    box('AXiD_Dormer_%d'%j,(x,(yf+yb)/2,(zb+ze)/2),(2.6,yb-yf,ze-zb),cream,.035)
    box('AXiD_DormerWindow_%d'%j,(x,yf-.015,zb+.68),(1.22,.04,1.0),glass,.015)
    for xx in (x-.69,x+.69): box('AXiD_DormerJamb_%d'%j,(xx,yf-.035,zb+.68),(.12,.07,1.15),frame,.012)
    for zz in (zb+.10,zb+1.25): box('AXiD_DormerHeadSill_%d'%j,(x,yf-.035,zz),(1.5,.07,.12),frame,.012)
    mesh_obj('AXiD_DormerGable_%d'%j,[(x-1.3,yf,ze),(x+1.3,yf,ze),(x,yf,zr)],[(0,1,2)],timber)
    dr=[(x-1.35,yf,ze),(x+1.35,yf,ze),(x+1.35,yb,ze),(x-1.35,yb,ze),(x,yf,zr),(x,yb,zr)]
    ob=mesh_obj('AXiD_DormerRoof_%d'%j,dr,[(0,4,5,3),(4,1,2,5)],roofmat); ob.modifiers.new('Dormer slate thickness','SOLIDIFY').thickness=.12

# schematic interior: lobby/common room and generic partitions/furniture, intentionally not a claimed surveyed plan
for y in (cy-4.4,cy+4.4):
    box('Interior_Partition_Lower',(cx,y,2.0),(x1-x0-3.0,.13,3.65),wallmat,.02)
    box('Interior_Partition_Upper',(cx,y,5.55),(x1-x0-3.0,.13,3.2),wallmat,.02)
# cross walls make generic rooms; leave front door axis open
for x in (cx-5.0,cx+5.0):
    box('Interior_CrossWall_Lower',(x,cy,2.0),(.13,y1-y0-3.0,3.65),wallmat,.02)
    box('Interior_CrossWall_Upper',(x,cy,5.55),(.13,y1-y0-3.0,3.2),wallmat,.02)
# lobby floor entry rug and living/dining pieces
box('Interior_Lobby_Rug',(cx,cy,0.30),(5.0,6.0,.08),blue,.03)
box('Interior_DiningTable',(cx+3.0,cy+6.0,4.08),(4.0,2.0,.16),wood,.06)
for x in (cx+1.3,cx+4.7):
    for y in (cy+4.8,cy+7.2): box('Interior_DiningChair',(x,y,3.55),(.7,.7,1.0),lightwood,.06)
box('Interior_LoungeTable',(cx-3.0,cy-5.5,4.08),(2.5,1.2,.15),wood,.05)
for xx,yy in ((cx-4.8,cy-5.5),(cx-1.2,cy-5.5)):
    box('Interior_LoungeSeat',(xx,yy,4.65),(1.2,.9,.8),blue,.10)
# Ground-level common lounge/dining furniture; placement is schematic, not a recovered floorplan.
box('Interior_GroundDiningTable',(cx+3.0,cy-5.6,.82),(4.0,2.0,.16),wood,.06)
for x in (cx+1.3,cx+4.7):
    for y in (cy-6.8,cy-4.4): box('Interior_GroundDiningChair',(x,y,.48),(.7,.7,.8),lightwood,.06)
box('Interior_GroundLoungeSeat',(cx-3.0,cy+6.0,.72),(3.0,1.0,.8),blue,.10)
box('Interior_GroundLoungeTable',(cx-3.0,cy+4.2,.56),(2.1,1.1,.12),wood,.04)

# stair stack visible in cutaway, along entry-to-interior axis
for i in range(12):
    box('Interior_StairStep_%02d'%i,(cx-5.6+i*.30,cy,4.0+i*.28),(.42,1.55,.17),lightwood,.02)
# upper corridor/bedroom beds are schematic
for xx,yy in ((cx-5.0,cy-8.0),(cx+5.0,cy+8.0)):
    box('Interior_UpperBed',(xx,yy,7.48),(2.1,3.0,.25),white,.06)
    box('Interior_UpperHeadboard',(xx,yy-1.35,7.85),(2.2,.18,.65),wood,.04)

# Combine repetitive trim assemblies to keep the export collection compact.
def join_prefix_groups(name,prefixes):
    members=[o for o in list(root.objects) if any(o.name.startswith(p) for p in prefixes)]
    if not members: return None
    names=[o.name for o in members]
    for nm in names:
        ob=bpy.data.objects.get(nm)
        bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
        if ob.type!='MESH': bpy.ops.object.convert(target='MESH')
        elif ob.modifiers: bpy.ops.object.convert(target='MESH')
    objects=[bpy.data.objects.get(nm) for nm in names if bpy.data.objects.get(nm) is not None]
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects: ob.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.join(); objects[0].name=name
    return objects[0]
join_prefix_groups('AXiD_WindowAssemblies',['AXiD_Window_'])
join_prefix_groups('AXiD_TudorTimber',['Tudor_'])
join_prefix_groups('AXiD_RoofWings',['AXiD_RoofWing_'])
join_prefix_groups('AXiD_Dormers',['AXiD_Dormer'])
join_prefix_groups('AXiD_EntryAssembly',['AXiD_Entry','AXiD_PorticoPost','AXiD_Stone','AXiD_ChapterSign','AXiD_GreekLetters'])
join_prefix_groups('Interior_GroundFloorFurniture',['Interior_Ground','Interior_Lobby_Rug'])
join_prefix_groups('Interior_GroundFloorPartitions',['Interior_Partition_Lower','Interior_CrossWall_Lower'])
join_prefix_groups('Interior_UpperFloorPartitions',['Interior_Partition_Upper','Interior_CrossWall_Upper'])

# Render previews in a temporary Workbench context; camera and backdrop are removed before the library is saved.
def aim(ob,target): ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
camdata=bpy.data.cameras.new('AXiD_TemporaryPreviewCamera'); cam=bpy.data.objects.new('AXiD_TemporaryPreviewCamera',camdata); scene.collection.objects.link(cam)
cam.location=(x1+38,y0-40,25); aim(cam,(cx,cy,4.5)); camdata.lens=54; scene.camera=cam
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'; scene.display.shading.studio_light='paint.sl'; scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True; scene.display.shading.cavity_type='WORLD'
scene.display.shading.curvature_ridge_factor=1.3; scene.display.shading.curvature_valley_factor=1.0
scene.display.shading.background_type='VIEWPORT'; scene.display.shading.background_color=(.46,.50,.55); scene.display.shading.show_specular_highlight=False
# Workbench uses diffuse colors; brighten only those preview colors while preserving shader materials.
for m in (brick,cream,timber,roofmat,glass,frame,wood,lightwood,wallmat,stone,blue,gold,white):
    c=m.diffuse_color; m.diffuse_color=(min(c[0]*1.25,1),min(c[1]*1.25,1),min(c[2]*1.25,1),1)
scene.render.resolution_x=1500; scene.render.resolution_y=1125; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.render.filepath=os.path.abspath(OUT+'/exterior_preview.png')
# Keep schematic contents below the roof cover so they cannot read as a roof opening in the exterior view.
for ob in list(root.objects):
    if ob.name.startswith('Interior_UpperBed') or ob.name.startswith('Interior_UpperHeadboard'):
        bpy.data.objects.remove(ob,do_unlink=True)
for ob in root.objects: ob.hide_render=ob.name.startswith('Interior_')
bpy.ops.render.render(write_still=True)
for ob in root.objects: ob.hide_render=False
# The cutaway intentionally shows one schematic floor only; it is not an as-built plan.
for ob in scene.objects: ob.hide_render=True
keep={'Interior_GroundFloorFurniture','Interior_GroundFloorPartitions'}
for ob in scene.objects:
    if ob.name in keep or ob.name.startswith('Interior_GroundFloor'): ob.hide_render=False
cam.location=(cx,cy,70); aim(cam,(cx,cy,.5)); camdata.type='ORTHO'; camdata.ortho_scale=47
# Preview-only caption makes the unverified interior status explicit in the image itself.
label_curve=bpy.data.curves.new('AXiD_SchematicCaption','FONT'); label_curve.body='SCHEMATIC INTERIOR - NOT AN AS-BUILT PLAN'; label_curve.size=.82; label_curve.extrude=.006
label_obj=bpy.data.objects.new('AXiD_SchematicCaption',label_curve); scene.collection.objects.link(label_obj); label_obj.location=(x0+.8,y1+2.5,.15); label_obj.hide_render=False
labelmat=mat('AXiD - preview caption',(.08,.10,.14)); label_curve.materials.append(labelmat)
scene.render.filepath=os.path.abspath(OUT+'/interior_cutaway_preview.png'); bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(label_obj,do_unlink=True)
if label_curve.users==0: bpy.data.curves.remove(label_curve)
# Clear temporary visibility state and remove all preview-only scene objects from the saved asset.
for ob in root.objects: ob.hide_render=False
scene.camera=None
for ob in (cam,): bpy.data.objects.remove(ob,do_unlink=True)
if camdata.users==0: bpy.data.cameras.remove(camdata)
# Keep the exported manifest contract: one stable root object in the named collection.
# The cutaway preview above is rendered from this complete scene before merging.
for ob in list(root.objects):
    ob.select_set(False)
for ob in list(root.objects): ob.select_set(True)
bpy.context.view_layer.objects.active=house
bpy.ops.object.join()
house.name='House_301841248'; house.data.name='AXiD_CompleteExteriorAndSchematicInteriorMesh'
house['asset_contract']='Single mesh object in the named asset collection to match the current shared manifest object_count=1.'
house['interior_representation']='Schematic only; not an as-built floor plan. See interior_cutaway_preview.png.'
house['roof_transition']='Continuous roof cover closes previous unsupported central opening; gabled wings and three dormers remain estimated from available visual sources.'
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('SAVED',BLEND,'POINTS',n,'BOUNDS',(x0,x1,y0,y1),'ASSET_OBJECTS',len(root.objects),'SCENE_OBJECTS',len(scene.objects))







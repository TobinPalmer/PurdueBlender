import bpy, bmesh, math, json
from mathutils import Vector
src=bpy.data.filepath
assert src.lower().endswith('krach_leadership_center.blend'), src
shell=bpy.data.objects['KRCH structural shell | GIS outline']
facade=bpy.data.collections['Facade_Details']
interior=bpy.data.collections['Schematic_Interior']
structure=bpy.data.collections['Structure']

# Preserve the exact simplified GIS ring already in this source, then recreate the shell before applying the corrected, photo-supported openings.
base_poly=next(p for p in shell.data.polygons if all(abs(shell.data.vertices[i].co.z+1.0)<1e-4 for i in p.vertices))
ring=[shell.data.vertices[i].co.copy() for i in base_poly.vertices]
top_z=max(v.co.z for v in shell.data.vertices if v.co.z>15.0)
N=len(ring); verts=[(v.x,v.y,-1.0) for v in ring]+[(v.x,v.y,top_z) for v in ring]
faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
for i in range(N): faces.append((i,(i+1)%N,(i+1)%N+N,i+N))
mesh=bpy.data.meshes.new('KRCH GIS ring | four-story brick shell')
mesh.from_pydata(verts,[],faces); mesh.update()
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(mesh); bm.free()
for m in shell.data.materials:
 if m: mesh.materials.append(m)
old=shell.data; shell.data=mesh; bpy.data.meshes.remove(old)
shell['geometry']='Rebuilt from unchanged simplified official GIS ring and existing estimated wall height; facade openings added only where source imagery supports glazing.'

# Remove broad generic overlays and the previous center-mounted window/stair treatment. These conflicted with the published photos.
remove_prefixes=[
 'Continuous horizontal facade banding','Curtainwall vertical mullions','Facade glazing | repeated vision panels',
 'Krach glazed stair tower','Krach pale vertical facade pier','Krach main entrance canopy',
 'Krach Leadership | canopy column','Krach Leadership | entrance name panel','Krach Leadership | entry canopy',
 'Krach Leadership | entry step','Krach Leadership | glazed entrance doors','Krach Leadership | left stone entry pier','Krach Leadership | right stone entry pier',
 'KRCH four-level collaboration window','KRCH full-height limestone cadence | pier','KRCH documented fourth-floor slab',
 'KRCH open stair | handrail segment','KRCH open stair | 4-floor lobby flights and etched glass balustrade',
 'Schematic interior floor plate 0','KRACH_LEADERSHIP_CENTER | schematic interior monitor','KRACH_LEADERSHIP_CENTER | schematic interior table support','KRACH_LEADERSHIP_CENTER | schematic interior work table',
 'KRACH_LEADERSHIP_CENTER | low planter planting','KRACH_LEADERSHIP_CENTER | schematic entry planter','KRACH_LEADERSHIP_CENTER | schematic entry walk','KRCH | occupied lounge table'
]
for o in list(bpy.data.objects):
 if any(o.name.startswith(p) for p in remove_prefixes): bpy.data.objects.remove(o,do_unlink=True)

# Local, dependency-free materials in the established Purdue brick/limestone/glass palette.
def mat(name,color,rough=0.55,metal=0.0,alpha=1.0,trans=0.0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
 m.diffuse_color=(*color,alpha); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF')
 if bs:
  bs.inputs['Base Color'].default_value=(*color,alpha); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
  bs.inputs['Alpha'].default_value=alpha
  if 'Transmission Weight' in bs.inputs: bs.inputs['Transmission Weight'].default_value=trans
  if 'IOR' in bs.inputs: bs.inputs['IOR'].default_value=1.45
 if alpha<1: m.surface_render_method='DITHERED'
 return m
stone=mat('KRCH | Sasaki photo-backed pale limestone frame',(0.72,0.69,0.60),0.52)
frame=mat('KRCH | dark bronze-gray facade mullion',(0.13,0.15,0.15),0.35,0.45)
glass=mat('KRCH | clear blue-gray lobby glazing',(0.23,0.38,0.41),0.1,0.0,0.22,0.18)
brick=bpy.data.materials.get('KRACH_LEADERSHIP_CENTER | evidence palette textured masonry')
if brick: shell.data.materials.clear(); shell.data.materials.append(brick)

# Helpers: disconnected solids are grouped into one mesh to keep the modular asset light.
def add_boxes_mesh(name, specs, material, col):
 vv=[]; ff=[]
 for (cx,cy,cz),(sx,sy,sz) in specs:
  k=len(vv)
  vv.extend([(cx-sx/2,cy-sy/2,cz-sz/2),(cx+sx/2,cy-sy/2,cz-sz/2),(cx+sx/2,cy+sy/2,cz-sz/2),(cx-sx/2,cy+sy/2,cz-sz/2),(cx-sx/2,cy-sy/2,cz+sz/2),(cx+sx/2,cy-sy/2,cz+sz/2),(cx+sx/2,cy+sy/2,cz+sz/2),(cx-sx/2,cy+sy/2,cz+sz/2)])
  ff.extend([(k+0,k+3,k+2,k+1),(k+4,k+5,k+6,k+7),(k+0,k+1,k+5,k+4),(k+1,k+2,k+6,k+5),(k+2,k+3,k+7,k+6),(k+3,k+0,k+4,k+7)])
 me=bpy.data.meshes.new(name+' mesh'); me.from_pydata(vv,[],ff); me.materials.append(material); me.update()
 ob=bpy.data.objects.new(name,me); col.objects.link(ob); ob['building_id']='krach_leadership_center'; return ob

def add_panel(name,center,dims,material):
 return add_boxes_mesh(name,[(center,dims)],material,facade)

# Photo-supported south / Third Street facade apertures: wraparound multilevel lobby bay,
# first-floor transparent Main Street, and discrete upper-floor windows in brick/stone.
# Aperture boxes extend through the front wall but do not alter GIS perimeter coordinates.
cut_specs=[]
def cutter(center,dims): cut_specs.append((center,dims))
# Four-story corner glass bay estimated from Sasaki's corner view.
cutter((-17.45,-14.0,7.25),(8.8,2.6,15.5))
# Street-facing first-floor Main Street / public lobby storefront along long wing.
cutter((9.15,-14.0,1.48),(44.0,2.6,2.96))
# Repeated punched upper-floor windows with limestone reveals.
upper_x=[-31.0,-26.0,-9.2,-3.6,2.0,7.6,13.2,18.8,24.4,30.0]
window_levels=[4.88,8.78,12.68]
# Two west-side bays retain first-floor punched glazing; the street-facing east wing is storefront.
for x in upper_x:
 for z in ([1.38]+window_levels if x<-20 else window_levels): cutter((x,-14.0,z),(1.52,2.6,1.9))
cutmesh=bpy.data.meshes.new('KRCH photo-backed south facade apertures | temporary')
vv=[]; ff=[]
for (cx,cy,cz),(sx,sy,sz) in cut_specs:
 k=len(vv); vv.extend([(cx-sx/2,cy-sy/2,cz-sz/2),(cx+sx/2,cy-sy/2,cz-sz/2),(cx+sx/2,cy+sy/2,cz-sz/2),(cx-sx/2,cy+sy/2,cz-sz/2),(cx-sx/2,cy-sy/2,cz+sz/2),(cx+sx/2,cy-sy/2,cz+sz/2),(cx+sx/2,cy+sy/2,cz+sz/2),(cx-sx/2,cy+sy/2,cz+sz/2)])
 ff.extend([(k+0,k+3,k+2,k+1),(k+4,k+5,k+6,k+7),(k+0,k+1,k+5,k+4),(k+1,k+2,k+6,k+5),(k+2,k+3,k+7,k+6),(k+3,k+0,k+4,k+7)])
cutmesh.from_pydata(vv,[],ff); cut=bpy.data.objects.new('TEMP | facade opening cutters',cutmesh); bpy.context.scene.collection.objects.link(cut)
bpy.ops.object.select_all(action='DESELECT'); shell.select_set(True); bpy.context.view_layer.objects.active=shell
mod=shell.modifiers.new('Photo-backed street facade openings','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cut
bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cut,do_unlink=True)
shell['facade_evidence']='Sasaki exterior project photograph: https://www.sasaki.com/wp-content/uploads/2019/10/01-Krach_CornerView_2014_8789-1800x1200.jpg ; project description identifies first-floor Main Street transparency. Repeated upper windows and corner bay are interpreted from the photo.'

# Window walls and surrounds are set slightly proud of the opened brick face, with panes just inside the limestone/bronze frames.
# Continuous lower glazing on the street-facing wing, divided by slender bronze-gray mullions.
store_x0=-12.85; store_x1=31.15; store_z0=0.02; store_z1=2.96
panes=[]; mullions=[]; stone_parts=[]
span=4.4; n=int(math.ceil((store_x1-store_x0)/span)); panelw=(store_x1-store_x0)/n
for i in range(n):
 cx=store_x0+(i+0.5)*panelw
 panes.append(((cx,-13.88,(store_z0+store_z1)/2),(panelw-0.09,0.07,store_z1-store_z0-0.04)))
 if i>0: mullions.append(((store_x0+i*panelw,-14.22,(store_z0+store_z1)/2),(0.075,0.14,store_z1-store_z0)))
# low sill/transom and head divide the transparent first floor as shown in reference photos
mullions.extend([(( (store_x0+store_x1)/2,-14.22,0.12),(store_x1-store_x0,0.14,0.10)),(((store_x0+store_x1)/2,-14.22,2.88),(store_x1-store_x0,0.14,0.12)),(((store_x0+store_x1)/2,-14.22,1.45),(store_x1-store_x0,0.14,0.075))])
add_boxes_mesh('KRCH | transparent Main Street ground-floor storefront',panes,glass,facade)
add_boxes_mesh('KRCH | Main Street storefront dark mullions and transoms',mullions,frame,facade)

# Four-story glazed lobby/stair bay at the photographed corner. Floor-level transoms give the visible four-story rhythm.
bay_x0=-21.85; bay_x1=-13.05; bay_y=-14.18; bay_z0=0.0; bay_z1=15.2
bay_specs=[]
for story,z0 in enumerate([0.0,3.9,7.8,11.7]):
 for panel in range(3):
  cx=bay_x0+(panel+0.5)*(bay_x1-bay_x0)/3
  bay_specs.append(((cx,bay_y,z0+1.90),((bay_x1-bay_x0)/3-0.08,0.07,3.75)))
add_boxes_mesh('KRCH | 4-story corner lobby curtainwall panes',bay_specs,glass,facade)
bay_frames=[]
for i in range(4):
 x=bay_x0+i*(bay_x1-bay_x0)/3
 bay_frames.append(((x,-14.29,(bay_z0+bay_z1)/2),(0.17,0.22,bay_z1-bay_z0)))
bay_frames += [((bay_x0,-14.29,7.6),(0.22,0.22,15.2)),((bay_x1,-14.29,7.6),(0.22,0.22,15.2))]
for z in [0.12,3.84,7.74,11.64,15.08]: bay_frames.append((((bay_x0+bay_x1)/2,-14.29,z),(bay_x1-bay_x0,0.22,0.16)))
add_boxes_mesh('KRCH | limestone and bronze corner curtainwall frame',bay_frames,stone,facade)
# Darker slender operable sash dividers in the curtainwall.
add_boxes_mesh('KRCH | corner bay slim metal mullions',[
 (((bay_x0+bay_x1)/2,-14.32,7.6),(0.055,0.10,15.1)),
],frame,facade)

# Repeated rectangular upper-story windows and their pale limestone surrounds.
window_panes=[]; window_frames=[]
for x in upper_x:
 zs=([1.38]+window_levels if x<-20 else window_levels)
 for z in zs:
  w=1.28; h=1.66
  window_panes.append(((x,-13.90,z),(w-0.24,0.07,h-0.22)))
  # pale stone jambs, header, and sill; same restrained rhythm as architect photograph
  window_frames += [((x-w/2+0.08,-14.26,z),(0.16,0.25,h)),((x+w/2-0.08,-14.26,z),(0.16,0.25,h)),((x,-14.26,z-h/2+0.08),(w,0.25,0.16)),((x,-14.26,z+h/2-0.08),(w,0.25,0.16))]
add_boxes_mesh('KRCH | repeated punched window glass',window_panes,glass,facade)
add_boxes_mesh('KRCH | limestone punched-window reveals',window_frames,stone,facade)

# Entrance at the public street-level lobby bay: paired glazed doors, shallow limestone canopy, canopy supports, step and readable name.
entry_x=-17.45; entry_y=-14.43
entry_panels=[((entry_x-0.52,entry_y,1.14),(0.96,0.08,2.18)),((entry_x+0.52,entry_y,1.14),(0.96,0.08,2.18))]
add_boxes_mesh('KRCH | paired transparent lobby entrance leaves',entry_panels,glass,facade)
add_boxes_mesh('KRCH | entrance door frame and bronze pulls',[
 ((entry_x-1.05,-14.52,1.12),(0.12,0.16,2.35)),((entry_x+1.05,-14.52,1.12),(0.12,0.16,2.35)),((entry_x,-14.52,2.29),(2.22,0.16,0.13)),((entry_x,-14.58,1.12),(0.045,0.08,0.7)),
],frame,facade)
add_boxes_mesh('KRCH | pale stone entrance canopy and supports',[
 ((entry_x,-15.23,3.15),(8.1,2.15,0.28)),((entry_x-3.75,-15.95,1.45),(0.28,0.30,2.9)),((entry_x+3.75,-15.95,1.45),(0.28,0.30,2.9)),
],stone,facade)
add_boxes_mesh('KRCH | accessible entry landing',[
 ((entry_x,-16.35,-0.28),(8.6,2.0,0.20)),((entry_x,-17.55,-0.47),(8.0,0.95,0.18)),((entry_x,-18.45,-0.66),(7.4,0.75,0.18)),
],stone,facade)
# Text face points south (-Y), explicit building identifier matches official project name.
text=bpy.data.curves.new('KRCH public entrance lettering','FONT'); text.body='KRACH LEADERSHIP CENTER'; text.size=0.23; text.extrude=0.002; text.align_x='CENTER'
textob=bpy.data.objects.new('KRCH | entrance name lettering',text); facade.objects.link(textob); textob.location=(entry_x,-14.56,2.70); textob.rotation_euler[0]=math.radians(90); text.materials.append(frame)
textob['reference']='Visible Krach Leadership Center identification in the official Sasaki exterior photograph; letter style and exact size interpretive.'

# Move the source-evidenced open multilevel stair from the former center location to the photographed glazed lobby bay.
stair=bpy.data.objects.get('KRCH open stair | 4-floor lobby flights and etched glass balustrade')
assert stair is None, 'old stair should have been removed by prefix cleanup'
# Rebuild broad paired switchback flights in a camera-visible atrium well; two runs per floor interval.
# Geometry is schematic, while multi-level stair, open galleries and etched glass guards are source-backed.
stair_mat=mat('KRCH | visible lobby cast stone stair treads',(0.61,0.58,0.52),0.68)
rail_glass=mat('KRCH | translucent etched glass gallery guards',(0.64,0.73,0.73),0.36,0,0.52)
hand_mat=frame
st_verts=[]; st_faces=[]; st_material_indices=[]
def add_tread(cx,cy,cz,sx,sy,sz):
 k=len(st_verts)
 st_verts.extend([(cx-sx/2,cy-sy/2,cz-sz/2),(cx+sx/2,cy-sy/2,cz-sz/2),(cx+sx/2,cy+sy/2,cz-sz/2),(cx-sx/2,cy+sy/2,cz-sz/2),(cx-sx/2,cy-sy/2,cz+sz/2),(cx+sx/2,cy-sy/2,cz+sz/2),(cx+sx/2,cy+sy/2,cz+sz/2),(cx-sx/2,cy+sy/2,cz+sz/2)])
 st_faces.extend([(k+0,k+3,k+2,k+1),(k+4,k+5,k+6,k+7),(k+0,k+1,k+5,k+4),(k+1,k+2,k+6,k+5),(k+2,k+3,k+7,k+6),(k+3,k+0,k+4,k+7)]); st_material_indices.extend([0]*6)
def add_guard(a,b,y):
 k=len(st_verts); st_verts.extend([(a[0],y,a[1]),(b[0],y,b[1]),(b[0],y,b[1]+0.82),(a[0],y,a[1]+0.82)])
 st_faces.append((k,k+1,k+2,k+3)); st_material_indices.append(1)
levels=[-0.92,2.98,6.88,10.78,14.68]
yA=-10.55; yB=-8.05; x0=-23.35; xmid=-19.45; xend=-15.55; n=11
for lo,hi in zip(levels[:-1],levels[1:]):
 mid=(lo+hi)/2; rise=(hi-lo)/2
 for j in range(n):
  z=lo+(j+1)*rise/n; xa=x0+(j+0.5)*(xmid-x0)/n
  add_tread(xa,yA,z-0.09,(xmid-x0)/n+0.02,1.75,0.18)
  zb=mid+(j+1)*rise/n; xb=xend-(j+0.5)*(xend-xmid)/n
  add_tread(xb,yB,zb-0.09,(xend-xmid)/n+0.02,1.75,0.18)
 add_tread((xmid+xend)/2,(yA+yB)/2,mid-0.10,xend-xmid,4.95,0.20)
 add_tread(x0-0.55,(yA+yB)/2,lo+0.04,1.1,4.95,0.18)
 add_tread(xend+0.55,(yA+yB)/2,hi-0.04,1.1,4.95,0.18)
 # recognizable translucent gallery guards on both stair runs and edges of the broad intermediate landing
 for ya in [yA-0.93,yA+0.93]: add_guard((x0,ya,lo+0.14),(xmid,ya,mid+0.14),ya)
 for yb in [yB-0.93,yB+0.93]: add_guard((xend,yb,mid+0.14),(xmid,yb,hi+0.14),yb)
stmesh=bpy.data.meshes.new('KRCH documented open stair and gallery | schematic')
stmesh.from_pydata(st_verts,[],st_faces); stmesh.materials.append(stair_mat); stmesh.materials.append(rail_glass)
for p,mi in zip(stmesh.polygons,st_material_indices): p.material_index=mi
stair=bpy.data.objects.new('KRCH | four-story visible switchback stair and etched glass guard',stmesh); interior.objects.link(stair)
stair['source_basis']='Purdue Stories photo CFJ_Krach-Stairwell-Comp-Flattened_FullRes-scaled.jpg (2022); McGrory confirms etched laminated glass guardrails at multilevel lobby walks.'
stair['uncertainty']='Flight arrangement, exact plan location, tread count, width, floor-to-floor heights and void size are schematic; no measured architectural plans were located.'

# Replace full plates with conservative GIS-footprint slabs and evidence-supported atrium voids around the documented multi-level lobby/stair.
floor_mat=mat('KRCH | pale terrazzo gallery floor',(0.53,0.50,0.44),0.72)
void_specs=[]
for z in levels:
 n=len(ring); vv=[(v.x,v.y,z-0.18) for v in ring]+[(v.x,v.y,z) for v in ring]
 ff=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 for i in range(n): ff.append((i,(i+1)%n,(i+1)%n+n,i+n))
 me=bpy.data.meshes.new('KRCH level slab with atrium | GIS footprint'); me.from_pydata(vv,[],ff); me.materials.append(floor_mat); me.update()
 bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
 ob=bpy.data.objects.new('KRCH | schematic level slab %02d' % (levels.index(z)+1),me); interior.objects.link(ob)
 ob['level_top_m']=z; ob['atrium_void']='Open rectangle around multi-level public stair, evidenced by Purdue interior photograph and glass-guard gallery descriptions; exact dimensions schematic.'
 # Rectangular opening follows stair plan with only modest clearance.
 bpy.ops.mesh.primitive_cube_add(size=1,location=(-19.45,-9.3,z-0.09)); cut=bpy.context.object; cut.name='TEMP | stairwell floor void cutter'; cut.dimensions=(11.7,7.2,0.4); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
 mod=ob.modifiers.new('Documented multi-level lobby stair void','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cut
 bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cut,do_unlink=True)

# Keep stairs and stairwell aligned; the envelope opening above covers front-glazing levels.
for o in [stair]:
 o['building_id']='krach_leadership_center'; o['local_frame']='project local meters; placement remains controlled by the existing master marker'

# Save the modular building source only; no master or shared files are touched.
bpy.ops.wm.save_as_mainfile(filepath=src)
print(json.dumps({'saved':src,'footprint_vertices':N,'shell_bounds':[-35.19456,35.2,-14.14485,14.15313,-1.0,top_z],'front_window_count':len(upper_x)*3,'cutout_count':len(cut_specs),'stair_treads':44*2,'floor_levels':levels,'floorwell_xy_bounds':[-25.3,-13.6,-12.9,-5.7]},indent=2))

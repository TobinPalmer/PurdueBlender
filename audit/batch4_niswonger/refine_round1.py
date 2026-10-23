"""Source-led detail pass for the Niswonger library. Run with Blender 5.2."""
import bpy, math, json, shutil
from pathlib import Path
from mathutils import Vector

OUT = Path('audit/batch4_niswonger')
ASSET_PATH = Path(bpy.data.filepath)
OUT.mkdir(parents=True, exist_ok=True)
backup = OUT / 'niswonger_before_round1.blend'
if not backup.exists():
    shutil.copy2(ASSET_PATH, backup)
asset = bpy.data.collections['Asset_niswonger_aviation_tech']
detail = bpy.data.collections.get('NISW_Batch4_Reviewable_Detail')
if detail is None:
    detail = bpy.data.collections.new('NISW_Batch4_Reviewable_Detail')
    asset.children.link(detail)
else:
    for o in list(detail.objects):
        bpy.data.objects.remove(o, do_unlink=True)

def mat(name, color, rough=.5, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Base Color'].default_value = (*color, 1.0)
        bs.inputs['Roughness'].default_value = rough
        bs.inputs['Metallic'].default_value = metallic
    return m

def emissive(name, color, strength):
    m = mat(name, color, .24, .05)
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Emission Color'].default_value = (*color, 1.0)
    bs.inputs['Emission Strength'].default_value = strength
    return m

steel = bpy.data.materials['NISW_Satin_Metal']
brick = bpy.data.materials['NISW_Purdue_Red_Brick']
glass = bpy.data.materials['NISW_CurtainWall_Glass']
panel = bpy.data.materials['NISW_Photographic_Terracotta_Panels']
deskmat = bpy.data.materials['NISW_Lecture_Desk_Laminate']
seatmat = bpy.data.materials['NISW_Seat_Upholstery']
tile = bpy.data.materials['NISW_Terrazzo_Tile_MetreScale']
roofmat = bpy.data.materials['NISW_Roof_Membrane']
white = bpy.data.materials['NISW_Photographic_Offwhite_Plaster']
plane_white = mat('NISW_B4_LightAircraft_White', (.78,.80,.79), .32, .12)
plane_red = mat('NISW_B4_LightAircraft_CrimsonAccent', (.53,.045,.035), .31, .06)
plane_glass = mat('NISW_B4_LightAircraft_Canopy', (.035,.16,.22), .18, .32)
rubber = mat('NISW_B4_Tire_Rubber', (.018,.022,.025), .76, .0)
lightmat = emissive('NISW_B4_Recessed_Luminaire', (1.0,.91,.73), 3.0)
grillemat = mat('NISW_B4_Ceiling_Grille',(.105,.13,.14),.72,.18)
frame = mat('NISW_B4_Clerestory_Frame',(.16,.20,.21),.26,.68)

# Improve the physical response of existing finishes while keeping their source colors.
bs = tile.node_tree.nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value = .20
bs.inputs['Metallic'].default_value = .025
if 'Coat Weight' in bs.inputs: bs.inputs['Coat Weight'].default_value = .22
bs = deskmat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value = .31
bs.inputs['Metallic'].default_value = .015
bs = seatmat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value = .36
bs.inputs['Sheen Weight'].default_value = .18
bs = roofmat.node_tree.nodes.get('Principled BSDF')
if bs:
    bs.inputs['Base Color'].default_value = (.48,.48,.44,1)
    bs.inputs['Roughness'].default_value = .62
    bs.inputs['Metallic'].default_value = .22

def box(name, center, dims, material, rot=None, bevel=0.0):
    hx,hy,hz = (d/2 for d in dims)
    verts=[(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
           (-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.materials.append(material)
    ob=bpy.data.objects.new(name,me); detail.objects.link(ob); ob.location=center
    if rot: ob.rotation_euler=rot
    if bevel:
        mod=ob.modifiers.new('Soft manufactured edges','BEVEL');mod.width=bevel;mod.segments=3
        mod2=ob.modifiers.new('Corner normals','WEIGHTED_NORMAL');mod2.keep_sharp=True
    return ob

def mesh(name, verts, faces, material, smooth=False):
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.materials.append(material)
    ob=bpy.data.objects.new(name,me);detail.objects.link(ob)
    if smooth:
        for p in me.polygons: p.use_smooth=True
    return ob

# The photographed clerestory roof belongs over the long glass connector (about x=5..20.5),
# not the full 44.5 m classroom/wing span used in the previous sketch.
old_roof = bpy.data.objects.get('NISW_Photographic_Sloping_Roof')
if old_roof:
    me=old_roof.data
    # local vertices exactly as authored at world/local origin
    me.clear_geometry()
    me.from_pydata([(5,7.5,7.60),(20.5,7.5,9.40),(20.5,43.5,9.40),(5,43.5,7.60)],[],[(0,1,2,3)])
    me.update()
    old_roof['source_status']='Approximate long connector roof span from MSKTD atrium photographs; dimensions inferred, not surveyed.'
    old_roof['batch4_review']='roof rescaled to align with visible steel/clerestory spine x=5..20.5 m'
    # Reuse solidify modifier and exact roof material.
for name in list(bpy.data.objects.keys()):
    if name.startswith('NISW_ClerestoryClosure') or name.startswith('NISW_PaleMetal_RoofFascia'):
        ob=bpy.data.objects.get(name)
        if ob and ob.type=='MESH' and any(col==asset or col in asset.children_recursive for col in ob.users_collection):
            bpy.data.objects.remove(ob,do_unlink=True)
for ob in list(asset.all_objects):
    if ob.name.startswith('NISW_Atrium_Steel_Crossbeam'):
        bpy.data.objects.remove(ob,do_unlink=True)

slope=math.atan2(1.8,15.5)
def roof_z(x): return 7.60 + (x-5.0)*(1.8/15.5)
# Steel rafters cross the corridor every approximately 5 m, following the single-slope roof.
for i,y in enumerate([7.7,12.7,17.7,22.7,27.7,32.7,37.7,43.3]):
    box(f'NISW_B4_Rafter_{i:02d}',(12.75,y,8.50),(15.55,.20,.30),steel,(0,-slope,0),.025)
# Purlins and standing seams run with the long slope direction, matching the photographed metal deck.
for i in range(8):
    x=6.0+i*2.0
    z=roof_z(x)-.18
    box(f'NISW_B4_Roof_Purlin_{i:02d}',(x,25.5,z),(.11,35.8,.15),steel,None,.015)
for i in range(30):
    x=5.25+i*.50
    z=roof_z(x)+.025
    box(f'NISW_B4_Roof_StandingSeam_{i:02d}',(x,25.5,z),(.028,35.7,.035),frame,(0,-slope,0),.006)
# Fascia follows the narrow roof footprint. Gable glazing occupies only the triangular clerestory ends.
box('NISW_B4_Roof_Fascia_Low',(5,25.5,7.60),(.20,36.2,.24),steel,None,.025)
box('NISW_B4_Roof_Fascia_High',(20.5,25.5,9.40),(.20,36.2,.24),steel,None,.025)
for y in [7.5,43.5]:
    v=[(5,y,7.35),(20.5,y,7.35),(20.5,y,9.4)]
    ob=mesh('NISW_B4_Clerestory_Gable',v,[(0,1,2)],glass)
    ob['source_status']='Visual form and blue-green glazing from MSKTD atrium/exterior photos; exact gable dimensions estimated.'
    # Recessed perimeter frame and repeated vertical mullions.
    for x in [5.3,8.0,10.7,13.4,16.1,18.8,20.35]:
        ztop=roof_z(x)-.06
        box(f'NISW_B4_Gable_Mullion_{str(y).replace(".","_")}_{str(x).replace(".","_")}',(x,y-.035, (7.35+ztop)/2),(.075,.11,ztop-7.35),frame,None,.012)
    for z in [7.75,8.15,8.55,8.95]:
        xmax=5+(z-7.6)/(1.8/15.5)
        if xmax>5.1:
            box(f'NISW_B4_Gable_Horizontal_{str(y).replace(".","_")}_{str(z).replace(".","_")}',((5+xmax)/2,y-.04,z),(xmax-5,.11,.065),frame,None,.008)

# Extend existing support columns to meet the adjusted connector roof soffit.
for ob in asset.all_objects:
    if ob and ob.name.startswith('NISW_Atrium_Steel_Column'):
        ztop=roof_z(ob.location.x)-.06
        ob.dimensions.z=ztop
        ob.location.z=ztop/2
        ob['source_status']='Support location from prior corridor reconstruction; height set to approximate roof soffit.'

# Visible corridor fixtures and slim conduits follow the documented exposed steel/metal ceiling.
for row,y in enumerate([10.1,15.1,20.1,25.1,30.1,35.1,40.1]):
    for j,x in enumerate([10.5,14.2,17.2]):
        z=roof_z(x)-.42
        box(f'NISW_B4_Corridor_Light_{row}_{j}',(x,y,z),(.13,2.10,.07),lightmat,None,.025)
        ld=bpy.data.lights.new(f'NISW_B4_Corridor_Area_{row}_{j}','AREA');ld.energy=115;ld.shape='RECTANGLE';ld.size=1.2;ld.size_y=.4
        lo=bpy.data.objects.new(ld.name,ld);detail.objects.link(lo);lo.location=(x,y,z-.10)
    # Small suspended pipe/conduit line alongside the visible frame rhythm.
    box(f'NISW_B4_Corridor_Conduit_{row}',(16.2,y,roof_z(16.2)-.20),(.055,.055,3.0),steel,None,.015)

# Improve the four plan-backed classrooms with explicit recessed fixtures, HVAC registers,
# shared continuous desk runs, and softly radiused upholstery. The original footprints and seats stay put.
rooms=json.loads(Path('audit/batch2_niswonger/changes.json').read_text())['rooms']
for r in rooms:
    rn=r['room'];cx,cy=r['center'];w=r['width_m'];d=r['depth_m'];ang=math.radians(r['orientation_deg'])
    def xy(x,y): return (cx+x*math.cos(ang)-y*math.sin(ang),cy+x*math.sin(ang)+y*math.cos(ang))
    # replace square desk leaves with one continuous top per row; existing supports and chair positions remain.
    oldtops=[o for o in list(asset.all_objects) if o.name.startswith(f'NISW_Room{rn}_Desk_') and o.type=='MESH']
    row_centers={}
    for o in oldtops:
        rel=o.location-Vector((cx,cy,o.location.z))
        ly=rel.x*math.sin(ang)+rel.y*math.cos(ang)
        row_centers.setdefault(round(ly,3),[]).append(o)
    for idx,(ly,group) in enumerate(sorted(row_centers.items())):
        for o in group: o.hide_render=True
        z=sum(o.location.z for o in group)/len(group)+.002
        top=box(f'NISW_B4_Room{rn}_ContinuousDeskRow_{idx+1:02d}',xy(0,ly)+(z,), (w-2.02,.47,.055),deskmat,(0,0,ang),.025)
        top['source_status']='Shared row desktop follows 2016 classroom photo; exact seat arrangement from archived plan.'
    for o in list(asset.all_objects):
        if o and o.name.startswith((f'NISW_Room{rn}_Seat_',f'NISW_Room{rn}_ChairBack_')) and o.type=='MESH':
            if not any(m.name=='B4_Soft_Upholstery_Edges' for m in o.modifiers):
                b=o.modifiers.new('B4_Soft_Upholstery_Edges','BEVEL');b.width=.045 if 'Seat_' in o.name else .055;b.segments=4
                o.modifiers.new('B4_Weighted_Corner_Normals','WEIGHTED_NORMAL')
    # Recessed warm-white ceiling light panels and narrow slotted return grilles.
    for i in range(8):
        row=i//4; col=i%4
        lx=(col-1.5)*w*.20; ly=-d*.28+row*d*.56
        gx,gy=xy(lx,ly); z=3.375
        box(f'NISW_B4_Room{rn}_RecessedLight_{i+1:02d}',(gx,gy,z),(1.15,.30,.025),lightmat,(0,0,ang),.035)
        for k in range(5):
            box(f'NISW_B4_Room{rn}_LightLensRib_{i+1:02d}_{k}',(gx,gy+(k-2)*.035,z-.014),(.98,.012,.009),white if 'NISW_Photographic_Offwhite_Plaster' in bpy.data.materials else steel,(0,0,ang),.003)
    for i,(lx,ly) in enumerate([(-w*.30,-d*.32),(w*.30,-d*.32),(-w*.30,d*.32),(w*.30,d*.32)]):
        gx,gy=xy(lx,ly);z=3.372
        box(f'NISW_B4_Room{rn}_AirRegisterFrame_{i+1}',(gx,gy,z),(.40,.25,.022),steel,(0,0,ang),.014)
        for k in range(7):
            box(f'NISW_B4_Room{rn}_AirRegisterSlot_{i+1}_{k}',(gx,gy+(k-3)*.027,z-.013),(.31,.009,.008),grillemat,(0,0,ang),.002)
    # Make the overhead projection screen read as a framed white drop screen above the dark board.
    screen=bpy.data.objects.get(f'NISW_Room{rn}_ProjectionScreen')
    if screen:
        screen.data.materials.clear();screen.data.materials.append(mat('NISW_B4_ProjectionSurface',(.86,.88,.87),.22,.0))
        screen['review_note']='Framed projection plane made visible above the source-documented teaching wall.'
        # narrow dark case at the top edge
        p=screen.location.copy();sx=screen.dimensions.x
        box(f'NISW_B4_Room{rn}_ScreenCase',(p.x,p.y,p.z+.57),(sx,.08,.10),frame,(0,0,ang),.015)

# Generic light-aircraft silhouettes in the documented Hangar 1 volume. Their scale is tied to
# Cirrus SR20 published dimensions (11.7 m span, 7.9 m length); type/parking positions are illustrative.
def aircraft(prefix,cx,cy,heading_deg=0):
    a=math.radians(heading_deg)
    def tr(x,y,z): return (cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a),z)
    def local_box(name,loc,dims,material,rot=None,bevel=0):
        loc=tr(*loc); base=rot or (0,0,a)
        return box(prefix+'_'+name,loc,dims,material,base,bevel)
    # Elliptic, tapered cabin fuselage with a soft composite shell.
    stations=[(-4.0,.05,.08),(-3.65,.20,.19),(-2.9,.34,.32),(-1.8,.43,.42),(.4,.43,.43),(1.8,.33,.33),(3.1,.23,.24),(3.8,.08,.12)]
    verts=[]; faces=[]; n=16
    for y,rx,rz in stations:
        for j in range(n):
            t=2*math.pi*j/n
            verts.append(tr(rx*math.cos(t),y,.90+rz*math.sin(t)))
    for i in range(len(stations)-1):
        for j in range(n): faces.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
    mesh(prefix+'_Fuselage',verts,faces,plane_white,True)
    # Low tapered cantilever wing, published span scale; the outline is a generic SR20-class visual model.
    wing_outline=[(-5.85,.15),(-5.1,.18),(-1.35,-.90),(1.35,-.90),(5.1,.18),(5.85,.15),(5.5,-.85),(1.25,-1.42),(-1.25,-1.42),(-5.5,-.85)]
    wv=[tr(x,y,.75) for x,y in wing_outline]
    mesh(prefix+'_MainWing',wv,[tuple(range(len(wv)))],plane_white)
    # Control-surface trailing-edge stripe.
    for side in [-1,1]:
        local_box(f'Flap_{side}',(side*3.25,-1.06,.77),(3.6,.055,.022),plane_red,(0,0,a),.008)
    # Horizontal and vertical empennage.
    tail=[(-1.55,2.70),(1.55,2.70),(1.25,3.55),(-1.25,3.55)]
    mesh(prefix+'_Tailplane',[tr(x,y,.98) for x,y in tail],[tuple(range(4))],plane_white)
    fin=[tr(0,2.6,.96),tr(0,3.72,1.03),tr(0,3.32,2.48),tr(0,2.85,1.35)]
    mesh(prefix+'_VerticalTail',fin,[(0,1,2,3)],plane_white)
    local_box('TailAccent',(0,3.14,1.70),(.04,.57,.075),plane_red,(0,0,a),.015)
    # Teardrop cockpit canopy and side windows as restrained cool blue glass.
    canopy=local_box('CockpitCanopy',(0,-.90,1.30),(.66,1.75,.38),plane_glass,(0,0,a),.14)
    canopy['source_status']='Canopy silhouette and cabin glazing are generic aircraft cues; no individual airframe identity claimed.'
    # Thin crimson fuselage side stripe.
    for side in [-1,1]: local_box(f'FuselageAccent_{side}',(side*.386,.40,.92),(.024,2.8,.08),plane_red,(0,0,a),.025)
    # Propeller hub and two blades in the nose plane.
    hub=local_box('PropellerHub',(0,-4.0,.90),(.16,.13,.16),steel,(0,0,a),.025)
    for i,rz in enumerate([0,math.pi/2]):
        local_box(f'PropellerBlade_{i+1}',(0,-4.10,.90),(.105,.075,1.18),plane_white,(0,rz,a),.04)
    # Tricycle landing gear: robust 1.2 m-ish track, three rubber tires and struts.
    for i,(x,y) in enumerate([(-1.45,.62),(1.45,.62),(0,-2.72)]):
        wheel_z=.37
        local_box(f'GearStrut_{i+1}',(x,y,.58),(.075,.085,.48),steel,(0,0,a),.025)
        ob=local_box(f'Tire_{i+1}',(x,y,wheel_z),(.19,.42,.44),rubber,(0,0,a),.055)
        ob['dimensions_reference']='SR20 overall dimensions only; wheel/gear dimensions visually estimated.'
    # Wingtip nav lights.
    for side,color in [(-1,(.68,.018,.012)),(1,(.02,.26,.08))]:
        nav=mat(prefix+'_NavLight_'+str(side),color,.24,.05)
        local_box('NavLight_'+str(side),(side*5.78,.10,.78),(.16,.18,.13),nav,(0,0,a),.03)
    for ob in detail.objects:
        if ob.name.startswith(prefix+'_'):
            ob['source_status']='Illustrative light aircraft in Hangar 1; Hangar 1 is documented as storing flight-instruction aircraft. Parking location and exact current type/count unverified.'

aircraft('NISW_B4_Hangar_Aircraft_A',-16.0,-8.0,0)
aircraft('NISW_B4_Hangar_Aircraft_B',-3.0,-8.0,0)

# Hangar roof framing/lighting beneath the retained low wing roof; structural position is explicitly estimated.
for i,y in enumerate([-25,-19,-13,-7,-1,5,11]):
    box(f'NISW_B4_Hangar_RoofTruss_{i+1:02d}',(-12.5,y,4.24),(34,.16,.16),steel,None,.018)
    for x in [-27,-20,-12.5,-5,2]:
        box(f'NISW_B4_Hangar_Light_{i+1:02d}_{str(x).replace("-","m")}',(x,y,4.08),(.20,2.2,.055),lightmat,None,.03)
        ld=bpy.data.lights.new(f'NISW_B4_Hangar_Area_{i+1}_{str(x).replace("-","m")}','AREA');ld.energy=210;ld.shape='RECTANGLE';ld.size=2.2;ld.size_y=.4
        lo=bpy.data.objects.new(ld.name,ld);detail.objects.link(lo);lo.location=(x,y,3.98)

# Add small wall panel seams and light-scaled reflectance cues to the corridor's orange system.
for i,y in enumerate([10,15,20,25,30,35,40]):
    for z in [1.25,2.35,3.10]:
        box(f'NISW_B4_Corridor_PanelReveal_{i}_{str(z).replace(".","_")}',(5.075,y,z),(.018,4.65,.018),frame,None,.003)

# Document source use and measurable geometry checks; do not assert a full room layout.
report={
 'asset':'modular/buildings/niswonger_aviation_tech.blend',
 'asset_id':'niswonger_aviation_tech','collection':'Asset_niswonger_aviation_tech',
 'retrieval_date':'2026-10-23',
 'sources':[
  {'url':'https://msktd.com/project/purdue-university-niswonger-aviation-technology/','provider':'MSKTD architect project page','use':'Exterior, clerestory/atrium geometry, roof deck framing, terracotta panels, brick, glazing, classroom, terrazzo photos; archived images in audit/batch2_niswonger/photo*.jpg and photof.jpg.'},
  {'url':'https://old.polytechnic.purdue.edu/sites/default/files/files/TCO%20and%20S%26P%20Manual%20Final%20Copy.pdf','provider':'Purdue Polytechnic facility manual, revision 12 dated 2016-06-01','use':'Ground floor plan page 33 / PDF page 33, classroom dimension and seat capacities page 31; historical layout only.'},
  {'url':'https://www.purduealumnus.org/a-day-at-the-airport/features/','provider':'Purdue Alumnus','use':'Hangar One is described as full of light aircraft used for flight instruction; article published circa 2016, not a current inventory.'},
  {'url':'https://cirrusaircraft.com/wp-content/uploads/2024/01/NorthAmerica_SR20_PriceList_2026.pdf','provider':'Cirrus Aircraft 2026 SR20 dimensions sheet','use':'11.7 m wingspan and 7.9 m length used as aircraft silhouette scale reference; does not verify a specific aircraft in the hangar.'},
  {'url':'https://events.purdue.edu/niswonger_aviation_technology_building','provider':'Purdue events location listing','use':'Current public building identity/address: 1401 Aviation Dr, West Lafayette, IN 47907-2015.'},
  {'url':'https://www.google.com/maps/search/Niswonger+Aviation+Technology+Building+Purdue+University','provider':'Google Maps','use':'Attempted direct in-app browser open on 2026-10-23; browser tool reported "IAB visibility is not supported in a subagent thread". Search-result identity only; no satellite or Street View frame independently inspected.'}
 ],
 'changes':[
   'Rescaled the clerestory roof from full 44.5 m wing span to the photographed connector spine x=5..20.5 m; made dimension estimate explicit.',
   'Replaced oversized perimeter glazing closures with two triangular gable clerestories, repeated mullions, purlins and standing seams.',
   'Extended connector columns to meet roof soffit and added framed long-span roof members, visible linear lights and conduit.',
   'Added 8 recessed ceiling light panels and 4 air registers per 2016 plan-backed classroom; screens gained a visible case.',
   'Added continuous row desktop leaves and softened chair upholstery edges without changing the previous seat counts/room locations.',
   'Added two generic SR20-scale aircraft silhouettes in Hangar 1 and low-wing estimated truss/lighting details.'
 ],
 'uncertainty':[
   'GIS FID870 supports the footprint only; no surveyed height or roof dimension was found.',
   'Classroom registration remains approximately 1.5 m uncertain and the source plan is historical (2016).',
   'Current hangar airframe inventory, aircraft positions, hangar roof structure, exact exits/circulation and current non-classroom partitions are unverified.',
   'Map visual access failed inside this subagent; no satellite/Street View comparison is claimed.'
 ],
 'coordinate_frame':'Local asset meters, X east/Y north/Z up; building library transform preserved.',
 'master_or_manifest_edits':False
}
Path(OUT/'round1_changes.json').write_text(json.dumps(report,indent=2))

# Save the asset before rendering. Render setups are temporary, outside the export collection.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.resolution_x=1100;scene.render.resolution_y=850;scene.render.resolution_percentage=100
scene.world.color=(.38,.38,.38)
for o in bpy.data.objects:
    if o.type=='LIGHT': o.hide_render=True
review_lights=[]
for loc,power,size in [((0,20,55),26000,36),((-45,55,28),15500,25)]:
    ld=bpy.data.lights.new('NISW_B4_ReviewArea','AREA');ld.energy=power;ld.shape='DISK';ld.size=size
    ob=bpy.data.objects.new('NISW_B4_ReviewArea',ld);scene.collection.objects.link(ob);ob.location=loc;review_lights.append(ob)
ca=bpy.data.cameras.new('NISW_B4_ReviewCamera');cam=bpy.data.objects.new('NISW_B4_ReviewCamera',ca);scene.collection.objects.link(cam);scene.camera=cam
views=[
 ('exterior',(73,92,52),(-8,16,3.2),46,False),
 ('atrium',(14,40,2.7),(10.5,17.5,5.7),25,False),
 ('classroom_eye',(-14.0,28.5,2.1),(-14.0,17.0,1.55),25,False),
 ('hangar_eye',(-21,-16,2.8),(-18,-8,1.25),35,False),
 ('top_cutaway',(-8,7,105),(-8,7,0),0,False),
]
for name,loc,target,lens,hide_roof in views:
    for o in asset.all_objects:
        if not o: continue
        if any(tag in o.name for tag in ['Roof','Clerestory_Gable','Ceiling']): o.hide_render=hide_roof
        if o.type=='LIGHT':o.hide_render=False
    if name=='top_cutaway':
        for o in asset.all_objects:
            if not o: continue
            if any(tag in o.name for tag in ['Roof','Ceiling','ClerestoryClosure']):o.hide_render=True
        ca.type='ORTHO';ca.ortho_scale=85;cam.location=loc;cam.rotation_euler=(0,0,0)
    else:
        ca.type='PERSP';ca.lens=lens;cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str((OUT/f'{name}.png').resolve());bpy.ops.render.render(write_still=True)
# Remove review rig from the saved building library so the export remains a clean asset.
scene.camera=None
bpy.data.objects.remove(cam,do_unlink=True)
for ob in review_lights:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
Path(OUT/'round1_render_status.json').write_text(json.dumps({'rendered':[f'{n}.png' for n,*_ in views], 'asset_saved':str(ASSET_PATH)},indent=2))

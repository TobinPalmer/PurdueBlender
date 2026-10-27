import bpy, math, os, json
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
ASSET_ID='massing_house_860826641_2c90f97'
ASSET_FILE=os.path.join(ROOT,'modular','buildings',ASSET_ID+'.blend')
GIS_FILE=os.path.join(ROOT,'audit','delta_sigma_phi','sources','purdue_gis_fid798_delta_sigma_phi_2026-10-26_wgs84.json')
OUT_DIR=os.path.join(ROOT,'audit','delta_sigma_phi','previews')
os.makedirs(OUT_DIR,exist_ok=True)

# Verified source transform: Purdue campus approximation, metres; GIS polygon supplied in WGS84.
ORIGIN_LON=-86.9137
ORIGIN_LAT=40.4274
X_PER_DEG=84810.60416539927
Y_PER_DEG=111040.0
THETA=math.radians(129.44405524991802)  # official footprint minimum rotated rectangle long axis
CENTROID_WORLD=(357.7400581596961,-73.82974158000164)  # official polygon centroid in campus-local XY
OUTWARD=-1.0  # Street-facing elevation is the low-v edge, toward Northwestern Avenue.

with open(GIS_FILE,encoding='utf-8-sig') as f: feature=json.load(f)['features'][0]
ring=feature['geometry']['rings'][0]
# Convert outer footprint to project XY, then into a local frame centered on the official polygon centroid.
def world_xy(lon,lat): return ((lon-ORIGIN_LON)*X_PER_DEG,(lat-ORIGIN_LAT)*Y_PER_DEG)
def world_to_uv(x,y):
    dx=x-CENTROID_WORLD[0]; dy=y-CENTROID_WORLD[1]
    return (dx*math.cos(THETA)+dy*math.sin(THETA),-dx*math.sin(THETA)+dy*math.cos(THETA))
def uv_to_local(u,v):
    return (u*math.cos(THETA)-v*math.sin(THETA),u*math.sin(THETA)+v*math.cos(THETA))
POLY=[]
for lon,lat in ring[:-1]:
    POLY.append(world_to_uv(*world_xy(lon,lat)))

# Recreate a clean library scene with the original scene, collection, and exported collection names.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.name='Building_'+ASSET_ID
asset_col=bpy.data.collections.new('Asset_'+ASSET_ID)
scene.collection.children.link(asset_col)
root=bpy.data.objects.new('AssetRoot_'+ASSET_ID,None)
asset_col.objects.link(root)
root.empty_display_type='PLAIN_AXES'; root.empty_display_size=0.6; root.location=(0,0,0)

# Materials: all textures are procedural, packed inside the .blend and independent of external paths.
def mat_brick():
    m=bpy.data.materials.new('DSP_Weathered_Buff_Brick'); m.diffuse_color=(0.48,0.29,0.17,1); m.use_nodes=True
    n=m.node_tree.nodes; n.clear(); out=n.new('ShaderNodeOutputMaterial'); bs=n.new('ShaderNodeBsdfPrincipled'); bs.inputs['Roughness'].default_value=.82
    uv=n.new('ShaderNodeTexCoord'); brick=n.new('ShaderNodeTexBrick'); brick.offset=.5; brick.offset_frequency=2
    brick.inputs['Color1'].default_value=(0.39,0.225,0.13,1); brick.inputs['Color2'].default_value=(0.58,0.37,0.23,1); brick.inputs['Mortar'].default_value=(0.31,0.29,0.26,1)
    brick.inputs['Scale'].default_value=2.15; brick.inputs['Brick Width'].default_value=.62; brick.inputs['Row Height'].default_value=.27; brick.inputs['Mortar Size'].default_value=.045
    noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=7; noise.inputs['Detail'].default_value=3; noise.inputs['Roughness'].default_value=.7
    ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.2; ramp.color_ramp.elements[0].color=(.72,.68,.61,1); ramp.color_ramp.elements[1].position=.82; ramp.color_ramp.elements[1].color=(1,.96,.88,1)
    mix=n.new('ShaderNodeMixRGB'); mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=.28
    bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.16; bump.inputs['Distance'].default_value=.025
    links=m.node_tree.links; links.new(uv.outputs['UV'],brick.inputs['Vector']); links.new(uv.outputs['Generated'],noise.inputs['Vector']); links.new(noise.outputs['Fac'],ramp.inputs['Fac']); links.new(brick.outputs['Color'],mix.inputs[1]); links.new(ramp.outputs['Color'],mix.inputs[2]); links.new(mix.outputs['Color'],bs.inputs['Base Color']); links.new(brick.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bs.inputs['Normal']); links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    return m

def mat_stone(name='DSP_Limestone_Trim',color=(.72,.67,.57,1),rough=.78):
    m=bpy.data.materials.new(name); m.diffuse_color=color; m.use_nodes=True
    n=m.node_tree.nodes; bs=n.get('Principled BSDF'); bs.inputs['Base Color'].default_value=color; bs.inputs['Roughness'].default_value=rough
    noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=18; noise.inputs['Detail'].default_value=2
    bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.1; bump.inputs['Distance'].default_value=.025
    m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']); m.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return m

def mat_roof():
    m=bpy.data.materials.new('DSP_Dark_Slate_Shingle'); m.diffuse_color=(.105,.095,.084,1); m.use_nodes=True
    n=m.node_tree.nodes; n.clear(); out=n.new('ShaderNodeOutputMaterial'); bs=n.new('ShaderNodeBsdfPrincipled'); bs.inputs['Roughness'].default_value=.82
    tc=n.new('ShaderNodeTexCoord'); bt=n.new('ShaderNodeTexBrick'); bt.inputs['Scale'].default_value=2.6; bt.inputs['Brick Width'].default_value=.52; bt.inputs['Row Height'].default_value=.32; bt.inputs['Mortar Size'].default_value=.02; bt.inputs['Color1'].default_value=(.13,.12,.105,1); bt.inputs['Color2'].default_value=(.22,.205,.18,1); bt.inputs['Mortar'].default_value=(.07,.067,.06,1); bt.offset=.5
    bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.22; bump.inputs['Distance'].default_value=.035
    l=m.node_tree.links; l.new(tc.outputs['UV'],bt.inputs['Vector']); l.new(bt.outputs['Color'],bs.inputs['Base Color']); l.new(bt.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs['Normal'],bs.inputs['Normal']); l.new(bs.outputs['BSDF'],out.inputs['Surface'])
    return m

def simple_mat(name,color,rough=.55,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True; bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal; return m

BRICK=mat_brick(); STONE=mat_stone(); FOUNDATION=mat_stone('DSP_Foundation_Stone',(.34,.32,.29,1)); ROOF=mat_roof()
GLASS=simple_mat('DSP_Recessed_Window_Glass',(.035,.075,.09),.16,.18); WOOD=simple_mat('DSP_Oak_Entry_Door',(.095,.045,.025),.65); IRON=simple_mat('DSP_Dark_Wrought_Iron',(.055,.065,.065),.45,.68); CONCRETE=mat_stone('DSP_Entry_Concrete',(.46,.44,.4,1),.89)

# Helpers use the chapter-house frame (u along the verified long GIS axis, v toward the street).
def xyz(u,v,z):
    x,y=uv_to_local(u,v); return (x,y,z)
def mesh_obj(name,uvz_verts,faces,material,uv_faces=None):
    verts=[xyz(*p) for p in uvz_verts]
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(name,me); asset_col.objects.link(ob); ob.parent=root
    if uv_faces:
        layer=me.uv_layers.new(name='UVMap')
        for poly,coords in zip(me.polygons,uv_faces):
            for li,coord in zip(poly.loop_indices,coords): layer.data[li].uv=coord
    elif material == BRICK:
        # Photo-informed gables/dormers also receive brick-scale UVs (horizontal distance × height).
        layer=me.uv_layers.new(name='UVMap')
        for poly in me.polygons:
            coords=[uvz_verts[me.loops[li].vertex_index] for li in poly.loop_indices]
            span_u=max(p[0] for p in coords)-min(p[0] for p in coords)
            span_v=max(p[1] for p in coords)-min(p[1] for p in coords)
            axis=0 if span_u >= span_v else 1
            for li in poly.loop_indices:
                p=uvz_verts[me.loops[li].vertex_index]
                layer.data[li].uv=(p[axis],p[2])
    return ob

def box(name,uc,vc,zc,su,sv,sz,material,bevel=0.0):
    u0,u1=uc-su/2,uc+su/2; v0,v1=vc-sv/2,vc+sv/2; z0,z1=zc-sz/2,zc+sz/2
    verts=[(u0,v0,z0),(u1,v0,z0),(u1,v1,z0),(u0,v1,z0),(u0,v0,z1),(u1,v0,z1),(u1,v1,z1),(u0,v1,z1)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    ob=mesh_obj(name,verts,faces,material)
    if bevel:
        mod=ob.modifiers.new('Soft_masonry_edges','BEVEL'); mod.width=bevel; mod.segments=2
    return ob

def wall_edge(i,a,b,z0,z1,material=BRICK):
    ua,va=a; ub,vb=b; length=math.hypot(ub-ua,vb-va)
    # Face orientation points outward from a clockwise footprint ring.
    verts=[(ua,va,z0),(ua,va,z1),(ub,vb,z1),(ub,vb,z0)]
    uv=[(0,0),(0,z1-z0),(length,z1-z0),(length,0)]
    return mesh_obj('DSP_Exterior_Wall_%02d'%i,verts,[(0,1,2,3)],material,[uv])

def arch_profile(center_u,base_z,width,height,v):
    r=width/2; spring=base_z+height-r; pts=[(center_u-r,base_z),(center_u+r,base_z),(center_u+r,spring)]
    for k in range(1,9):
        a=math.pi*k/8; pts.append((center_u+r*math.cos(a),spring+r*math.sin(a)))
    return [(u,v,z) for u,z in pts]

def arch_window(index,center_u,base_z=0.82,width=1.58,height=2.45,front_v=.98):
    # Dark arched glazing panel and a continuous limestone ring; no fake interior is visible through the glass.
    inner=arch_profile(center_u,base_z,width,height,front_v)
    mesh_obj('DSP_Arched_Glazing_%02d'%index,inner,[tuple(reversed(range(len(inner))))],GLASS)
    outer=arch_profile(center_u,base_z-.10,width+.38,height+.30,front_v+OUTWARD*.055)
    # Build a matched band between corresponding outer/inner profiles.
    faces=[]; n=len(inner)
    for k in range(n): faces.append((k,(k+1)%n,(k+1)%n+n,k+n))
    mesh_obj('DSP_Limestone_Arch_Surround_%02d'%index,inner+outer,faces,STONE)
    # Slim dark mullions, clipped visually to the arched panel.
    box('DSP_Arch_Mullion_%02d'%index,center_u,front_v+.09,base_z+height*.47,.055,.055,height*.91,IRON)

def rect_window(index,center_u,base_z,width=1.32,height=1.52,front_v=.99):
    box('DSP_Window_Reveal_%02d'%index,center_u,front_v+OUTWARD*.025,base_z+height/2,width+.18,.10,height+.18,STONE,.025)
    box('DSP_Window_Glass_%02d'%index,center_u,front_v+OUTWARD*.10,base_z+height/2,width,.035,height,GLASS,.01)
    box('DSP_Window_MullionV_%02d'%index,center_u,front_v+OUTWARD*.13,base_z+height/2,.045,.03,height,IRON)
    box('DSP_Window_MullionH_%02d'%index,center_u,front_v+OUTWARD*.13,base_z+height/2,width,.03,.045,IRON)
    # A sill and lintel create the deep limestone reveal seen in the source views.
    box('DSP_Window_Sill_%02d'%index,center_u,front_v+OUTWARD*.11,base_z-.07,width+.26,.18,.14,STONE,.018)

def roof_panel(name,verts,uv):
    ob=mesh_obj(name,verts,[(0,1,2,3)],ROOF,[uv]); return ob

def gabled_roof_along_u(prefix,u0,u1,v0,v1,eave,ridge_z,overhang=.45):
    uc=(u0+u1)/2; vr=(v0+v1)/2; u0-=overhang; u1+=overhang; v0-=overhang; v1+=overhang
    # two long shingle planes, with metric UVs for stable physical scale
    roof_panel(prefix+'_Roof_Front',[(u0,v1,eave),(u1,v1,eave),(u1,vr,ridge_z),(u0,vr,ridge_z)],[(0,0),(u1-u0,0),(u1-u0,math.hypot(v1-vr,ridge_z-eave)),(0,math.hypot(v1-vr,ridge_z-eave))])
    roof_panel(prefix+'_Roof_Back',[(u0,vr,ridge_z),(u1,vr,ridge_z),(u1,v0,eave),(u0,v0,eave)],[(0,0),(u1-u0,0),(u1-u0,math.hypot(vr-v0,ridge_z-eave)),(0,math.hypot(vr-v0,ridge_z-eave))])
    # Gable end walls match the observed tall triangular ends.
    for tag,u in [('West',u0+overhang),('East',u1-overhang)]:
        verts=[(u,v0,eave),(u,v1,eave),(u,vr,ridge_z)]
        mesh_obj(prefix+'_Gable_'+tag,verts,[(0,2,1)],BRICK)
    # narrow wood fascia at the eaves and ridge; kept beneath the shingle planes
    box(prefix+'_Fascia_Front',(u0+u1)/2,v1,eave-.08,u1-u0,.16,.22,FOUNDATION)
    box(prefix+'_Fascia_Back',(u0+u1)/2,v0,eave-.08,u1-u0,.16,.22,FOUNDATION)
    box(prefix+'_Ridge_Cap',(u0+u1)/2,vr,ridge_z-.02,u1-u0,.16,.16,ROOF)

def gabled_roof_along_v(prefix,u0,u1,v0,v1,eave,ridge_z,overhang=.35):
    uc=(u0+u1)/2; u0-=overhang; u1+=overhang; v0-=overhang; v1+=overhang
    roof_panel(prefix+'_Roof_Left',[(u0,v0,eave),(uc,v0,ridge_z),(uc,v1,ridge_z),(u0,v1,eave)],[(0,0),(math.hypot(uc-u0,ridge_z-eave),0),(math.hypot(uc-u0,ridge_z-eave),v1-v0),(0,v1-v0)])
    roof_panel(prefix+'_Roof_Right',[(uc,v0,ridge_z),(u1,v0,eave),(u1,v1,eave),(uc,v1,ridge_z)],[(0,0),(math.hypot(u1-uc,ridge_z-eave),0),(math.hypot(u1-uc,ridge_z-eave),v1-v0),(0,v1-v0)])
    for tag,v in [('Rear',v0+overhang),('Front',v1-overhang)]:
        mesh_obj(prefix+'_Gable_'+tag,[(u0,v,eave),(u1,v,eave),(uc,v,ridge_z)],[(0,2,1)],BRICK)
    box(prefix+'_Ridge_Cap',uc,(v0+v1)/2,ridge_z-.02,.16,v1-v0,.16,ROOF)

def dormer(index,center_u,base_v,base_z,width=2.4,depth=1.45,rise=1.35):
    u0=center_u-width/2; u1=center_u+width/2; back=base_v-OUTWARD*depth; front=base_v
    spring=base_z+1.35; peak=spring+rise
    # Low front wall and triangular gable
    mesh_obj('DSP_Dormer_Front_%02d'%index,[(u0,front,base_z),(u1,front,base_z),(u1,front,spring),(center_u,front,peak),(u0,front,spring)],[(0,4,3,2,1)],BRICK)
    # side cheek walls
    mesh_obj('DSP_Dormer_SideL_%02d'%index,[(u0,back,base_z),(u0,front,base_z),(u0,front,spring),(u0,back,spring)],[(0,1,2,3)],BRICK)
    mesh_obj('DSP_Dormer_SideR_%02d'%index,[(u1,front,base_z),(u1,back,base_z),(u1,back,spring),(u1,front,spring)],[(0,1,2,3)],BRICK)
    roof_panel('DSP_Dormer_RoofL_%02d'%index,[(u0,back,spring),(center_u,back,peak),(center_u,front,peak),(u0,front,spring)],[(0,0),(math.hypot(width/2,rise),0),(math.hypot(width/2,rise),depth),(0,depth)])
    roof_panel('DSP_Dormer_RoofR_%02d'%index,[(center_u,back,peak),(u1,back,spring),(u1,front,spring),(center_u,front,peak)],[(0,0),(math.hypot(width/2,rise),0),(math.hypot(width/2,rise),depth),(0,depth)])
    rect_window(index+30,center_u,base_z+.18,width*.58,height=.93,front_v=front+.08)
    box('DSP_Dormer_Sill_%02d'%index,center_u,front+.12,base_z+.12,width*.76,.16,.14,STONE,.02)

def entry_cross_gable(center_u,front_v=-12.4,width=6.0,base_z=7.4,peak_z=11.2,back_v=-9.2):
    u0=center_u-width/2; u1=center_u+width/2
    # Limestone-edged projecting gabled entry; gable is a high wall above an open porch zone.
    mesh_obj('DSP_Entry_Gable_Face',[(u0,front_v,base_z),(u1,front_v,base_z),(center_u,front_v,peak_z)],[(0,2,1)],BRICK)
    roof_panel('DSP_Entry_Gable_RoofL',[(u0,back_v,base_z),(center_u,back_v,peak_z),(center_u,front_v,peak_z),(u0,front_v,base_z)],[(0,0),(math.hypot(width/2,peak_z-base_z),0),(math.hypot(width/2,peak_z-base_z),front_v-back_v),(0,front_v-back_v)])
    roof_panel('DSP_Entry_Gable_RoofR',[(center_u,back_v,peak_z),(u1,back_v,base_z),(u1,front_v,base_z),(center_u,front_v,peak_z)],[(0,0),(math.hypot(width/2,peak_z-base_z),0),(math.hypot(width/2,peak_z-base_z),front_v-back_v),(0,front_v-back_v)])
    # Thin limestone rake bands
    for side in (-1,1):
        us=center_u+side*width/2
        box('DSP_Gable_Rake', (us+center_u)/2,(front_v+back_v)/2,base_z+(peak_z-base_z)/2,.11,abs(front_v-back_v),.11,STONE)
    # Porch piers, understated so the door remains visible.
    # The photograph does not show a columned portico; omit unsupported piers.

def polygon_area(coords):
    return .5*sum(coords[i][0]*coords[(i+1)%len(coords)][1]-coords[(i+1)%len(coords)][0]*coords[i][1] for i in range(len(coords)))

# GIS-true wall perimeter and raised stone plinth. Store shell surfaces as per-edge objects so UV brick scale is physical.
for i,a in enumerate(POLY): wall_edge(i,a,POLY[(i+1)%len(POLY)],.5,7.55)
# Continuous foundation/plinth as shallow bands along footprint perimeter.
for i,a in enumerate(POLY):
    b=POLY[(i+1)%len(POLY)]
    wall_edge(i+100,a,b,0.0,.5,FOUNDATION)  # solid lower masonry plinth under the facade
# Main 20 m roof mass and perpendicular wing, directly inferred from the official L-shaped perimeter.
main_u0,main_u1=-19.7,12.9; main_v0,main_v1=-9.58,.95
main_eave=7.58; main_ridge=11.95; main_vridge=(main_v0+main_v1)/2
gabled_roof_along_u('DSP_Main_Roof',main_u0,main_u1,main_v0,main_v1,main_eave,main_ridge)
wing_u0,wing_u1=1.35,12.95; wing_v0,wing_v1=.75,16.85
# Correct Python tuple assignment because the wing is the perpendicular GIS footprint arm.
gabled_roof_along_v('DSP_Wing_Roof',wing_u0,wing_u1,wing_v0,wing_v1,7.45,10.65)
# Dormers on the street-facing main roof plane; their spacing follows the photographed three-plus-one rhythm.
front_slope=(main_ridge-main_eave)/(main_vridge-main_v0)
for i,u in enumerate([-15.0,-9.5,-4.0,2.5],1):
    base_v=-8.95; bz=main_eave+(base_v-main_v0)*front_slope-.05
    dormer(i,u,base_v,bz,width=2.15,depth=1.48,rise=.92)
# Rear elevation fenestration is left unmodeled where current imagery does not resolve it.
# Entry facade and floor pattern on the long street-facing wall.
front_v=-9.58
# Lower story arched openings, with a recessed dark center and light stone ring.
for i,u in enumerate([-15.5,-9.8,-4.2],1): arch_window(i,u,.76,1.5,2.38,front_v+OUTWARD*.04)
# Upper story fenestration, windows paired around entry gable.
for i,u in enumerate([-17.0,-13.0,-9.0,-5.0,-1.0,3.2,8.0],1): rect_window(i,u,4.25,1.28,1.58,front_v)
# Front door, dark-stained, framed in limestone and centered toward the cross-gable end.
door_u=5.2; door_v=front_v+OUTWARD*.13
box('DSP_Main_Entry_Door_Frame',door_u,door_v,1.65,1.86,.20,3.10,STONE,.03)
box('DSP_Main_Entry_Door',door_u,door_v+OUTWARD*.12,1.58,1.34,.07,2.78,WOOD,.025)
box('DSP_Entry_Door_Upper_Glazing',door_u,door_v+OUTWARD*.17,2.12,.56,.025,.66,GLASS,.015)
box('DSP_Entry_Door_Kickplate',door_u,door_v+OUTWARD*.18,.65,1.05,.025,.12,IRON)
box('DSP_Entry_Door_Handle',door_u+.43,door_v+OUTWARD*.21,1.47,.06,.06,.23,IRON,.02)
# A belt course and limestone arch/door lintel treatment match the visible buff trim.
box('DSP_Front_Belt_Course',(main_u0+main_u1)/2,front_v+OUTWARD*.055,3.48,main_u1-main_u0,.12,.22,STONE,.02)
box('DSP_Door_Stone_Lintel',door_u,door_v+OUTWARD*.08,3.26,1.98,.2,.22,STONE,.02)
entry_cross_gable(door_u,-12.35,6.0,7.55,11.15,back_v=-9.0)
# Concrete front steps in a short run at the entry, based on the repeated street-view stair profile.
for i in range(5):
    z=.12+i*.15; v=front_v+OUTWARD*(.55+i*.45)
    box('DSP_Entry_Step_%02d'%i,door_u,v,z,2.05,.47,.22,CONCRETE,.025)
# Main facade pilaster caps and window side details
for i,u in enumerate([-19.1,12.4]):
    box('DSP_Front_Corner_Pilaster',u,front_v+.02,3.6,.22,.12,6.55,STONE,.018)
# Upper facade trim at the eaves, visible under the roof edge.
box('DSP_Front_Eave_Cornice',(main_u0+main_u1)/2,front_v+OUTWARD*.07,7.35,main_u1-main_u0,.22,.2,STONE,.025)
# Roofline finials were omitted: neither GIS nor photos resolves them reliably.

# Parent all geometry to stable asset root while preserving local coordinates.
for ob in list(asset_col.objects):
    if ob is not root and ob.parent is None: ob.parent=root

# Scene setup and packed procedural material data.
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1400; scene.render.resolution_y=950; scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('DSP_Preview_World'); scene.world.use_nodes=True; scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.42,.52,.68,1); scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.8
# Library asset file itself carries geometry/materials only; preview camera/light are temporary and excluded from saved asset.
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=ASSET_FILE)

# Render external review previews using a temporary non-exported collection and neutral daylight.
rig=bpy.data.collections.new('Temporary_Preview_Rig'); scene.collection.children.link(rig)
def add_camera(name,loc_uvz,target_uvz,lens=55):
    camdata=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,camdata); rig.objects.link(cam)
    cam.location=xyz(*loc_uvz); target=Vector(xyz(*target_uvz)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); cam.data.lens=lens; return cam
def area(name,loc_uvz,energy,size,target_uvz):
    d=bpy.data.lights.new(name,'AREA'); ob=bpy.data.objects.new(name,d); rig.objects.link(ob); ob.location=xyz(*loc_uvz); ob.rotation_euler=(Vector(xyz(*target_uvz))-ob.location).to_track_quat('-Z','Y').to_euler(); d.energy=energy; d.shape='DISK'; d.size=size
area('Preview_Key',(-26,25,35),8000,22,(0,0,5)); area('Preview_Fill',(18,10,22),4200,18,(0,0,5)); area('Preview_Rim',(0,-28,26),2600,15,(0,0,6))
# Temporary grass display base for context; not part of the exported asset collection.
base=bpy.data.materials.new('Temporary_Preview_Ground'); base.diffuse_color=(.19,.24,.14,1); base.use_nodes=True; bs=base.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(.18,.23,.14,1); bs.inputs['Roughness'].default_value=.95
verts=[xyz(-28,-22,-.15),xyz(25,-22,-.15),xyz(25,30,-.15),xyz(-28,30,-.15)]
me=bpy.data.meshes.new('Temporary_Preview_Ground_Mesh'); me.from_pydata(verts,[],[(0,1,2,3)]); me.materials.append(base); ground=bpy.data.objects.new('Temporary_Preview_Ground',me); rig.objects.link(ground)
for name,loc,target,lens in [('front',(-3.5,-38,17),(-3.5,-2.5,5.5),35),('oblique',(-28,-29,16),(-3,-1,5.5),42)]:
    cam=add_camera('Preview_Camera_'+name,loc,target,lens); scene.camera=cam; scene.render.filepath=os.path.join(OUT_DIR,'delta_sigma_phi_'+name+'.png'); bpy.ops.render.render(write_still=True)
# Ensure scripts exit without writing preview rig into the saved building file.
print('ASSET_SAVED',ASSET_FILE,'polygon_area_project_m2',abs(polygon_area(POLY)),'footprint_uv_bounds',[[min(p[0] for p in POLY),max(p[0] for p in POLY)],[min(p[1] for p in POLY),max(p[1] for p in POLY)]], 'world_placement',CENTROID_WORLD)

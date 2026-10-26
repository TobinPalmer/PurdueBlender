"""Source-informed R2 repair for the 2013 HLAB building. Run on the standalone library only."""
import bpy, bmesh, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = ROOT / 'modular/buildings/ray_w_herrick_laboratories.blend'
OUT_PATH = ROOT / 'audit/ray_w_herrick_refine/ray_w_herrick_r2_candidate.blend'
AUDIT_DIR = ROOT / 'audit/ray_w_herrick_refine'
ASSET_ID = 'ray_w_herrick_laboratories'
asset = bpy.data.collections['Asset_ray_w_herrick_laboratories']
scene = bpy.context.scene
shell = bpy.data.objects['HLAB structural shell | GIS outline']
facade = bpy.data.collections.get('Facade_Details') or asset
interior = bpy.data.collections.get('Schematic_Interior') or asset

# Derive the exact authored GIS ring from the original extruded shell cap.
mesh = shell.data
bottom_faces = [p for p in mesh.polygons if all(abs(mesh.vertices[i].co.z) < 1e-5 for i in p.vertices)]
cap = max(bottom_faces, key=lambda p: len(p.vertices))
ring = [tuple(mesh.vertices[i].co[:2]) for i in reversed(list(cap.vertices))]
if len(ring) != 58:
    raise RuntimeError(f'Expected original 58-point GIS ring, got {len(ring)}')
area2 = sum(ring[i][0]*ring[(i+1)%len(ring)][1] - ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))
ccw = area2 > 0
if not ccw:
    ring.reverse()

# Remove the former solid wall shell and its generic facade overlays. Preserve GIS ring, roof, unique lab volumes, and the local root.
remove_prefixes = (
    'Facade glazing | repeated vision panels',
    'Continuous horizontal facade banding',
    'Curtainwall vertical mullions',
    'HLAB alternating brick and metal bays | pier',
    'Herrick Laboratories glazed entry canopy',
    'Herrick Labs | entry canopy',
    'Herrick Labs | entry lettering',
    'Herrick Labs | entrance name panel',
    'Herrick Labs | entry step',
    'Herrick Labs | glazed entrance doors',
    'Herrick Labs | left stone entry pier',
    'Herrick Labs | right stone entry pier',
    'RAY_W_HERRICK_LABORATORIES | schematic vestibule visible through entry',
    'RAY_W_HERRICK_LABORATORIES | schematic entry planter',
    'RAY_W_HERRICK_LABORATORIES | low planter planting',
    'RAY_W_HERRICK_LABORATORIES | schematic entry walk',
    'HLAB cast metal facade sign',
)
for obj in list(asset.all_objects):
    if obj == shell:
        continue
    if obj.name.startswith(remove_prefixes):
        bpy.data.objects.remove(obj, do_unlink=True)

# The inherited asset's over-height west/north block is not visible in the
# official 2013 photo or 2011-12 south/east elevations. It also overhangs the
# GIS footprint as a blank rooftop wall. Keep the GIS shell and source-matched
# east high-bay facade; omit this unsupported legacy volume.
legacy_wing = bpy.data.objects.get('HLAB | high-bay lab wing')
if legacy_wing is not None:
    bpy.data.objects.remove(legacy_wing, do_unlink=True)

# Create restrained procedural brick, graphite panel, pale metal, frame, and glass materials.
def material(name, color, metallic=0.0, roughness=0.45, texture='noise'):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes; links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial'); out.location=(520,40)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location=(260,40)
    bsdf.inputs['Base Color'].default_value=(*color,1.0)
    bsdf.inputs['Metallic'].default_value=metallic
    bsdf.inputs['Roughness'].default_value=roughness
    if texture == 'brick':
        tc=nodes.new('ShaderNodeTexCoord'); tc.location=(-700,80)
        brick=nodes.new('ShaderNodeTexBrick'); brick.location=(-400,120)
        brick.offset=0.5; brick.offset_frequency=2; brick.squash=1.0; brick.squash_frequency=2
        brick.inputs['Color1'].default_value=(0.40,0.13,0.075,1)
        brick.inputs['Color2'].default_value=(0.30,0.085,0.047,1)
        brick.inputs['Mortar'].default_value=(0.30,0.29,0.26,1)
        brick.inputs['Scale'].default_value=1.15
        brick.inputs['Brick Width'].default_value=0.40
        brick.inputs['Row Height'].default_value=0.105
        brick.inputs['Mortar Size'].default_value=0.008
        links.new(tc.outputs['Object'], brick.inputs['Vector'])
        links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
        noise=nodes.new('ShaderNodeTexNoise'); noise.location=(-400,-100)
        noise.inputs['Scale'].default_value=30; noise.inputs['Detail'].default_value=2.0
        links.new(tc.outputs['Object'],noise.inputs['Vector'])
        bump=nodes.new('ShaderNodeBump'); bump.location=(0,-100)
        bump.inputs['Strength'].default_value=0.14; bump.inputs['Distance'].default_value=0.018
        links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    elif texture == 'panel':
        tc=nodes.new('ShaderNodeTexCoord'); tc.location=(-500,0)
        noise=nodes.new('ShaderNodeTexNoise'); noise.location=(-280,0)
        noise.inputs['Scale'].default_value=65; noise.inputs['Detail'].default_value=2
        ramp=nodes.new('ShaderNodeValToRGB'); ramp.location=(-40,110)
        lo=tuple(max(0,min(1,v*.86)) for v in color)+(1,)
        hi=tuple(max(0,min(1,v*1.08)) for v in color)+(1,)
        ramp.color_ramp.elements[0].color=lo; ramp.color_ramp.elements[1].color=hi
        links.new(tc.outputs['Object'],noise.inputs['Vector']); links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'],bsdf.inputs['Base Color'])
        bump=nodes.new('ShaderNodeBump'); bump.location=(20,-100)
        bump.inputs['Strength'].default_value=.08; bump.inputs['Distance'].default_value=.008
        links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    elif texture == 'glass':
        tc=nodes.new('ShaderNodeTexCoord'); tc.location=(-500,0)
        noise=nodes.new('ShaderNodeTexNoise'); noise.location=(-280,0)
        noise.inputs['Scale'].default_value=2.8; noise.inputs['Detail'].default_value=1.2
        ramp=nodes.new('ShaderNodeValToRGB'); ramp.location=(-40,110)
        ramp.color_ramp.elements[0].color=(color[0]*.58,color[1]*.58,color[2]*.58,1)
        ramp.color_ramp.elements[1].color=(color[0]*1.3,color[1]*1.22,color[2]*1.18,1)
        links.new(tc.outputs['Generated'],noise.inputs['Vector']); links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'],bsdf.inputs['Base Color'])
        bsdf.inputs['Metallic'].default_value=.28; bsdf.inputs['Roughness'].default_value=.18
        bsdf.inputs['Transmission Weight'].default_value=.06
    else:
        tc=nodes.new('ShaderNodeTexCoord'); tc.location=(-500,0)
        noise=nodes.new('ShaderNodeTexNoise'); noise.location=(-280,0)
        noise.inputs['Scale'].default_value=18; noise.inputs['Detail'].default_value=2
        ramp=nodes.new('ShaderNodeValToRGB'); ramp.location=(-40,100)
        ramp.color_ramp.elements[0].color=tuple(v*.85 for v in color)+(1,)
        ramp.color_ramp.elements[1].color=tuple(min(1,v*1.12) for v in color)+(1,)
        links.new(tc.outputs['Object'],noise.inputs['Vector']); links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'],bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    return mat

brick_mat=material('HLAB R2 | Purdue red-brown brick coursing',(0.36,.105,.055),.02,.72,'brick')
panel_mat=material('HLAB R2 | pale gray architectural metal panels',(.52,.56,.55),.28,.48,'panel')
graphite_mat=material('HLAB R2 | dark graphite high-bay panels',(.10,.125,.13),.55,.34,'panel')
frame_mat=material('HLAB R2 | silver-gray aluminum frames',(.48,.53,.54),.58,.31,'panel')
glass_mat=material('HLAB R2 | blue gray reflective glazing',(.105,.225,.27),.24,.2,'glass')
concrete_mat=material('HLAB R2 | pale architectural concrete',(.64,.65,.62),.05,.76,'panel')
interior_wall_mat=material('HLAB R2 | interior painted partitions',(.78,.77,.72),0,.82,'panel')
interior_glass_mat=material('HLAB R2 | interior lab glazing',(.16,.28,.30),.12,.28,'glass')

# Combined box geometry. Local box X follows facade tangent, local Y points inward (ring is CCW), local Z is vertical.
geo={key:{'verts':[],'faces':[]} for key in ('brick','panel','graphite','frame','glass','concrete','interior','interior_glass')}
def add_box(key, center, dims, angle=0.0):
    cx,cy,cz=center; wx,wy,wz=dims; co=math.cos(angle); si=math.sin(angle)
    ix=len(geo[key]['verts'])
    for x in (-wx/2,wx/2):
        for y in (-wy/2,wy/2):
            for z in (-wz/2,wz/2):
                geo[key]['verts'].append((cx+x*co-y*si,cy+x*si+y*co,cz+z))
    # local indices 000,001,010,011,100,101,110,111
    faces=((0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6))
    geo[key]['faces'].extend(tuple(ix+i for i in f) for f in faces)
def point_on(a,u,d,inward,depth):
    return (a[0]+u[0]*d+inward[0]*depth,a[1]+u[1]*d+inward[1]*depth)
def wall_box(key,a,u,inward,d0,d1,z0,z1,thickness=.34):
    if d1-d0<=.035 or z1-z0<=.035:return
    d=(d0+d1)/2; dep=thickness/2
    px,py=point_on(a,u,d,inward,dep)
    add_box(key,(px,py,(z0+z1)/2),(d1-d0,thickness,z1-z0),math.atan2(u[1],u[0]))
def facade_pane(a,u,inward,d0,d1,z0,z1,vertical_bars=1,horizontal_bars=1):
    width=d1-d0; height=z1-z0
    if width<.35 or height<.35:return
    d=(d0+d1)/2
    px,py=point_on(a,u,d,inward,.12)
    angle=math.atan2(u[1],u[0])
    add_box('glass',(px,py,(z0+z1)/2),(width,.035,height),angle)
    frame_y=-.015
    # Perimeter frames sit slightly proud of wall face.
    for dd in (d0,d1):
        fx,fy=point_on(a,u,dd,inward,frame_y)
        add_box('frame',(fx,fy,(z0+z1)/2),(.07,.09,height+.08),angle)
    for zz in (z0,z1):
        fx,fy=point_on(a,u,d,inward,frame_y)
        add_box('frame',(fx,fy,zz),(width+.07,.09,.08),angle)
    for k in range(1,vertical_bars+1):
        dd=d0+width*k/(vertical_bars+1); fx,fy=point_on(a,u,dd,inward,frame_y)
        add_box('frame',(fx,fy,(z0+z1)/2),(.045,.085,height),angle)
    for k in range(1,horizontal_bars+1):
        zz=z0+height*k/(horizontal_bars+1); fx,fy=point_on(a,u,d,inward,frame_y)
        add_box('frame',(fx,fy,zz),(width,.085,.045),angle)

# Replace the full solid prism with GIS-edge walls containing real window openings.
story_base=.48; story_h=4.2; shell_top=13.32
exterior_edges=[]
entry_edge=None; entry_x=None; entry_y=None; entry_distance=None
for i,a in enumerate(ring):
    b=ring[(i+1)%len(ring)]; dx=b[0]-a[0]; dy=b[1]-a[1]; length=math.hypot(dx,dy)
    if length<4.0: continue
    u=(dx/length,dy/length); outward=(u[1],-u[0]); inward=(-outward[0],-outward[1])
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
    if outward[1]<-.8 and mid[1]<-25 and abs(u[1])<.08:
        if entry_edge is None or length>entry_edge['length']:
            entry_edge={'i':i,'a':a,'b':b,'u':u,'inward':inward,'length':length,'mid':mid}
if entry_edge is None:
    raise RuntimeError('No south-facing entrance facade found in the GIS ring')
entry_x=entry_edge['mid'][0]+entry_edge['u'][0]*1.25
entry_y=entry_edge['mid'][1]
entry_distance=(entry_x-entry_edge['a'][0])*entry_edge['u'][0]+(entry_y-entry_edge['a'][1])*entry_edge['u'][1]

for i,a in enumerate(ring):
    b=ring[(i+1)%len(ring)]; dx=b[0]-a[0]; dy=b[1]-a[1]; length=math.hypot(dx,dy)
    if length<.2: continue
    u=(dx/length,dy/length); outward=(u[1],-u[0]) if ccw else (-u[1],u[0]); inward=(-outward[0],-outward[1])
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2); angle=math.atan2(u[1],u[0])
    south_main=(outward[1]<-.8 and mid[1]<-25 and abs(u[1])<.08 and length>=4.0)
    east_highbay=(mid[0]>12.0 and mid[1]<-17.0)
    if length<4.0:
        wall_box('brick',a,u,inward,0,length,story_base,shell_top)
        continue
    modules=max(1,round(length/4.35)); step=length/modules
    for module in range(modules):
        d0=module*step; d1=(module+1)*step; dc=(d0+d1)/2
        cx=a[0]+u[0]*dc; cy=a[1]+u[1]*dc
        is_entry=(south_main and i==entry_edge['i'] and abs(dc-entry_distance)<step*.54)
        for story in range(3):
            z0=story_base+story*story_h; z1=min(shell_top,z0+story_h)
            if z1<=z0:continue
            highbay_clad=east_highbay and story>=1
            use_module_mat='graphite' if highbay_clad else ('panel' if (south_main or story==0) else 'brick')
            # Define each window or door opening in edge-distance coordinates.
            opening=None
            if is_entry and story==0:
                door_w=min(2.35,step-1.15); door_h=2.65
                opening=(entry_distance-door_w/2,entry_distance+door_w/2,z0+.06,z0+door_h)
            elif highbay_clad:
                opening=None
            elif south_main and story==2 and not east_highbay:
                # The published south elevation shows the living-lab office wing as a glazed upper band.
                opening=(d0+.16,d1-.16,z0+.18,z1-.15)
            elif south_main and east_highbay and story==0:
                opening=(d0+.28,d1-.28,z0+.65,z1-.36)
            else:
                win_h=2.05 if story==0 else 1.85
                sill=z0+(.7 if story==0 else .9)
                win_w=min(2.8,step-.9)
                if win_w>=1.4 and z1-(sill+win_h)>.2:
                    opening=(dc-win_w/2,dc+win_w/2,sill,sill+win_h)
            if opening:
                o0,o1,oz0,oz1=opening
                wall_box(use_module_mat,a,u,inward,d0,min(o0,d1),z0,z1)
                wall_box(use_module_mat,a,u,inward,max(o1,d0),d1,z0,z1)
                wall_box(use_module_mat,a,u,inward,max(d0,o0),min(d1,o1),z0,oz0)
                wall_box(use_module_mat,a,u,inward,max(d0,o0),min(d1,o1),oz1,z1)
                facade_pane(a,u,inward,max(d0,o0)+.08,min(d1,o1)-.08,oz0+.08,oz1-.08,
                            vertical_bars=2 if south_main and story==2 else 1,
                            horizontal_bars=2 if south_main and story==2 else 1)
            else:
                wall_box(use_module_mat,a,u,inward,d0,d1,z0,z1)
            # Structural brick piers and visible floor-level metal bands.
            if (not highbay_clad) and (module%2==0) and (south_main or story>0):
                pier_w=min(.34,step*.11)
                wall_box('brick',a,u,inward,d0,d0+pier_w,z0,z1,.42)
            if story>0 or story==0:
                bandz=z0+.08
                px,py=point_on(a,u,dc,inward,-.035)
                add_box('panel',(px,py,bandz),(step,.14,.16),angle)
            # Dark high-bay upper walls get regular vertical panel joints.
            if highbay_clad:
                for seam in range(1,max(1,round(step/1.2))):
                    sd=d0+step*seam/max(1,round(step/1.2)); sx,sy=point_on(a,u,sd,inward,-.025)
                    add_box('frame',(sx,sy,(z0+z1)/2),(.045,.07,z1-z0),angle)

# The original facade shell object keeps its stable name but now carries the full-depth GIS walls with apertures.
if shell.name in bpy.data.objects:
    bpy.data.objects.remove(shell,do_unlink=True)

def emit_group(key,name,mat,collection):
    data=geo[key]
    if not data['faces']:return None
    me=bpy.data.meshes.new(name+' | mesh'); me.from_pydata(data['verts'],[],data['faces']); me.materials.append(mat); me.update()
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    obj=bpy.data.objects.new(name,me); collection.objects.link(obj)
    return obj
# South-facing main entry. This corrects the old north-side canopy placement, based on Purdue's visitor directions.
edge=entry_edge; a=edge['a']; u=edge['u']; inward=edge['inward']; outward=(-inward[0],-inward[1]); angle=math.atan2(u[1],u[0])
def edge_center(distance, depth_from_wall=0):
    px,py=point_on(a,u,distance,inward,-depth_from_wall)
    return px,py
# Wide brick portal supports, recessed paired doors, and a shallow metal canopy.
for side in (-1,1):
    d=entry_distance+side*1.55; px,py=edge_center(d,-.03)
    add_box('brick',(px,py,2.25),(.42,.38,3.55),angle)
door_left=entry_distance-1.12; door_right=entry_distance+1.12
px,py=edge_center(entry_distance,.16); add_box('glass',(px,py,1.83),(door_right-door_left,.045,2.58),angle)
for side in (-1,1):
    d=entry_distance+side*1.12; px,py=edge_center(d,-.04); add_box('frame',(px,py,1.84),(.07,.10,2.68),angle)
px,py=edge_center(entry_distance,-.04); add_box('frame',(px,py,3.18),(2.30,.10,.10),angle)
# Split door leaves and a narrow transom; glass remains solid, reflective and readable in exterior renders.
px,py=edge_center(entry_distance,.12); add_box('frame',(px,py,1.82),(.045,.08,2.45),angle)
px,py=edge_center(entry_distance,-1.25); add_box('panel',(px,py,3.55),(6.4,2.25,.22),0)
# Re-anchor canopy local dimensions so its long side follows the front wall, with projection south.
canopy_center=edge_center(entry_distance,-1.25)
add_box('concrete',(canopy_center[0],canopy_center[1],3.45),(6.4,2.45,.22),angle)
# Concrete threshold and short accessible approach, all outside the GIS shell.
path_x,path_y=edge_center(entry_distance,-4.0)
add_box('concrete',(path_x,path_y,.10),(5.4,5.4,.20),0)
# Two shallow steps at the door threshold; the flat path remains at grade.
for step_i in range(2):
    ydist=1.55+step_i*.35
    px,py=edge_center(entry_distance,ydist)
    add_box('concrete',(px,py,.10+step_i*.08),(4.3,.38,.16),angle)
# Small low planters flank the south walk; foliage uses the project's existing foliage material.
plant_mat=bpy.data.materials.get('SITE | low evergreen planting')
planter_mat=bpy.data.materials.get('SITE | dark bronze planter')
for side in (-1,1):
    d=entry_distance+side*4.5; px,py=edge_center(d,-3.8)
    add_box('concrete',(px,py,.32),(1.6,.72,.64),angle)
    if plant_mat:
        # simple low perennial mass: discrete rounded leafy blocks, not transparent card planes
        for j in range(3):
            ox=side*(4.0+j*.28); fx,fy=edge_center(entry_distance+ox,-3.8)
            add_box('interior',(fx,fy,.86+j*.03),(.42,.42,.50),angle)
# South sign at eye level, readable and correctly located.
font=bpy.data.curves.new('HLAB south entrance sign | text','FONT'); font.body='HERRICK LABORATORIES'; font.size=.62; font.extrude=.008; font.align_x='CENTER'
sign=bpy.data.objects.new('HLAB south entrance sign | R2',font); facade.objects.link(sign)
sx,sy=edge_center(entry_distance,-.09); sign.location=(sx,sy,4.25)
sign.rotation_euler=Vector((outward[0],outward[1],0)).to_track_quat('Z','Y').to_euler(); font.materials.append(frame_mat)

# Build plan-supported, explicitly schematic interior zoning with a continuous main corridor and two stair/elevator cores.
# These dimensions are illustrative: the official floor diagram supports program zones, not survey-grade partitions.
def point_in_polygon(x,y):
    inside=False; j=len(ring)-1
    for i in range(len(ring)):
        xi,yi=ring[i]; xj,yj=ring[j]
        if ((yi>y)!=(yj>y)) and (x < (xj-xi)*(y-yi)/(yj-yi+1e-12)+xi): inside=not inside
        j=i
    return inside
def segment_inside(p0,p1,samples=24):
    return all(point_in_polygon(p0[0]+(p1[0]-p0[0])*k/samples,p0[1]+(p1[1]-p0[1])*k/samples) for k in range(samples+1))
def interior_wall_x(x,y0,y1,z,door_centers=()):
    cuts=[y0,y1]
    for center in door_centers:
        cuts.extend([max(y0,center-.48),min(y1,center+.48)])
    cuts=sorted(set(cuts))
    for lo,hi in zip(cuts[::2],cuts[1::2]):
        if hi-lo>.03 and segment_inside((x,lo),(x,hi)):
            add_box('interior',(x, (lo+hi)/2,z+1.55),(.12,hi-lo,3.1),0)
def interior_wall_y(y,x0,x1,z,door_x=()):
    cuts=[x0,x1]
    for center in door_x:
        cuts.extend([max(x0,center-.48),min(x1,center+.48)])
    cuts=sorted(set(cuts))
    for lo,hi in zip(cuts[::2],cuts[1::2]):
        if hi-lo>.03 and segment_inside((lo,y),(hi,y)):
            add_box('interior',((lo+hi)/2,y,z+1.55),(hi-lo,.12,3.1),0)

corridor_x=entry_x
floor_zs=(.48,4.68,8.88)
# Main entrance corridor aligns with the south doors and passes northward through each floor.
for floor_i,z in enumerate(floor_zs):
    cy0=-31.5; cy1=31.0
    if segment_inside((corridor_x,cy0),(corridor_x,cy1)):
        add_box('interior',(corridor_x,(cy0+cy1)/2,z+.045),(2.25,cy1-cy0,.09),0)
    # Side partitions and cross-corridor zones. Door gaps preserve continuous circulation.
    interior_wall_x(-12.0,-26.0,29.0,z,(-21,-8,7,22))
    interior_wall_x(10.5,-26.0,29.0,z,(-21,-8,7,22))
    for yy in (-20.0,-5.0,10.0,25.0):
        interior_wall_y(yy,-17.0,15.5,z,(corridor_x,))
    # Interior glass frontage is associated with the offices/living laboratory use, not the entire plan.
    if floor_i>=1:
        for yy in (-14.0,-7.0,0.0,7.0,14.0):
            if point_in_polygon(8.5,yy):
                add_box('interior_glass',(8.5,yy,z+1.55),(.035,3.0,2.45),0)
    # Corridor and lab labels lie on the floor as a schematic, not as measured room names.
    labels=[]
    if floor_i==0:
        labels=[(-8,-25,'OFFICES / PBE'),(-8,-12,'VIBRATION / ELECTROMECHANICAL'),(-8,4,'THERMAL SYSTEMS'),(-8,20,'ENGINE TEST CELLS')]
    elif floor_i==1:
        labels=[(-8,-16,'OFFICES / COLLABORATION'),(-8,5,'THERMAL / BUILDING SYSTEMS'),(-8,20,'LAB SUPPORT')]
    else:
        labels=[(-8,-18,'LIVING LABORATORIES'),(-8,1,'RECONFIGURABLE OFFICES'),(-8,19,'TEST / OBSERVATION')]
    for lx,ly,text in labels:
        if point_in_polygon(lx,ly):
            curve=bpy.data.curves.new('HLAB schematic zone label | '+text,'FONT'); curve.body=text; curve.size=.48; curve.extrude=0
            ob=bpy.data.objects.new('HLAB schematic zone label | '+text+' | floor '+str(floor_i+1),curve); interior.objects.link(ob)
            ob.location=(lx,ly,z+.10); ob.data.materials.append(interior_wall_mat)

# Two stair cores with two flights and landings between each pair of floors, plus elevator doors on the main corridor.
def stair_core(cx,cy):
    for floor_i,z in enumerate(floor_zs[:2]):
        step_count=12; tread=.25; rise=story_h/2/step_count; run=step_count*tread
        # lower flight rises away from south; upper flight returns alongside it.
        for j in range(step_count):
            zc=z+rise*(j+.5)
            add_box('concrete',(cx-.72,cy-run/2+(j+.5)*tread,zc),(1.08,tread-.025,rise),0)
        landing_z=z+story_h/2
        add_box('concrete',(cx,cy+run/2+.35,landing_z),(2.6,.70,.16),0)
        for j in range(step_count):
            zc=landing_z+rise*(j+.5)
            add_box('concrete',(cx+.72,cy+run/2-(j+.5)*tread,zc),(1.08,tread-.025,rise),0)
        # slim guardrails identify a real stair, without occupying the corridor.
        add_box('frame',(cx-.72,cy, z+1.0),(.055,run,.95),0)
        add_box('frame',(cx+.72,cy, z+story_h/2+1.0),(.055,run,.95),0)
for cx,cy in ((corridor_x+5.2,-9.0),(corridor_x-5.2,18.0)):
    if point_in_polygon(cx,cy):
        stair_core(cx,cy)
# Elevator shaft cues and corridor-facing doors at all three levels.
for cx,cy in ((corridor_x+2.0,2.0),(corridor_x-2.0,2.0)):
    if not point_in_polygon(cx,cy):continue
    for floor_i,z in enumerate(floor_zs):
        add_box('interior',(cx,cy,z+1.58),(1.9,1.7,3.16),0)
        add_box('frame',(cx,cy-.86,z+1.1),(1.0,.07,2.2),0)
        add_box('glass',(cx,cy-.81,z+1.1),(.84,.025,2.02),0)

# Add readable workstations and test-rig silhouettes where the official floor diagram places their research zones.
# Three compact test bays in the north/engine zone; the inner layout is deliberately schematic.
for j,x in enumerate((-8.5,-2.0,4.5)):
    if point_in_polygon(x,22.5):
        add_box('frame',(x,22.5,1.9),(2.9,.16,2.8),0)
        add_box('graphite',(x,22.5,3.35),(2.9,.18,.12),0)
        add_box('panel',(x,22.5,.58),(3.2,2.6,.12),0)
# Office worktables and chair/monitor cues in the Living Laboratories zone on floor three.
for x in (-10,-6,0,5,9):
    for y in (-19,-15,-11):
        if point_in_polygon(x,y) and point_in_polygon(x+1.8,y+1.0):
            z=floor_zs[2]+.78
            add_box('interior',(x,y,z),(2.0,.80,.08),0)
            add_box('frame',(x,y,z+.38),(.65,.07,.42),0)
# Emit grouped assets with normal correction and material assignment.
materials={'brick':brick_mat,'panel':panel_mat,'graphite':graphite_mat,'frame':frame_mat,'glass':glass_mat,'concrete':concrete_mat,'interior':interior_wall_mat,'interior_glass':interior_glass_mat}
for key,data in geo.items():
    if not data['faces']:continue
    name={'brick':'HLAB structural shell | GIS outline','panel':'HLAB facade | gray spandrels and wall panels R2','graphite':'HLAB facade | graphite high-bay panels R2','frame':'HLAB facade | aluminum mullions and seams R2','glass':'HLAB facade | source-matched glazing R2','concrete':'HLAB facade | entrance concrete and stairs R2','interior':'HLAB interior | connected partitions, workstations and corridor R2','interior_glass':'HLAB interior | schematic glass partitions R2'}[key]
    coll=facade if key in ('brick','panel','graphite','frame','glass','concrete') else interior
    me=bpy.data.meshes.new(name+' mesh'); me.from_pydata(data['verts'],[],data['faces']); me.materials.append(materials[key]); me.update()
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me); coll.objects.link(ob)

# Mark uncertainty in the library itself for downstream reviewers.
root_obj=bpy.data.objects.get('AssetRoot_ray_w_herrick_laboratories')
if root_obj is not None:
    root_obj['asset_revision']='R2 source-informed facade and connected schematic interior'
    root_obj['source_basis']='Purdue 2013 exterior photo; Purdue Herrick 2011-12 annual report p.15; official visitor entrance direction; GIS FID878 unchanged.'
    root_obj['uncertainty']='2012 design elevations/floor diagrams and 2013 opening photo; room dimensions, partitions, exact roof height and as-built details remain estimates.'

# Save a candidate, preserving the original source file until the author/grade loop accepts this revision.
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT_PATH),compress=True)
print(json.dumps({'status':'SAVED_CANDIDATE','asset':str(OUT_PATH),'sha256':hashlib.sha256(OUT_PATH.read_bytes()).hexdigest(),'gis_vertex_count':len(ring),'signed_area_m2':area2/2,'main_south_entry_xy_local_m':[entry_x,entry_y],'object_count':len(asset.all_objects),'mesh_count':sum(o.type=='MESH' for o in asset.all_objects),'unique_materials':len({m.name for o in asset.all_objects if o.type=='MESH' for m in o.data.materials if m})},indent=2))

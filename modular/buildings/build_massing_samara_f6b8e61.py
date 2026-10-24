import bpy, math, json, pathlib
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[2]
E=ROOT/'audit'/'samara'; E.mkdir(exist_ok=True)
ID='massing_samara_f6b8e61'
OUT=ROOT/'modular'/'buildings'/(ID+'.blend')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene; scene.name='Building_'+ID
asset=bpy.data.collections.new('Asset_'+ID); scene.collection.children.link(asset)
preview=bpy.data.collections.new('Preview_samara'); scene.collection.children.link(preview)
# Digitized from HABS IN-247 sheet 3, 1024x683 derivative, calibrated against 85 ft 7-7/8 in dimension.
S=(85+7.875/12)*.3048/(813-206)
ANG=math.radians(-63.5); U=Vector((math.cos(ANG),math.sin(ANG))); V=Vector((-math.sin(ANG),math.cos(ANG)))
# Lower roof trace includes the open carport, unlike enclosed walls.
roof=[(192,208),(229,208),(229,177),(425,177),(425,94),(594,94),(594,178),(741,178),(741,270),(768,270),(768,370),(563,370),(563,397),(438,397),(438,584),(310,584),(310,397),(254,397),(254,322),(192,322)]
base=[(206,220),(240,220),(240,190),(438,190),(438,106),(582,106),(582,190),(727,190),(727,281),(755,281),(755,357),(548,357),(548,383),(267,383),(267,310),(206,310)]
def rel(p): return (Vector(((p[0]-500)*S,(300-p[1])*S)))
pts=[U*rel(p).x+V*rel(p).y for p in roof]
osm=json.load(open(E/'osm_samara_snapshot.json'))['world_xy']; target=Vector(((min(p[0] for p in osm)+max(p[0] for p in osm))/2,(min(p[1] for p in osm)+max(p[1] for p in osm))/2))
anchor=target-Vector(((min(p.x for p in pts)+max(p.x for p in pts))/2,(min(p.y for p in pts)+max(p.y for p in pts))/2))
def world(p,z):
 q=rel(p); r=anchor+U*q.x+V*q.y; return (r.x,r.y,z)
def mat(n,c,metal=0,rough=.5):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*c,1); bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough; return m
brick=mat('Samara red Attica brick',(0.33,.095,.065)); wood=mat('Philippine mahogany',(.21,.085,.035)); copper=mat('Patinated copper fascia',(.105,.32,.27),.65,.42); roofmat=mat('White marble gravel roof',(.58,.58,.52),0,.9); floor=mat('Cherokee red concrete',(.32,.115,.065)); mortar=mat('Raked horizontal mortar',(.36,.29,.22)); dark=mat('Hearth opening',(.025,.02,.015)); glass=mat('Clear glazing',(.16,.24,.22),.12,.15)
bs=glass.node_tree.nodes.get('Principled BSDF'); bs.inputs['Transmission Weight'].default_value=.65
# Brick scale uses world position rotated into the drawing frame; running bond and raked mortar are shader detail.
nt=brick.node_tree; tex=nt.nodes.new('ShaderNodeTexBrick'); tex.inputs['Scale'].default_value=1; tex.inputs['Mortar Size'].default_value=.009; tex.inputs['Brick Width'].default_value=.245; tex.inputs['Row Height'].default_value=.07; tex.inputs['Color1'].default_value=(.32,.10,.075,1); tex.inputs['Color2'].default_value=(.43,.16,.12,1); tex.inputs['Mortar'].default_value=(.19,.14,.105,1)
coord=nt.nodes.new('ShaderNodeTexCoord'); sep=nt.nodes.new('ShaderNodeSeparateXYZ'); comb=nt.nodes.new('ShaderNodeCombineXYZ'); nt.links.new(coord.outputs['Generated'],tex.inputs['Vector'])
# Override with world position and rotate so mortar stays horizontal on all walls.
geo=nt.nodes.new('ShaderNodeNewGeometry'); separate=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Position'],separate.inputs[0]); combine=nt.nodes.new('ShaderNodeCombineXYZ'); add=nt.nodes.new('ShaderNodeMath'); add.operation='ADD'; nt.links.new(separate.outputs['X'],add.inputs[0]); nt.links.new(separate.outputs['Y'],add.inputs[1]); nt.links.new(add.outputs[0],combine.inputs['X']); nt.links.new(separate.outputs['Z'],combine.inputs['Y']); nt.links.new(combine.outputs[0],tex.inputs['Vector']); nt.links.new(tex.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color']); bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.18; bump.inputs['Distance'].default_value=.015; nt.links.new(tex.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs[0],nt.nodes.get('Principled BSDF').inputs['Normal'])
def obj(n,verts,faces,m,col=asset):
 me=bpy.data.meshes.new(n); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new(n,me); col.objects.link(o); o.data.materials.append(m); return o
def prism(n,poly,z0,z1,m,col=asset):
 N=len(poly); return obj(n,[world(p,z) for z in (z0,z1) for p in poly],[tuple(reversed(range(N))),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],m,col)
def box(n,x0,y0,x1,y1,z0,z1,m): return prism(n,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,m)
def line(n,a,b,z0,z1,width,m):
 a=Vector(a); b=Vector(b); d=b-a; p=Vector((-d.y,d.x)).normalized()*(width/S/2); return prism(n,[a+p,b+p,b-p,a-p],z0,z1,m)
def wall(n,a,b,z0,z1,m=brick,w=.26): return line(n,a,b,z0,z1,w,m)
# Structural slabs and walls follow survey, not roof outline.
def point_inside(p,poly):
 x,y=p; yes=False
 for i,(ax,ay) in enumerate(poly):
  bx,by=poly[(i+1)%len(poly)]
  if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax: yes=not yes
 return yes
def cut_slab(n,poly,hole,z0,z1,m):
 # Exact rectangular partition, retaining source outline while omitting void cells.
 xs=sorted(set([p[0] for p in poly]+[hole[0],hole[2]])); ys=sorted(set([p[1] for p in poly]+[hole[1],hole[3]])); vs=[]; fs=[]
 for xa,xb in zip(xs,xs[1:]):
  for ya,yb in zip(ys,ys[1:]):
   mid=((xa+xb)/2,(ya+yb)/2)
   if not point_inside(mid,poly) or (hole[0]<mid[0]<hole[2] and hole[1]<mid[1]<hole[3]):continue
   poly4=[(xa,ya),(xb,ya),(xb,yb),(xa,yb)]; off=len(vs); vs.extend([world(p,z) for z in (z0,z1) for p in poly4]); fs.extend([tuple(off+i for i in f) for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
 return obj(n,vs,fs,m)
cut_slab('Survey structural floor footprint',base,(525,190,727,318),-.14,0,floor)
# Segment table: low walls where windows float above, full brick on private/service elevations.
segments=[((206,220),(240,220),2.05),((240,220),(240,190),2.05),((240,190),(438,190),1.04),((438,190),(438,106),2.8),((438,106),(582,106),2.8),((582,106),(582,190),1.03),((582,190),(727,190),.03),((727,190),(727,281),.03),((727,281),(755,281),1.03),((755,281),(755,357),2.8),((755,357),(548,357),2.8),((548,357),(548,383),.03),((548,383),(267,383),.03),((267,383),(267,310),.03),((267,310),(206,310),2.05),((206,310),(206,220),2.05)]
# Living room is 1 ft 10 in below entrance datum (HABS sections 6).
for i,(a,b,h) in enumerate(segments):
 if h>.05 and i!=10: wall('Structural_wall_%02d'%i,a,b,0,h)
# Entry doors and three narrow vertical windows on full foyer facade, as southeast elevation.
# Replace continuous foyer wall with narrow glazed recesses overlaid against wall face, geometric inset.
# True through-apertures: full wall is split at jambs, sill and head; pane centered in opening.
foyer_windows=(620,650,680); cursor=548
for x in foyer_windows:
 wall('Structural_wall_10_pier_'+str(x),(cursor,357),(x-4,357),0,2.8)
 wall('Structural_wall_10_sill_'+str(x),(x-4,357),(x+4,357),0,.75)
 wall('Structural_wall_10_head_'+str(x),(x-4,357),(x+4,357),2.42,2.8)
 box('Narrow_foyer_light_'+str(x),x-3.4,356.7,x+3.4,357.3,.79,2.38,glass)
 for j in (x-4,x+4):box('Foyer_mahogany_jamb_'+str(x)+'_'+str(j),j-.6,353.9,j+.6,360.1,.75,2.42,wood)
 for z in (.75,2.42):box('Foyer_mahogany_head_sill_'+str(x)+'_'+str(z),x-4,353.9,x+4,360.1,z-.025,z+.025,wood)
 cursor=x+4
wall('Structural_wall_10_end',(cursor,357),(755,357),0,2.8)
# Standard framed glazing is actual separated panels, not painted window stripes.
def glazing(n,a,b,z0,z1,spacing=1.22,clerestory=False):
 length=(Vector(b)-Vector(a)).length*S; count=max(1,round(length/spacing)); av=Vector(a); bv=Vector(b)
 wall(n+'_glass',a,b,z0,z1,glass,.035)
 for z in (z0,z1): wall(n+'_rail',a,b,z-.035,z+.035,wood,.09)
 for i in range(count+1):
  q=av+(bv-av)*i/count; wall(n+'_mullion_%02d'%i,q-Vector((.4,0)),q+Vector((.4,0)),z0,z1,wood,.075)
 if clerestory:
  for i in range(count):
   c=av+(bv-av)*(i+.5)/count; tangent=(bv-av).normalized(); half=min(.35,length/count*.32)/S
   # angular seed motif, stylized geometry matching HABS/foundation description; proportions estimated.
   a1=c-tangent*half; a2=c+tangent*half
   beam3(n+'_seed_left',world(a1,z0+.12),world(c,z1-.10),.025,wood)
   beam3(n+'_seed_right',world(c,z1-.10),world(a2,z0+.12),.025,wood)
def beam3(n,a,b,width,m):
 av=Vector(a); bv=Vector(b); d=(bv-av).normalized(); cross=d.cross(Vector((0,0,1)))
 if cross.length<.01:cross=d.cross(Vector((0,1,0)))
 p=cross.normalized()*width/2; q=d.cross(p).normalized()*width/2
 vv=[tuple(c+dx*p+dy*q) for c in (av,bv) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 return obj(n,vv,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
glazing('Bedroom_high_band',(240,190),(438,190),1.06,2.05)
glazing('Dining_garden_doors',(582,106),(582,190),1.05,2.76,.98)
glazing('Living_garden_glazing',(582,190),(727,190),-.55,2.02,1.22)
glazing('Living_mitered_corner',(727,190),(727,281),-.55,2.02,1.22)
glazing('Study_garden_doors',(267,383),(438,383),0,2.03,1.22)
glazing('Study_end_glazing',(267,310),(267,383),0,2.03,1.22)
glazing('Entry_glass_and_mahogany',(438,383),(548,383),0,2.03,1.1)
# Open living floor, sunken by 22 in, internal hearth and service core.
DROP=22*.0254
box('Sunken_living_red_floor',525,190,727,318,-DROP-.09,-DROP,floor)
# Three transition treads interpreted from HABS sheet3 UP lines and section6 drop.
for i in range(3):
 top=-DROP+(i+1)*DROP/3
 box('Living_foyer_step_'+str(i+1),540,300+i*6,727,306+i*6,-DROP-.09,top,floor)
for i in range(3):
 top=-i*DROP/3
 box('Living_dining_step_'+str(i+1),550,190+i*6,610,196+i*6,-DROP-.09,top,floor)
wall('Central_hearth_back',(514,241),(514,311),-.56,2.9)
wall('Hearth_left_return',(514,241),(542,241),-.56,2.9)
box('Hearth_firebox',516,254,518,289,-.36,.83,dark)
wall('Hearth_lintel',(516,254),(516,289),.83,1.10,brick,.4)
box('Hearth_projecting_slab',515,290,548,310,-.56,-.39,brick)
# Central chimney at survey's fireplace; current copper cap is documented in 2026 owner update.
box('Red_brick_chimney',497,239,528,274,2.7,4.382,brick)
box('2026_patinated_chimney_cap',494,236,531,277,4.382,4.47,copper)
for a,b in [((438,190),(438,280)),((438,280),(500,280)),((298,190),(298,280)),((298,280),(382,280)),((382,280),(382,383))]: wall('Interior_partition',a,b,0,2.02)
# Two levels per HABS elevation: low soffit 6 ft 7-3/4 in, upper roof surface 9 ft 6-1/2 in.
LOW=(6+7.75/12)*.3048; HIGH=(9+6.5/12)*.3048
cut_slab('Lower_cantilever_roof',roof,(425,94,768,370),LOW,LOW+.19,roofmat)
# Raised roof through the public core, with mahogany framed clerestory on exposed margins.
upper=[(425,94),(594,94),(594,177),(768,177),(768,370),(425,370)]
prism('Upper_flat_roof',upper,HIGH-.19,HIGH,roofmat)
for i,a in enumerate(upper): glazing('Clerestory_%d'%i,a,upper[(i+1)%len(upper)],LOW+.20,HIGH-.20,.85,True)
# Roof fascia perimeter and repeated folded copper samara ornaments.
def fascia(poly,z,n,ornament=True):
 for i,a in enumerate(poly):
  b=poly[(i+1)%len(poly)]; wall(n+'_copper_band_%d'%i,a,b,z-.045,z+.18,copper,.10)
  if ornament:
   av=Vector(a); bv=Vector(b); d=(bv-av); N=max(1,round(d.length*S/.88)); tangent=d.normalized(); normal=Vector((-tangent.y,tangent.x))
   for j in range(N):
    c=av+d*(j+.5)/N; w=min(.43,d.length*S/N*.45)/S
    # Deep folded sheet profile, derived from Foundation close photograph.
    # Each trapezoid drops below roof datum and leans outward at its upper wings.
    # Dimensions are photograph interpretations: 0.44m vertical, 0.16m return.
    outward=-normal
    loL=c-tangent*w*.72; loR=c+tangent*w*.72
    hiL=c-tangent*w+outward*(.16/S); hiR=c+tangent*w+outward*(.16/S)
    mid=c+outward*(.10/S)
    vv=[world(loL,z-.16),world(loR,z-.16),world(hiR,z+.28),world(hiL,z+.28),world(mid,z+.02)]
    ob=obj(n+'_folded_seed_%d_%d'%(i,j),vv,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],copper)
    for aa,bb in [(vv[0],vv[1]),(vv[1],vv[2]),(vv[2],vv[3]),(vv[3],vv[0]),(vv[0],vv[4]),(vv[1],vv[4])]:beam3(n+'_folded_panel_rib',aa,bb,.025,copper)
fascia(roof,LOW,'Lower_fascia'); fascia(upper,HIGH-.19,'Upper_fascia',False)
# Terrace boundaries and brick planters from survey; terrace is not counted as wall footprint.
terr=[(582,118),(813,118),(813,299),(755,299),(755,357),(548,357),(548,410),(383,410),(383,438),(641,438),(641,383),(267,383),(267,394),(548,394),(548,370),(768,370),(768,313),(827,313),(827,106),(582,106)]
# use clear separate slabs, avoiding a self intersecting terrace polygon.
for n,x0,y0,x1,y1 in [('Garden_terrace_north',582,118,813,190),('Garden_terrace_east',727,190,813,300),('Entrance_terrace',383,383,641,438)]: box(n,x0,y0,x1,y1,-.20,-.05,floor)
for a,b in [((582,118),(813,118)),((813,118),(813,299)),((813,299),(755,299)),((755,299),(755,357))]: wall('Terrace_brick_parapet',a,b,-.2,.76,brick,.26)
# Pergola beams at northeast terrace above living garden doors, following sheet 3 plan rhythm.
for x in range(590,814,28): wall('Garden_pergola_beam',(x,118),(x,190),LOW,LOW+.17,wood,.12)
# Tool crib structural support for open carport roof, from plan sheet 3.
crib=[(322,550),(359,550),(359,542),(380,542),(380,550),(417,550),(417,583),(322,583)]
prism('Tool_crib_carport_support',crib,0,LOW,brick)
box('Tool_crib_door',359,541,380,544,0,1.83,wood)
box('Carport_red_slab',310,397,438,584,-.22,-.12,floor)
# Roof metadata, wall-footprint metadata, reproducible source registration.
for o in asset.objects: o['building_id']=ID
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
asset['coordinate_frame']='Campus world geometry; collection instance offset zero; identity master placement retained'
asset['source']='HABS IN-247 sheets 2-6 (2020 field survey, 2021 documentation); OSM way 1096999543; FLW Foundation photo; official 2026 copper update'
asset['uncertainty']='Plan digitization ±0.15 m; registration ±2 m; roof trace ±0.5 m; decorative tab detail simplified; no site topography or full furnished interior'
# Presentation helpers kept outside exported collection.
ground=mat('Preview ground',(.22,.26,.19)); p=[(150,70),(850,70),(850,620),(150,620)]; prism('Preview ground only',p,-.35,-.3,ground,preview)
worldmat=bpy.data.worlds.new('Samara daylight'); scene.world=worldmat; worldmat.use_nodes=True; worldmat.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.85,1); worldmat.node_tree.nodes['Background'].inputs[1].default_value=.6
ld=bpy.data.lights.new('Preview sun','SUN'); ld.energy=3; lo=bpy.data.objects.new('Preview sun',ld); preview.objects.link(lo); lo.rotation_euler=(.5,-.4,-.5)
camd=bpy.data.cameras.new('Preview camera'); cam=bpy.data.objects.new('Preview camera',camd); preview.objects.link(cam); scene.camera=cam; camd.type='ORTHO'; camd.ortho_scale=43
scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.render.resolution_x=1400; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'; scene.render.image_settings.file_format='PNG'
def aim(loc,target): cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
center=Vector((target.x,target.y,1)); aim(center+Vector((32,-35,29)),center)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
scene.render.filepath=str(E/'preview_southeast.png'); bpy.ops.render.render(write_still=True)
aim(center+Vector((-32,29,26)),center); scene.render.filepath=str(E/'preview_northwest.png'); bpy.ops.render.render(write_still=True)
aim(center+Vector((0,0,50)),center); camd.ortho_scale=42; scene.render.filepath=str(E/'preview_top.png'); bpy.ops.render.render(write_still=True)
record={'id':ID,'asset':str(OUT.relative_to(ROOT)),'collection':asset.name,'scene':scene.name,'anchor_world_m':list(anchor),'drawing_pixel_scale_m':S,'drawing_x_world_angle_deg':-63.5,'registration_method':'fixed HABS scale; orientation from OSM roof edge; translation aligning roof bounds centers only, no plan rescaling','plan_trace_pixels':base,'roof_trace_pixels':roof,'structural_height_m':{'low_soffit':LOW,'upper_surface':HIGH,'chimney_survey':4.382},'objects':len(asset.objects),'source_footprint':osm,'wall_footprint_world':[world(p,0) for p in base],'bounds_roof_world':[world(p,LOW) for p in roof],'uncertainties':['Horizontal translation +/-2m from roof correspondence; no independent surveyed georeference','Roof outline digitization and overhangs approx +/-0.5m','HABS heights measured relative entrance; campus ground datum 0 is inherited','Copper motif simplified, exterior detail proportions partly estimated','Terrace and carport modeled; landscaping and furniture not fully reconstructed']}
json.dump(record,open(E/'build_record.json','w'),indent=2)
print('SAMARA_BUILD_COMPLETE',len(asset.objects),anchor)

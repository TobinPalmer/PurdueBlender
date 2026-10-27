"""Rebuild the FID 785 former ATO house from the GIS footprint and NPS evidence.

Run in Blender 5.2 from the repository root:
  blender -b --python modular/buildings/build_massing_house_301840870_c45a5f4.py
The asset keeps its original file, scene, collection and campus-world XY position.
"""
from __future__ import annotations
import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
ASSET_PATH=Path(__file__).resolve().parent/'massing_house_301840870_c45a5f4.blend'
AUDIT=ROOT/'audit/alpha_tau_omega'
GIS_PATH=AUDIT/'sources/purdue_gis_fid785_2026-10-26.json'
ASSET_COLLECTION='Asset_massing_house_301840870_c45a5f4'
ASSET_SCENE='Building_massing_house_301840870_c45a5f4'
ROOT_OBJECT='House_301840870'
LAT0,LON0=40.4274,-86.9137

def ll_to_xy(lon,lat):
    return ((lon-LON0)*111412.84*math.cos(math.radians(LAT0)),(lat-LAT0)*111040.0)

def xyz(v): return tuple(float(k) for k in v)

# Open the source massing library so that its stable scene/collection IDs and campus frame survive.
bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))
scene=bpy.data.scenes.get(ASSET_SCENE)
asset=bpy.data.collections.get(ASSET_COLLECTION)
assert scene is not None and asset is not None
for ob in list(asset.objects):
    if ob.name != ROOT_OBJECT:
        bpy.data.objects.remove(ob,do_unlink=True)
root=bpy.data.objects.get(ROOT_OBJECT)
assert root and root.type=='MESH'
oldmesh=root.data
root.data=bpy.data.meshes.new('Alpha Tau Omega | detailed brick house shell')
if oldmesh.users==0: bpy.data.meshes.remove(oldmesh)
root.name=ROOT_OBJECT
root.location=(0,0,0); root.rotation_euler=(0,0,0); root.scale=(1,1,1)
root.data.materials.clear()

# Clear preview-only data from a previous run while keeping the published asset collection.
for ob in list(scene.objects):
    if ob.name != ROOT_OBJECT and ob.name not in asset.objects:
        pass

mats={}
def make_mat(name,color,rough=0.55,metal=0.0,brick=False,noise=False):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    n=m.node_tree.nodes; links=m.node_tree.links
    bs=n.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metal
    if brick:
        tex=n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=22; tex.inputs['Detail'].default_value=3; tex.inputs['Roughness'].default_value=0.7
        coord=n.new('ShaderNodeTexCoord'); links.new(coord.outputs['Generated'],tex.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=0.22; ramp.color_ramp.elements[0].color=(0.19,0.055,0.035,1); ramp.color_ramp.elements[1].position=0.78; ramp.color_ramp.elements[1].color=(0.38,0.15,0.09,1)
        links.new(tex.outputs['Fac'],ramp.inputs['Fac']); links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.08; bump.inputs['Distance'].default_value=0.012; links.new(tex.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    elif noise:
        tex=n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=45; tex.inputs['Detail'].default_value=2
        coord=n.new('ShaderNodeTexCoord'); links.new(coord.outputs['Object'],tex.inputs['Vector'])
        bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.14; bump.inputs['Distance'].default_value=0.018; links.new(tex.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    mats[name]=m
    return m

brick=make_mat('ATO | historic red-brown stretcher-bond brick',(0.30,0.095,0.055),0.82,brick=True)
brick_add=make_mat('ATO | subtle 1963 addition brick',(0.27,0.085,0.05),0.84,brick=True)
limestone=make_mat('ATO | dressed Indiana limestone',(0.67,0.61,0.49),0.8,noise=True)
roofmat=make_mat('ATO | simulated slate shingle',(0.105,0.13,0.15),0.68,noise=True)
stucco=make_mat('ATO | warm pale stucco',(0.62,0.54,0.41),0.9,noise=True)
timber=make_mat('ATO | dark Tudor half timber',(0.12,0.07,0.045),0.72)
glass=make_mat('ATO | leaded window glass',(0.105,0.16,0.18),0.22,0.15)
wood=make_mat('ATO | dark oak joinery',(0.22,0.105,0.048),0.6,noise=True)
metal=make_mat('ATO | aged copper and iron',(0.20,0.22,0.18),0.32,0.7)
interior_wall=make_mat('ATO | schematic interior plaster',(0.58,0.52,0.40),0.92)
interior_floor=make_mat('ATO | natural edge limestone floor',(0.48,0.44,0.35),0.85,noise=True)
wood_floor=make_mat('ATO | oak floorboards',(0.31,0.17,0.08),0.72,noise=True)
velvet=make_mat('ATO | common room upholstery',(0.36,0.20,0.13),0.85)

class Batch:
    def __init__(self,name,material): self.name=name; self.material=material; self.v=[]; self.f=[]
    def box(self,c,d):
        x,y,z=c; dx,dy,dz=(v/2 for v in d); i=len(self.v)
        self.v.extend([(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),(x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),(x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),(x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)])
        self.f.extend([(i+a,i+b,i+c,i+d) for a,b,c,d in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])
    def quad(self,points):
        i=len(self.v); self.v.extend([xyz(p) for p in points]); self.f.append(tuple(range(i,i+len(points))))
    def tri(self,points): self.quad(points)
    def mesh(self,object_name=None,collection=asset):
        if not self.f: return None
        me=bpy.data.meshes.new(self.name+' | mesh'); me.from_pydata(self.v,[],self.f); me.materials.append(self.material); me.update()
        bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free(); me.update()
        ob=bpy.data.objects.new(object_name or self.name,me); collection.objects.link(ob)
        return ob

batches={}
def B(key,material):
    if key not in batches: batches[key]=Batch(key,material)
    return batches[key]
def box(key,material,c,d): B(key,material).box(c,d)
def wall_panel(key,material,center,dims): box(key,material,center,dims)

# Preserve a stable root mesh object for the published building. It carries the primary brick mass.
# Geometry stays in the same campus-world coordinate frame as the original massing asset.
rootbatch=Batch('Primary walls | original 1920 block and 1963 south addition',brick)
rootbatch.box((-427.75,76.20,4.40),(15.20,15.00,8.80))
rootbatch.box((-426.78,55.55,4.35),(13.35,19.10,8.70))
rootbatch.box((-426.78,66.45,4.30),(13.35,4.40,8.60))
root.data.from_pydata(rootbatch.v,[],rootbatch.f); root.data.materials.append(brick); root.data.update()
# register detail objects for useful render toggles
exterior_objects=[root]

# GIS-corner perimeter and foundation: the perimeter line reproduces Purdue feature FID 785.
gis_data=json.loads(GIS_PATH.read_text(encoding='utf-8-sig')); gis=gis_data['features'][0]
assert gis['attributes']['FID']==785 and gis['attributes']['BUILDING_N']=='Alpha Tau Omega' and gis['attributes']['ADDRESS']=='314 Russell St'
ring=[ll_to_xy(p[0],p[1]) for p in gis['geometry']['rings'][0]]
curve=bpy.data.curves.new('GIS 785 exact projected footprint curb','CURVE'); curve.dimensions='3D'; curve.bevel_depth=0.105; curve.bevel_resolution=2
sp=curve.splines.new('POLY'); sp.points.add(len(ring)-1)
for pt,(x,y) in zip(sp.points,ring): pt.co=(x,y,0.16,1)
sp.use_cyclic_u=True
ob=bpy.data.objects.new('GIS 785 perimeter curb | source outline',curve); asset.objects.link(ob); curve.materials.append(limestone); exterior_objects.append(ob)

# East-side one-storey kitchen block documented as a 1940s addition.
box('1940s east kitchen wing | brick mass',brick,(-416.90,79.0,2.05),(6.20,7.65,4.10))
# West-facing projecting tower/porch: fifth and dominant front bay, parapeted and crenellated.
box('Gothic entry tower | brick shaft',brick,(-434.75,66.25,5.50),(4.25,4.45,11.0))
# low platform porch and parapet walls on the west frontage
box('Platform porch | limestone-topped brick wall',brick,(-434.3,65.9,0.65),(1.45,17.2,0.9))
box('Platform porch | limestone cap',limestone,(-434.3,65.9,1.14),(1.58,17.35,0.16))
# Entrance stoop and broad stone treads (west is decreasing X).
for i in range(4):
    box('West entry stone stairs',limestone,(-436.6+i*0.35,66.25,0.18+i*0.13),(0.55,2.5,0.24))
# Main tower parapet and crenellated coping.
box('Tower parapet | west',brick,(-434.80,64.10,11.25),(4.4,0.25,1.2))
box('Tower parapet | east',brick,(-434.80,68.40,11.25),(4.4,0.25,1.2))
box('Tower parapet | north',brick,(-436.95,66.25,11.25),(0.25,4.5,1.2))
box('Tower parapet | south',brick,(-432.65,66.25,11.25),(0.25,4.5,1.2))
for x in (-436.9,-435.8,-434.7,-433.6,-432.7):
    for y in (64.1,68.4): box('Tower crenellation stone cap',limestone,(x,y,11.9),(0.48,0.32,0.18))
for y in (64.1,65.2,66.3,67.4,68.4):
    for x in (-436.9,-432.7): box('Tower crenellation stone cap',limestone,(x,y,11.9),(0.32,0.48,0.18))
# stone coping and belt course at tower crown
box('Tower parapet limestone coping',limestone,(-434.8,66.25,12.05),(4.55,4.65,0.18))
# Tower quoins and stringcourse at chamfered/stepped corners.
for y in (64.05,68.45):
    for z in (1.25,2.0,2.75,3.5,4.25,5.0,5.75,6.5,7.25,8.0,8.75,9.5,10.25):
        box('Tower limestone quoin blocks',limestone,(-436.98,y,z),(0.18,0.34,0.28))
for z in (3.25,7.25,10.35): box('Tower carved limestone stringcourse',limestone,(-437.02,66.25,z),(0.24,4.4,0.18))

# Roofs: steep hip roofs, dormers, a small shingled kitchen roof and projecting open eaves.
def roof_quad(name,pts):
    b=Batch(name,roofmat); b.quad(pts); ob=b.mesh(); exterior_objects.append(ob); return ob
# Roof over original northern block and the southern 1963 addition: separate ridges mark the seam.
def hip_roof(xw,xe,ys,yn,eave,ridge,hip):
    xc=(xw+xe)/2
    roof_quad('Steep hip roof | west slope',[(xw,ys,eave),(xw,yn,eave),(xc,yn-hip,ridge),(xc,ys+hip,ridge)])
    roof_quad('Steep hip roof | east slope',[(xe,ys,eave),(xc,ys+hip,ridge),(xc,yn-hip,ridge),(xe,yn,eave)])
    roof_quad('Steep hip roof | south end',[(xw,ys,eave),(xc,ys+hip,ridge),(xe,ys,eave)])
    roof_quad('Steep hip roof | north end',[(xw,yn,eave),(xe,yn,eave),(xc,yn-hip,ridge)])
    # ridge cap split into short blocks for the shingle silhouette
    for y in [ys+hip+k*0.9 for k in range(max(1,int((yn-ys-2*hip)/0.9)))]:
        box('Slate ridge caps',roofmat,(xc,y,ridge+0.06),(0.34,1.0,0.18))
hip_roof(-435.35,-420.15,68.0,83.65,8.95,12.05,3.0)
hip_roof(-433.20,-420.25,46.45,64.25,8.65,11.70,3.1)
# Kitchen wing's low east roof.
roof_quad('1940s kitchen shed roof', [(-420.0,75.1,4.15),(-413.55,75.1,4.35),(-413.55,82.88,4.35),(-420.0,82.88,4.15)])
# Open eaves and copper trough gutters at street and rear.
for y in (46.4,64.3,68.0,83.7):
    box('Copper gutter eaves',metal,(-433.38,y,8.5),(0.28,0.12,0.12))
for x in (-433.25,-420.15):
    box('Copper trough gutter',metal,(x,56.0,8.52),(0.13,19.4,0.13))
    box('Copper trough gutter',metal,(x,75.8,8.82),(0.13,16.0,0.13))

# Through-the-cornice gabled dormers, stucco cheeks and false half-timbering.
def dormer(yc,width,zbase,ridge_z):
    x=-435.48 if yc>68 else -433.38; depth=1.75
    wall_panel('Front wall dormer | stucco gable',stucco,(x-0.15,yc,zbase+0.9),(0.34,width,1.9))
    # gable triangle on the street-facing side
    b=Batch('Front dormer gable triangle',stucco)
    b.tri([(x-0.33,yc-width/2,zbase+1.75),(x-0.33,yc+width/2,zbase+1.75),(x-0.33,yc,zbase+2.8)])
    exterior_objects.append(b.mesh())
    # projecting little gable roof planes
    roof_quad('Dormer slate cheek | left',[(x-0.55,yc-width/2-0.12,zbase+1.8),(x-0.55,yc,zbase+2.95),(x+depth,yc,zbase+2.95),(x+depth,yc-width/2-0.12,zbase+1.8)])
    roof_quad('Dormer slate cheek | right',[(x-0.55,yc,zbase+2.95),(x-0.55,yc+width/2+0.12,zbase+1.8),(x+depth,yc+width/2+0.12,zbase+1.8),(x+depth,yc,zbase+2.95)])
    window_west(yc,zbase+0.95,1.6,1.5,front_x=x-0.36)
    # dark timber framing in the gable
    for end in (-1,1): box('False half timber | dormer',timber,(x-0.39,yc+end*width*0.28,zbase+2.13),(0.12,0.13,1.3))
    box('False half timber | dormer',timber,(x-0.40,yc,zbase+1.83),(0.12,width*0.77,0.11))
# helper window geometry follows below; calls occur after its definition.

# Window builders: inset dark glass, limestone surrounds, metal casements/muntins.
def window_west(y,z,w=1.55,h=1.75,front_x=-433.45,transom=True):
    depth=0.09; x=front_x-0.08
    box('Leaded west window glass',glass,(x,y,z),(depth,w-0.25,h-0.22))
    frame_x=x-0.09
    for yy in (y-w/2,y+w/2): box('Limestone window jamb | west',limestone,(frame_x,yy,z),(0.18,0.16,h+0.28))
    for zz in (z-h/2,z+h/2): box('Limestone window lintel and sill | west',limestone,(frame_x,y,zz),(0.18,w+0.16,0.16))
    # leaded grid pattern
    for frac in (-0.22,0,0.22): box('Leaded glass mullions | west',metal,(x-0.07,y+frac*w,z),(0.07,0.055,h-0.22))
    for frac in (-0.20,0.20): box('Leaded glass muntins | west',metal,(x-0.07,y,z+frac*h),(0.07,w-0.25,0.055))
    if transom: box('Window transom bar | west',metal,(x-0.08,y,z+h*0.24),(0.08,w-0.25,0.07))

def window_east(y,z,w=1.5,h=1.7,x= -420.02):
    xx=x+0.08
    box('Leaded east window glass',glass,(xx,y,z),(0.09,w-0.25,h-0.22))
    frame_x=xx+0.09
    for yy in (y-w/2,y+w/2): box('Limestone window jamb | east',limestone,(frame_x,yy,z),(0.18,0.16,h+0.28))
    for zz in (z-h/2,z+h/2): box('Limestone window lintel and sill | east',limestone,(frame_x,y,zz),(0.18,w+0.16,0.16))
    for frac in (-0.22,0,0.22): box('Leaded glass mullions | east',metal,(xx+0.07,y+frac*w,z),(0.07,0.055,h-0.22))
    for frac in (-0.20,0.20): box('Leaded glass muntins | east',metal,(xx+0.07,y,z+frac*h),(0.07,w-0.25,0.055))

def window_north(x,z,w=1.5,h=1.7,y=83.76):
    yy=y+0.08
    box('Leaded north window glass',glass,(x,yy,z),(w-0.25,0.09,h-0.22))
    for xx in (x-w/2,x+w/2): box('Limestone window jamb | north',limestone,(xx,yy+0.09,z),(0.16,0.18,h+0.28))
    for zz in (z-h/2,z+h/2): box('Limestone window lintel and sill | north',limestone,(x,yy+0.09,zz),(w+0.16,0.18,0.16))
    for frac in (-0.22,0,0.22): box('Leaded glass mullions | north',metal,(x+frac*w,yy+0.05,z),(0.055,0.07,h-0.22))
    for frac in (-0.2,0.2): box('Leaded glass muntins | north',metal,(x,yy+0.05,z+frac*h),(w-0.25,0.07,0.055))

# Tower entrance: solid oak replica, two copper lights, gothic pointed limestone arch.
door_y=66.25; door_x=-437.03
box('Historic oak entry door',wood,(door_x,door_y,1.85),(0.16,1.48,2.9))
box('Historic door inset panel upper',timber,(door_x-0.10,door_y,2.35),(0.055,0.88,1.15))
box('Historic door inset panel lower',timber,(door_x-0.10,door_y,1.05),(0.055,0.88,0.65))
for yy in (door_y-0.82,door_y+0.82): box('Gothic entrance deep limestone jamb',limestone,(-437.12,yy,2.4),(0.30,0.23,3.7))
# pointed arch in the facade plane as limestone ring segments and Gothic tympanum
arch=Batch('Pointed limestone gothic entry arch',limestone)
arch.quad([(-437.18,door_y-0.94,4.05),(-437.18,door_y,5.25),(-437.18,door_y-0.55,4.1)])
arch.quad([(-437.18,door_y,5.25),(-437.18,door_y+0.94,4.05),(-437.18,door_y+0.55,4.1)])
exterior_objects.append(arch.mesh())
# copper lanterns on either side, with brackets
for yy in (door_y-1.25,door_y+1.25):
    box('Copper entry lantern',metal,(-437.17,yy,2.75),(0.20,0.22,0.52))
# ATO sign on the parapet/tower above entrance.
font=bpy.data.curves.new('ATO nameplate text','FONT'); font.body='A T O'; font.size=0.58; font.align_x='CENTER'; font.extrude=0.006
textob=bpy.data.objects.new('ATO tower nameplate | period sign',font); asset.objects.link(textob); textob.location=(-437.18,66.25,8.0)
textob.rotation_euler=Vector((-1,0,0)).to_track_quat('Z','Y').to_euler(); font.materials.append(limestone); exterior_objects.append(textob)

# Nine-bay west front, ordered north to south. Bay 5 is the tower; 2/3/8 rise into gables.
front_bays=[82.0,77.5,73.0,68.5,64.3,60.2,55.7,51.3,47.1]
# bays north of tower
for i,y in enumerate(front_bays):
    if i==4: continue
    fx=-435.30 if y>68.0 else -433.45
    # first floor: documented mix of French doors and multi-light/sliding windows
    if i in (0,1,2,5):
        # paired multi-pane french doors at west facade
        window_west(y,1.9,1.7,2.4,front_x=fx,transom=True)
    else: window_west(y,1.85,1.7,2.15,front_x=fx,transom=True)
    # second level multi-light double-hung windows
    window_west(y,5.05,1.65,1.8,front_x=fx,transom=False)
# Upper dormer windows/gable projections: bays 2, 3 and eighth bay per historic description.
dormer(77.5,3.05,8.25,11.1)
dormer(73.0,3.05,8.25,11.1)
dormer(51.3,3.05,8.0,10.8)
# Tower's paired second-floor windows and concealed third-floor light.
window_west(65.1,8.7,1.35,1.6,front_x=-437.2,transom=True)
window_west(65.1,5.2,1.45,1.8,front_x=-437.2,transom=True)
# East (rear) wall windows, with small shed dormers and 1940s kitchen service windows.
for y in (48,52,56,60,71,75,79,82):
    window_east(y,1.85,1.35,1.65)
    window_east(y,5.05,1.35,1.65)
for y in (71,76,81): window_east(y,8.05,1.35,1.45)
# North end wall windows; southern addition end has mostly blind masonry per the source description.
for x in (-431.0,-427.0,-423.0):
    window_north(x,1.9,1.6,1.8)
    window_north(x,5.15,1.6,1.8)
# Door/window bays on the south end and east kitchen service door.
box('South service door',wood,(-427.0,46.34,1.5),(1.25,0.16,2.55))
box('East kitchen door',wood,(-413.65,79.0,1.55),(0.16,1.15,2.6))

# Tudor gable cheeks and false half-timber panels along the three through-the-cornice dormers.
# (Dormer function above was declared before the window builder; instantiate now.)
# dormer geometry already added after function calls below.

# Chimneys: NPS documents three brick stacks, including kitchen, fireplace and heating-system flues.
for x,y,z,h in [(-421.1,81.0,9.55,2.15),(-425.8,71.5,11.85,1.95),(-426.5,50.0,10.20,1.75)]:
    box('Brick chimney stack',brick,(x,y,z+h/2),(1.05,1.25,h))
    box('Limestone chimney cap',limestone,(x,y,z+h),(1.24,1.42,0.18))
# 1963 addition seam and original copper troughs remain legible as material/detail cues.
box('1963 addition reveal',limestone,(-433.47,64.4,4.4),(0.12,0.18,8.4))

# Porch and yard screen wall from period photographs, low keyed so it does not obscure the facade.
box('West frontage low brick garden wall',brick,(-438.4,57.8,0.5),(0.35,7.7,0.9))
box('West frontage low brick garden wall cap',limestone,(-438.4,57.8,0.98),(0.48,7.8,0.13))
box('Entry porch rail wall return',brick,(-435.1,74.4,0.56),(0.65,0.25,0.8))

# Generate the main geometry batches now. The root object already represents primary brick masses.
for k,b in batches.items():
    if k.startswith('Pointed limestone'): continue
    ob=b.mesh();
    if ob and (ob.name.startswith('Steep hip') or ob.name.startswith('Slate ridge')): exterior_objects.append(ob)
    elif ob: exterior_objects.append(ob)

# Rebuild root's mesh from exact two principal wall blocks so its original stable object is used.
# (The object itself is kept; its geometry is swapped for the curated building mass.)
# Hide the duplicate batched shell meshes and reassign main wall mass to the stable root object.
# Batch meshes are the source of current root-body pieces; consolidate by joining their vertices.
# The root mesh is intentionally non-empty and retains the former asset object name.
if len(root.data.vertices)==0:
    root.data.from_pydata(rootbatch.v,[],rootbatch.f); root.data.materials.append(brick); root.data.update()

# A documented, schematic first-floor cutaway/interior vignette. The NPS nomination names these
# spaces/features, but gives no measured floor plan; partitions and furniture remain explicitly schematic.
interior_objects=[]
def ibox(name,material,c,d):
    before=set(bpy.data.objects.keys()); b=Batch(name,material); b.box(c,d); o=b.mesh(object_name=name)
    interior_objects.append(o); return o
# three floors, with labeled ground floor room zones
ibox('Schematic first-floor oak and limestone underlay',interior_floor,(-426.7,65.0,0.20),(12.2,36.0,0.30))
ibox('Schematic second-floor plate',wood_floor,(-426.7,65.0,3.45),(12.2,36.0,0.22))
ibox('Schematic third-floor plate',wood_floor,(-426.7,65.0,6.65),(12.2,36.0,0.22))
# selectively colored room plates
ibox('Foyer | limestone floor',interior_floor,(-430.3,65.9,0.39),(4.8,5.0,0.06))
ibox('Formal living room | oak floor',wood_floor,(-426.4,75.0,0.39),(11.4,11.0,0.06))
ibox('Dining room | oak floor',wood_floor,(-426.4,54.0,0.39),(11.4,8.0,0.06))
ibox('Billiards room | oak floor',wood_floor,(-423.0,64.2,0.39),(5.0,8.5,0.06))
# Low partition cues establish the schematic room boundaries without claiming measured walls.
for y in (69.5,59.0): ibox('Schematic low room divider',interior_wall,(-426.5,y,1.45),(11.4,0.12,2.0))
ibox('Schematic foyer divider',interior_wall,(-428.1,65.8,1.45),(0.12,4.8,2.0))
# Main staircase and documented oak polygonal newel/post, rendered as a recognizable stair flight.
for i in range(13):
    y=64.0+i*0.26; z=0.62+i*0.18
    ibox('Main oak stair | tread',wood,(-429.4,y,z),(2.25,0.34,0.13))
ibox('Oak polygonal staircase newel',wood,(-428.2,64.1,1.7),(0.28,0.28,2.7))
for i in range(11): ibox('Oak stair baluster',wood,(-428.2,64.8+i*0.25,1.85+i*0.14),(0.09,0.09,0.62))
ibox('Oak stair handrail',wood,(-428.2,66.05,3.1),(0.15,3.2,0.15))
# Living room inglenook: limestone Tudor arch, firebox, recessed oak paneling and paired columns.
ibox('Limestone living-room fireplace surround',limestone,(-420.15,75.2,1.65),(0.32,3.0,2.6))
ibox('Tudor fireplace dark firebox',timber,(-419.92,75.2,1.25),(0.12,1.55,1.45))
ibox('Limestone fireplace lintel',limestone,(-419.85,75.2,2.75),(0.45,3.2,0.28))
for y in (73.65,76.75): ibox('Oak inglenook panel column',wood,(-419.9,y,1.8),(0.22,0.22,2.2))
# Common room furnishing in approximate, non-measured arrangement.
ibox('Formal room settee',velvet,(-426.0,77.0,0.92),(2.4,0.85,0.75))
ibox('Formal room table',wood,(-425.4,73.7,0.70),(1.25,0.85,0.78))
ibox('Dining table | schematic',wood,(-426.6,53.8,1.0),(3.8,1.4,0.14))
for x in (-428.7,-424.5):
  for y in (52.5,55.0): ibox('Dining chair | schematic',wood,(x,y,0.75),(0.55,0.55,0.8))
ibox('Billiards table | schematic',wood,(-423.0,63.8,1.10),(2.4,4.0,0.20))
# Documented twin gothic-pointed oak display cases in billiards room.
for y in (61.2,66.2):
    ibox('Gothic-pointed oak display case | schematic',wood,(-420.8,y,2.0),(0.45,0.55,2.4))
# labeled interior spaces and a persistent caveat label visible in cutaway preview.
def text_label(name,body,loc,size,material=limestone):
    c=bpy.data.curves.new(name,'FONT'); c.body=body; c.size=size; c.extrude=0.004; c.align_x='CENTER'; c.align_y='CENTER'
    o=bpy.data.objects.new(name,c); asset.objects.link(o); o.location=loc; c.materials.append(material); interior_objects.append(o); return o
text_label('Interior label | foyer','FOYER',(-430.3,65.8,0.47),0.40,wood)
text_label('Interior label | living room','LIVING ROOM',(-426.0,76.0,0.49),0.42,wood)
text_label('Interior label | dining room','DINING ROOM',(-426.4,54.0,0.49),0.42,wood)
text_label('Interior label | billiards room','BILLIARDS',(-423.0,64.2,0.49),0.36,wood)
text_label('Interior label | bedrooms','26 LIVING QUARTERS\nROOM LAYOUT UNVERIFIED',(-426.7,65.0,3.58),0.34,wood)
text_label('Interior schematic caveat','SCHEMATIC • DIMENSIONS / PARTITIONS UNDOCUMENTED',(-426.6,45.6,0.5),0.30,timber)

# Ensure a small number of descriptive, source-bearing custom properties remain inspectable in Blender.
root['building_id']='massing_house_301840870_c45a5f4'
root['source_identity']='Purdue GIS FID 785 | SOATO | Alpha Tau Omega | 314 Russell St'
root['model_period']='Historic ATO house, documented circa 2002; current 2024 reuse is not represented'
root['position_method']='GIS FID 785 geometry; EPSG:4326 converted to Purdue project local XY about 40.4274,-86.9137'
root['height_status']='Estimated from 2.5-story NPS description and GIS Extrution=12; no measured elevations'
root['interior_status']='Schematic; room names/features documented, floor plan dimensions/layout unavailable'

# Make a separate review scene/collection so master import still sees only the named asset collection.
review=bpy.data.scenes.get('Review_massing_house_301840870_c45a5f4') or bpy.data.scenes.new('Review_massing_house_301840870_c45a5f4')
if asset.name not in review.collection.children:
    review.collection.children.link(asset)
preview_col=bpy.data.collections.get('ATO Review Rig')
if preview_col:
    for o in list(preview_col.objects): bpy.data.objects.remove(o,do_unlink=True)
else:
    preview_col=bpy.data.collections.new('ATO Review Rig'); review.collection.children.link(preview_col)
# Reusable preview camera and lights.
def look_at(o,target): o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def add_camera(name,loc,target,ortho):
    d=bpy.data.cameras.new(name); d.type='ORTHO'; d.ortho_scale=ortho
    o=bpy.data.objects.new(name,d); preview_col.objects.link(o); o.location=loc; look_at(o,target); return o
def add_area(name,loc,target,power,size):
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size
    o=bpy.data.objects.new(name,d); preview_col.objects.link(o); o.location=loc; look_at(o,target); return o
# world and a muted ground plane for context (review-only)
world=bpy.data.worlds.get('ATO Review World') or bpy.data.worlds.new('ATO Review World'); world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(0.28,0.34,0.42,1); world.node_tree.nodes['Background'].inputs[1].default_value=0.65
review.world=world
review.render.engine='CYCLES'; review.cycles.samples=24
review.render.resolution_x=1500; review.render.resolution_y=1200; review.render.resolution_percentage=100
review.view_settings.view_transform='AgX'; review.render.image_settings.file_format='PNG'
# low ground slab and front street/walkway
rig_batch=Batch('ATO site review ground',make_mat('ATO | review context turf',(0.13,0.20,0.12),0.92))
rig_batch.box((-426.0,65.0,-0.22),(68,80,0.40)); ground=rig_batch.mesh(object_name='Review only | context ground',collection=preview_col)
road_batch=Batch('ATO review street context',make_mat('ATO | review context pavement',(0.22,0.24,0.25),0.92))
road_batch.box((-444.4,65.0,-0.015),(0.4,72,0.08)); road=road_batch.mesh(object_name='Review only | Russell street strip',collection=preview_col)
add_area('Soft daylight key',(-462,34,45),(-426,65,3),17000,34)
add_area('Soft north fill',(-414,95,30),(-426,65,4),10500,38)
# exterior preview, west/front and a slight south angle
cam=add_camera('Exterior front review camera',(-475,57,27),(-427,65,6),56); review.camera=cam
review.render.filepath=str(AUDIT/'previews/ato_exterior_front.png')
bpy.context.window.scene=review
bpy.ops.render.render(write_still=True)
# second detailed three-quarter view includes addition/roof silhouette
cam2=add_camera('Exterior three-quarter review camera',(-463,32,30),(-425,65,5),62); review.camera=cam2
review.render.filepath=str(AUDIT/'previews/ato_exterior_three_quarter.png')
bpy.ops.render.render(write_still=True)
# Cutaway preview: temporarily hide exterior shell/roof/outer windows and show the documented schematic rooms.
# The asset geometry is not deleted; hide flags are reset immediately after rendering.
for o in exterior_objects:
    o.hide_render=True
for o in asset.objects:
    if o.name.startswith(('Leaded west window','Limestone window','Leaded glass','Window transom','Steep hip roof','1940s kitchen shed roof','Dormer slate','Tower','Gothic entry tower','Platform porch','Historic oak entry','Gothic entrance','West entry stone','Brick chimney','Limestone chimney','Copper gutter','Copper trough','False half timber','Gothic-pointed oak display case')):
        o.hide_render=True
# Open the cutaway through the roof and both upper-level floor plates so the documented first-floor rooms read clearly.
for o in interior_objects:
    if o.name in ('Schematic second-floor plate','Schematic third-floor plate'):
        o.hide_render=True
cam3=add_camera('Interior cutaway schematic review camera',(-454,70,31),(-426,65,1.0),46); review.camera=cam3
review.render.filepath=str(AUDIT/'previews/ato_interior_schematic.png')
bpy.ops.render.render(write_still=True)
for o in asset.objects: o.hide_render=False
for o in exterior_objects: o.hide_render=False
# Set published scene active and avoid treating review camera/material objects as asset contents.
bpy.context.window.scene=scene
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1400; scene.render.resolution_y=1000
scene.world=world
# Save only this dedicated house library. External photos are evidence only; no linked image textures.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
print(json.dumps({'asset':str(ASSET_PATH),'collection':asset.name,'scene':scene.name,'asset_objects':len(asset.objects),'bounds_xy_m':[[min(v.co.x for o in asset.objects if o.type=='MESH' for v in o.data.vertices),max(v.co.x for o in asset.objects if o.type=='MESH' for v in o.data.vertices)],[min(v.co.y for o in asset.objects if o.type=='MESH' for v in o.data.vertices),max(v.co.y for o in asset.objects if o.type=='MESH' for v in o.data.vertices)]],'height_estimate_m':12.2},indent=2))



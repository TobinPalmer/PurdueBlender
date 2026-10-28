"""Hash-guarded Haas exterior r02: address independent r01 facade findings.

Keeps campus placement/footprint and roof geometry. Cuts the three existing front
upper openings through inherited wall layers instead of painting over the occluder.
"""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'audit/felix_haas_hall/second_pass'
ASSET=ROOT/'modular/buildings/felix_haas_hall.blend'
INPUT='445c1499ef1b1c0bb2c5520304cff9784a572e0478abcc17a72157f951ba88f4'
assert hashlib.sha256(ASSET.read_bytes()).hexdigest()==INPUT
assert Path(bpy.data.filepath).resolve()==ASSET.resolve()
C=bpy.data.collections['Asset_felix_haas_hall'];removed=[];added=[];modified=[]
stone=bpy.data.materials['HAAS_SP_Bedford_Limestone_estimate']
brick=bpy.data.materials['HAAS_SP_West_RedBrick_estimate']
frame=bpy.data.materials['HAAS_SP_DarkBronzeFrame_estimate']
glass=bpy.data.materials['HAAS_SP_NeutralGlass_estimate']

def plane_x(y):return -25.84852+(-26.22032+25.84852)*(y+25.97952)/(26.75972+25.97952)
def box(name,lo,hi,mat):
    vertices=[(x,y,z) for x,y,z in [(lo[0],lo[1],lo[2]),(hi[0],lo[1],lo[2]),(hi[0],hi[1],lo[2]),(lo[0],hi[1],lo[2]),(lo[0],lo[1],hi[2]),(hi[0],lo[1],hi[2]),(hi[0],hi[1],hi[2]),(lo[0],hi[1],hi[2])]]
    mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(vertices,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);mesh.update()
    if mat:mesh.materials.append(mat)
    o=bpy.data.objects.new(name,mesh);C.objects.link(o);added.append(name);return o
def west(name,y,z,w,h,mat,offset=.115,depth=.16):
    x=plane_x(y)-offset
    return box(name,(x-depth/2,y-w/2,z-h/2),(x+depth/2,y+w/2,z+h/2),mat)
def remove(o):
    removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)

# Slim dark middle openings with a pale sill and key; remove heavy white surrounds.
for o in list(C.all_objects):
    if o and o.name.startswith('HAAS_SP_West_Middle_') and ('_Jamb' in o.name or o.name.endswith('_Head')):remove(o)

centers=[-22.8+5.7*i for i in range(9)]
intervals=[]
for i,y in enumerate(centers):
    width=2.55 if i==6 else 2.8
    intervals.append((y-width/2-.18,y+width/2+.18))
left=-25.85
for i,(a,b) in enumerate(intervals):
    if a>left:
        west(f'HAAS_SP_R02_BasementPier_{i}',(left+a)/2,1.70,a-left,3.4,stone)
        # Brick inset within the pale basement register, as seen in 2016/2026.
        if a-left>.85:west(f'HAAS_SP_R02_BasementBrickInset_{i}',(left+a)/2,1.75,a-left-.30,1.55,brick,offset=.215,depth=.05)
    left=b
if left<26.65:west('HAAS_SP_R02_BasementEnd',(left+26.65)/2,1.7,26.65-left,3.4,stone)
for i,y in enumerate(centers):
    if i==6:
        west('HAAS_SP_R02_DoorHeader',y,3.30,2.91,.20,stone)
        # Delineate a large transom and two lower leaves; dark frames remain visible.
        west('HAAS_SP_R02_DoorTransom',y,2.48,2.55,.105,frame,offset=.24,depth=.10)
        west('HAAS_SP_R02_DoorTransomMullion',y,2.79,.075,.57,frame,offset=.24,depth=.10)
    else:
        west(f'HAAS_SP_R02_BasementBelow_{i}',y,.45,3.16,.90,stone)
        west(f'HAAS_SP_R02_BasementAbove_{i}',y,2.93,3.16,.93,stone)

# Recessed west-door approach; exact dimensions remain photographic estimates.
door_y=centers[6];xwall=plane_x(door_y)
box('HAAS_SP_R02_WestDoorLanding',(xwall-1.8,door_y-1.50,.15),(xwall-.15,door_y+1.50,.29),stone)
verts=[(xwall-6.2,door_y-1.50,1.12),(xwall-6.2,door_y+1.50,1.12),(xwall-1.8,door_y+1.50,.29),(xwall-1.8,door_y-1.50,.29)]
mesh=bpy.data.meshes.new('HAAS_SP_R02_ApproachRamp_Mesh');mesh.from_pydata(verts,[],[(0,1,2,3)]);mesh.materials.append(stone);mesh.update()
o=bpy.data.objects.new('HAAS_SP_R02_ApproachRamp',mesh);C.objects.link(o);added.append(o.name)
for side in (-1,1):box(f'HAAS_SP_R02_WestDoorCheek_{side}',(xwall-6.2,door_y+side*1.68-.12,.12),(xwall-.2,door_y+side*1.68+.12,1.30),stone)

def cut(target,cutter):
    bpy.context.view_layer.objects.active=target;target.select_set(True)
    mod=target.modifiers.new('SecondPass_Opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);modified.append(target.name)
for y in (-7.65,0,7.65):
    # Slight clearance inside existing limestone jambs; no base footprint vertices touched.
    cutter=box(f'HAAS_SP_R02_TEMP_Cut_{y}',(12.40,y-1.56,6.95),(13.60,y+1.56,8.45),None)
    for name in ('HAAS_Corrected_GIS_Wall_Envelope','HAAS_Brick_Wall_East'):cut(bpy.data.objects[name],cutter)
    added.remove(cutter.name);bpy.data.objects.remove(cutter,do_unlink=True)
    old=bpy.data.objects.get(f'HAAS_Win_Floor2_East_{-8.0 if y<0 else 8.0 if y>0 else 0.0}')
    if old:remove(old)
    glazing=bpy.data.objects[f'HAAS_Photo_Glazing_{y if y else 0}_7.7']
    glazing.data.materials.clear();glazing.data.materials.append(glass);modified.append(glazing.name)
    for k,yy in enumerate((y-1.54,y-1.54+3.08/3,y-1.54+6.16/3,y+1.54)):
        box(f'HAAS_SP_R02_FrontUpper_{y}_Vertical{k}',(12.835,yy-.035,6.96),(12.935,yy+.035,8.44),frame)
    for k,zz in enumerate((6.96,7.70,8.44)):
        box(f'HAAS_SP_R02_FrontUpper_{y}_Horizontal{k}',(12.835,y-1.54,zz-.035),(12.935,y+1.54,zz+.035),frame)

bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();rays=[]
for y in (-7.65,0,7.65):
    # Sample away from mullions to verify a wall no longer conceals the glazing.
    hit,loc,n,face,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((30,y+.22,8.15)),Vector((-1,0,0)),distance=25)
    rays.append({'y':y,'first_hit':obj.name if hit else None,'x':float(loc.x) if hit else None})
    assert hit and 'Glazing' in obj.name,('Front glazing remains occluded',rays[-1])
C['second_pass_revision']='exterior_r02';C['second_pass_status']='Round 2 candidate; independent review required. Front upper openings cut through inherited walls; west basement/trim/entry revised. Other facade discrepancies remain.'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(ASSET),compress=True)
folder=OUT/'revision_r02';folder.mkdir(exist_ok=True)
record={'building_id':'felix_haas_hall','revision':'exterior_r02','input_sha256':INPUT,'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'independent_findings_addressed':['r01 front upper glazing occlusion','r01 west broad pale basement register/brick insets','r01 narrow middle trim','r01 west door transom and recessed approach'],'added':added,'removed':removed,'modified':sorted(set(modified)),'front_upper_visibility_ray_tests':rays,'remaining':['front lower arches need segmental profile correction','north/south openings require stronger correctly oriented references','opening dimensions and new approach remain estimates','west glazing still sits ahead of retained wall layers'],'preserved':['GIS ground footprint and campus origin','roofs','stable asset/collection ID','schematic interior'],'score':None,'accepted':False}
(folder/'change_record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'revision':'exterior_r02','sha256':record['asset_sha256'],'added':len(added),'removed':len(removed),'visibility':rays}))

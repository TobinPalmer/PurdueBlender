"""Apply the documented exterior second-pass delta to the saved Haas library.

Run with Blender --background --disable-autoexec <asset> --python <this file>.
Round 1 deliberately changes only the evidenced west facade. This is a revision
candidate, not visual acceptance. Exact dimensions remain photo-derived estimates.
"""
import bpy,json,hashlib,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/felix_haas_hall.blend'
OUT=ROOT/'audit/felix_haas_hall/second_pass'
BASE='0de3417c6cc3af247b2100242720d39871bc8ed188dcf06bfbb96d9bead2c067'
assert Path(bpy.data.filepath).resolve()==ASSET.resolve()
assert hashlib.sha256(ASSET.read_bytes()).hexdigest()==BASE,'Expected exact reviewed starting asset; do not apply to another revision.'
C=bpy.data.collections['Asset_felix_haas_hall']
before={o.name for o in C.all_objects if o}
removed=[]
# Replace only the prior unsupported west facade attachments. Preserve its wall,
# the GIS envelope, roof, other elevations, interior, and placement frame.
for o in list(C.all_objects):
    if not o:continue
    if o.name.startswith('HAAS_R4_West_') or (any(t in o.name for t in ('HAAS_Win_Floor','HAAS_Sill_Floor','HAAS_Arch_Floor')) and '_West_' in o.name):
        removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)

def material(name,color,roughness=.65,metallic=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    node=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    node.inputs['Base Color'].default_value=(*color,1);node.inputs['Roughness'].default_value=roughness
    node.inputs['Metallic'].default_value=metallic;m.diffuse_color=(*color,1);return m
stone=material('HAAS_SP_Bedford_Limestone_estimate',(.48,.45,.37),.82)
brick=material('HAAS_SP_West_RedBrick_estimate',(.22,.069,.037),.88)
frame=material('HAAS_SP_DarkBronzeFrame_estimate',(.036,.033,.026),.43,.25)
glass=material('HAAS_SP_NeutralGlass_estimate',(.025,.042,.055),.23,.15)
joint=material('HAAS_SP_WindowReveal',(.011,.012,.011),.9)

new=[]
# Recorded GIS west edge is slightly skewed. Follow it instead of moving the shell.
def plane_x(y):return -25.84852+(-26.22032+25.84852)*(y+25.97952)/(26.75972+25.97952)
def box(name,y,z,w,h,depth,offset,mat):
    verts=[]
    for d in (-depth/2,depth/2):
        for yy,zz in ((y-w/2,z-h/2),(y+w/2,z-h/2),(y+w/2,z+h/2),(y-w/2,z+h/2)):
            verts.append((plane_x(yy)-offset-d,yy,zz))
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.materials.append(mat);me.update()
    obj=bpy.data.objects.new(name,me);C.objects.link(obj)
    obj['second_pass_source']='Google Street View F4m7ya0MXAz0LkjEAIJB5g, April 2026; Jay Discovery May 2016 elevated west photo'
    obj['dimensions_status']='photo-derived estimate, not surveyed'
    new.append(name);return obj

def window(label,y,z,w,h,panes,stone_width=.18,decorative=False):
    # 3-D reveal/frame geometry; neutral opaque glazing avoids inventing an interior.
    box(label+'_Reveal',y,z,w+.12,h+.12,.045,.045,joint)
    box(label+'_Glass',y,z,w-.12,h-.12,.025,.071,glass)
    for side in (-1,1):
        box(label+f'_Jamb{side}',y+side*(w/2+.09),z,.18,h+.30,.21,.16,stone)
        box(label+f'_FrameV{side}',y+side*(w/2-.04),z,.08,h,.11,.126,frame)
    for side in (-1,1):
        box(label+f'_FrameH{side}',y,z+side*(h/2-.04),w,.08,.11,.126,frame)
    box(label+'_Head',y,z+h/2+.115,w+.36,.23,.21,.16,stone)
    box(label+'_Sill',y,z-h/2-.12,w+.48,.24,.31,.20,stone)
    for p in range(1,panes):box(label+f'_Mullion{p}',y-w/2+w*p/panes,z,.09,h,.115,.13,frame)
    box(label+'_Transom',y,z+h*.16,w,.07,.11,.13,frame)
    if decorative:
        # Stepped corner blocks and small keystone visible in both independent views.
        for side in (-1,1):
            for level,extra in ((z+h/2-.2,.12),(z-h/2+.18,.11)):
                box(label+f'_Quoin{side}_{level:.2f}',y+side*(w/2+.15),level,.42,.28,.24,.18,stone)
        box(label+'_Key',y,z+h/2+.25,.34,.48,.24,.19,stone)

centers=[-22.8+5.7*i for i in range(9)]
# Articulated brick pilasters, not the former six tall pale posts.
for i,y in enumerate([-25.65]+[(a+b)/2 for a,b in zip(centers,centers[1:])]+[25.65]):
    box(f'HAAS_SP_West_BrickPilaster_{i}',y,7.3,.52,8.4,.24,.12,brick)
    box(f'HAAS_SP_West_PilasterFoot_{i}',y,2.45,.70,.40,.26,.14,stone)
box('HAAS_SP_West_BasementBelt',.39,3.38,52.55,.43,.22,.12,stone)
box('HAAS_SP_West_UpperString',.39,10.98,52.55,.17,.15,.09,stone)

for i,y in enumerate(centers):
    pane_count=3 if i>=6 else 2
    width=3.45 if pane_count==3 else 2.85
    window(f'HAAS_SP_West_Upper_{i}',y,9.8,width,1.75,pane_count,decorative=True)
    window(f'HAAS_SP_West_Middle_{i}',y,6.35,.82,2.0,1)
    box(f'HAAS_SP_West_MiddleKey_{i}',y,7.66,.28,.45,.18,.13,stone)
    if i==6:
        # Visible west double-door bay: estimated location within observed bay rhythm.
        window(f'HAAS_SP_West_Door_{i}',y,1.70,2.55,2.85,2)
        for side in (-1,1):box(f'HAAS_SP_West_DoorPush_{side}',y+side*.40,1.40,.035,.62,.05,.24,frame)
    else:window(f'HAAS_SP_West_Basement_{i}',y,1.65,2.8,1.25,2)

C['second_pass_status']='Round 1 candidate; west window and stone rhythm revised from 2016 photo and April 2026 Street View. Independent review required; north and exact dimensions remain unverified.'
C['second_pass_revision']='exterior_r01'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET),compress=True)
record={'building_id':'felix_haas_hall','revision':'exterior_r01','input_sha256':BASE,'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'removed_unsupported_west_attachments':removed,'added_objects':new,'west_upper_bays':9,'middle_narrow_windows':9,'basement_windows':8,'west_double_door_bays':1,'source_evidence':['sources/maps_side_jay_discovery_2016.png','sources/streetview_university_entry_apr2026.png','sources/streetview_west_upper_apr2026.png'],'estimates':['bay count near occluded corners requires independent confirmation','window widths, heights and elevations are photo-derived estimates','door bay approximate, not surveyed','materials estimated from uncalibrated daylight photographs'],'preserved':['GIS envelope mesh and coordinates','main and entry roofs','east/north/south facades','schematic interior','manifest ID, path, collection and placement origin'],'object_count_before':len(before),'object_count_after':len(C.all_objects),'accepted':False,'score':None}
(OUT/'revision_r01').mkdir(exist_ok=True)
(OUT/'revision_r01/change_record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'revision':record['revision'],'sha256':record['asset_sha256'],'added':len(new),'removed':len(removed),'accepted':False}))

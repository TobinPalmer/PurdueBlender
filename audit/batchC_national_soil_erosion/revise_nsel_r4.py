import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'audit' / 'batchC_national_soil_erosion'
ASSET = ROOT / 'modular' / 'buildings' / 'national_soil_erosion_laboratory.blend'
INTERIOR = bpy.data.collections['SOIL_Interior']

# Rerunnable R4 additions. These are clearly grouped as an interpretive
# high-bay interior because public sources do not provide NSEL interior plans.
for obj in list(INTERIOR.objects):
    if obj.name.startswith('SOIL | R4 '):
        bpy.data.objects.remove(obj, do_unlink=True)

def material(name, color, roughness=.55, metallic=0.0, emission=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if emission:
        socket = bsdf.inputs.get('Emission Color') or bsdf.inputs.get('Emission')
        if socket:
            socket.default_value = (*emission[0], 1.0)
        strength = bsdf.inputs.get('Emission Strength')
        if strength:
            strength.default_value = emission[1]
    return mat

def box(name, center, dims, mat, bevel=0.0):
    dx, dy, dz = dims
    verts = [(x, y, z) for x in (-dx/2, dx/2) for y in (-dy/2, dy/2) for z in (-dz/2, dz/2)]
    faces = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    mesh = bpy.data.meshes.new(name + ' | mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    INTERIOR.objects.link(obj)
    obj.location = center
    if bevel:
        mod = obj.modifiers.new('small fabricated edge radius', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return obj

def beam(name, a, b, width, depth, mat):
    start, end = Vector(a), Vector(b)
    delta = end - start
    obj = box(name, (start + end) / 2, (width, depth, delta.length), mat)
    obj.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    return obj

concrete = bpy.data.materials['SOIL | cast concrete']
steel = bpy.data.materials['SOIL | R2 brushed hydraulic steel']
wall_mat = material('SOIL | R4 pale gray high-bay liner', (.48,.51,.51), .78)
roof_mat = material('SOIL | R4 light industrial ceiling', (.60,.62,.60), .82)
bench_mat = material('SOIL | R4 stainless work surface', (.48,.54,.55), .28, .68)
cabinet_mat = material('SOIL | R4 lab cabinet enamel', (.27,.35,.36), .38, .18)
bin_mat = material('SOIL | R4 soil sample trays', (.39,.24,.13), .72)
mark_mat = material('SOIL | R4 safety aisle paint', (.80,.57,.12), .7)
fixture_mat = material('SOIL | R4 high-bay lamp diffuser', (.86,.82,.68), .34, emission=((1.0,.83,.58), 1.1))

cx, half_x, half_y, wall_h = -25.4, 4.5, 17.75, 6.36
zmid = wall_h / 2

# Enclose the previously open portal-frame concept with high-bay liner walls
# and a ceiling plane. The south wall is represented as part of the enclosure
# but may be hidden in the cutaway render so the flume and access route read.
box('SOIL | R4 high-bay west liner wall',(cx-half_x,0,zmid),(.18,2*half_y,wall_h),wall_mat)
box('SOIL | R4 high-bay east liner wall',(cx+half_x,0,zmid),(.18,2*half_y,wall_h),wall_mat)
box('SOIL | R4 high-bay north end wall',(cx,half_y,zmid),(2*half_x,.18,wall_h),wall_mat)
box('SOIL | R4 high-bay south end wall',(cx,-half_y,zmid),(2*half_x,.18,wall_h),wall_mat)
box('SOIL | R4 high-bay ceiling',(cx,0,wall_h+.10),(2*half_x,2*half_y,.20),roof_mat)

# Subtle liner panel seams and perimeter base guard lend scale without adding
# unsupported windows or openings. Portal/roof sizes retain the R3 estimates.
for i,y in enumerate((-14,-10,-6,-2,2,6,10,14)):
    beam(f'SOIL | R4 west wall liner joint {i}',(cx-half_x+.1,y,.25),(cx-half_x+.1,y,wall_h-.12),.035,.035,steel)
    beam(f'SOIL | R4 east wall liner joint {i}',(cx+half_x-.1,y,.25),(cx+half_x-.1,y,wall_h-.12),.035,.035,steel)
for side in (-1,1):
    x = cx + side*(half_x-.16)
    box(f'SOIL | R4 wall base guard {side}',(x,0,.12),(.12,2*half_y,.24),steel)

# High-bay service work zone opposing the existing walkway. It is separated
# from the flume by a clearly readable, roughly 1.9 m working aisle.
bx = cx - 3.2
box('SOIL | R4 stainless soil-preparation bench',(bx,-1.5,.92),(.92,12.0,.12),bench_mat,.025)
for y in (-6.9,-3.3,.3,3.9):
    for dx in (-.34,.34):
        box(f'SOIL | R4 bench leg {y:.1f} {dx:.2f}',(bx+dx,y,.46),(.07,.07,.92),steel)
box('SOIL | R4 bench lower shelf',(bx,-1.5,.31),(.78,11.5,.08),steel)
for j,y in enumerate((-6.1,-3.7,-1.3,1.1,3.5)):
    box(f'SOIL | R4 soil sample tray {j+1}',(bx,-1.5+y,.99),(.58,.76,.12),bin_mat,.035)
    # Small shallow sample cells read as task equipment, not furniture clutter.
    for k in range(3):
        box(f'SOIL | R4 tray cell {j+1}-{k+1}',(bx-.19+k*.19,-1.5+y,1.06),(.16,.62,.035),concrete)

# A compact wet-work / instrument station is kept clear of the main flume
# operating aisle and the R3 service walkway.
box('SOIL | R4 instrument worktable',(cx-3.1,11.2,.88),(1.35,3.6,.12),bench_mat,.025)
for x in (cx-3.65,cx-2.55):
    for y in (9.8,12.6):
        box(f'SOIL | R4 instrument table leg {x:.2f}-{y:.1f}',(x,y,.43),(.07,.07,.86),steel)
for i in range(3):
    box(f'SOIL | R4 instrument case {i+1}',(cx-3.1,10.25+i*.85,1.16),(.72,.56,.42),cabinet_mat,.04)
box('SOIL | R4 sample cart platform',(cx-3.3,-12.3,.52),(1.0,1.5,.10),steel,.03)
for i in range(4):
    box(f'SOIL | R4 sample cart bin {i+1}',(cx-3.3,-12.65+i*.25,.82),(.72,.20,.48),bin_mat,.02)

# Paint discreet aisle edges between the work zone and the flume operation.
# They signal circulation only; actual NSEL safety markings are not verified.
for x in (cx-2.60,cx-.85):
    box(f'SOIL | R4 circulation boundary {x:.2f}',(x,-.1,.012),(.055,27.4,.024),mark_mat)

# Diffused strip fixtures beneath the ceiling support a believable interior
# read. Their count/location are illustrative rather than source-verified.
for i,y in enumerate((-11,0,11)):
    box(f'SOIL | R4 overhead light diffuser {i+1}',(cx,y,wall_h-.22),(.42,4.8,.07),fixture_mat,.03)

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

report = {
    'revision':'R4', 'previous_independent_score':'7.8/10',
    'source_context':[
        {'provider':'USDA Agricultural Research Service','url':'https://www.ars.usda.gov/oc/images/photos/apr97/k7567-11/','asset':'K7567-11 hydraulics laboratory photo','supports':'Comparable USDA research flume in a large enclosed industrial bay, hard floor, working platforms, people/equipment and adjacent work activity; not NSEL room dimensions or exact layout.'},
        {'provider':'Purdue/visitor photograph','url':'https://ppgta.ufms.br/files/2018/02/Grupo-Purdue.jpg','asset':'2018 Purdue NSEL exterior photograph','supports':'Exterior lettering/façade; does not show interior.'},
    ],
    'changes':[
        'Added four perimeter liner walls and a ceiling to enclose the R3 high-bay floor/frame concept. Their extent and height remain schematic estimates, not surveyed NSEL interior dimensions.',
        'Added soil-preparation bench, sample trays, instrument station/cart, clear operation aisle, illustrative aisle-edge paint, and diffused overhead fixtures. These depict plausible work context from the comparable USDA image and known NSEL hydraulics-lab function, not verified NSEL equipment locations.',
        'Added a separate close, perspective exterior sign render with warm directional key/fill lighting and improved camera framing; no exterior architecture or sign geometry changed in R4.',
    ],
    'circulation':{'walkway':'R3 east side walkway retained','opposing_work_zone':'R4 west side prep bench','estimated_clear_work_aisle_m':1.9,'status':'illustrative; exact circulation plan unavailable'},
    'roof_height_caveat':'No roof height or footprint changes. Roof/wall heights remain estimates from 5-ft DSM samples and interpolated DTM ground; the USDA comparison photo does not establish NSEL dimensions.',
    'limitations':['No NSEL interior plan or interior photos located in the current evidence set; wall, ceiling, lighting and lab stations are interpretive context.','Comparable USDA image establishes typology, not identity, dimensions, equipment count, or specific circulation for NSEL.','No new openings, windows, or roof equipment added without direct evidence.','Existing 5-ft DSM/interpolated DTM roof-height split remains approximate.'],
}
(AUDIT/'nsel_revision_r4.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))

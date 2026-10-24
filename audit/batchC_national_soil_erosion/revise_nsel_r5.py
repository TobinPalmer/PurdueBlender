import bpy, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'batchC_national_soil_erosion'
ASSET=ROOT/'modular'/'buildings'/'national_soil_erosion_laboratory.blend'
INTERIOR=bpy.data.collections['SOIL_Interior']

for obj in list(INTERIOR.objects):
    if obj.name.startswith('SOIL | R5 '):
        bpy.data.objects.remove(obj,do_unlink=True)

def set_color(name,color,roughness=None):
    mat=bpy.data.materials[name]
    mat.diffuse_color=(*color,1)
    bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value=(*color,1)
    if roughness is not None:
        bsdf.inputs['Roughness'].default_value=roughness
    return mat

def make_material(name,color,roughness=.65,metallic=0):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color=(*color,1)
    mat.use_nodes=True
    bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value=(*color,1)
    bsdf.inputs['Roughness'].default_value=roughness
    bsdf.inputs['Metallic'].default_value=metallic
    return mat

def box(name,center,dims,mat,bevel=0):
    dx,dy,dz=dims
    verts=[(x,y,z) for x in (-dx/2,dx/2) for y in (-dy/2,dy/2) for z in (-dz/2,dz/2)]
    faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    mesh=bpy.data.meshes.new(name+' | mesh');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(mat)
    obj=bpy.data.objects.new(name,mesh);INTERIOR.objects.link(obj);obj.location=center
    if bevel:
        mod=obj.modifiers.new('soft fabricated panel edge','BEVEL');mod.width=bevel;mod.segments=2
    return obj

def beam(name,a,b,width,depth,mat):
    p0,p1=Vector(a),Vector(b);delta=p1-p0
    obj=box(name,(p0+p1)/2,(width,depth,delta.length),mat)
    obj.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
    return obj

# Warm up the liner/ceiling and give the wall and equipment a clear hierarchy.
# These are presentation choices, not claims about original paint colors.
set_color('SOIL | R4 pale gray high-bay liner',(.67,.62,.49),.72)
set_color('SOIL | R4 light industrial ceiling',(.78,.75,.66),.8)
set_color('SOIL | R4 lab cabinet enamel',(.20,.39,.40),.34)
set_color('SOIL | R4 soil sample trays',(.48,.22,.10),.68)
set_color('SOIL | R4 stainless work surface',(.58,.63,.62),.27)

cx,half_x,half_y=-25.4,4.5,17.75
band=make_material('SOIL | R5 muted mineral wall band',(.34,.42,.39),.78)
trim=make_material('SOIL | R5 warm metal wall trim',(.42,.34,.22),.36,.58)
panel=make_material('SOIL | R5 soft green-gray cladding',(.49,.57,.52),.64)

# A subdued lower wall band and rail/girt divisions break up the blank liner
# surfaces without inventing windows, lab doors, or roof openings.
box('SOIL | R5 west lower wall band',(cx-half_x+.13,0,.58),(.12,35.15,1.16),band,.025)
box('SOIL | R5 east lower wall band',(cx+half_x-.13,0,.58),(.12,35.15,1.16),band,.025)
box('SOIL | R5 north lower wall band',(cx,half_y-.13,.58),(8.92,.12,1.16),band,.025)
box('SOIL | R5 south lower wall band',(cx,-half_y+.13,.58),(8.92,.12,1.16),band,.025)
for side in (-1,1):
    x=cx+side*(half_x-.13)
    for z in (1.18,2.48,4.68):
        beam(f'SOIL | R5 wall girt {side} {z:.2f}',(x,-17.35,z),(x,17.35,z),.065,.075,trim)
for y in (-17.35,17.35):
    for z in (1.18,2.48,4.68):
        beam(f'SOIL | R5 end-wall girt {y:.2f} {z:.2f}',(cx-4.35,y,z),(cx+4.35,y,z),.065,.075,trim)

# Three restrained cladding color fields read as large industrial wall panels;
# positions remain schematic and no window/opening schedule is implied.
for index,y in enumerate((-11.4,0,11.4)):
    box(f'SOIL | R5 west cladding panel {index+1}',(cx-half_x+.12,y,3.48),(.055,7.0,3.55),panel,.015)
    box(f'SOIL | R5 east cladding panel {index+1}',(cx+half_x-.12,y,3.48),(.055,7.0,3.55),panel,.015)

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

report={
  'revision':'R5','previous_independent_score':'7.9/10',
  'changes':['Adjusted the R4 neutral gray liner, ceiling, cabinets, steel work surface, and sample tray colors for a warmer, more legible material hierarchy. These colors are presentation choices and are not evidence of original NSEL finishes.','Added a lower mineral-color wall band, slim horizontal girts, and muted upper cladding fields to the high-bay cutaway. These architectural divisions add scale/context without adding unsupported windows, doors, or roof openings.','Added a street-distance exterior render including a broad facade/roof silhouette, entry, and readable building/address lettering. No facade dimensions or sign geometry changed.'],
  'uncertainty':['Interior wall finishes, girts, panel colors and divisions are interpretive; no NSEL interior plan or interior photo is available.','The USDA ARS photo supports an enclosed industrial hydraulics lab and flume work context, not exact NSEL interior construction.','The 2018 visitor image supports facade lettering but does not give measured font size, camera distance or survey dimensions.','Roof-height split remains approximate from 5-ft DSM cells and interpolated DTM ground.'],
  'source_context':['https://www.ars.usda.gov/oc/images/photos/apr97/k7567-11/','https://ppgta.ufms.br/files/2018/02/Grupo-Purdue.jpg','https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0']
}
(AUDIT/'nsel_revision_r5.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))

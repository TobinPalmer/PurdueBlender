import bpy, math, json
from pathlib import Path
from mathutils import Vector
D=Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas')
c=bpy.data.collections['Asset_felix_haas_hall']
# Remove the simplified flat roof cap that concealed the photo-based hipped roof.
old=bpy.data.objects.get('HAAS_Corrected_GIS_Roof_Slab')
if old: bpy.data.objects.remove(old,do_unlink=True)
# Convert the center lower opening on the documented entrance facade into a pair of doors.
old=bpy.data.objects.get('HAAS_Photo_Glazing_0_3.1')
if old: bpy.data.objects.remove(old,do_unlink=True)
# Reuse the existing stone and wood materials when present.
stone=bpy.data.materials.get('HAAS_Photo_Limestone')
wood=bpy.data.materials.get('HAAS_Plan_Laminate_estimated')
if wood is None:
    wood=bpy.data.materials.new('HAAS_Photo_Wood_Door_estimated');wood.diffuse_color=(.19,.075,.035,1);wood.use_nodes=True;wood.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.19,.075,.035,1)
def box(name,loc,dim,mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object;o.name='HAAS_Photo_'+name;o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for co in list(o.users_collection):co.objects.unlink(o)
    c.objects.link(o)
    if mat:o.data.materials.append(mat)
    o['evidence']='Qualitative Purdue Felix Haas Hall facade photo; dimensions estimated, retrieved 2026-10-23'
    return o
# Two recessed timber leaves inside the existing lower central opening.
for side in (-1,1):
    box('Main_Door_'+str(side),(12.77,side*.48,1.82),(.07,.92,2.64),wood)
    box('Door_Glazing_'+str(side),(12.72,side*.48,2.44),(.025,.55,.8),bpy.data.materials.get('HAAS_Photo_BlueGlass'))
    box('Door_Handle_'+str(side),(12.68,side*.86,1.78),(.05,.035,.18),stone)
# Limestone threshold, jambs, and entrance sign panel.
box('Door_Threshold',(13.12,0,.43),(.65,2.3,.16),stone)
box('Door_Sign_Panel',(13.11,0,5.12),(.30,2.7,.7),stone)
# Shallow stone arch over the double door.
curve=bpy.data.curves.new('HAAS_Main_Entry_Stone_Arch','CURVE');curve.dimensions='3D';curve.bevel_depth=.14;curve.bevel_resolution=4
spl=curve.splines.new('POLY');spl.points.add(32)
for i,p in enumerate(spl.points):
    a=math.pi*i/32;p.co=(13.13,1.1*math.cos(a),3.12+.7*math.sin(a),1)
obj=bpy.data.objects.new('HAAS_Photo_Main_Entry_Arch',curve);c.objects.link(obj);curve.materials.append(stone);obj['evidence']='Photo-derived arched central entrance; curve dimensions estimated'
# Exterior approach: 10 broad masonry treads rising toward the door.
for i in range(10):
    h=.18*(i+1);length=.34
    box('Entry_Stair_Tread_'+str(i),(13.35+(i+.5)*length,0,.24+h/2),(length,4.6,h),stone)
# Reduce texture contrast so tiles read as shallow roofing at campus scale.
roofmat=bpy.data.materials.get('HAAS_GooglePhotos_RedClayTiles_estimated')
if roofmat and roofmat.use_nodes:
    nodes=roofmat.node_tree.nodes
    brick=next((n for n in nodes if n.type=='TEX_BRICK'),None)
    if brick:
        brick.inputs['Brick Width'].default_value=.42
        brick.inputs['Row Height'].default_value=.18
        brick.inputs['Mortar Size'].default_value=.004
        brick.inputs['Mortar Smooth'].default_value=.003
    bump=next((n for n in nodes if n.type=='BUMP'),None)
    if bump:bump.inputs['Distance'].default_value=.004;bump.inputs['Strength'].default_value=.22
# Store explicit source and measurement limitations on collection for reviewers.
c['exterior_source']='https://events.purdue.edu/felix_haas_hall (Purdue event photo gallery); Google Maps photo review 2026-10-23'
c['floor_plan_source']='https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf (first-floor diagram, PDF metadata 2016-08-16)'
c['roof_height_status']='Estimated from imagery; no measured roof elevations located.'
c['interior_scope']='One published first-floor diagram modeled. Furniture, wall heights, door positions and room dimensions estimated; no current upper-floor plans verified.'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
(D/'finish_changes.json').write_text(json.dumps({'removed':['HAAS_Corrected_GIS_Roof_Slab','HAAS_Photo_Glazing_0_3.1'],'added':[o.name for o in c.all_objects if o.name.startswith('HAAS_Photo_Main_Door') or o.name.startswith('HAAS_Photo_Door_') or o.name.startswith('HAAS_Photo_Entry_') or o.name=='HAAS_Photo_Main_Entry_Arch'],'source_plan':'https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf','source_exterior':'https://events.purdue.edu/felix_haas_hall','limitations':'Photo-derived doorway details and roof heights estimated; only first-floor diagram verified; GIS shell dimensions retained'},indent=2))

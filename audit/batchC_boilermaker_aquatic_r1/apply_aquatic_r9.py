import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']
old=bpy.data.collections.get('AQUA_R9 | bleacher supports and cutaway review')
if old:
    for o in list(old.objects):
        dat=o.data; typ=o.type
        bpy.data.objects.remove(o,do_unlink=True)
        if dat and dat.users==0:
            if typ=='CAMERA': bpy.data.cameras.remove(dat)
            elif typ=='CURVE': bpy.data.curves.remove(dat)
            elif typ=='MESH': bpy.data.meshes.remove(dat)
    bpy.data.collections.remove(old)
col=bpy.data.collections.new('AQUA_R9 | bleacher supports and cutaway review')
asset.children.link(col)
railmat=bpy.data.materials.get('AQUA | charcoal anodized metal')
if not railmat:
    railmat=bpy.data.materials.new('AQUA_R9 | graphite structural aluminum')
    railmat.diffuse_color=(.13,.16,.17,1)
    railmat.use_nodes=True
    bsdf=next(n for n in railmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value=(.13,.16,.17,1)
    bsdf.inputs['Metallic'].default_value=.62
    bsdf.inputs['Roughness'].default_value=.36

def add_box(name,loc,dims,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o)
    if mat: o.data.materials.append(mat)
    bevel=o.modifiers.new('AQUA R9 | softened bracket edges','BEVEL');bevel.width=.018;bevel.segments=2
    o['r9_note']='Representative support detail added to visually connect the schematic aluminum bleacher tiers; not an as-built structural plan.'
    return o
# Continuous graphite riser plates visually tie the twenty-four bench sections into two coherent stepped banks.
risers=[]
for row in range(12):
    x=15.6+row*.68; z=.5+row*.28
    for bank,(y0,y1) in enumerate(((-20.0,-1.7),(1.7,20.0)),1):
        y=(y0+y1)/2; width=y1-y0
        risers.append(add_box(f'AQUA R9 | continuous bleacher riser row {row+1:02d} bank {bank}',(x+.345,y,z+.185),(.075,width,.29),railmat))
# The center stair handrails already trace the step incline; add regular posts that land on each tread.
posts=[]
rails=[o for o in asset.all_objects if o.type=='CURVE' and o.name.startswith('AQUA R4 | schematic center aisle handrail')]
assert len(rails)==2, f'Expected 2 aisle rails, found {len(rails)}'
for o in rails:
    o.data.bevel_depth=.042; o.data.bevel_resolution=4
for side in (-1,1):
    for row in range(12):
        x=15.88+row*.68
        tread_top=.62+row*.28+.12
        rail_center=.62+row*.28+.24+1.02
        post_top=rail_center-.042
        height=post_top-tread_top
        posts.append(add_box(f'AQUA R9 | center aisle rail post {side:+d} {row+1:02d}',(x,side*.96,(post_top+tread_top)/2),(.06,.06,height),railmat))
        posts[-1]['r9_note']='Post aligns to a representative center-aisle tread and meets the existing sloped handrail; dimensions/layout remain schematic.'
# Persistent camera identifies the saved model review angle. The renderer temporarily opens the roof for this cutaway.
rig=bpy.data.collections.get('Preview_Rig') or col
camdata=bpy.data.cameras.new('AQUA R9 | truss pool and bleacher cutaway camera')
cam=bpy.data.objects.new('AQUA R9 | truss pool and bleacher cutaway camera',camdata);col.objects.link(cam)
cam.location=(-5,-42,7.8);cam.rotation_euler=(Vector((12,22,7.0))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.lens=26
cam['r9_note']='Presentation viewpoint for the pool, aluminum stands and existing exposed roof trusses; it is not a surveyed viewpoint. Full roof geometry remains in the saved asset.'
# Persist useful camera and content metadata without applying a roof-height change.
asset['r9_improvements']='Connected representative bleacher risers and center-aisle handrail posts; saved interior review camera for an open-roof cutaway render.'
asset['r9_geometry_change']='No roof, footprint, floor, facade, or building height geometry changed.'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print({'saved':str(ASSET),'r9_collection_objects':len(col.objects),'bleacher_risers':len(risers),'aisle_posts':len(posts),'existing_trusses':sum(1 for o in asset.all_objects if o.type=='MESH' and o.name.startswith('AQUA | schematic clear-span roof truss')),'camera':cam.name})

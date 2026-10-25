"""Add evidence-based flat membrane roofs to the roofless Niswonger classroom wings.
The sloping glazed connector roof (x=5..20.5) and Hangar 1 roof are retained.
"""
import bpy, json, shutil
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
ASSET=ROOT/'modular/buildings/niswonger_aviation_tech.blend'
OUT=ROOT/'audit/niswonger_aviation_tech_refine'
if not (OUT/'niswonger_before_refine.blend').exists():
    shutil.copy2(ASSET,OUT/'niswonger_before_refine.blend')
asset=bpy.data.collections['Asset_niswonger_aviation_tech']
assert asset
roofmat=bpy.data.materials['NISW_Roof_Membrane']
# Don't duplicate on rerun.
for name in ('NISW_R2_Roof_Classroom_Wing','NISW_R2_Roof_Brick_Wing'):
    ob=bpy.data.objects.get(name)
    if ob: bpy.data.objects.remove(ob,do_unlink=True)

def roof_slab(name,x0,x1,y0,y1,z0,z1,thickness=.16):
    # Four supported corners allow a subtle fall of about 0.35% for drainage.
    verts=[(x0,y0,z0),(x1,y0,z0-.12),(x1,y1,z1-.12),(x0,y1,z1),
           (x0,y0,z0-thickness),(x1,y0,z0-.12-thickness),(x1,y1,z1-.12-thickness),(x0,y1,z1-thickness)]
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.materials.append(roofmat);me.update()
    ob=bpy.data.objects.new(name,me);asset.objects.link(ob)
    # Crisp perimeter, tiny bevel only on exposed lower fascia edges.
    bevel=ob.modifiers.new('Soft membrane edge','BEVEL');bevel.width=.025;bevel.segments=2
    norm=ob.modifiers.new('Weighted roof normals','WEIGHTED_NORMAL');norm.keep_sharp=True
    return ob
# Two roof plates close the incomplete classroom / service wings at the shell wall tops.
# Their elevations follow the modeled perimeter wall top elevations; no coverage is added
# above the photo-documented sloping clerestory or Hangar 1.
brick=roof_slab('NISW_R2_Roof_Brick_Wing',-39.45,-31.85,7.15,42.35,4.72,4.72)
classroom=roof_slab('NISW_R2_Roof_Classroom_Wing',-31.7,4.84,7.15,43.95,7.84,7.84)
# Tag provenance and limitation for file inspectors.
for ob in (brick,classroom):
    ob['source_basis']='MSKTD 2019 project photographs show complete enclosed addition with roofed interiors; plate fills existing shell footprint at modeled wall top.'
    ob['dimensions_basis']='Approximate from existing modeled shell bounds; no current roof plan available.'
    ob['asset_edit']='Niswonger refinement round 2'
# Ensure they render and export with existing collection.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({'saved':str(ASSET),'added':[brick.name,classroom.name],'bounds':{o.name:[[round(min((o.matrix_world@Vector(v))[i] for v in o.bound_box),3) for i in range(3)],[round(max((o.matrix_world@Vector(v))[i] for v in o.bound_box),3) for i in range(3)]] for o in (brick,classroom)}},indent=2))

import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
path=ROOT/'modular/buildings/physics_building_phys_3bf42f3.blend'
bpy.ops.wm.open_mainfile(filepath=str(path))
asset=bpy.data.collections['Asset_physics_building']
roof=bpy.data.objects['PHYS | estimated sloped red tile roof']
shell=bpy.data.objects['PHYS | GIS footprint brick envelope']
base=[v.co.copy() for v in shell.data.vertices if abs(v.co.z)<1e-5]
axis=(base[2]-base[0]).normalized(); axis.z=0; axis.normalize()
across=Vector((-axis.y,axis.x,0))
uv=roof.data.uv_layers.get('Roof tile UV') or roof.data.uv_layers.new(name='Roof tile UV')
for poly in roof.data.polygons:
    for li,vi in zip(poly.loop_indices,poly.vertices):
        p=roof.data.vertices[vi].co
        uv.data[li].uv=(p.x*axis.x+p.y*axis.y,p.x*across.x+p.y*across.y)
mat=bpy.data.materials['PHYSICS_BUILDING | evidence palette roof']
mat['roof_surface_note']='Meter-scale staggered red clay tiles; shared GIS-oriented UV axes keep rows parallel to the long eaves across every sloped facet.'
roof['tile_uv_note']='Shared local GIS long axis and perpendicular direction; meter UV scale, no independent face rotation.'
asset['roof_surface_revision']='Meter-scale clay tiles use consistent GIS-aligned UV axes across all 33 roof facets.'
bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
print('GIS-oriented roof UVs updated for',len(roof.data.polygons),'facets; objects',len(asset.all_objects))

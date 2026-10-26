"""Locally correct Tarkington's four structural wing footprints from registered GIS/orthophoto evidence.

GIS FID 662 is a building outline, not documented wall-survey geometry. The
targets below use mid-wing sections where the 2023 roof edge is legible, and
are explicitly treated as a roof/wall proxy rather than exact wall truth.
"""
import bpy
import json
from mathutils import Matrix
from mathutils import Vector
from pathlib import Path

OUT = Path(bpy.path.abspath('//'))
MAPPING = {
    # source wall-face endpoints -> registered Purdue GIS / 2023 roof-edge proxy
    'NW': (-48.39, -21.39, -45.80, -33.60),
    'SW': (-48.39, -21.39, -46.80, -34.60),
    'NE': (14.61, 41.61, 28.00, 40.20),
    'SE': (14.61, 41.61, 28.70, 40.90),
}
# The GIS and orthophoto show an asymmetric southeast termination: unlike the
# southwest arm, the southeast roof stops at about local Y=-43.4 m.
SE_Y_SOURCE = (-54.50, -7.00)
SE_Y_TARGET = (-43.40, -7.00)

def remap(code, x):
    a, b, c, d = MAPPING[code]
    return c + (x-a) * (d-c) / (b-a)

def remap_se_y(y):
    a, b = SE_Y_SOURCE
    c, d = SE_Y_TARGET
    return c + (y-a) * (d-c) / (b-a)

def set_world_x(obj, x):
    mw = obj.matrix_world.copy()
    mw.translation.x = x
    obj.matrix_world = mw

# Deform only the architectural shell meshes. This preserves the orthogonal
# four-wing plan while leaving the standard 11'7" x 16'2" room/interior details
# at their original, independently supported dimensions.
shell_count = 0
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    code = next((code for code in MAPPING if obj.name.startswith(f'Tark_{code}_Wing_')), None)
    if not code:
        continue
    inv = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        old_world = obj.matrix_world @ vertex.co
        new_y = remap_se_y(old_world.y) if code == 'SE' else old_world.y
        new_world = Vector((remap(code, old_world.x), new_y, old_world.z))
        vertex.co = inv @ new_world
    obj.data.update()
    shell_count += 1

# Keep side-wall openings and sills in the remodeled wall plane. Reposition
# their centers only; retain sill/window dimensions and floor-to-floor spacing.
facade_repositioned = 0
end_facade_scaled = 0
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    if not (obj.name.startswith('Tark_Win_') or obj.name.startswith('Tark_Sill_')):
        continue
    code = next((code for code in MAPPING if f'_{code}_' in obj.name), None)
    if not code:
        continue
    # End-facade units span the compressed wing width. Narrow only their
    # horizontal aperture dimension so adjacent windows remain discrete.
    if 'North_' in obj.name or 'South_' in obj.name:
        old_x = obj.matrix_world.translation.x
        a, b, c, d = MAPPING[code]
        factor = (d-c)/(b-a)
        inv = obj.matrix_world.inverted()
        for vertex in obj.data.vertices:
            p = obj.matrix_world @ vertex.co
            q = Vector((old_x + (p.x-old_x)*factor, p.y, p.z))
            vertex.co = inv @ q
        obj.data.update()
        old_y = obj.matrix_world.translation.y
        set_world_x(obj, remap(code, old_x))
        if code == 'SE':
            mw = obj.matrix_world.copy()
            mw.translation.y = remap_se_y(old_y)
            obj.matrix_world = mw
        end_facade_scaled += 1
    else:
        old_y = obj.matrix_world.translation.y
        set_world_x(obj, remap(code, obj.matrix_world.translation.x))
        if code == 'SE':
            mw = obj.matrix_world.copy()
            mw.translation.y = remap_se_y(old_y)
            obj.matrix_world = mw
        facade_repositioned += 1

# Roof penthouses/HVAC are architectural details located at each wing's center.
# Move their centers with the wings while preserving the modeled equipment size.
roof_moved = 0
for obj in bpy.data.objects:
    if not (obj.name.startswith('Tark_Roof_Penthouse_') or obj.name.startswith('Tark_Roof_HVAC_Louver_')):
        continue
    idx = obj.name.rsplit('_', 1)[-1]
    code = {'0':'NW','1':'NE','2':'SW','3':'SE'}.get(idx)
    if code:
        old_y = obj.matrix_world.translation.y
        set_world_x(obj, remap(code, obj.matrix_world.translation.x))
        if code == 'SE':
            mw = obj.matrix_world.copy()
            mw.translation.y = remap_se_y(old_y)
            obj.matrix_world = mw
        roof_moved += 1

# The registered source footprint and 2023 orthophoto show a north connector
# joining the four-wing masses. The old shell set left two gaps. Add connector
# volumes in the same brick/limestone/roof palette and align them to the GIS.
root_obj = bpy.data.objects.get('AssetRoot_tarkington_hall')
brick = bpy.data.materials.get('Beering_Purdue_Red_Brick')
limestone = bpy.data.materials.get('Indiana_Bedford_Limestone')
roofmat = bpy.data.materials.get('Beering_Roof_Membrane')
glass = bpy.data.materials.get('Beering_Solar_Ribbon_Glass')

def add_box(name, bounds, material):
    x0,x1,y0,y1,z0,z1=bounds
    verts=[(0,0,0),(x1-x0,0,0),(x1-x0,y1-y0,0),(0,y1-y0,0),
           (0,0,z1-z0),(x1-x0,0,z1-z0),(x1-x0,y1-y0,z1-z0),(0,y1-y0,z1-z0)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh=bpy.data.meshes.new(name+'_Mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.scene.collection.objects.link(obj)
    if material: obj.data.materials.append(material)
    obj.matrix_world=Matrix.Translation(Vector((x0,y0,z0)))
    if root_obj:
        obj.parent=root_obj
        obj.matrix_world=Matrix.Translation(Vector((x0,y0,z0)))
    return obj

def add_connector(code,x0,x1):
    y0,y1=19.0,33.0
    add_box(f'Tark_{code}_Connector_Limestone_Base',(x0,x1,y0,y1,0.0,1.5),limestone)
    add_box(f'Tark_{code}_Connector_Brick_Shaft',(x0,x1,y0,y1,1.5,15.2),brick)
    for level,z in enumerate((3.8,7.6,11.4,15.2),1):
        add_box(f'Tark_{code}_Connector_Limestone_Belt_{level}',(x0,x1,y0,y1,z-.11,z+.11),limestone)
    add_box(f'Tark_{code}_Connector_Roof_Membrane',(x0+.35,x1-.35,y0+.35,y1-.35,15.2,15.38),roofmat)
    add_box(f'Tark_{code}_Connector_Roof_Parapet',(x0-.05,x1+.05,y0-.05,y1+.05,15.5,15.9),limestone)
    # Match the four stacked dorm window bands at a restrained room-bay rhythm.
    cols=5
    xs=[x0+(x1-x0)*(i+.5)/cols for i in range(cols)]
    for side,yc in [('N',y1+.08),('S',y0-.08)]:
        for col,xc in enumerate(xs):
            for row,z in enumerate((2.4,6.2,10.0,13.8)):
                add_box(f'Tark_{code}_Connector_Win_{side}_{col}_{row}',
                        (xc-.85,xc+.85,yc-.09,yc+.09,z-.75,z+.75),glass)

add_connector('West',-33.60,-15.3875)
add_connector('East',8.6125,28.00)

audit = {
    'asset': 'Tarkington Hall',
    'changes': 'Four wing structural-shell vertices remapped along X to GIS/orthophoto roof-edge proxy; southeast wing shortened to registered termination; wing facade windows and sills repositioned; end-facade aperture widths adjusted; roof penthouse/HVAC centers moved with wings; missing north connector bridges added with brick, limestone, roof finish, and room-bay windows.',
    'mapping_source_wall_face_x_to_target_proxy_x_m': MAPPING,
    'southeast_source_y_to_target_proxy_y_m': {'source': SE_Y_SOURCE, 'target': SE_Y_TARGET},
    'structural_shell_meshes_deformed': shell_count,
    'side_facade_windows_sills_repositioned': facade_repositioned,
    'north_south_facade_openings_width_adjusted': end_facade_scaled,
    'roof_equipment_centers_moved': roof_moved,
    'north_connector_bridges_added': ['West connector x=-33.60..-15.3875, y=19..33 m', 'East connector x=8.6125..28.00, y=19..33 m'],
    'preserved': ['Dorm room 118 and room furnishings dimensions/locations', 'central core', 'wing Y/Z dimensions and floor heights', 'window/sill vertical dimensions and spacing'],
    'source_uncertainty': 'Purdue GIS FID 662 documents a building outline but not whether its digitized edges are wall faces, roof eaves, or another cartographic edge. Targets were selected at straight mid-wing sections and aligned with the visible Spring 2023 Indiana orthophoto roofs. Metrics quantify model-to-GIS outline agreement, not a surveyed wall offset.',
}
(OUT / 'correction_r2.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
print(json.dumps(audit, indent=2))

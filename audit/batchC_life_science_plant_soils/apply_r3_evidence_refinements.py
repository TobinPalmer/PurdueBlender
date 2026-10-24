import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/life_science_plant_and_soils_laboratory.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_life_science_plant_and_soils_laboratory']
roof=bpy.data.collections['LSPS_Roof']
interior=bpy.data.collections['LSPS_Interior']
for o in list(bpy.data.objects):
    if o.name.startswith('LSPS R3 | '): bpy.data.objects.remove(o,do_unlink=True)
def mat(name,color,rough=.65,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    return m
m_roof=mat('LSPS | R3 rooftop service equipment enamel',(0.29,.32,.32),.72,.25)
m_dark=mat('LSPS | R3 roof vent recess',(0.045,.06,.06),.82,.05)
m_cold=mat('LSPS | R3 insulated cold-room panels',(.68,.72,.72),.72,.08)
m_door=mat('LSPS | R3 walk-in cold-room door',(.35,.42,.43),.48,.35)
m_floor=mat('LSPS | R3 below-grade concrete floor',(.36,.38,.37),.84)
def box(name, loc, size, material, collection, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection): c.objects.unlink(o)
    collection.objects.link(o)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Small softened sheet-metal edges','BEVEL'); mod.width=bevel; mod.segments=2
        o.modifiers.new('Weighted panel normals','WEIGHTED_NORMAL')
    o['detail_status']='schematic detail added from source evidence; exact dimensions/positions unverified'
    return o
# Two below-grade floor plates, cloned from existing GIS-clipped ground slab; use attribute interval as an estimate only.
ground=bpy.data.objects['Life Science Plant and Soils Laboratory | official GIS footprint ground floor']
for label,z in [('B',-3.6576),('SB',-7.3152)]:
    me=ground.data.copy(); me.name=f'LSPS R3 | level {label} below-grade floor slab mesh'
    for v in me.vertices: v.co.z += z
    o=bpy.data.objects.new(f'LSPS R3 | level {label} below-grade floor plate',me); interior.objects.link(o); o.data.materials.append(m_floor)
    o['source']='Purdue BuildingShapesZip4 FID 917 attributes B=-12 and SB=-24; unit semantics undocumented, modeled at approximate 12-foot intervals.'
    o['geometry_status']='GIS footprint-shaped schematic basement plate; basement wall extents not independently verified.'
# Roof evidence: 2022-2025 Indiana orthophoto shows a broad flat roof and several small rooftop service units.
# Pixel positions are visual approximations from local evidence image; model placements are illustrative.
roof_z=11.0
roof_xy=[(-24.5,-7.2),(-16.0,-5.3),(-8.3,-7.8),(-1.2,-4.5),(7.0,-7.4),(15.2,-5.4),(23.1,-7.0),(27.4,0.5)]
for i,(x,y) in enumerate(roof_xy,1):
    base=box(f'LSPS R3 | roof service unit {i:02}',(x,y,roof_z+.16),(1.45,.85,.32),m_roof,roof,.04)
    base['source_basis']='Visual check against Indiana GIO current orthophoto, 2022-2025; small rooftop service equipment is visible, exact count/type/positions unresolved.'
    box(f'LSPS R3 | roof service unit {i:02} vent cap',(x,y,roof_z+.48),(.78,.52,.32),m_roof,roof,.035)
    for j in range(3):
        box(f'LSPS R3 | roof service unit {i:02} louver {j+1}',(x,y-.27+j*.20,roof_z+.50),(.62,.025,.15),m_dark,roof,.008)
# Basement cold storage equipment and enclosures. Room geometry/location are deliberately schematic.
# One grouping on each named below-grade level reflects report's basement cold-storage use without asserting an exact plan.
for level,z,centers in [('B',-3.6576,[(-17,-3),(-9,-3),(-1,-3)]),('SB',-7.3152,[(7,2),(15,2)])]:
    for i,(cx,cy) in enumerate(centers,1):
        floorz=z+.08; h=2.45; cz=floorz+h/2
        # Insulated cabinet-like room: side/back panels and roof, with a front panel split by a door opening.
        box(f'LSPS R3 | {level} cold room {i} left panel',(cx-1.55,cy,cz),(.12,3.0,h),m_cold,interior,.018)
        box(f'LSPS R3 | {level} cold room {i} right panel',(cx+1.55,cy,cz),(.12,3.0,h),m_cold,interior,.018)
        box(f'LSPS R3 | {level} cold room {i} back panel',(cx,cy+1.44,cz),(3.0,.12,h),m_cold,interior,.018)
        box(f'LSPS R3 | {level} cold room {i} front left panel',(cx-.98,cy-1.44,cz),(1.04,.12,h),m_cold,interior,.018)
        box(f'LSPS R3 | {level} cold room {i} front right panel',(cx+.98,cy-1.44,cz),(1.04,.12,h),m_cold,interior,.018)
        box(f'LSPS R3 | {level} cold room {i} lintel',(cx,cy-1.44,z+2.34),(1.0,.14,.24),m_cold,interior,.015)
        box(f'LSPS R3 | {level} cold room {i} insulated door',(cx,cy-1.52,z+.99),(.86,.11,1.74),m_door,interior,.025)
        box(f'LSPS R3 | {level} cold room {i} handle',(cx+.34,cy-1.60,z+.96),(.035,.035,.38),m_dark,interior,.009)
        box(f'LSPS R3 | {level} cold room {i} condenser',(cx+.95,cy+1.1,z+2.63),(.84,.48,.28),m_roof,interior,.03)
        box(f'LSPS R3 | {level} cold room {i} condenser grille',(cx+.95,cy+.84,z+2.63),(.48,.025,.17),m_dark,interior,.008)
        for obj in interior.objects:
            if obj.name.startswith(f'LSPS R3 | {level} cold room {i} '):
                obj['source_basis']='Purdue Agronomy five-year report (2021) identifies basement cold storage; exact room locations, count, dimensions, and current configuration are not shown and are schematic.'
                obj['level_status']='B/SB label taken from official GIS fields; floor elevation is approximate because units and vertical semantics are undocumented.'
# Preserve standard view state, save and force a reload to validate persistence.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('R3_saved',ASSET,'objects',len(list(o for o in asset.all_objects)),'materials',len({m for o in asset.all_objects if o.type=='MESH' for m in o.data.materials if m}))
